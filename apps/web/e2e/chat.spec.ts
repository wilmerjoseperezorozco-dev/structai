import { abrirChat, expect, iniciarSesionFalsa, preguntar, test } from "./soporte";
import * as fx from "./fixtures";
import { SUPABASE_FALSO } from "./constantes";

/**
 * Pruebas E2E del chat (issue #190). Cada escenario corresponde a algo que ya
 * se arregló o se exige en el backend y que el usuario solo ve si el
 * frontend lo pinta bien. API simulada: ver e2e/soporte.ts.
 */

test.describe("con sesión", () => {
  test.beforeEach(async ({ page }) => {
    await iniciarSesionFalsa(page);
  });

  test("Sincelejo: cifras, fuentes, aviso de responsabilidad y pie de metadatos", async ({ page, backend }) => {
    backend.consultar(() => ({ json: fx.sincelejo }));
    await abrirChat(page);
    await preguntar(page, "¿Cuál es la amenaza sísmica (Aa/Av) de Sincelejo?");

    await expect(page.getByText("Aa = 0.10")).toBeVisible();
    await expect(page.getByText("Av = 0.15")).toBeVisible();
    await expect(page.getByText(fx.AVISO_RESPONSABILIDAD)).toBeVisible();
    await expect(page.getByText("2 fuentes consultadas · 1.8s")).toBeVisible();

    // Panel de fuentes: colapsado, con las normas citadas; al abrir, la sección con "§".
    const panel = page.getByRole("button", { name: /NSR-10 Apéndice A-4 · NSR-10 A\.2/ });
    await expect(panel).toBeVisible();
    await panel.click();
    await expect(page.getByText("§ A-4 Sucre")).toBeVisible();
    await expect(page.getByText("91%")).toBeVisible();

    // Lo que se le mandó al backend es exactamente la pregunta.
    const consulta = backend.peticiones.find((p) => p.ruta === "/consultar");
    expect(consulta?.cuerpo).toMatchObject({ pregunta: "¿Cuál es la amenaza sísmica (Aa/Av) de Sincelejo?" });
  });

  test("Supía: se ve el aviso de vigencia normativa con el valor del Decreto 1711", async ({ page, backend }) => {
    backend.consultar(() => ({ json: fx.supia }));
    await abrirChat(page);
    await preguntar(page, "¿Cuál es el Aa de Supía, Caldas?");

    await expect(page.getByText(/VIGENCIA NORMATIVA/)).toBeVisible();
    await expect(page.getByText(/Decreto 1711 de 2021/).first()).toBeVisible();
    await expect(page.getByText("Aa = 0.25", { exact: true })).toBeVisible();
  });

  test("Vivienda: responde con el checklist AIS, no con una abstención", async ({ page, backend }) => {
    backend.consultar(() => ({ json: fx.vivienda }));
    await abrirChat(page);
    await preguntar(page, "¿Cómo reviso si mi casa de dos pisos de ladrillo es vulnerable a un sismo?");

    await expect(page.getByText(/checklist AIS 2004/)).toBeVisible();
    await expect(page.getByText(/No encontré/)).toHaveCount(0);
    await expect(page.getByRole("button", { name: /AIS 2004 · NSR-10 Título E/ })).toBeVisible();
  });

  test("Abstención: sin fuentes no se pinta un panel vacío", async ({ page, backend }) => {
    backend.consultar(() => ({ json: fx.abstencion }));
    await abrirChat(page);
    await preguntar(page, "¿Qué dice la NSR-10 sobre ascensores espaciales?");

    await expect(page.getByText(/Prefiero no inventar un valor/)).toBeVisible();
    await expect(page.getByText("0 fuentes consultadas · 1.8s")).toBeVisible();
    // El único botón de fuentes posible tendría el contador; no debe existir.
    await expect(page.locator("button:has(svg.lucide-book-open)")).toHaveCount(0);
  });

  test("Precios APU: rótulo de precios, sin '§' y sin aviso de responsabilidad", async ({ page, backend }) => {
    backend.consultar(() => ({ json: fx.precios }));
    await abrirChat(page);
    await preguntar(page, "¿Cuánto cuesta el cemento en Barranquilla?");

    await expect(page.getByText("$ 32.900", { exact: false }).first()).toBeVisible();
    const panel = page.getByRole("button", { name: /Precios de construcción \(Barranquilla/ });
    await expect(panel).toBeVisible();
    await panel.click();
    await expect(page.getByText("Cemento gris 50 kg — $ 32.900 / bulto")).toBeVisible();
    await expect(page.getByText(/^§/)).toHaveCount(0);
    await expect(page.getByText(fx.AVISO_RESPONSABILIDAD)).toHaveCount(0);
  });

  test("👍 envía el feedback de esa consulta y deja la confirmación", async ({ page, backend }) => {
    backend.consultar(() => ({ json: fx.sincelejo }));
    await abrirChat(page);
    await preguntar(page, "¿Cuál es la amenaza sísmica (Aa/Av) de Sincelejo?");

    await page.getByTitle("Útil", { exact: true }).click();
    await expect(page.getByText("Gracias, marcaste esta respuesta como útil.")).toBeVisible();
    await expect(page.getByTitle("Útil", { exact: true })).toHaveCount(0);
    const fb = backend.peticiones.find((p) => p.ruta.endsWith("/feedback"));
    expect(fb?.ruta).toBe(`/consultas/${fx.sincelejo.consulta_id}/feedback`);
    expect(fb?.cuerpo).toMatchObject({ util: true });
  });

  test("Sin consulta_id no se ofrece 👍/👎", async ({ page, backend }) => {
    backend.consultar(() => ({ json: fx.supia }));
    await abrirChat(page);
    await preguntar(page, "¿Cuál es el Aa de Supía, Caldas?");
    await expect(page.getByText(/VIGENCIA NORMATIVA/)).toBeVisible();
    await expect(page.getByTitle("Útil", { exact: true })).toHaveCount(0);
  });

  test("API caída: se ve el error, sin spinner infinito, y se puede volver a preguntar", async ({ page, backend }) => {
    backend.consultar(() => ({ status: 500, json: { detail: "El servicio de consulta no está disponible" } }));
    await abrirChat(page);
    await preguntar(page, "¿Recubrimiento mínimo de vigas?");

    await expect(page.getByText("❌ El servicio de consulta no está disponible")).toBeVisible();
    await expect(page.locator(".animate-spin")).toHaveCount(0);
    await expect(page.getByRole("textbox")).toBeEnabled();
  });

  test("Un link javascript: de la respuesta no se convierte en enlace", async ({ page, backend }) => {
    backend.consultar(() => ({ json: fx.linkPeligroso }));
    await abrirChat(page);
    await preguntar(page, "Dame un enlace");

    await expect(page.getByText("este enlace")).toBeVisible();
    await expect(page.locator('a[href^="javascript:"]')).toHaveCount(0);
    // react-markdown ya vacía el href de javascript:; esUrlSegura además evita que quede un <a> clicable.
    await expect(page.getByRole("link", { name: "este enlace" })).toHaveCount(0);
    const seguro = page.getByRole("link", { name: "norma oficial" });
    await expect(seguro).toHaveAttribute("href", "https://www.minvivienda.gov.co");
    await expect(seguro).toHaveAttribute("rel", "noopener noreferrer");
  });

  test("Sin scroll horizontal con una respuesta larga", async ({ page, backend }) => {
    backend.consultar(() => ({ json: fx.vivienda }));
    await abrirChat(page);
    await preguntar(page, "¿Cómo reviso si mi casa es vulnerable?");
    await expect(page.getByText(/checklist AIS 2004/)).toBeVisible();
    const desborde = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    expect(desborde).toBeLessThanOrEqual(0);
  });
});

test.describe("sin sesión", () => {
  test("se avisa que hay que iniciar sesión y no se llama a /consultar", async ({ page, backend }) => {
    backend.consultar(() => ({ json: fx.sincelejo }));
    await abrirChat(page);
    await expect(page.getByText("Inicia sesión para hacer consultas — es gratis.")).toBeVisible();

    await preguntar(page, "¿Cuál es la amenaza sísmica (Aa/Av) de Sincelejo?");
    await page.waitForURL("**/login");
    expect(backend.peticiones.filter((p) => p.ruta === "/consultar")).toHaveLength(0);
  });
});

test("red cerrada: la sesión sale de la cookie y todo host externo se bloquea", async ({ page, backend }) => {
  await iniciarSesionFalsa(page);
  backend.consultar(() => ({ json: fx.sincelejo }));
  await abrirChat(page);
  await preguntar(page, "¿Cuál es la amenaza sísmica (Aa/Av) de Sincelejo?");
  await expect(page.getByText("Aa = 0.10")).toBeVisible();
  // La sesión falsa se lee de la cookie: el cliente de Supabase no necesita red.
  expect(backend.bloqueadas.filter((o) => o === SUPABASE_FALSO)).toHaveLength(0);
  // Todo lo que no es el backend falso se aborta (p. ej. el script de analítica
  // de Vercel): queda registrado como bloqueado, nunca llega a su destino.
  test.info().annotations.push({ type: "bloqueados", description: [...new Set(backend.bloqueadas)].join(", ") || "ninguno" });
  const delChat = backend.peticiones.filter((p) => p.ruta !== "/apu/list");
  expect(delChat.map((p) => `${p.metodo} ${p.ruta}`)).toEqual(["POST /consultar"]);
});
