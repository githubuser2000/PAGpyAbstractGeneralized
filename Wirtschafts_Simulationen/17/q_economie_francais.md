# Q-économie : système économique complet pour une monnaie à valeur de ligne

**Langue :** Français  
**Version :** 1.0  
**Base :** La monnaie se compose de pièces Q. La hauteur de ligne est la valeur de la pièce.

---

## 1. Idée centrale

La Q-économie est un ordre monétaire, de crédit et de production sémantique. Elle ne traite pas seulement l’argent comme unité économique, mais aussi la difficulté, la structure, le code, les interfaces, l’architecture, l’exploitation et les modules terminés.

Une pièce est une ligne de tableau. **La hauteur de ligne** est sa valeur. **La numérotation** est sa frappe. Le texte du continuum est sa couverture sémantique.

```text
Pièce Qn = (numéro n, valeur h, signification B)
Valeur(Qn) = hauteur de ligne h
Signification(Qn) = contenu sémantique dans le continuum
```

Q20 ne signifie donc pas « vingt unités ». Q20 est la pièce frappée du numéro 20 et dont la valeur est 4. Quatre pièces Q1 peuvent avoir la même valeur nominale qu’une pièce Q20, mais elles n’ont pas la même fonction.

---

## 2. Unités de base

L’unité de base s’appelle la **valeur de ligne**.

```text
1 VL = 1 valeur de ligne
```

Une sous-unité peut être l’**octadégramme** :

```text
1 VL = 18 octadégrammes
```

Donc :

```text
Valeur 1 = 1 VL = 18 octadégrammes
Valeur 2 = 2 VL = 36 octadégrammes
Valeur 3 = 3 VL = 54 octadégrammes
Valeur 4 = 4 VL = 72 octadégrammes
```

---

## 3. Catalogue des pièces

| Pièce | Valeur | Couche | Signification économique |
|---:|---:|---|---|
| Q1 | 1 | Difficulté de base | tâche, difficulté, nœud, noyau du problème |
| Q2 | 1 | Complexité | partie, complication, élément moléculaire, sous-structure |
| Q3 | 1 | Abstraction | théorie, modèle, état intermédiaire entre lâche et fixé |
| Q4 | 1 | Cristallisation | objet formel, fil, forme mathématique |
| Q5 | 2 | Opération | encodage, ordre, commande, programmation impérative |
| Q6 | 2 | Déclaration | description déclarative, règle, fil au lieu de commande |
| Q7 | 2 | Délégation | déléguer, référencer, transférer la responsabilité |
| Q8 | 2 | Bibliothèque | pierre réutilisable, ruche, minéral, collection de blocs |
| Q9 | 2 | Framework | cadre, forme organique, structure d’intelligence générale |
| Q10 | 3 | Contrainte | limitation, structure, corde, espace des possibilités |
| Q11 | 3 | Interface | intervention, interface, insertion de pensée |
| Q12 | 3 | Boîte à outils | méthodes, mathématiques, algèbre, analyse, topologie, théorie des catégories |
| Q13 | 3 | Programme | service, paradigme, approche de pensée |
| Q14 | 3 | Orchestration | composition, chorégraphie, direction, maîtrise |
| Q15 | 3 | Application | application, œuvre, opus |
| Q16 | 3 | Exploitation | menu, noyau, système d’exploitation, exécution |
| Q17 | 4 | Compression | compression ; opération inverse : décompression |
| Q18 | 4 | Architecture | construction, plan, forme globale porteuse |
| Q19 | 4 | Génération | production ; mouvement inverse : dégénérescence ou décadence |
| Q20 | 4 | Module/Machine | développement terminé, appareil, motif, machine de difficulté |

Les quatre couches de valeur :

```text
Valeur 1 : Q1–Q4     pièces de base
Valeur 2 : Q5–Q9     pièces opérationnelles
Valeur 3 : Q10–Q16   pièces systémiques
Valeur 4 : Q17–Q20   pièces de capital
```

---

## 4. Addition, richesse et portefeuille

Les pièces peuvent être additionnées. On additionne d’abord la valeur de ligne.

Exemple :

```text
2 × Q1
1 × Q8
3 × Q10
1 × Q20
```

Valeur nominale :

