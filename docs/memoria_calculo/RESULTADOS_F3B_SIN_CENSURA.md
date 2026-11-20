# Resultados F3b (#275, #276): confiabilidad sin censura (FORM + muestreo por importancia)

Corrida única según [`PRERREGISTRO_F3B_SIN_CENSURA.md`](PRERREGISTRO_F3B_SIN_CENSURA.md) (incluida su enmienda tras el piloto), del 2026-11-20.

- **Edificios:** 1.348 de 1.348 reproducidos.
- **Elementos:** 106.620 evaluaciones de elemento × variante.
- **Tiempo:** 1.559 s con 6 procesos.
- **Datos:** [`beta_por_edificio.csv`](../../data/memorias_sinteticas/f3b/beta_por_edificio.csv) y [`resultados_f3b.json`](../../data/memorias_sinteticas/f3b/resultados_f3b.json).

## Puerta de calidad: **cumple**

| | Criterio | Resultado |
|---|---|---|
| **Q1**: concordancia con el Monte Carlo de la F3 (716 pares con ≥ 100 fallas) | ≥ 95 % con \|Δβ\| ≤ 0,10 y mediana ≤ 0,03 | **100 %**, mediana **0,006**, p95 0,029 |
| **Q2**: elementos imprecisos (CoV de Pf > 0,10) | ≤ 1 % | **0,40 %** (431 de 106.620) |

## Veredictos

La regla de variantes es la misma de la F3. Recordatorio: H-F3b-1 y H-F3b-3 están **[informadas por F3]** y no son ciegas.

| Hipótesis | Central | Baja | Alta | Veredicto |
|---|---|---|---|---|
| **H-F3b-1**: mediana(alta) − mediana(baja) ≥ 0,5 | **+2,35**, IC [1,92; 2,66] | +0,85, IC [0,67; 1,11] | +1,61, IC [1,34; 1,83] | **CONFIRMADA** |
| **H-F3b-2**: rango intercuartílico de β ≥ 0,75, con límite inferior ≥ 0,5 | **3,00**, IC [2,81; 3,14] | 1,20, IC [1,05; 1,34] | 2,10, IC [1,97; 2,24] | **CONFIRMADA** |
| **H-F3b-3**: en zona baja, altos − bajos > 0 | **+0,93**, IC [0,51; 1,34] | +1,21, IC [0,66; 1,62] | +0,63, IC [0,35; 0,92] | **CONFIRMADA** |

## Lectura

### 1. La NSR-10 cumple bajo gravedad, pero la reserva es muy desigual

**Variante central:**
- La mediana de β₅₀ es **6,1**.
- El percentil 10 es **4,1**.
- El **6,4 %** de los edificios queda por debajo de 3,8.

Pero la dispersión es enorme: el rango intercuartílico es de **3,0 unidades de β**. Las calibraciones de código buscan precisamente lo contrario, una confiabilidad pareja. Esa dispersión la explica sobre todo la amenaza sísmica:

| Zona | Mediana β (central) | Percentil 10 | Fracción con β < 3,8 | Mediana β (alta) | Fracción con β < 3,8 (alta) |
|---|---|---|---|---|---|
| Baja | 5,19 | 3,66 | **13,4 %** | **3,20** | **70,7 %** |
| Intermedia | 5,66 | 4,07 | 6,5 % | 3,50 | 60,8 % |
| Alta | 7,54 | 4,85 | 2,0 % | 4,82 | 29,7 % |

- **En zona alta,** el sismo sobredimensiona y deja una reserva grande frente a la gravedad.
- **En zona baja,** la gravedad gobierna sin esa reserva. Si la incertidumbre real es la desfavorable, **7 de cada 10 edificios de zona baja quedan bajo la referencia EN 1990** (β 3,8, una referencia internacional, no un requisito de la NSR-10).
- **Lo que esto sugiere,** como hipótesis de política y no como conclusión: si hubiera que endurecer algo, convendría hacerlo en los factores de gravedad o en el control de calidad de la obra en zona baja. Los requisitos sísmicos no son el sitio.

### 2. Los edificios bajos de zona baja son los menos confiables

