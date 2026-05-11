"""
Punto de entrada: modo web (por defecto) o modo consola (--consola).

Ejecutar desde esta carpeta:
  python main.py
  python main.py --consola
  python main.py --host 127.0.0.1 --puerto 8765
"""

import argparse

from console_ui import menu_principal
from web_server import ejecutar_servidor_web


def main():
    parser = argparse.ArgumentParser(
        description="Sistema Experto Edilicio — interfaz web o consola."
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


if __name__ == "__main__":
    main()
