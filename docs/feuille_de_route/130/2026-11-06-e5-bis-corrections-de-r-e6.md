# Les corrections de la relecture R-E6 : la CPRN et la CARPIMKO, reprises à la source

File E5-bis de la vague 11, les 5 et 6 novembre 2026 : les écarts faibles que la relecture R-E6
(`2026-11-05-relecture-r-e6.md`) laisse sur le travail d'E5 (la CPRN,
`cprn_ages_decote_enfants`, note `2026-11-05-carte-des-fiches-cprn-lue-au-droit.md`) et sur les
chiffres d'E4-bis (`carpimko_ages_2015`, note `2026-11-05-e4-bis-corrections-de-r-e5.md`).
**Aucune règle, aucune donnée servie, aucun test ne change** : seule la prose de deux fiches, et
un chiffre du bloc « Reprise ». Chaque retouche a rouvert sa source dans l'index de la DILA
(`dila_index.py jorf --recuperer`, JORF à jour au 3 novembre 2026, `dila_cherche.py --texte`,
`--motif`) ou refait son calcul en décimal ; R-E6 n'a pas servi de preuve.

## A. La CPRN

### Les trois arrêtés, et cinq textes au seul Bulletin officiel

Relus dans l'index :

- arrêté du 2 août 1963, JORFTEXT000000437564, JO du 15 août 1963 : « APPROBATION DE
  MODIFICATIONS APPORTEES AU REGLEMENT DE LA SECTION PROFESSIONNELLE DES NOTAIRES », titre seul ;
- arrêté du 20 novembre 1964, JORFTEXT000000620399, JO du 1er décembre 1964 : « APPROBATION DES
  MODIFICATIONS APPORTEES A L'ART. 8 ET DE L'ADJONCTION DES ART. 20-BIS,50 A 55 DU REGLEMENT [...] »,
  titre seul ;
- arrêté du 21 février 2001, JORFTEXT000000753863, JO du 24 février 2001 : « sont approuvées telles
  qu'elles sont annexées (1) au présent arrêté les modifications apportées au règlement de la
  section professionnelle des notaires relatives au régime d'assurance vieillesse complémentaire
  (art. 30, 36, 39, 40, 41 et 47) » (JORFARTI000002396641) ; « (1) Cet arrêté accompagné de ses
  annexes paraîtra dans un prochain Bulletin officiel » (JORFARTI000001924450).

Les textes au seul Bulletin officiel, chacun avec sa phrase relue : le 9 juin 1980 (« CET ARRETE
SERA PUBLIE INTEGRALEMENT AU BULLETIN OFFICIEL », JORFTEXT000000314300) ; le 19 avril 1983
(« PUBLICATION INTEGRALE DE CET ARRETE AU BO », JORFTEXT000000652420) ; le 12 septembre 1990 (« LE
PRESENT ARRETE SERA PUBLIE AU BULLETIN OFFICIEL 90-42 », JORFTEXT000000533318) ; le 16 décembre 1996
(« Nota. - L'arrêté du 16 décembre 1996 sera publié intégralement au Bulletin officiel no 97-03 »,
JORFARTI000002135074) ; le 21 février 2001 (ci-dessus). **Cinq, non trois**. La fiche les dit
maintenant dans l'hypothèse de `reglement_d_avant_2005`, dans son approximation et dans son « à
relire ». Aucun ne se lit : la version reste supposée, aucun chiffre ne bouge. (Les décrets n°
83-519 et 2001-179, que R-E6 relève hors de l'âge, ne font pas partie des retouches demandées :
non rouverts ici, candidats.)

### L'âge d'avant 2014 : deux phrases reprises

Relu, l'arrêté du 16 décembre 2013, annexe (JORFARTI000028387445), article 15 : « avant le premier
alinéa, sont insérés neuf alinéas ainsi rédigés [...] ― le dixième alinéa est ainsi rédigé : «
Toutefois, le conseil d'administration peut accorder à celui que des infirmités ou une maladie
grave ont contraint de cesser ses fonctions et rendent inapte [...] » ; ― au onzième alinéa, les
mots : « d'un médecin agréé par la caisse » sont remplacés [...] ; ― le douzième alinéa est ainsi
rédigé : « 2° Une attestation du président de la chambre [...] » » ; puis « L'article 16 est ainsi
rédigé ».

