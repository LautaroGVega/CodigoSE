"""
Interfaz por consola: menú, carga manual y demostración de propagación.
"""

from inference_engine import evaluar_caso
from knowledge_base import EVIDENCIAS_ETIQUETAS, HIPOTESIS_NOMBRES, PROBABILIDADES_CONDICIONALES
from test_cases import CASOS_DE_PRUEBA, ETAPAS_PROPAGACION


def mostrar_resultado(nombre_caso, evidencias_presentes, resultado_esperado=None):
    """
    Ejecuta inferencia y muestra por consola evidencias (con etiquetas), reglas,
    ranking, diagnóstico, confianza, razonamiento aplicado, recomendación y validación.
    """
    resultado = evaluar_caso(evidencias_presentes, resultado_esperado=resultado_esperado)
    analisis = resultado["analisis"]
    ranking = resultado["ranking"]
    rz = resultado["razonamiento_aplicado"]

    print("\n========================================")
    print(f"CASO: {nombre_caso}")
    print("========================================\n")

    print("Evidencias seleccionadas:")
    for evidencia in evidencias_presentes:
        etiqueta = EVIDENCIAS_ETIQUETAS.get(evidencia, evidencia)
        print(f"- {etiqueta} ({evidencia})")

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

    print("\nRazonamiento aplicado:")
    print(f"- Cantidad de evidencias: {rz['cantidad_evidencias']}")
    print(f"- Método: {rz['metodo']}")
    priors = rz["priors"]
    print(
        "- Priors: "
        f"H1={priors['H1']*100:.2f}%, H2={priors['H2']*100:.2f}%, H3={priors['H3']*100:.2f}%"
    )
    print(
        "- Diferencia 1ra vs 2da hipótesis: "
        f"{rz['diferencia_primera_segunda'] * 100:.2f}%"
    )
    for c in rz["criterios"]:
        print(f"  · {c}")
    print(f"- Conclusión: {rz['conclusion']}")

    print("\nRecomendación:")
    print(resultado["recomendacion"])

    if resultado["validacion"] is not None:
        print("\nValidación del caso:")
        print(resultado["validacion"])

    print("\n" + "=" * 40 + "\n")


def cargar_caso_manual():
    """
    Permite seleccionar evidencias por números separados por coma.
    Valida entrada y evita duplicados.
    """
    evidencias_disponibles = list(PROBABILIDADES_CONDICIONALES.keys())

    print("\n--- Carga manual de caso ---")
    print("Seleccione evidencias ingresando números separados por coma.")
    print("Ejemplo: 1,3,5")
    print("Evidencias disponibles:")

    for indice, evidencia in enumerate(evidencias_disponibles, start=1):
        etiqueta = EVIDENCIAS_ETIQUETAS.get(evidencia, evidencia)
        print(f"{indice}. {etiqueta} ({evidencia})")

    while True:
        try:
            entrada = input("\nIngrese su selección: ").strip()
        except EOFError:
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
    """Muestra cómo evoluciona el diagnóstico al agregar evidencias (ETAPAS_PROPAGACION)."""
    print("\n========================================")
    print("DEMONSTRACIÓN: Propagación de evidencias")
    print("========================================\n")

    for i, evidencias in enumerate(ETAPAS_PROPAGACION, start=1):
        print(f"--- Etapa {i} ---")
        mostrar_resultado(
            nombre_caso=f"Propagación - Etapa {i}",
            evidencias_presentes=evidencias,
            resultado_esperado=None,
        )


def menu_principal():
    """Menú principal del sistema experto (consola)."""
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
