"use client";

import dynamic from "next/dynamic";

const GeoPotPanel = dynamic(() => import("@/components/GeoPotPanel"), { ssr: false });

export default function GeoPotPage() {
  return (
    <div className="h-full min-h-[calc(100vh-80px)]">
      <GeoPotPanel />
    </div>
  );
}
