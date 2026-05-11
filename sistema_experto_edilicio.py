"""
Lanzador de compatibilidad: ejecuta el main del paquete modular
sistema_experto_edilicio/ sin cambiar el nombre del archivo en la raíz.

Uso:
  python sistema_experto_edilicio.py
  python sistema_experto_edilicio.py --consola
"""

import os
import runpy
import sys

if __name__ == "__main__":
    _raiz = os.path.dirname(os.path.abspath(__file__))
    _paquete = os.path.join(_raiz, "sistema_experto_edilicio")
    _main = os.path.join(_paquete, "main.py")
    if not os.path.isfile(_main):
        sys.stderr.write(
            "No se encontró sistema_experto_edilicio/main.py. "
            "Ejecutá desde la carpeta del proyecto o usá: cd sistema_experto_edilicio && python main.py\n"
        )
        sys.exit(1)
    sys.path.insert(0, _paquete)
    runpy.run_path(_main, run_name="__main__")
