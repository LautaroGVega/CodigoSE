"""
Servidor HTTP local (WSGI) que sirve la interfaz web y la API JSON del motor.
Los archivos estáticos se leen desde la carpeta web/ junto a este módulo.
"""

import json
import os
from wsgiref.simple_server import make_server

from inference_engine import evaluar_caso
from knowledge_base import (
    EVIDENCIAS_DESCRIPCIONES,
    EVIDENCIAS_ETIQUETAS,
    HIPOTESIS_DESCRIPCIONES,
    HIPOTESIS_NOMBRES,
    MIN_EVIDENCIAS,
    PRIORS,
    PROBABILIDADES_CONDICIONALES,
    UMBRAL_CONFIANZA_ALTA,
    UMBRAL_INCERTIDUMBRE,
)
from test_cases import CASOS_DE_PRUEBA, ETAPAS_PROPAGACION

# Carpeta web/ relativa a este archivo (independiente del directorio de trabajo).
_DIR_PAQUETE = os.path.dirname(os.path.abspath(__file__))
_DIR_WEB = os.path.join(_DIR_PAQUETE, "web")

# Archivos estáticos permitidos (evita path traversal).
_ARCHIVOS_WEB_PERMITIDOS = frozenset({"index.html", "styles.css", "app.js"})


def _leer_archivo_web(nombre_archivo, tipo):
    """
    Lee un archivo desde web/ y devuelve bytes, o None si no existe o no está permitido.

    nombre_archivo: solo el nombre del archivo (ej. index.html).
    tipo: descripción MIME esperada (no usada para validación; sirve para documentar).
    """
    _ = tipo  # reservado para logs o extensiones futuras
    base = os.path.basename(nombre_archivo)
    if base not in _ARCHIVOS_WEB_PERMITIDOS:
        return None
    ruta = os.path.join(_DIR_WEB, base)
    try:
        with open(ruta, "rb") as archivo:
            return archivo.read()
    except OSError:
        return None


def _serializar_analisis_api(nombre_caso, evidencias_filtradas, resultado_esperado):
    """Convierte la salida de evaluar_caso a un dict JSON-friendly para la API web."""
    resultado = evaluar_caso(evidencias_filtradas, resultado_esperado=resultado_esperado)
    analisis = resultado["analisis"]
    ranking_json = [
        {
            "hipotesis": hipotesis,
            "nombre": HIPOTESIS_NOMBRES[hipotesis],
            "probabilidad": round(probabilidad, 6),
            "porcentaje": round(probabilidad * 100, 2),
        }
        for hipotesis, probabilidad in resultado["ranking"]
    ]
    return {
        "ok": True,
        "nombre_caso": nombre_caso,
        "evidencias": evidencias_filtradas,
        "evidencias_detalle": [
            {
                "id": ev,
                "etiqueta": EVIDENCIAS_ETIQUETAS.get(ev, ev),
            }
            for ev in evidencias_filtradas
        ],
        "diagnostico_codigo": resultado["diagnostico"],
        "diagnostico_texto": resultado["diagnostico_texto"],
        "motivo_h4": analisis.get("motivo_h4"),
        "nivel_confianza": analisis["nivel_confianza"],
        "diferencia": round(analisis["diferencia"], 6),
        "ranking": ranking_json,
        "reglas_activadas": resultado["reglas_activadas"],
        "recomendacion": resultado["recomendacion"],
        "validacion": resultado["validacion"],
        "razonamiento_aplicado": {
            "cantidad_evidencias": resultado["razonamiento_aplicado"]["cantidad_evidencias"],
            "metodo": resultado["razonamiento_aplicado"]["metodo"],
            "priors": resultado["razonamiento_aplicado"]["priors"],
            "diferencia_porcentaje": round(
                resultado["razonamiento_aplicado"]["diferencia_primera_segunda"] * 100, 2
            ),
            "criterios": resultado["razonamiento_aplicado"]["criterios"],
            "conclusion": resultado["razonamiento_aplicado"]["conclusion"],
        },
    }


