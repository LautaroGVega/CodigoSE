"""
Sistema Experto probabilístico simplificado para mantenimiento edilicio.

Este programa implementa un modelo Naive Bayes simplificado para diagnóstico
preliminar en cubiertas, techos metálicos e impermeabilizaciones.

Interfaz: servidor web local (solo biblioteca estándar). La inferencia vive en
Python; el navegador muestra la UI.
"""

import argparse
import json
from wsgiref.simple_server import make_server


# -----------------------------
# Base de conocimiento principal
# -----------------------------

# Nombres descriptivos de hipótesis.
HIPOTESIS_NOMBRES = {
    "H1": "Dilatación de materiales por temperatura",
    "H2": "Falla de impermeabilización",
    "H3": "Problema de desagüe o acumulación de agua",
}

# Priors P(H).
PRIORS = {
    "H1": 0.35,
    "H2": 0.40,
    "H3": 0.25,
}

# Parámetros de decisión del sistema experto.
UMBRAL_INCERTIDUMBRE = 0.15
UMBRAL_CONFIANZA_ALTA = 0.25
MIN_EVIDENCIAS = 2

# Probabilidades condicionales P(E|H) por evidencia.
PROBABILIDADES_CONDICIONALES = {
    "techo_metalico": {"H1": 0.80, "H2": 0.45, "H3": 0.25},
    "exposicion_alta_sol": {"H1": 0.90, "H2": 0.50, "H3": 0.20},
    "cambios_termicos": {"H1": 0.85, "H2": 0.45, "H3": 0.15},
    "fisuras_visibles": {"H1": 0.80, "H2": 0.60, "H3": 0.20},
    "separacion_juntas": {"H1": 0.75, "H2": 0.70, "H3": 0.25},
    "aparece_con_calor": {"H1": 0.90, "H2": 0.35, "H3": 0.10},
    "membrana_agrietada_o_levantada": {"H1": 0.50, "H2": 0.90, "H3": 0.35},
    "sellador_envejecido_o_abierto": {"H1": 0.60, "H2": 0.80, "H3": 0.25},
    "humedad_visible": {"H1": 0.65, "H2": 0.80, "H3": 0.65},
    "filtracion_goteo": {"H1": 0.40, "H2": 0.90, "H3": 0.70},
    "lluvia_reciente": {"H1": 0.30, "H2": 0.80, "H3": 0.75},
    "acumulacion_agua": {"H1": 0.20, "H2": 0.45, "H3": 0.90},
    "desagues_obstruidos": {"H1": 0.15, "H2": 0.35, "H3": 0.90},
}

# Reglas explicativas del subsistema de explicación.
REGLAS_EXPLICATIVAS = {
    "techo_metalico": {
        "codigo": "R1",
        "explicacion": (
            "Se observó techo metálico. Esta evidencia favorece principalmente "
            "la dilatación térmica."
        ),
    },
    "exposicion_alta_sol": {
        "codigo": "R2",
        "explicacion": (
            "La alta exposición al sol favorece la hipótesis de dilatación de materiales."
        ),
    },
    "cambios_termicos": {
        "codigo": "R3",
        "explicacion": (
            "Los cambios térmicos bruscos pueden producir expansión y contracción "
            "de materiales."
        ),
    },
    "fisuras_visibles": {
        "codigo": "R4",
        "explicacion": (
            "Las fisuras visibles pueden relacionarse con dilatación o fallas "
            "de impermeabilización."
        ),
    },
    "separacion_juntas": {
        "codigo": "R5",
        "explicacion": (
            "La separación de juntas puede indicar movimiento de materiales o "
            "falla de sellado."
        ),
    },
    "aparece_con_calor": {
        "codigo": "R6",
        "explicacion": (
            "Si el problema aparece o empeora con calor, aumenta la probabilidad "
            "de dilatación térmica."
        ),
    },
    "membrana_agrietada_o_levantada": {
        "codigo": "R7",
        "explicacion": (
            "Una membrana agrietada o levantada favorece falla de impermeabilización."
        ),
    },
    "sellador_envejecido_o_abierto": {
        "codigo": "R8",
        "explicacion": "El sellador deteriorado puede permitir ingreso de agua.",
    },
    "humedad_visible": {
        "codigo": "R9",
        "explicacion": (
            "La humedad visible es un síntoma general que puede aparecer en "
            "varias patologías."
        ),
    },
    "filtracion_goteo": {
        "codigo": "R10",
        "explicacion": (
            "La filtración o goteo favorece principalmente falla de impermeabilización "
            "o problemas de escurrimiento."
        ),
    },
    "lluvia_reciente": {
        "codigo": "R11",
        "explicacion": (
            "Si el problema aparece después de lluvias, puede relacionarse con "
            "impermeabilización o desagüe."
        ),
    },
    "acumulacion_agua": {
        "codigo": "R12",
        "explicacion": "La acumulación de agua favorece problema de desagüe.",
    },
    "desagues_obstruidos": {
        "codigo": "R13",
        "explicacion": (
            "Los desagües obstruidos favorecen problema de desagüe o acumulación."
        ),
    },
}

# Recomendaciones por diagnóstico.
RECOMENDACIONES = {
    "H1": (
        "Revisar fisuras, juntas y selladores. Se recomienda utilizar materiales "
        "elásticos o impermeabilizantes flexibles que absorban los movimientos "
        "térmicos."
    ),
    "H2": (
        "Inspeccionar membranas, selladores, uniones y puntos de ingreso de agua. "
        "Puede requerirse reparación o refuerzo de impermeabilización."
    ),
    "H3": (
        "Revisar pendientes, canaletas, desagües y zonas con acumulación de agua. "
        "Limpiar obstrucciones y corregir el escurrimiento."
    ),
    "H4": (
        "La evidencia no permite establecer una causa principal clara. Se recomienda "
        "cargar más datos o solicitar una inspección técnica."
    ),
}

# Etiquetas amigables para mostrar evidencias en UI/UX.
EVIDENCIAS_ETIQUETAS = {
    "techo_metalico": "Techo metálico",
    "exposicion_alta_sol": "Exposición alta al sol",
    "cambios_termicos": "Cambios térmicos",
    "fisuras_visibles": "Fisuras visibles",
    "separacion_juntas": "Separación de juntas",
    "aparece_con_calor": "El problema aparece con calor",
    "membrana_agrietada_o_levantada": "Membrana agrietada o levantada",
    "sellador_envejecido_o_abierto": "Sellador envejecido o abierto",
    "humedad_visible": "Humedad visible",
    "filtracion_goteo": "Filtración / goteo",
    "lluvia_reciente": "Lluvia reciente",
    "acumulacion_agua": "Acumulación de agua",
    "desagues_obstruidos": "Desagües obstruidos",
}

