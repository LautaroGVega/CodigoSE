# Sistema Experto probabilístico edilicio

Proyecto académico de **Sistemas Inteligentes**: diagnóstico preliminar de problemas en **cubiertas, techos metálicos e impermeabilizaciones** del mantenimiento edilicio, usando un **Naive Bayes simplificado** (solo biblioteca estándar de Python).

## Hipótesis que evalúa el motor

| Código | Significado |
|--------|-------------|
| **H1** | Dilatación de materiales por temperatura |
| **H2** | Falla de impermeabilización |
| **H3** | Problema de desagüe o acumulación de agua |
| **H4** | Otro / diagnóstico incierto (salida de control; **no** se calcula con \(P(E \mid H4)\)) |

**H4** aparece si hay pocas evidencias, si la diferencia entre la primera y la segunda hipótesis es menor al umbral de incertidumbre, o cuando no se puede elegir una causa técnica principal con la confianza configurada.

## Tecnología

- **Python 3** puro, sin dependencias pip.
- Inferencia en Python (`inference_engine.py`).
- Interfaz web local con **`wsgiref.simple_server`** y archivos estáticos en `web/`.
- Consola interactiva en `console_ui.py`.

## Cómo ejecutarlo

Desde la carpeta del proyecto `sistema_experto_edilicio/`:

### Modo web (por defecto)

```bash
cd sistema_experto_edilicio
python main.py
```

Abre en el navegador la URL que muestra la consola, por ejemplo:

`http://127.0.0.1:8765/`

Opcional:

```bash
python main.py --host 127.0.0.1 --puerto 8765
```

### Modo consola

```bash
python main.py --consola
```

## Archivos del sistema

| Archivo | Rol |
|---------|-----|
| `main.py` | Entrada: argparse, web o consola |
| `knowledge_base.py` | Datos: priors, \(P(E\mid H)\), reglas, recomendaciones, descripciones |
| `inference_engine.py` | Motor: probabilidades, diagnóstico, `evaluar_caso` |
| `test_cases.py` | `CASOS_DE_PRUEBA` y `ETAPAS_PROPAGACION` |
| `console_ui.py` | Menú, carga manual, propagación por consola |
| `web_server.py` | WSGI, API JSON y lectura de `web/*` |
| `web/index.html` | Estructura de la interfaz |
| `web/styles.css` | Estilos |
| `web/app.js` | Lógica del cliente (fetch a `/api/*`) |

## Consigna Componente 3 (cómo se cumple)

- El motor corre **sin librerías externas** y explica reglas activadas, ranking, confianza y recomendación.
- **Entrada**: casos predefinidos (API y consola) y **carga manual** (consola y checkboxes en web).
- Se usan solo las **probabilidades condicionales** de la base de conocimiento para evidencias **presentes** (sin complemento \(1 - P(E|H)\) para ausentes).
- Salida con **porcentajes**, **nivel de confianza**, **razonamiento aplicado** y validación cuando hay resultado esperado.

## Consigna Componente 4 (cómo se cumple)

- **Seis casos** en `test_cases.py` (dilatación, impermeabilización, desagüe, mixto, insuficiente, ambiguo).
- **Propagación**: `ETAPAS_PROPAGACION` usada en consola y en `GET /api/propagacion`.
- Cada ejecución muestra evidencias, reglas, ranking, diagnóstico, confianza, recomendación y validación razonable frente al esperado.
