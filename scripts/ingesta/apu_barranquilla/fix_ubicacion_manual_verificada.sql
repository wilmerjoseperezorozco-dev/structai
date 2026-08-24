-- Correcciones manuales de ubicación para proveedores nacionales que las
-- pasadas automáticas (SECOP II + RUES, ver enriquecer_ubicacion_proveedores_secop.py
-- y enriquecer_ubicacion_proveedores_rues.py) dejaron sin resolver por su
-- algoritmo de match EXACTO -- cada una verificada a mano contra RUES
-- (datos.gov.co c82u-588k) antes de aplicar, nunca adivinada.
--
-- Lección real para la próxima recarga completa: RUES guarda personas
-- naturales en orden "Apellidos Nombres" (ej. "ARAUJO OÑATE LUISA LEONOR"),
-- no "Nombres Apellidos" como el resto del proyecto -- el algoritmo
-- automático nunca probaba esa variante. También: el nombre comercial
-- entre paréntesis a veces contiene la ciudad literal (ej. "MULTITUBOS
-- PASTO" -> Pasto), señal fuerte que tampoco se explotaba.
--
-- Casos descartados explícitamente por ambigüedad real (NO se adivinó):
-- CLAUDIA PATRICIA MURILLO (4 personas homónimas, todas canceladas),
-- DANIEL TARAZONA (5 personas distintas con ese nombre de pila),
-- LUIS ALVARO GOMEZ LOPEZ (2 registros reales en ciudades distintas,
-- Barranquilla y Cartago -- sin forma de saber cuál es el proveedor real),
-- FF SOLUCIONES SA (5 candidatos sin match claro), QUINTERO & QUINTERO
-- CONSTRUCCIONES (sin candidato real), EL NOGAL MATERIALES DE
-- CONSTRUCCION S.A (forma jurídica distinta -- "Depósito de Maderas..."
-- Limitada, no confiable como la misma empresa), y las 2 Uniones
-- Temporales (ALINCO, FERRECOM -- por diseño no suelen registrarse en
-- RUES como empresa regular, son consorcios de proyecto específico).

update apu_proveedores_nacional set municipio = null, departamento = 'Bogotá, D. C.', ubicacion_verificada_en = current_date
  where nombre = 'COMPAÑÍA DE DISTRIBUCIÓN FERRETERA SAS COMFERRETERA';
update apu_proveedores_nacional set municipio = null, departamento = 'Bogotá, D. C.', ubicacion_verificada_en = current_date
  where nombre = 'SERVICIOS Y SUMINISTROS DIP SAS';
update apu_proveedores_nacional set municipio = 'Ipiales', departamento = 'Nariño', ubicacion_verificada_en = current_date
  where nombre = 'POSTES Y HERRAJES S.A.S.';
update apu_proveedores_nacional set municipio = 'Valledupar', departamento = 'Cesar', ubicacion_verificada_en = current_date
  where nombre = 'INVERSIONES Y VALORES DEL CARIBE- INVALCA SAS';
update apu_proveedores_nacional set municipio = 'Cúcuta', departamento = 'Norte De Santander', ubicacion_verificada_en = current_date
  where nombre = 'ARIS SKAFIDAS VARGAS';
update apu_proveedores_nacional set municipio = null, departamento = 'Antioquia', ubicacion_verificada_en = current_date
  where nombre = 'LUISA LEONOR ARAUJO OÑATE';
update apu_proveedores_nacional set municipio = 'Pasto', departamento = 'Nariño', ubicacion_verificada_en = current_date
  where nombre = 'DIANA STEFANNY DE LA CRUZ NARVAEZ (DISTRIBUCIONES Y FERRETERIA COLOMBIANAR)';
update apu_proveedores_nacional set municipio = 'Pasto', departamento = 'Nariño', ubicacion_verificada_en = current_date
  where nombre = 'JUAN CARLOS FAJARDO ZAMUDIO (DISTRIBUIDORA CONSTRUNAR)';
update apu_proveedores_nacional set municipio = 'Ocaña', departamento = 'Norte De Santander', ubicacion_verificada_en = current_date
  where nombre = 'LUCY MERCEDES QUINTERO CORONEL (VARIEDADES LEIDY)';
update apu_proveedores_nacional set municipio = null, departamento = 'Bogotá, D. C.', ubicacion_verificada_en = current_date
  where nombre = 'MARCELA MESA MARTIN SAS (ACEC CONSULTING GROUP)';
update apu_proveedores_nacional set municipio = 'Pasto', departamento = 'Nariño', ubicacion_verificada_en = current_date
  where nombre = 'MARINA DEL ROSARIO TOBAR TELLO (PROVECOL)';
update apu_proveedores_nacional set municipio = 'Pasto', departamento = 'Nariño', ubicacion_verificada_en = current_date
  where nombre = 'ZULMA PATRICIA GUERRERO TELLO (MULTITUBOS PASTO)';
