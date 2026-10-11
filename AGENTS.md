# AGENTS.md — memoria del proyecto ING

Contexto para cualquier asistente (Claude, Codex u otro) que trabaje en este repositorio. Leerlo completo antes de tocar código: la HP Prime rechaza el programa entero por un solo detalle de formato y no hay forma de probar en el equipo desde acá.

## Qué es

**ING** es un programa en HP PPL para la calculadora **HP Prime G2**: una portada de cuadros táctiles (2 páginas × 12) que da acceso por formularios a matemática e ingeniería química y nuclear. Se entrega como **un único archivo de texto** que la persona pega en un programa llamado `ING` desde el HP Connectivity Kit.

- Usuario: estudiante avanzado de Ingeniería (química y nuclear). Encuentra poco intuitiva la interfaz original; quiere entender cada pantalla con solo mirarla.
- Idioma de la interfaz y de la documentación: **español** (Argentina). Los textos en pantalla usan infinitivo o voseo ("Tocá el gráfico…"), son cortos y no usan jerga de programación.
- Estado: **versión 1.1, confirmada funcionando en la calculadora real** (octubre de 2026).

## Estructura

```
src/p1_base.ppl       encabezado, variables globales, ayudantes Ui* (pantalla, menús, formularios)
                      y motor de expresiones Ex* (traducción, evaluación, raíces, CAS)
src/p2_graf.ppl       gráficos Gr* (cartesiano, polar, superficie 3D) y MdAbreApp
src/p3_mate.ppl       módulos Md*: gráficos, derivadas, integrales, límites, ecuaciones,
                      polinomios, EDO, Laplace, campos, álgebra
src/p4_mat_prob.ppl   matrices Mt* y probabilidad Pr*
src/p5_inge.ppl       coordenadas Co*, iteración, interpolación, estadística
src/p6_datos.ppl      unidades Un*, constantes, masa molar Qm*
src/p7_formulas.ppl   biblioteca de fórmulas Fm*, autoprueba MdPrueba, MdAyuda
src/p8_main.ppl       IngIni, IngPortada, IngModulo, IngAbre y EXPORT ING()
tools/build.sh        une src/ → build/ING.txt → sim/ing_py.py → dist/ING_v<VERSION>.txt
tools/wrap.py         corta renglones de más de 110 caracteres después de una coma fuera de comillas
tools/audit.py        auditoría de formato del archivo final, renglón por renglón
tools/test.sh         build + auditoría + todas las pruebas
sim/ppl2py.py         analizador estricto de PPL y traductor a Python
sim/pplrt.py          calculadora simulada (pantalla 320×240, INPUT, WAIT, EXPR, distribuciones…)
sim/harness.py        guiones de toques/teclas/formularios y hojas de capturas
sim/t_*.py            pruebas
dist/ING_v1.1.txt     ENTREGA. Generado. UTF-8 sin BOM, finales CRLF
extras/               programas opcionales y separados (tecla de usuario, app con ícono). SIN PROBAR en el equipo
docs/                 EMULACION.md, ACCESO_RAPIDO.md, imágenes
VERSION               número de versión que usa build.sh para nombrar la entrega
```

`build/` y `sim/ing_py.py` se generan y no se versionan.

## Flujo de trabajo obligatorio

1. Editar **solo** `src/*.ppl` (nunca `dist/` a mano).
2. `tools/build.sh` — tiene que terminar sin `PROBLEM:` ni `SYNTAX ERROR`.
3. `tools/test.sh` — auditoría sin problemas, pruebas sin fallas, recorridas al azar con `tipos de error: 0`.
4. Si el cambio toca pantallas, mirar las imágenes de `build/shots/<prueba>/`.
5. Si cambia el comportamiento: subir `VERSION`, actualizar el texto `"~ING versión X"` en `MdAyuda` y el encabezado de `p1_base.ppl`, agregar la entrada en `CHANGELOG.md`, borrar la entrega anterior de `dist/` y actualizar los enlaces del README.

El orden de los archivos importa: una función debe estar **definida antes de usarse**. `p1` no puede llamar a nada de `p2`…`p8`.

## Reglas de formato PPL (no negociables)

Estas reglas salen de la documentación de HP, del foro de HP Museum y de los errores encontrados durante el desarrollo. `sim/ppl2py.py` y `tools/audit.py` verifican la mayoría.

