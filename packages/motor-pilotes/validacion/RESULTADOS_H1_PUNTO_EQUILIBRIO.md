# Resultados H1 (#273): diseño conservador de pilotes frente a prueba de carga (2026-11-18)

- **Prerregistro:** `PRERREGISTRO_H1_PUNTO_EQUILIBRIO.md`, publicado en [#273](https://github.com/wilmerjoseperezorozco-dev/structai/issues/273#issuecomment-6995150029) antes de calcular ahorros.
- **Código:** `h1_punto_equilibrio.py`, sin cambios después del prerregistro. **Salida:** `h1_resultados.json`.
- **Escenario principal:** 30 pilotes, 1 prueba estática, precios INVIAS 2026-1 (mediana).

## Veredicto: depende del suelo

| Perfil | Ahorro esperado en el costo de los pilotes | IC95 % (bootstrap por sitio) | Afirmación "18-30 %" |
|---|---|---|---|
| **Arcilla blanda** | **34 %** | [24 %; 42 %] | **CONFIRMADO** (incluso por encima) |
| Mixto (8 m de arcilla sobre arena) | 12 % | [3 %; 20 %] | NO CONCLUYENTE |
| **Arena** | **−0,5 %** | [−16 %; +13 %] | **REFUTADO** |

## De dónde sale el ahorro

| Perfil | Solo bajar el FS al 80 % (λ = 1) | Con lo que revela la prueba (λ empírico) | P(la prueba obliga a alargar) | P(λ < 0,8) |
|---|---|---|---|---|
| Arcilla blanda | 12-18 % | 30-36 % | 11 % | 11 % |
| Mixto | 5-16 % | 5-18 % | 26 % | 28 % |
| Arena | 8-16 % | −5 a +4 % | 38-41 % | **42 %** |

- **En arcilla**, la mitad del ahorro viene de la reducción del FS que permite H.4.7.3. La otra mitad viene de que **el método de la NSR-10 (α·Su + 9·Su) subestima la capacidad**: en la base CYCU, λ ≈ 1,45. La prueba revela esa reserva. Así que el 18-30 % no es "el constructor infla el FS": es el sesgo del método normativo.
- **En arena**, en promedio el método acierta (λ ≈ 1), pero con mucha dispersión. La prueba ahorra en unos sitios y obliga a alargar en otros (cerca del 40 %).
  - **El hallazgo importante aquí es de seguridad, no de costo.** En el 42 % de los sitios, la capacidad real es menor que el 80 % de la predicha. Es decir, el diseño sin prueba queda con un margen real por debajo del mínimo que la norma acepta incluso con prueba.

## Punto de equilibrio: desde cuántos pilotes se paga una prueba

| Perfil | Solo FS (λ = 1) | Con λ empírico |
|---|---|---|
| Arcilla blanda | 1-10 pilotes | 1-5 pilotes |
| Mixto | 1-18 pilotes | 1-18 pilotes |
| Arena | 5-11 pilotes | 13-86 pilotes (o nunca en promedio) |

**Sensibilidad** (ahorro esperado):

| Perfil | Precio de la prueba ×3 | Precio de la prueba ×10 | 100 pilotes, prueba ×10 | 10 pilotes, prueba ×1 |
|---|---|---|---|---|
| Arcilla blanda | 29 % | 11 % | 29 % | 29 % |
| Mixto | 6 % | −16 % | 6 % | 6 % |
| Arena | −10 % | −43 % | −10 % | −10 % |

- El precio de la prueba del INVIAS (unos 8,9 M$, valor nacional único) parece bajo. Si el real es diez veces mayor, en arcilla la prueba se sigue pagando con 30 pilotes y en arena no.
- El precio del pilote (p10 frente a p90) casi no cambia nada.

## Lectura (fijada de antemano)

- **Para StructAI:** antes de licitar pilotes en arcilla blanda, recomendar una prueba de carga estática temprana. Con unas pocas decenas de pilotes, se paga varias veces.
- En **arena** la recomendación es la misma, pero **por seguridad**: el diseño solo con SPT queda corto en cuatro de cada diez sitios.
- **Qué no mide:** las contingencias que mete el constructor en la licitación por falta de estudio. SECOP no desagrega el ítem. Esto es el **componente normativo** del sobrecosto.

## Limitaciones

- La base CYCU es de Taiwán.
- Un λ por sitio ignora la variabilidad dentro del sitio.
- Los perfiles son idealizados.
- El precio de la prueba no escala con la carga.
- La tabla H.4.7-2 (número de pruebas exigidas) no está verificada.
- El ahorro se calcula sobre el costo de los pilotes, no sobre el de toda la cimentación.
- El caso arcilla Ø1,0 m con 3.000 kN no es factible en 40 m y queda excluido.
