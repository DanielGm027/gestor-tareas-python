"""Menú de consola. Ejecutar con python main.py."""
import argparse
import sys
from pathlib import Path

from gestor.configuracion import Configuracion
from gestor.persistencia import DatosInvalidos
from gestor.tareas import GestorTareas


def mostrar_tareas(gestor):
    tareas = gestor.listar()
    if not tareas:
        print("No hay tareas registradas.")
        return
    print("\nID | Estado     | Descripción")
    print("-" * 55)
    for tarea in tareas:
        estado = "Completada" if tarea.completada else "Pendiente"
        print(f"{tarea.id:>2} | {estado:<10} | {tarea.descripcion}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Gestor de tareas en Python")
    parser.add_argument("--debug", action="store_true", help="Mostrar diagnósticos")
    parser.add_argument("--archivo", type=Path, help="Ruta alternativa para el JSON")
    argumentos = parser.parse_args(argv)
    configuracion = Configuracion()
    configuracion.debug = argumentos.debug
    if argumentos.archivo is not None:
        configuracion.archivo_tareas = argumentos.archivo.resolve()
    try:
        gestor = GestorTareas(configuracion)
    except (OSError, DatosInvalidos) as error:
        print(f"No pude cargar las tareas: {error}", file=sys.stderr)
        print("Revisa el archivo. No se modificó su contenido.", file=sys.stderr)
        return 1

    print("GESTOR DE TAREAS")
    print(f"Tareas cargadas: {len(gestor.listar())}")
    if configuracion.debug:
        print(f"[DEBUG] Archivo: {configuracion.archivo_tareas}")

    try:
        while True:
            print("\n1. Agregar tarea\n2. Listar tareas\n3. Completar tarea\n4. Guardar y salir")
            opcion = input("Elige una opción: ").strip()
            try:
                if opcion == "1":
                    tarea = gestor.agregar(input("Descripción: "))
                    gestor.guardar()
                    print(f"Tarea agregada con ID {tarea.id}.")
                elif opcion == "2":
                    mostrar_tareas(gestor)
                elif opcion == "3":
                    id_tarea = int(input("ID de la tarea: "))
                    if gestor.completar(id_tarea):
                        gestor.guardar()
                        print("Tarea marcada como completada.")
                    else:
                        print("La tarea ya estaba completada.")
                elif opcion == "4":
                    break
                else:
                    print("Opción inválida. Elige un número del 1 al 4.")
            except ValueError as error:
                print(f"Dato inválido: {error}")
            except KeyError as error:
                print(error.args[0])
            if configuracion.debug:
                print(f"[DEBUG] Tareas en memoria: {len(gestor.listar())}")
    except (EOFError, KeyboardInterrupt):
        print("\nSe solicitó el cierre de la aplicación.")
    except OSError as error:
        print(f"No pude guardar las tareas: {error}", file=sys.stderr)
        return 1

    try:
        gestor.guardar()
    except OSError as error:
        print(f"No pude guardar las tareas: {error}", file=sys.stderr)
        return 1
    print("Cambios guardados. Hasta luego.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
