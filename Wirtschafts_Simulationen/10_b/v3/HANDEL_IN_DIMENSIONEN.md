# Handeln in Dimensionen — Kaufen/Verkaufen ohne Wertlogik

Dieses Dokument erklärt die neue Handelslogik der Simulation.

In der klassischen Volkswirtschaft ist Handel meistens:

```text
Ware + Menge + Preis + Eigentumswechsel = Kauf/Verkauf
```

In der Planetenwirtschaft ist Handel:

```text
Wirkung + Ursache + Zeitlage + reale Differenz + Substanz + Richtung + Vertrag = Zustandsänderung
```

Es wird also nicht primär ein Ding gehandelt. Ein Ding kann Träger sein, aber gehandelt wird die **kausale Wirkung**, die ein Bedarf, eine Fähigkeit, eine Substanz oder ein Ort im Gesamtsystem auslöst.

## Drei neue Handelsarten

| Alter Begriff | Neuer Flow-Typ | Bedeutung |
|---|---|---|
| Kaufen / Konsumieren | `need_acceptance` | Ein realer Bedarf nimmt eine passende Wirkung an. Beispiel: Hunger nimmt Nahrungswirkung an. |
| Verkaufen / Arbeitskraft anbieten | `contribution_offer` | Eine Person, Gruppe oder Kommune trägt Fähigkeit, Zeit, Substanz oder Wissen bei. |
| Import / Export / Handel | `planetary_transfer` | Überschuss und Mangel werden planetar nach Differenz, Dringlichkeit, Substanz und Richtung verbunden. |

## Die 12 Dimensionen als Vertragskörper

Der Vertrag besteht nicht aus Preis und Gegenleistung, sondern aus Bedingungen.

| Dimension | Frage | Vertragsfolge |
|---|---|---|
| Kausalität | Trifft die Handlung die Ursache? | Niedrig = Pilot/Audit; hoch = priorisierbare Wirkung. |
| Zeit | Wie dringend ist es? | Hoch = Notfallpfad; niedrig = normal planbar. |
| Intensität | Wie stark ist Bedarf/Schaden/Wirkung? | Hoch = stärkere Ressourcenbindung erlaubt. |
| Existenz | Ist das Phänomen real nachweisbar? | Niedrig = Messung/Bericht/Audit nötig. |
| Potenzen | Gibt es Fähigkeiten und Möglichkeiten? | Niedrig = zuerst Aufbau von Fähigkeiten/Material. |
| Wirkungen | Welche Systemfolgen entstehen? | Hoch = gesellschaftlich starkes Wirkungsziel. |
| Substanz | Sind Stoffe/Energie/Wissen/Zeit da? | Niedrig = Stofffreigabe begrenzen, Kreislauf sichern. |
| Materie | Wo ist die Infrastruktur materiell? | Niedrig = Logistik/Ort/Nähe klären. |
| Differenz | Wie groß ist die Lücke zwischen Bedarf und Zustand? | Hoch = Handlung legitimiert; niedrig = eher Erhaltung/Prävention. |
| Bestimmung | Ist die Handlung demokratisch/sinnvoll bestimmt? | Niedrig = Widerspruchsrecht und Rückkopplung nötig. |
| Phänomene | Wie erscheint der Zustand sichtbar/messbar? | Niedrig = Beobachtung und Betroffenenmeldung stärken. |
| Winkelrichtung | Wirkt es regenerativ oder zerstörend/kontrollierend? | Niedrig = blockieren oder umbauen; hoch = planetar passend. |

## Der gestapelte Wahrheitswert

Jede Dimension bekommt einen Wert von `0` bis `4`:

```text
0 = nicht vorhanden / falsch / blockiert
1 = schwach / unsicher / latent
2 = teilweise real / bedingt
3 = stark / aktiv
4 = kritisch / sehr stark / notwendig
```

Der Wahrheitsstapel wird als Basis-5-Zahl geschrieben. Beispiel:

```text
truth_stack_base5 = 434424234343
Reihenfolge       = K Z I E P W S M D B Ph R
```

Das bedeutet:

```text
Kausalität       = 4
Zeit             = 3
Intensität       = 4
Existenz         = 4
Potenzen         = 2
Wirkungen        = 4
Substanz         = 2
Materie          = 3
Differenz        = 4
Bestimmung       = 3
Phänomene        = 4
Winkelrichtung   = 3
```

Der gewichtete `truth_stack_score_0_4` ist dann eine zusammenfassende Prioritätszahl. Aber die Einzelziffern bleiben wichtig. Zwei Verträge können denselben Score haben, aber gegensätzliche Bedeutung:

