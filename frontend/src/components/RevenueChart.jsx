import React from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

function RevenueChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis
          dataKey="month"
          tick={{ fontSize: 12 }}
          tickFormatter={(v) => v.slice(5)}
        />
        <YAxis
          tick={{ fontSize: 12 }}
          tickFormatter={(v) => `$${v}`}
        />
        <Tooltip
          formatter={(value) => [`$${value.toLocaleString()}`, "Revenue"]}
          labelFormatter={(label) => `Month: ${label}`}
        />
        <Area
          type="monotone"
          dataKey="revenue"
          stroke="#10b981"
          fill="#10b981"
          fillOpacity={0.15}
          strokeWidth={2}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export default RevenueChart;