# Descripción pedagógica de las hipótesis para la guía web.
HIPOTESIS_DESCRIPCIONES = {
    "H1": {
        "titulo": "Dilatación de materiales por temperatura",
        "descripcion": (
            "Representa daños generados por expansión y contracción de materiales "
            "debido a calor, exposición solar o cambios térmicos. Puede provocar "
            "fisuras, separación de juntas y deterioro de selladores."
        ),
        "evidencias_clave": [
            "techo_metalico",
            "exposicion_alta_sol",
            "cambios_termicos",
            "fisuras_visibles",
            "separacion_juntas",
            "aparece_con_calor",
        ],
    },
    "H2": {
        "titulo": "Falla de impermeabilización",
        "descripcion": (
            "Representa una pérdida de capacidad impermeabilizante en membranas, "
            "selladores, uniones o juntas. Puede permitir ingreso de agua y producir "
            "humedad o filtraciones."
        ),
        "evidencias_clave": [
            "membrana_agrietada_o_levantada",
            "sellador_envejecido_o_abierto",
            "humedad_visible",
            "filtracion_goteo",
            "lluvia_reciente",
            "separacion_juntas",
        ],
    },
    "H3": {
        "titulo": "Problema de desagüe o acumulación de agua",
        "descripcion": (
            "Representa fallas de escurrimiento, pendientes, canaletas o desagües. "
            "Puede provocar acumulación de agua, humedad y filtraciones luego de lluvias."
        ),
        "evidencias_clave": [
            "lluvia_reciente",
            "acumulacion_agua",
            "desagues_obstruidos",
            "filtracion_goteo",
            "humedad_visible",
        ],
    },
    "H4": {
        "titulo": "Otro / diagnóstico incierto",
        "descripcion": (
            "No es una hipótesis técnica calculada por probabilidad. Es una salida de "
            "control cuando la evidencia es insuficiente o cuando las probabilidades de "
            "las hipótesis principales son muy cercanas."
        ),
        "evidencias_clave": [],
    },
}

# Descripción de variables/evidencias para la guía web.
EVIDENCIAS_DESCRIPCIONES = {
    "techo_metalico": {
        "etiqueta": "Techo metálico",
        "descripcion": (
            "Indica que la cubierta afectada es metálica, material sensible a expansión "
            "y contracción por temperatura."
        ),
        "favorece": ["H1"],
    },
    "exposicion_alta_sol": {
        "etiqueta": "Exposición alta al sol",
        "descripcion": (
            "Refiere a radiación solar intensa y sostenida, lo que incrementa la "
            "temperatura superficial de la cubierta."
        ),
        "favorece": ["H1"],
    },
    "cambios_termicos": {
        "etiqueta": "Cambios térmicos",
        "descripcion": (
            "Se observan variaciones térmicas marcadas entre día y noche o entre "
            "estaciones, favoreciendo ciclos de dilatación/contracción."
        ),
        "favorece": ["H1"],
    },
    "fisuras_visibles": {
        "etiqueta": "Fisuras visibles",
        "descripcion": (
            "Presencia de grietas o microfisuras en superficies o encuentros "
            "constructivos."
        ),
        "favorece": ["H1", "H2"],
    },
    "separacion_juntas": {
        "etiqueta": "Separación de juntas",
        "descripcion": (
            "Aberturas en juntas o encuentros entre materiales que pueden perder "
            "continuidad de sellado."
        ),
        "favorece": ["H1", "H2"],
    },
    "aparece_con_calor": {
        "etiqueta": "El problema aparece con calor",
        "descripcion": (
            "La manifestación se activa o agrava cuando sube la temperatura ambiente "
            "o la radiación solar."
        ),
        "favorece": ["H1"],
    },
    "membrana_agrietada_o_levantada": {
        "etiqueta": "Membrana agrietada o levantada",
        "descripcion": (
            "Se observa deterioro físico de la membrana impermeabilizante, con pérdida "
            "de adherencia o continuidad."
        ),
        "favorece": ["H2"],
    },
    "sellador_envejecido_o_abierto": {
        "etiqueta": "Sellador envejecido o abierto",
        "descripcion": (
            "Selladores rígidos, fisurados o desprendidos que facilitan ingreso de agua."
        ),
        "favorece": ["H2"],
    },
    "humedad_visible": {
        "etiqueta": "Humedad visible",
        "descripcion": (
            "Manchas, ampollamientos o desprendimientos asociados a presencia de agua "
            "en la envolvente."
        ),
        "favorece": ["H1", "H2", "H3"],
    },
    "filtracion_goteo": {
        "etiqueta": "Filtración / goteo",
        "descripcion": (
            "Ingreso de agua en forma localizada o continua, especialmente en lluvia."
        ),
        "favorece": ["H2", "H3"],
    },
    "lluvia_reciente": {
        "etiqueta": "Lluvia reciente",
        "descripcion": (
            "El síntoma aparece luego de precipitaciones, reforzando la relación con "
            "ingreso y escurrimiento del agua."
        ),
        "favorece": ["H2", "H3"],
    },
    "acumulacion_agua": {
        "etiqueta": "Acumulación de agua",
        "descripcion": (
            "Se detectan charcos o permanencia de agua por drenaje insuficiente."
        ),
        "favorece": ["H3"],
    },
    "desagues_obstruidos": {
        "etiqueta": "Desagües obstruidos",
        "descripcion": (
            "Canaletas o desagües con suciedad u obstrucciones que dificultan "
            "el escurrimiento correcto."
        ),
        "favorece": ["H3"],
    },
}


# Casos de prueba requeridos por la consigna.
CASOS_DE_PRUEBA = {
    1: {
        "nombre": "Caso 1 - Dilatación térmica",
        "evidencias": [
            "techo_metalico",
            "exposicion_alta_sol",
            "cambios_termicos",
            "fisuras_visibles",
            "separacion_juntas",
            "aparece_con_calor",
            "humedad_visible",
        ],
        "esperado": "H1",
    },
    2: {
        "nombre": "Caso 2 - Falla de impermeabilización",
        "evidencias": [
            "membrana_agrietada_o_levantada",
            "sellador_envejecido_o_abierto",
            "humedad_visible",
            "filtracion_goteo",
            "lluvia_reciente",
            "separacion_juntas",
        ],
        "esperado": "H2",
    },
    3: {
        "nombre": "Caso 3 - Problema de desagüe",
        "evidencias": [
            "lluvia_reciente",
            "acumulacion_agua",
            "desagues_obstruidos",
            "humedad_visible",
            "filtracion_goteo",
        ],
        "esperado": "H3",
    },
    4: {
        "nombre": "Caso 4 - Caso mixto dilatación + impermeabilización",
        "evidencias": [
            "exposicion_alta_sol",
            "fisuras_visibles",
            "separacion_juntas",
            "membrana_agrietada_o_levantada",
            "humedad_visible",
            "filtracion_goteo",
        ],
        "esperado": "H2",  # También puede ser discutible con confianza media.
    },
    5: {
        "nombre": "Caso 5 - Evidencia insuficiente",
        "evidencias": ["humedad_visible"],
        "esperado": "H4",
    },
    6: {
        "nombre": "Caso 6 - Caso ambiguo",
        "evidencias": [
            "fisuras_visibles",
            "separacion_juntas",
            "humedad_visible",
        ],
        "esperado": "H4",
    },
}


