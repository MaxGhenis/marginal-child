"use client";

import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import Header from "../components/Header";
import InputPanel from "../components/InputPanel";
import MarginalChildChart from "../components/MarginalChildChart";
import { IconLoader2 } from "@tabler/icons-react";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001/api";

interface Params {
  marital_status: string;
  state: string;
  spouse_income: number;
  income_min: number;
  income_max: number;
  income_step: number;
}

interface ApiDataPoint {
  income: number;
  num_children: number;
  marginal_benefit: number;
  net_income: number;
}

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [initialized, setInitialized] = useState(false);

  const [params, setParams] = useState<Params>({
    marital_status: "single",
    state: "TX",
    spouse_income: 0,
    income_min: 0,
    income_max: 200000,
    income_step: 2500,
  });

  const [marginalChildData, setMarginalChildData] = useState<
    ApiDataPoint[] | null
  >(null);
  const [states, setStates] = useState<string[]>([]);

  const calculateMarginalChild = useCallback(
    async (overrideParams?: Params) => {
      if (loading) return;

      setLoading(true);
      setError(null);
      try {
        const paramsToUse = overrideParams || params;
        const response = await axios.post(
          `${API_URL}/marginal_child`,
          paramsToUse
        );

        if (response.data && response.data.length > 0) {
          setMarginalChildData(response.data);
          setError(null);
        } else {
          throw new Error("No data returned from API");
        }
      } catch (err: unknown) {
        const axiosErr = err as {
          response?: { data?: { error?: string } };
          message?: string;
        };
        const errorMessage =
          axiosErr.response?.data?.error ||
          axiosErr.message ||
          "Failed to calculate marginal child benefits. Make sure the API is running.";
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    },
    [loading, params]
  );

  // Initialize: fetch states and run first calculation
  useEffect(() => {
    if (initialized) return;

    const init = async () => {
      try {
        const response = await axios.get(`${API_URL}/states`);
        setStates(response.data);

        const calcResponse = await axios.post(
          `${API_URL}/marginal_child`,
          params
        );
        setMarginalChildData(calcResponse.data);
        setInitialized(true);
      } catch (err) {
        console.error("Initialization error:", err);
        setError("Failed to initialize. Please refresh the page.");
      }
    };

    init();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialized]);

  const handleParamChange = (key: string, value: string | number) => {
    const newParams = { ...params, [key]: value };
    setParams(newParams);

    // Auto-recalculate when state or marital status changes
    if (key === "state" || key === "marital_status") {
      setTimeout(() => {
        calculateMarginalChild(newParams);
      }, 100);
    }
  };

  return (
    <div className="min-h-screen bg-pe-gray-50">
      <Header />
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <p className="mb-6 text-center text-pe-gray-500">
          Analyze how government benefits change with each additional child
        </p>

        {error && (
          <div className="mb-4 rounded-lg border border-pe-error/30 bg-red-50 px-4 py-3 text-sm text-pe-error">
            {error}
          </div>
        )}

        <InputPanel
          params={params}
          states={states}
          loading={loading}
          onParamChange={handleParamChange}
          onCalculate={() => calculateMarginalChild()}
        />

        {loading && (
          <div className="mt-6 flex justify-center">
            <IconLoader2 className="h-8 w-8 animate-spin text-pe-primary-500" />
          </div>
        )}

        {marginalChildData && (
          <div className="mt-6">
            <MarginalChildChart data={marginalChildData} />
          </div>
        )}
      </main>
    </div>
  );
}