```text
2 × 1 VL = 2 VL
1 × 2 VL = 2 VL
3 × 3 VL = 9 VL
1 × 4 VL = 4 VL
Valeur totale = 17 VL
```

En octadégrammes :

```text
17 VL × 18 = 306 octadégrammes
```

Portefeuille :

```text
Wallet = (Q1:2, Q8:1, Q10:3, Q20:1)
Valeur = 17 VL
```

Règle essentielle : une même valeur nominale ne signifie pas une même fonction sémantique.

```text
4 × Q1 = 4 VL
1 × Q20 = 4 VL
mais : 4 × Q1 ≠ 1 × Q20
```

Quatre noyaux de tâche ne sont pas encore une machine terminée. Une machine terminée peut être décomposée en noyaux de tâche, mais elle n’est pas identique à eux.

---

## 5. Dettes et opérations inverses

Les dettes sont des soldes négatifs de pièces.

```text
-1 × Q18 = je dois une unité d’architecture
```

Un compte peut être nominalement positif mais sémantiquement fragile :

```text
+3 × Q5 -1 × Q10
```

Nominalement :

```text
3 × Q5 = 6 VL
-1 × Q10 = -3 VL
Net = +3 VL
```

Mais sémantiquement, Q10 manque : la structure et la contrainte manquent.

> Un acteur peut être riche nominalement et illiquide sémantiquement.

La dette et l’opération inverse sont différentes :

```text
-Q17  = dette de compression
1/Q17 = décompression
-Q19  = dette de génération
1/Q19 = dégénérescence
```

Quatre formes de dette :

| Type de dette | Sens | Exemple |
|---|---|---|
| Dette de valeur | seul un montant est dû | 10 VL |
| Dette de hauteur | une classe de valeur est due | trois pièces de hauteur 2 |
| Dette de type | un type précis de pièce est dû | 2 × Q10 |
| Dette de projet | une prestation concrète est due | service Q13 avec interface Q11 |

---

## 6. Comptes, bilan et richesse

Un compte n’est pas un solde unique, mais un vecteur de 20 types de pièces.

```text
Compte A :
Q1:  10
Q2:   5
Q3:   2
Q5:   8
Q6:  -1
Q8:   3
Q9:   1
Q10: -2
Q20:  1
```

Les valeurs négatives sont des dettes. Le compte se lit de deux manières :

```text
Lecture nominale = somme de tous les soldes × valeur de ligne
Bilan sémantique = excédents et manques par type de pièce
```

Trois formes de richesse :

1. **Richesse nominale :** valeur totale en VL.
2. **Richesse sémantique :** possession des bons types de pièces pour l’action réelle.
3. **Richesse de liquidité :** capacité à régler les dettes exigibles dans le bon type de pièce.

Une entreprise avec beaucoup de Q5 et Q13 possède beaucoup de code et de services. Si elle doit Q10, Q16 et Q18, elle porte une dette structurelle, opérationnelle et architecturale.

---

## 7. Marchés

La Q-économie a besoin de plusieurs marchés.

### Marché des pièces

Les pièces Q s’échangent entre elles :

```text
1 × Q20 contre 4 × Q1
1 × Q18 contre 2 × Q5
1 × Q13 contre 1 × Q10
```

Un échange peut être équilibré nominalement, mais déséquilibré sémantiquement.

### Marché du travail

Les humains ou les agents vendent des prestations :

```text
Travail Q5 : codage
Travail Q6 : spécification
Travail Q10 : contraintes et structure
Travail Q11 : interfaces
Travail Q18 : architecture
Travail Q20 : construction de modules
```

### Marché des biens

Les produits et services ont une signature Q. Exemple :

```text
Service d’analyse :
Q10: 2
Q11: 1
Q12: 1
Q13: 2
Q16: 1
```

### Marché du crédit

Les créances et dettes y sont négociées.

```text
A doit 5 × Q18 à B.
B vend la créance à C.
C paie moins que la valeur nominale à cause du risque de défaut.
```

### Marché à terme

Les livraisons futures y sont négociées.

```text
Livraison dans 30 jours : 3 × Q13 + 1 × Q16
Prix aujourd’hui : 12 VL
```

### Marché de l’assurance