def calcular_probabilidades(evidencias_presentes):
    """
    Calcula probabilidades finales de H1, H2 y H3 mediante Naive Bayes simplificado.

    Fórmula usada:
      puntaje(H) = P(H) * Π P(E|H) solo para evidencias presentes.
      probabilidad_final(H) = puntaje(H) / sumatoria_de_puntajes.

    Importante:
    - No se usan evidencias ausentes como complemento (1 - P(E|H)).
    """
    puntajes = {}

    # Se calcula un puntaje por cada hipótesis principal.
    for hipotesis, prior in PRIORS.items():
        puntaje = prior
        for evidencia in evidencias_presentes:
            puntaje *= PROBABILIDADES_CONDICIONALES[evidencia][hipotesis]
        puntajes[hipotesis] = puntaje

    suma_puntajes = sum(puntajes.values())

    # Evita división por cero ante un caso extremo.
    if suma_puntajes == 0:
        cantidad = len(PRIORS)
        return {h: 1.0 / cantidad for h in PRIORS}

    probabilidades = {
        hipotesis: puntaje / suma_puntajes for hipotesis, puntaje in puntajes.items()
    }
    return probabilidades


def determinar_diagnostico(probabilidades, cantidad_evidencias):
    """
    Determina diagnóstico final y nivel de confianza según reglas del enunciado.

    Reglas de salida especial H4:
    - Si hay menos de MIN_EVIDENCIAS evidencias => H4 por evidencia insuficiente.
    - Si diferencia entre 1ra y 2da hipótesis es menor a UMBRAL_INCERTIDUMBRE => H4 incierto.
    """
    ranking = sorted(probabilidades.items(), key=lambda item: item[1], reverse=True)
    mejor_hipotesis, prob_primera = ranking[0]
    _, prob_segunda = ranking[1]
    diferencia = prob_primera - prob_segunda

    if cantidad_evidencias < MIN_EVIDENCIAS:
        return {
            "diagnostico": "H4",
            "motivo_h4": "evidencia insuficiente",
            "nivel_confianza": "Incierto",
            "diferencia": diferencia,
            "ranking": ranking,
        }

    if diferencia < UMBRAL_INCERTIDUMBRE:
        return {
            "diagnostico": "H4",
            "motivo_h4": "diagnóstico incierto",
            "nivel_confianza": "Bajo / incierto",
            "diferencia": diferencia,
            "ranking": ranking,
        }

    if diferencia >= UMBRAL_CONFIANZA_ALTA:
        nivel = "Alto"
    else:
        nivel = "Medio"

    return {
        "diagnostico": mejor_hipotesis,
        "motivo_h4": None,
        "nivel_confianza": nivel,
        "diferencia": diferencia,
        "ranking": ranking,
    }


def obtener_recomendacion(diagnostico):
    """
    Retorna texto de recomendación según diagnóstico.
    H4 representa caso incierto u otra causa no concluyente.
    """
    if diagnostico in RECOMENDACIONES:
        return RECOMENDACIONES[diagnostico]
    return RECOMENDACIONES["H4"]


def evaluar_caso(evidencias_presentes, resultado_esperado=None):
    """
    Evalúa un conjunto de evidencias y retorna todos los datos de salida
    en una estructura reutilizable para consola y para interfaz gráfica.
    """
    probabilidades = calcular_probabilidades(evidencias_presentes)
    analisis = determinar_diagnostico(probabilidades, len(evidencias_presentes))
    diagnostico = analisis["diagnostico"]
    ranking = analisis["ranking"]
    recomendacion = obtener_recomendacion(diagnostico)

    if diagnostico == "H4":
        if analisis["motivo_h4"] == "evidencia insuficiente":
            diagnostico_texto = "Otro / evidencia insuficiente"
        else:
            diagnostico_texto = "Otro / diagnóstico incierto"
    else:
        diagnostico_texto = f"{diagnostico} - {HIPOTESIS_NOMBRES[diagnostico]}"

    validacion = None
    if resultado_esperado is not None:
        if resultado_esperado == "H4":
            if diagnostico == "H4":
                validacion = (
                    "Resultado razonable: el caso era insuficiente/ambiguo y el sistema "
                    "indicó diagnóstico incierto."
                )
            else:
                validacion = (
                    "Resultado discutible: se esperaba incertidumbre, pero el sistema "
                    "logró inclinarse por una hipótesis principal."
                )
        elif diagnostico == resultado_esperado:
            validacion = (
                f"Resultado razonable: el diagnóstico ({diagnostico}) coincide con "
                "lo esperado."
            )
        elif analisis["nivel_confianza"] in ("Medio", "Bajo / incierto", "Incierto"):
            validacion = (
                "Resultado discutible pero razonable: el caso presenta mezcla de "
                "evidencias o baja confianza."
            )
        else:
            validacion = (
                f"Resultado no esperado: se esperaba {resultado_esperado} y el "
                f"sistema obtuvo {diagnostico}."
            )

    reglas_activadas = []
    for evidencia in evidencias_presentes:
        regla = REGLAS_EXPLICATIVAS.get(evidencia)
        if regla:
            reglas_activadas.append(
                {
                    "evidencia": evidencia,
                    "codigo": regla["codigo"],
                    "explicacion": regla["explicacion"],
                }
            )

    if diagnostico == "H4":
        frase_final = (
            "El sistema no eligió una hipótesis técnica principal porque la evidencia "
            "fue insuficiente o las probabilidades resultaron demasiado cercanas."
        )
    else:
        frase_final = (
            f"El sistema eligió {diagnostico} porque obtuvo la mayor probabilidad "
            "posterior y la diferencia respecto de la segunda hipótesis superó el "
            "umbral mínimo de incertidumbre."
        )

    razonamiento_aplicado = {
        "cantidad_evidencias": len(evidencias_presentes),
        "metodo": "Naive Bayes simplificado",
        "priors": PRIORS.copy(),
        "diferencia_primera_segunda": analisis["diferencia"],
        "criterios": [
            (
                f"menos de {MIN_EVIDENCIAS} evidencias => H4 evidencia insuficiente"
            ),
            (
                f"diferencia menor a {UMBRAL_INCERTIDUMBRE:.2f} => H4 diagnóstico incierto"
            ),
            (
                f"diferencia mayor o igual a {UMBRAL_CONFIANZA_ALTA:.2f} => confianza alta"
            ),
            "caso contrario => confianza media",
        ],
        "conclusion": frase_final,
    }

    return {
        "evidencias_presentes": evidencias_presentes,
        "analisis": analisis,
        "diagnostico": diagnostico,
        "diagnostico_texto": diagnostico_texto,
        "ranking": ranking,
        "recomendacion": recomendacion,
        "reglas_activadas": reglas_activadas,
        "validacion": validacion,
        "razonamiento_aplicado": razonamiento_aplicado,
    }


