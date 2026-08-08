from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from data_loader import load_data
from similarity import build_vectorizer, find_top_matches
from decision_engine import decide_action

# Try importing AI Layer (if ai_layer.py is present in backend folder)
try:
    from ai_layer import generate_ai_reply_and_explanation
    HAS_AI_LAYER = True
except ImportError:
    HAS_AI_LAYER = False

app = FastAPI(title="Zepto Support Ticket Manager")

# Allow frontend (running on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load everything once at startup
resolved, new_tickets_full, orders = load_data()
vectorizer, resolved_vectors = build_vectorizer(resolved)

DECISIONS_LOG = "decisions_log.json"


def draft_reply(ticket_desc, decision):
    """Simple template-based reply generator fallback."""
    if decision["status"] == "auto_resolved":
        action_text = {
            "full_refund": f"a full refund of ₹{decision['refund_amount']}",
            "partial_refund": f"a partial refund of ₹{decision['refund_amount']}",
            "refund_reissue": f"a reissued refund of ₹{decision['refund_amount']}",
            "redelivery": "a free redelivery",
            "coupon": "a coupon as compensation",
            "apology_no_action": "our sincere apologies",
        }.get(decision["action"], "an appropriate resolution")

        return (
            f"Hi, thanks for reaching out about '{ticket_desc}'. "
            f"Based on {len(decision['precedents'])} similar past cases, "
            f"we've processed {action_text} for you right away."
        )
    else:
        return (
            f"Hi, thanks for reaching out about '{ticket_desc}'. "
            f"We're reviewing your ticket closely and a support agent will "
            f"get back to you shortly with the best resolution."
        )


def generate_reply_and_explanation(ticket_desc, decision, order_info):
    """Generate customer reply and AI explanation using AI Layer if available."""
    if HAS_AI_LAYER:
        res = generate_ai_reply_and_explanation(ticket_desc, decision, order_info)
        return res.get("customer_reply"), res.get("ai_explanation")
    else:
        reply = draft_reply(ticket_desc, decision)
        explanation = f"Action '{decision['action']}' determined based on similarity matching and guardrails."
        return reply, explanation


def process_all_tickets():
    """Run the full pipeline on all new tickets and return results."""
    results = []
    for i in range(len(new_tickets_full)):
        ticket = new_tickets_full.iloc[i]
        matches = find_top_matches(ticket["description"], vectorizer, resolved_vectors, resolved)
        
        order_info = {
            "order_id": str(ticket["order_id"]),
            "value_inr": float(ticket["value_inr"]),
            "delivery_status": str(ticket["delivery_status"]),
            "found": True
        }
        
        decision = decide_action(matches, order_info)
        reply, ai_explanation = generate_reply_and_explanation(ticket["description"], decision, order_info)

        results.append({
            "ticket_id": str(ticket["ticket_id"]),
            "description": str(ticket["description"]),
            "order_id": str(ticket["order_id"]),
            "order_value": float(ticket["value_inr"]),
            "delivery_status": str(ticket["delivery_status"]),
            "status": decision["status"],
            "action": decision["action"],
            "confidence": float(decision["confidence"]),
            "reason": decision["reason"],
            "refund_amount": float(decision["refund_amount"]) if decision["refund_amount"] is not None else None,
            "reply": reply,
            "ai_explanation": ai_explanation,
            "precedents": decision["precedents"],
        })
    return results


@app.get("/board")
def get_board():
    """Return all tickets processed, split into auto-resolved and human-review lanes."""
    results = process_all_tickets()

    # Save log for audit trail
    with open(DECISIONS_LOG, "w") as f:
        json.dump(results, f, indent=2, default=str)

    auto_resolved = [r for r in results if r["status"] == "auto_resolved"]
    human_review = [r for r in results if r["status"] == "human_review"]

    return {
        "auto_resolved": auto_resolved,
        "human_review": human_review,
        "total": len(results),
    }


@app.get("/")
def root():
    return {"message": "Zepto Support Ticket Manager API is running"}


class TicketInput(BaseModel):
    description: str
    order_id: Optional[str] = None


def get_order_info(order_id):
    """Look up order context; return sensible defaults if not found."""
    if order_id:
        match = orders[orders["order_id"] == order_id]
        if not match.empty:
            row = match.iloc[0]
            return {
                "order_id": str(row["order_id"]),
                "value_inr": float(row["value_inr"]),
                "delivery_status": str(row["delivery_status"]),
                "items": int(row["items"]),
                "delivery_time_min": int(row["delivery_time_min"]),
                "found": True,
            }
    return {
        "order_id": order_id or "N/A",
        "value_inr": 0.0,
        "delivery_status": "unknown",
        "items": 0,
        "delivery_time_min": 0,
        "found": False,
    }


@app.post("/process_ticket")
def process_single_ticket(ticket: TicketInput):
    """Analyze one arbitrary ticket description live."""
    order_info = get_order_info(ticket.order_id)
    matches = find_top_matches(ticket.description, vectorizer, resolved_vectors, resolved)
    decision = decide_action(matches, order_info)
    reply, ai_explanation = generate_reply_and_explanation(ticket.description, decision, order_info)

    return {
        "description": ticket.description,
        "order": order_info,
        "status": decision["status"],
        "action": decision["action"],
        "confidence": decision["confidence"],
        "reason": decision["reason"],
        "refund_amount": decision["refund_amount"],
        "reply": reply,
        "ai_explanation": ai_explanation,
        "precedents": decision["precedents"],
    }