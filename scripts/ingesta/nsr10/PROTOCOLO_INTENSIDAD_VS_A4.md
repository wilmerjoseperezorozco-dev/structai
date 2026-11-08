# Protocolo: capas de intensidad sísmica del SGC frente al Apéndice A-4 de la NSR-10 (fijado el 2026-11-08, antes de cruzar nada)

**Datos (todos municipales, por código DANE):**
1. **A-4 NSR-10** (PDF 2010, ya extraído y verificado): Aa, Av, zona de amenaza.
2. **SGC, Intensidad máxima observada** (`Mapa_Intensidad_Maxima_Observada_Colombia`, capa «Intensidad Observada Municipio»): `GRIDCODE` de 4 a 9 (escala de intensidad macrosísmica; 9 = destructivo) y categoría (`M`, `D`, `CD`, `SIN`; solo se usa `M`). Es una observación histórica, no una probabilidad.
3. **SGC, Zonificación sísmica de intensidad esperada** (capa `Municipios_Int_Sismica`): PGA (en g), rango y percepción. **El servicio no documenta el periodo de retorno ni el modelo** del PGA; por eso no se asume que sea comparable con el Aa de la NSR-10 (que corresponde a un periodo de retorno de 475 años).

**Preguntas y criterios (fijados antes):**
- **Q1 (consistencia de orden):** ρ de Spearman entre Aa y la intensidad observada, y entre Aa y el PGA esperado. IC95 % por bootstrap de bloques por departamento (2.000 réplicas). «Concuerdan» si ρ > 0 con IC que excluye 0; no se fija un umbral de magnitud.
- **Q2 (discordancias que importan):** municipios con intensidad observada ≥ 8 (daño severo o destructivo) y zona **Baja** en el A-4, y municipios con intensidad observada ≥ 8 y Aa ≤ 0,10. Se **listan**; no se interpretan como error del reglamento, porque la intensidad observada depende de la vulnerabilidad local y del suelo, no solo del peligro.
- **Q3 (tamaño de la discrepancia con el PGA esperado):** razón PGA esperado / Aa por municipio: mediana, percentiles 10 y 90, y número de municipios con razón > 1,5 o < 0,67. Se reporta el resultado para la capa **sin concluir cuál es la correcta**.

**Qué NO se concluye:** que el Aa del reglamento esté mal en algún municipio, o que el PGA del SGC sea el valor de diseño. No hay periodo de retorno documentado en la capa esperada, así que Q3 es descriptivo. Una intensidad observada alta en zona «Baja» es una señal para revisar con un ingeniero, no un hallazgo de error.

**Limitaciones declaradas de antemano:** la intensidad observada está sesgada por la antigüedad y la densidad del poblamiento (lugares poco poblados tienen menos registro); es una escala ordinal con pocos niveles (muchos empates); el análisis es municipal (un municipio con relieve variado tiene un solo valor); el PGA del SGC es continuo y el Aa tiene pasos discretos.
