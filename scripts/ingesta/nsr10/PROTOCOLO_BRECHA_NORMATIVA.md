# Protocolo: brecha entre el Apéndice A-4 y la capa del SGC, y a quién afecta (fijado el 2026-11-08, antes de calcular)

**Pregunta.** En los 29 municipios donde el A-4 (PDF 2010) y la capa `Municipios_Amenaza_NR10` del SGC dan valores distintos de Aa o Av, ¿qué tan grande es la diferencia y cuánta población y vivienda vulnerable queda bajo ella?

**Postura sobre la fuente.** No se asume cuál de las dos fuentes es correcta (el resultado previo, `RESULTADOS_AUDITORIA_A4_VS_SGC.md`, no lo pudo determinar). Todo se calcula **en ambos sentidos**: la «brecha» es el intervalo entre el menor y el mayor de los dos valores. Si resulta que la fuente vigente es la menor, la «deuda» sería cero para ese municipio; si es la mayor, es la cifra completa. Se reportan los dos escenarios, no uno.

**Datos (ya en el repo, ningún dato nuevo):**
- `auditoria_a4_vs_sgc.json`: los 29 municipios con diferencia en Aa o Av (los otros 44 casos de «diferencia» son solo de nombre y se excluyen).
- `scripts/satelite/v1_panel.csv`: 1.000 municipios con población, `pct_mat_vulnerable` y NBI 2018. **Límite conocido de antemano:** solo 22 de los 29 están en el panel; los otros 7 se reportan sin exposición, no se imputan.
- **No se usa el Sisbén.** No verifiqué que su acceso sea público y son datos personales; se sustituye por los agregados municipales del DANE (NBI y material de vivienda). Si luego se obtiene el Sisbén agregado por municipio, es un protocolo aparte.

**Medidas fijas:**
- Brecha relativa de demanda: `(máx − mín) / mín` del Aa, y lo mismo para Av, por municipio. Aa y Av son proporcionales a la demanda de diseño, así que la razón es una medida directa de cuánto cambia la fuerza de diseño.
- Población expuesta a la brecha: población del municipio en los que la brecha de Aa o Av es > 0.
- Población bajo escenario «peor caso»: población de los municipios donde la capa del SGC es **mayor** que el A-4 (si el SGC fuera lo vigente y el A-4 lo que se aplicó en el diseño de lo ya construido, el parque existente se diseñó con menos demanda de la actual). Escenario inverso: población donde el A-4 es mayor.

**Confirmatorio (único, para no pescar):**
- **B1:** los 29 municipios con diferencia tienen una `pct_mat_vulnerable` mediana distinta de la de los demás municipios del panel (prueba de Mann-Whitney bilateral, p < 0,05, con IC95 % bootstrap de bloques por departamento de la diferencia de medianas). Se plantea bilateral porque no tengo base para predecir el signo; las diferencias entre fuentes pueden ser un artefacto de actualización que no tenga relación con la vulnerabilidad.

**Descriptivo (sin criterio de decisión):**
- Distribución de la brecha relativa de Aa y de Av (mínimo, mediana, máximo) y cuántos casos cambian de zona (se espera 7 según el resultado previo).
- Cuántos municipios y cuánta población hay en cada escenario (SGC mayor / A-4 mayor).
- Lista ordenada por `población × brecha relativa`, con los 10 primeros, para que un ingeniero revise esos casos. No es un ranking de riesgo.

**Qué NO se concluye:**
- Qué fuente es vigente ni que alguna esté mal.
- Un riesgo sísmico: no hay datos de amenaza real, solo diferencias normativas. La «deuda» es una cota de exposición a una discrepancia, no una probabilidad de daño.
- Nada sobre las viviendas individuales: es nivel municipal.

**Limitaciones de antemano:** n = 29 es pequeño, y B1 tiene poca potencia; un resultado no significativo no demuestra ausencia de relación. Solo 22 tienen exposición. La población de la cabecera y la rural tienen vulnerabilidad distinta y no se separan. Las diferencias de Av tienen menos peso en el diseño de edificios corrientes que las de Aa; se reportan por separado.

**Qué se publica pase lo que pase:** el resultado de B1, la tabla completa de los 29 y los dos escenarios, aunque B1 salga negativo.