L’assurance couvre les défaillances de certains types de pièces, surtout Q16, Q18 et Q20.

### Marché des communs

Q8, Q9, Q12 et Q16 sont souvent des biens communs. Bibliothèques, frameworks, outils et infrastructures doivent être financés en partie publiquement ou collectivement.

---

## 8. Prix et taux d’échange

Il existe un prix nominal et un prix de marché.

```text
Prix nominal(Qi) = valeur de ligne h(Qi)
```

Le prix de marché résulte de la rareté, de la qualité, de l’urgence et de la confiance :

```text
Prix de marché(Qi) =
Valeur nominale(Qi)
× rareté
× facteur qualité
× facteur urgence
× facteur confiance
```

Exemple :

```text
Q18 nominal = 4 VL
rareté : ×1,5
qualité : ×1,2
urgence : ×1,3
confiance : ×1,1
prix de marché = 4 × 1,5 × 1,2 × 1,3 × 1,1 = 10,296 VL
```

Pour les dettes de type, la même valeur nominale ne suffit pas. Celui qui doit Q18 ne peut pas payer automatiquement avec Q17. Le créancier peut fixer une décote sémantique :

```text
1 × Q17 compte comme substitut à 60 % de 1 × Q18
```

C’est une **décote sémantique**.

---

## 9. Production et recettes de production

Produire signifie transformer la difficulté en formes structurées, exécutables et réutilisables.

Chaîne de valeur principale :

```text
Q1 tâche
→ Q2 décomposition
→ Q3 abstraction
→ Q4 forme formelle
→ Q5/Q6 programmation ou spécification
→ Q8/Q9 réutilisation et cadre
→ Q10/Q11 structure et interface
→ Q13 service
→ Q15 application
→ Q18 architecture
→ Q20 machine/module
```

Recettes de production :

```text
Sortie Q5 codage :
Q1 tâche + Q3 modèle + temps de travail

Sortie Q6 spécification :
Q1 tâche + Q3 abstraction + Q10 contrainte

Sortie Q8 bibliothèque :
plusieurs Q5 + au moins un Q6 + compétence d’outils Q12 + compression Q17

Sortie Q9 framework :
Q8 bibliothèques + Q10 contraintes + Q11 interfaces + logique de service Q13

Sortie Q13 service :
Q5 code + Q6 spécification + Q10 contraintes + Q11 interface + Q8 bibliothèque

Sortie Q18 architecture :
Q10 contraintes + Q11 interfaces + Q14 orchestration + Q17 compression + forme Q3/Q4

Sortie Q20 module/machine :
Q13 programme + Q15 application + Q16 exploitation + Q18 architecture + Q19 génération
```

---

## 10. Création monétaire et hôtel des monnaies

Les nouvelles pièces ne sont pas créées arbitrairement. Elles sont frappées lorsqu’une prestation a été vérifiée et reconnue.

```text
architecture validée → nouvelles pièces Q18
service validé → nouvelles pièces Q13
module validé → nouvelles pièces Q20
```

L’hôtel des monnaies a cinq tâches :

```text
1. frapper les pièces
2. détruire les pièces
3. classer les types de pièces
4. empêcher les contrefaçons
5. assurer la stabilité des prix
```

La monnaie n’est pas couverte par l’or, mais par du **travail sémantique vérifié**.

Les validateurs contrôlent le travail :

```text
Le validateur Q5 vérifie le code.
Le validateur Q6 vérifie les spécifications.
Le validateur Q10 vérifie les contraintes.
Le validateur Q18 vérifie l’architecture.
Le validateur Q20 vérifie la maturité du module.
```

Une fausse validation entraîne perte de réputation et dettes de pénalité.

---

## 11. Banques, crédit et intérêts

Les banques accordent du crédit, mais ne créent pas automatiquement de valeur réelle. Le crédit crée une capacité de paiement ; la couverture naît seulement d’un travail productif.

Exemple :

```text
La banque prête à l’entreprise F :
3 × Q18
2 × Q13

L’entreprise F reçoit :
+3 Q18 +2 Q13

En même temps apparaît :
-3 Q18 -2 Q13 plus intérêts
```

Les intérêts viennent du temps, du risque, de la rareté et de la difficulté sémantique :

