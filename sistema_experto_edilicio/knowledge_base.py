"""
Base de conocimiento del Sistema Experto edilicio.

Solo contiene datos (hipótesis, priors, probabilidades condicionales, reglas,
recomendaciones y descripciones pedagógicas). Sin lógica de inferencia ni servidor.
"""

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

# Etiquetas amigables para mostrar evidencias en consola y en la API web.
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
