"""Interfaz de consola para agregar, listar y completar tareas."""
from gestor.tareas import GestorTareas


def main():
    gestor = GestorTareas()
    while True:
        print("\n1. Agregar tarea\n2. Listar tareas\n3. Completar tarea\n4. Salir")
        opcion = input("Elige una opción: ").strip()
        try:
            if opcion == "1":
                tarea = gestor.agregar(input("Descripción: "))
                print(f"Tarea agregada con ID {tarea.id}.")
            elif opcion == "2":
                for tarea in gestor.listar():
                    print(tarea)
            elif opcion == "3":
                gestor.completar(int(input("ID de la tarea: ")))
                print("Tarea completada.")
            elif opcion == "4":
                break
            else:
                print("Opción inválida.")
        except (ValueError, KeyError) as error:
            print(error)


if __name__ == "__main__":
    main()
