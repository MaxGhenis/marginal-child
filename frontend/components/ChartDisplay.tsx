"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

// App-v2 colors
const COLORS = ["#9CA3AF", "#81E6D9", "#4FD1C5", "#319795"];

interface ChartDisplayProps {
  data: any[];
  config: any;
}

export default function ChartDisplay({ data, config }: ChartDisplayProps) {
  // Group data by num_children
  const childrenCounts = [...new Set(data.map(d => d.num_children))].sort();

  // Transform data for Recharts format
  const chartData = data
    .filter(d => d.num_children === childrenCounts[0])
    .map(d => ({ income: d.income }));

  childrenCounts.forEach(numChildren => {
    const childData = data.filter(d => d.num_children === numChildren);
    childData.forEach((d, i) => {
      const valueKey = config.metric === "net_income"
        ? (config.view === "absolute" ? "net_income" : "marginal_benefit")
        : (config.view === "absolute" ? "mtr" : "marginal_mtr");

      chartData[i][`${numChildren}_children`] = d[valueKey];
    });
  });

  const currency = config.country === "UK" ? "£" : "$";
  const isMTR = config.metric === "mtr";
  const isPercent = isMTR;

  const formatValue = (value: number) => {
    if (isPercent) {
      return `${(value * 100).toFixed(1)}%`;
    }
    return `${currency}${value.toLocaleString()}`;
  };

  const getTitle = () => {
    const metricName = config.metric === "net_income" ? "Net Income" : "Marginal Tax Rate";
    const viewName = config.view === "absolute" ? "by Number of Children" : "Change per Additional Child";
    return `${metricName} ${viewName}`;
  };

  const getYAxisLabel = () => {
    if (config.metric === "net_income") {
      return config.view === "absolute"
        ? `Net Income (${currency})`
        : `Net Income Change (${currency})`;
    } else {
      return config.view === "absolute"
        ? "Marginal Tax Rate"
        : "MTR Change (pp)";
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-semibold text-gray-900 mb-6">{getTitle()}</h2>

      <ResponsiveContainer width="100%" height={500}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis
            dataKey="income"
            tickFormatter={(value) => `${currency}${(value / 1000).toFixed(0)}k`}
            stroke="#6B7280"
            style={{ fontFamily: "Inter, sans-serif" }}
          />
          <YAxis
            tickFormatter={isPercent ? (v) => `${(v * 100).toFixed(0)}%` : (v) => `${currency}${(v / 1000).toFixed(0)}k`}
            stroke="#6B7280"
            style={{ fontFamily: "Inter, sans-serif" }}
            domain={isPercent && config.view === "absolute" ? [0, 1] : ["auto", "auto"]}
          />
          <Tooltip
            formatter={formatValue}
            labelFormatter={(value) => `Income: ${currency}${value.toLocaleString()}`}
            contentStyle={{
              fontFamily: "Inter, sans-serif",
              backgroundColor: "white",
              border: "1px solid #E5E7EB",
              borderRadius: "0.375rem",
            }}
          />
          <Legend
            wrapperStyle={{ fontFamily: "Inter, sans-serif" }}
          />
          {childrenCounts.map((numChildren, index) => (
            <Line
              key={numChildren}
              type="monotone"
              dataKey={`${numChildren}_children`}
              name={`${numChildren} ${numChildren === 1 ? "child" : "children"}`}
              stroke={COLORS[index % COLORS.length]}
              strokeWidth={2.5}
              dot={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>

      <div className="mt-4 flex justify-end">
        <img
          src="https://raw.githubusercontent.com/PolicyEngine/policyengine-app/master/src/images/logos/policyengine/teal.png"
          alt="PolicyEngine"
          className="h-8"
        />
      </div>
    </div>
  );
}
