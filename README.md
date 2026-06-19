# Apuesta Mundial 2026 — Dashboard automático

La web se actualiza sola: un robot (GitHub Actions) consulta los resultados del
Mundial cada 5 minutos, escribe `resultados.json`, y la página lo lee y recalcula
el ranking. **Nunca más resubís el HTML.**

## Qué hace cada archivo
- `index.html` — el dashboard. Lee `resultados.json` al abrir y cada 60s.
- `resultados.json` — resultados + estado (final / en vivo) + goleadores. Lo escribe el robot.
- `fixtures.json` — mapa de los 72 partidos (no se toca).
- `scripts/actualizar.py` — consulta la API y arma `resultados.json`.
- `.github/workflows/actualizar.yml` — programa el robot cada 5 min.

## Puesta en marcha (una sola vez, ~10 min)
1. **Token gratis:** registrate en https://www.football-data.org/client/register
   y copiá tu API token.
2. **Repo:** creá un repositorio **público** en GitHub y subí estos archivos
   (manteniendo las carpetas `scripts/` y `.github/workflows/`).
3. **Secreto:** en el repo → Settings → Secrets and variables → Actions →
   *New repository secret*. Nombre: `FOOTBALL_TOKEN`, valor: tu token.
4. **Pages:** Settings → Pages → Source: *Deploy from a branch* → branch `main` / `/root`.
   Te da la URL pública (ej. `https://usuario.github.io/quiniela/`).
5. **Probar:** pestaña **Actions** → "Actualizar resultados" → *Run workflow*.
   En ~1 min se genera `resultados.json` y la web queda viva.

## En vivo
El partido en juego sale en un banner rojo arriba y en su fila como "EN VIVO".
Sus puntos **se suman al ranking como provisionales** (la tarjeta muestra
"▲N en vivo" en rojo y el TOTAL pasa a "incl. en vivo"). Cuando el partido
figura FINISHED el provisional se vuelve definitivo automáticamente.

## Si la API fallara
Podés editar `resultados.json` a mano (formato `"M30":{"rl":2,"rv":1,"st":"FINISHED"}`)
y hacer commit. La web se actualiza igual, sin tocar el HTML.

## Notas
- football-data.org free: 10 req/min. El robot usa 2 req cada 5 min → de sobra.
- GitHub Actions (cron) puede demorar el disparo unos minutos en horas pico; normal.
- Repo público para Pages gratis (pronósticos y resultados no son datos sensibles).
