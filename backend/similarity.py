from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from data_loader import load_data


def build_vectorizer(resolved):
    """Fit TF-IDF on all historical ticket descriptions."""
    vectorizer = TfidfVectorizer(stop_words="english")
    resolved_vectors = vectorizer.fit_transform(resolved["description"])
    return vectorizer, resolved_vectors


def find_top_matches(new_description, vectorizer, resolved_vectors, resolved, top_k=3):
    """Return top-k most similar resolved tickets for a new ticket description."""
    new_vector = vectorizer.transform([new_description])
    scores = cosine_similarity(new_vector, resolved_vectors)[0]

    top_indices = scores.argsort()[::-1][:top_k]

    matches = []
    for idx in top_indices:
        row = resolved.iloc[idx]
        matches.append({
            "ticket_id": str(row["ticket_id"]),
            "description": str(row["description"]),
            "resolution_action": str(row["resolution_action"]),
            "resolution_note": str(row["resolution_note"]),
            "similarity": round(float(scores[idx]), 4)
        })
    return matches

if __name__ == "__main__":
    resolved, new_tickets_full, orders = load_data()
    vectorizer, resolved_vectors = build_vectorizer(resolved)

    # Test on the first 3 new tickets
    for i in range(3):
        ticket = new_tickets_full.iloc[i]
        print(f"\n===== NEW TICKET {ticket['ticket_id']} =====")
        print("Description:", ticket["description"])
        print("Order status:", ticket["delivery_status"], "| Value:", ticket["value_inr"])

        matches = find_top_matches(ticket["description"], vectorizer, resolved_vectors, resolved)
        print("\nTop 3 similar past tickets:")
        for m in matches:
            print(f"  [{m['similarity']}] {m['ticket_id']} -> {m['resolution_action']} | \"{m['description']}\"")