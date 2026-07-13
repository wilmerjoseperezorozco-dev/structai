"use client";

import dynamic from "next/dynamic";

const ViasPanel = dynamic(() => import("@/components/ViasPanel"), { ssr: false });

export default function ViasPage() {
  return (
    <div className="h-full min-h-[calc(100vh-80px)]">
      <ViasPanel />
    </div>
  );
}
