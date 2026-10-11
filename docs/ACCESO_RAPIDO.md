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

## 3. Un ícono en la biblioteca de apps (sin probar)

1. `Apps` → seleccionar **Función** → **Guardar** → nombre `Menu ING`. Queda una app nueva con su ícono.
2. `Shift` + `1` (Programa): aparece un programa con el nombre de la app. Abrirlo, borrar su contenido y pegar [`extras/INGAPP.txt`](../extras/INGAPP.txt). **Comprobar**.
3. Desde ahora: `Apps` → tocar **Menu ING** abre el menú.

Como la calculadora recuerda la última app usada, la tecla `Apps` deja el ícono a un toque.

## Qué falta saber

Si alguna de las dos opciones sin probar da error en **Comprobar** o al ejecutarse, anotar el mensaje y abrir un issue: son pocas líneas y se ajustan rápido.
