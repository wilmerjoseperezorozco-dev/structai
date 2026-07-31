import type { Metadata, Viewport } from "next";
import { Inter, JetBrains_Mono, Fraunces } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-sans",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["400", "600"],
  variable: "--font-mono",
  display: "swap",
});

// Serif editorial para el titular de la landing (hero) — carácter
// institucional, en contraste deliberado con Inter (cuerpo) y JetBrains
// Mono (datos/citas). No se usa en el resto de la app.
const fraunces = Fraunces({
  subsets: ["latin"],
  weight: ["500", "600"],
  variable: "--font-display",
  display: "swap",
});

export const metadata: Metadata = {
  title: "StructAI — Cálculos con trazabilidad normativa",
  description:
    "NSR-10, NTC y SGSST citados con norma, título y sección exacta. Precios unitarios, estructuras, acueducto, geotecnia, vías y gerencia de obra para ingeniería civil en Colombia.",
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "black-translucent",
    title: "StructAI",
  },
  icons: {
    icon: "/icon-192.png",
    apple: "/icon-192.png",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  themeColor: "#0A0E14",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" className={`h-full ${inter.variable} ${jetbrainsMono.variable} ${fraunces.variable}`}>
      <body className="h-full font-sans">{children}</body>
    </html>
  );
}
