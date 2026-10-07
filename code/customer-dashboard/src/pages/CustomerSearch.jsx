import { useState } from "react";
import { api } from "../api";

function CustomerSearch() {
  const [customerId, setCustomerId] = useState("");
  const [customer, setCustomer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const searchCustomer = async () => {
    if (!customerId.trim()) {
      setError("Please enter a customer ID");
      return;
    }

    setLoading(true);
    setError("");
    setCustomer(null);

    try {
      const response = await api.get(
        `/customer/${customerId.trim()}`,
        {
          headers: {
            "X-API-Key": import.meta.env.VITE_API_KEY,
          },
        }
      );

      setCustomer(response.data);
    } catch (err) {
      if (err.response?.status === 404) {
        setError("Customer not found");
      } else {
        setError("Failed to fetch customer");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Customer Search</h2>

      <input
        type="text"
        placeholder="Enter Customer ID"
        value={customerId}
        onChange={(e) => setCustomerId(e.target.value)}
      />

      <button onClick={searchCustomer}>
        Search
      </button>

      {loading && <p>Loading...</p>}

      {error && <p>{error}</p>}

      {customer && (
        <div>
          <h3>Customer Details</h3>

          <p>Customer ID: {customer.customer_id}</p>
          <p>Tenure: {customer.tenure}</p>
          <p>Contract: {customer.contract_type}</p>
          <p>Internet Service: {customer.internet_service}</p>
          <p>Monthly Charges: {customer.monthly_charges}</p>

          <p>
            Churn Status:{" "}
            <span
              style={{
                backgroundColor:
                  customer.churn === 1 ? "red" : "green",
                color: "white",
                padding: "5px",
              }}
            >
              {customer.churn === 1 ? "Churned" : "Active"}
            </span>
          </p>
        </div>
      )}
    </div>
  );
}

export default CustomerSearch;