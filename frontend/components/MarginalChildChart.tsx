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

interface ApiDataPoint {
  income: number;
  num_children: number;
  marginal_benefit: number;
  net_income: number;
}

interface ChartDataPoint {
  income: number;
  [key: string]: number;
}

const SERIES_COLORS = ["#319795", "#0EA5E9", "#285E61", "#026AA2"];

const formatCurrency = (value: number) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);

interface MarginalChildChartProps {
  data: ApiDataPoint[];
}

export default function MarginalChildChart({ data }: MarginalChildChartProps) {
  // Get unique child numbers
  const childNumbers = [...new Set(data.map((d) => d.num_children))].sort();

  // Transform data into recharts format: { income, child1, child2, ... }
  const incomes = [...new Set(data.map((d) => d.income))].sort((a, b) => a - b);
  const chartData: ChartDataPoint[] = incomes.map((income) => {
    const point: ChartDataPoint = { income };
    childNumbers.forEach((childNum) => {
      const match = data.find(
        (d) => d.income === income && d.num_children === childNum
      );
      point[`child${childNum}`] = match ? match.marginal_benefit : 0;
    });
    return point;
  });

  return (
    <div className="rounded-lg bg-white p-6 shadow-sm">
      <h2
        className="mb-4 text-center text-lg font-semibold text-pe-gray-700"
        style={{ fontFamily: "Inter, sans-serif" }}
      >
        Net income change from taxes and benefits per additional child
      </h2>
      <ResponsiveContainer width="100%" height={500}>
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
          <XAxis
            dataKey="income"
            tickFormatter={formatCurrency}
            label={{
              value: "Earnings",
              position: "insideBottom",
              offset: -5,
              style: { fontFamily: "Inter, sans-serif", fill: "#344054" },
            }}
            tick={{ fontFamily: "Inter, sans-serif", fontSize: 12 }}
          />
          <YAxis
            tickFormatter={formatCurrency}
            label={{
              value: "Net income change for additional child",
              angle: -90,
              position: "insideLeft",
              offset: 10,
              style: {
                fontFamily: "Inter, sans-serif",
                fill: "#344054",
                textAnchor: "middle",
              },
            }}
            tick={{ fontFamily: "Inter, sans-serif", fontSize: 12 }}
            domain={[0, "auto"]}
          />
          <Tooltip
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            formatter={((value: any, name: any) => [
              formatCurrency(value ?? 0),
              String(name ?? ""),
            ]) as any}
            labelFormatter={((label: any) =>
              `Earnings: ${formatCurrency(Number(label) || 0)}`) as any}
            contentStyle={{
              fontFamily: "Inter, sans-serif",
              borderRadius: "8px",
              border: "1px solid #E2E8F0",
            }}
          />
          <Legend
            wrapperStyle={{ fontFamily: "Inter, sans-serif" }}
          />
          {childNumbers.map((childNum, index) => (
            <Line
              key={childNum}
              type="monotone"
              dataKey={`child${childNum}`}
              name={`Child ${childNum}`}
              stroke={SERIES_COLORS[index % SERIES_COLORS.length]}
              strokeWidth={3}
              dot={false}
              activeDot={{ r: 5 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
