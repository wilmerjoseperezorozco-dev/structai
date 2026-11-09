# Matriz de madurez por subsistema

Generado por `scripts/inventario/matriz_madurez.py`; no editar a mano. No existe una nota única de «madurez»: cada columna sale de una fuente distinta y se lee por separado.

- **TRL**: escala de niveles de madurez tecnológica. Es **autoevaluado**, sin revisión externa; cada valor lleva su evidencia y el límite que impide subir. «?» = sin atestar (no significa que cumpla).
- **Calidad**: se calcula del repositorio: funciones de prueba, presencia en la matriz de CI y, en motores, contrato `ResultadoMotor`, fallo explícito 422 y límite de tasa. **No se publica porcentaje de cobertura porque no se mide hoy.**
- **Operación**: «en producción verificado» exige revisión de Cloud Run y llamada real registradas (ver [REGISTRO_MOTORES.md](REGISTRO_MOTORES.md)).
- **Licencias**: la peor clasificación entre las dependencias directas del subsistema ([LICENCIAS_DEPENDENCIAS.md](LICENCIAS_DEPENDENCIAS.md)).

| Subsistema | TRL (autoevaluado) | Calidad de software | Operación | Licencias (dependencias directas) |
|---|---|---|---|---|
| Corpus normativo y consulta con citas (NSR-10, NTC, SG-SST, RAS) | TRL 6 | 31 pruebas · CI sí · job test-api de integración (RAG, límites de tasa, salud) | en producción | permisiva |
| Motor de redes hidráulicas (permanente, periodo extendido, golpe de ariete) | TRL 4 | 105 pruebas · CI sí · contrato/422/límite sí | no desplegado | sin dependencias directas declaradas |
| Motor de geotecnia (asentamiento, capacidad portante) | TRL 4 | 88 pruebas · CI sí · contrato/422/límite sí | no desplegado | sin dependencias directas declaradas |
| Motor estructural / BIM por visión (InfraCortex, YOLO) | ? | 18 pruebas · CI sí | desactivado por defecto en producción | copyleft fuerte (red): revisar (ultralytics) |
| Motor `licuacion` | ? | 53 pruebas · CI sí · contrato/422/límite sí | ? | sin dependencias directas declaradas |
| Motor `concreto` | ? | 283 pruebas · CI sí · contrato/422/límite sí | ? | permisiva |
| Motor `analisis` | ? | 18 pruebas · CI sí · contrato/422/límite sí | ? | sin dependencias directas declaradas |
| Motor `orquestador_api` | ? | 75 pruebas · CI sí · contrato/422/límite sí | ? | sin dependencias directas declaradas |

## Evidencia y límites de los TRL atestados

**Corpus normativo y consulta con citas (NSR-10, NTC, SG-SST, RAS).** Piloto en producción (structai.online, Cloud Run) con métricas medidas y publicadas: RAGAS n = 278, 88,2 % de citas con soporte en el contexto, abstención cuando no hay base; auditoría de cobertura por título con línea base en CI. **Límite:** No se declara TRL 7: falta uso por terceros medido y la revisión técnica independiente de la extracción normativa; los Títulos A y B tienen cierre verbatim parcial (45,6 % y 41,9 %).

**Motor de redes hidráulicas (permanente, periodo extendido, golpe de ariete).** Validado en laboratorio contra Hardy-Cross, soluciones cerradas, scipy y casos de EPANET (Net1, todinitest); golpe de ariete contra Joukowsky; dos revisiones adversarias corregidas. **Límite:** Es validación frente a otro solver y casos analíticos, no contra datos medidos; sin desplegar en producción.

**Motor de geotecnia (asentamiento, capacidad portante).** REGLAS_MOTORES_DE_CALCULO.md declara que cumple las condiciones 1–3 en su primer corte (atestación heredada, no re-verificada aquí). **Límite:** Sin desplegar en producción; imagen de Cloud Run anterior a este motor.

## Qué no se publica, y por qué

- **Un único badge de madurez o de TRL**: comprime evidencias de naturaleza distinta y no se puede verificar en vivo.
- **Porcentaje de cobertura de pruebas**: no hay medición; un número sin medir sería una afirmación sin sustento.
- **«Seguridad» o «calidad» como sello**: lo comprobable es el estado de alertas de dependencias, la auditoría de CI y las revisiones adversarias documentadas, no un sello.
- **TRL 7 o superior**: exige operación por terceros medida y revisión técnica independiente; hoy no existen.
