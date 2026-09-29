#!/bin/bash
# Muestra en vivo el avance de la descarga de AndyGram (Ctrl+C para salir)
cd "$(dirname "$0")"
TOTAL=$(python3 -c "import json;print(len(json.load(open('scripts/urls.json'))))" 2>/dev/null || echo 2418)
while true; do
  clear
  n=$(ls posts | wc -l)
  echo "AndyGram: $n / $TOTAL descargados  ($(date +%H:%M:%S))"
  echo "Ritmo último minuto: $(find posts -name '*.md' -mmin -1 | wc -l) posts/min"
  pgrep -f "^python3.*scripts/scrape\.py" >/dev/null && echo "Estado: corriendo" || echo "Estado: DETENIDO"
  echo "Último 429: $(grep 429 scrape.log | tail -1 || echo ninguno)"
  echo; echo "Últimas descargadas (hora - archivo):"
  ls -lt --time-style=+%H:%M:%S posts | awk 'NR>1 && NR<=11 {print $6"  "$7}'
  sleep 2
done
