"use client";

import Image from "next/image";

export default function Header() {
  return (
    <header className="bg-white shadow-sm">
      <div className="mx-auto flex max-w-7xl items-center px-6 py-3">
        <Image
          src="https://raw.githubusercontent.com/PolicyEngine/policyengine-app-v2/main/app/public/assets/logos/policyengine/teal.png"
          alt="PolicyEngine"
          width={160}
          height={32}
          className="mr-4 h-8 w-auto"
          unoptimized
        />
        <h1 className="text-xl font-semibold text-pe-gray-700">
          The marginal child
        </h1>
        <span className="ml-3 text-sm italic text-pe-gray-500">
          Powered by PolicyEngine
        </span>
      </div>
    </header>
  );
}
