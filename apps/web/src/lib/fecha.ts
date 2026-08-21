/**
 * Formateo de fecha/hora fijado a Colombia (America/Bogota, UTC-5, sin
 * horario de verano).
 *
 * El backend siempre devuelve timestamps en UTC (ver apps/api/main.py,
 * `datetime.utcnow().isoformat() + "Z"`) -- correcto para transmitir/
 * almacenar. Pero mostrarlos con `toLocaleString()` sin `timeZone`
 * explícito usa el reloj del DISPOSITIVO de quien mira la pantalla, no
 * el de Colombia -- para un sistema de trazabilidad (auditoría de
 * cálculos APU) eso es una debilidad real: un registro que debería ser
 * inequívoco cambiaría de hora mostrada según desde dónde se revise.
 * Fijar el timezone hace que la hora mostrada sea siempre la misma,
 * sin importar el dispositivo del usuario.
 */
export function formatearFechaColombia(
  timestamp: string | number | Date,
  opciones?: Intl.DateTimeFormatOptions
): string {
  return new Date(timestamp).toLocaleString("es-CO", {
    timeZone: "America/Bogota",
    ...opciones,
  });
}
