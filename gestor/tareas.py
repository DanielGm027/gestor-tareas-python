"""Operaciones sobre las tareas y representación de sus datos."""
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Tarea:
    id: int
    descripcion: str
    completada: bool = False


class GestorTareas:
    def __init__(self):
        self._tareas = []
        self._siguiente_id = 1

    def agregar(self, descripcion):
        if not isinstance(descripcion, str) or not descripcion.strip():
            raise ValueError("La descripción no puede estar vacía.")
        tarea = Tarea(self._siguiente_id, descripcion.strip())
        self._tareas.append(tarea)
        self._siguiente_id += 1
        return tarea

    def listar(self):
        return list(self._tareas)

    def completar(self, id_tarea):
        if type(id_tarea) is not int or id_tarea <= 0:
            raise ValueError("El ID debe ser un entero positivo.")
        for indice, tarea in enumerate(self._tareas):
            if tarea.id == id_tarea:
                if tarea.completada:
                    return False
                self._tareas[indice] = replace(tarea, completada=True)
                return True
        raise KeyError(f"No existe una tarea con ID {id_tarea}.")
