# Historial

## 1.1 — 2026-10-11

Revisión de formato renglón por renglón. Primera versión confirmada en una HP Prime G2 real.

- Ayudantes seguros para las funciones de texto y de listas (`UiResto`, `UiIzq`, `UiMid`, `UiEn`, `UiPos`): la calculadora falla con largo 0, posición fuera del texto o texto vacío.
- Texto vacío comparado con `==""` en lugar de `DIM(...)==0`.
- Verificado que no hay ningún `RETURN` dentro de un bloque `IFERR`.
- Protección contra división por cero en el zoom de los gráficos.
- Archivo de entrega con finales de renglón CRLF.

## 1.0 — 2026-10-11

Primera versión completa: 24 cuadros en dos páginas.

- Matemática: gráficos 2D, polares y 3D, derivadas, integrales, límites, ecuaciones, polinomios, ecuaciones diferenciales, Laplace, matrices, probabilidad, coordenadas, campos.
- Ingeniería: 144 fórmulas despejables por materia, fórmulas propias, iteración, unidades, constantes, interpolación, masa molar, adimensionales, nuclear, álgebra, accesos a Estadística y Hoja de cálculo.
- Autoprueba y modo diagnóstico en la Ayuda.
- Buscador de raíces propio para despejar cualquier variable de una fórmula.

## 0.1 — prototipo

Descartado. Llamaba al CAS con `CAS("string(...)")`, que no funciona; se reemplazó por `CAS(EVAL(...))` con `CAS.expr(...)` de respaldo.
