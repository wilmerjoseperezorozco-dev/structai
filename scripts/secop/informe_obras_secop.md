# Contratos de obra de SECOP II: descripcion de la realidad (borrador reproducible)

Generado: 2026-11-06. Solo columnas no personales. Fuente: datos.gov.co (SECOP II), sin identidad de proveedores.

## 1. Inventario y calidad
- Contratos de obra: **50154**; ids repetidos: **0**.
- Valor del contrato faltante: 0; en cero: 141; **> 1e+13 COP (probable error de captura): 1**; negativos: 0.
- Fecha de firma nula: 1152; fuera de 2012-2027: 0; fin anterior al inicio: **14**.
- Pagado mayor que el valor del contrato (pagado > 1,5 x valor, ambos > 0): 1.

### Valor del contrato (COP, sin atipicos absurdos ni ceros)
n = 50012; mediana **217 M** [p5 17.2 M, p25 60 M, p75 883 M, p95 9,126 M]; asimetria muy fuerte (media 2,922 M).

## 2. Estado y años
| estado | contratos | % |
|---|---|---|
| Modificado | 16306 | 32.5 |
| terminado | 14283 | 28.5 |
| En ejecución | 10980 | 21.9 |
| Cerrado | 3871 | 7.7 |
| Aprobado | 2649 | 5.3 |
| Suspendido | 861 | 1.7 |
| enviado Proveedor | 698 | 1.4 |
| En aprobación | 454 | 0.9 |
| cedido | 52 | 0.1 |

Contratos por año de firma: 2016: 7, 2017: 236, 2018: 1281, 2019: 2292, 2020: 2763, 2021: 5401, 2022: 5960, 2023: 7965, 2024: 6502, 2025: 9738, 2026: 6857

## 3. Señales de modificacion (tasas base con intervalo de Wilson)
- Con días adicionados > 0: **26.9 % [26.5, 27.3] (n=50154)**
- Con al menos una adición en el valor: **9.7 % [9.4, 9.9] (n=50154)**
- Con suspensión: 19.3 % [18.9, 19.6] (n=50154); con reactivación: 20.5 % [20.2, 20.9] (n=50154)
- En estado 'Modificado': 32.5 % [32.1, 32.9] (n=50154)
- Entre los que tienen días adicionados (n=13481): mediana 59 días, p90 221, max 3688.

Advertencia: la tabla de adiciones **no trae el monto**; 'adición en el valor' es un indicador, no una medida de sobrecosto. Una adición puede responder a un cambio de alcance legitimo.

## 4. Anticipos y amortizacion
- Contratos con pago adelantado > 0: 2.3 % [2.2, 2.4] (n=50154).
- Entre los terminados o cerrados con anticipo (n=357): amortizado < 99 % del anticipo: **67.5 % [62.5, 72.2] (n=357)**; amortizado = 0: 55.2 % [50.0, 60.3] (n=357).
Advertencia: 'amortizado = 0' puede ser falta de reporte y no falta de amortizacion; el detector necesita validar contra el avance de ejecucion.

## 5. Avance de ejecucion (esperado vs real)
- Contratos con al menos un hito vencido con avance esperado y real: 3241 de 50154.
- Último hito vencido con avance real < esperado: **22.7 % [21.3, 24.2] (n=3235)**; con real < 80 % del esperado: 19.9 % [18.5, 21.3] (n=3235).
- Registros con porcentaje fuera de 0-100 (inconsistente): 0.

## 6. Sanciones (SECOP II)
- Sanciones registradas en contratos de obra: **60** (de 588 en todo SECOP II).
- Por estado: A la espera de aprobación: 44, Publicado por el administrador de la plataforma: 14, Rechazado por el administrador de la plataforma: 2.
- Solo las publicadas serian etiqueta utilizable: **14** (0.03 % [0.02, 0.05] (n=50154) de los contratos de obra). Es una etiqueta demasiado escasa para entrenar un clasificador de sanciones.

## 7. Por departamento (contratos con dias adicionados)
| departamento | contratos | con dias adicionados |
|---|---|---|
| Distrito Capital de Bogotá | 13797 | 26.4 % [25.7, 27.2] (n=13797) |
| Antioquia | 5833 | 23.0 % [21.9, 24.1] (n=5833) |
| Cundinamarca | 2857 | 35.1 % [33.3, 36.8] (n=2857) |
| Valle del Cauca | 2687 | 27.1 % [25.4, 28.8] (n=2687) |
| Boyacá | 2391 | 22.9 % [21.3, 24.6] (n=2391) |
| Caldas | 2117 | 31.7 % [29.7, 33.7] (n=2117) |
| Santander | 1921 | 31.7 % [29.6, 33.8] (n=1921) |
| No Definido | 1415 | 16.6 % [14.8, 18.6] (n=1415) |
| Tolima | 1386 | 29.7 % [27.3, 32.1] (n=1386) |
| Bolívar | 1375 | 30.8 % [28.5, 33.3] (n=1375) |

Limites: datos autorreportados por las entidades; errores de captura conocidos; los contratos 'En ejecución' aun no tienen resultado final.