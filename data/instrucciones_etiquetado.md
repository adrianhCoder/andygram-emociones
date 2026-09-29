# Instrucciones de etiquetado: AndyGram por emociones

## Objetivo

Estas notas alimentan un grafo: quien siente una emoción abre ese nodo y encuentra las notas de Andy Frisella que le sirven. Etiqueta pensando en el **lector**. La pregunta no es "¿la nota menciona esta palabra?", sino "**¿a alguien que se siente así le serviría leer esta nota hoy?**".

Andy casi nunca nombra la emoción: le habla directo a quien la siente. Una nota sobre "la gente que dudó de ti" le sirve a quien siente resentimiento o ganas de revancha aunque nunca diga "anger".

## Qué produces por nota

1. **tags**: de 0 a 3 sub-sentimientos de la taxonomía de abajo (usa el `id` exacto), cada uno con un peso:
   - **3**: la nota está escrita para quien siente esto; es su tema central.
   - **2**: le ayuda claramente, aunque no sea el tema central.

   Nada de etiquetas débiles o por una palabra suelta: mejor 1 etiqueta buena que 3 flojas. Ordénalas de mayor a menor peso.
   Si la nota no le habla a ningún sentimiento (felicitación, anuncio, promoción, táctica de negocio sin ángulo emocional), deja `tags` vacío: `[]`.

2. **consejo**: una frase en español de máximo 25 palabras, en segunda persona (tú), con el consejo central tal como lo diría Andy: directo y sin rodeos.
   - Fiel al texto: no inventes nada que la nota no diga.
   - Sin groserías gratuitas.
   - Si la nota no tiene texto (solo imagen o video), usa el título: `"Video: <título traducido>"` o `"Imagen: <título traducido>"`. Pon tags solo si el título indica claramente el tema, y con peso 2 como máximo.

## Cómo trabajar

- **Lee y juzga cada nota tú mismo.** No escribas scripts ni uses palabras clave para clasificar.
- Si ningún sub-sentimiento le queda bien a una nota, deja `tags` vacío en vez de forzar uno parecido.
- Trabaja directo: no expliques tu razonamiento, solo produce las líneas JSON.
- Procesa todas las notas del chunk, en orden. El `id` es lo que viene después de `=== POST`.
- Guarda cada chunk completo con el validador (una línea JSON por nota):

  ```
  python3 scripts/save_tags.py <chunk> <<'EOF'
  {"id": "...", "tags": [["presion", 3], ["dudar-de-ti", 2]], "consejo": "..."}
  ...
  EOF
  ```

  Si reporta errores, corrígelos y vuelve a guardar hasta que diga `OK`.

## Ejemplos

```
{"id": "2026-09-19_the-pressure-you-feel-isn-t-a-curse", "tags": [["presion", 3], ["dudar-de-ti", 2]], "consejo": "La presión que sientes no es una maldición, es tu llamado: deja de pelear contra tu destino y cree que naciste para esto."}
{"id": "2021-07-04_happy-independence-day", "tags": [], "consejo": "Imagen: Feliz Día de la Independencia"}
```

## Taxonomía

{{TAXONOMIA}}
