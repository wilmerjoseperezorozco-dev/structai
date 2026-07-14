import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Escala "sky" de Tailwind — ya se usaba parcialmente (50/100/500/
        // 600/700/900 son valores literales de esa escala); completada aquí
        // con los stops reales que faltaban (200/300/400/800/950), no
        // inventados. Sin esto, ~60 usos de brand-200/300/400/950 en todo
        // el sitio no pintaban ningún color (Tailwind no genera CSS para
        // una clase de un shade no declarado).
        brand: {
          50:  "#f0f9ff",
          100: "#e0f2fe",
          200: "#bae6fd",
          300: "#7dd3fc",
          400: "#38bdf8",
          500: "#0ea5e9",
          600: "#0284c7",
          700: "#0369a1",
          800: "#075985",
          900: "#0c4a6e",
          950: "#082f49",
        },
        // Escala "slate" de Tailwind — mismo caso: 50/100/200/700/800/900
        // ya eran valores literales de slate. Completada con 300/400/500/
        // 600 (stops reales) y 750 (interpolación propia entre 700/800,
        // slate no tiene ese stop) — cubre ~148 usos que antes no pintaban.
        concrete: {
          50:  "#f8fafc",
          100: "#f1f5f9",
          200: "#e2e8f0",
          300: "#cbd5e1",
          400: "#94a3b8",
          500: "#64748b",
          600: "#475569",
          700: "#334155",
          750: "#293548",
          800: "#1e293b",
          900: "#0f172a",
        },
      },
      // Variables inyectadas por next/font en layout.tsx — auto-hospedadas,
      // sin @import bloqueante ni parpadeo de fuente (FOUT). "JetBrains
      // Mono" se usa deliberadamente para todo dato de trazabilidad (UUIDs,
      // citas normativas, timestamps): una tipografía tabular de ingeniero,
      // no decorativa — cada carácter ocupa el mismo ancho, así que un
      // uuid_trazabilidad o un código NTC se lee sin ambigüedad visual.
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
