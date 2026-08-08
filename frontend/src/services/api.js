const API_URL = "http://localhost:8000";

export async function analyzeTicket(description, orderId) {
  const res = await fetch(`${API_URL}/process_ticket`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      description,
      order_id: orderId || null,
    }),
  });
  if (!res.ok) throw new Error("Failed to analyze ticket");
  return res.json();
}

export async function getBoard() {
  const res = await fetch(`${API_URL}/board`);
  if (!res.ok) throw new Error("Failed to fetch board");
  return res.json();
}