def _filtrar_evidencias_solicitud(evidencias_crudas):
    """Valida lista de strings contra evidencias conocidas; sin duplicados."""
    if not isinstance(evidencias_crudas, list):
        return None
    conocidas = set(PROBABILIDADES_CONDICIONALES.keys())
    vistas = set()
    validas = []
    for item in evidencias_crudas:
        if not isinstance(item, str):
            return None
        if item in conocidas and item not in vistas:
            validas.append(item)
            vistas.add(item)
    return validas


def _respuesta_wsgi(start_response, status, cuerpo, tipo="application/json; charset=utf-8"):
    """Cabeceras HTTP + CORS mínimo para desarrollo local."""
    cabeceras = [
        ("Content-Type", tipo),
        ("Content-Length", str(len(cuerpo))),
        ("Access-Control-Allow-Origin", "*"),
        ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
        ("Access-Control-Allow-Headers", "Content-Type"),
    ]
    start_response(status, cabeceras)
    return [cuerpo]


def _leer_cuerpo_wsgi(environ):
    try:
        longitud = int(environ.get("CONTENT_LENGTH") or 0)
    except ValueError:
        longitud = 0
    if longitud <= 0:
        return b""
    return environ["wsgi.input"].read(longitud)


def aplicacion_wsgi(environ, start_response):
    """Aplicación WSGI: archivos estáticos y endpoints JSON."""
    metodo = environ.get("REQUEST_METHOD", "GET")
    ruta = environ.get("PATH_INFO", "/")

    if metodo == "OPTIONS":
        return _respuesta_wsgi(
            start_response,
            "204 No Content",
            b"",
            "text/plain; charset=utf-8",
        )

    if ruta == "/" and metodo == "GET":
        datos = _leer_archivo_web("index.html", "text/html")
        if datos is None:
            err = b"index.html no encontrado"
            return _respuesta_wsgi(start_response, "500 Internal Server Error", err)

        return _respuesta_wsgi(start_response, "200 OK", datos, "text/html; charset=utf-8")

    if ruta == "/styles.css" and metodo == "GET":
        datos = _leer_archivo_web("styles.css", "text/css")
        if datos is None:
            err = json.dumps({"ok": False, "error": "styles.css no encontrado"}).encode("utf-8")
            return _respuesta_wsgi(start_response, "404 Not Found", err)
        return _respuesta_wsgi(start_response, "200 OK", datos, "text/css; charset=utf-8")

    if ruta == "/app.js" and metodo == "GET":
        datos = _leer_archivo_web("app.js", "application/javascript")
        if datos is None:
            err = json.dumps({"ok": False, "error": "app.js no encontrado"}).encode("utf-8")
            return _respuesta_wsgi(start_response, "404 Not Found", err)
        return _respuesta_wsgi(
            start_response, "200 OK", datos, "application/javascript; charset=utf-8"
        )

    if ruta == "/api/meta" and metodo == "GET":
        evidencias = [
            {"id": k, "etiqueta": EVIDENCIAS_ETIQUETAS.get(k, k)}
            for k in PROBABILIDADES_CONDICIONALES.keys()
        ]
        casos = [
            {
                "id": num,
                "nombre": CASOS_DE_PRUEBA[num]["nombre"],
                "esperado": CASOS_DE_PRUEBA[num]["esperado"],
            }
            for num in sorted(CASOS_DE_PRUEBA.keys())
        ]
        cuerpo = json.dumps(
            {
                "evidencias": evidencias,
                "casos": casos,
                "hipotesis_descripciones": HIPOTESIS_DESCRIPCIONES,
                "evidencias_descripciones": EVIDENCIAS_DESCRIPCIONES,
                "priors": PRIORS,
                "probabilidades_condicionales": PROBABILIDADES_CONDICIONALES,
                "umbral_incertidumbre": UMBRAL_INCERTIDUMBRE,
                "umbral_confianza_alta": UMBRAL_CONFIANZA_ALTA,
                "min_evidencias": MIN_EVIDENCIAS,
            },
            ensure_ascii=False,
        ).encode("utf-8")
        return _respuesta_wsgi(start_response, "200 OK", cuerpo)

    if ruta.startswith("/api/caso/") and metodo == "GET":
        try:
            num = int(ruta.rstrip("/").split("/")[-1])
        except ValueError:
            err = json.dumps({"ok": False, "error": "id inválido"}).encode("utf-8")
            return _respuesta_wsgi(start_response, "400 Bad Request", err)
        if num not in CASOS_DE_PRUEBA:
            err = json.dumps({"ok": False, "error": "caso no encontrado"}).encode("utf-8")
            return _respuesta_wsgi(start_response, "404 Not Found", err)
        caso = CASOS_DE_PRUEBA[num]
        payload = _serializar_analisis_api(
            caso["nombre"],
            caso["evidencias"],
            caso["esperado"],
        )
        cuerpo = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        return _respuesta_wsgi(start_response, "200 OK", cuerpo)

    if ruta == "/api/analizar" and metodo == "POST":
        try:
            cuerpo_dict = json.loads(_leer_cuerpo_wsgi(environ).decode("utf-8") or "{}")
        except json.JSONDecodeError:
            err = json.dumps({"ok": False, "error": "JSON inválido"}).encode("utf-8")
            return _respuesta_wsgi(start_response, "400 Bad Request", err)
        evidencias = _filtrar_evidencias_solicitud(cuerpo_dict.get("evidencias"))
        if evidencias is None:
            err = json.dumps(
                {"ok": False, "error": "evidencias debe ser lista de strings"},
                ensure_ascii=False,
            ).encode("utf-8")
            return _respuesta_wsgi(start_response, "400 Bad Request", err)
        if len(evidencias) == 0:
            err = json.dumps(
                {"ok": False, "error": "Seleccione al menos una evidencia conocida."},
                ensure_ascii=False,
            ).encode("utf-8")
            return _respuesta_wsgi(start_response, "400 Bad Request", err)
        nombre = cuerpo_dict.get("nombre_caso") or "Caso manual"
        if not isinstance(nombre, str):
            nombre = "Caso manual"
        esperado = cuerpo_dict.get("esperado", None)
        if esperado is not None and esperado not in ("H1", "H2", "H3", "H4"):
            esperado = None
        payload = _serializar_analisis_api(nombre, evidencias, esperado)
        cuerpo = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        return _respuesta_wsgi(start_response, "200 OK", cuerpo)

    if ruta == "/api/propagacion" and metodo == "GET":
        etapas = []
        for i, evs in enumerate(ETAPAS_PROPAGACION, start=1):
            nombre = f"Propagación - Etapa {i}"
            res_eval = evaluar_caso(evs, resultado_esperado=None)
            analisis = res_eval["analisis"]
            ranking_json = [
                {
                    "hipotesis": hipotesis,
                    "nombre": HIPOTESIS_NOMBRES[hipotesis],
                    "probabilidad": round(probabilidad, 6),
                    "porcentaje": round(probabilidad * 100, 2),
                }
                for hipotesis, probabilidad in res_eval["ranking"]
            ]
            etapas.append(
                {
                    "nombre_caso": nombre,
                    "evidencias": evs,
                    "evidencias_detalle": [
                        {"id": ev, "etiqueta": EVIDENCIAS_ETIQUETAS.get(ev, ev)} for ev in evs
                    ],
                    "resultado": {
                        "diagnostico_texto": res_eval["diagnostico_texto"],
                        "nivel_confianza": analisis["nivel_confianza"],
                        "ranking": ranking_json,
                    },
                }
            )
        cuerpo = json.dumps({"etapas": etapas}, ensure_ascii=False).encode("utf-8")
        return _respuesta_wsgi(start_response, "200 OK", cuerpo)

    notfound = json.dumps({"ok": False, "error": "no encontrado"}).encode("utf-8")
    return _respuesta_wsgi(start_response, "404 Not Found", notfound)


def ejecutar_servidor_web(host="127.0.0.1", puerto=8765):
    """Inicia el servidor HTTP local."""
    servidor = make_server(host, puerto, aplicacion_wsgi)
    print("Sistema Experto Edilicio — interfaz web")
    print(f"Abre en el navegador: http://{host}:{puerto}/")
    print("Ctrl+C para detener el servidor.\n")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
