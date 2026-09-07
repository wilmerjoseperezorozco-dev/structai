# Fuentes normativas — NSR-10

Mapa real de qué archivo de Google Drive corresponde a qué Título/Capítulo
de la NSR-10, y estado real de ingesta verbatim por título. Existe porque
hasta el 2026-09-01 esta información solo vivía en la memoria privada de
sesiones de Claude Code — si esa memoria se perdiera, reconstruir "qué PDF
es cuál título" habría requerido releer 90+ archivos de Drive uno por uno.
Este documento cierra ese hueco de lineage/ownership: vive en el repo,
versionado en git, no depende de ninguna sesión de IA en particular.

## Carpeta de Drive

- **Carpeta padre** (todos los 87 archivos PDF de NSR-10): `1cjG4OHjxLpla0s5dlpnWS_PAhTd6Dqmh`
  — https://drive.google.com/drive/folders/1cjG4OHjxLpla0s5dlpnWS_PAhTd6Dqmh
- Cobertura real: páginas Drive 1 a 1625, con un hueco real documentado abajo.
- El catálogo detallado por archivo (capítulos, tablas mencionadas, notas de
  corrección histórica, huecos de numeración no verificados uno a uno) vive
  local en `scripts/ingesta/nsr10/raw/_catalogo_maestro_limpio.txt` —
  **gitignored a propósito** (es un catálogo intermedio/documento fuente,
  misma convención que los PDF crudos, ver `scripts/README.md`). Este
  documento es el resumen navegable y versionado; el catálogo local sigue
  siendo la fuente de mayor detalle si hace falta.

## Hueco real conocido en la fuente

**Página Drive 560 no existe como archivo.** Verificado por lectura de
contenido (no solo numeración): el Apéndice C-F "Equivalencia SI/mks/inglés"
se corta a mitad de una ecuación en la página interna C-257 (fin de
`NSR-10-551-559.pdf`), y el siguiente archivo (`NSR-10-561-563.pdf`) retoma
directamente en C-259. No existe ningún archivo en la carpeta de Drive que
cubra esa página — pérdida real de una fracción del Apéndice C-F. Documentado
por decisión del usuario (2026-08-01): no bloquea el resto del catálogo, pero
sigue pendiente de completar si aparece la fuente.

## Estado real de ingesta verbatim por título (actualizado 2026-09-07, `count(*)` real contra `nsr10_chunks`)

Los conteos de esta tabla crecieron bastante frente a versiones anteriores
de este documento — no por contenido nuevo en A/B/H/K, sino por la
auditoría de tokens reales del 2026-09-01 (ver nota más abajo), que
re-trocheó todo el corpus a piezas más pequeñas respetando el límite real
de 128 tokens del modelo de embeddings. Un título con más chunks hoy no
significa más norma cubierta, solo troceo más fino.