def mostrar_resultado(nombre_caso, evidencias_presentes, resultado_esperado=None):
    """
    Ejecuta inferencia de un caso y muestra salida completa por consola:
    - Evidencias
    - Reglas activadas
    - Ranking
    - Diagnóstico
    - Confianza
    - Recomendación
    - Validación breve
    """
    resultado = evaluar_caso(evidencias_presentes, resultado_esperado=resultado_esperado)
    analisis = resultado["analisis"]
    ranking = resultado["ranking"]

    print("\n========================================")
    print(f"CASO: {nombre_caso}")
    print("========================================\n")

    print("Evidencias seleccionadas:")
    for evidencia in evidencias_presentes:
        print(f"- {evidencia}")

    print("\nReglas activadas:")
    for regla in resultado["reglas_activadas"]:
        print(f"- {regla['codigo']}: {regla['explicacion']}")

    print("\nRanking de hipótesis:")
    for indice, (hipotesis, probabilidad) in enumerate(ranking, start=1):
        nombre = HIPOTESIS_NOMBRES[hipotesis]
        print(f"{indice}. {hipotesis} - {nombre}: {probabilidad * 100:.2f}%")

    print("\nDiagnóstico:")
    print(resultado["diagnostico_texto"])

    print("\nNivel de confianza:")
    print(analisis["nivel_confianza"])

    print("\nRecomendación:")
    print(resultado["recomendacion"])

    if resultado["validacion"] is not None:
        print("\nValidación del caso:")
        print(resultado["validacion"])

    print("\n" + "=" * 40 + "\n")


def cargar_caso_manual():
    """
    Permite al usuario seleccionar manualmente evidencias por consola.
    Incluye validación básica de entradas y evita duplicados.
    """
    evidencias_disponibles = list(PROBABILIDADES_CONDICIONALES.keys())

    print("\n--- Carga manual de caso ---")
    print("Seleccione evidencias ingresando números separados por coma.")
    print("Ejemplo: 1,3,5")
    print("Evidencias disponibles:")

    for indice, evidencia in enumerate(evidencias_disponibles, start=1):
        print(f"{indice}. {evidencia}")

    while True:
        try:
            entrada = input("\nIngrese su selección: ").strip()
        except EOFError:
            # Permite que el programa termine sin traceback si no hay stdin.
            print("\nEntrada finalizada (EOF). Volviendo al menú.")
            return
        if not entrada:
            print("Entrada vacía. Intente nuevamente.")
            continue

        partes = [p.strip() for p in entrada.split(",") if p.strip()]
        indices = []
        valido = True

        for parte in partes:
            if not parte.isdigit():
                valido = False
                break
            numero = int(parte)
            if numero < 1 or numero > len(evidencias_disponibles):
                valido = False
                break
            indices.append(numero)

        if not valido:
            print("Selección inválida. Use números válidos separados por coma.")
            continue

        # Se eliminan duplicados preservando orden.
        vistos = set()
        evidencias_seleccionadas = []
        for numero in indices:
            evidencia = evidencias_disponibles[numero - 1]
            if evidencia not in vistos:
                evidencias_seleccionadas.append(evidencia)
                vistos.add(evidencia)

        if not evidencias_seleccionadas:
            print("Debe seleccionar al menos una evidencia.")
            continue

        mostrar_resultado("Caso manual", evidencias_seleccionadas, resultado_esperado=None)
        break


def demostrar_propagacion_evidencias():
    """
    Demuestra propagación de evidencia en 4 etapas.
    En cada etapa se agrega nueva evidencia y se observa cambio en probabilidades
    y diagnóstico.
    """
    etapas = [
        ["humedad_visible"],
        ["humedad_visible", "exposicion_alta_sol"],
        ["humedad_visible", "exposicion_alta_sol", "fisuras_visibles"],
        [
            "humedad_visible",
            "exposicion_alta_sol",
            "fisuras_visibles",
            "aparece_con_calor",
        ],
    ]

    print("\n========================================")
    print("DEMONSTRACIÓN: Propagación de evidencias")
    print("========================================\n")

    for i, evidencias in enumerate(etapas, start=1):
        print(f"--- Etapa {i} ---")
        mostrar_resultado(
            nombre_caso=f"Propagación - Etapa {i}",
            evidencias_presentes=evidencias,
            resultado_esperado=None,
        )


def construir_texto_resultado(nombre_caso, resultado):
    """
    Construye una salida textual amigable para mostrar en la interfaz.
    """
    lineas = []
    lineas.append("========================================")
    lineas.append(f"CASO: {nombre_caso}")
    lineas.append("========================================")
    lineas.append("")
    lineas.append("Evidencias seleccionadas:")
    for evidencia in resultado["evidencias_presentes"]:
        etiqueta = EVIDENCIAS_ETIQUETAS.get(evidencia, evidencia)
        lineas.append(f"- {etiqueta} ({evidencia})")

    lineas.append("")
    lineas.append("Reglas activadas:")
    for regla in resultado["reglas_activadas"]:
        lineas.append(f"- {regla['codigo']}: {regla['explicacion']}")

    lineas.append("")
    lineas.append("Ranking de hipótesis:")
    for indice, (hipotesis, probabilidad) in enumerate(resultado["ranking"], start=1):
        lineas.append(
            f"{indice}. {hipotesis} - {HIPOTESIS_NOMBRES[hipotesis]}: "
            f"{probabilidad * 100:.2f}%"
        )

    lineas.append("")
    lineas.append("Diagnóstico:")
    lineas.append(resultado["diagnostico_texto"])

    lineas.append("")
    lineas.append("Nivel de confianza:")
    lineas.append(resultado["analisis"]["nivel_confianza"])

    lineas.append("")
    lineas.append("Recomendación:")
    lineas.append(resultado["recomendacion"])

    if resultado["validacion"] is not None:
        lineas.append("")
        lineas.append("Validación del caso:")
        lineas.append(resultado["validacion"])

    lineas.append("")
    lineas.append("========================================")
    return "\n".join(lineas)


