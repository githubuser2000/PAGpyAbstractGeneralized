# Sichtbare Anzeige von Handeln in Dimensionen

Diese Version schreibt Handels-/Wirkungsverträge nicht nur in CSV/Markdown-Dateien, sondern zeigt sie direkt im Terminal an.

## Standardlauf

```bash
pypy3 planetary_effect_economy.py --steps 120 --scenario planetary_commons --out out_planetenwirtschaft
```

Standardmäßig werden nach der Zusammenfassung 16 sichtbare Wirkungsverträge angezeigt.

## Viel anzeigen

```bash
pypy3 planetary_effect_economy.py \
  --steps 120 \
  --scenario planetary_commons \
  --out out_planetenwirtschaft \
  --show-trades 40 \
  --show-trade-detail \
  --show-dimensions \
  --show-catalog \
  --show-stack-explanation
```

## Anzeige abschalten

```bash
pypy3 planetary_effect_economy.py --steps 120 --show-trades 0 --quiet
```

## Neue Terminal-Optionen

| Option | Bedeutung |
|---|---|
| `--show-trades N` | Zeigt N Wirkungsverträge direkt im Terminal. Standard: 16. `0` schaltet es ab. |
| `--show-trade-detail` | Zeigt Produkte, Arbeitsplätze, Dienstleistungen, Ökologie, Klima und Vertragsbedingungen pro Vertrag. |
| `--show-dimensions` | Zeigt die Bedeutung aller Dimensionen. |
| `--show-catalog` | Zeigt den Handelskatalog aller Domänen: was gehandelt wird, gemeint ist, Produkte, Jobs, Dienste, Öko/Klima. |
| `--show-stack-explanation` | Zeigt, wie der gestapelte Wahrheitswert gelesen wird. |

## Grundsatz

Alte Form:

```text
Ware + Menge + Preis + Eigentum → kaufen/verkaufen/importieren/exportieren
```

Neue Form:

```text
Kausalität + Zeit + Intensität + Existenz + Potenzen + Wirkungen
+ Substanz + Materie + Differenz + Bestimmung + Phänomene + Winkelrichtung
→ Wirkungsvertrag
```

`activated_effect` ist keine Geldmenge. Es ist eine Wirkungseinheit. Der `truth_stack_base5` ist keine Wertzahl. Er ist die Zustands- und Vertragssignatur des Wirkungsflusses.
