-- Enriquece los 78 proveedores del catalogo nacional IAD MIPYMES
-- (apu_proveedores_nacional) con ciudad/departamento real, cruzados
-- contra el registro publico oficial SECOP II - Proveedores Registrados
-- (datos.gov.co, resource qmzu-gj57). El catalogo IAD MIPYMES en si NO
-- trae ubicacion (verificado abriendo el Excel fuente: solo nombre de
-- item + precio por proveedor) -- este es un cruce contra una fuente
-- oficial DISTINTA para dar granularidad geografica real, no un dato
-- inventado ni derivado del nombre del proveedor.
--
-- nit nullable: no todos los 78 proveedores necesariamente aparecen en
-- SECOP II (pueden vender via IAD MIPYMES sin estar en el registro
-- completo de proponentes). departamento/municipio quedan NULL cuando no
-- hay match confiable -- nunca se adivina.

alter table apu_proveedores_nacional
  add column if not exists nit text,
  add column if not exists departamento text,
  add column if not exists municipio text,
  add column if not exists ubicacion_verificada_en date;
