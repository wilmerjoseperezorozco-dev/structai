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

// Datos estructurados (schema.org) -- le dicen a Google explícitamente que
// StructAI, el perfil de GitHub y el de LinkedIn son la misma persona/marca
// (propiedad "sameAs" = el mecanismo real que usan los buscadores para
// enlazar identidades, no solo un link visual). Contenido 100% estático,
// sin ningún dato de usuario -- por eso dangerouslySetInnerHTML es seguro
// aquí (ver rules/react/security.md: fuente bajo control total, nunca
// entrada externa).
const JSON_LD = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Person",
      "@id": "https://www.structai.online/#persona",
      name: "Wilmer José Pérez Orozco",
      jobTitle: "Ingeniero civil · Polímata en IA aplicada",
      url: "https://www.structai.online",
      sameAs: [
        "https://github.com/wilmerjoseperezorozco-dev",
        "https://www.linkedin.com/in/wilmerperez-ai/",
      ],
    },
    {
      "@type": "SoftwareApplication",
      "@id": "https://www.structai.online/#software",
      name: "StructAI",
      applicationCategory: "BusinessApplication",
      operatingSystem: "Web",
      url: "https://www.structai.online",
      description: DESCRIPCION,
      author: { "@id": "https://www.structai.online/#persona" },
      offers: { "@type": "Offer", availability: "https://schema.org/InStock" },
    },
  ],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" className={`h-full ${inter.variable} ${jetbrainsMono.variable} ${fraunces.variable}`}>
      <head>
        <script
          type="application/ld+json"
          // eslint-disable-next-line react/no-danger
          dangerouslySetInnerHTML={{ __html: JSON.stringify(JSON_LD) }}
        />
      </head>
      <body className="h-full font-sans">{children}</body>
    </html>
  );
}
