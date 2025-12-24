"use client";

import { useState } from "react";
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

// App-v2 colors - gradient from gray to teal
const COLORS = ["#9CA3AF", "#81E6D9", "#4FD1C5", "#319795"];

interface ChartDisplayProps {
  data: any[];
  config: any;
}

export default function ChartDisplay({ data, config }: ChartDisplayProps) {
  const [metric, setMetric] = useState<"net_income" | "mtr">("net_income");
  const [view, setView] = useState<"value" | "incremental">("incremental");

  const currency = config.country === "UK" ? "£" : "$";
  const xTicks = config.country === "UK"
    ? [0, 25000, 50000, 75000, 100000, 125000, 150000, 175000, 200000]
    : [0, 50000, 100000, 150000, 200000, 250000, 300000, 350000, 400000, 450000, 500000];

  // Group data by num_children
  const childrenCounts = [...new Set(data.map(d => d.num_children))].sort();

  // Determine which value key to use based on metric and view
  const getValueKey = () => {
    if (metric === "net_income") {
      return view === "value" ? "net_income" : "marginal_benefit";
    } else {
      return view === "value" ? "mtr" : "marginal_mtr";
    }
  };

  const valueKey = getValueKey();
  const isPercent = metric === "mtr";

  // Transform data for Recharts
  const chartData = data
    .filter(d => d.num_children === childrenCounts[0])
    .map(d => ({ income: d.income }));

  childrenCounts.forEach(numChildren => {
    const childData = data.filter(d => d.num_children === numChildren);
    childData.forEach((d, i) => {
      if (chartData[i]) {
        let value = d[valueKey] || 0;
        // Clip MTR values to [-1, 1]
        if (isPercent) {
          value = Math.max(-1, Math.min(1, value));
        }
        chartData[i][`child_${numChildren}`] = value;
      }
    });
  });

  const formatValue = (value: number) => {
    if (isPercent) {
      return view === "incremental"
        ? `${(value * 100).toFixed(1)}pp`
        : `${(value * 100).toFixed(1)}%`;
    }
    return `${currency}${Math.round(value).toLocaleString()}`;
  };

  const getTitle = () => {
    const metricLabel = metric === "net_income" ? "Net Income" : "Marginal Tax Rate";
    if (view === "value") {
      return `${metricLabel} by Number of Children`;
    }
    return `${metricLabel} Change per Additional Child`;
  };

  const getYAxisLabel = () => {
    if (metric === "net_income") {
      return view === "value" ? `Net Income (${currency})` : `Change (${currency})`;
    }
    return view === "value" ? "MTR" : "Change (pp)";
  };

  // For value view, show "0 children", "1 child", etc. For incremental, show "Child 1", "Child 2", etc.
  const getLegendLabel = (numChildren: number) => {
    if (view === "value") {
      return numChildren === 1 ? "1 child" : `${numChildren} children`;
    }
    return `Child ${numChildren}`;
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      {/* Two tab rows */}
      <div className="space-y-3 mb-6">
        {/* Metric tabs */}
        <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
          <button
            onClick={() => setMetric("net_income")}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              metric === "net_income"
                ? "bg-white text-[#319795] shadow-sm"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            Net Income
          </button>
          <button
            onClick={() => setMetric("mtr")}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              metric === "mtr"
                ? "bg-white text-[#319795] shadow-sm"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            Marginal Tax Rate
          </button>
        </div>

        {/* View tabs */}
        <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
          <button
            onClick={() => setView("value")}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              view === "value"
                ? "bg-white text-[#319795] shadow-sm"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            By # Children
          </button>
          <button
            onClick={() => setView("incremental")}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              view === "incremental"
                ? "bg-white text-[#319795] shadow-sm"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            Per Additional Child
          </button>
        </div>
      </div>

      <h2 className="text-xl font-semibold text-gray-900 mb-4">{getTitle()}</h2>

      <ResponsiveContainer width="100%" height={420}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis
            dataKey="income"
            tickFormatter={(value) => `${currency}${Math.round(value / 1000)}k`}
            stroke="#6B7280"
            style={{ fontFamily: "Inter, sans-serif", fontSize: "12px" }}
            ticks={xTicks}
            label={{
              value: "Earnings",
              position: "insideBottom",
              offset: -5,
              style: { fontFamily: "Inter, sans-serif", fontSize: "12px", fill: "#6B7280" }
            }}
          />
          <YAxis
            tickFormatter={isPercent ? (v) => `${(v * 100).toFixed(0)}%` : (v) => `${currency}${Math.round(v / 1000)}k`}
            stroke="#6B7280"
            style={{ fontFamily: "Inter, sans-serif", fontSize: "12px" }}
            domain={isPercent ? [-1, 1] : ["auto", "auto"]}
            ticks={isPercent ? [-1, -0.5, 0, 0.5, 1] : undefined}
            label={{
              value: getYAxisLabel(),
              angle: -90,
              position: "insideLeft",
              style: { fontFamily: "Inter, sans-serif", fontSize: "12px", fill: "#6B7280" }
            }}
          />
          <Tooltip
            formatter={formatValue}
            labelFormatter={(value) => `Earnings: ${currency}${Number(value).toLocaleString()}`}
            contentStyle={{
              fontFamily: "Inter, sans-serif",
              backgroundColor: "white",
              border: "1px solid #E5E7EB",
              borderRadius: "0.375rem",
            }}
          />
          <Legend
            wrapperStyle={{ fontFamily: "Inter, sans-serif", fontSize: "12px" }}
            formatter={(value) => {
              const num = parseInt(value.replace("child_", ""));
              return getLegendLabel(num);
            }}
          />
          {childrenCounts.map((numChildren, index) => (
            <Line
              key={numChildren}
              type="monotone"
              dataKey={`child_${numChildren}`}
              name={`child_${numChildren}`}
              stroke={COLORS[index % COLORS.length]}
              strokeWidth={2}
              dot={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>

      <div className="mt-4 flex justify-between items-center">
        <p className="text-xs text-gray-500">
          {view === "incremental"
            ? "Shows the change from having one additional child"
            : "Shows values for households with different numbers of children"}
        </p>
        <img
          src="https://raw.githubusercontent.com/PolicyEngine/policyengine-app/master/src/images/logos/policyengine/teal.png"
          alt="PolicyEngine"
          className="h-6"
        />
      </div>
    </div>
  );
}
