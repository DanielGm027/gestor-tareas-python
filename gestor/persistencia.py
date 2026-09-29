"""Lectura validada de JSON y escritura mediante reemplazo atómico."""
import json
import os
import tempfile
from dataclasses import asdict
from pathlib import Path

from .tareas import Tarea


class DatosInvalidos(ValueError):
    """El archivo existe pero no contiene una lista de tareas válida."""


def cargar_tareas(archivo):
    archivo = Path(archivo)
    try:
        with archivo.open("r", encoding="utf-8") as entrada:
            datos = json.load(entrada)
    except FileNotFoundError:
        return []
    except (json.JSONDecodeError, UnicodeError) as error:
        raise DatosInvalidos("El archivo de tareas no es un JSON válido.") from error

    if not isinstance(datos, list):
        raise DatosInvalidos("El JSON debe contener una lista de tareas.")
    tareas = []
    ids = set()
    for registro in datos:
        if not isinstance(registro, dict) or set(registro) != {
            "id", "descripcion", "completada"
        }:
            raise DatosInvalidos("Una tarea tiene campos incorrectos.")
        id_tarea = registro["id"]
        descripcion = registro["descripcion"]
        if type(id_tarea) is not int or id_tarea <= 0 or id_tarea in ids:
            raise DatosInvalidos("Los ID deben ser positivos y únicos.")
        if not isinstance(descripcion, str) or not descripcion.strip():
            raise DatosInvalidos("Una descripción está vacía o es inválida.")
        if type(registro["completada"]) is not bool:
            raise DatosInvalidos("El estado completada debe ser booleano.")
        ids.add(id_tarea)
        tareas.append(Tarea(id_tarea, descripcion.strip(), registro["completada"]))
    return tareas


def guardar_tareas(archivo, tareas):
    archivo = Path(archivo)
    archivo.parent.mkdir(parents=True, exist_ok=True)
    temporal = None
    try:
        # El temporal está en el mismo directorio para poder reemplazar el archivo.
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=archivo.parent,
            prefix=archivo.name + ".", suffix=".tmp", delete=False
        ) as salida:
            temporal = Path(salida.name)
            json.dump([asdict(tarea) for tarea in tareas], salida,
                      ensure_ascii=False, indent=2)
            salida.write("\n")
            salida.flush()
            os.fsync(salida.fileno())
        os.replace(temporal, archivo)
    finally:
        if temporal is not None:
            temporal.unlink(missing_ok=True)
