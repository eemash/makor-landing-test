import React, { useEffect, useState } from "react";
import MetricCard from "./components/MetricCard";
import OrdersChart from "./components/OrdersChart";
import LTVChart from "./components/LTVChart";
import RetentionTable from "./components/RetentionTable";
import RevenueChart from "./components/RevenueChart";

function App() {
  const [summary, setSummary] = useState(null);
  const [orders, setOrders] = useState([]);
  const [retention, setRetention] = useState([]);
  const [ltvDist, setLtvDist] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([
      fetch("/api/summary").then((r) => r.json()),
      fetch("/api/orders").then((r) => r.json()),
      fetch("/api/retention").then((r) => r.json()),
      fetch("/api/ltv-distribution").then((r) => r.json()),
    ])
      .then(([summaryData, ordersData, retentionData, ltvData]) => {
        setSummary(summaryData);
        setOrders(ordersData);
        setRetention(retentionData);
        setLtvDist(ltvData);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="loading">Loading dashboard...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Makor Coffee - LTV Dashboard</h1>
        <p>Customer lifetime value, orders, and retention analytics</p>
      </div>

      <div className="metrics-grid">
        <MetricCard
          label="Estimated LTV"
          value={`$${summary.estimated_ltv.toLocaleString()}`}
        />
        <MetricCard
          label="Total Orders"
          value={summary.total_orders.toLocaleString()}
        />
        <MetricCard
          label="Total Revenue"
          value={`$${summary.total_revenue.toLocaleString()}`}
        />
        <MetricCard
          label="Avg Order Value"
          value={`$${summary.avg_order_value.toLocaleString()}`}
        />
        <MetricCard
          label="Repeat Customer Rate"
          value={`${summary.repeat_customer_rate}%`}
        />
        <MetricCard
          label="Total Customers"
          value={summary.total_customers.toLocaleString()}
        />
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3>Orders Over Time</h3>
          <OrdersChart data={orders} />
        </div>
        <div className="chart-card">
          <h3>Monthly Revenue</h3>
          <RevenueChart data={orders} />
        </div>
        <div className="chart-card">
          <h3>LTV Distribution</h3>
          <LTVChart data={ltvDist} />
        </div>
      </div>

      <div className="retention-section">
        <h3>Cohort Retention</h3>
        <RetentionTable data={retention} />
      </div>
    </div>
  );
}

export default App;