```text
A: hohe Differenz, niedrige Winkelrichtung → Bedarf echt, Handlung falsch gerichtet.
B: mittlere Differenz, hohe Winkelrichtung → weniger dringend, aber sehr regenerativ.
```

Darum entscheidet nicht nur der Score, sondern die Vertragslogik pro Dimension.

## Beispiele: Was wird wirklich gehandelt?

### Nahrung

Nicht gehandelt wird „1 Ware Brot gegen 3 Geldeinheiten“.

Gehandelt wird:

```text
Hunger + Nährstoffbedarf + Saatgut + Boden + Wasser + Arbeit + Zeit + Verteilung
→ Sättigungs- und Gesundheitswirkung
```

Produkte: Getreide, Gemüse, Hülsenfrüchte, Lagerkisten, Kücheninfrastruktur.  
Arbeitsplätze: Landwirtschaft, Verarbeitung, Gemeinschaftsküche, Agrarökologie.  
Dienstleistungen: Anbauplanung, Ernte, Lagerung, Verteilung, Verpflegung.  
Ökologisch: Bodenaufbau, Wasserverbrauch, Biodiversität.  
Klimarelevant: Methan, Dünger, Kühlung, Transport, klimaresilienter Anbau.

### Arbeit

Nicht gehandelt wird „Arbeitskraft gegen Lohn“.

Gehandelt wird:

```text
Fähigkeit + Zeit + Gesundheit + Werkzeug + soziale Bestimmung
→ Beitrag zu einer Wirkung
```

Beispiel Pflege:

```text
Pflegebedarf + Sorgefähigkeit + Nähe + Vertrauen + Zeit
→ Würde, Entlastung, Alltagssicherheit
```

### Dienstleistung

Nicht gehandelt wird „Service gegen Preis“.

Gehandelt wird:

```text
Bedarf + Fähigkeit + Beziehung + Wirkungskontrolle
→ angenommene soziale Wirkung
```

Beispiel Bildung:

```text
Lernbedarf + Lehrfähigkeit + Material + Zeit + Potenzial
→ Kompetenz, Urteilskraft, Selbstbestimmung
```

### Ökologie

Nicht gehandelt wird „Naturkapital“.

Gehandelt wird:

```text
Boden-/Wasser-/Biodiversitätsdifferenz + Regenerationsfähigkeit + Zeit
→ Lebensgrundlagen-Stabilisierung
```

Produktträger können Saatgut, Feuchtgebiete, Agroforst, Bodenschutzmaterial oder Stadtgrün sein. Der eigentliche Handel ist aber Regeneration.

### Klima

Nicht gehandelt wird „CO₂-Zertifikat als Wertpapier“.

Gehandelt wird:

```text
Emissionsrichtung + Energiequelle + Materialdurchsatz + Resilienz + Regeneration
→ Klimawirkung
```

Eine energieintensive Handlung kann blockiert werden, selbst wenn ein Bedarf real ist, wenn ihre Winkelrichtung zerstörend bleibt. Dann wird nicht der Bedarf bestritten, sondern die Ausführungsform geändert.

## Vertragsmuster

```text
Wirkungsvertrag:
  Flow-Typ: need_acceptance | contribution_offer | planetary_transfer
  Domäne: water | food | energy | shelter | health | ...
  Gehandelte Wirkung: z.B. Nahrungswirkung
  Gemeint als: Existenzsicherung / Pflege / Reparatur / Regeneration
  Wahrheitsstapel: K,Z,I,E,P,W,S,M,D,B,Ph,R
  Gültigkeit: gültig | bedingt gültig | experimentell | blockiert
  Bedingungen:
    - Kausalität muss plausibel sein.
    - Differenz muss real sein.
    - Substanz und Materie müssen vorhanden oder aufbaubar sein.
    - Bestimmung braucht demokratische Rückkopplung.
    - Winkelrichtung darf planetare Grenzen nicht verletzen.
    - Phänomene müssen beobachtet und korrigiert werden.
```

## Harte Regel

Ein hoher Bedarf allein reicht nicht. Eine Handlung muss auch in die richtige Richtung wirken.

```text
Hohe Differenz + niedrige Winkelrichtung = Handlung umbauen.
Hohe Differenz + hohe Kausalität + hohe Winkelrichtung = starke Priorität.
Hohe Wirkung + niedrige Bestimmung = erst demokratisch legitimieren.
Hohe Potenzen + niedrige Substanz = Fähigkeit vorhanden, Stoff fehlt.
Hohe Substanz + niedrige Kausalität = Material vorhanden, aber falscher Lösungsweg.
```

So hängt der gestapelte Wahrheitswert direkt mit den Dimensionen zusammen: Er ist nicht eine Zahl über Dinge, sondern eine Zahl über **Bedingungen einer Wirklichkeitsänderung**.
