#!/bin/bash
# Avance en vivo del etiquetado por emociones (Ctrl+C para salir)
cd "$(dirname "$0")" && exec python3 scripts/progreso_etiquetado.py "$@"
