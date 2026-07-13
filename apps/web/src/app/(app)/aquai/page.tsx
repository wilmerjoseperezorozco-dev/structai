"use client";

import dynamic from "next/dynamic";

const AquAIPanel = dynamic(() => import("@/components/AquAIPanel"), { ssr: false });

export default function AquAIPage() {
  return (
    <div className="h-full min-h-[calc(100vh-80px)]">
      <AquAIPanel />
    </div>
  );
}
