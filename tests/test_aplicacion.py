"""Pruebas de comportamiento con archivos temporales independientes."""
import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path
from unittest.mock import patch

from gestor.configuracion import Configuracion
from gestor.persistencia import DatosInvalidos
from gestor.tareas import GestorTareas
from main import main

ROOT = Path(__file__).resolve().parent.parent


class BasePrueba(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.archivo = Path(self.temporal.name) / "data" / "tareas.json"
        self.config = Configuracion()
        anterior = (self.config.debug, self.config.archivo_tareas)
        self.addCleanup(self.restaurar_configuracion, anterior)
        self.config.debug = False
        self.config.archivo_tareas = self.archivo
        self.gestor = GestorTareas(self.config)

    def restaurar_configuracion(self, valores):
        self.config.debug, self.config.archivo_tareas = valores

    def escribir_json(self, datos):
        self.archivo.parent.mkdir(parents=True, exist_ok=True)
        self.archivo.write_text(json.dumps(datos), encoding="utf-8")

    def ejecutar_cli(self, entradas, *opciones):
        return subprocess.run(
            [sys.executable, str(ROOT / "main.py"), "--archivo",
             str(self.archivo), *opciones],
            input=entradas, capture_output=True, text=True, encoding="utf-8",
            timeout=10, cwd=ROOT,
        )


class PruebasConfiguracion(BasePrueba):
    def test_instancia_unica(self):
        self.assertIs(Configuracion(), Configuracion())

    def test_configuracion_compartida_sin_reinicio(self):
        self.config.debug = True
        otra = Configuracion()
        self.assertTrue(otra.debug)
        self.assertEqual(otra.archivo_tareas, self.archivo)


class PruebasTareas(BasePrueba):
    def test_agregar_tarea_pendiente(self):
        tarea = self.gestor.agregar("Estudiar Python")
        self.assertEqual(tarea.id, 1)
        self.assertEqual(tarea.descripcion, "Estudiar Python")
        self.assertFalse(tarea.completada)
        self.assertEqual(self.gestor.listar(), [tarea])

    def test_quitar_espacios_exteriores(self):
        self.assertEqual(self.gestor.agregar("  Leer  ").descripcion, "Leer")

    def test_rechazar_descripciones_invalidas(self):
        for descripcion in ("", "   ", "\n\t", None, 15):
            with self.subTest(descripcion=descripcion):
                with self.assertRaises(ValueError):
                    self.gestor.agregar(descripcion)
        self.assertEqual(self.gestor.listar(), [])

    def test_ids_unicos_consecutivos(self):
        ids = [self.gestor.agregar("Tarea").id for _ in range(3)]
        self.assertEqual(ids, [1, 2, 3])

    def test_listar_sin_tareas(self):
        self.assertEqual(self.gestor.listar(), [])

    def test_listado_no_permite_borrar_datos_internos(self):
        self.gestor.agregar("Tarea")
        self.gestor.listar().clear()
        self.assertEqual(len(self.gestor.listar()), 1)

    def test_tarea_no_se_modifica_desde_fuera(self):
        tarea = self.gestor.agregar("Tarea")
        with self.assertRaises(FrozenInstanceError):
            tarea.completada = True
        self.assertFalse(self.gestor.listar()[0].completada)

    def test_completar_tarea_existente(self):
        tarea = self.gestor.agregar("Entregar actividad")
        self.assertTrue(self.gestor.completar(tarea.id))
        self.assertTrue(self.gestor.listar()[0].completada)

    def test_completar_dos_veces_sin_duplicar(self):
        tarea = self.gestor.agregar("Tarea")
        self.gestor.completar(tarea.id)
        self.assertFalse(self.gestor.completar(tarea.id))
        self.assertEqual(len(self.gestor.listar()), 1)

    def test_completar_id_inexistente(self):
        self.gestor.agregar("Tarea")
        with self.assertRaises(KeyError):
            self.gestor.completar(99)
        self.assertFalse(self.gestor.listar()[0].completada)

    def test_rechazar_ids_invalidos(self):
        for id_tarea in (0, -1, True, "1", 1.5, None):
            with self.subTest(id=id_tarea):
                with self.assertRaises(ValueError):
                    self.gestor.completar(id_tarea)


class PruebasPersistencia(BasePrueba):
    def test_archivo_inexistente_inicia_vacio(self):
        self.assertFalse(self.archivo.exists())
        self.assertEqual(GestorTareas(self.config).listar(), [])

    def test_guardar_y_cargar_estado_y_acentos(self):
        tarea = self.gestor.agregar("Repasar diseño y programación")
        self.gestor.completar(tarea.id)
        self.gestor.guardar()
        nuevo = GestorTareas(self.config)
        self.assertEqual(nuevo.listar(), self.gestor.listar())
        texto = self.archivo.read_text(encoding="utf-8")
        self.assertIn("programación", texto)
        self.assertEqual(json.loads(texto)[0]["completada"], True)

    def test_crear_directorio_y_guardar_lista_vacia(self):
        self.gestor.guardar()
        self.assertEqual(json.loads(self.archivo.read_text()), [])

    def test_continuar_ids_al_cargar(self):
        self.escribir_json([{"id": 8, "descripcion": "Anterior", "completada": False}])
        nuevo = GestorTareas(self.config)
        self.assertEqual(nuevo.agregar("Nueva").id, 9)

    def test_rechazar_json_corrupto(self):
        self.archivo.parent.mkdir(parents=True)
        self.archivo.write_text("{contenido roto", encoding="utf-8")
        with self.assertRaises(DatosInvalidos):
            GestorTareas(self.config)
        self.assertEqual(self.archivo.read_text(), "{contenido roto")

    def test_rechazar_esquemas_invalidos(self):
        valido = {"id": 1, "descripcion": "Tarea", "completada": False}
        casos = [
            {}, [None], [{"id": 1}], [dict(valido, extra=1)],
            [dict(valido, id=True)], [dict(valido, id=0)],
            [dict(valido, descripcion=" ")], [dict(valido, descripcion=5)],
            [dict(valido, completada="false")], [valido, valido],
        ]
        for datos in casos:
            with self.subTest(datos=datos):
                self.escribir_json(datos)
                with self.assertRaises(DatosInvalidos):
                    GestorTareas(self.config)

    def test_fallo_de_escritura_conserva_archivo_anterior(self):
        self.gestor.agregar("Original")
        self.gestor.guardar()
        anterior = self.archivo.read_bytes()
        self.gestor.agregar("Nueva")
        with patch("gestor.persistencia.os.replace", side_effect=OSError("Sin permiso")):
            with self.assertRaises(OSError):
                self.gestor.guardar()
        self.assertEqual(self.archivo.read_bytes(), anterior)
        self.assertEqual(list(self.archivo.parent.glob("*.tmp")), [])


class PruebasConsola(BasePrueba):
    def test_flujo_completo_y_reinicio(self):
        primera = self.ejecutar_cli("1\nEstudiar Python\n3\n1\n2\n4\n")
        self.assertEqual(primera.returncode, 0, primera.stderr)
        self.assertIn("Tarea agregada con ID 1", primera.stdout)
        self.assertIn("Completada", primera.stdout)
        segunda = self.ejecutar_cli("2\n4\n")
        self.assertEqual(segunda.returncode, 0, segunda.stderr)
        self.assertIn("Tareas cargadas: 1", segunda.stdout)
        self.assertIn("Estudiar Python", segunda.stdout)

    def test_entradas_invalidas_no_cierran_aplicacion(self):
        resultado = self.ejecutar_cli("9\n1\n   \n3\nabc\n3\n99\n4\n")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("Opción inválida", resultado.stdout)
        self.assertIn("Dato inválido", resultado.stdout)
        self.assertIn("No existe una tarea", resultado.stdout)

    def test_fin_de_entrada_guarda_datos(self):
        resultado = self.ejecutar_cli("1\nTarea antes del cierre\n")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("Cambios guardados", resultado.stdout)
        self.assertEqual(json.loads(self.archivo.read_text())[0]["descripcion"],
                         "Tarea antes del cierre")

    def test_ctrl_c_guarda_datos(self):
        with patch("builtins.input", side_effect=["1", "Tarea", KeyboardInterrupt()]):
            with contextlib.redirect_stdout(io.StringIO()):
                codigo = main(["--archivo", str(self.archivo)])
        self.assertEqual(codigo, 0)
        self.assertEqual(len(json.loads(self.archivo.read_text())), 1)

    def test_debug_muestra_diagnosticos(self):
        resultado = self.ejecutar_cli("2\n4\n", "--debug")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("[DEBUG] Archivo:", resultado.stdout)
        self.assertIn("[DEBUG] Tareas en memoria: 0", resultado.stdout)

    def test_json_corrupto_no_se_sobrescribe_al_iniciar(self):
        self.archivo.parent.mkdir(parents=True)
        self.archivo.write_text("archivo corrupto", encoding="utf-8")
        resultado = self.ejecutar_cli("4\n")
        self.assertEqual(resultado.returncode, 1)
        self.assertIn("No pude cargar", resultado.stderr)
        self.assertEqual(self.archivo.read_text(), "archivo corrupto")

    def test_error_guardando_se_informa_y_devuelve_error(self):
        with patch("gestor.tareas.GestorTareas.guardar", side_effect=OSError("Sin permiso")):
            with patch("builtins.input", return_value="4"):
                with contextlib.redirect_stdout(io.StringIO()), \
                        contextlib.redirect_stderr(io.StringIO()) as errores:
                    codigo = main(["--archivo", str(self.archivo)])
        self.assertEqual(codigo, 1)
        self.assertIn("No pude guardar", errores.getvalue())


if __name__ == "__main__":
    unittest.main()
