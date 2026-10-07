import { useEffect, useState } from "react";
import { api } from "../api";

function ChurnSummary() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchChurnSummary = async () => {
      try {
        const response = await api.get("/churn/summary", {
          headers: {
            "X-API-Key": import.meta.env.VITE_API_KEY,
          },
        });

        setSummary(response.data);
      } catch (err) {
        console.error(err);
        setError("Failed to load churn summary");
      } finally {
        setLoading(false);
      }
    };

    fetchChurnSummary();
  }, []);

  if (loading) {
    return <h2>Loading...</h2>;
  }

  if (error) {
    return <h2>{error}</h2>;
  }

  return (
    <div>
      <h1>Churn Summary</h1>

      <p>
        This page shows overall customer churn and churn rates
        across different contract types.
      </p>

      {/* Metric Cards */}
      <div style={styles.metrics}>
        <div style={styles.card}>
          <h3>Total Customers</h3>
          <p>{summary.total_customers}</p>
        </div>

        <div style={styles.card}>
          <h3>Total Churned</h3>
          <p>{summary.total_churned}</p>
        </div>

        <div style={styles.card}>
          <h3>Churn Rate</h3>
          <p>
            {(summary.churn_rate * 100).toFixed(1)}%
          </p>
        </div>
      </div>

      {/* Contract Churn Table */}
      <h2>Churn Rate by Contract Type</h2>

      <table border="1" cellPadding="10">
        <thead>
          <tr>
            <th>Contract Type</th>
            <th>Churn Rate</th>
            <th>Visual</th>
          </tr>
        </thead>

        <tbody>
          {summary.churn_rate_by_contract.map((item) => (
            <tr key={item.contract_type}>
              <td>{item.contract_type}</td>

              <td>
                {(item.churn_rate * 100).toFixed(1)}%
              </td>

              <td>
                <div style={styles.barContainer}>
                  <div
                    style={{
                      ...styles.bar,
                      width: `${item.churn_rate * 100}%`,
                    }}
                  />
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

const styles = {
  metrics: {
    display: "flex",
    gap: "20px",
    margin: "20px 0",
  },

  card: {
    border: "1px solid #ddd",
    borderRadius: "8px",
    padding: "20px",
    width: "200px",
  },

  barContainer: {
    width: "200px",
    height: "20px",
    backgroundColor: "#eee",
  },

  bar: {
    height: "20px",
    backgroundColor: "red",
  },
};

export default ChurnSummary;