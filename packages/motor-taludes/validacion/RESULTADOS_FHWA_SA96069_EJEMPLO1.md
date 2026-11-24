# Validación de la v3 contra FHWA-SA-96-069, Ejemplo 1 (#241)

- **Prerregistro:** [#241, comentario 7130671025](https://github.com/wilmerjoseperezorozco-dev/structai/issues/241#issuecomment-7130671025), publicado antes de correr.
- **Código:** `d9309d3` y `23163ad`, script `validacion/fhwa_sa96069_ejemplo1.py`. Se corrió sin cambios.

## Resultado: NO PASA (caso final dentro; 3 de 5 etapas dentro, se exigían 4)

| Caso | FS libro (círculos) | FS v3 (gobierna) | Desvío | ¿Dentro? | FS círculo | FS cuña |
|---|---|---|---|---|---|---|
| Final, 6 filas | 1,35 | 1,371 (cuña) | +1,5 % | sí | 1,391 | 1,371 |
| Etapa, 1 fila | 2,38 | 1,768 (cuña) | −25,7 % | **no** | 2,308 | 1,768 |
| Etapa, 2 filas | 2,20 | 1,916 (cuña) | −12,9 % | **no** | 2,038 | 1,916 |
| Etapa, 3 filas | 1,85 | 1,797 (círculo) | −2,9 % | sí | 1,797 | 1,802 |
| Etapa, 4 filas | 1,53 | 1,533 (cuña) | +0,2 % | sí | 1,581 | 1,533 |
| Etapa, 5 filas | 1,25 | 1,276 (cuña) | +2,1 % | sí | 1,360 | 1,276 |
| Control sin clavos (informativo) | 1,16 | 1,254 (cuña) | +8,1 % | — | 1,705 | 1,254 |
| Cuña a mano del libro, β = 0 (informativo) | 1,39 | 1,345 | −3,3 % | — | | |

**Las dos fallas quedan del lado conservador:** el motor da un FS menor que el libro.

**Ya no aparece el sesgo de la v2:** en el caso final y en las etapas 3 a 5, la v3 queda entre −3 % y +2 % del libro.

**Las ecuaciones de las cuñas se comprueban de forma independiente:** con la superficie y la interfaz del libro, el motor da 1,345 frente a 1,39.

## Diagnóstico post hoc (NO prerregistrado, no cuenta como validación)

1. **Las cuñas que gobiernan en las etapas 1 y 2 son degeneradas.** La cuña superior tiene un ancho casi nulo (xb ≈ xe ≈ 1,8–1,9 m) y su base es prácticamente vertical. Con la interfaz movilizada, ese mecanismo es un artefacto numérico de la búsqueda, no un mecanismo físico.
2. **Solo con círculos, las cinco etapas y el caso final quedarían dentro de ±10 %:** entre −7,4 % y +8,8 %. No cuenta, porque el criterio se fijó sobre el FS que gobierna.
3. **El control sin clavos con círculos (1,705) se calculó con `paramento_continuo=True`.** Esa condición no aplica a un corte sin paramento, así que ese valor no es comparable.

## Qué sigue (v4, con datos distintos)

- Restringir la cinemática de las cuñas, con criterios fijados antes de ver datos nuevos:
  - inclinación máxima de la base superior;
  - ancho mínimo de cada cuña, o un ángulo mínimo entre la base superior y la interfaz.
- Paramento continuo solo cuando hay paramento.
- Validar con otro caso. Candidato: el Ejemplo 2 del mismo manual (estribo de puente). Habría que preregistrarlo antes de abrir sus resultados.
- Sin integración a la API hasta que pase.
