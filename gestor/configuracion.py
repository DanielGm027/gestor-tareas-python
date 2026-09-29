"""Configuración compartida mediante el patrón Singleton."""
from pathlib import Path


class Configuracion:
    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            instancia = super().__new__(cls)
            instancia.debug = False
            instancia.archivo_tareas = (
                Path(__file__).resolve().parent.parent / "data" / "tareas.json"
            )
            cls._instancia = instancia
        return cls._instancia

    # No uso __init__: una nueva llamada no debe reiniciar los valores.
