# Cómo emular ING

Hay dos herramientas distintas. Conviene usar las dos: el simulador del repositorio para verificar cada cambio en segundos, y el emulador de HP (o la calculadora) para la prueba final.

## 1. Emulador oficial: HP Prime Virtual Calculator

Es la calculadora completa corriendo en la computadora, con el mismo firmware y el mismo CAS. Lo que funciona ahí funciona en el equipo.

### Instalación

| Sistema | Cómo |
|---|---|
| Windows (64 bits) | `winget install --id=HP.PrimeVirtualCalculator -e`, o el instalador de [hpcalc.org](https://www.hpcalc.org/details/8939). |
| Windows (32 bits) | Instalador de [hpcalc.org](https://www.hpcalc.org/details/7468). |
| macOS | [HP Prime Virtual Calculator for MacOS](https://www.hpcalc.org/details/7799). |
| Linux | No hay versión oficial. |

A la fecha de este documento (octubre de 2026) la versión publicada es la 2.4.2. El listado completo, junto con el HP Connectivity Kit, está en <https://www.hpcalc.org/prime/pc>.

### Cargar el programa

**Opción A — pegar el texto**

1. Abrir `dist/ING_v1.1.txt` en un editor de texto, seleccionar todo y copiar.
2. En el emulador: `Shift` + `1` (Programa) → **Nuevo** → nombre `ING` → **OK**.
3. Borrar la plantilla que aparece (`EXPORT ING() BEGIN END;`).
4. Menú **Edit → Paste** del emulador.
5. Tocar **Comprobar**. Debe informar que no hay errores.
6. `Esc`, elegir `ING` y tocar **Ejecutar**.

**Opción B — con el HP Connectivity Kit**

Con el emulador abierto, el Connectivity Kit lo muestra como una calculadora más. Se crea el programa `ING` en *Programas*, se pega el texto y se guarda, igual que con el equipo real (ver el README).

### Qué revisar

- **Ayuda → Prueba**: cada renglón dice qué debería dar. Si el CAS responde `2*x` en los dos primeros, las derivadas, integrales, límites, Laplace y ecuaciones diferenciales tienen de dónde salir.
- Un recorrido por cada cuadro con los valores iniciales de los formularios (todos traen un ejemplo cargado).
- **Ayuda → Diagn.** antes de reproducir un error: el emulador muestra el número de renglón del archivo de `dist/`.

### Para pasar del renglón de `dist/` al archivo de `src/`

`dist/ING_v1.1.txt` es la unión de los ocho archivos de `src/` con los renglones largos cortados. Buscar el texto del renglón con `grep` en `src/` es la forma más rápida de ubicarlo.

## 2. Simulador de este repositorio

No es un emulador: no ejecuta el firmware de HP. Traduce el programa PPL a Python y lo corre contra una calculadora simulada que dibuja la pantalla en una imagen de 320×240.

### Para qué sirve

- **Verificar el formato.** El traductor (`sim/ppl2py.py`) acepta solo un subconjunto estricto de PPL y rechaza lo que la calculadora rechazaría o lo que se sabe que da problemas: más de 8 variables en un `LOCAL`, variables sin declarar, funciones usadas antes de definirse, cantidad de argumentos, nombres reservados, `RETURN` dentro de `IFERR`, mezcla de `AND`/`OR` sin paréntesis, etc.
- **Recorrer las pantallas.** Las pruebas son guiones de toques, teclas y respuestas de formularios. Cada pantalla queda guardada como imagen en `build/shots/`.
- **Encontrar caídas.** `sim/t_monkey.py` toca y escribe al azar durante cientos de pasos.
- **Comparar números.** Las distribuciones, el buscador de raíces de las fórmulas, las unidades y la masa molar se comparan contra `scipy` y valores de referencia.

### Qué no hace

- **No tiene CAS.** `CAS(...)` devuelve el comando entre `<< >>`. Los resultados simbólicos solo se pueden comprobar en el emulador de HP o en la calculadora.
- Las fuentes, los colores y los formularios `INPUT` son aproximados.
- Las apps nativas (`STARTAPP`, `EDITMAT`) solo quedan registradas.

### Requisitos

Python 3.10 o superior y:

```
pip install pillow numpy scipy
```

La fuente DejaVu Sans debe estar en `/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf` (viene instalada en la mayoría de las distribuciones de Linux). En otro sistema, cambiar `FONT_FILE` y `FALLBACK` al comienzo de `sim/pplrt.py`.

### Uso

```
tools/build.sh             # une src/, verifica y genera dist/ y sim/ing_py.py
tools/test.sh              # todo: build + auditoría + pruebas + 60 recorridas al azar
tools/test.sh 300          # lo mismo con 300 recorridas

python3 sim/t_math.py      # una sola familia de pruebas
python3 sim/t_monkey.py 1 30017   # repetir una recorrida al azar por su semilla
```

| Prueba | Qué recorre |
|---|---|
| `t_math.py` | Derivadas, integrales, límites, ecuaciones, polinomios, EDO, Laplace, campos, álgebra (muestra los comandos que irían al CAS). |
| `t_num.py` | Gráficos, coordenadas, matrices, probabilidad, RK4, ecuaciones numéricas. |
| `t_unit.py` | Distribuciones contra `scipy`, unidades y masa molar contra valores de referencia. |
| `t_form.py`, `t_form2.py` | La biblioteca de fórmulas: cada una se despeja para cada variable con datos al azar y se verifica; más casos con resultado conocido. |
| `t_inge.py` | Fórmulas, iteración, unidades, constantes, interpolación, masa molar, adimensionales, nuclear, estadística, planilla. |
| `t_monkey.py` | Recorridas al azar. |

### Escribir un guion

```python
import sys, os
sys.path.insert(0, "sim")
from harness import *

# cuadro 2 de la portada (Derivadas), primer renglón, completar el formulario, volver
r = run("mi_prueba", [tile(2), row(1), form("X^2*SIN(X)", "X", "X=2"), ESC, ESC])
print(r["cas"])        # comandos enviados al CAS
print(r["shots"])      # imágenes en build/shots/mi_prueba/
```

Acciones disponibles: `tile(k)` cuadro de la portada, `row(k)` renglón de un menú, `soft(k)` botón inferior, `key(c)` tecla por su código, `form(...)` respuestas de un formulario, `SAME` aceptar los valores iniciales, `CANCEL`, `ESC`, `PAGE2`.

Hay que ejecutar `tools/build.sh` antes: las pruebas usan `sim/ing_py.py`, que se genera.