```text
Intérêt(Qi) =
taux de base
+ risque de défaut
+ supplément de rareté
+ supplément de complexité
- réduction de garantie
```

Les pièces hautes comme Q18 et Q20 ont souvent des intérêts plus élevés, parce que leur défaut peut endommager des systèmes entiers.

---

## 12. Dette technique comme dette réelle

La dette technique est comptabilisée comme une dette Q réelle.

| Dette | Signification |
|---|---|
| -Q1 | tâche de base non résolue |
| -Q2 | problème non décomposé |
| -Q3 | modèle manquant |
| -Q4 | précision formelle manquante |
| -Q5 | implémentation manquante |
| -Q6 | spécification manquante |
| -Q7 | responsabilité floue |
| -Q8 | bibliothèque ou réutilisation manquante |
| -Q9 | cadre manquant |
| -Q10 | contraintes manquantes |
| -Q11 | interface cassée |
| -Q12 | outil manquant |
| -Q13 | service manquant |
| -Q14 | dette de coordination |
| -Q15 | application non livrée |
| -Q16 | dette d’exploitation ou d’exécution |
| -Q17 | complexité non compressée |
| -Q18 | dette architecturale |
| -Q19 | capacité générative manquante |
| -Q20 | module manquant ou machine inachevée |

Un projet avec beaucoup de Q5, mais des Q10 et Q18 négatifs, semble productif mais est structurellement malade.

```text
+20 Q5
-10 Q10
-5 Q18
```

Cela signifie : beaucoup de code, mauvaise structure, mauvaise architecture.

---

## 13. Acteurs, division du travail et capacités

Les acteurs sont les ménages, entreprises, banques, validateurs, l’État, fonds de communs et partenaires commerciaux extérieurs.

Les capacités sont décrites par un profil Q :

```text
Agent A :
Q1: 0.8
Q2: 0.7
Q3: 0.5
Q5: 0.9
Q6: 0.4
Q10: 0.3
Q18: 0.1
```

Cela signifie : fort pour reconnaître et coder, faible en structure et architecture.

Les métiers émergent selon les types de pièces :

```text
Analyste Q1/Q2 : trouve et décompose les problèmes
Théoricien Q3/Q4 : modélise et formalise
Programmeur Q5 : implémente
Spécificateur Q6 : décrit déclarativement
Coordinateur Q7 : délègue et référence
Bibliothécaire Q8 : construit des composants réutilisables
Constructeur de frameworks Q9 : crée des cadres
Ingénieur des contraintes Q10 : fixe limites et structure
Designer d’interfaces Q11 : relie les systèmes
Toolsmith Q12 : construit des outils
Constructeur de services Q13 : crée des services
Orchestrateur Q14 : compose les processus
Constructeur d’applications Q15 : crée des œuvres utilisables
Ingénieur d’exploitation Q16 : stabilise l’exécution
Compresseur Q17 : condense la complexité
Architecte Q18 : construit des formes porteuses
Constructeur de générateurs Q19 : bâtit des systèmes génératifs
Constructeur de modules Q20 : livre des machines terminées
```

---

## 14. État, impôts et communs

L’État protège la monnaie, stabilise les crises et finance les communs. Les impôts peuvent être levés en VL :

```text
impôt sur le revenu : pourcentage de la valeur nominale
taxe sur les transactions : faible prélèvement sur les échanges
taxe sur la dette : supplément sur l’effet de levier risqué Q18/Q20
```

Les dépenses publiques soutiennent surtout :

```text
Q8 bibliothèques
Q9 frameworks
Q12 outils
Q16 infrastructure
éducation
validation
sécurité publique
```

Les règles antimonopoles sont importantes, car Q8, Q9, Q16, Q18 et Q20 peuvent contrôler les conditions de production. Les moyens sont interfaces ouvertes, obligation d’interopérabilité, licences obligatoires, contributions aux communs et, si nécessaire, démantèlement.

---

## 15. Inflation, déflation et crises

L’inflation ne signifie pas seulement une hausse des prix. Elle signifie qu’un type de pièce est multiplié sans couverture sémantique suffisante.

