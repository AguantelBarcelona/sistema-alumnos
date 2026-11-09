
"""!
@file app.py
@brief API de gestión de alumnos "Sistema Alumnos" (actividad OCY1102).
"""

import os
from flask import Flask, jsonify, request


## Aplicación Flask principal del sistema.
app = Flask(__name__)


## Base de datos de alumnos almacenada en memoria.
ALUMNOS = [
    {"id": 1, "nombre": "Ana Pérez", "carrera": "Ingeniería en Informática", "promedio": 6.1},
    {"id": 2, "nombre": "Benjamín Rojas", "carrera": "Ingeniería en Ciberseguridad", "promedio": 5.4},
    {"id": 3, "nombre": "Camila Soto", "carrera": "Analista Programador", "promedio": 6.8},
]


## Versión de la aplicación proporcionada por Jenkins mediante APP_VERSION.
VERSION = os.environ.get("APP_VERSION", "dev")


@app.route('/hello')
def hello():
    """!
    @brief Genera un mensaje de saludo.

    Obtiene el nombre desde el parámetro de consulta
    'name' de la URL.

    @return Cadena de texto con el saludo generado.
    """
    name = request.args.get('name')
    return f"Hello, {name}!"


@app.route('/health')
def health():
    """!
    @brief Comprueba el estado de salud de la API.

    @return Respuesta JSON que indica que el servicio está operativo.
    """
    return jsonify({"estado": "ok"})


@app.route('/version')
def version():
    """!
    @brief Consulta la versión actual de la aplicación.

    @return Respuesta JSON con el nombre y la versión del sistema.
    """
    return jsonify({"aplicacion": "Sistema Alumnos", "version": VERSION})


@app.route('/alumnos')
def listar_alumnos():
    """!
    @brief Obtiene la lista completa de alumnos.

    @return Respuesta JSON con todos los alumnos registrados.
    """
    return jsonify(ALUMNOS)


@app.route('/alumnos/<int:alumno_id>')
def obtener_alumno(alumno_id):
    """!
    @brief Busca un alumno utilizando su identificador.

    @param alumno_id Identificador numérico del alumno.
    @return Respuesta JSON con el alumno encontrado o error 404.
    """
    for alumno in ALUMNOS:
        if alumno["id"] == alumno_id:
            return jsonify(alumno)
    return jsonify({"error": "Alumno no encontrado"}), 404


@app.route('/alumnos', methods=['POST'])
def crear_alumno():
    """!
    @brief Registra un nuevo alumno en la base de datos en memoria.

    Valida el nombre y que el promedio esté entre 1.0 y 7.0.

    @return Respuesta JSON con el alumno creado y estado 201,
    o un mensaje de error con estado 400.
    """
    datos = request.get_json(silent=True) or {}
    nombre = str(datos.get("nombre", "")).strip()
    promedio = datos.get("promedio")

    if not nombre:
        return jsonify({"error": "El campo 'nombre' es obligatorio"}), 400

    if not isinstance(promedio, (int, float)) or not 1.0 <= promedio <= 7.0:
        return jsonify({"error": "El 'promedio' debe ser un número entre 1.0 y 7.0"}), 400

    nuevo = {
        "id": max(a["id"] for a in ALUMNOS) + 1,
        "nombre": nombre,
        "carrera": str(datos.get("carrera", "Sin carrera")),
        "promedio": promedio,
    }

    ALUMNOS.append(nuevo)
    return jsonify(nuevo), 201


def main():
    """!
    @brief Inicia el servidor Flask en modo de desarrollo.
    """
    app.run(debug=True)


if __name__ == '__main__':
    main()
