def decide_action(matches, order_info):
    # --- Guardrail: unknown/invalid order -> human ---
    if isinstance(order_info, dict) and not order_info.get("found", True):
        similarities = [m["similarity"] for m in matches]
        avg_similarity = float(sum(similarities) / len(similarities))
        return build_result("human_review", None, avg_similarity, matches,
                             "Order ID not found — cannot verify order context")

    similarities = [m["similarity"] for m in matches]
    avg_similarity = float(sum(similarities) / len(similarities))
    actions = [m["resolution_action"] for m in matches]
    ...

from collections import Counter

SIMILARITY_THRESHOLD = 0.3   # below this -> not confident enough, go to human
AGREEMENT_THRESHOLD = 0.6    # fraction of top-3 that must agree on same action


def decide_action(matches, order_info):
    similarities = [m["similarity"] for m in matches]
    avg_similarity = float(sum(similarities) / len(similarities))
    actions = [m["resolution_action"] for m in matches]

    action_counts = Counter(actions)
    top_action, top_count = action_counts.most_common(1)[0]
    agreement_ratio = top_count / len(actions)

    reason_flags = []

    # --- Guardrail: low similarity -> human ---
    if avg_similarity < SIMILARITY_THRESHOLD:
        return build_result("human_review", None, avg_similarity, matches,
                             "Low similarity to any precedent")

    # --- Guardrail: precedents disagree -> human ---
    if agreement_ratio < AGREEMENT_THRESHOLD:
        return build_result("human_review", None, avg_similarity, matches,
                             f"Precedents disagree on action ({dict(action_counts)})")

    chosen_action = top_action

    # --- Guardrail: escalation was the historical action -> human ---
    if chosen_action == "escalation":
        return build_result("human_review", "escalation", avg_similarity, matches,
                             "Historical precedent itself required escalation")

    # --- Guardrail: cancelled order blocks redelivery ---
    if chosen_action == "redelivery" and order_info["delivery_status"] == "cancelled":
        return build_result("human_review", chosen_action, avg_similarity, matches,
                             "Order is cancelled — cannot redeliver, needs human decision")

    #--- Guardrail: refund capped at order value ---
    refund_amount = None
    if chosen_action in ("full_refund", "partial_refund", "refund_reissue"):
        if chosen_action == "partial_refund":
            refund_amount = round(float(order_info["value_inr"]) * 0.5, 2)
        else:
            refund_amount = float(order_info["value_inr"])
        refund_amount = min(refund_amount, float(order_info["value_inr"]))

    return build_result("auto_resolved", chosen_action, avg_similarity, matches,
                         "High confidence, precedents agree", refund_amount)


def build_result(status, action, confidence, matches, reason, refund_amount=None):
    return {
        "status": status,                 # "auto_resolved" or "human_review"
        "action": action,
        "confidence": round(confidence, 4),
        "reason": reason,
        "refund_amount": refund_amount,
        "precedents": matches
    }


if __name__ == "__main__":
    from data_loader import load_data
    from similarity import build_vectorizer, find_top_matches

    resolved, new_tickets_full, orders = load_data()
    vectorizer, resolved_vectors = build_vectorizer(resolved)

    for i in range(len(new_tickets_full)):
        ticket = new_tickets_full.iloc[i]
        matches = find_top_matches(ticket["description"], vectorizer, resolved_vectors, resolved)
        decision = decide_action(matches, ticket)

        print(f"\n{ticket['ticket_id']} | \"{ticket['description']}\"")
        print(f"  -> {decision['status'].upper()} | action={decision['action']} | "
              f"confidence={decision['confidence']} | refund={decision['refund_amount']}")
        print(f"  reason: {decision['reason']}")






if __name__ == "__main__":
    # ... existing loop above ...

    print("\n\n===== MANUAL EDGE-CASE TESTS =====")

    # Test 1: low similarity (novel ticket) -> should go to human
    fake_matches_low_sim = [
        {"ticket_id": "H-X1", "description": "...", "resolution_action": "coupon", "resolution_note": "", "similarity": 0.1},
        {"ticket_id": "H-X2", "description": "...", "resolution_action": "coupon", "resolution_note": "", "similarity": 0.15},
        {"ticket_id": "H-X3", "description": "...", "resolution_action": "coupon", "resolution_note": "", "similarity": 0.05},
    ]
    fake_order = {"value_inr": 200, "delivery_status": "delivered"}
    print("Low similarity test:", decide_action(fake_matches_low_sim, fake_order)["status"])
    # expect: human_review

    # Test 2: precedents disagree -> should go to human
    fake_matches_disagree = [
        {"ticket_id": "H-Y1", "description": "...", "resolution_action": "full_refund", "resolution_note": "", "similarity": 0.9},
        {"ticket_id": "H-Y2", "description": "...", "resolution_action": "coupon", "resolution_note": "", "similarity": 0.85},
        {"ticket_id": "H-Y3", "description": "...", "resolution_action": "redelivery", "resolution_note": "", "similarity": 0.8},
    ]
    print("Disagreement test:", decide_action(fake_matches_disagree, fake_order)["status"])
    # expect: human_review