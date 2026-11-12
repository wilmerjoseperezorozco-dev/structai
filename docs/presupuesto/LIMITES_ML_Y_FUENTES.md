# Límites: estadística, machine learning y datos sintéticos en el presupuesto por etapas

Fecha: 2026-11-12. Resultados: [`CLASIFICADOR_ETAPAS.md`](CLASIFICADOR_ETAPAS.md), [`RECETAS_DISPERSION.md`](RECETAS_DISPERSION.md),
[`APU_COLEGAS_RESUMEN.md`](APU_COLEGAS_RESUMEN.md). Datos de los colegas: permiso de uso para StructAI confirmado por
Wilmer el 2026-11-12. Están en `scripts/presupuesto/_privado/` (gitignored); en el repo solo hay agregados.

## 1. Qué tenemos y qué no

| Recurso | Cantidad | Sirve para | No sirve para |
|---|---|---|---|
| APU de colegas (ejercicio académico, una vivienda campestre, 21 capítulos) | 902 únicos (119 copias exactas fuera), 717 descripciones, 45 archivos (algunos con varios APU por hoja) | **etiquetas humanas de capítulo**; **recetas**: cantidad de material y horas de cuadrilla por unidad; estructura de costos por capítulo | precios actuales (son de hace ~5 a 7 años); dispersión **de obra** de rendimientos (son estimaciones de estudiantes; varios usaron la misma tabla); otros tipos de obra |
| Precios de la base (`apu_precios_referencia`) | 2.812 actividades de obra + 1.754 insumos IAD | precios reales (contratos y catálogos) | etiquetas: no tienen capítulo; 32 % de las no clasificadas son fragmentos de sub-ítem sin su actividad padre |
| Proveedores | 114.616 precios de 102 proveedores | **volver a poner precio a las recetas** con insumos actuales | — |

## 2. Lo que sí se puede hacer (y se hizo)

1. **Clasificador por etapa y capítulo** (TF-IDF de caracteres + regresión logística con rechazo):
   - en actividades **nunca vistas** de los colegas (E1b, validación agrupada por descripción, 877 APU de oro): **92,2 % de acierto en etapa** y 88,5 % en capítulo (91,2 % / 94,0 % si se agrupa solo por archivo);
   - en la base es otro dominio y **no está validado**: hay errores claros en la muestra. Falta una muestra etiquetada por una persona (`_privado/muestra_para_etiquetar.csv`, 186 filas: la mitad las más dudosas y la mitad aleatoria, para medir sin sesgo).
   - MiniLM, que ganó en el enrutador de #169, aquí pierde (68 %): el vocabulario de presupuesto es muy específico y lo capturan mejor los n-gramas de caracteres.
   - Las etiquetas automáticas por palabras clave ("plata") **no enseñan** lo que etiqueta un humano (57 %): no se usan para entrenar.
