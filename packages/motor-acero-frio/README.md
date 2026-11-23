# motor-acero-frio (#81)

Perfiles de acero formado en frío según NSR-10 F.4. Cubre la sección C (con o sin pestaña a 90°) en sus estados límite básicos.

| Función (`src/contrato_api.py`) | Qué calcula | NSR-10 |
|---|---|---|
| `propiedades_perfil_c` | A, Ix, Iy, J, centro de cortante, Cw y ro | F.4.3.1, F.4.3.3-13 |
| `flexion_perfil_c` | φbMn = φb·Se·Fy con la sección efectiva iterada | F.4.3.3.1.1 (proc. 1), F.4.2.2.3, F.4.2.3.2, F.4.2.4 |
| `cortante_perfil_c` | φvVn de almas sin huecos | F.4.3.3.2.1 |
| `tension_perfil_c` | φTn por fluencia y por rotura en la sección neta | F.4.3.2 a) y b) |
| `compresion_perfil_c` | φcPn con Fe = mín(flexión en el eje débil; flexo-torsional) y Ae con Fn | F.4.3.4.1 |
| `verificar_viga_c` | Flexión, cortante e interacción → `cumple` | F.4.3.3.3 (ec. 54) |

Todas devuelven `ResultadoMotor` con supuestos, advertencias y `en_borde_dominio`.

## Lo que NO verifica todavía

El contrato lo advierte en cada salida:

- **Pandeo lateral-torsional** (F.4.3.3.1.2). La flexión exige declarar `aleta_comprimida_arriostrada=True`; sin esa declaración falla.
- **Pandeo distorsional** (F.4.3.3.1.4 y F.4.3.4.2). Puede gobernar en C con pestaña.
- Conexiones (F.4.5): por eso no se cubre la rotura en la conexión de F.4.3.2 c).
- Arrugamiento del alma (F.4.3.3.4), flexo-compresión (F.4.3.5), secciones Z, almas con huecos y deflexiones.

## Decisiones y hallazgos

- **E = 203 000 MPa**, el valor que F.4 fija (F.4.4.6.1.3). La primera versión usaba 200 000 MPa.
- **G = E/(2(1+μ))**, porque el corpus no fija G para F.4.
- **Propiedades por el método lineal con esquinas rectas.** El radio de doblez no se modela, así que los anchos planos son la dimensión externa − 2t.
- **Erratas del corpus documentadas en `src/elementos.py`:**
  - F.4.2.2-19 se lee b2 (no b1);
  - en F.4.2.3-1, ψ se toma como |f2/f1|.
- **Salto propio de la norma en cortante:** en h/t = 1,51·√(E·kv/Fy) hay un salto de 0,24 % entre F.4.3.3-46 y -47. El contrato marca esa zona como borde de dominio.
- **Sección efectiva sin pasos fijos:** el punto fijo se resuelve con `brentq` (regla 3). Una prueba lo compara con sustitución sucesiva.

## Verificación

37 pruebas, todas contra referencias independientes:

- solución cerrada del canal (centro de cortante, Cw y J);
- propiedades por integración numérica;
- un Se calculado a mano;
- cortante, tensión y compresión evaluados a mano;
- monotonicidad, homogeneidad dimensional y sabotaje (entradas fuera de dominio fallan).

**Pendiente para el registro de motores:**
- contraste con un ejemplo publicado (condición 1 completa);
- endpoint con 422 y límite de tasa;
- despliegue con una llamada real.

```powershell
python -m pytest packages/motor-acero-frio/tests -q
```
