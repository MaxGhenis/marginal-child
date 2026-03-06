"use client";

interface Params {
  marital_status: string;
  state: string;
  spouse_income: number;
  income_min: number;
  income_max: number;
  income_step: number;
}

interface InputPanelProps {
  params: Params;
  states: string[];
  loading: boolean;
  onParamChange: (key: string, value: string | number) => void;
  onCalculate: () => void;
}

export default function InputPanel({
  params,
  states,
  loading,
  onParamChange,
  onCalculate,
}: InputPanelProps) {
  return (
    <div className="rounded-lg bg-white p-6 shadow-sm">
      <h2 className="mb-4 text-lg font-semibold text-pe-primary-700">
        Household configuration
      </h2>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {/* Marital status */}
        <div>
          <label
            htmlFor="marital_status"
            className="mb-1 block text-sm font-medium text-pe-gray-700"
          >
            Marital status
          </label>
          <select
            id="marital_status"
            value={params.marital_status}
            onChange={(e) => onParamChange("marital_status", e.target.value)}
            className="w-full rounded-md border border-pe-gray-200 bg-white px-3 py-2 text-sm text-pe-gray-700 focus:border-pe-primary-500 focus:ring-1 focus:ring-pe-primary-500 focus:outline-none"
          >
            <option value="single">Single</option>
            <option value="married">Married</option>
          </select>
        </div>

        {/* State */}
        <div>
          <label
            htmlFor="state"
            className="mb-1 block text-sm font-medium text-pe-gray-700"
          >
            State
          </label>
          <select
            id="state"
            value={params.state}
            onChange={(e) => onParamChange("state", e.target.value)}
            className="w-full rounded-md border border-pe-gray-200 bg-white px-3 py-2 text-sm text-pe-gray-700 focus:border-pe-primary-500 focus:ring-1 focus:ring-pe-primary-500 focus:outline-none"
          >
            {states.map((st) => (
              <option key={st} value={st}>
                {st}
              </option>
            ))}
          </select>
        </div>

        {/* Spouse income (conditional) */}
        {params.marital_status === "married" && (
          <div>
            <label
              htmlFor="spouse_income"
              className="mb-1 block text-sm font-medium text-pe-gray-700"
            >
              Spouse income
            </label>
            <input
              id="spouse_income"
              type="number"
              min={0}
              value={params.spouse_income}
              onChange={(e) =>
                onParamChange("spouse_income", parseInt(e.target.value) || 0)
              }
              className="w-full rounded-md border border-pe-gray-200 bg-white px-3 py-2 text-sm text-pe-gray-700 focus:border-pe-primary-500 focus:ring-1 focus:ring-pe-primary-500 focus:outline-none"
            />
          </div>
        )}
      </div>

      {/* Income range */}
      <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div>
          <label
            htmlFor="income_min"
            className="mb-1 block text-sm font-medium text-pe-gray-700"
          >
            Income minimum
          </label>
          <input
            id="income_min"
            type="number"
            min={0}
            value={params.income_min}
            onChange={(e) =>
              onParamChange("income_min", parseInt(e.target.value) || 0)
            }
            className="w-full rounded-md border border-pe-gray-200 bg-white px-3 py-2 text-sm text-pe-gray-700 focus:border-pe-primary-500 focus:ring-1 focus:ring-pe-primary-500 focus:outline-none"
          />
        </div>
        <div>
          <label
            htmlFor="income_max"
            className="mb-1 block text-sm font-medium text-pe-gray-700"
          >
            Income maximum
          </label>
          <input
            id="income_max"
            type="number"
            min={0}
            value={params.income_max}
            onChange={(e) =>
              onParamChange("income_max", parseInt(e.target.value) || 0)
            }
            className="w-full rounded-md border border-pe-gray-200 bg-white px-3 py-2 text-sm text-pe-gray-700 focus:border-pe-primary-500 focus:ring-1 focus:ring-pe-primary-500 focus:outline-none"
          />
        </div>
        <div>
          <label
            htmlFor="income_step"
            className="mb-1 block text-sm font-medium text-pe-gray-700"
          >
            Income step
          </label>
          <input
            id="income_step"
            type="number"
            min={1}
            value={params.income_step}
            onChange={(e) =>
              onParamChange("income_step", parseInt(e.target.value) || 1)
            }
            className="w-full rounded-md border border-pe-gray-200 bg-white px-3 py-2 text-sm text-pe-gray-700 focus:border-pe-primary-500 focus:ring-1 focus:ring-pe-primary-500 focus:outline-none"
          />
        </div>
      </div>

      {/* Calculate button */}
      <div className="mt-6 flex justify-center">
        <button
          onClick={onCalculate}
          disabled={loading}
          className="rounded-lg bg-pe-primary-500 px-8 py-3 text-base font-medium text-white transition-colors hover:bg-pe-primary-600 focus:ring-2 focus:ring-pe-primary-300 focus:ring-offset-2 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? "Calculating..." : "Calculate marginal child benefits"}
        </button>
      </div>
    </div>
  );
}