```text
Inflation Q5  = beaucoup de code sans spécification, contraintes et architecture
Inflation Q13 = beaucoup de services sans fiabilité
Inflation Q18 = architecture proclamée sans construction porteuse
Inflation Q20 = modules inachevés vendus comme machines
```

La déflation signifie : trop peu de pièces valides pour les tâches existantes. Exemple : beaucoup de tâches Q1, mais trop peu de Q5, Q10 et Q18.

Crise typique :

```text
Q5:  très haut
Q13: haut
Q15: haut
Q10: bas
Q16: bas
Q18: bas
```

Cela signifie : beaucoup de code et d’applications, mais trop peu de structure, d’exploitation et d’architecture. La crise se manifeste par des pannes, problèmes d’intégration, failles de sécurité et retard de maintenance.

La politique de crise ne doit pas imprimer de l’argent aveuglément. Elle doit renforcer les types de pièces manquants.

---

## 16. Qualité, réputation et propriété

Toutes les pièces d’un même type n’ont pas la même qualité. Classes de qualité :

```text
A = vérifié, stable, réutilisable
B = utilisable, mais limité
C = expérimental
D = problématique
F = invalide ou échoué
```

Q18-A vaut plus que Q18-C, même si les deux valent nominalement 4 VL.

La réputation est suivie par type de pièce :

```text
Agent A :
réputation Q5 : 90
réputation Q6 : 60
réputation Q10 : 45
réputation Q18 : 20
```

La propriété existe sur les pièces, les artefacts et les droits d’usage :

```text
propriété de pièces : 5 × Q10
propriété d’artefact : programme, bibliothèque, machine
droit d’usage : licence sur Q8, Q9 ou Q20
```

---

## 17. Économie des licences et commerce des tâches

Les bibliothèques Q8, frameworks Q9, services Q13, applications Q15 et modules Q20 peuvent être licenciés.

Exemple :

```text
Bibliothèque Q8 :
usage unique : 1 VL
usage commercial : 2 Q5 par mois
licence open commons : financement public
```

Les tâches peuvent aussi être échangées. Q1 est une matière première : une bonne tâche, question de recherche ou demande client peut être achetée et vendue. Une bonne tâche est précieuse, car elle peut devenir la base d’une chaîne Q1→Q20.

---

## 18. Chaîne de valeur Q1 → Q20 et intelligence

Le mouvement économique central :

```text
Q1 → Q20
tâche → machine
```

Chaîne complète :

```text
Q1  reconnaître la tâche
Q2  décomposer la tâche
Q3  former un modèle
Q4  formaliser
Q5  implémenter
Q6  déclarer
Q7  déléguer
Q8  construire une bibliothèque
Q9  créer un framework
Q10 poser des contraintes
Q11 construire des interfaces
Q12 fournir des outils
Q13 créer un service
Q14 orchestrer des services
Q15 construire une application
Q16 sécuriser l’exploitation
Q17 compresser la complexité
Q18 construire l’architecture
Q19 permettre la génération
Q20 livrer le module/la machine
```

L’intelligence est une capacité de transformation :

```text
Intelligence = capacité de transformer Q1 en formes Q supérieures
```

Transformation basse :

```text
Q1 → Q5 = la tâche devient du code
```

Transformation haute :

```text
Q1 → Q18 → Q19 → Q20 = la tâche est architecturée, rendue générative et livrée comme machine
```

---

## 19. Bourse, indice des prix, masse monétaire et insolvabilité

Sur la bourse Q, les pièces ont des prix de marché. Exemple :

| Pièce | Nominal | Prix de marché |
|---:|---:|---:|
| Q1 | 1 | 0,8 |
| Q5 | 2 | 2,4 |
| Q8 | 2 | 3,1 |
| Q10 | 3 | 5,0 |
| Q13 | 3 | 3,6 |
| Q18 | 4 | 9,5 |
| Q20 | 4 | 7,8 |

L’indice de prix Q mesure un cycle de développement typique :

```text
4 × Q1
2 × Q5
2 × Q8
2 × Q10
1 × Q13
1 × Q16
1 × Q18
1 × Q20
```

La masse monétaire est mesurée par type de pièce :

```text
M(Q18) = quantité de pièces Q18 valides
L(Q18) = dette ouverte en Q18
```

