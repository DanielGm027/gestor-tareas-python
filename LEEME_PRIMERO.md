# Cómo usar y entregar el proyecto

1. Extrae todo el ZIP en una carpeta de tu equipo.
2. Abre `GestorTareas` en Visual Studio Code y abre su terminal.
3. Comprueba Python con `py --version` en Windows.
4. Ejecuta `py main.py` para abrir el menú.
5. Ejecuta `py -m unittest discover -s tests -v` para comprobar las 27 pruebas.
6. Revisa el reporte editable en `docs/Actividad1_GomezCarlosDaniel.docx`.
7. Sigue `PUBLICAR_GITHUB.md` para publicar y compartir el enlace del repositorio.

En Linux o macOS sustituye `py` por `python3`. La aplicación y las pruebas
utilizan únicamente la biblioteca estándar; no necesitas instalar paquetes.

El ZIP incluye un repositorio real con seis commits. Conserva la carpeta `.git`.
También incluye `Historial_GestorTareas.bundle` junto a la carpeta del proyecto,
como respaldo de todo el historial. No necesitas volver a ejecutar `git init`.

El archivo `data/tareas.json` se crea al guardar. Las tareas de demostración
están en `evidencias/datos_demo.json` y las capturas en `evidencias/`.

En Windows puedes abrir `iniciar_windows.bat` con doble clic si tienes instalado
Python con el lanzador `py`.
