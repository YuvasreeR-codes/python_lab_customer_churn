import { useState } from "react";
import { api } from "../api";

function ChurnPrediction() {
  // const [form, setForm] = useState({
  //   tenure: "",
  //   monthly_charges: "",
  //   contract_type: "Month-to-month",
  //   service_count: "",
  // });
  const [form, setForm] = useState({
  tenure: "",
  monthly_charges: "",
  contract_type: "Month-to-month",
  service_count: "",
  has_streaming_bundle: "0",
  auto_pay_flag: "0",
  internet_service: "DSL",
});

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;

    setForm({
      ...form,
      [name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await api.post(
        "/predict-churn",
        // {
        //   tenure: Number(form.tenure),
        //   monthly_charges: Number(form.monthly_charges),
        //   contract_type: form.contract_type,
        //   service_count: Number(form.service_count),
        // },
        {
  tenure: Number(form.tenure),

  monthly_charges: Number(
    form.monthly_charges
  ),

  contract_type: form.contract_type,

  service_count: Number(
    form.service_count
  ),

  has_streaming_bundle: Number(
    form.has_streaming_bundle
  ),

  auto_pay_flag: Number(
    form.auto_pay_flag
  ),

  internet_service: form.internet_service,
},
        {
          headers: {
            "X-API-Key": import.meta.env.VITE_API_KEY,
          },
        }
      );

      setResult(response.data);
    } catch (err) {
      console.error(err);

      // Pydantic 422 validation error
      if (err.response?.status === 422) {
        const validationErrors = err.response.data.detail;

        if (Array.isArray(validationErrors)) {
          setError(
            validationErrors
              .map((item) => item.msg)
              .join(", ")
          );
        } else {
          setError("Validation error");
        }
      } else {
        setError("Failed to get churn prediction");
      }
    } finally {
      setLoading(false);
    }
  };

  // Determine risk level
  const getRiskLevel = (score) => {
    if (score < 0.3) {
      return {
        text: "Low Risk",
        color: "green",
      };
    }

    if (score <= 0.6) {
      return {
        text: "Medium Risk",
        color: "orange",
      };
    }

    return {
      text: "High Risk",
      color: "red",
    };
  };

  return (
    <div>
      <h1>Churn Prediction</h1>

      <p>
        Enter customer information to predict the likelihood
        of churn.
      </p>

      <form onSubmit={handleSubmit}>
        {/* Tenure */}
        <div>
          <label>Tenure (months)</label>

          <input
            type="number"
            name="tenure"
            value={form.tenure}
            onChange={handleChange}
          />
        </div>

        {/* Monthly Charges */}
        <div>
          <label>Monthly Charges</label>

          <input
            type="number"
            step="0.01"
            name="monthly_charges"
            value={form.monthly_charges}
            onChange={handleChange}
          />
        </div>

        {/* Contract Type */}
        <div>
          <label>Contract Type</label>

          <select
            name="contract_type"
            value={form.contract_type}
            onChange={handleChange}
          >
            <option value="Month-to-month">
              Month-to-month
            </option>

            <option value="One year">
              One year
            </option>

            <option value="Two year">
              Two year
            </option>
          </select>
        </div>

        {/* Service Count */}
        <div>
          <label>Service Count</label>

          <input
            type="number"
            name="service_count"
            min="0"
            max="6"
            value={form.service_count}
            onChange={handleChange}
          />
        </div>


        <div>
  <label>Streaming Bundle</label>

  <select
    name="has_streaming_bundle"
    value={form.has_streaming_bundle}
    onChange={handleChange}
  >
    <option value="0">No</option>
    <option value="1">Yes</option>
  </select>
</div>
<div>
  <label>Auto Pay</label>

  <select
    name="auto_pay_flag"
    value={form.auto_pay_flag}
    onChange={handleChange}
  >
    <option value="0">No</option>
    <option value="1">Yes</option>
  </select>
</div>
<div>
  <label>Internet Service</label>

  <select
    name="internet_service"
    value={form.internet_service}
    onChange={handleChange}
  >
    <option value="DSL">DSL</option>
    <option value="Fiber optic">Fiber optic</option>
    <option value="No">No Internet</option>
  </select>
</div>

        <button type="submit" disabled={loading}>
          {loading ? "Predicting..." : "Predict Churn"}
        </button>
      </form>

      {/* Error */}
      {error && (
        <div>
          <p>{error}</p>
        </div>
      )}

      {/* Result */}
      {result && (
        <PredictionResult result={result} getRiskLevel={getRiskLevel} />
      )}
    </div>
  );
}

function PredictionResult({ result, getRiskLevel }) {
  const risk = getRiskLevel(result.risk_score);

  return (
    <div
      style={{
        marginTop: "30px",
        padding: "20px",
        border: `3px solid ${risk.color}`,
        borderRadius: "8px",
      }}
    >
      <h2>Prediction Result</h2>

      <h3
        style={{
          color: risk.color,
        }}
      >
        {risk.text}
      </h3>

      <p>
        <strong>Risk Score:</strong>{" "}
        {(result.risk_score * 100).toFixed(1)}%
      </p>

      <p>
        <strong>Prediction:</strong>{" "}
        {result.prediction}
      </p>

      <p>
        <strong>Confidence Level:</strong>{" "}
        {(result.confidence * 100).toFixed(1)}%
      </p>

      {result.note && (
        <p>
          <strong>Note:</strong> {result.note}
        </p>
      )}
    </div>
  );
}

// function getConfidenceLevel(score) {
//   const distanceFromMiddle = Math.abs(score - 0.5);

//   if (distanceFromMiddle >= 0.3) {
//     return "High";
//   }

//   if (distanceFromMiddle >= 0.15) {
//     return "Medium";
//   }

//   return "Low";
// }

export default ChurnPrediction;