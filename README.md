# Momo the Koala – automatisk posting af Reels

Dette repository poster Momos videoer som Reels på Instagram, helt automatisk.

**Sådan kører det:**
- Videoerne laves i en videogenerator og sendes til Claude, som lægger dem i mappen `queue/` med billedtekst og tidspunkt.
- Hver time tjekker GitHub, om en video skal ud, og poster den som en Reel.
- Faste tidspunkter: mandag, onsdag og lørdag kl. 19:00 (dansk tid). Rettes under `postdage` og `tid` i `config.json`.

## Din kontrol

Alt kan gøres på github.com eller i GitHub-appen: åbn filen, tryk på blyanten, ret og tryk **Commit changes**.

| Det vil du | Sådan gør du |
|---|---|
| **Stoppe al posting** | Ret `"pause": false` til `"pause": true` i `config.json`. Tilbage til `false` for at starte igen. |
| **Stoppe én video** | Ret `"status": "klar"` til `"status": "stop"` i videoens `queue/<mappe>/opslag.json`. |
| **Ændre teksten** | Ret `"billedtekst"` i videoens `opslag.json`. Brug `\n` for linjeskift. |
| **Flytte tidspunktet** | Ret `"tidspunkt"`, fx `"2026-11-11T19:00:00+01:00"`. |
| **Teste forbindelsen** | *Actions → Post Reels til Instagram → Run workflow*. Grøn = forbindelsen virker. |

## Status på en video

- `klar` – venter på sit tidspunkt
- `stop` – bliver ikke postet
- `postet` – ligger på Instagram
- `udløbet` – blev ikke postet inden for 12 timer efter tidspunktet, fx under pause
- `fejl` – fejlede tre gange; se `"note"`

Melder Instagram, at kontoen er begrænset, sætter systemet selv al posting på pause og prøver ikke igen.
Før et nyt forsøg tjekker det altid profilen, så der ikke opstår dubletter.

## Engangsopsætning

1. Instagram-kontoen er en offentlig creator-konto og forbundet til Facebook-siden "Momo the Koala".
2. GitHub Pages er slået til: *Settings → Pages → Deploy from a branch → main / (root)*.
3. Hemmelighederne `IG_TOKEN` (sidens nøgle fra Graph API Explorer) og `IG_USER_ID` (Instagram-kontoens ID) ligger under *Settings → Secrets and variables → Actions*.
4. `"pause"` i `config.json` er sat til `false`.
