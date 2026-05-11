"""
Motor de inferencia: Naive Bayes simplificado para el diagnóstico edilicio.

H4 no se calcula con P(E|H); es una salida de control según reglas en
determinar_diagnostico().
"""

from knowledge_base import (
    HIPOTESIS_NOMBRES,
    MIN_EVIDENCIAS,
    PRIORS,
    PROBABILIDADES_CONDICIONALES,
    RECOMENDACIONES,
    REGLAS_EXPLICATIVAS,
    UMBRAL_CONFIANZA_ALTA,
    UMBRAL_INCERTIDUMBRE,
)


def calcular_probabilidades(evidencias_presentes):
    """
    Calcula probabilidades finales de H1, H2 y H3 mediante Naive Bayes simplificado.

    Fórmula:
      puntaje(H) = P(H) * Π P(E|H) solo para evidencias presentes.
      probabilidad_final(H) = puntaje(H) / sumatoria_de_puntajes.

    No se usan evidencias ausentes como complemento (1 - P(E|H)).
    """
    puntajes = {}

    for hipotesis, prior in PRIORS.items():
        puntaje = prior
        for evidencia in evidencias_presentes:
            puntaje *= PROBABILIDADES_CONDICIONALES[evidencia][hipotesis]
        puntajes[hipotesis] = puntaje

    suma_puntajes = sum(puntajes.values())

    if suma_puntajes == 0:
        cantidad = len(PRIORS)
        return {h: 1.0 / cantidad for h in PRIORS}

    return {
        hipotesis: puntaje / suma_puntajes for hipotesis, puntaje in puntajes.items()
    }


def determinar_diagnostico(probabilidades, cantidad_evidencias):
    """
    Determina diagnóstico final y nivel de confianza.

    H4 si:
    - cantidad_evidencias < MIN_EVIDENCIAS (evidencia insuficiente), o
    - diferencia (1ra - 2da) < UMBRAL_INCERTIDUMBRE (diagnóstico incierto).

    Confianza alta si diferencia >= UMBRAL_CONFIANZA_ALTA; si no, media.
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
    """Retorna texto de recomendación según diagnóstico (incluye H4)."""
    if diagnostico in RECOMENDACIONES:
        return RECOMENDACIONES[diagnostico]
    return RECOMENDACIONES["H4"]


def evaluar_caso(evidencias_presentes, resultado_esperado=None):
    """
    Evalúa un conjunto de evidencias y devuelve diagnóstico, ranking, reglas,
    validación opcional y bloque de razonamiento aplicado.
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
            f"menos de {MIN_EVIDENCIAS} evidencias => H4 evidencia insuficiente",
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