def construir_texto_propagacion():
    """
    Crea un reporte textual de propagación de evidencias en 4 etapas.
    """
    etapas = [
        ["humedad_visible"],
        ["humedad_visible", "exposicion_alta_sol"],
        ["humedad_visible", "exposicion_alta_sol", "fisuras_visibles"],
        [
            "humedad_visible",
            "exposicion_alta_sol",
            "fisuras_visibles",
            "aparece_con_calor",
        ],
    ]
    bloques = []
    bloques.append("DEMONSTRACIÓN: PROPAGACIÓN DE EVIDENCIAS")
    bloques.append("")
    for i, evidencias in enumerate(etapas, start=1):
        nombre = f"Propagación - Etapa {i}"
        resultado = evaluar_caso(evidencias, resultado_esperado=None)
        bloques.append(construir_texto_resultado(nombre, resultado))
        bloques.append("")
    return "\n".join(bloques)


def _serializar_analisis_api(nombre_caso, evidencias_filtradas, resultado_esperado):
    """
    Convierte la salida de evaluar_caso a un dict JSON-friendly para la API web.
    """
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
    """
    Valida y ordena evidencias conocidas para evitar entradas inválidas en la API.
    """
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
    """Genera cabeceras CORS mínimas para desarrollo local."""
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


def _html_interfaz_web():
    """
    Página única: UI moderna (HTML/CSS/JS) sin dependencias externas.
    Consume /api/meta, POST /api/analizar, GET /api/caso/<n>, GET /api/propagacion.
    """
    return """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Sistema Experto Edilicio</title>
  <style>
    :root {
      --surface: #1a2332;
      --surface2: #243044;
      --surface3: #1f2a3d;
      --text: #e8ecf1;
      --muted: #9aa8b8;
      --accent: #3d9ee5;
      --accent2: #5ad4a8;
      --warn: #f0b429;
      --danger: #e85d75;
      --radius: 12px;
      --shadow: 0 8px 32px rgba(0,0,0,.35);
      font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0; min-height: 100vh;
      background: linear-gradient(160deg, #0b0f14 0%, #15202b 50%, #0f1419 100%);
      color: var(--text);
    }
    .wrap { max-width: 1240px; margin: 0 auto; padding: 24px 20px 48px; }
    .panel {
      background: var(--surface);
      border-radius: var(--radius);
      border: 1px solid rgba(255,255,255,.06);
      box-shadow: var(--shadow);
      padding: 20px;
    }
    header.hero {
      padding: 28px 24px;
      background: linear-gradient(135deg, var(--surface) 0%, var(--surface2) 100%);
      margin-bottom: 18px;
    }
    header.hero h1 { margin: 0 0 8px; font-size: 1.5rem; }
    header.hero p { margin: 0; color: var(--muted); line-height: 1.55; max-width: 80ch; }
    .badge {
      display: inline-block; margin-top: 10px; padding: 4px 10px; border-radius: 999px;
      font-size: .75rem; font-weight: 600; background: rgba(61,158,229,.15); color: var(--accent);
    }
    .guide { margin-bottom: 18px; }
    .guide h2 { margin: 0 0 12px; font-size: 1.08rem; }
    .guide-grid { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 14px; }
    .guide-card {
      background: var(--surface3); border: 1px solid rgba(255,255,255,.07);
      border-radius: 10px; padding: 14px;
    }
    .guide-card h3 { margin: 0 0 8px; font-size: .95rem; color: #cde8ff; }
    .mini-list { margin: 0; padding-left: 18px; color: var(--muted); font-size: .84rem; line-height: 1.45; }
    .formula {
      margin-top: 8px; padding: 10px; border-radius: 8px; font-family: Consolas, monospace;
      font-size: .82rem; background: rgba(0,0,0,.22); color: #d4efff;
    }
    .hyp-grid, .ev-info-grid {
      display: grid; grid-template-columns: repeat(auto-fill, minmax(250px,1fr)); gap: 10px;
    }
    .hyp-card, .ev-card {
      background: rgba(0,0,0,.18); border: 1px solid rgba(255,255,255,.06);
      border-radius: 8px; padding: 10px;
    }
    .hyp-card h4, .ev-card h4 { margin: 0 0 6px; font-size: .88rem; color: #d8ecff; }
    .ev-card p, .hyp-card p { margin: 0; font-size: .8rem; color: var(--muted); line-height: 1.45; }
    .tag-list { margin-top: 8px; display: flex; flex-wrap: wrap; gap: 6px; }
    .tag {
      font-size: .72rem; padding: 2px 7px; border-radius: 999px; border: 1px solid rgba(255,255,255,.14);
      color: #cbe3ff; background: rgba(61,158,229,.12);
    }
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    .panel h2 { margin: 0 0 16px; font-size: 1.05rem; display: flex; align-items: center; gap: 8px; }
    .btn-row { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
    button {
      cursor: pointer; border: none; border-radius: 8px;
      padding: 10px 14px; font-weight: 600; font-size: .86rem;
      background: linear-gradient(180deg, #4aa8ef, var(--accent)); color: #061018;
      transition: transform .12s, filter .12s;
    }
    button:hover { filter: brightness(1.08); transform: translateY(-1px); }
    button.secondary { background: var(--surface2); color: var(--text); border: 1px solid rgba(255,255,255,.1); }
    button.ghost { background: transparent; color: var(--muted); border: 1px dashed rgba(255,255,255,.15); }
    .evid-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px,1fr)); gap: 10px; max-height: 430px; overflow-y: auto; }
    .evid-item { display:flex; gap:10px; padding:10px 12px; border-radius:8px; background: rgba(0,0,0,.2); border: 1px solid rgba(255,255,255,.05);}
    .evid-item input { margin-top: 4px; accent-color: var(--accent);}
    .evid-item label { font-size:.84rem; line-height:1.35; cursor:pointer; color:#d8e3ef;}
    .evid-item code { display:block; font-size:.72rem; color:var(--muted); margin-top:4px;}
    .result-header { display:flex; flex-wrap:wrap; gap:12px; align-items:center; justify-content:space-between; margin-bottom: 14px;}
    .diag-box { padding: 14px 16px; border-radius: 8px; background: rgba(61,158,229,.12); border:1px solid rgba(61,158,229,.25); font-size: .94rem; line-height: 1.45;}
    .conf-pill { padding:6px 12px; border-radius:999px; font-size:.78rem; font-weight:700; text-transform: uppercase; letter-spacing:.04em; }
    .conf-alto { background: rgba(90,212,168,.2); color: var(--accent2); }
    .conf-medio { background: rgba(240,180,41,.18); color: var(--warn); }
    .conf-bajo { background: rgba(232,93,117,.18); color: var(--danger); }
    .conf-incierto { background: rgba(154,168,184,.15); color: var(--muted); }
    .bars { display:flex; flex-direction:column; gap:12px; margin: 16px 0; }
    .bar-row { display:grid; grid-template-columns: 120px 1fr 52px; gap:10px; align-items:center; font-size:.82rem; }
    .bar-track { height:10px; border-radius:999px; background: rgba(255,255,255,.08); overflow:hidden; }
    .bar-fill { height:100%; border-radius:999px; background: linear-gradient(90deg,var(--accent),var(--accent2)); transition: width .45s ease; }
    .bar-fill.h2 { background: linear-gradient(90deg,#c084fc,#818cf8); }
    .bar-fill.h3 { background: linear-gradient(90deg,#fb923c,#f472b6); }
    .rules { margin:0; padding-left:18px; color:var(--muted); font-size:.86rem; line-height:1.5; }
    .rules li { margin-bottom:6px; }
    .reco, .razonamiento {
      margin-top: 14px; padding: 12px; border-radius: 8px; font-size: .86rem; line-height: 1.55;
      border: 1px solid rgba(255,255,255,.1);
    }
    .reco { background: rgba(90,212,168,.08); border-color: rgba(90,212,168,.2); }
    .razonamiento { background: rgba(61,158,229,.08); border-color: rgba(61,158,229,.2); }
    .razonamiento ul { margin: 8px 0 0; padding-left: 18px; color: var(--muted); }
    .val-box { margin-top: 12px; padding: 10px; border-radius: 8px; font-size: .84rem; background: rgba(0,0,0,.2); color: var(--muted); border-left: 3px solid var(--accent); }
    .prop-stage { margin-bottom: 18px; padding-bottom: 18px; border-bottom: 1px solid rgba(255,255,255,.06); }
    .prop-stage:last-child { border-bottom:0; margin-bottom:0; padding-bottom:0; }
    .empty-state { color: var(--muted); font-size:.9rem; text-align:center; padding: 32px 16px; }
    .loading { opacity:.55; pointer-events:none; }
    footer { margin-top: 30px; text-align:center; color: var(--muted); font-size: .78rem; }
    @media (max-width: 980px) { .grid-2, .guide-grid { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <div class="wrap">
    <header class="hero panel">
      <h1>Sistema experto probabilístico — Mantenimiento edilicio</h1>
      <p>Diagnóstico preliminar de cubiertas y techos usando <strong>Naive Bayes simplificado</strong>. Marca evidencias observadas o ejecuta casos predefinidos; la inferencia se realiza en <strong>Python</strong> y se visualiza en esta interfaz web local.</p>
      <span class="badge">Inferencia en servidor · UI en navegador</span>
    </header>

    <section class="guide panel">
      <h2>Guía del sistema experto</h2>
      <div class="guide-grid">
        <article class="guide-card">
          <h3>A. Hipótesis evaluadas</h3>
          <div id="hipotesis-grid" class="hyp-grid"></div>
        </article>
        <article class="guide-card">
          <h3>B. ¿Cómo razona el sistema?</h3>
          <p style="margin:0;color:var(--muted);font-size:.84rem;line-height:1.5">
            El sistema utiliza un modelo Naive Bayes simplificado. Para cada hipótesis se parte de una probabilidad inicial P(H). Luego, por cada evidencia seleccionada, se multiplica por la probabilidad condicional P(E|H). Finalmente, los puntajes se normalizan para obtener porcentajes. Solo se usan evidencias presentes; las evidencias no seleccionadas no se penalizan.
          </p>
          <div class="formula">Puntaje(H) = P(H) × P(E1|H) × P(E2|H) × ... × P(En|H)</div>
          <ul id="reglas-globales" class="mini-list"></ul>
        </article>
        <article class="guide-card">
          <h3>C. Variables / evidencias</h3>
          <div id="evidencias-info-grid" class="ev-info-grid"></div>
        </article>
      </div>
    </section>

    <div class="grid-2">
      <section class="panel" id="panel-input">
        <h2>📋 Evidencias del caso</h2>
        <div class="btn-row">
          <button type="button" class="secondary" id="btn-analizar">Analizar selección</button>
          <button type="button" class="ghost" id="btn-limpiar">Limpiar</button>
        </div>
        <div class="btn-row">
          <button type="button" class="secondary" data-caso="1">Caso 1 · Dilatación</button>
          <button type="button" class="secondary" data-caso="2">Caso 2 · Impermeabilización</button>
          <button type="button" class="secondary" data-caso="3">Caso 3 · Desagüe</button>
          <button type="button" class="secondary" data-caso="4">Caso 4 · Mixto</button>
          <button type="button" class="secondary" data-caso="5">Caso 5 · Insuficiente</button>
          <button type="button" class="secondary" data-caso="6">Caso 6 · Ambiguo</button>
          <button type="button" id="btn-prop">Propagación (4 etapas)</button>
        </div>
        <div class="evid-grid" id="evidencias-grid"></div>
      </section>

      <section class="panel" id="panel-out">
        <h2>📊 Resultado</h2>
        <div id="resultado-area">
          <div class="empty-state">Selecciona evidencias y pulsa <strong>Analizar selección</strong>, o ejecuta un caso de prueba.</div>
        </div>
      </section>
    </div>

    <footer>Servidor Python (wsgiref) · Sin librerías externas · Datos procesados localmente</footer>
  </div>

<script>
(function(){
  const grid = document.getElementById('evidencias-grid');
  const out = document.getElementById('resultado-area');
  const panelOut = document.getElementById('panel-out');
  const hipotesisGrid = document.getElementById('hipotesis-grid');
  const evidenciasInfoGrid = document.getElementById('evidencias-info-grid');
  const reglasGlobales = document.getElementById('reglas-globales');

  function escapeHtml(s) {
    if (s === null || s === undefined) return '';
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }
  function confClass(nivel) {
    const n = (nivel || '').toLowerCase();
    if (n.indexOf('alto') !== -1 && n.indexOf('incierto') === -1) return 'conf-alto';
    if (n.indexOf('medio') !== -1) return 'conf-medio';
    if (n.indexOf('bajo') !== -1 || n.indexOf('incierto') !== -1) return 'conf-bajo';
    return 'conf-incierto';
  }
  function barClass(h) { if (h === 'H2') return 'h2'; if (h === 'H3') return 'h3'; return ''; }
  function setLoading(on) { panelOut.classList.toggle('loading', on); }

  function renderGuia(meta) {
    const hip = meta.hipotesis_descripciones || {};
    const evd = meta.evidencias_descripciones || {};

    hipotesisGrid.innerHTML = Object.keys(hip).map(function(h){
      const item = hip[h];
      const tags = (item.evidencias_clave || []).map(function(ev){ return '<span class="tag">' + escapeHtml(ev) + '</span>'; }).join('');
      return '<div class="hyp-card"><h4>' + h + ' · ' + escapeHtml(item.titulo) + '</h4><p>' + escapeHtml(item.descripcion) + '</p>' +
        (tags ? '<div class="tag-list">' + tags + '</div>' : '') + '</div>';
    }).join('');

    evidenciasInfoGrid.innerHTML = Object.keys(evd).map(function(id){
      const item = evd[id];
      const fav = (item.favorece || []).map(function(h){ return '<span class="tag">' + escapeHtml(h) + '</span>'; }).join('');
      return '<div class="ev-card"><h4>' + escapeHtml(item.etiqueta) + '</h4><p>' + escapeHtml(item.descripcion) +
        '</p><div class="tag-list">' + fav + '</div></div>';
    }).join('');

    reglasGlobales.innerHTML =
      '<li>menos de ' + meta.min_evidencias + ' evidencias => H4 evidencia insuficiente</li>' +
      '<li>diferencia menor a ' + meta.umbral_incertidumbre + ' => H4 diagnóstico incierto</li>' +
      '<li>diferencia mayor o igual a ' + meta.umbral_confianza_alta + ' => confianza alta</li>' +
      '<li>caso contrario => confianza media</li>';
  }

  function renderSeleccion(meta) {
    grid.innerHTML = '';
    (meta.evidencias || []).forEach(function(ev){
      const div = document.createElement('div');
      div.className = 'evid-item';
      const info = (meta.evidencias_descripciones || {})[ev.id] || {};
      const id = 'ev-' + ev.id;
      div.innerHTML = '<input type="checkbox" id="' + id + '" value="' + ev.id + '">' +
        '<label for="' + id + '">' + escapeHtml(ev.etiqueta) + '<code>' + escapeHtml(ev.id) + '</code>' +
        (info.descripcion ? '<span style="display:block;color:#9aa8b8;font-size:.76rem;margin-top:3px">' + escapeHtml(info.descripcion) + '</span>' : '') +
        '</label>';
      grid.appendChild(div);
    });
  }

  function renderCaso(data) {
    if (!data.ok) {
      out.innerHTML = '<div class="empty-state">' + escapeHtml(data.error || 'Error en análisis.') + '</div>';
      return;
    }
    const r = data;
    const pills = '<span class="conf-pill ' + confClass(r.nivel_confianza) + '">' + escapeHtml(r.nivel_confianza) + '</span>';
    let rules = '<ul class="rules">';
    (r.reglas_activadas || []).forEach(function(reg){ rules += '<li><strong>' + escapeHtml(reg.codigo) + '</strong> — ' + escapeHtml(reg.explicacion) + '</li>'; });
    rules += '</ul>';
    let bars = '<div class="bars">';
    (r.ranking || []).forEach(function(row){
      const pct = row.porcentaje;
      bars += '<div class="bar-row"><span>' + escapeHtml(row.hipotesis) + '</span><div class="bar-track"><div class="bar-fill ' + barClass(row.hipotesis) + '" style="width:' + pct + '%"></div></div><span>' + pct.toFixed(2) + '%</span></div>';
    });
    bars += '</div>';
    let razon = '';
    if (r.razonamiento_aplicado) {
      const rz = r.razonamiento_aplicado;
      const priors = rz.priors || {};
      const priorsTxt = 'H1=' + ((priors.H1 || 0) * 100).toFixed(2) + '%, H2=' + ((priors.H2 || 0) * 100).toFixed(2) + '%, H3=' + ((priors.H3 || 0) * 100).toFixed(2) + '%';
      razon = '<div class="razonamiento"><strong>Razonamiento aplicado</strong>' +
        '<ul>' +
        '<li>Cantidad de evidencias seleccionadas: ' + rz.cantidad_evidencias + '</li>' +
        '<li>Método usado: ' + escapeHtml(rz.metodo) + '</li>' +
        '<li>Priors utilizados: ' + escapeHtml(priorsTxt) + '</li>' +
        '<li>Diferencia entre primera y segunda hipótesis: ' + Number(rz.diferencia_porcentaje).toFixed(2) + '%</li>' +
        (rz.criterios || []).map(function(c){ return '<li>Criterio: ' + escapeHtml(c) + '</li>'; }).join('') +
        '<li><strong>' + escapeHtml(rz.conclusion) + '</strong></li>' +
        '</ul></div>';
    }
    let val = r.validacion ? '<div class="val-box"><strong>Validación:</strong> ' + escapeHtml(r.validacion) + '</div>' : '';
    out.innerHTML =
      '<div class="result-header"><div class="diag-box"><strong>Diagnóstico:</strong> ' + escapeHtml(r.diagnostico_texto) + '</div>' + pills + '</div>' +
      '<p style="margin:0 0 8px;color:#9aa8b8;font-size:.84rem"><strong>Caso:</strong> ' + escapeHtml(r.nombre_caso) + '</p>' +
      bars +
      '<p style="margin:14px 0 6px;font-size:.88rem;color:#9aa8b8"><strong>Reglas activadas</strong></p>' + rules +
      razon +
      '<div class="reco"><strong>Recomendación</strong><br>' + escapeHtml(r.recomendacion) + '</div>' + val;
  }

  function evidenciasSeleccionadas() {
    const boxes = grid.querySelectorAll('input[type=checkbox]:checked');
    return Array.prototype.map.call(boxes, function(c){ return c.value; });
  }

  async function postAnalizar(body) {
    setLoading(true);
    try {
      const res = await fetch('/api/analizar', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      const data = await res.json();
      renderCaso(data);
    } catch (e) {
      out.innerHTML = '<div class="empty-state">No se pudo conectar al servidor.</div>';
    } finally {
      setLoading(false);
    }
  }

  document.getElementById('btn-analizar').addEventListener('click', function(){
    const ev = evidenciasSeleccionadas();
    if (!ev.length) {
      out.innerHTML = '<div class="empty-state">Selecciona al menos una evidencia.</div>';
      return;
    }
    postAnalizar({ evidencias: ev, nombre_caso: 'Caso manual', esperado: null });
  });
  document.getElementById('btn-limpiar').addEventListener('click', function(){
    grid.querySelectorAll('input[type=checkbox]').forEach(function(c){ c.checked = false; });
    out.innerHTML = '<div class="empty-state">Selecciona evidencias y pulsa <strong>Analizar selección</strong>.</div>';
  });
  document.querySelectorAll('[data-caso]').forEach(function(btn){
    btn.addEventListener('click', function(){
      const id = parseInt(btn.getAttribute('data-caso'), 10);
      fetch('/api/caso/' + id).then(function(r){ return r.json(); }).then(renderCaso);
    });
  });
  document.getElementById('btn-prop').addEventListener('click', async function(){
    setLoading(true);
    try {
      const res = await fetch('/api/propagacion');
      const data = await res.json();
      let html = '';
      (data.etapas || []).forEach(function(st){
        html += '<div class="prop-stage"><h3 style="margin:0 0 8px;font-size:.95rem">' + escapeHtml(st.nombre_caso) + '</h3>';
        html += '<p style="margin:0 0 12px;font-size:.8rem;color:#9aa8b8">Evidencias: ' + (st.evidencias_detalle || []).map(function(x){ return x.etiqueta; }).join(', ') + '</p>';
        const r = st.resultado;
        html += '<div class="result-header"><div class="diag-box" style="font-size:.85rem"><strong>Diagnóstico:</strong> ' + escapeHtml(r.diagnostico_texto) + '</div><span class="conf-pill ' + confClass(r.nivel_confianza) + '">' + escapeHtml(r.nivel_confianza) + '</span></div><div class="bars">';
        (r.ranking || []).forEach(function(row){
          const pct = row.porcentaje;
          html += '<div class="bar-row"><span>' + escapeHtml(row.hipotesis) + '</span><div class="bar-track"><div class="bar-fill ' + barClass(row.hipotesis) + '" style="width:' + pct + '%"></div></div><span>' + pct.toFixed(2) + '%</span></div>';
        });
        html += '</div></div>';
      });
      out.innerHTML = html || '<div class="empty-state">Sin datos.</div>';
    } catch(e) {
      out.innerHTML = '<div class="empty-state">Error al cargar propagación.</div>';
    } finally {
      setLoading(false);
    }
  });

  fetch('/api/meta').then(function(res){ return res.json(); }).then(function(meta){
    renderGuia(meta);
    renderSeleccion(meta);
  }).catch(function(){
    grid.innerHTML = '<div class="empty-state">No se pudo cargar /api/meta</div>';
    hipotesisGrid.innerHTML = '<div class="empty-state">Sin datos</div>';
    evidenciasInfoGrid.innerHTML = '<div class="empty-state">Sin datos</div>';
  });
})();
</script>
</body>
</html>"""


