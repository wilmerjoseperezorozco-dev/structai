# Resultados #292-W: el viento B.6 en el corpus F1 de zona baja

- **Prerregistro:** [`PRERREGISTRO_292W_VIENTO_ZONA_BAJA.md`](PRERREGISTRO_292W_VIENTO_ZONA_BAJA.md), commit `1f2990d`, publicado en #292 antes de correr.
- **Corrida:** `scripts/memorias_sinteticas/viento_292.py` sin cambios: 258 diseños, 0 errores, 27 s.
- **Salida:** `data/memorias_sinteticas/f1_292w/`.

## Decisión: el viento NO gobierna el pórtico de concreto con losa en zona baja; queda opcional

| Id | Métrica | W28C | W36D | Criterio (W36D) | Veredicto |
|---|---|---|---|---|---|
| **H-W1** (primaria) | Edificios con refuerzo cambiado | 0/86, IC95 [0; 4,3 %] | 0/86, IC95 [0; 4,3 %] | IC95 sup. ≤ 10 % | **CUMPLE** |
| **H-W2** (descriptiva) | 1,6W en la base > E = ΣFs/R | 0/86 | 0/86 | predicción > 50 % | **REFUTADA** |
| **C-W** | Sobrecosto | 0 % en todos | 0 % en todos | p90 ≤ 1 % | **CUMPLE** |
| **R-W** | Dejan de cumplir | 0 | 0 | 0 | **CUMPLE** |

**Razón 1,6W / E en la base** (descriptivo):

| Brazo | Mínimo | Mediana | Máximo | qh |
|---|---|---|---|---|
| W28C | 0,03 | 0,07 | 0,21 | 0,39–1,02 kPa (ambos brazos) |
| W36D | 0,05 | 0,14 | 0,40 | |

## Por qué se refutó la H-W2

La predicción salió de una exploración con un edificio que no representa el corpus:

| | Exploración | Corpus de zona baja (edificios bajos) |
|---|---|---|
| Capacidad | DES (R = 7) | DMI (R = 2,5) en los 358 |
| Cubierta | Liviana, 0,3 kPa | Losa, D de 5 a 6,5 kPa |
| Aa | 0,05 | Casi siempre 0,10 |
| E en la base | 26,6 kN | Mediana 1.859 kN |

Con R = 2,5 y losas pesadas, el sismo de diseño es de 2,5 a 30 veces el viento factorado.

## Alcance y limitaciones

- **Población evaluada:** solo los 86 "edificios bajos" de B.6 (h ≤ 18 m y h ≤ menor dimensión). Los otros 272 de zona baja (h > 18 m o esbeltos en planta) no se evaluaron. En edificios más altos el viento crece con Kz y el área expuesta: queda para #242.
- **Cubierta:** es la losa del corpus. **La cubierta liviana no se evaluó.** Ahí la succión de componentes es de unas 7 veces su peso, y los anclajes siguen SIN VALIDAR (#319).
- **Hipótesis del motor:**
  - sin casos torsionales de viento;
  - zonas de borde en ambos extremos;
  - I = 1,00 en el grupo I.
- **Velocidad del viento:** la de la región, sin topografía (Kzt = 1). Un sitio en cresta o escarpe puede multiplicar qh.

## Consecuencia

El viento queda **opcional** en el diseño 3D de pórticos con losa en zona baja, declarado en la memoria. Lo que sí merece atención en #292 es la **cubierta liviana y sus anclajes**, que no dependen del pórtico.
