# Abrir ING más rápido

La HP Prime **no tiene una opción para ejecutar un programa al encenderse**: al prender vuelve a la pantalla donde estaba. Lo que sí se puede es acortar el camino. Hay tres formas; las dos últimas todavía **no se probaron en la calculadora**.

## 1. Desde la caja de herramientas (ya funciona)

`Toolbox` (la tecla de la caja) → pestaña **Usuario** → **ING** → `Enter`. No hace falta entrar al catálogo de programas.

## 2. Una tecla (sin probar)

Un programa aparte asigna ING a una tecla del modo Usuario.

1. Crear un programa nuevo llamado `INGTECLA`, borrar la plantilla y pegar [`extras/INGTECLA.txt`](../extras/INGTECLA.txt). **Comprobar**.
2. Activar el modo Usuario fijo: `Shift` + `Help` **dos veces** (arriba aparece `1U` la primera vez y `U` fijo la segunda).
3. Con el modo Usuario activo, la tecla `Help` abre ING.

Para usar otra tecla, cambiar `K_Help` por el nombre de la tecla (`K_Apps`, `K_Symb`, `K_Plot`, `K_Num`, `K_View`, `K_Menu`…). Para sacarlo, borrar el programa `INGTECLA`.

Va en un programa separado a propósito: si esta parte fallara, ING sigue funcionando igual.

## 3. Un ícono en la biblioteca de apps (sin probar) — opción elegida

El programa `ING` tiene que seguir instalado: la app solo lo llama.

1. `Apps` → resaltar **Función** sin abrirla (con las flechas, o manteniendo el dedo) → **Guardar** → nombre `Menu ING` → **OK**. Queda una app nueva con su ícono.
2. Abrir **Menu ING** una vez desde `Apps`, para que sea la app activa.
3. `Shift` + `1` (Programa): arriba de todo aparece **Menu ING (App)**. Abrirlo, borrar su contenido y pegar [`extras/INGAPP.txt`](../extras/INGAPP.txt). **Comprobar**.
4. Desde ahora: `Apps` → tocar **Menu ING** abre el menú.

Al tocar **Salir** en ING se queda en la vista de la app copiada (la de Función). Los cuadros que abren otra app (Planilla, Estadística, Función) cambian la app activa; para volver, `Apps` → **Menu ING**.

Si al abrir la app aparece la pantalla de Función y no el menú, es que `START()` no se ejecutó: revisar que el texto esté en **Menu ING (App)** y no en un programa común del catálogo.

## Qué falta saber

Si alguna de las dos opciones sin probar da error en **Comprobar** o al ejecutarse, anotar el mensaje y abrir un issue: son pocas líneas y se ajustan rápido.
