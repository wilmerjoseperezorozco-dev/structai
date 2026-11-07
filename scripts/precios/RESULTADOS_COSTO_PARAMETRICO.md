# Resultados: costo paramétrico de pavimentos y periodo de retorno de alcantarillas

> **Actualización (2026-11-08): el error de unidades de `motor-vias` (issue #103) está corregido y el ítem 4 se recalculó.** La sección «Ítem 4» de abajo conserva el resultado original (con los espesores erróneos) como registro histórico; **los valores vigentes son los de esta nota.**
>
> | Resultado (provincia 0801, costo directo de referencia) | Antes (con el error) | Ahora (corregido) |
> |---|---|---|
> | Estructura flexible para ESAL 5 M y CBR 8 % | 5 / 15 / 15 cm | **5 / 15 / 40 cm** (rodadura / base / subbase) |
> | Costo por m² en esa estructura | 73.266 | **94.764** |
> | Rango en la malla ESAL × CBR | 73.266 en casi todo (constante) | **73.266 a 174.305**, creciente con el tránsito y con la subrasante pobre |
> | Dispersión entre 140 provincias, ESAL 5 / CBR 8 (P90/P10) | 1,19 | **1,30** (IC95 % 1,25-1,33) |
> | Parte de la dispersión explicada por base y subbase | 91 % | **95 %** |
> | Sensibilidad (asfalto 4,5-6,5 %, rodadura ±20 %) | ±5,9 %, ±10,4 % | ±4,5 %, ±8,0 % |
> | Diseños flexibles que el motor marca «no cumple» | 1 de 32 | **9 de 32** (tránsito alto con subrasante pobre: la subbase requerida supera el máximo) |
> | ESAL desde el que el rígido cuesta menos que el flexible | Ninguno | **10 M con CBR 3 %**; en CBR ≥ 5 % sigue sin cruzarse |
>
> Sigue sin ser un costo de diseño validado: el motor mantiene la rodadura (5 cm) y la base (15 cm) en su mínimo y solo ajusta la subbase, y la conversión del pavimento rígido (SN/0,39) no está verificada. Ver el issue de seguimiento.

Ejecutado el 2026-11-07 según [`PROTOCOLO_COSTO_PARAMETRICO.md`](PROTOCOLO_COSTO_PARAMETRICO.md) (commit `8dae609`, anterior a los resultados). Scripts: `costo_parametrico_pavimentos.py` y `periodo_retorno_alcantarilla.py`. Precios INVIAS 2026-1, costo directo de referencia. Señal de análisis, no diseño ni presupuesto.

## Ítem 4: pavimentos

**Verificaciones previas.** S1: las 8 actividades de pavimento tienen precio en las 140 provincias. S2: `costo_directo_total` coincide con la suma de sus componentes (diferencia máxima 0). S3: dos precios superan 3× la mediana nacional (base granular `330,1,1` y riego de imprimación `420,1`, una provincia cada uno).

**Hallazgo principal: la entrada de espesores no es confiable.** `motor-vias` entrega 5/15/15 cm en 28 de 32 diseños de su propia malla. Con los coeficientes estructurales convertidos a cm, esa estructura queda un 31-60 % por debajo del SN requerido para ESAL ≥ 5 millones. Es una causa probable (error de unidades), no demostrada; está en el issue #103. Los costos de abajo son por tanto el costo de **lo que el motor entrega hoy**, no el de un diseño válido.

| Resultado (provincia de referencia 0801, Atlántico) | Valor |
|---|---|
| Costo flexible, estructura 5/15/15 cm | 73.266 COP/m² (rodadura y asfalto 52 %, subbase 18 %) |
| Costo rígido (losa 15 cm) | 139.708 COP/m², unas 1,9 veces el flexible |
| ESAL desde el que el rígido cuesta menos | Ninguno en la malla |
| Dispersión entre 140 provincias, diseño ESAL 5 M / CBR 8 % | P10 69.723; mediana 76.725; P90 83.095; P90/P10 = 1,19 (IC95 % 1,15-1,27) |
| Parte de la dispersión que se explica por base y subbase | 91 % de la varianza logarítmica |
| Sensibilidad | asfalto 4,5-6,5 %: ±5,9 %; cemento asfáltico 40-50 / 80-100: +3,3 % / −5,9 %; espesor de rodadura ±20 %: ±10,4 % |

**Lectura.** Con la estructura dada, la variación entre provincias casi la explican los materiales granulares (el transporte), no el asfalto. Las sensibilidades al asfalto son moderadas. Nada de esto valida cuál pavimento conviene: falta mantenimiento, vida útil y costo de usuario.

## Ítem 5: periodo de retorno de alcantarillas

**Datos.** 132 estaciones limpias a nivel nacional; en el Caribe solo 14, por debajo del mínimo preregistrado de 15, así que el análisis principal es nacional. Curva de crecimiento x_T = Q_T / Q_2 (mediana): T=5: 1,32; T=10: 1,52; T=25: 1,76; T=50: 1,93; T=100: 2,08. El CV de x_100 entre estaciones es 1,06 (alta heterogeneidad).

**Resultado.** T\* = 100 años en 56 de las 60 combinaciones (50 años en las otras 4, con pérdida m = 0,5 y Q_2 = 10 m³/s). El criterio de robustez del protocolo se cumple (moda en 93 % de la malla; acuerdo bootstrap ≥ 80 % en 90 % de las combinaciones).

**Por qué no es una recomendación.**
1. **El óptimo está en el borde de la malla.** T = 100 es el mayor periodo evaluado; el óptimo verdadero podría estar más allá. El criterio preregistrado no incluía una comprobación de borde: es un defecto del protocolo, y se declara aquí.
2. **La economía no discrimina.** El costo de inversión de Q_2 = 2 m³/s va de 20,7 a 24,9 millones COP entre T = 2 y T = 100 (+20 %); para T ≤ 5 es el mismo, porque el cajón mínimo de 0,9 m domina. Agrandar es barato frente a cualquier pérdida plausible, por eso gana el mayor T.
3. **La hidrología es el eslabón débil.** La curva proviene de ríos medianos y grandes, con máximos horarios, no de cuencas pequeñas de crecida súbita. El ajuste estacionario no está calibrado (excedencia observada del Q10: 0,135) y la pérdida m es un supuesto.

**Conclusión sostenible.** Bajo estos supuestos, sobredimensionar una alcantarilla pequeña cuesta poco frente al riesgo, así que el resultado depende de la hidrología de cuencas pequeñas, que estos datos no entregan. Para recomendar un periodo de retorno hacen falta curvas regionales de cuencas pequeñas y un modelo de pérdida con datos reales.
