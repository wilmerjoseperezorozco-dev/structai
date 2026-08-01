"use client";

import dynamic from "next/dynamic";

const APUPanel = dynamic(() => import("@/components/APUPanel"), { ssr: false });
const ApuLotePanel = dynamic(() => import("@/components/ApuLotePanel"), { ssr: false });

export default function APUPage() {
  return (
    <div className="h-full min-h-[calc(100vh-80px)] flex flex-col gap-3 px-4 pt-4">
      <ApuLotePanel />
      <div className="flex-1 -mx-4">
        <APUPanel />
      </div>
    </div>
  );
}
