# Prerregistro #320: validación ciega de la V por municipio (v1)

Fijado el 2026-11-24, **antes** de que Wilmer lea la muestra.

## Qué se valida

`data/viento/v_municipio.csv` v1, generado por estos scripts del commit de este prerregistro:
- `scripts/viento/digitalizar_fig_b641.py`: figura digitalizada desde el PDF oficial, con su cuadrícula como georreferencia. El cierre máximo de líneas es de 0,058°.
- `scripts/viento/asignar_municipios.py`: cabecera DANE, V máxima a menos de 0,10° y marca de frontera a 0,15°.

## Decisiones de digitalización declaradas antes de validar

1. **Corte en Valledupar.** El rótulo "VALLEDUPAR" tapa las líneas entre la franja 1 (sur) y la franja 2 (norte). Se cierra con lat = 10,32°.
2. **Rótulo "2" de La Guajira.** Su círculo cae fuera del contorno del país, a 0,09°. Se asigna a la cara más cercana.
3. **Caras diminutas que crean los cierres** (< 0,01 grados²): toman la V máxima de sus vecinas.
4. **Caras sin rótulo:** zona de la nota, 28 m/s.
5. **San Andrés y Providencia:** región 5, por el recuadro.

## Muestra

- 60 municipios, estratificados: V asignada (17, 22, 28, 33, 36) × frontera (sí/no), 6 por estrato.
- Semilla 3200, orden aleatorio.
- Ids en `data/viento/muestra_validacion_320.txt`; hoja en `HOJA_VALIDACION_320.md`, sin la V.
- **Validador:** Wilmer, a ojo sobre la Fig. B.6.4-1 impresa o en pantalla, ubicando la cabecera por latitud y longitud.
- Wilmer **no abre** la clave (`v_municipio.csv`, GeoJSON) hasta entregar la hoja.

## Criterios (fijos)

| Id | Métrica | Criterio |
|---|---|---|
| **V1** (primaria) | Municipios **no frontera** cuya región leída por Wilmer coincide con `v_cabecera` | ≥ 95 % |
| **V2** (seguridad) | Municipios (todos) con `v_asignada` **menor** que la V leída por Wilmer (si anota dos regiones, se toma la mayor) | **0** |
| V3 (descriptiva) | Coincidencia en los municipios frontera, y los casos en que Wilmer anota dos regiones | sin criterio |

- **PASA** si V1 y V2 se cumplen. Entonces #321 fase 2 puede usar `v_basica` por defecto, con aprobación.
- **NO PASA:** se diagnostica y cualquier corrección es una v2, que se valida con una **muestra nueva** de municipios distintos.
- Lo anotado en la hoja no se reinterpreta después de ver la clave. Las ilegibles o en blanco se reportan aparte.

## Fuera de alcance

- Polígono municipal del MGN (v2 posible, con aprobación de descarga).
- Exposición y Kzt.
- Velocidades por estudio de sitio.
