## Qué cambia y por qué

<!-- Una o dos frases. Enlace al issue: Closes #… -->

## Si toca un motor de cálculo (docs/REGLAS_MOTORES_DE_CALCULO.md)

- [ ] Pruebas rojo→verde contra una referencia independiente (analítica, publicada o a mano con fuente)
- [ ] Entradas fuera de dominio responden 422 (no un valor silencioso)
- [ ] Salida con `ResultadoMotor` y `en_borde_dominio` cuando aplica
- [ ] Límite de tasa en el endpoint
- [ ] Revisión adversaria hecha o anotada como pendiente en `docs/registro_motores.json`

## Si toca normativa o datos

- [ ] Verifiqué la vigencia de la norma antes de ingestar (CLAUDE.md)
- [ ] Verifiqué con una consulta de retrieval real, no solo que el insert no falló

## Siempre

- [ ] Pruebas locales pasan
- [ ] Sin secretos ni datos personales en el diff
- [ ] Regeneré los documentos generados que cambian (`scripts/inventario/registro_motores.py`, `matriz_madurez.py`, `licencias.py`)