**Archivo**
- Primer renglón: `#pragma mode( separator(.,;) integer(h32) )`. Fija punto decimal y `;`/`,` como separadores sin importar el ajuste de la calculadora.
- UTF-8 **sin BOM**; la entrega con **CRLF**. Sin tabuladores ni espacios al final.
- Caracteres fuera de ASCII (acentos, ², ³, °) **solo dentro de textos entre comillas**. Los comentarios van sin acentos.
- Sin comillas tipográficas, sin apóstrofos fuera de textos, sin guion bajo salvo en `RECT_P`, `LINE_P`, `TEXTOUT_P`.

**Nombres**
- Solo letras y dígitos, empezando con letra. Distinguen mayúsculas de minúsculas.
- Mínimo 3 caracteres (las letras sueltas A–Z, θ, y G0–G9, L0–L9, M0–M9, Z0–Z9, etc. son variables de la calculadora).
- No pueden coincidir —ni diferir solo en mayúsculas— con comandos, variables del sistema o de las apps (`Xmin`, `Nmax`, `Root`, `Result`, `Total`…). `tools/audit.py` trae la lista.
- Convención del proyecto: funciones con prefijo `Ui`, `Ex`, `Gr`, `Md`, `Mt`, `Pr`, `Co`, `Un`, `Qm`, `Fm`, `Ing` + CamelCase. Variables con prefijo de tipo + CamelCase: `n` número, `s` texto, `l` lista, `v` cualquiera, `g` global del programa. Ejemplos: `nIdx`, `sTit`, `lOpc`, `gBad`.
- Nombres que ya chocaron y se cambiaron: `nMax`, `nMin`, `nSub`, `sVd`.

**Declaraciones**
- `LOCAL` con **8 variables como máximo** por instrucción; usar varios `LOCAL` seguidos.
- Todos los `LOCAL` al comienzo de la función. No asignar en la misma línea de `LOCAL`.
- Las globales del programa son `LOCAL` a nivel de archivo (hoy 13, en `p1_base.ppl`). Solo `ING()` lleva `EXPORT`.
- No asignar a los parámetros de una función.

**Instrucciones**
- Palabras clave en MAYÚSCULAS. Asignación con `:=`. Comparación con `==`, `<>`, `<=`, `>=`.
- No usar `CASE` ni `BREAK`: cadenas de `IF … END;`.
- No mezclar `AND` y `OR` sin paréntesis. Paréntesis alrededor de `MOD` antes de comparar: `(nIdx MOD 4)==0`.
- **Nunca `RETURN` dentro de un bloque `IFERR`** (colgaba firmwares viejos). Patrón: bandera `nMal:=0; IFERR … THEN nMal:=1; END;` y decidir después.
- Sin notación `1E-5` en el código: escribir `0.00001` o `10^(-5)`. (Dentro de textos que se muestran sí puede aparecer.)
- La calculadora corta programas con demasiadas instrucciones seguidas sin pausa (del orden de 10 000 por ciclo de espera en firmwares viejos): acotar todos los bucles.

**Funciones de texto y listas: usar siempre los ayudantes**
- `ASC("")`, `LEFT`/`MID` con largo 0 o negativo, o con posición fuera del texto, fallan o se comportan mal. `INSTRING` y `POS` con texto o lista vacía, también.
- Usar `UiResto`, `UiIzq`, `UiMid`, `UiEn`, `UiPos`, `UiSinUlt` (definidos al comienzo de `p1_base.ppl`) en lugar de llamar directo.
- Texto vacío se compara con `sTxt==""`, no con `DIM(sTxt)==0`.

**Comandos de la calculadora en uso** (lista completa en `build/audit.txt` después de `tools/test.sh`): dibujo `RECT_P`, `LINE_P`, `TEXTOUT_P`, `DRAWMENU`, `RGB`; entrada `WAIT`, `INPUT`, `MSGBOX`, `EDITMAT`; apps `STARTAPP`, `STARTVIEW`; texto y listas `STRING`, `CHAR`, `ASC`, `DIM`, `SIZE`, `CONCAT`, `LEFT`, `MID`, `INSTRING`, `POS`, `SORT`, `TYPE`; evaluación `EXPR`, `CAS`, `CAS.expr`, `HVars`; matemática `ABS`, `IP`, `FLOOR`, `CEILING`, `ROUND`, `MIN`, `MAX`, `SIN`, `COS`, `ACOS`, `EXP`, `LN`, `LOG`, `COMB`. Las funciones de distribución (`NORMALD_CDF`, etc.) y el reloj (`TICKS`) se llaman a través de `EXPR` con el nombre en un texto, para que el programa compile aunque el firmware no las tenga. Antes de usar un comando nuevo: confirmar la firma en la documentación y agregarlo a `BUILTINS` en `sim/ppl2py.py` y a `sim/pplrt.py`.

