# motor-acero-frio (#81)

Perfiles de acero formado en frío según NSR-10 F.4. Cubre la sección C (con o sin pestaña a 90°) en todos sus estados límite de miembro, salvo los de conexiones.

| Función (`src/contrato_api.py`) | Endpoint | Qué calcula | NSR-10 |
|---|---|---|---|
| `propiedades_perfil_c` | `POST /acero-frio/perfil-c/propiedades` | A, Ix, Iy, J, centro de cortante, Cw y ro | F.4.3.1, F.4.3.3-13 |
| `flexion_perfil_c` | `…/flexion` | φbMn = mín(sección; lateral-torsional; distorsional) | F.4.3.3.1.1, F.4.3.3.1.2.1, F.4.3.3.1.4(b), F.4.2 |
| `cortante_perfil_c` | — | φvVn de almas sin huecos | F.4.3.3.2.1 |
| `verificar_viga_c` | `…/viga` | Flexión, cortante e interacción → `cumple` | F.4.3.3.3 (ec. 54) |
| `compresion_perfil_c` | `…/compresion` | φcPn = 0,85·mín(Ae·Fn; distorsional) | F.4.3.4.1, F.4.3.4.2(b) |
| `tension_perfil_c` | `…/tension` | φTn por fluencia y por rotura en la sección neta | F.4.3.2 a) y b) |
| `flexocompresion_perfil_c` | `…/flexocompresion` | Ecuaciones de interacción con αx y Cmx | F.4.3.5.2 |
| `flexotension_perfil_c` | `…/flexotension` | Ecuaciones de interacción + tensión sola | F.4.3.5.1 |
| `arrugamiento_perfil_c` | `…/arrugamiento` | Pn del alma e interacción con la flexión | F.4.3.3.4.1, F.4.3.3.5.1(a) |

Todas devuelven `ResultadoMotor` con supuestos, advertencias y `en_borde_dominio`. Los endpoints tienen límite de tasa y responden 422 con la norma citada. `src/espacio_diseno.py` declara el espacio de diseño para la épica #311.

## Entradas que la norma exige y el motor no supone

- **Lm** (distancia entre restricciones al pandeo distorsional), obligatoria en la C con pestaña. Si falta, el motor falla.
- **kφ**: 0 por defecto, que es el valor de la norma para una aleta sin restricción rotacional.
- **Pandeo lateral-torsional:** o se declara `aleta_comprimida_arriostrada=True`, o se dan KyLy, KtLt y Cb. `coeficiente_cb` aplica F.4.3.3-12; Cb = 1 es conservador.
- **Cmx** para la flexo-compresión: `coeficiente_cm` aplica F.4.3.5.2.1.
- **Coeficientes de arrugamiento:** se pasan con la fila citada de la Tabla F.4.3.3-2 (ver abajo).

## Lo que NO verifica todavía

- Conexiones (F.4.5); por eso no se cubre la rotura en la conexión de F.4.3.2 c).
- Flexión alrededor del eje débil (M̄y), secciones Z, almas con huecos y deflexiones.
- Parales y cerchas (F.4.8).

## Decisiones y hallazgos del corpus

- **E = 203 000 MPa** (F.4.4.6.1.3); G = E/(2(1+μ)), porque el corpus no fija G para F.4.
- **Propiedades por el método lineal con esquinas rectas.** Frente a la Guía DSM de AISI, My sale +3,8 % por no modelar los radios de doblez.
- **Distorsional por el método general (b).** La disposición simplificada (a) del corpus exige 45° ≤ θ < 90° y deja fuera la pestaña a 90°.
- **Erratas del corpus documentadas en el código:**
  - F.4.2.2-19 se lee b2 (no b1).
  - En F.4.2.3-1, ψ se toma como |f2/f1|.
  - En F.4.3.3-42 (K̃φfg) el corpus dice «ho²» donde va **hx²**. Una prueba verifica que K̃φfg no depende de la altura del alma.
- **Pendiente de cotejar con la NSR-10 impresa: F.4.3.3-41 (kφwe en flexión).** El corpus da E·t³/(12(1−μ²)ho); AISI S100-07 da E·t³/(12(1−μ²))·[3/ho + (π/L)²·19ho/60 + (π/L)⁴·ho³/240].
  - Se usa la del corpus, que es del lado seguro, pero para 9CS2.5×059 da Mcrd/My = 0,45, frente a 0,76 con la de AISI y 0,85 por franjas finitas (Guía DSM).
  - Todo indica que el corpus la truncó.
- **Tabla F.4.3.3-2 (arrugamiento):** el corpus la describe pero no trae los coeficientes. El motor no los carga de memoria: los recibe con la fila citada. Cuando la tabla esté transcrita de la norma impresa, se llena `TABLA_F_4_3_3_2`.
- **Salto propio de la norma en cortante:** en h/t = 1,51·√(E·kv/Fy) hay un salto de 0,24 %. El contrato marca esa zona como borde de dominio.
- **Sin pasos fijos:** la sección efectiva y Sc (a Fc) se resuelven con `brentq`, contrastados con sustitución sucesiva.

## Verificación

86 pruebas del paquete y 9 del router:

- solución cerrada del canal;
- formas cerradas de AISI para aleta + pestaña;
- Fd y Fe evaluados a mano;
- Cb clásico de 1,14;
- interacciones con números redondos;
- contraste con la Guía DSM de AISI §8.1;
- monotonicidad, homogeneidad dimensional, continuidad de las curvas y sabotaje;
- regresión del hallazgo de la revisión adversaria: φb en el rango sin pandeo lateral-torsional.

**Pendiente para «medido a producción»:** despliegue y llamada real autenticada (condición 4).

```powershell
python -m pytest packages/motor-acero-frio/tests -q
```
