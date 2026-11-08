-- Verificación de la Res. 108/2015 (MinTransporte, adopta CCP-2014) contra la ficha SISJUR (aplicada vía MCP 2026-11-08).
update normas_registro set
 nombre_completo = 'Resolución 108 de 2015 (Ministerio de Transporte) — adopta la Norma Colombiana de Diseño de Puentes CCP-2014',
 estado_vigencia = 'vigente',
 notas_vigencia = coalesce(notas_vigencia,'') || E'\n[2026-11-08] Verificada en la ficha SISJUR de la Alcaldía de Bogotá: expedida 2015-01-26; art. 1 adopta CCP-2014 para puentes de la Red Vial Nacional a cargo de INVÍAS; art. 2 deroga la Res. 3600 de 1996. Sin modificaciones listadas. Residual: no se consultó el Diario Oficial; proyecto de 2026 sobre la Sección 13 (barandas) no confirmado como expedido.',
 cadena_modificaciones = 'parcial',
 updated_at = now()
where codigo = 'RES-108-2015';
