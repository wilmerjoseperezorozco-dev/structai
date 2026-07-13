"use client";

import dynamic from "next/dynamic";

const APUPanel = dynamic(() => import("@/components/APUPanel"), { ssr: false });

export default function APUPage() {
  return (
    <div className="h-full min-h-[calc(100vh-80px)]">
      <APUPanel />
    </div>
  );
}
