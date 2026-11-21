# Anillos 4 y 5 de clientes potenciales — agregados (#216)

Generado por `anillos_4_5.py` el 2026-11-16. Solo agregados; las listas nominales están en `_privado/`. Sin teléfonos, correos, direcciones, representantes ni personas naturales.

## Anillo 4 — empresas de servicios públicos

Fuente: RUPS (Superservicios, `4qkq-csdn`, última actualización 2021: puede estar desactualizado). Personas jurídicas: **5,820** (48 NIT de persona natural excluidos). Activas u operando: 4,464.

- Contratan obra, interventoría o consultoría en SECOP II como entidad: **292** (5.0%); desde 2024: 254.

| Servicio | Prestadores | Contratan en SECOP II |
|---|---|---|
| Acueducto | 2,943 | 222 |
| Aseo | 2,173 | 229 |
| Alcantarillado | 1,248 | 224 |
| Inscripcion Oficio Delegada Aaa | 1,159 | 27 |
| Energia Electrica | 301 | 6 |
| Gas Natural | 151 | 1 |
| Gas Licuado Del Petroleo | 145 | 1 |
| Inscripcion Oficio Delegada Energia | 12 | 2 |
| Inscripcion Oficio | 3 | 0 |

## Anillo 5 — aseguradoras, laboratorios y curadurías

**Aseguradoras.** Superfinanciera vigila 456 entidades; de ellas 25 son compañías de seguros generales (las que expiden pólizas de cumplimiento) y 38 corredores de seguros (colocan esas pólizas). Seguros de vida, bancos y fondos se excluyen.

La tabla por aseguradora queda en `_privado/aseguradoras_garantias.csv`: el nombre en SECOP es texto libre y la agrupación por palabra clave puede atribuir mal algunas pólizas, así que no se publica por nombre.

**Pólizas en SECOP II Garantías** (`gjp9-cutm`): 48,949 pólizas; 6,736 corresponden a contratos de obra, interventoría o consultoría ya descargados (13.8%). La aseguradora es texto libre en SECOP; se agrupó por nombre distintivo en 19 grupos (concentración: el primer grupo emite el 55% de las pólizas).

**Laboratorios ambientales acreditados (IDEAM, `2waz-acaa`):** 207 personas jurídicas; 54 con matriz de suelo. Los laboratorios de materiales y geotecnia (concreto, acero, suelos) los acredita ONAC, cuyo directorio no está en datos.gov.co: queda pendiente.

**Curadurías urbanas:** 110 combinaciones curaduría-municipio en 53 municipios. La fuente (SNR, `psyr-i7bp`) es CC BY-ND 4.0: se usa solo internamente y no se publican derivados.

## Limitaciones

- El puntaje es una hipótesis inicial sin validar; se calibra con la muestra ciega que etiqueta Wilmer.
- RUPS no se actualiza en datos.gov.co desde 2021.
- Garantías cubre una fracción de los contratos (no todos los procesos publican sus pólizas).
