# Prerregistro #322, parte 2: casos torsionales de edificios bajos (Fig. B.6.5-7, nota 5)

Fijado el 2026-11-25, **antes** de correr la población. Solo se corrió un piloto de 2 edificios para revisar que el script funcione.

- **Código:** `_casos_viento` y `_tramos_torsion_bajos` en `packages/orquestador/src/diseno_edificio_3d.py`.
- **Script:** `scripts/memorias_sinteticas/viento_322.py --bajos`.

## Qué cambia (leído de la NSR-10, Fig. B.6.5-7, nota 5)

- En los casos torsionales, las zonas 1T a 4T llevan el **25 %** de la presión total de diseño. Esas zonas ocupan la mitad del edificio lejana a la esquina de referencia (más allá de B/2).
- El borde E (2a) va solo junto a la esquina de referencia. Se aplican a cada esquina de referencia: 4 direcciones × 2 esquinas × ±GCpi = **16 casos más**.
- **Excepción:** un solo nivel con h ≤ 9 m. Las otras dos excepciones (construcción liviana y diafragma flexible) no aplican a pórticos de concreto con losa.

Hipótesis declaradas:
- el 25 % se aplica a la presión neta, GCpf − GCpi, también en la cubierta;
- el torsor es el de la resultante respecto al centro de la planta.

Los casos son **obligatorios** y quedan activos pase lo que pase aquí. Lo que se mide es su efecto.

## Población y brazos

- **Población:** los 86 edificios bajos de zona baja de #292-W, con losa de concreto.
- **Brazos:** W28C y W36D, cada uno con y sin los casos torsionales (c1 / c14).

## Anclaje físico

- En el caso torsional, el cortante total **baja**: la mitad lejana va al 25 % y el borde E queda solo en un extremo.
- El marco de borde cercano a la esquina de referencia recibe algo más que en el patrón básico, por el torsor. El aumento es del orden del 10–20 % de una fuerza de viento que en #292-W no gobernó ningún elemento: 0 de 86 cambiaron refuerzo, con ρ = 1,6W/E muy por debajo de 1.

## Predicciones

| Id | Métrica | Predicción |
|---|---|---|
| **T0b** (control) | c1 reproduce la firma de #292-W | 86/86 en W28C y en W36D. Si no, se diagnostica antes de leer lo demás |
| **T1b** (primaria) | W36D: edificios cuyo refuerzo cambia de c1 a c14 | **0/86**. Un solo cambio la refuta |
| T2b | Edificios que dejan de cumplir | 0 en ambos brazos |
| T4b | W28C: edificios cuyo refuerzo cambia | 0/86 |

Los criterios no cambian después de ver los resultados.