1. La fiche disait « le premier alinéa de l'article 15, le seul que l'arrêté de 2013 laisse voir,
   n'excepte que l'inapte ». L'arrêté ne montre pas l'ancien alinéa : il le récrit. Ce qu'on lit est
   sa rédaction de 2014 ; que l'ancien visât l'inapte se déduit des onzième et douzième alinéas,
   modifiés par mots seulement. L'ancien article 16, récrit en entier, n'est pas lu : il a pu porter
   une liquidation anticipée. La fiche le dit ; le non-tranché ne tombe pas, la lecture du modèle
   en reçoit un appui.
2. La fiche disait « rien ne dit que la phrase date de 2005 » (et, dans l'hypothèse de
   `statuts_de_2005`, « ni rien qui dise si ces phrases datent de 2005 »). Relu dans l'index, du
   28 décembre 2004 (JORFARTI000001075201, JO du 4 février 2005) à l'arrêté du 16 décembre 2013
   (JO du 27 décembre 2013), deux requêtes, l'une sur le titre « section professionnelle des
   notaires », l'autre sur « assurance vieillesse » et « notaires » et « statuts ou règlement » dans
   les textes de 2004 à 2014, ne rendent qu'une approbation de modifications de ces statuts : celle
   du 27 février 2008, JORFARTI000018229446, qui ne récrit que l'article 20 (« L'article 20 des
   statuts annexés à l'arrêté du 28 décembre 2004 susvisé est rédigé comme suit »). Le décret n°
   2013-1157 (articles 1er et 2) remplace l'article 2 du décret de 1949, les sections et les classes
   de cotisation, et fixe une période transitoire. Sauf une modification que le Journal officiel n'aurait
   pas mentionnée, la phrase de l'article 14 est celle des statuts de 2005 : la fiche le dit,
   avec cette réserve. Le texte de 2005 reste à lire ; le non-tranché tient.

### Le passage de 2024 : deux égalités au centime, et une précision

Posées en décimal, à partir des valeurs écrites dans la fiche (14 679,08 € ; 0,85 ; 0,7875 ; 0,80),
puis sans arrondi intermédiaire :

| Égalité | Sur le papier, valeurs écrites | Sans arrondi intermédiaire |
|---|---|---|
| 0,7875 | 1 − 17 × 0,0125 = 0,7875 | |
| 0,80 | 1 − 16 × 0,0125 = 0,80 | |
| annuel à 0,7875 | 14 679,08 / 0,85 × 0,7875 = 13 599,7359 → **13 599,74** | |
| quinze mois à 0,7875 | 13 599,74 × 15 / 12 = **16 999,675** → 16 999,68 | 14 679,08 / 0,85 × 0,7875 × 15 / 12 = 16 999,6699 → 16 999,67 |
| trop par an | 14 679,08 − 13 599,74 = **1 079,34** | |
| annuel à 0,80 | 14 679,08 / 0,85 × 0,80 = 13 815,6047 → **13 815,60** | |
| quinze mois à 0,80 | 13 815,60 × 15 / 12 = **17 269,50** | 14 679,08 / 0,85 × 0,80 × 15 / 12 = 17 269,5059 → 17 269,51 |
| trop par an | 14 679,08 − 13 815,60 = **863,48** | |

La fiche écrivait « = 16 999,67 » et « 17 269,51 » à la suite de 13 599,74 et de 13 815,60 : sur le
papier, ces deux égalités étaient fausses d'un centime (13 599,74 × 15 / 12 = 16 999,675, qui
s'arrondit au demi supérieur à 16 999,68 ; 13 815,60 × 15 / 12 = 17 269,50 exactement). Elle écrit
maintenant la chaîne sur le papier, 16 999,68 € et 17 269,50 €, et dit entre parenthèses ce que
donne le calcul sans arrondir l'annuel, 16 999,67 € et 17 269,51 €. Les chiffres de tête de la
note d'E5, du message de commit de 5f6196d et de l'ancien bloc « Reprise » sont ceux de la chaîne ;
le bloc « Reprise » porte désormais 16 999,68 €. Aucune valeur servie ne bouge : ce sont des
chiffres d'une erreur déclarée, non corrigée, que le modèle ne sert pas.

