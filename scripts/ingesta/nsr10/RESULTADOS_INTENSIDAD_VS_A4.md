# Resultados: capas de intensidad sísmica del SGC frente al Apéndice A-4 de la NSR-10 (2026-11-08)

Protocolo, fijado y publicado antes de cruzar (commit `2bf8a32`): [`PROTOCOLO_INTENSIDAD_VS_A4.md`](PROTOCOLO_INTENSIDAD_VS_A4.md). Código: `auditoria_intensidad_vs_a4.py`. Salida: `auditoria_intensidad_vs_a4.json`.

## Datos y cruce
A-4 (1.117 municipios), intensidad máxima observada del SGC (1.095 con categoría `M` y valor), PGA «esperado» del SGC (1.122). Cruce por código DANE: **1.088 municipios**. IC95 % por bootstrap de bloques por departamento.

## Q1: ¿concuerdan en el orden de los municipios?
| Comparación | ρ de Spearman | IC95 % |
|---|---:|---|
| Aa del A-4 frente a intensidad observada | **+0,59** | [+0,45; +0,72] |
| Aa del A-4 frente a PGA esperado del SGC | **+0,54** | [+0,36; +0,68] |

Los dos ICs excluyen 0: el Aa ordena a los municipios en el mismo sentido que la intensidad observada y que el PGA del SGC, con una concordancia moderada. Con una escala ordinal de pocos niveles y muchos empates, ρ ≈ 0,6 no es una concordancia fuerte.

## Q2: ¿hay municipios con daño severo observado en zona de baja amenaza?
**No.** Ningún municipio con intensidad observada ≥ 8 (111 municipios) está en zona **Baja**, y ninguno tiene Aa ≤ 0,10. Solo uno está en zona Intermedia: **Sonsón (Antioquia)**, intensidad 8, Aa 0,15. El 20 % de los municipios de zona Alta tiene intensidad observada ≥ 8, frente al 0,2 % de los de zona Intermedia y el 0 % de los de zona Baja. La intensidad media observada sube de 5,1 (Baja) a 6,1 (Intermedia) y 6,9 (Alta).

## Q3: tamaño de la diferencia con el PGA «esperado» del SGC
Razón PGA esperado / Aa, por municipio: **mediana 1,31**; percentil 10 en 0,84 y percentil 90 en 2,22. En **390 municipios** la razón supera 1,5 (211 de zona Intermedia, 103 Alta, 76 Baja) y en 20 es menor de 0,67. Las mayores razones están en el interior del Caribe y la depresión momposina (El Banco, Magdalena: PGA 0,40 frente a Aa 0,10, razón 4,0). Las menores, en la Amazonía (Leticia, Mitú: razón 0,14-0,20, con PGA de 0,01).

**No concluyo cuál valor es el correcto.** El servicio no documenta el periodo de retorno ni el modelo del PGA, y una razón de 4 en el Caribe interior es difícil de explicar solo con un periodo de retorno mayor. Hay tres explicaciones posibles que no distingo: otro periodo de retorno, otro modelo de amenaza, o un escenario de «máxima esperada» y no un valor de diseño. Hasta aclararlo, **no es válido** usar ese PGA como sustituto del Aa en un cálculo.

## Qué cambia en StructAI
- El A-4 es consistente con la observación histórica en lo esencial: no hay daño severo registrado en zona Baja.
- **No** debe mostrarse el PGA «esperado» del SGC junto al Aa como si fueran comparables; si se muestra, con una advertencia explícita de que es otro producto y que su periodo de retorno no está documentado.
- Sonsón es un caso para revisar con un ingeniero, no una conclusión.

## Límites
La intensidad observada depende de la antigüedad del poblamiento y de la vulnerabilidad local, no solo del peligro. Es una escala ordinal de 4 a 9. El análisis es municipal. Bogotá no entró al cruce (no verifiqué por qué; probablemente por el nombre o el código). La capa de PGA no fue verificada contra su documentación porque no la hay en el servicio.
