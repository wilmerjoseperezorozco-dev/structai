"use client";

import dynamic from "next/dynamic";

const GerenciaPanel = dynamic(() => import("@/components/GerenciaPanel"), { ssr: false });

export default function GerenciaPage() {
  return (
    <div className="h-full min-h-[calc(100vh-80px)]">
      <GerenciaPanel />
    </div>
  );
}
