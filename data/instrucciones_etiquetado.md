# Instrucciones de etiquetado: AndyGram por emociones

## Objetivo

Estas notas alimentan un grafo: quien siente una emoción abre ese nodo y encuentra las notas de Andy Frisella que le sirven. Etiqueta pensando en el **lector**. La pregunta no es "¿la nota menciona esta palabra?", sino "**¿a alguien que se siente así le serviría leer esta nota hoy?**".

Andy casi nunca nombra la emoción: le habla directo a quien la siente. Una nota sobre "la gente que dudó de ti" le sirve a quien siente resentimiento o ganas de revancha aunque nunca diga "anger".

La lista cubre todo el espectro: emociones **agradables** (felicidad, gratitud, amor, esperanza, confianza, motivación, calma) y **difíciles**.

## Qué produces por nota

**tags**: de 0 a 4 sub-sentimientos de la taxonomía de abajo (usa el `id` exacto), cada uno con un peso:
- **3**: la nota está escrita para quien siente esto; es su tema central.
- **2**: le ayuda claramente, aunque no sea el tema central.

Nada de etiquetas débiles o por una palabra suelta: mejor 1 etiqueta buena que 4 flojas. Ordénalas de mayor a menor peso.

Con 77 sub-sentimientos casi cualquier nota "encaja" en algo; eso no basta. Lo normal es 1 a 3 etiquetas, y 4 es la excepción. Una etiqueta de peso 2 tiene que ser algo que alguien buscaría al sentir esa emoción: si tienes que justificarla, no la pongas. No agregues una etiqueta genérica (estancamiento, presión, seguridad en ti) solo porque la nota tiene un tono de exigencia. Si la nota no le habla a ningún sentimiento (felicitación, anuncio, promoción, táctica de negocio sin ángulo emocional), deja `tags` vacío: `[]`.

No escribas consejo: cada nota ya tiene uno y se conserva.

## Emociones agradables

Etiqueta una emoción agradable cuando la nota le habla a quien **ya** se siente así: cómo aprovechar una racha sin volverse complaciente, cómo cultivar la gratitud, qué hacer con la ambición, cómo cuidar a los que amas. Una nota que empuja a alguien sin ganas es **Desmotivación**, no Motivación: Motivación / Ambición es para quien ya está encendido. No etiquetes una nota como agradable solo por ser motivacional.

## Desesperanza y pensamientos suicidas (regla estricta)

`pensamientos-suicidas` y `sentirte-una-carga` son para alguien que puede estar en peligro. Úsalos **solo** si la nota habla con compasión de no rendirse con la vida, del valor de tu vida para otros, de pedir ayuda o de salir de la oscuridad (por ejemplo, cuando Andy cuenta que él mismo tuvo pensamientos suicidas y cómo salió).

**Nunca** los uses en notas de mano dura ("deja de ser víctima", "deja de quejarte", "no hay excusas"): a alguien con ideas suicidas esas notas le pueden hacer daño. "Suicidal empathy" es un término político, no tiene que ver con el suicidio. Ante la duda, no etiquetes.

## Cómo trabajar

- **Lee y juzga cada nota tú mismo.** No escribas scripts ni uses palabras clave para clasificar.
- Si ningún sub-sentimiento le queda bien a una nota, deja `tags` vacío en vez de forzar uno parecido.
- Trabaja directo: no expliques tu razonamiento, solo produce las líneas JSON.
- Procesa todas las notas del chunk, en orden. El `id` es lo que viene después de `=== POST`.
- Guarda **por lotes de unas 12 notas** con el validador (una línea JSON por nota), en orden, hasta completar el chunk:

  ```
  python3 scripts/save_tags.py <chunk> --lote <<'EOF'
  {"id": "...", "tags": [["presion", 3], ["dudar-de-ti", 2]]}
  ...
  EOF
  ```

  Cada lote responde `Lote OK` con cuántas faltan; el último responde `OK <chunk>: N notas guardadas`. Si un lote reporta errores, corrígelo y vuelve a mandar ese lote.

## Ejemplos

```
{"id": "2026-09-19_the-pressure-you-feel-isn-t-a-curse", "tags": [["presion", 3], ["dudar-de-ti", 2]]}
{"id": "2021-04-29_be-the-alchemist-of-your-own-life", "tags": [["duelo", 3], ["sin-esperanza", 2], ["pensamientos-suicidas", 2]]}
{"id": "2021-07-04_happy-independence-day", "tags": []}
```

## Taxonomía

{{TAXONOMIA}}
