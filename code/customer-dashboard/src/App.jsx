// import { useEffect, useState } from "react";
// import { api } from "./api";

// function App() {
//   const [data, setData] = useState(null);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState("");

//   useEffect(() => {
//     const fetchChurnSummary = async () => {
//       try {
//         const response = await api.get("/churn/summary", {
//           headers: {
//             "X-API-Key": import.meta.env.VITE_API_KEY,
//           },
//         });

//         console.log("API response:", response.data);
//         setData(response.data);
//       } catch (err) {
//         console.error("API error:", err);
//         setError("Failed to load churn summary");
//       } finally {
//         setLoading(false);
//       }
//     };

//     fetchChurnSummary();
//   }, []);

//   if (loading) {
//     return <h2>Loading...</h2>;
//   }

//   if (error) {
//     return <h2>{error}</h2>;
//   }

//   return (
//     <div>
//       <h1>Customer Retention Dashboard</h1>

//       <pre>
//         {JSON.stringify(data, null, 2)}
//       </pre>
//     </div>
//   );
// }

// export default App;

import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import CustomerSearch from "./pages/CustomerSearch";
import ChurnSummary from "./pages/ChurnSummary";
import HighRiskCustomers from "./pages/HighRiskCustomers";
import ChurnPrediction from "./pages/ChurnPrediction";

function App() {
  const linkStyle = {
    color: "#e5e7eb",
    textDecoration: "none",
    padding: "10px 16px",
    borderRadius: "8px",
    fontSize: "14px",
    fontWeight: "500",
  };

  return (
    <BrowserRouter>
      <div
        style={{
          minHeight: "100vh",
          background: "#f4f6f9",
          fontFamily: "Arial, sans-serif",
        }}
      >
        {/* Navbar */}
        <header
          style={{
            background: "#172033",
            color: "white",
            padding: "18px 35px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            boxShadow: "0 3px 10px rgba(0,0,0,0.15)",
          }}
        >
          <div
            style={{
              fontSize: "22px",
              fontWeight: "bold",
            }}
          >
            📊 Churn Analytics
          </div>

          <nav
            style={{
              display: "flex",
              gap: "8px",
            }}
          >
            <Link style={linkStyle} to="/customer-search">
              Customer Search
            </Link>

            <Link style={linkStyle} to="/churn-summary">
              Churn Summary
            </Link>

            <Link style={linkStyle} to="/High-Risk-Cust">
              High Risk Customers
            </Link>

            <Link style={linkStyle} to="/Churn-predict">
              Churn Prediction
            </Link>
          </nav>
        </header>

        {/* Page Content */}
        <main
          style={{
            maxWidth: "1200px",
            margin: "35px auto",
            padding: "0 25px",
          }}
        >
          <Routes>
            <Route
              path="/customer-search"
              element={<CustomerSearch />}
            />

            <Route
              path="/churn-summary"
              element={<ChurnSummary />}
            />

            <Route
              path="/High-Risk-Cust"
              element={<HighRiskCustomers />}
            />

            <Route
              path="/Churn-predict"
              element={<ChurnPrediction />}
            />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;