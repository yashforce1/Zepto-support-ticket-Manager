import pandas as pd

# Load the three CSVs
resolved = pd.read_csv("data/resolved_tickets.csv")
new_tickets = pd.read_csv("data/new_tickets.csv")
orders = pd.read_csv("data/orders_context.csv")

print("===== RESOLVED TICKETS =====")
print("Shape:", resolved.shape)
print("Columns:", list(resolved.columns))
print(resolved.head(3))
print()

print("===== NEW TICKETS =====")
print("Shape:", new_tickets.shape)
print("Columns:", list(new_tickets.columns))
print(new_tickets.head(3))
print()

print("===== ORDERS CONTEXT =====")
print("Shape:", orders.shape)
print("Columns:", list(orders.columns))
print(orders.head(3))

print("===== UNIQUE VALUES (for decision logic) =====")
print("Categories in resolved tickets:")
print(resolved['category'].unique())
print()

print("Resolution actions taken historically:")
print(resolved['resolution_action'].unique())
print()

print("Delivery statuses in orders:")
print(orders['delivery_status'].unique())
print()

print("Any missing values?")
print("Resolved tickets nulls:\n", resolved.isnull().sum())
print("New tickets nulls:\n", new_tickets.isnull().sum())
print("Orders nulls:\n", orders.isnull().sum())