## Cómo está hecho

**Pantalla.** 320×240. Barra de título de 0 a 24 px, contenido, y botones inferiores desde y = 220 (6 botones de 53,4 px). `UiFondo(sTit)` pinta el marco; `UiEspera()` devuelve `{1,x,y}` para un toque o `{2,tecla,0}` para una tecla (usa `WAIT(-1)`); `UiSoft(x)` convierte la x de un toque en número de botón.

**Componentes.**
- `UiMenu(sTit,lOpc,lSim)` → número de opción o 0. Siete renglones por página; recuerda la página por título.
- `UiPedir(sTit,lLab,lAyu,lIni,nTipo)` → lista de valores o `{}` si se canceló. `nTipo` 0 números, 1 textos. Reparte en formularios `INPUT` de hasta 6 campos.
- `UiTexto(sTit,lLin,lBot)` / `UiVer` → visor paginado. El primer carácter de cada renglón es el estilo: `#` rótulo, espacio texto, `!` resultado, `~` nota.
- `UiAviso(sTxt)` → mensaje. `UiNum(nVal,nDig)` → número con cifras significativas.
- `UiMarca()` se llama al cerrar un formulario o aviso: ignora toques durante 250 ms para que el toque que cerró la ventana no accione la pantalla siguiente.

**Expresiones.** La persona escribe `x^2*sin(x)` en mayúsculas o minúsculas. `ExComp(sExp,lVar,lDst,nModo)` la divide en piezas y la traduce:
- `nModo` 0, para evaluar con números en Inicio: las variables se reemplazan por variables reales de Inicio (`X` incógnita, `Y` segunda variable, `A B C D F G H J K L M N` datos; se saltean `E` e `I`), `log` → `LOG`, y se evalúa con `EXPR`.
- `nModo` 1, para el CAS: todo en minúsculas, `log` → `log10`, `sqrt(…)` → `((…)^0.5)`, `1.5e-3` → `(1.5*10^(-3))`.
- Si aparece un nombre desconocido: `gBad:=1` y el nombre queda en `gErr`.

**Errores.** No hay excepciones útiles: las funciones dejan `gBad` en 1 y quien llama decide. `IngAbre` envuelve cada módulo en `IFERR` y muestra un aviso genérico, salvo que `gDepura==1` (botón *Diagn.* de la Ayuda), en cuyo caso el error llega a la calculadora con su número de renglón.

**CAS.** `ExCas(sCmd)` arma `string(<comando>)` y prueba `CAS(EVAL(texto))`; si falla, `CAS.expr(texto)`. Devuelve texto. Los comandos son de giac: `diff`, `int`, `limit`, `solve`, `csolve`, `desolve`, `laplace`, `ilaplace`, `proot`, `factor`, `partfrac`, `taylor`, `subst`, `evalf`, `sum`. (`CAS("string(...)")` directo **no** funciona: fue el error del primer prototipo.)

**Raíces numéricas.** `ExRaices(nIni)` resuelve `gRes = 0` para el módulo de fórmulas y el de ecuaciones: atajo si es lineal, secante desde la semilla, y barrido de cambios de signo de −1e30 a 1e30 con bisección. Devuelve todas las raíces reales encontradas, la más razonable primero (positiva y del orden de la semilla). Descarta polos con `ExEsRaiz`.

**Fórmulas.** Cada una es un texto `"Nombre|ecuacion|var:descripcion;var:descripcion"` en `FmDatos(nCat)`. `FmUsar` muestra las variables, la persona elige la incógnita, carga el resto y se resuelve numéricamente; el botón *Otra* recorre las demás raíces. Las fórmulas propias viven en la lista `gMias` y se guardan en la variable de Inicio `INGF` con `HVars`.

**Matrices.** A = `M1`, B = `M2`, resultado en `M3`. Se editan con `EDITMAT`.

**Probabilidad.** 10 distribuciones. Las continuas usan las funciones de la calculadora (`NORMALD_CDF`, `STUDENT_CDF`, `CHISQUARE_CDF`, `FISHER_CDF`, y sus densidades e inversas) a través de `PrCall`; las discretas se suman en bucles acotados (n, λ y N ≤ 2000).