Situation dangereuse :

```text
L(Q18) très élevé
M(Q18) bas
```

C’est une crise de dette architecturale.

L’insolvabilité peut être nominale ou sémantique. L’insolvabilité nominale signifie que les dettes totales dépassent les actifs totaux. L’insolvabilité sémantique signifie que la valeur totale suffit, mais que les bons types de pièces manquent.

---

## 20. Recherche, commerce extérieur et continuum R

La recherche crée surtout :

```text
Q1 nouvelles tâches
Q3 nouvelles abstractions
Q4 nouveaux objets formels
Q12 nouveaux outils
Q17 compressions
Q19 principes génératifs
```

Le commerce extérieur relie la Q-économie à d’autres économies. Q8, Q9, Q13, Q15, Q18 et Q20 sont particulièrement exportables. Les importations comprennent matières premières, matériel, énergie, données, travail et capital.

Le continuum R est l’exécution réelle ou la réalité pratique. La valeur Q devient particulièrement forte lorsqu’elle passe dans un effet R :

```text
Q18 architecture + Q20 module → machine réelle → valeur R
Q13 service + Q16 exploitation → service en fonctionnement → utilité R
```

---

## 21. Ledger triple-store, contrats et simulation

La comptabilité se fait comme un registre sémantique en triplets :

```text
(sujet, prédicat, objet)
```

Exemples :

```text
(Agent A, possède, 3 × Q10)
(Agent A, doit, 1 × Q18 à Agent B)
(Projet P, nécessite, 2 × Q5)
(Projet P, produit, 1 × Q13)
(Q17, opération inverse, décompression)
```

Un contrat contient :

```text
parties
objet livré
signature Q
prix
échéance
classe de qualité
sanction
validation
```

La simulation fonctionne par périodes :

```text
1. Des tâches apparaissent.
2. Les acteurs choisissent des actions.
3. Les marchés ouvrent.
4. La production se déroule.
5. Les résultats sont validés.
6. Les pièces sont frappées ou refusées.
7. Les paiements sont comptabilisés.
8. Les dettes sont mises à jour.
9. Les prix sont ajustés.
10. La réputation est mise à jour.
11. L’État et l’hôtel des monnaies réagissent.
```

---

## 22. Lois de la Q-économie

```text
1. Loi de la pièce : chaque pièce Q a un numéro, une valeur de ligne et une signification.
2. Loi d’addition : les valeurs des pièces s’additionnent selon la hauteur de ligne.
3. Loi sémantique : même valeur nominale ne signifie pas même fonction.
4. Loi de dette : les soldes négatifs de pièces sont des dettes.
5. Loi d’inversion : 1/Qi est une opération inverse, -Qi est une dette.
6. Loi de production : la production transforme la difficulté Q1 en formes Q supérieures.
7. Loi de validation : les nouvelles pièces naissent seulement d’une prestation vérifiée.
8. Loi de prix : les prix de marché viennent du nominal, de la rareté, de la qualité, du risque et de la confiance.
9. Loi de solvabilité : la santé exige solvabilité nominale et solvabilité sémantique.
10. Loi de stabilité : les pièces hautes doivent être couvertes par structure, exploitation et architecture.
```

---

## 23. Définition finale

La Q-économie est un ordre monétaire, de crédit et de production sémantique.

Sa monnaie se compose de Q1 à Q20. La valeur de chaque pièce est sa hauteur de ligne. Les pièces peuvent être additionnées, échangées, prêtées et dues. Les dettes sont des soldes Q négatifs. Les opérations inverses s’écrivent 1/Qi et ne sont pas des dettes.

La production est la transformation de la difficulté en formes structurées, exécutables et réutilisables. La richesse naît lorsque des tâches Q1 deviennent un effet réel grâce au code Q5, à la structure Q10, aux services Q13, à l’architecture Q18 et aux modules Q20.

Les crises naissent lorsque la richesse nominale et la solvabilité sémantique divergent. La stabilité naît de la validation, des interfaces ouvertes, d’une bonne architecture, des dettes visibles et des communs publics.

**Phrase centrale :** Cette économie ne paie pas simplement le travail. Elle paie la transformation réussie de la difficulté en intelligence fonctionnelle.
