import pandas as pd

def load_data():
    resolved = pd.read_csv("data/resolved_tickets.csv")
    new_tickets = pd.read_csv("data/new_tickets.csv")
    orders = pd.read_csv("data/orders_context.csv")

    # Join new_tickets with their order context
    new_tickets_full = new_tickets.merge(orders, on="order_id", how="left")

    return resolved, new_tickets_full, orders


if __name__ == "__main__":
    resolved, new_tickets_full, orders = load_data()
    print("===== NEW TICKETS + ORDER CONTEXT =====")
    print(new_tickets_full.shape)
    print(new_tickets_full.head(5))
    print()
    print("Any tickets with no matching order (null after merge)?")
    print(new_tickets_full.isnull().sum())