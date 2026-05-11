"""
Casos de prueba y etapas de demostración de propagación de evidencias.
"""

# Casos de prueba para consola y API web.
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
        # Resultado esperado H2; puede ser discutible con confianza media según evidencias.
        "esperado": "H2",
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

# Secuencia incremental para la demostración de propagación de evidencias.
ETAPAS_PROPAGACION = [
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
