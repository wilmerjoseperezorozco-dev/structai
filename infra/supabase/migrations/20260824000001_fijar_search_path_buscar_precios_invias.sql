-- Corrige advisor WARN: search_path mutable permite que un rol con
-- privilegios de creacion de objetos en un schema distinto intercepte
-- referencias no calificadas dentro de la funcion. Fijarlo explicitamente
-- a public elimina el riesgo sin cambiar el comportamiento (la funcion ya
-- solo referencia tablas de public).
alter function public.buscar_precios_invias set search_path = public;
