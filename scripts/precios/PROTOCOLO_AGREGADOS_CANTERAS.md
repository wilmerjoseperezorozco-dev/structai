# Protocolo B1: precio de agregados y producción de canteras (preregistrado 2026-11-08, antes de calcular ninguna asociación)

**Pregunta.** ¿El precio de referencia de los agregados pétreos (arena, grava, triturado) en las provincias de Colombia sigue la oferta local de material, o lo explica solo el costo de llevarlo desde lejos?

**Datos.** (1) INVIAS 2026-1: insumos de categoría AGREGADOS en m³, 140 provincias (`scripts/precios/_cache/`). (2) ANM, volúmenes de explotación y regalías por municipio (`datos.gov.co`, `r85m-vv6c`), años 2019-2024, recursos GRAVAS, ARENAS, RECEBO, GRAVAS DE RIO, ARENA DE RIO, GRAVA DE CANTERA, ARENA DE CANTERA y DIABASA, todos en m³. (3) DIVIPOLA para las coordenadas.

**Variables (fijadas ahora).**
- *Resultado:* índice de prima de agregados de la provincia = media geométrica de precio/mediana nacional del mismo insumo, sobre los insumos de AGREGADOS en m³ con precio en al menos 70 % de las provincias.
- *X1:* log10(1 + volumen declarado 2019-2024 en el departamento de la provincia, m³).
- *X2:* distancia (km, círculo máximo) entre la capital del departamento y el municipio productor más cercano entre los **25 municipios con mayor volumen declarado** (regla fija, sin mirar precios). Si la capital es uno de ellos, la distancia es 0.
- *Control:* distancia a Bogotá y distancia al puerto más cercano (Cartagena, Barranquilla, Santa Marta, Buenaventura), como en `geografia_precios_invias.py`.

**Hipótesis.**
- **B1a.** ρ de Spearman entre el índice y X1 es negativo (más oferta, precio menor).
- **B1b.** ρ de Spearman entre el índice y X2 es positivo (más lejos de un centro productor, precio mayor).
- **B1c.** B1b se mantiene al controlar por la distancia a Bogotá (correlación parcial por rangos): X2 aporta algo más que «estar lejos del centro del país».

**Criterio.** IC95 % por remuestreo de **departamentos** (las provincias de un departamento comparten ubicación) que excluya 0 en el sentido esperado, con corrección de Holm sobre B1a y B1b (α = 0,05). B1c se evalúa solo si B1b se cumple. Un IC que incluya 0 se reporta como resultado nulo.

**Límites declarados de antemano.** El volumen de la ANM es el declarado para liquidar regalías: la extracción informal o sin título no aparece y el sesgo puede ser grande en agregados. El precio de INVIAS es de referencia por provincia, no una cotización. La ubicación de la provincia es la capital del departamento (aproximación gruesa). Es una asociación entre provincias, no una causa. No se nombran productores.