2. **Recetas que no envejecen.** Lo que envejece en un APU de hace 7 años es el **precio**. La **receta** (cantidad de material por unidad, horas de cuadrilla por unidad, desperdicio) depende del método constructivo y cambia poco. Plan:
   - receta de los colegas;
   - más los precios actuales de insumos (proveedores, IAD);
   - más el salario de 2026 con el factor prestacional;
   - da como resultado un APU de 2026 trazable.
   Lo que no se pueda volver a poner precio se indexa **por componente**: mano de obra con el salario mínimo; materiales y equipo con el ICOCED del capítulo (#113), usando la estructura de costos por capítulo de `RECETAS_DISPERSION.md`.
3. **Dispersión entre colegas** (48 actividades con 3 o más versiones): mediana del CV robusto de rendimientos 37 % y de costo directo 23 %; `sd_log` del rendimiento 0,64. Sirve como **cota provisional** para el Monte Carlo, no como dispersión de obra: una parte de los archivos usa la misma tabla de rendimientos (CV 0 %), otra parte estimó por su cuenta.
4. **Control de calidad estadístico:** atípicos por MAD entre versiones y frente a la base. Esto detecta errores como el pañete con materiales 40 veces más caros: cantidad por m³ usada como por m².

## 3. Datos sintéticos: dónde sí y dónde no

| Uso | ¿Sirve? | Por qué |
|---|---|---|
| **Aumentar texto para el clasificador**: variantes de redacción ("Suministro e instalación de...", abreviaturas, unidades) | **Sí, con cuidado** | mejora la robustez al estilo de cada fuente. Se usa **solo en entrenamiento**; las métricas siempre se miden con etiquetas humanas reales |
| **Monte Carlo de precios y rendimientos** (lo que ya hace `motor-apu`) | **Sí** | es simulación de incertidumbre sobre una receta real, no un dato inventado. La dispersión de los colegas (CV 37 %) es una cota provisional; la definitiva debe venir de mediciones de obra |
| **Cantidades paramétricas** (m² de pañete a partir de la geometría) | **Sí** | es cálculo determinista con reglas explícitas (#199), no síntesis |
| **Inventar APU o precios** para capítulos sin datos (eléctricas regionales, puentes) | **No** | un precio sintético no tiene fuente: StructAI quedaría citando un número que nadie cotizó. Viola la regla de no inventar cifras (detector de alucinación numérica). Un hueco se declara como hueco |
| **Entrenar y evaluar con datos sintéticos** | **No** | se mediría la calidad del generador, no la del modelo (circularidad) |
| **"Motores funcionales" con datos sintéticos** | Solo para **probar el código** | un motor puede probarse con casos sintéticos (unidades, monotonicidad, #132), pero sus valores de diseño deben salir de norma y datos reales |

## 4. Fuentes públicas para otros proyectos (edificios, vías, redes, puentes)

| Fuente | Tipo de proyecto | Qué trae | Estado |
|---|---|---|---|
| **EPC, Empresas Públicas de Cundinamarca**: listas de precios de referencia 2026 por municipio (PDF) | redes de acueducto y alcantarillado, obras civiles | precio unitario por actividad y municipio, con capítulos (preliminares, demoliciones, impacto urbano, redes...). Ej.: el PDF de Sibaté y Soacha tiene 22 páginas. Sin APU desglosado | verificado; extraíble con PyMuPDF |
| **Proyectos del Sistema General de Regalías (OCAD)**: anexos de proyectos aprobados (p. ej. Gobernación de Antioquia) | vías, puentes, acueductos, colegios en todo el país | presupuesto con Formulario 1 (ítem, especificación, unidad, cantidad, valor) y a veces APU | por explorar: muchos PDF, cobertura nacional |
| **SECOP II**: datos abiertos (`jbjy-vk9h`, CC BY-SA 4.0) + documentos de cada proceso | todos | el dataset tiene el contrato (valor, objeto, entidad), **no los ítems**. Los ítems y APU están en los documentos adjuntos de cada proceso (Formulario 1 en Excel) | se necesita un recolector por proceso; respetar los términos de uso |
| **Visor de precios del IDU** | espacio público y vías urbanas (Bogotá) | APU e insumos, actualizados al menos dos veces al año | verificar si se puede descargar |
| **Trabajos de grado** (UIS, UdeA, UAN *Torres del Norte*, Javeriana, U. Distrital) | edificios multifamiliares, VIS | presupuestos con APU y cantidades en anexos PDF | uso con cita; derechos de los autores: solo extraer cifras con referencia |
| **ANI**: anexos de licitaciones | vías concesionadas, puentes peatonales | APU publicados como documento adicional en algunos procesos | por explorar |
| **DANE ICOCED** | edificaciones | variación mensual por capítulo, sistema y ciudad (no son precios) | para indexar (#113) |

Las listas de gobernaciones (Antioquia, Valle, Cundinamarca, Atlántico) no aparecieron publicadas en línea: pedirlas por **derecho de petición**. Las descargas se piden al usuario antes de hacerlas.

## 5. Siguientes pasos

1. **Wilmer etiqueta la muestra** (`_privado/muestra_para_etiquetar.csv`, columna `capitulo_correcto`), con la misma regla de #171: yo no etiqueto. Con esa muestra se mide el clasificador en la base y se reentrena con oro de los dos dominios.
2. **Re-preciar recetas:** emparejar cada insumo de las recetas con proveedores e IAD (por similitud de texto y unidad), recalcular a 2026 y comparar con la base.
3. **Ingerir EPC** como primera fuente fuera del Atlántico (redes), en dry-run.
4. **Explorar regalías y SECOP II** con un piloto de 10 proyectos por tipo (edificio, vía, red, puente), antes de construir un recolector.
