# motor-geotecnia (#136)

Asentamientos y capacidad portante de cimentaciones superficiales según el Título H de la NSR-10. Los valores
normativos se cotejaron con la NSR-10 impresa (Minvivienda / AIS, 2010; copia local fuera del repositorio, págs. H-17
a H-19).

| Función (`src/contrato_api.py`) | Endpoint | Qué calcula | NSR-10 |
|---|---|---|---|
| `asentamiento_contrato` | `POST /geotecnia/asentamiento` | Consolidación primaria última por estratos y t90 | H.4.8.2, H.4.9.2 |
| `asentamiento_total_contrato` | `…/asentamiento-total` | Inmediato + consolidación a 20 años + secundario, contra 30 / 15 cm | H.4.8.1–H.4.8.4, H.4.9.2 |
| `diferencial_contrato` | `…/diferencial` | Δ entre apoyos contiguos contra ℓ/1000, ℓ/500, ℓ/300 o ℓ/160; giro contra ℓ/250 | H.4.9.3 (Tabla H.4.9-1), H.4.9.4 |
| `multicapa_contrato` | `…/multicapa` | Consolidación multicapa en el tiempo (volúmenes finitos, solución espectral) | H.4.8.2 |
| `montecarlo_contrato` | `…/asentamiento-montecarlo` | Percentiles y P(S > límite) con Cc y e0 lognormales | H.4.9.2 |
| `portante_contrato` | `…/portante` | q_ult de Vesić, carga vertical centrada | H.4.7 (Tabla H.4.7-1) |
| `portante_excentrica_contrato` | `…/portante-excentrica` | Área efectiva de Meyerhof y factores de inclinación de Vesić | H.4.7, H.4.10 |

Todas devuelven `ResultadoMotor` con supuestos, advertencias y `en_borde_dominio`. Los endpoints tienen límite de tasa y
responden 422 con la norma citada.

## Valores de la norma

| Dato | Valor | Fuente |
|---|---|---|
| FS indirecto mínimo, capacidad portante | 3,0 (D + L normal), 2,5 (D + L máxima), 1,5 (D + L normal + sismo seudoestático) | Tabla H.4.7-1 |
| Asentamiento total a 20 años | 30 cm aisladas; 15 cm entre medianeros | H.4.9.2 |
| Asentamiento diferencial | ℓ/1000 (a), ℓ/500 (b), ℓ/300 (c), ℓ/160 (d) | Tabla H.4.9-1 |
| Giro | ≤ ℓ/250 | H.4.9.4 |
| Asentamiento total | inmediato + consolidación + secundario | H.4.8.4 |

`/portante` sin `condicion_carga` conserva el comportamiento anterior, con aviso si FS < 3, porque hay llamadas reales en
producción que no la envían. Con `condicion_carga`, un FS bajo el mínimo de la tabla es un error.

## Entradas que la norma exige y el motor no supone

- σ'0 y σ'p de cada estrato, del estudio geotécnico. El motor no calcula la historia de esfuerzos.
- Es y ν para el inmediato.
- Cα por estrato, o `null` explícito. Si es `null`, el secundario es nulo y queda declarado, porque H.4.8.3 pide comprobarlo en laboratorio.
- La condición de carga de la Tabla H.4.7-1 para la capacidad excéntrica.

## Lo que NO verifica

- El asentamiento por sismo (H.4.8). Tampoco los efectos estéticos o funcionales del giro (H.4.9.4) ni la condición «siempre y cuando no se afecte» de H.4.9.2.
- El deslizamiento y el volcamiento de la zapata, ni los factores directos de la Tabla H.2.4-1.
- Las cimentaciones profundas (#118) y los macizos rocosos (H.4.8.5).
- El diferencial y el giro se revisan sobre un eje, no en planta.

## Decisiones

- **Inmediato:** semiespacio elástico, zapata flexible, en el centro (Harr; Iw del cuadrado = 1,122).
- **Consolidación a 20 años:** U(Tv a 20 años) por la serie de Terzaghi, con carga instantánea.
- **Secundario:** de tp = t(U = 95 %) a 20 años; si tp ≥ 20 años, es cero.
- **Giro:** rotación de cuerpo rígido, la pendiente de mínimos cuadrados de S(x).
- **Excentricidad:** B' = B − 2eB y L' = L − 2eL. Los factores de forma usan B'/L' y los de profundidad, Df/B real.
- **Inclinación:** el exponente m de Vesić toma la dimensión efectiva paralela a H, aunque B' y L' se intercambien.
- **Núcleo central:** una resultante fuera de él (e > B/6) se advierte y marca borde de dominio.

## Verificación

```powershell
python -m pytest packages/motor-geotecnia/tests -q
```

157 pruebas del paquete y 13 del router. Cubren:
- las constantes transcritas de la norma;
- la corrida excéntrica reescrita a mano;
- ic con φ = 0 e iq, iγ con c = 0, a mano;
- inmediato + primario + secundario sumados a mano, con Tv95 = 1,129;
- el diferencial y el giro a mano, y cada fila de la Tabla H.4.9-1;
- la multicapa de una capa contra U(0,2) = 0,504 de Terzaghi;
- Monte Carlo sin variabilidad igual al determinista, y reproducible con semilla;
- monotonicidad y rechazos de dominio.
