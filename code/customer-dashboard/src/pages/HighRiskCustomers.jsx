import { useEffect, useState } from "react";
import { api } from "../api";

function HighRiskCustomers() {
  const [customers, setCustomers] = useState([]);
  const [limit, setLimit] = useState(50);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [sortAscending, setSortAscending] = useState(true);

  const fetchHighRiskCustomers = async (newLimit) => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/customers/high-risk", {
        params: {
          limit: newLimit,
        },
        headers: {
          "X-API-Key": import.meta.env.VITE_API_KEY,
        },
      });

      setCustomers(response.data);
    } catch (err) {
      console.error(err);
      setError("Failed to load high-risk customers");
    } finally {
      setLoading(false);
    }
  };

  // Fetch first 50 when page loads
  useEffect(() => {
    fetchHighRiskCustomers(50);
  }, []);

  // Load 50 more
  const loadMore = () => {
    const newLimit = limit + 50;

    setLimit(newLimit);
    fetchHighRiskCustomers(newLimit);
  };

  // Sort by tenure
  const sortedCustomers = [...customers].sort((a, b) => {
    if (sortAscending) {
      return a.tenure - b.tenure;
    }

    return b.tenure - a.tenure;
  });

  const toggleSort = () => {
    setSortAscending(!sortAscending);
  };

  if (loading) {
    return <h2>Loading...</h2>;
  }

  if (error) {
    return <h2>{error}</h2>;
  }

  return (
    <div>
      <h1>High-Risk Customers</h1>

      <p>
        Customers identified as high-risk using explainable
        business rules.
      </p>

      {/* Count Banner */}
      <div>
        {customers.length} high-risk customers identified
      </div>

      {/* No Results */}
      {customers.length === 0 ? (
        <p>No high-risk customers found</p>
      ) : (
        <>
          <table border="1" cellPadding="10">
            <thead>
              <tr>
                <th>Customer ID</th>

                <th onClick={toggleSort} style={{ cursor: "pointer" }}>
                  Tenure {sortAscending ? "↑" : "↓"}
                </th>

                <th>Monthly Charges</th>
                <th>Contract Type</th>
                <th>Risk Reason</th>
              </tr>
            </thead>

            <tbody>
              {sortedCustomers.map((customer) => (
                <tr key={customer.customer_id}>
                  <td>{customer.customer_id}</td>

                  <td>{customer.tenure}</td>

                  <td>
                    ${customer.monthly_charges.toFixed(2)}
                  </td>

                  <td>{customer.contract_type}</td>

                  <td>{customer.risk_reason}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Load More */}
          <button onClick={loadMore}>
            Load More
          </button>
        </>
      )}
    </div>
  );
}

export default HighRiskCustomers;