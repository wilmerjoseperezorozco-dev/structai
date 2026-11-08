# Resultados: Apéndice A-4 de la NSR-10 contra la capa del SGC (2026-11-08)

Protocolo (fijado antes de comparar por código): [`PROTOCOLO_AUDITORIA_A4_VS_SGC.md`](PROTOCOLO_AUDITORIA_A4_VS_SGC.md). Código: `auditoria_a4_vs_sgc.py`. Salida completa: `auditoria_a4_vs_sgc.json`.

## Qué se comparó
- A-4 del PDF (páginas A-153 a A-174): 1.117 códigos DANE distintos.
- Capa `Municipios_Amenaza_NR10` del SGC consultada en vivo: 1.123 registros, 1.122 códigos.
- Cruce por **código DANE**, no por nombre.

## Resultado
| Clase | Municipios |
|---|---:|
| Pares emparejados por código | 1.115 |
| Con diferencia en algún valor (Aa o Av) | **29** |
| Solo difieren en el nombre (mayúsculas, "EL CARMEN DE VIBORAL" frente a "Carmen De Viboral") | 44 |
| En A-4 y sin pareja en la capa | 2 (Belén de Bajirá, Chocó; Nariño, Cundinamarca) |
| En la capa y sin pareja en A-4 | 6 códigos + 1 registro sin código |
| Código con dos registros en la capa | 1 (Inzá, Cauca) |

De los 29 con valores distintos:
- **En ninguno difieren Ae ni Ad**; solo Aa o Av.
- En **7 cambia además la zona de amenaza** (Caldas, Santafé de Antioquia, Titiribí y La Calera pasan de Intermedia a Alta en la capa; San Luis y Oicatá de Alta a Intermedia; Cartagena del Chairá de Intermedia a Baja).
- El SGC da un valor **mayor** en 16 casos y **menor** en 13. No hay un sentido único.

## Verificación contra el PDF
Para los 29 volví al texto del PDF y comparé la fila completa. **Mi extracción coincide con el PDF en los 29.** Por tanto estas diferencias no son errores de transcripción nuestros: la capa del SGC y el Apéndice A-4 publicado en 2010 dicen cosas distintas para esos municipios.

## Lo que no se puede afirmar
- **No sé cuál de las dos fuentes es la vigente** para cada municipio. La capa podría reflejar una actualización normativa posterior, una corrección del SGC o un error de la capa. No encontré ni leí ningún decreto que lo aclare, así que no atribuyo ninguna diferencia a uno.
- Los 6 códigos que solo están en la capa corresponden a municipios con nombre conocido (Norosí, Guachené, San José de Uré, Tuchín, Nariño en Nariño, Coveñas). No verifiqué si el PDF los trae bajo otro código; la causa más simple es de creación o cambio de código, pero **es una suposición**.
- Que A-4 y la capa coincidan en 1.086 municipios no demuestra que ambos sean correctos; solo que no se contradicen.

## Qué cambia en StructAI
El chat sirve hoy los valores de la capa del SGC. En esos 29 municipios el valor que muestra puede diferir del reglamento de 2010. Recomendación (no implementada): que la respuesta cite la fuente y, en estos municipios, avise la discrepancia. La lista está en `auditoria_a4_vs_sgc.json`.

## Siguiente paso posible
Buscar el decreto o resolución que actualiza la tabla A-4 (si existe) y leerlo antes de decidir cuál valor es el vigente.
