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
import { colors } from "@policyengine/design-system/tokens";
import { chartColors } from "@policyengine/design-system/charts";

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

const FONT_FAMILY = "Inter, sans-serif";

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
  const childNumbers = [...new Set(data.map((d) => d.num_children))].sort();

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
        style={{ fontFamily: FONT_FAMILY }}
      >
        Net income change from taxes and benefits per additional child
      </h2>
      <ResponsiveContainer width="100%" height={500}>
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke={colors.border.light} />
          <XAxis
            dataKey="income"
            tickFormatter={formatCurrency}
            label={{
              value: "Earnings",
              position: "insideBottom",
              offset: -5,
              style: { fontFamily: FONT_FAMILY, fill: colors.gray[700] },
            }}
            tick={{ fontFamily: FONT_FAMILY, fontSize: 12 }}
          />
          <YAxis
            tickFormatter={formatCurrency}
            label={{
              value: "Net income change for additional child",
              angle: -90,
              position: "insideLeft",
              offset: 10,
              style: {
                fontFamily: FONT_FAMILY,
                fill: colors.gray[700],
                textAnchor: "middle",
              },
            }}
            tick={{ fontFamily: FONT_FAMILY, fontSize: 12 }}
            domain={[0, "auto"]}
          />
          <Tooltip
            formatter={((value: number, name: string) => [
              formatCurrency(value ?? 0),
              String(name ?? ""),
            ]) as any}
            labelFormatter={((label: number) =>
              `Earnings: ${formatCurrency(Number(label) || 0)}`) as any}
            contentStyle={{
              fontFamily: FONT_FAMILY,
              borderRadius: "8px",
              border: `1px solid ${colors.border.light}`,
            }}
          />
          <Legend
            wrapperStyle={{ fontFamily: FONT_FAMILY }}
          />
          {childNumbers.map((childNum, index) => (
            <Line
              key={childNum}
              type="monotone"
              dataKey={`child${childNum}`}
              name={`Child ${childNum}`}
              stroke={chartColors.series[index % chartColors.series.length]}
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