Le « 1 079,34 € par an de trop » : relue, la règle des statuts (article 19 de 2017,
JORFARTI000034975971 : « Le droit à l'allocation est fixé au premier jour du mois civil qui suit la
date de fin d'exercice ou la date souhaitée par l'affilié ») permet au notaire de liquider le 1er
janvier 2024 comme le 1er avril 2025. Les 1 079,34 € comparent donc deux dates de liquidation
permises toutes deux ; ils ne valent que dans la règle du modèle, servir chaque caisse dès son
ouverture. La fiche le dit (même chose pour 863,48 €). Les quinze mois non servis, eux, sont bien
le défaut de date d'ouverture.

## B. La CARPIMKO : l'écart d'un centime, et un second

Posés en décimal, à partir de l'écrit (5 681,23 € par an, 1,0375, 1,0125) :

| Égalité | Du montant écrit | Dans la fiche |
|---|---|---|
| 5 681,23 / 1,0375 | 5 475,8843 → **5 475,88** | 5 475,89 → **5 475,88** |
| 5 681,23 / 1,0375 × 1,0125 | 5 544,3329 → **5 544,33** | 5 544,34 → **5 544,33** |
| 5 681,23 − 5 475,88 | 205,35 | 205,35 inchangé |
| 5 681,23 − 5 544,33 | 136,90 | 136,90 inchangé |

Les deux intermédiaires écrits, 5 475,89 et 5 544,34, étaient ceux du montant servi non arrondi
(5 681,2345 : 5 681,2345 / 1,0375 = 5 475,8887, × 1,0125 = 5 544,3373) ; écrits après le dividende
arrondi 5 681,23, ils laissaient un centime de trop, et 5 681,23 − 5 475,89 = 205,34 et 5 681,23 −
5 544,34 = 136,89 ne tombaient pas sur 205,35 et 136,90. Du montant servi, les deux différences sont
205,3458 et 136,8972, soit 205,35 et 136,90 : **les deux montants sont les mêmes par les deux
chemins**. Le montant servi, 5 681,2345, est celui que R-E5 et R-E6 relèvent dans les deux moteurs ;
il n'a pas été rejoué ici, la retouche ne portant que sur l'écriture. Corrigés dans `carpimko_ages_2015`,
aux quatre lieux de R-E6 : les approximations de l'âge de la génération 1955 (« 5 475,88 € sans
coefficient », « 5 544,33 € ») et de la majoration avant l'âge légal (« 5 681,23 / 1,0375 × 1,0125 =
5 544,33 € », « 5 681,23 / 1,0375 = 5 475,88 € »). La note d'E4-bis, qui garde les anciens chiffres,
est un récit : elle porte déjà le renvoi de R-E6, et en reçoit un second.

## Les tests, et le paquet

`construire_donnees.py` ne change pas `moteur/donnees.json` : le paquet ne lit pas la prose de ces
deux fiches. `python -m pytest -m rapide` : 4 461 réussis, 51 sautés ; sous
`PRESOMPTIONS_DECALEES=1` : 4 256 réussis, 256 sautés ; `tests/test_sections_juridiques.py`,
`test_sections_liberales.py`, `test_sections_sante.py` et `test_carte.py`, en entier, tous niveaux :
139 réussis ; `test_conservation.py` : 9 réussis ; `verifier_prose.py --corriger` : la prose dit le
vrai. `conservation.py --depuis HEAD` signale deux « pertes », voulues : le bloc « Reprise » de
l'action 130, seul paragraphe qui se récrit, et l'entrée de veille de la CPRN, dont le « à relire »
reçoit les trois derniers arrêtés au Bulletin officiel. Aucun test neuf : la prose de deux fiches
ne se teste pas, et aucune valeur servie ne bouge.

## Ce que la retouche laisse

- **Rien au propriétaire** : l'erreur de la CPRN et les non-tranchés de la CPRN, de la CAVP et de la
  CARPIMKO sont tels qu'E5 et E4-bis les déclarent, confirmés par R-E6 et par cette reprise ; leurs
  montants sont ceux des deux moteurs.
- **Candidats, non lancés** (déjà dans le bloc « Reprise ») : lire les statuts de la CPRN d'avant 2014
  et les cinq arrêtés de 1980 à 2001, au seul Bulletin officiel, auprès de la caisse ou de la
  direction de l'information légale et administrative.