def aplicacion_wsgi(environ, start_response):
    """
    Aplicación WSGI: sirve la SPA y endpoints JSON para el motor en Python.
    """
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
        html = _html_interfaz_web().encode("utf-8")
        return _respuesta_wsgi(start_response, "200 OK", html, "text/html; charset=utf-8")

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
            err = json.dumps({"ok": False, "error": "evidencias debe ser lista de strings"}).encode(
                "utf-8"
            )
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
        etapas_defs = [
            ["humedad_visible"],
            ["humedad_visible", "exposicion_alta_sol"],
            ["humedad_visible", "exposicion_alta_sol", "fisuras_visibles"],
            [
                "humedad_visible",
                "exposicion_alta_sol",
                "fisuras_visibles",
                "aparece_con_calor",
            ],
        ]
        etapas = []
        for i, evs in enumerate(etapas_defs, start=1):
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
    """
    Inicia el servidor HTTP local. Abrí http://127.0.0.1:8765 en el navegador.
    """
    servidor = make_server(host, puerto, aplicacion_wsgi)
    print(f"Sistema Experto Edilicio — interfaz web")
    print(f"Abre en el navegador: http://{host}:{puerto}/")
    print("Ctrl+C para detener el servidor.\n")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")


def menu_principal():
    """
    Muestra menú principal del sistema experto y enruta cada opción.
    """
    while True:
        print("Sistema Experto Edilicio - Menú Principal")
        print("1. Ejecutar caso de prueba 1: dilatación térmica.")
        print("2. Ejecutar caso de prueba 2: falla de impermeabilización.")
        print("3. Ejecutar caso de prueba 3: problema de desagüe.")
        print("4. Ejecutar caso de prueba 4: caso mixto dilatación + impermeabilización.")
        print("5. Ejecutar caso de prueba 5: evidencia insuficiente.")
        print("6. Ejecutar caso de prueba 6: caso ambiguo.")
        print("7. Demostrar propagación de evidencias.")
        print("8. Cargar caso manual.")
        print("9. Salir.")

        try:
            opcion = input("\nSeleccione una opción (1-9): ").strip()
        except EOFError:
            # Escenario típico: ejecución no interactiva (sin stdin).
            print("\nNo hay entrada disponible (EOF). Saliendo del sistema experto.")
            break
        print()

        if opcion in {"1", "2", "3", "4", "5", "6"}:
            numero = int(opcion)
            caso = CASOS_DE_PRUEBA[numero]
            mostrar_resultado(
                nombre_caso=caso["nombre"],
                evidencias_presentes=caso["evidencias"],
                resultado_esperado=caso["esperado"],
            )
        elif opcion == "7":
            demostrar_propagacion_evidencias()
        elif opcion == "8":
            cargar_caso_manual()
        elif opcion == "9":
            print("Saliendo del sistema experto. Hasta luego.")
            break
        else:
            print("Opción inválida. Ingrese un número del 1 al 9.\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sistema Experto Edilicio — interfaz web (por defecto) o consola."
    )
    parser.add_argument(
        "--consola",
        action="store_true",
        help="Ejecutar el menú por consola en lugar del servidor web.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Dirección del servidor web (por defecto 127.0.0.1).",
    )
    parser.add_argument(
        "--puerto",
        type=int,
        default=8765,
        help="Puerto del servidor web (por defecto 8765).",
    )
    argumentos = parser.parse_args()
    if argumentos.consola:
        menu_principal()
    else:
        ejecutar_servidor_web(host=argumentos.host, puerto=argumentos.puerto)



