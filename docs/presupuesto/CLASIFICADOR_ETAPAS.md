# Clasificador de actividades por etapa y capítulo (#196)

Generado por `scripts/presupuesto/clasificador_etapas.py`. Sin LLM; Supabase solo lectura.

- **Oro** (etiqueta humana): 877 APU de los colegas, 45 archivos, 20 capítulos, una sola obra (vivienda campestre).
- **Plata** (etiqueta automática): 1472 actividades de la base donde las palabras clave dan un solo capítulo.
- **Sin etiqueta**: 1340 actividades de la base (sin coincidencia o ambiguas).

Umbral de rechazo τ: el menor que da precisión de capítulo ≥ 90% en las aceptadas (validación fuera de pliegue).

| Modelo | Experimento | n | Exactitud capítulo | Exactitud ETAPA | Macro-F1 capítulo | τ | Cobertura | Precisión capítulo (aceptadas) | Precisión etapa (aceptadas) |
|---|---|---|---|---|---|---|---|---|---|
| Palabras clave (línea base) | — | 670 | 76.0% | 85.7% | 0.56 | — | 76.4% | — | — |
| TF-IDF caracteres + LR | E1 oro→oro (por archivo) | 877 | 91.2% | 94.0% | 0.80 | 0.0 | 100.0% | 91.2% | 94.0% |
| TF-IDF caracteres + LR | E1b oro→oro (actividad no vista) | 877 | 88.5% | 92.2% | 0.72 | 0.175 | 97.6% | 90.3% | 93.2% |
| TF-IDF caracteres + LR | E2 plata→oro | 877 | 56.9% | 73.3% | 0.37 | 0.625 | 27.4% | 91.2% | 94.6% |
| TF-IDF caracteres + LR | E3 plata+oro→oro (por archivo) | 877 | 91.2% | 93.6% | 0.71 | 0.0 | 100.0% | 91.2% | 93.6% |
| MiniLM + LR | E1 oro→oro (por archivo) | 877 | 67.2% | 79.1% | 0.58 | 0.55 | 38.2% | 90.7% | 95.8% |
| MiniLM + LR | E1b oro→oro (actividad no vista) | 877 | 67.7% | 78.1% | 0.54 | 0.6 | 30.9% | 90.0% | 94.8% |
| MiniLM + LR | E2 plata→oro | 877 | 39.6% | 60.0% | 0.21 | 0.95 | 0.3% | 100.0% | 100.0% |
| MiniLM + LR | E3 plata+oro→oro (por archivo) | 877 | 67.8% | 78.0% | 0.44 | 0.625 | 36.8% | 90.1% | 94.4% |

**Aplicado a las 1340 actividades sin etiqueta** (TF-IDF caracteres + LR entrenado con el oro, elegido por E1b; τ = 0.175): 846 aceptadas (63%); el resto queda para etiquetar.

Aceptadas por capítulo: 1.1 85, 1.2 21, 1.3 90, 1.4 3, 1.5 2, 1.6 78, 1.7 21, 2.1 135, 2.3 9, 2.4 85, 2.6 40, 3.1 10, 3.2 93, 3.3 114, 3.4 2, 3.5 18, 3.6 34, 4.1 6

**Advertencia (revisión manual de una muestra, 2026-11-12):** el umbral τ se calibró con los APU de los colegas (una sola obra de vivienda) y **no se transfiere a la base**, que es otro dominio (contratos de redes, vías y catálogos). En la muestra aparecen errores claros: accesorios sanitarios y diámetros ('codo reventilado', 'D=160mm') propuestos como eléctricas; adoquín como pisos en vez de urbanismo. Además el oro no tiene ejemplos de 0.x, 2.2, 2.5 ni 4.3, que el modelo no puede predecir. Las 'aceptadas' de la base NO están validadas: hace falta una muestra etiquetada por una persona (`_privado/muestra_para_etiquetar.csv`) antes de usar el clasificador fuera del dominio de vivienda.

Hallazgo de datos para #200: hay filas que son sub-ítems sin su actividad padre ('D=110mm.', 'En zona dura', 'De 0,15 m x 0,20 m'): la jerarquía del contrato se aplanó al cargarlos.

Las propuestas (ordenadas de más dudosa a más segura, para aprendizaje activo) están en `scripts/presupuesto/_privado/propuestas_clasificacion.csv`, columna `capitulo_correcto` para etiquetar.
**Nada se escribe en `apu_precios_referencia`**: la columna de capítulo en producción se decide aparte.