| Título | Chunks reales | Estado |
|---|---|---|
| A — Requisitos generales | 75 | Verbatim, **pero sin auditoría numeral por numeral todavía**. 15 chunks no-verbatim (parafraseados, presentados como texto oficial) borrados el 2026-09-01 — issue [#38](https://github.com/wilmerjoseperezorozco-dev/structai/issues/38) sigue abierto. No se ha comparado A.1–A.9 numeral por numeral contra el PDF fuente (el método sí aplicado a K.3 — ver más abajo) para confirmar que no falten numerales enteros |
| B — Cargas | 169 | Verbatim, mismo caveat que A: nunca se auditaron huecos específicos numeral por numeral |
| C — Concreto estructural | 2.410 | Verbatim completo, auditado (0% de chunks truncados) |
| D — Mampostería estructural | 711 | Verbatim completo, auditado (0% de chunks truncados) |
| E — Casas de 1 y 2 pisos | 37 | Verbatim completo (E.1–E.9) |
| F.1–F.4 (generalidades, acero laminado/armado/tubular, provisiones sísmicas, acero formado en frío) | 988 | **Verbatim completo** (F.4 cerrado 2026-09-01) |
| F.5.1–F.5.4.6 (Aluminio — generalidades, propiedades, principios de diseño, miembros: generalidades/esfuerzos/pandeo local/ablandamiento/vigas/tensión) | 403 | Verbatim completo |
| F.5.4.7 (Miembros a compresión) | 0 | **Pendiente** — la pieza más densa de F.5 (Tabla F.5.4.7-2, 18 tipos de sección con fórmulas propias cada uno), ya mapeada parcialmente pero no transcrita, mismo `NSR-10-1083-1182.pdf` ya descargado |
| F.5.4.8–F.5.4.9, F.5.5–F.5.8 + apéndices F.5.A–F.5.F (cierra el Título F) | 0 | Pendiente — requiere descargar `NSR-10-1183-1283.pdf` (id `1xuOZukeQsLIV957z59BK2eJqpZ5qu__b`, confirmado real, no descargado todavía) |
| G — Madera y Guadua | 464 | Verbatim completo |
| H — Estudios geotécnicos | 48 | **INCOMPLETO — hueco real grande, confirmado 2026-09-07 con auditoría numeral por numeral** (`pypdf` sobre los 3 PDF fuente + comparación contra `nsr10_chunks`, 181 encabezados reales identificados). Solo cubre H.1–H.3.2 (~18% del título, 33 de 181 encabezados). **Faltan por completo H.3.3 (ensayos de laboratorio) y los capítulos H.4 (cimentaciones), H.5 (excavaciones y taludes), H.6 (estructuras de contención), H.7 (efectos sísmicos/licuación), H.8 (sistema constructivo), H.9 (suelos expansivos/colapsables) y H.10 (rehabilitación sísmica)** — 148 de 181 encabezados sin chunk. Los 3 PDF fuente ya están descargados en `scripts/ingesta/nsr10/raw/`. 13 chunks no-verbatim (de lo poco que sí existía) borrados el 2026-09-01 — issue [#38](https://github.com/wilmerjoseperezorozco-dev/structai/issues/38) sigue abierto |
| I — Supervisión técnica | 33 | Verbatim completo (I.1–I.4) |
| J — Protección contra incendios | 18 | Verbatim completo (J.1–J.4) |
| K — Otros requisitos complementarios (K.1–K.4.3) | 416 | **Verbatim completo, incluido K.4.3** — corrección real 2026-09-07: una memoria interna daba K.4.3 por "bloqueado, sin fuente" desde 2026-08-28, pero en algún punto posterior sí se ingestó sin que se actualizara esa nota; confirmado con SQL directo (chunks reales `NSR10-K-K_4_3_*`, K.4.3.1 a K.4.3.9) y con una respuesta real de `ask()` citando K.4.3.2 con precisión exacta |

**Título F, total real hoy**: 1.391 chunks (988 + 403) de los ~2.200-2.400
estimados para cerrarlo por completo — sigue siendo, con diferencia, el
título con más volumen de todos.

**Sobre la auditoría numeral por numeral (mismo método que confirmó
K.3.11–K.3.18, 0% cubiertos, 2026-08-27 — extraer con `pypdf`/regex los
numerales que existen REALMENTE en el PDF fuente y compararlos contra los
ids de chunk en la base, no solo mirar si "el chunk que existe se ve
completo")**:

- **Título H — auditado 2026-09-07, hueco real confirmado** (ver fila de
  arriba): 148 de 181 encabezados reales sin chunk, el título cubre apenas
  H.1–H.3.2. No era un caso de "probablemente está bien, falta el
  papeleo" — de hecho la mayoría técnica del título (cimentaciones,
  taludes, muros de contención, licuación, suelos problemáticos,
  rehabilitación sísmica) nunca se ingestó.
- **Título A — auditoría en curso**, mismo método, resultado pendiente.
- **Título B — todavía sin auditar**, dado el hallazgo real de H no
  asumir que B está bien solo porque no se ha revisado.

**Nota real sobre calidad, ya corregida (2026-09-01)**: se encontró que
151 de 293 chunks (51.5%) de F.4.3/F.4.4/F.4.5 se truncaban en silencio al
buscar, por un bug real del splitter de troceo. Generalizado el chequeo a
**todo** `nsr10_chunks` (4.129 chunks medidos entonces): 493 (11.9%)
superaban el límite real de 128 tokens, con severidad muy dispareja —
Títulos K, B, J y A rotos al 100% de sus chunks; C, D, H y las 3
resoluciones SGSST en 0%. **Corregido el mismo día para todo el corpus**
(no solo F.4.3-F.4.5): verificado con una segunda auditoría independiente,
0% de chunks sobre el límite en la totalidad de `nsr10_chunks`. Esto
explica por qué los conteos de A/B/K de esta tabla son mucho más altos que
en versiones anteriores del documento — no es contenido nuevo, es el mismo
texto verbatim ya cargado, re-trocheado en piezas más pequeñas y
correctas. Script de auditoría reusable:
`scripts/mantenimiento/auditar_tokens_reales_corpus_completo.py`.

## Otros dominios (no cubiertos por este documento todavía)

RAS 2000 (motor AquAI), NTC/SGSST, ACI-318, interventoría, y las normas de
otros países del programa de replicabilidad (Perú E.030, Ecuador NEC-SE-DS)
tienen su propia procedencia documentada dentro de los docstrings de sus
scripts de ingesta respectivos (`scripts/ingesta/<dominio>/`), no
consolidada aquí. Candidato real para una futura extensión de este
documento si se vuelve a sentir el mismo dolor de "¿de dónde salió esto?".

## Tabla completa: los 87 archivos PDF de NSR-10 en Drive

Generada programáticamente desde `_catalogo_maestro_limpio.txt`
(2026-09-01) para minimizar error de transcripción manual sobre 87 filas.

| Archivo Drive | Drive file ID | Páginas Drive | Título(s) NSR-10 que cubre |
|---|---|---|---|
| `NSR-10-1-42.pdf` | `1FE_Q1ZkpTHi02qzTeFfYvZ8SiSG0c0nl` | 1-42 | Frente/preliminares del documento — no corresponde a un Título específico; resume y referencia TODOS los Títulos (A a K) |
| `NSR-10-43-54.pdf` | `18hLA1kxfXSYM6_BBEhZAGrQoIyLWoEKi` | 43-54 | Título A — Requisitos generales de diseño y construcción sismo resistente |
| `NSR-10-56-81.pdf` | `1oXm1kdtcMT2IE7ncFXmjKhybR3GEuh-g` | 56-81 | Título A |
| `NSR-10-81-94.pdf` | `1Z2rzll9ER-td_OGXzTUUPv1R68kAoNSL` | 81-94 | Título A |
| `NSR-10-95-105.pdf` | `1-KdJrOrUi_CTanS9XwJ7F1yDUGR83iuZ` | 95-105 | Título A |
| `NSR-10-106-115.pdf` | `1K7g_gGXO8hinr4_gIZxX31A-3tOxRx8A` | 106-115 | Título A |
| `NSR-10-116-123.pdf` | `10GAjgw1bkvL_o2joqtlofClkvDfLtNK-` | 116-123 | Título A |
| `NSR-10-124-128.pdf` | `1Uz5bf-lKMi5w4-2srJGTC_6jiuIxOiij` | 124-128 | Título A |
| `NSR-10-130-138.pdf` | `1-aUdCX_gFVIuooVNKrxu3xYB0WUlwo4p` | 130-138 | Título A |
| `NSR-10-140-154.pdf` | `1-QYd8J2UT0e9J0NQqp--2R4zVkoLhE9G` | 140-154 | Título A |
| `NSR-10-156-158.pdf` | `1iWkVUjD0g6FhAqFQu_uk2TdMbUwQ051O` | 156-158 | Título A |
| `NSR-10-160-166.pdf` | `1ADbcvU5sdKszsu1YBX_PQh7wa1EeW82y` | 160-166 | Título A |
| `NSR-10-168-181.pdf` | `1_rIFrq446kA5KvtuhkBAz3EChmnTZPju` | 168-181 | Título A |
| `NSR-10-183-190.pdf` | `17GTmdRIAURzlFrZlmhfK7ZA-APQ7JGvp` | 183-190 | Título A |
| `NSR-10-191-218.pdf` | `15ITURkjmFtqW2Ti-NEGaV63083QIby7t` | 191-218 | Título A |
| `NSR-10-219-221.pdf` | `1QfZAq-Iq7niauW_cj-CHqi31jG_r1zvV` | 219-221 | Título B — Cargas |
| `NSR-10-222-226.pdf` | `1fs3wrb8XUW1RQl15wgwlORir7aQOiFub` | 222-226 | Título B |
| `NSR-10-228-233.pdf` | `1JW5YAIgkKWDxx0zaEzKY9Q5ViW7L1uWv` | 228-233 | Título B |
| `NSR-10-234-237.pdf` | `10HxWiRfuK_hGoSEeLpKOThRJR4nQBFgL` | 234-237 | Título B |
| `NSR-10-238.pdf` | `1ZPWTQjhxPI-aX7WeDFoe3vhPEWxYG_0G` | 238 | Título B |
| `NSR-10-240-301.pdf` | `1ZLlTm7J__ucSvEt99qizpl3AocB12naL` | 240-301 | Título B |
| `NSR-10-302-306.pdf` | `1GG9xFIcyG40bRxL8BoiSGvFURSUDK5qA` | 302-306 | Título C — Concreto estructural |
| `NSR-10-307-326.pdf` | `15RTPZ-YuHm8Si_8bvqVbQa6mvp4d3PC7` | 307-326 | Título C |
| `NSR-10-327-335.pdf` | `1wLo8D1HHvJGZ-bwUjDX4padkPhHWwKlU` | 327-335 | Título C |
| `NSR-10-337-340.pdf` | `1TgJElqq6wHfw_z7iZ-9CiEDocumuTmYn` | 337-340 | Título C |
| `NSR-10-341-347.pdf` | `14FNc8gDURxzl0Tx5rIqiUG9-CkUNUlAV` | 341-347 | Título C |
| `NSR-10-349-351.pdf` | `1SM6LyDkFQwDCLS3oIphbIOFTwRTx1-5j` | 349-351 | Título C |
| `NSR-10-353-362.pdf` | `1Jv-QdqVSTXBTc6YryrOUr0oi7WL8cXKr` | 353-362 | Título C |
| `NSR-10-363-367.pdf` | `16naJnmO-oc43chhaMiwH8xN6nmK9p_ir` | 363-367 | Título C |
| `NSR-10-369-375.pdf` | `1oeZnIpg80Q43K7hgcbFrV8L8vQ9ZAe8w` | 369-375 | Título C |
| `NSR-10-377-387.pdf` | `1pWyvESW5zxlrSDmkf_Mq5mqLt-HaylGd` | 377-387 | Título C |
| `NSR-10-389-407.pdf` | `1GjwE7e-6PrdG-1oB_6a5pOACgcGPfP-B` | 389-407 | Título C |
| `NSR-10-409-419.pdf` | `1o1f3UOenS1jMjTFJCbxcoDSyaYlm0bVU` | 409-419 | Título C |
| `NSR-10-421-434.pdf` | `1rnyD279L75BRYj37RKmUonfFLZpbq6q_` | 421-434 | Título C |
| `NSR-10-435-438.pdf` | `11rUWagmqgIg0qUMQxm1psrakoWpq9AF3` | 435-438 | Título C |
| `NSR-10-439-442.pdf` | `1smeqckxouKNR1JgDrjlJslBD1M21-teE` | 439-442 | Título C |
| `NSR-10-443-448.pdf` | `1vOMV5i2zKWXLWKNEN6ydod-mBkvm28fY` | 443-448 | Título C |
| `NSR-10-449-452.pdf` | `1NhX0OSYA5f1bWRuw10mRk1urA50BZNTv` | 449-452 | Título C |
| `NSR-10-453-467.pdf` | `1xKquECuk3uMOqibbBHzaTR7fAmWhJ5rA` | 453-467 | Título C |
| `NSR-10-469-471.pdf` | `1WKY1RHabP5UtGN9DbOPDxdMrrQ4730DT` | 469-471 | Título C |
| `NSR-10-473-475.pdf` | `1uFLdvk6of90E4OUsFqVxYGFlV9Lx7TlT` | 473-475 | Título C |
| `NSR-10-477-501.pdf` | `1omqD-cbxdtW-EICMmIa6mcUp4XEGRqVu` | 477-501 | Título C |
| `NSR-10-503-508.pdf` | `1RIVSynbH1B9eqZfNDJib0j3N9RTMkpx0` | 503-508 | Título C |
| `NSR-10-509-524.pdf` | `1Ysawa0UrNH-iPB8F8R9jrigx_a8tSSH7` | 509-524 | Título C |
| `NSR-10-525-528.pdf` | `1HlPRfbeSYkMc4080ayr2KF3DgooD0DTm` | 525-528 | Título C |
| `NSR-10-529-531.pdf` | `1cr7WV4rl-huaujmoOc-25nyQ_q67k0Xk` | 529-531 | Título C |
| `NSR-10-533-535.pdf` | `1bS0Ky3YAjvS_ONBvu_ekkEgR2hjKyZAQ` | 533-535 | Título C |
| `NSR-10-537-550.pdf` | `1Ve_VbHxBMoOL9itWKtq5rgDylGJy6EA8` | 537-550 | Título C |
| `NSR-10-551-559.pdf` | `1oww3CM4OOoWROkEnAThYfWWmNC2Fzpft` | 551-559 | Título C (fin — ver hueco de la página 560 arriba) |
| `NSR-10-561-563.pdf` | `1eBPBon0MfXqWVoFoeSdQgxeMkSQ-BoKB` | 561-563 | Título C (Apéndice C-G en adelante) |
| `NSR-10-565-569.pdf` | `1LayIE7iRuAqEXNLMbEyz1EH8LCpM5BOn` | 565-569 | Título D — Mampostería estructural |
| `NSR-10-570-577.pdf` | `1f9qokn6yW9B3dIUIKeqAQ5KmTDRDOwL1` | 570-577 | Título D |
| `NSR-10-578-585.pdf` | `17GXpDJk_Pdc7_KTRR8xFssFZFGLRV97u` | 578-585 | Título D |
| `NSR-10-586-594.pdf` | `1D6qb6zw3DDNa9y6Z6d83iBCnFJQJyV6B` | 586-594 | Título D |
| `NSR-10-596-607.pdf` | `1yCB-S_xJv_5USUPcz5PPlGx68L7Ks-Rx` | 596-607 | Título D |
| `NSR-10-608-610.pdf` | `1QRiGCTDJcTdq6tpbE3GR02asFlzcNJ_m` | 608-610 | Título D |
| `NSR-10-612-613.pdf` | `1wJ2L1-tIdhDR-H3V0vQQK0oOO-zpi-zb` | 612-613 | Título D |
| `NSR-10-614-615.pdf` | `1p2bI1oS4LTLy_65mIsUr_EZ_aAvGRmQr` | 614-615 | Título D |
| `NSR-10-616.pdf` | `1VoXYeio7wnewSUPa4mASs-3mpWx1DZ9V` | 616 | Título D |
| `NSR-10-618-626.pdf` | `15EN9smBI-6Rdqvg_reL4TpguXl21RuHA` | 618-626 | Título D |
| `NSR-10-628-629.pdf` | `1ljmWcNf1DPpZ-AFNCPpu9uaIGTheMYtG` | 628-629 | Título D |
| `NSR-10-630-632.pdf` | `1BDBrYKhSyAHp_-hn8JTRuLYmxI5jM2_e` | 630-632 | Título D |
| `NSR-10-634-639.pdf` | `1jynQiUueUL2e4_zBXwrBdCHMh8JHlYQM` | 634-639 | Título D (fin) |
| `NSR-10-640-645.pdf` | `19Q4eHuWYfnqP2sOl2yA_sFlkpCHkdmJv` | 640-645 | Título E — Casas de 1 y 2 pisos |
| `NSR-10-647-650.pdf` | `1wXLPONpRf0jE5zrcLCdIdPd9eh6H1CvJ` | 647-650 | Título E |
| `NSR-10-651-656.pdf` | `15TEbUtDIBiBJOYWPV6gnhBv6wnz4wFfU` | 651-656 | Título E |
| `NSR-10-657-659.pdf` | `1esCTjzirgAYJo0Od6TkGmevawU30tBO2` | 657-659 | Título E |
| `NSR-10-661-662.pdf` | `1L0UTAwzdv7yORk-Qsy4U-UCTVXscxJ7r` | 661-662 | Título E |
| `NSR-10-663-668.pdf` | `1MmwioL9qcmrvwq_HCpivlVN1OVMqVPxe` | 663-668 | Título E |
| `NSR-10-669-673.pdf` | `1hOnhHtDKKVSBfJT2lcCP9qkrd2A4wVzQ` | 669-673 | Título E |
| `NSR-10-675-677.pdf` | `1Wi6mUKjduN2_TZlmIYCqqORAnL1O4qE7` | 675-677 | Título E (fin) |
| `NSR-10-681-712.pdf` | `1bqvzOLETovw6ePw9wSD0g5kFntS4nnuK` | 681-712 | Título F — Estructuras metálicas |
| `NSR-10-712-742.pdf` | `14t3dnpSmcqmLHvC-Qn5NOsQYmHlV99SB` | 712-742 | Título F |
| `NSR-10-743-770.pdf` | `15RBFpErGNE3cYaDsVGIYyVbwCu0NbdCF` | 743-770 | Título F |
| `NSR-10-771-800.pdf` | `1SdwrVt8VdwB-UgB74Rdk4aAvkDPPNdhj` | 771-800 | Título F |
| `NSR-10-801-840.pdf` | `1qqTLAZvH7iG4_qVQToeY_fgKwblxlffk` | 801-840 | Título F |
| `NSR-10-841-900.pdf` | `116BU3sPl1kJfQxYct7AaS2wf9-kMPzgF` | 841-900 | Título F |
| `NSR-10-901-980.pdf` | `14q4ylyJYB9H1IdLrdZ0X0crekxxbajmm` | 901-980 | Título F — F.3 (F-220 a F-299) |
| `NSR-10-982-1082.pdf` | `1Mr7auE8pwQ3IiQaZmLgVY5-Xdu7psmze` | 982-1082 | Título F — F.4.1 a F.4.7 (F-301 a F-401) ✅ verbatim completo |
| `NSR-10-1083-1182.pdf` | `1XeyIKw992yoJAD1kgjmYJ5qEA70R85Gi` | 1083-1182 | Título F — F.4.7 (cont.) + F.4.8 (F-402 en adelante) — descargado localmente, F.4.8 pendiente de ingestar |
| `NSR-10-1183-1283.pdf` | `1xuOZukeQsLIV957z59BK2eJqpZ5qu__b` | 1183-1283 | Título F — F.5 Aluminio + apéndices, cierra el Título F — pendiente, no descargado todavía |
| `NSR-10-1284-1320.pdf` | `13jdgOa7_r2qZfxaIOT-_0UY1FvAX0q1B` | 1284-1320 | Título G — Madera y Guadua |
| `NSR-10-1321-1400.pdf` | `1M5uohqWc7oyyoVudbJcMPZN-AiYm0CAa` | 1321-1400 | Título G |
| `NSR-10-1401-1450.pdf` | `1-EB1qUFpZCvgDtp0wOrB-cwAbvlL0O3-` | 1401-1450 | Título G (fin) + Título H — Estudios geotécnicos (inicio) |
| `NSR-10-1451-1500.pdf` | `1DSJnOYqJixF0Nm1ewOH1VBDFpKas4x-y` | 1451-1500 | Título H |
| `NSR-10-1501-1570.pdf` | `1AXhovLAquw_qFr0I4B7IiTGmuiIl24JP` | 1501-1570 | Título H (fin) + Título I — Supervisión técnica + Título J — Incendios + Título K — Complementarios (inicio, K.2 K-3 a K-8) |
| `NSR-10-1571-1625.pdf` | `1M_lQD8NRDBHaB6pc_GE1n2l2sW34U88Z` | 1571-1625 | Título K (K.2 K-9 a K-12, K.3 completo, K.4.1, K.4.2, K.4.3 parcial hasta K.4.3.16 — **último archivo de la carpeta, K.4.3 bloqueado a partir de aquí**) |

## How to apply

Antes de arrancar una nueva pieza de ingesta verbatim de NSR-10, buscar el
título en la tabla de arriba para saber qué archivo de Drive descargar (o
confirmar que ya está en `scripts/ingesta/nsr10/raw/`, gitignored, antes de
volver a descargarlo). Actualizar la sección "Estado real de ingesta" de
este documento en el mismo commit que cierre un título — que no vuelva a
vivir solo en memoria privada.