**Apps nativas.** `MdAbreApp(lNom,nVista)` prueba varios nombres porque cambian con el idioma (`"Spreadsheet"`, `"Hoja de cálculo"`). Abrir una app termina ING.

## Recetas

**Agregar una fórmula fija.** Sumar un renglón en la categoría que corresponda de `FmDatos` (`src/p7_formulas.ppl`):
```
"Nombre visible|ecuacion=con*variables|var:Descripción [unidad];otra:Descripción",
```
Nombre de hasta 52 caracteres, único en su categoría. Variables en minúsculas, letras y dígitos, entre 1 y 13, todas con descripción. No usar `e` ni `i` como variables. `sim/t_form.py` la verifica sola; conviene sumar un caso con resultado conocido en `sim/t_form2.py`.

**Agregar una unidad.** En `UnDatos(nCat)` de `src/p6_datos.ppl`: nombre en la primera lista y factor a la unidad base en la segunda, en la misma posición. La temperatura va aparte (`UnAKelvin`, `UnDeKelvin`).

**Agregar una opción a un módulo.** Sumar el texto y el símbolo en la llamada a `UiMenu` del `Md…` y un `IF nOpc==k THEN … END;`. Todos los formularios llevan valores iniciales que funcionen como ejemplo.

**Agregar un módulo.** Las dos páginas de la portada están llenas (24 cuadros). Hay que reemplazar un cuadro o agregar una tercera página en `IngPortada`, `IngModulo` y el bucle de `ING()`.

## Simulador y pruebas

`sim/ppl2py.py` traduce el PPL a Python (`sim/ing_py.py`) y `sim/pplrt.py` hace de calculadora. Es deliberadamente **más estricto** que el equipo en los casos límite de texto (`MID`, `LEFT`, `ASC`, `INSTRING`, `POS` levantan error donde la calculadora podría fallar).

- El CAS **no** está simulado: `CAS(...)` devuelve `<<comando>>`. Ningún resultado simbólico está verificado por las pruebas.
- `giac` no se pudo instalar en el entorno donde se desarrolló (sin acceso a PyPI para ese paquete). Si está disponible, conectar `giacpy` al stub de CAS sería la mejora más valiosa del simulador.
- `python3 sim/t_monkey.py N` hace N recorridas al azar; `python3 sim/t_monkey.py 1 <semilla>` repite una.
- Detalle de uso y de guiones en `docs/EMULACION.md`.

## Decisiones tomadas (y por qué)

- **Programa del catálogo, no app con ícono.** Un programa es un solo texto que se pega; una app requiere archivos binarios que no se pueden generar ni verificar desde acá.
- **Planilla y Estadística abren las apps nativas.** Reescribirlas sería peor que lo que ya trae la calculadora.
- **Límites de dos variables por caminos.** El CAS no resuelve el caso general; se evalúan rectas y parábolas y se informa si coinciden.
- **EDO numérica solo de primer orden (RK4).** Las de orden superior se resuelven con `desolve`.
- **Fórmulas resueltas numéricamente, no con el CAS.** Así se despeja cualquier variable, incluso implícita (Colebrook), y no depende del estado del CAS.
- **Sin persistencia salvo `INGF`.** El programa pisa las variables A–N, X, Y y M1–M3 de Inicio; está avisado en la Ayuda.

## Lo que no está verificado

- `extras/INGTECLA.txt` y `extras/INGAPP.txt` (pedido del usuario: llegar al menú sin pasar por el catálogo). La calculadora no puede ejecutar un programa al encenderse; estas son las dos alternativas, escritas pero no probadas. Se mantienen fuera de `ING` para no arriesgar el programa que ya funciona.
- Resultados simbólicos (ver arriba). En la calculadora, **Ayuda → Prueba** muestra si el CAS responde.
- Aspecto exacto de fuentes y formularios en el equipo.
- Versiones de firmware anteriores a la que tiene la calculadora del usuario.

Si se informa una falla en el equipo: pedir el mensaje y el número de renglón con **Ayuda → Diagn.** activado, ubicar el renglón en `dist/` y de ahí en `src/`.

## Qué no hacer

- No editar `dist/` a mano ni entregar un archivo que no pasó `tools/test.sh`.
- No "modernizar" el estilo (CASE, BREAK, nombres cortos, llamadas directas a `MID`/`LEFT`): las restricciones son deliberadas.
- No afirmar que algo fue probado en la calculadora o en el emulador de HP si solo corrió en el simulador.
- No agregar texto en inglés a la interfaz.
