"use client";

import { useState } from "react";
import ConfigPanel from "@/components/ConfigPanel";
import ChartDisplay from "@/components/ChartDisplay";

export default function Home() {
  const [data, setData] = useState<any[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [currentCountry, setCurrentCountry] = useState("UK"); // Track current form state for UI
  const [config, setConfig] = useState({
    country: "UK",
    metric: "mtr",
    view: "absolute",
    maxChildren: 3,
    year: 2025,
    region: "LONDON",
    rent: 12000,
    childcarePerChild: 12000,
  });
  // Derive marginal values client-side (change per additional child)
  // Returns data for ALL child counts (0, 1, 2, 3...) with marginal values for 1+
  const deriveMarginals = (rawData: any[]) => {
    // Group by income
    const incomeMap = new Map<number, any[]>();
    for (const d of rawData) {
      if (!incomeMap.has(d.income)) {
        incomeMap.set(d.income, []);
      }
      incomeMap.get(d.income)!.push(d);
    }

    const result: any[] = [];
    for (const [income, items] of incomeMap) {
      // Sort by num_children
      items.sort((a, b) => a.num_children - b.num_children);

      for (let i = 0; i < items.length; i++) {
        const current = items[i];
        if (i === 0) {
          // num_children = 0, include absolute values but no marginal values
          result.push({
            income: current.income,
            num_children: current.num_children,
            net_income: current.net_income,
            mtr: current.mtr,
            // No marginal values for 0 children
          });
        } else {
          const prev = items[i - 1];
          result.push({
            income: current.income,
            num_children: current.num_children,
            net_income: current.net_income,
            mtr: current.mtr,
            marginal_benefit: current.net_income - prev.net_income,
            marginal_mtr: current.mtr - prev.mtr,
          });
        }
      }
    }
    return result;
  };

  // Smooth marginal MTR using centered moving average (reduces noise from numerical gradients)
  const smoothMarginalMtr = (data: any[], windowSize: number = 20) => {
    // Separate data with and without marginal_mtr (0 children has no marginal values)
    const withMarginal = data.filter(d => d.marginal_mtr !== undefined);
    const withoutMarginal = data.filter(d => d.marginal_mtr === undefined);

    // Group by num_children (only those with marginal values)
    const childrenCounts = [...new Set(withMarginal.map(d => d.num_children))].sort((a, b) => a - b);

    const smoothed: any[] = [];
    for (const numChildren of childrenCounts) {
      const childData = withMarginal
        .filter(d => d.num_children === numChildren)
        .sort((a, b) => a.income - b.income);

      const values = childData.map(d => d.marginal_mtr);

      // Apply centered moving average
      const smoothedValues = values.map((_, i) => {
        const start = Math.max(0, i - Math.floor(windowSize / 2));
        const end = Math.min(values.length, i + Math.floor(windowSize / 2) + 1);
        const slice = values.slice(start, end);
        const avg = slice.reduce((sum, v) => sum + v, 0) / slice.length;
        return Math.max(-1, Math.min(1, avg)); // Clip to [-1, 1]
      });

      for (let i = 0; i < childData.length; i++) {
        smoothed.push({
          ...childData[i],
          marginal_mtr: smoothedValues[i],
        });
      }
    }

    // Return both: data without marginal (0 children) + smoothed data
    return [...withoutMarginal, ...smoothed];
  };

  const handleCalculate = async (newConfig: any) => {
    console.log("handleCalculate called with:", newConfig);
    setLoading(true);
    setConfig(newConfig);
    setCurrentCountry(newConfig.country);

    try {
      // Single API call using /all endpoint
      const endpoint = newConfig.country === "US" ? "/calculate/us/all" : "/calculate/uk/all";
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "https://maxghenis--marginal-child-api-fastapi-app.modal.run";
      const url = `${apiBase}${endpoint}`;

      const payload = {
        max_children: newConfig.maxChildren,
        year: newConfig.year,
        ...(newConfig.country === "UK" ? {
          region: newConfig.region,
          rent: newConfig.rent,
          childcare_per_child: newConfig.childcarePerChild,
        } : {
          marital_status: newConfig.maritalStatus || "single",
          state_code: newConfig.stateCode || "CA",
          spouse_income: newConfig.spouseIncome || 0,
          include_health_benefits: newConfig.includeHealthBenefits !== false,
        }),
      };

      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const result = await response.json();

      // Derive marginal values client-side
      let processedData = deriveMarginals(result.data);

      // Apply smoothing to marginal_mtr
      processedData = smoothMarginalMtr(processedData, 20);

      console.log("Processed data length:", processedData.length);
      setData(processedData);
    } catch (error) {
      console.error("Calculation error:", error);
      alert(`Error: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white font-inter">
      <header className="border-b border-gray-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-semibold text-[#319795]">
            The Marginal Child
          </h1>
          <p className="mt-2 text-gray-600">
            {currentCountry === "UK" ? "Analyse" : "Analyze"} marginal tax rates and benefits by number of children
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          <div className="lg:col-span-1">
            <ConfigPanel
              onCalculate={handleCalculate}
              initialConfig={config}
              hasData={data !== null}
              onCountryChange={setCurrentCountry}
            />
          </div>

          <div className="lg:col-span-3">
            {loading && (
              <div className="flex flex-col items-center justify-center h-96">
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-[#319795] mb-4"></div>
                <div className="text-lg text-gray-500">Calculating...</div>
              </div>
            )}

            {!loading && data && data.length > 0 && (
              <ChartDisplay data={data} config={config} />
            )}

            {!loading && !data && (
              <div className="flex items-center justify-center h-96 text-gray-400">
                Configure options and click Calculate
              </div>
            )}
          </div>
        </div>
      </main>

      <footer className="mt-16 border-t border-gray-200 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 text-center text-gray-600">
          Powered by <span className="font-semibold text-[#319795]">PolicyEngine</span>
        </div>
      </footer>
    </div>
  );
}
