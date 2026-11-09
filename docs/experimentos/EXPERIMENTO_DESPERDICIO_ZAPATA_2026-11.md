# Experimento: ¿cuánto concreto sobra en una zapata prismática? (2026-11-08)

**Hipótesis a falsear.** Una zapata prismática (espesor constante) diseñada con NSR-10 desperdicia hasta ~30 % del concreto en zonas casi sin esfuerzo.

**Método.** Sobre una malla de 30 casos (P_serv 300–2 500 kN, q_adm 120–300 kPa, f'c 21 y 28 MPa, columna 300–500 mm, carga concéntrica, P_u = 1,35·P_serv, desplante 1,5 m) se comparan:
- **Prisma:** el mínimo de `zapata.disenar` (NSR-10 C.15, C.11.1.3.1, C.11.11, C.9.3.2.1, C.15.7).
- **Tronco de pirámide:** el mínimo de `zapata_troncopiramidal.optimizar`, que usa las mismas verificaciones sección por sección, con espesor lineal entre la cara de la columna (h_c) y el borde (h_e ≥ 300 mm).
- Función objetivo común: volumen de concreto + masa de acero / 7 850. La prueba `test_con_espesor_constante_coincide_con_la_zapata_prismatica` confirma que con h_c = h_e el nuevo verificador coincide con `zapata.verificar` (mismo cumple/no cumple, mismo volumen, acero dentro de 2 %).

**Resultado (30 casos con solución).**

| Carga P_serv | Ahorro de concreto (mediana) | Rango |
|---|---|---|
| 300 kN | 0 % | 0 % (manda el espesor mínimo de 300 mm de la rejilla) |
| 600 kN | 14,9 % | 2,5–15,6 % |
| 1 000 kN | 21,6 % | 14,9–27,1 % |
| 1 500 kN | 27,0 % | 23,7–30,2 % |
| 2 500 kN | 33,6 % | 26,0–36,7 % |
| **Todas** | **21,6 %** | **0–36,7 %** |

Acero: mediana −9,6 % (0–21 %). Encofrado lateral: −34 % (mediana) porque baja el espesor de borde. Ángulo del talud: 0–23° (ninguno supera los 25° que se asumen sin contraencofrado).

**Lectura honesta.**
1. «Hasta 30 %» se cumple solo para zapatas pesadas (≥ 1 500 kN); para cargas pequeñas no hay ahorro. No es un desperdicio uniforme.
2. La forma que ahorra aquí es la **zapata troncopiramidal clásica**, ya conocida: este experimento mide la línea base contra la que habría que medir cualquier forma «orgánica». Lo que una topología con deep learning añada se debe medir contra este 21,6 %, no contra el prisma.
3. El prisma comparado ya es el **mínimo** que cumple la norma en la rejilla; la práctica usual (espesores redondeados por regla) probablemente desperdicia más. No lo medí.

**Límites (no sobreinterpretar).**
- Carga concéntrica; sin momentos ni punzonamiento con momento (C.11.11.7 no modelado).
- La NSR-10 se redactó para espesor constante: el espesor variable se verifica con las mismas fórmulas sección por sección (supuesto, no validación normativa).
- Longitud de desarrollo y separación libre (C.7.6) no verificadas; el espesor de borde mínimo (300 mm) es un límite de la rejilla, no de la norma (C.15.7 exige d ≥ 150 mm).
- Sin costos ni CO₂: faltan precios y factores de emisión con fuente verificada.
- No se modeló el costo de ejecutar el talud (acabado, vibrado en pendiente) ni el de variantes constructivas (escalonada).
- Solo es una estimación de ingeniería. Cualquier uso real requiere revisión y firma de un ingeniero estructural (issue #18).

**Reproducir.** `python scripts/experimentos/desperdicio_zapata.py` → `docs/experimentos/desperdicio_zapata_2026-11.json`.
