import os
import json
from pathlib import Path

from dotenv import load_dotenv


ENV_FILE = Path(__file__).resolve().parent / ".env"


def _get_env_value(*names):
    """Return the first non-empty configured secret without logging it."""
    for name in names:
        value = os.getenv(name)
        if value and value.strip():
            return value.strip()
    return None


def get_gemini_models():
    configured_models = os.getenv("GEMINI_MODEL", "gemini-2.5-flash,gemini-2.0-flash")
    return tuple(model.strip() for model in configured_models.split(",") if model.strip())


def get_ai_client():
    """Load local configuration and initialize the configured AI provider."""
    # This keeps the module usable from FastAPI, a CLI script, or a test runner.
    load_dotenv(ENV_FILE)

    gemini_key = _get_env_value("GEMINI_API_KEY", "AI_API_KEY")
    openai_key = _get_env_value("OPENAI_API_KEY")
    groq_key = _get_env_value("GROQ_API_KEY")

    if gemini_key:
        try:
            from google import genai
            return "gemini", genai.Client(api_key=gemini_key)
        except Exception as error:
            # Do not print the key or fall through to another provider silently.
            print(f"[AI Layer Init Warning] Gemini client unavailable: {error}")
            return "fallback", None

    if openai_key:
        try:
            from openai import OpenAI
            return "openai", OpenAI(api_key=openai_key)
        except Exception as error:
            print(f"[AI Layer Init Warning] OpenAI client unavailable: {error}")
            return "fallback", None

    if groq_key:
        try:
            from openai import OpenAI
            return "groq", OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
        except Exception as error:
            print(f"[AI Layer Init Warning] Groq client unavailable: {error}")
            return "fallback", None

    return "fallback", None


def clean_json_string(text: str) -> str:
    """Helper to strip markdown backticks before JSON parsing."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def parse_ai_response(text: str):
    """Parse and validate the response shape expected by the frontend."""
    result = json.loads(clean_json_string(text))
    if not isinstance(result, dict):
        raise ValueError("AI response must be a JSON object")

    customer_reply = result.get("customer_reply")
    ai_explanation = result.get("ai_explanation")
    if not isinstance(customer_reply, str) or not isinstance(ai_explanation, str):
        raise ValueError("AI response is missing customer_reply or ai_explanation")
    return {"customer_reply": customer_reply, "ai_explanation": ai_explanation}


def generate_ai_reply_and_explanation(ticket_desc, decision, order_info):
    """
    Uses AI API Key to generate empathetic customer response and explicit decision explanation.
    Falls back to template response if no API key is set or API fails.
    """
    provider, client = get_ai_client()

    precedents_str = "\n".join([
        f"- Ticket {p['ticket_id']}: '{p['description']}' -> Action: {p['resolution_action']} (Similarity: {p['similarity']})"
        for p in decision.get("precedents", [])
    ])

    action = decision.get("action")
    status = decision.get("status")
    refund = decision.get("refund_amount")
    confidence = decision.get("confidence", 0.0)
    reason = decision.get("reason", "")

    if provider == "fallback" or client is None:
        return generate_fallback(ticket_desc, decision)

    prompt = f"""
    You are Zepto's AI Resolution Agent for instant 10-minute grocery delivery.

    Incoming Customer Ticket: "{ticket_desc}"
    System Resolution Status: {status.upper()}
    Chosen Action: {action}
    Refund Amount: ₹{refund if refund else 0}
    Confidence Score: {confidence}
    System Guardrail Reason: {reason}
    Order Details: Status = {order_info.get('delivery_status', 'N/A')}, Value = ₹{order_info.get('value_inr', 'N/A')}

    Top Precedent Cases Matched:
    {precedents_str}

    Instructions:
    1. Write a professional, polite, 2-3 sentence customer reply.
       - If status is 'auto_resolved', confirm the action (e.g. refund/redelivery/coupon) clearly.
       - If status is 'human_review', explain empathetically that a human specialist is reviewing it.
    2. Write a concise 1-2 sentence internal explanation answering: "Why this action?" citing the precedents and guardrails.

    Return JSON strictly in this format:
    {{
        "customer_reply": "...",
        "ai_explanation": "..."
    }}
    """

    last_error = None
    try:
        if provider == "gemini":
            from google.genai import types
            for model_name in get_gemini_models():
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(response_mime_type="application/json")
                    )
                    return parse_ai_response(response.text)
                except Exception as err:
                    last_error = err
                    continue
            raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")

        elif provider in ("openai", "groq"):
            res = client.chat.completions.create(
                model="gpt-4o-mini" if provider == "openai" else "llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return parse_ai_response(res.choices[0].message.content)

    except Exception as e:
        print(f"[AI Layer Error] Details: {e}")
        return generate_fallback(ticket_desc, decision)


def generate_fallback(ticket_desc, decision):
    """Fallback template generator when no API key is provided."""
    status = decision.get("status")
    action = decision.get("action")
    refund = decision.get("refund_amount")
    precedents = decision.get("precedents", [])

    if status == "auto_resolved":
        action_text = {
            "full_refund": f"a full refund of ₹{refund}",
            "partial_refund": f"a partial refund of ₹{refund}",
            "refund_reissue": f"a reissued refund of ₹{refund}",
            "redelivery": "a free redelivery",
            "coupon": "a compensation coupon",
            "apology_no_action": "our sincere apologies",
        }.get(action, "an appropriate resolution")

        reply = (
            f"Hi, thanks for reaching out regarding '{ticket_desc}'. "
            f"Based on {len(precedents)} similar resolved cases in our system, "
            f"we've processed {action_text} for you right away!"
        )
        explanation = f"Auto-resolved with action '{action}' because top precedent tickets matched with high similarity."
    else:
        reply = (
            f"Hi, thanks for reaching out about '{ticket_desc}'. "
            f"We are reviewing your request closely and a customer support agent "
            f"will follow up with you shortly."
        )
        explanation = f"Queued for human review. Reason: {decision.get('reason')}."

    return {
        "customer_reply": reply,
        "ai_explanation": explanation
    }
