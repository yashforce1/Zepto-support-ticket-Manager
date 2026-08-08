export default function OrderContext({ order }) {
    if (!order) return null;
  
    return (
      <div className="order-context">
        <h4>Order Context</h4>
        {!order.found ? (
          <p className="order-not-found">
            Order ID "{order.order_id}" not found — decision defaults to human review.
          </p>
        ) : (
          <table>
            <tbody>
              <tr><td>Order ID</td><td>{order.order_id}</td></tr>
              <tr>
                <td>Status</td>
                <td className={`status-text ${order.delivery_status}`}>{order.delivery_status}</td>
              </tr>
              <tr><td>Order Value</td><td>₹{order.value_inr}</td></tr>
              <tr><td>Items</td><td>{order.items}</td></tr>
              <tr><td>Delivery Time</td><td>{order.delivery_time_min} min</td></tr>
            </tbody>
          </table>
        )}
      </div>
    );
  }