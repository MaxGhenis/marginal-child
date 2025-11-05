"use client";

import { useState, useEffect } from "react";

const UK_REGIONS = [
  ["LONDON", "London"],
  ["SOUTH_EAST", "South East"],
  ["SOUTH_WEST", "South West"],
  ["EAST_OF_ENGLAND", "East of England"],
  ["WEST_MIDLANDS", "West Midlands"],
  ["EAST_MIDLANDS", "East Midlands"],
  ["YORKSHIRE", "Yorkshire and the Humber"],
  ["NORTH_WEST", "North West"],
  ["NORTH_EAST", "North East"],
  ["SCOTLAND", "Scotland"],
  ["WALES", "Wales"],
  ["NORTHERN_IRELAND", "Northern Ireland"],
];

interface ConfigPanelProps {
  onCalculate: (config: any) => void;
  initialConfig: any;
}

export default function ConfigPanel({ onCalculate, initialConfig }: ConfigPanelProps) {
  const [country, setCountry] = useState(initialConfig.country);
  const [metric, setMetric] = useState(initialConfig.metric);
  const [view, setView] = useState(initialConfig.view);
  const [maxChildren, setMaxChildren] = useState(initialConfig.maxChildren);
  const [year, setYear] = useState(initialConfig.year);

  // UK-specific
  const [region, setRegion] = useState(initialConfig.region || "LONDON");
  const [rent, setRent] = useState((initialConfig.rent || 12000) / 12);
  const [childcare, setChildcare] = useState((initialConfig.childcarePerChild || 12000) / 12);

  const handleSubmit = () => {
    const config = {
      country,
      metric,
      view,
      maxChildren,
      year,
      ...(country === "UK" ? {
        region,
        rent: rent * 12,
        childcarePerChild: childcare * 12,
      } : {}),
    };
    console.log("Calculate clicked with config:", config);
    onCalculate(config);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 space-y-4">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Configuration</h2>

      {/* Country Tabs */}
      <div className="flex space-x-2">
        <button
          onClick={() => setCountry("US")}
          className={`flex-1 py-2 px-3 rounded-md font-medium transition-colors ${
            country === "US"
              ? "bg-[#319795] text-white"
              : "bg-gray-100 text-gray-700 hover:bg-gray-200"
          }`}
        >
          🇺🇸 US
        </button>
        <button
          onClick={() => setCountry("UK")}
          className={`flex-1 py-2 px-3 rounded-md font-medium transition-colors ${
            country === "UK"
              ? "bg-[#319795] text-white"
              : "bg-gray-100 text-gray-700 hover:bg-gray-200"
          }`}
        >
          🇬🇧 UK
        </button>
      </div>

      {/* Max Children */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Maximum Number of Children
        </label>
        <input
          type="number"
          value={maxChildren}
          onChange={(e) => setMaxChildren(parseInt(e.target.value))}
          min={1}
          max={6}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-[#319795] focus:border-transparent"
        />
        <p className="text-xs text-gray-500 mt-1">{country === "UK" ? "Analyse" : "Analyze"} from 0 to this number</p>
      </div>

      <div className="border-t border-gray-200 my-4"></div>

      {/* Metric */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Metric
        </label>
        <div className="space-y-2">
          <label className="flex items-center">
            <input
              type="radio"
              value="net_income"
              checked={metric === "net_income"}
              onChange={(e) => setMetric(e.target.value)}
              className="text-[#319795] focus:ring-[#319795]"
            />
            <span className="ml-2 text-sm text-gray-700">Net Income</span>
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              value="mtr"
              checked={metric === "mtr"}
              onChange={(e) => setMetric(e.target.value)}
              className="text-[#319795] focus:ring-[#319795]"
            />
            <span className="ml-2 text-sm text-gray-700">Marginal Tax Rate</span>
          </label>
        </div>
      </div>

      {/* View */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          View
        </label>
        <div className="space-y-2">
          <label className="flex items-center">
            <input
              type="radio"
              value="absolute"
              checked={view === "absolute"}
              onChange={(e) => setView(e.target.value)}
              className="text-[#319795] focus:ring-[#319795]"
            />
            <span className="ml-2 text-sm text-gray-700">Absolute</span>
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              value="marginal"
              checked={view === "marginal"}
              onChange={(e) => setView(e.target.value)}
              className="text-[#319795] focus:ring-[#319795]"
            />
            <span className="ml-2 text-sm text-gray-700">Marginal (per child)</span>
          </label>
        </div>
      </div>

      <div className="border-t border-gray-200 my-4"></div>

      {/* Year */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Year
        </label>
        <select
          value={year}
          onChange={(e) => setYear(parseInt(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-[#319795] focus:border-transparent"
        >
          {Array.from({ length: 15 }, (_, i) => 2021 + i).map((y) => (
            <option key={y} value={y}>{y}</option>
          ))}
        </select>
      </div>

      {/* UK-specific inputs */}
      {country === "UK" && (
        <>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Region
            </label>
            <select
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-[#319795] focus:border-transparent"
            >
              {UK_REGIONS.map(([code, name]) => (
                <option key={code} value={code}>{name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Monthly Rent (£)
            </label>
            <input
              type="number"
              value={rent}
              onChange={(e) => setRent(parseInt(e.target.value))}
              min={0}
              step={50}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-[#319795] focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Monthly Childcare per Child (£)
            </label>
            <input
              type="number"
              value={childcare}
              onChange={(e) => setChildcare(parseInt(e.target.value))}
              min={0}
              step={50}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-[#319795] focus:border-transparent"
            />
            <p className="text-xs text-gray-500 mt-1">Full-time nursery for ages 1, 3, 5</p>
          </div>
        </>
      )}

      <button
        onClick={handleSubmit}
        className="w-full bg-[#319795] hover:bg-[#2C7A7B] text-white font-medium py-2 px-4 rounded-md transition-colors"
      >
        Calculate
      </button>

      <p className="text-xs text-gray-500 mt-2">
        {country === "UK" ? "Parent age 35, children ages 1/3/5. BRMA not specified." : "All children age 10."}
      </p>
    </div>
  );
}
