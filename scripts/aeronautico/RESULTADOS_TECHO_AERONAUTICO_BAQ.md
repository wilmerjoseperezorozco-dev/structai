# Resultados: techo aeronáutico de Barranquilla frente al POT (#332 fase 2, para #325), 2026-11-28

Se siguió el [preregistro](../../docs/PREREGISTRO_TECHO_AERONAUTICO_BAQ_332.md) con su Enmienda 1, que se fijó antes del
cruce. Esta capa **orienta y no autoriza**: no reemplaza el permiso de la Aerocivil para levantar construcciones
(Código de Comercio, arts. 1823–1826) ni la licencia de construcción.

## Respuesta corta

- Las superficies limitadoras de SKBQ solo alcanzan el **borde sur** de Barranquilla: **221 ha** de las zonas con
  pisos del U-16 (2 460 celdas de 30 m). Casi todas (2 457) están bajo la **superficie cónica**. El aeropuerto queda en
  Soledad, al sur de la ciudad.
- **Escenario central** (3,0 m por piso + 1,5 m): **0 ha en conflicto** en todos los niveles, con la horizontal
  interna como estadio y también como círculo.
- **Sensibilidad de 3,5 m por piso: 1,2 ha en conflicto** (13 celdas), todas de 16 pisos y en la cónica, a unos 5 km
  del centro de la pista. Con 2,8 m por piso: 0 ha.
- Las zonas de **40 y 50 pisos** (norte y centro) no quedan bajo ninguna superficie.
- **Validación contra obstáculos: pasa, pero con poco poder.** El listado oficial trae un solo obstáculo para SKBQ y
  no tiene coordenadas.

## 1. Áreas y conflicto por nivel (ha)

Horizontal interna como **estadio**, que es la construcción principal del preregistro:

| Pisos U-16 | Área (ha) | Conflicto 2,8 m/piso | Conflicto 3,0 m/piso (central) | Conflicto 3,5 m/piso |
|---:|---:|---:|---:|---:|
| 2 | 41,6 | 0 | 0 | 0 |
| 5 | 1 431,0 | 0 | 0 | 0 |
| 8 | 1 063,8 | 0 | 0 | 0 |
| 11 | 604,0 | 0 | 0 | 0 |
| 16 | 565,7 | 0 | 0 | **1,2** |
| 40 | 283,6 | 0 | 0 | 0 |
| 50 | 72,9 | 0 | 0 | 0 |

- **Como círculo** desde el ARP: 0 ha en todos los niveles y escenarios.
- **Relleno de huecos** (sensibilidad; ver §4): el área clasificada sube de 4 063 a 4 772 ha, y el conflicto no cambia
  (0 ha central; 1,2 ha con 3,5 m/piso).
- **Zonas «Especial»** (a y b, 297 ha): su altura depende de otro plan. Se reportan sin altura, como fija el preregistro.

## 2. Qué superficie limita y cuánto margen queda

Celdas del U-16 bajo alguna superficie, por número de pisos:

| Pisos | Celdas |
|---:|---:|
| 5 | 1 079 |
| 11 | 954 |
| 8 | 359 |
| 16 | 59 |
| 2 | 9 |

Por superficie: 2 457 están bajo la cónica y 3 bajo la horizontal interna.

Margen en esas celdas (techo sobre el terreno − altura del POT, escenario central):

| Percentil | Margen |
|---|---:|
| Mínimo | 2,3 m |
| 1 % | 10,5 m |
| 5 % | 31,6 m |
| Mediana | 78,8 m |

- 7 celdas tienen menos de 5 m de margen y 23 menos de 10 m.
- Techo sobre el terreno más bajo dentro de la ciudad: **25,1 m**.

Las 13 celdas en conflicto con 3,5 m/piso:

| Variable | Valor |
|---|---|
| Superficie | cónica (techo 101–105 m s. n. m.) |
| Terreno según el DEM | 43–50 m |
| Altura libre | 51,8–56,5 m |
| Altura POT para 16 pisos | 57,5 m con 3,5 m/piso; 49,5 m en el escenario central |

**Ojo con el DEM:** Copernicus es un modelo de superficie. Si en esas celdas hay edificios o árboles, el terreno real
es más bajo y el conflicto puede desaparecer. Es el sesgo conservador que se declaró en el preregistro.

Mapas:
- `figuras/techo_sobre_terreno.png`;
- `figuras/margen_pot.png`, con las celdas en conflicto marcadas.

## 3. Validación (preregistrada)

| Control | Criterio | Resultado |
|---|---|---|
| Georreferencia del U-16 | 5 etiquetas geográficas < 30 m | −2,3, −3,7, −1,6, −4,9 y −7,3 m. **Pasa** |
| Prueba unitaria del 2 % | aproximación RWY 05 a ±0,1 m | **Pasa** (11 pruebas en `test_superficies.py`) |
| Obstáculos del listado oficial | ≤ 5 % sin marca con exceso > 5 m | **Pasa, sin poder estadístico** (ver abajo) |

### Listado oficial

Fuente: «Obstáculos AMDT 72», Conjunto de datos AIP, vigente desde 2026-07-09.

