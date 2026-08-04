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
        // Unificación de tema 2026-08-04: "brand" era la escala "sky" (azul)
        // usada en login/dashboard/los 4 motores — visualmente inconsistente
        // con el negro+dorado (ink/bronze) de la landing (Hero.tsx), que el
        // usuario ve primero. Ahora "brand" reutiliza los mismos valores que
        // "bronze" (mismo dorado, no un tono aparte) para que todo el sitio
        // comparta un único acento tras entrar. Con esto, todo lo que usa la
        // clase brand-* cambia de azul a dorado sin tocar cada componente —
        // solo los botones de fondo sólido (brand-600/500 + texto blanco)
        // se ajustaron aparte a texto oscuro (ink-950) porque blanco sobre
        // dorado pierde legibilidad.
        brand: {
          50:  "#FDF7EC",
          100: "#FAEED7",
          200: "#F5DDB2",
          300: "#EFCB8E",
          400: "#E6B564",
          500: "#D99A3F",
          600: "#B87526",
          700: "#91591F",
          800: "#6B4019",
          900: "#452A14",
          950: "#2B1B0E",
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
        // Paleta de la landing (hero) — deliberadamente distinta de brand/
        // concrete (que ya tienen ~200 usos en el resto de la app y no se
        // tocan aquí). "ink" es un carbón con matiz azul frío (no gris
        // plano) evocando papel de plano técnico oscuro; "bronze" es el
        // acento cálido (instrumentos de dibujo, sello oficial) que
        // reemplaza el azul cian genérico en la superficie de marketing.
        ink: {
          50:  "#F6F7FA",
          100: "#E9ECF2",
          200: "#CDD3DF",
          300: "#A7B0C2",
          400: "#7B879E",
          500: "#55627A",
          600: "#3A4557",
          700: "#262F3D",
          800: "#1A212C",
          900: "#10151D",
          950: "#0A0E14",
        },
        bronze: {
          50:  "#FDF7EC",
          100: "#FAEED7",
          200: "#F5DDB2",
          300: "#EFCB8E",
          400: "#E6B564",
          500: "#D99A3F",
          600: "#B87526",
          700: "#91591F",
          800: "#6B4019",
          900: "#452A14",
          950: "#2B1B0E",
        },
      },
      // Variables inyectadas por next/font en layout.tsx — auto-hospedadas,
      // sin @import bloqueante ni parpadeo de fuente (FOUT). "JetBrains
      // Mono" se usa deliberadamente para todo dato de trazabilidad (UUIDs,
      // citas normativas, timestamps): una tipografía tabular de ingeniero,
      // no decorativa — cada carácter ocupa el mismo ancho, así que un
      // uuid_trazabilidad o un código NTC se lee sin ambigüedad visual.
      // "display" (Fraunces) se usa solo en la landing/hero: un serif con
      // carácter editorial que le da autoridad institucional al titular,
      // en contraste deliberado con Inter (cuerpo) y JetBrains Mono (datos).
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
        display: ["var(--font-display)", "Georgia", "serif"],
      },
    },
  },
  plugins: [],
};

export default config;
