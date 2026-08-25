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

const TITULO = "StructAI — Cálculos con trazabilidad normativa";
const DESCRIPCION =
  "NSR-10, NTC y SGSST citados con norma, título y sección exacta. Precios unitarios, estructuras, acueducto, geotecnia, vías y gerencia de obra para ingeniería civil en Colombia.";

export const metadata: Metadata = {
  // metadataBase resuelve las URLs relativas de openGraph/twitter (og:image,
  // canonical) a absolutas -- sin esto Next.js las deja relativas y la
  // mayoría de crawlers sociales (LinkedIn, WhatsApp, Google) las ignoran.
  metadataBase: new URL("https://www.structai.online"),
  title: TITULO,
  description: DESCRIPCION,
  keywords: [
    "NSR-10", "norma sismo resistente Colombia", "ingeniería civil Colombia",
    "cálculo estructural", "APU precios unitarios", "diagnóstico vulnerabilidad sísmica",
    "RAS 2000", "SGSST", "INVIAS", "diseño sismorresistente",
  ],
  authors: [{ name: "Wilmer José Pérez Orozco" }],
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
  alternates: {
    canonical: "/",
  },
  openGraph: {
    type: "website",
    locale: "es_CO",
    url: "https://www.structai.online",
    siteName: "StructAI",
    title: TITULO,
    description: DESCRIPCION,
    images: [{ url: "/icon-512.png", width: 512, height: 512, alt: "StructAI" }],
  },
  twitter: {
    card: "summary",
    title: TITULO,
    description: DESCRIPCION,
    images: ["/icon-512.png"],
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