- En zona baja, los edificios de 9 o más pisos superan a los de 5 o menos por +0,93 en β (central).
- Por altura en todo el corpus, la mediana es 5,55 con 1–5 pisos, 7,16 con 6–8 y 6,41 con 9 o más.
- **Dónde está el elemento crítico** (corrección del 2026-11-20). La F3 decía «la viga del nivel 1 es la crítica en el 85 %», y era un **artefacto de desempate**: cuando todos los elementos empatan en el techo de β, `min()` devuelve el primero, que es el nivel 1.
  - Excluyendo los edificios en el techo, la crítica es la **viga del último nivel (cubierta)**:
    - en el **76 %** de los edificios de zona baja, 71 % en intermedia y 63 % en alta (central);
    - en los edificios de zona baja con N ≤ 5: 102 de 116 en la cubierta, 10 en pisos intermedios y **4 en el nivel 1**.
  - **Mecanismo plausible:** arriba la demanda sísmica es mínima, así que el refuerzo de esas vigas lo fija la gravedad, sin la sobrerresistencia sísmica de los pisos bajos.
  - **Advertencia:** el corpus aplica en la cubierta la misma carga viva que en los entrepisos. Si la cubierta real lleva menos carga viva, el β real es mayor; si lleva tanques o equipos, menor.

### 3. La variable dominante no es el material: es el modelo de análisis

Los factores de importancia α² de FORM en el elemento crítico dan:

| Variable dominante | Central | Alta | Baja |
|---|---|---|---|
| θS (error del modelo del efecto de carga) | **95 %** | **99 %** | 58 % |
| Carga viva L | 4 % | — | 37 % |
| f'c | 0,8 % | 0,7 % | — |

- **Lectura:** la flexión en vigas casi no depende de f'c. Con fy de CoV 5 %, la mayor incertidumbre es **qué tan bien el análisis lineal predice el momento real**.
- **Para StructAI:** es la mejor razón para invertir en **#276 P1 (vibración ambiental y calibración del modelo con edificios reales)** antes que en ensayos de material. Reducir V(θS) de 0,10 a 0,08 vale más que cualquier mejora de f'c.
- **Advertencia:** θS es un supuesto (V = 0,10) y no un valor medido. La dominancia depende de él, y por eso en la variante baja la carga viva ya pesa el 37 %.

### 4. Otros descriptivos (central)

- **Perfil de suelo:** la mediana es 5,60 en C, 6,37 en D y 6,90 en E. Los suelos blandos amplifican el espectro, lo que suma más reserva sísmica.
- **f'c:** la mediana es 6,23 con 21 MPa, 6,00 con 28 y 6,05 con 35. Casi no influye, y el percentil 10 empeora con f'c alto: 4,42 → 3,97.
- **Grupo de uso:** la mediana es 6,04 en el grupo I y 6,25 en el III, porque la importancia sísmica suma reserva.
- **Elemento crítico:** es una columna en el 5,5 % de los edificios (0,7 % en la F3, que lo enmascaraba con la censura).
- **Techo β > 8:** lo alcanza el 25 % de los edificios en la central. FORM no convergió en 31 elementos críticos de 1.348; ahí se usó el Monte Carlo de resguardo o el techo.

## Lo que cambia frente a la F3

**H-F3b-1 y H-F3b-3 son las versiones bien planteadas de H-F3b y H-F3c.** La F3 las «refutó» solo porque la censura en 4,5 hacía imposible discriminar. Ahora se confirman con margen amplio en las tres variantes. Como estaban **informadas por F3**, su confirmación pesa menos que una ciega.

## Siguientes pasos

1. **Réplica ciega:** un corpus nuevo con parámetros aleatorios, no la rejilla F1, y las mismas hipótesis prerregistradas. Así se elimina la no-ceguera.
2. **Calibrar θS y la carga viva con datos colombianos** (#276 P1 y P2). Hoy son la incertidumbre que manda.
3. **Confiabilidad del sistema:** correlación entre elementos y redistribución.

## Limitaciones

- Valen todas las de la F3: el β es del elemento y no del sistema, las distribuciones no están calibradas, el corpus es sintético y no hay corrosión ni cortante.
- **No es ciega** respecto a la F3.
- **El techo de 8 entra en las medianas,** y es conservador en las diferencias. En la variante baja, el 55 % de los edificios está en el techo.
- **Alcance:** nada de esto aprueba ni desaprueba un diseño. Todo diseño pasa por la F4 y por la firma de un ingeniero (#18).
