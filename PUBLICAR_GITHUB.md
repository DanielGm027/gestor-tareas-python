# Publicar el proyecto conservando sus commits

El repositorio local ya está listo. Inicia sesión en tu cuenta de GitHub desde
tu equipo, publícalo y entrega su URL real en la plataforma de la actividad.

## Opción sencilla con GitHub Desktop

1. Instala GitHub Desktop e inicia sesión.
2. Extrae el ZIP completo y conserva la carpeta `.git` dentro de `GestorTareas`.
3. En GitHub Desktop selecciona **File > Add local repository**.
4. Selecciona la carpeta `GestorTareas`, no la carpeta superior del ZIP.
5. Revisa **History** y comprueba que aparecen seis commits.
6. Selecciona **Publish repository** y usa el nombre `gestor-tareas-python`.
7. Define la visibilidad según lo que solicite tu docente. Si es privado,
   dale acceso para que pueda revisar la entrega.
8. Abre el repositorio en GitHub y copia la URL para entregarla.

No uses **Upload files** como único método: no transfiere el historial local
de commits que pide la actividad.

## Opción con Git Bash

1. Crea en GitHub un repositorio vacío llamado `gestor-tareas-python`.
   No agregues README, licencia ni `.gitignore` en la página.
2. Abre Git Bash dentro de la carpeta `GestorTareas`.
3. Ejecuta `git log --oneline --reverse` y comprueba los seis commits.
4. Copia la URL HTTPS del repositorio. Sustituye `TU_USUARIO` por tu usuario real:

```bash
git remote add origin https://github.com/TU_USUARIO/gestor-tareas-python.git
git push -u origin main
```

Git puede abrir una ventana de autenticación; inicia sesión con tu cuenta.
No guardes contraseñas ni tokens en el proyecto.

## Si tu extractor no conservó la carpeta .git

El ZIP incluye `Historial_GestorTareas.bundle`. Abre Git Bash en la carpeta
donde está ese archivo y recupera el proyecto completo con:

```bash
git clone Historial_GestorTareas.bundle GestorTareasRecuperado
cd GestorTareasRecuperado
git log --oneline --reverse
```

Publica esa carpeta recuperada siguiendo los pasos anteriores.

## Identidad para futuros commits

Los commits incluidos usan Carlos Daniel Gómez González y un correo local
de identificación. Para asociar tus siguientes commits a GitHub, configura
tu correo verificado o el correo privado que GitHub te asigna:

```bash
git config user.name "Carlos Daniel Gómez González"
git config user.email "TU_CORREO_VERIFICADO_O_PRIVADO"
```

## Revisión antes de compartir

- Comprueba que estén README, código, tests, evidencias y docs.
- Comprueba los seis commits de la rama main en GitHub.
- Ejecuta las 27 pruebas en tu equipo.
- Entrega el enlace del repositorio. El ZIP no sustituye ese enlace.

Referencia: GitHub. (s. f.). *Adding locally hosted code to GitHub*.
https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github
