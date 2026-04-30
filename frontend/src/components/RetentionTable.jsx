import React from "react";

function getCellColor(pct) {
  if (pct >= 80) return "#dcfce7";
  if (pct >= 50) return "#fef9c3";
  if (pct >= 25) return "#fed7aa";
  if (pct > 0) return "#fecaca";
  return "#f5f5f5";
}

function RetentionTable({ data }) {
  return (
    <div style={{ overflowX: "auto" }}>
      <table className="retention-table">
        <thead>
          <tr>
            <th>Cohort</th>
            <th>Customers</th>
            <th>Month 0</th>
            <th>Month 1</th>
            <th>Month 2</th>
            <th>Month 3</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row.cohort}>
              <td>{row.cohort}</td>
              <td>{row.customers}</td>
              {["month_0", "month_1", "month_2", "month_3"].map((key) => (
                <td key={key}>
                  <span
                    className="retention-cell"
                    style={{ backgroundColor: getCellColor(row[key]) }}
                  >
                    {row[key]}%
                  </span>
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default RetentionTable;
