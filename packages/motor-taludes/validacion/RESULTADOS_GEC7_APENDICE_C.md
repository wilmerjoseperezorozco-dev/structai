# Validación: estabilidad global contra el Apéndice C de FHWA GEC 7 (#241)

- **Prerregistro:** [#241, comentario 7117785102](https://github.com/wilmerjoseperezorozco-dev/structai/issues/241#issuecomment-7117785102), publicado antes de correr.
- **Código:** commit `7d9e561`, script `validacion/gec7_apendice_c.py`. Después del prerregistro solo se corrigió la carga del módulo (`sys.modules`), que impedía ejecutar; el método no cambió.

## Resultado: NO PASA (0 de 2 casos dentro de ±0,10)

| Caso | FS SNAP-2 (Tabla C.4) | FS motor | ¿Dentro de ±0,10? |
|---|---|---|---|
| Sin sobrecarga (etapa 6) | 1,62 | **1,151** | no |
| Con sobrecarga (etapa 7) | 1,51 | **1,033** | no |

- **Modos que coinciden con la Tabla C.5:** 0 de 5.
- **Con sobrecarga, el círculo crítico no corta ningún clavo.** Sin sobrecarga, deja fuera las cabezas de los clavos 4 y 5.

## Causa

La búsqueda de Bishop de motor-concreto acepta círculos que **salen por el paramento** entre las cabezas de los clavos. En un
muro de suelo cosido, el paramento es continuo y está unido a los clavos, así que esas superficies no son un mecanismo
real. SNAP-2 (Fig. C.3) busca superficies que pasan por el pie. Esta restricción no se declaró en el prerregistro: es un
defecto del modelo, no del dato.

## Diagnóstico post hoc (NO prerregistrado, no cuenta como validación)

Si se fuerzan los círculos a pasar por el pie (0, 0):

| Caso | FS con clavos | FS sin clavos | SNAP-2 |
|---|---|---|---|
| Sin sobrecarga | 1,703 | 1,165 | 1,62 |
| Con sobrecarga | 1,629 | 1,142 | 1,51 |

- Las fuerzas por clavo (0; 0,8; 6,3; 13,6; 24,0 kip) crecen con la profundidad, como en la Tabla C.5 (3,2; 7,2; 12,5;
  19,0; 24,7 kip). Pero aquí el clavo 5 queda gobernado por arrancamiento y no por tensión.
- Aun forzando los círculos por el pie, el caso con sobrecarga quedaría a +0,12, fuera de la tolerancia.
- **Este cálculo se hizo después de ver el resultado, así que no valida nada.**

## Lo que sigue

Según el prerregistro, no se cambia nada para volver a evaluar contra este ejemplo. La versión 2 tendrá:
- superficies obligadas a pasar por el pie o por debajo, con el paramento continuo;
- opcionalmente, la componente normal del clavo en la base de las dovelas.

Debe prerregistrarse y validarse con **casos distintos** de este. El motor no se integra a la API mientras tanto.