- Para SKBQ trae **una sola fila**: «Postes», 12 m, iluminados, «en área de aproximación y despegue, pista 23, 350 m
  del umbral». No trae coordenadas.
- Se ubicó sobre la prolongación del eje, 350 m antes del umbral 23. Allí el techo es la aproximación a la 23, con
  21,95 m.
- No se sabe si los 12 m son cota o altura, así que se evaluaron las dos lecturas:
  - si son **cota**, el poste queda 9,95 m por debajo del techo;
  - si son altura **sobre el umbral** (la lectura más pesimista; el plano tipo A muestra el terreno cerca de 0 m en
    ese punto), queda **6,2 m por encima**.
- En la lectura pesimista el poste está iluminado, es decir, señalizado. Por eso el criterio lo excluye.
- Conclusión: el criterio se cumple, pero **un solo obstáculo, sin coordenadas, no permite validar la construcción en
  serio**.

### Fuente secundaria (no estaba preregistrada; se informa aparte)

Plano de obstáculos de aeródromo OACI tipo A, AD 2 SKBQ-41, AIRAC 69/25. Es un plano escaneado y se leyó a ojo, con
incertidumbre de unos ±20 m en distancia y ±2 m en cota.

| Obstáculo | Distancia | Cota | Techo | Exceso |
|---|---:|---:|---:|---:|
| Obstáculo móvil al SO | 740 m | 35 m | 42,6 m | −7,6 m |
| Obstáculo n.º 2 al NE | 170 m | 21 m | 18,4 m | **+2,7 m** |
| Muro al NE | 350 m | 2 m | 22,0 m | −20 m |
| Obstáculo móvil al NE | 600 m | 10 m | 27,0 m | −17 m |

- Ningún obstáculo supera el techo en más de 5 m.
- El n.º 2 lo supera en unos 2,7 m. En el propio plano casi toca la pendiente del 2 %, así que es coherente.

### Alcance de la validación

Todos estos obstáculos están a menos de 1 km de los extremos de la pista. Ahí las superficies quedan totalmente fijadas
por las tablas del RAC. **No validan la cónica a 5 km**, que es donde está el hallazgo. Esa parte descansa en la
georreferencia (que pasa) y en las pruebas unitarias de la cónica (que pasan).

Archivos: `validar_obstaculos.py` → `validacion_obstaculos.json`.

## 4. Limitaciones

1. **Soledad no está.** El aeropuerto queda en Soledad, y casi toda la aproximación y la horizontal interna caen sobre
   ese municipio, no sobre Barranquilla. El U-16 solo cubre Barranquilla, así que **este resultado no dice nada de
   Soledad, Malambo ni Galapa**. Para ellos haría falta el POT de cada municipio.
2. **DEM de superficie.** Copernicus incluye edificios y vegetación, de modo que el techo sobre el terreno sale más bajo
   de lo real. Las 1,2 ha de la sensibilidad están en este caso.
3. **Huecos de clasificación.** Parte del U-16 quedó sin clase (vías, rótulos y texturas que tapan el color, sobre
   todo en el SO). El relleno por vecindario asigna clase a unas 710 ha más y no cambia el resultado.
4. **Extracción de un plano de impresión** a 1:28 000. El error de borde de zona es de ±10–20 m, y los colores del mapa
   se asignaron a la leyenda con un histograma (`clasificar_u16.py`).
5. **Fuera del alcance:**
   - no se modelan las superficies de protección de procedimientos (PANS-OPS) ni las de radioayudas, que pueden ser
     más restrictivas;
   - tampoco las nuevas superficies OACI (OFS/OES, desde 2030);
   - ni los planes parciales y zonales (zonas «Especial»).
6. **Pisos a metros es una convención.** El POT regula pisos, no metros. La sensibilidad muestra que el resultado
   depende de esa convención solo en 1,2 ha.

## 5. Cómo reproducir (entorno geo, fuera del venv de la API)

```text
python -I scripts/aeronautico/georef_u16.py      <U16.pdf> georef_u16.json
python -I scripts/aeronautico/clasificar_u16.py  <U16.pdf> georef_u16.json u16_pisos.npz
python -I scripts/aeronautico/cruce_pot_techo.py u16_pisos.npz <dir_copernicus> <dir_salida>
python -I scripts/aeronautico/mapas_techo.py     <dir_salida>/techo_malla.npz scripts/aeronautico/figuras
python -I scripts/aeronautico/validar_obstaculos.py scripts/aeronautico/validacion_obstaculos.json
```

Los insumos (plano U-16, teselas DEM, listado de obstáculos) y las mallas `.npz` **no se versionan**. Se descargan de
sus fuentes oficiales.

## Avisos

Produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided under
COPERNICUS by the European Union and ESA; all rights reserved. The organisations in charge of the Copernicus programme
by law or by delegation do not incur any liability for any use of the Copernicus WorldDEM-30.

Fuentes normativas:
- RAC 14 Ed. 01 Rev. 05 (Aerocivil);
- AIP Colombia AD 2 SKBQ, AIRAC 73-26;
- POT de Barranquilla, Decreto 0212 de 2014, plano U-16 (oct. 2019).
