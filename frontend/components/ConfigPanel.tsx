"use client";

import { useState } from "react";

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

const US_STATES = [
  ["AL", "Alabama"], ["AK", "Alaska"], ["AZ", "Arizona"], ["AR", "Arkansas"],
  ["CA", "California"], ["CO", "Colorado"], ["CT", "Connecticut"], ["DE", "Delaware"],
  ["DC", "District of Columbia"], ["FL", "Florida"], ["GA", "Georgia"], ["HI", "Hawaii"],
  ["ID", "Idaho"], ["IL", "Illinois"], ["IN", "Indiana"], ["IA", "Iowa"],
  ["KS", "Kansas"], ["KY", "Kentucky"], ["LA", "Louisiana"], ["ME", "Maine"],
  ["MD", "Maryland"], ["MA", "Massachusetts"], ["MI", "Michigan"], ["MN", "Minnesota"],
  ["MS", "Mississippi"], ["MO", "Missouri"], ["MT", "Montana"], ["NE", "Nebraska"],
  ["NV", "Nevada"], ["NH", "New Hampshire"], ["NJ", "New Jersey"], ["NM", "New Mexico"],
  ["NY", "New York"], ["NC", "North Carolina"], ["ND", "North Dakota"], ["OH", "Ohio"],
  ["OK", "Oklahoma"], ["OR", "Oregon"], ["PA", "Pennsylvania"], ["RI", "Rhode Island"],
  ["SC", "South Carolina"], ["SD", "South Dakota"], ["TN", "Tennessee"], ["TX", "Texas"],
  ["UT", "Utah"], ["VT", "Vermont"], ["VA", "Virginia"], ["WA", "Washington"],
  ["WV", "West Virginia"], ["WI", "Wisconsin"], ["WY", "Wyoming"],
];

interface ConfigPanelProps {
  onCalculate: (config: any) => void;
  initialConfig: any;
  hasData?: boolean;
  onCountryChange?: (country: string) => void;
}

export default function ConfigPanel({ onCalculate, initialConfig, onCountryChange }: ConfigPanelProps) {
  const [country, setCountry] = useState(initialConfig.country);
  const [maxChildren, setMaxChildren] = useState(initialConfig.maxChildren);
  const [year, setYear] = useState(initialConfig.year);

  // UK-specific
  const [region, setRegion] = useState(initialConfig.region || "LONDON");
  const [rent, setRent] = useState((initialConfig.rent || 12000) / 12);
  const [childcare, setChildcare] = useState((initialConfig.childcarePerChild || 12000) / 12);

  // US-specific
  const [maritalStatus, setMaritalStatus] = useState(initialConfig.maritalStatus || "single");
  const [stateCode, setStateCode] = useState(initialConfig.stateCode || "CA");
  const [spouseIncome, setSpouseIncome] = useState(initialConfig.spouseIncome || 0);
  const [includeHealthBenefits, setIncludeHealthBenefits] = useState(initialConfig.includeHealthBenefits !== false);

  const buildConfig = () => ({
    country,
    maxChildren,
    year,
    ...(country === "UK" ? {
      region,
      rent: rent * 12,
      childcarePerChild: childcare * 12,
    } : {
      maritalStatus,
      stateCode,
      spouseIncome,
      includeHealthBenefits,
    }),
  });

  const handleSubmit = () => {
    const config = buildConfig();
    console.log("Calculate clicked with config:", config);
    onCalculate(config);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 space-y-4">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Household</h2>

      {/* Country Tabs */}
      <div className="flex space-x-2">
        <button
          onClick={() => {
            setCountry("US");
            if (onCountryChange) onCountryChange("US");
          }}
          className={`flex-1 py-2 px-3 rounded-md font-medium transition-colors ${
            country === "US"
              ? "bg-[#319795] text-white"
              : "bg-gray-100 text-gray-700 hover:bg-gray-200"
          }`}
        >
          US
        </button>
        <button
          onClick={() => {
            setCountry("UK");
            if (onCountryChange) onCountryChange("UK");
          }}
          className={`flex-1 py-2 px-3 rounded-md font-medium transition-colors ${
            country === "UK"
              ? "bg-[#319795] text-white"
              : "bg-gray-100 text-gray-700 hover:bg-gray-200"
          }`}
        >
          UK
        </button>
      </div>

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
          {Array.from({ length: 10 }, (_, i) => 2024 + i).map((y) => (
            <option key={y} value={y}>{y}</option>
          ))}
        </select>
      </div>

      {/* Max Children */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Maximum Children
        </label>
        <input
          type="number"
          value={maxChildren}
          onChange={(e) => setMaxChildren(parseInt(e.target.value) || 1)}
          min={1}
          max={6}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-[#319795] focus:border-transparent"
        />
        <p className="text-xs text-gray-500 mt-1">{country === "UK" ? "Analyse" : "Analyze"} from 0 to {maxChildren}</p>
      </div>

      <div className="border-t border-gray-200 my-4"></div>

      {/* US-specific inputs */}
      {country === "US" && (
        <>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Marital Status
            </label>
            <div className="flex space-x-2">
              <button
                onClick={() => setMaritalStatus("single")}
                className={`flex-1 py-2 px-3 rounded-md text-sm font-medium transition-colors ${
                  maritalStatus === "single"
                    ? "bg-[#319795] text-white"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                Single
              </button>
              <button
                onClick={() => setMaritalStatus("married")}
                className={`flex-1 py-2 px-3 rounded-md text-sm font-medium transition-colors ${
                  maritalStatus === "married"
                    ? "bg-[#319795] text-white"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                Married
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              State
            </label>
            <select
              value={stateCode}
              onChange={(e) => setStateCode(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-[#319795] focus:border-transparent"
            >
              {US_STATES.map(([code, name]) => (
                <option key={code} value={code}>{name}</option>
              ))}
            </select>
          </div>

          {maritalStatus === "married" && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Spouse Income ($)
              </label>
              <input
                type="number"
                value={spouseIncome}
                onChange={(e) => setSpouseIncome(parseInt(e.target.value) || 0)}
                min={0}
                step={1000}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-[#319795] focus:border-transparent"
              />
            </div>
          )}

          <div className="flex items-start space-x-2">
            <input
              type="checkbox"
              id="healthBenefits"
              checked={includeHealthBenefits}
              onChange={(e) => setIncludeHealthBenefits(e.target.checked)}
              className="h-4 w-4 mt-0.5 text-[#319795] border-gray-300 rounded focus:ring-[#319795]"
            />
            <label htmlFor="healthBenefits" className="text-sm text-gray-700">
              Include health benefits (assumes no ESI)
            </label>
          </div>
        </>
      )}

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
              Monthly Rent
            </label>
            <input
              type="number"
              value={rent}
              onChange={(e) => setRent(parseInt(e.target.value) || 0)}
              min={0}
              step={50}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-[#319795] focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Monthly Childcare / Child
            </label>
            <input
              type="number"
              value={childcare}
              onChange={(e) => setChildcare(parseInt(e.target.value) || 0)}
              min={0}
              step={50}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-[#319795] focus:border-transparent"
            />
          </div>
        </>
      )}

      <button
        onClick={handleSubmit}
        className="w-full bg-[#319795] hover:bg-[#2C7A7B] text-white font-medium py-3 px-4 rounded-md transition-colors"
      >
        Calculate
      </button>

      <p className="text-xs text-gray-500 mt-2">
        {country === "UK"
          ? "Single parent, age 35. Children ages 1, 3, 5."
          : "All children age 10."}
      </p>
    </div>
  );
}
