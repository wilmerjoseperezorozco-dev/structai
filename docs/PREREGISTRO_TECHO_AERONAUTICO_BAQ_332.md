# Preregistro: techo aeronáutico de Barranquilla frente al POT (#332 fase 2, para #325), 2026-11-28

Este documento se fija **antes** de construir la capa y de cruzarla con el POT. Si algo cambia después, se agrega como
enmienda fechada al final, sin borrar lo de arriba.

## Pregunta

¿En qué sectores de Barranquilla la altura máxima que permite el POT (Decreto 0212 de 2014, plano U-16) supera la
superficie limitadora de obstáculos del aeropuerto Ernesto Cortissoz (RAC 14)? ¿Cuánto la supera?

La capa **orienta y no autoriza**: no reemplaza el permiso de la Aerocivil para levantar construcciones (Código de
Comercio, arts. 1823–1826) ni la licencia de construcción.

## Insumos (fijos)

| Insumo | Versión | Archivo |
|---|---|---|
| Superficies limitadoras | RAC 14 Ed. 01 Rev. 05 (06-oct-2025), Tablas D-1 y D-2, aplicables hasta el 20-nov-2030 | `scripts/aeronautico/rac14_superficies.json` |
| Aeródromo | AIP AD 2 SKBQ, AIRAC AMDT 67/24 (28-nov-2024) | `scripts/aeronautico/skbq_ad2.json` |
| Alturas POT | Plano U-16 «Edificabilidad – Densidades urbanísticas», versión de octubre de 2019, MAGNA-SIRGAS origen Barranquilla | `descargas/pot_barranquilla/` (no versionado) |
| Terreno | Copernicus DEM GLO-30 (con los avisos del Art. 6) | por descargar, con permiso |

## Procedimiento

1. **Superficies.**
   - **RWY 05:** aproximación de precisión, categoría I, número de clave 4.
   - **RWY 23:** aproximación que no es de precisión, número de clave 4.
   - **Despegue:** clave 3 o 4.
   - **Horizontal interna:** 45 m sobre la elevación del aeródromo (29 m) y radio de 4 000 m. Se construye como «estadio»
     desde los extremos de la pista. Si la tabla y la figura del RAC no dejan clara la forma, se usa el círculo desde el
     ARP y se informan las dos.
   - **Las demás superficies** (cónica, aproximación, aproximación interna, transición, transición interna y ascenso en
     el despegue) se construyen con las dimensiones de las tablas.
   - El techo en cada punto es la **superficie más baja** que lo cubre, en m sobre el nivel del mar.
2. **Techo sobre el terreno:** techo menos la cota del DEM, en una malla de 30 m.
   - Copernicus es un modelo de superficie: en zona construida sobreestima el terreno, lo que da un techo más bajo y más
     conservador. Se declara como sesgo y no se corrige.
3. **POT a metros.**
   - El U-16 da pisos máximos por zona: 2, 5, 8, 11, 16, 40 y 50. Se georreferencia con la cuadrícula del plano y se
     clasifica por el color de la leyenda.
   - La altura POT se calcula como **pisos × 3,0 m + 1,5 m** (primer piso más alto y remate).
   - Hay una sensibilidad fijada de antemano: 2,8 m y 3,5 m por piso.
   - Las zonas «Especial» (a, b), cuya altura depende de un plan aparte, se reportan aparte, sin altura.
4. **Conflicto** = altura POT > techo sobre el terreno.

## Qué se informa

- Área en conflicto (ha) por nivel del U-16 y por superficie que limita, con el escenario central y las dos
  sensibilidades.
- Un mapa del techo sobre el terreno y otro de los conflictos.
- La distancia mínima entre la zona de 40–50 pisos y la superficie que la limita.

## Validación

- **Control de georreferenciación:** 5 puntos de control fijados de antemano (cruces de la cuadrícula del plano)
  deben quedar a menos de 30 m de su coordenada después de transformarlos. Si no, se corrige el ajuste antes de seguir.
- **Validación contra obstáculos reales:** se usa el listado de obstáculos del Área 2 publicado por la Aerocivil
  («Conjunto de datos AIP»).
  - Ningún obstáculo debería superar el techo calculado en más de 5 m, salvo que el listado lo marque como obstáculo
    aceptado o señalizado.
  - Si más del 5 % lo supera sin esa marca, la construcción de las superficies se considera **errónea** y se revisa
    antes de publicar la capa.
  - Si el listado no está disponible, se dice explícitamente que la capa **no está validada**.
- **Comparación con lo esperado:** en los ejes de la pista, la aproximación debe dar exactamente 2 % (RWY 05) desde
  60 m antes del umbral. Es una prueba unitaria con tolerancia de 0,1 m.

## Limitaciones declaradas

- El U-16 es un plano de impresión a 1:28 000. Por resolución de la extracción, el error de borde de zona es del orden
  de ±10–20 m.
- La conversión de pisos a metros es una convención. El POT regula pisos, no metros.
- No se modelan las superficies nuevas de la OACI (desde 2030), ni las radioayudas, ni las superficies de protección
  de procedimientos (PANS-OPS), que pueden ser más restrictivas.
- No se consideran los planes zonales ni los parciales (zonas «Especial»).

## Enmienda 1 (2026-11-28, antes de cruzar el POT con el techo y antes de abrir el listado de obstáculos)

1. **Puntos de control.**
   - El texto decía «cruces de la cuadrícula del plano». Esos cruces son los mismos puntos con que se ajusta el plano,
     así que no prueban nada.
   - En su lugar se usan las **5 etiquetas de la cuadrícula geográfica** que el plano dibuja aparte (74°54', 74°51' y
     74°48' O en el borde superior; 11°00' y 10°57' N en el borde izquierdo).
   - Se proyectan con pyproj y se comparan con la posición que predice el ajuste. El umbral sigue en 30 m.
   - Resultado: errores de −2,3, −3,7, −1,6, −4,9 y −7,3 m. **Pasa.** Las otras 15 etiquetas geográficas dan como
     máximo 6,6 m.
2. **Meridiano de origen.** El plano no imprime la longitud de origen. Se toma la de la cuadrícula urbana oficial de
   Barranquilla (EPSG:6246, −74,8343313°), que comparte la latitud de origen y los falsos este y norte impresos.
3. **Prueba del 2 %.**
   - Se verifica sobre la **superficie de aproximación**, que es lo que dice el preregistro.
   - El **techo** coincide con ella solo hasta que la aproximación alcanza la horizontal interna (74 m), unos 2,3 km
     antes del umbral. Desde ahí manda la horizontal interna.
   - Ninguna cifra del análisis cambia por esto.
4. **Control de la pista.** Proyectada en la cuadrícula del U-16, la pista SKBQ mide 3 000,4 m (el AIP dice 3 001 m).
