# Arnhemse Luchtvaart Club, nieuwe website

Een vernieuwde, statische versie van [arnhemseluchtvaartclub.nl](https://arnhemseluchtvaartclub.nl/).
Alle teksten, foto's en pagina's zijn overgenomen van de bestaande WordPress-site;
de opmaak is vernieuwd in de huisstijl van het clublogo (blauw, geel, wit).

## Mappen

- `docs/` de kant-en-klare website (HTML, CSS, JS, foto's, folder). Deze map kun je
  zo online zetten, bijvoorbeeld met GitHub Pages (Settings → Pages → branch `main`, map `/docs`)
  of door de inhoud naar een webhost te uploaden.
- `bron/content/` de teksten per pagina, overgenomen van de oude site.
- `bron/build.py` zet het menu, de kop en de voettekst om de teksten heen en maakt `docs/`.

## Aanpassen

1. Pas een tekst aan in `bron/content/<pagina>.html` (de homepage, contact- en
   sponsorpagina staan in `bron/build.py` zelf).
2. Nieuwe foto's zet je in `docs/img/`.
3. Bouw de site opnieuw:

   ```
   pip install beautifulsoup4 pillow
   python3 bron/build.py
   ```

Lokaal bekijken: `cd docs && python3 -m http.server` en open http://localhost:8000.
