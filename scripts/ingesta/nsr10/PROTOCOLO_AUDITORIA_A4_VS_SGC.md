# Protocolo: auditoría del Apéndice A-4 de la NSR-10 contra la capa del SGC (fijado el 2026-11-08, antes de la comparación por código)

**Pregunta.** ¿Los valores Aa, Av, Ae, Ad y la zona de amenaza del Apéndice A-4 (PDF 2010, ya extraído en `apendice_a4_extraido.json`) coinciden con la capa pública `Zonas_amenaza_Sismica_NR10/Municipios_Amenaza_NR10` del SGC? Contexto: una comparación previa por nombre encontró 30 diferencias sin explicar.

**Datos.** (1) A-4 extraído: 1.118 filas con código DANE. (2) Capa del SGC, consultada en vivo sin geometría (`returnGeometry=false`), todos los registros.

**Método (fijo).**
1. Emparejar por **código DANE de 5 dígitos** (más robusto que el nombre). Si la capa trae varios registros por código (centros poblados), tratarlos aparte y reportarlo.
2. Por cada par comparar Aa, Av, Ae, Ad (igualdad exacta a 2 decimales) y la zona (sin tildes ni mayúsculas).
3. Clasificar cada diferencia como: (a) solo de zona, (b) de uno o más valores, (c) código en un lado y no en el otro, (d) municipio con nombre distinto pero mismo código.
4. Para cada diferencia, cotejar con el PDF original (página A-153 a A-174) antes de decir cuál de las dos fuentes es la que se apartó. Una diferencia no prueba por sí sola cuál lado tiene el error.

**Qué NO se concluye.** No se atribuye ninguna diferencia a un decreto modificatorio sin encontrar y leer el texto del decreto. No se «corrige» A-4 en la base: se reporta. La capa del SGC es la fuente que sirve hoy el chat para amenaza sísmica; si discrepa del reglamento, el aviso al usuario debe decirlo.

**Resultado esperado de publicar:** tabla de diferencias, conteo por clase y lista de las que quedan sin explicar, incluso si son cero o muchas.
