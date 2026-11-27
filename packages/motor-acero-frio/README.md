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
- **Arrugamiento:** apoyo (sujeta / no sujeta), carga (una / dos aletas) y posición (extremo / interior). El motor toma la fila de la Tabla F.4.3.3-2 y deduce la condición de la aleta de la geometría.
- **M1/M2** (opcional): β distorsional por gradiente de momento (F.4.3.3-38). Sin él, β = 1, el valor conservador.

## Lo que NO verifica todavía

- Conexiones (F.4.5); por eso no se cubre la rotura en la conexión de F.4.3.2 c).
- Flexión alrededor del eje débil (M̄y), secciones Z, almas con huecos y deflexiones.
- Parales y cerchas (F.4.8).

## Decisiones y hallazgos del corpus

- **E = 203 000 MPa** (F.4.4.6.1.3); G = E/(2(1+μ)), porque el corpus no fija G para F.4.
- **Propiedades por el método lineal con esquinas rectas.** Frente a la Guía DSM de AISI, My sale +3,8 % por no modelar los radios de doblez.
- **Distorsional por el método general (b).** La disposición simplificada (a) del corpus exige 45° ≤ θ < 90° y deja fuera la pestaña a 90°.
- **Cotejo con la NSR-10 impresa** (Minvivienda / AIS, 2010; copia local fuera del repositorio). En el distorsional manda la impresa sobre el corpus, que tenía estas diferencias:
  - F.4.3.3-41 (kφwe en flexión): el corpus la truncó; la impresa trae E·t³/(12(1−μ²))·[3/ho + (π/L)²·19ho/60 + (π/L)⁴·ho³/240];
  - F.4.3.3-39 (Lcr en flexión): lleva 4π⁴, no 6π⁴;
  - F.4.3.3-38: en flexión β es un factor de gradiente de momento (1 ≤ β ≤ 1,3), no (Lm/Lcr)^ln(Lm/Lcr);
  - F.4.3.4-21: en compresión, Fd no lleva β;
  - F.4.3.3-42: hx², donde el corpus decía «ho²». Una prueba verifica que K̃φfg no depende de la altura del alma.
- **Errata de traducción en la impresa:** define xo como «unión → centroide» y hx como «centroide → centro de cortante», al revés que AISI S100-07, de donde vienen las ecuaciones. Se usan las definiciones de AISI, que reproducen sus formas cerradas.
- **Contraste con la Guía DSM de AISI §8.1 (9CS2.5×059):** Mcrd/My da 0,74 frente a 0,85 por franjas finitas (12 % del lado seguro, lo esperable del método b). Con la kφwe truncada del corpus daba 0,45.
- **Tabla F.4.3.3-2** transcrita de la pág. F-344 (números, no texto de la norma). Las celdas combinadas del límite R/t se leen como en la Tabla C3.4.1-2 de AISI S100-07.
- **Otras erratas del corpus:** F.4.2.2-19 se lee b2 (no b1); en F.4.2.3-1, ψ = |f2/f1|.
- **Salto propio de la norma en cortante:** en h/t = 1,51·√(E·kv/Fy) hay un salto de 0,24 %. El contrato marca esa zona como borde de dominio.
- **Sin pasos fijos:** la sección efectiva y Sc (a Fc) se resuelven con `brentq`, contrastados con sustitución sucesiva.

## Verificación

88 pruebas del paquete y 9 del router:

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
