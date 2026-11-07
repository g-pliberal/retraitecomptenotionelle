# Un âge plancher de 62 ou de 64 ans, chiffré face aux 65 ans de la proposition

*Le 7 novembre 2026, le propriétaire veut le chiffre avant de choisir l'âge
(décisions 31 à 33, « Chiffrer avant de choisir ») : la piste « la liberté de
l'âge » du chantier 8 contredit l'âge légal de départ de 65 ans de la
proposition. Une session du modèle mesure ce que coûterait un âge plancher de
62 ou de 64 ans, la pension restant celle du compte actuariel. Les chiffres
portent leur origine : **(modèle)**, le modèle du dépôt au commit `584fad0`,
sous les réglages de la page Coût, le seul paramètre `age_legal_liberal`
changé ; **(à côté)**, un calcul fait à côté du modèle, qui en garde tout
sauf ce qu'il dit changer. Aucune ligne du code ni des données n'a changé.*

## L'essentiel

**(modèle)** Le scénario 6, variante rétroactive, en points de PIB, sous les
trois âges ; « aucun » retire la mesure, et la proposition part alors aux
âges du droit en vigueur.

| Âge plancher | 62 ans | 64 ans | **65 ans** (la proposition) | aucun |
|---|---:|---:|---:|---:|
| Solde du régime, 2026 | -2,52 | -2,34 | -2,19 | -2,59 |
| Solde du régime, 2040 | -2,17 | -2,06 | -1,92 | -2,29 |
| Solde du régime, 2070 | -0,03 | -0,01 | +0,05 | -0,00 |
| **Solde moyen, 2026-2070** | **-1,67** | **-1,57** | **-1,44** | -1,72 |
| Solde moyen, garantie comprise | -1,92 | -1,82 | -1,69 | -1,97 |
| Dette accumulée en 2070 | +120 | +112 | +103 | +124 |
| Écart moyen à 65 ans, garantie comprise | -0,23 | -0,13 | — | -0,29 |

Le système actuel a un solde moyen de -1,13 sur la même période. Les
niveaux comprennent les réversions servies à la bascule, que le scénario 6
garde depuis le commit `553e8ca` (décisions 16 à 28) : ils ont baissé de
1,4 point en 2026 ce jour-là, et bougeront encore avec le portage de la
réversion. Les **écarts** entre les âges n'en dépendent pas : mesurés avant
et après ce commit, ils sont les mêmes au millième. Avant lui, le calcul à
65 ans refaisait au centième le chiffrage publié (`docs/chiffrage_plf.md` :
-0,79, -1,48 et +0,05 ; -1,08 en moyenne ; +74 de dette).

Ce que le tableau dit : **le plancher n'est pas neutre pour le budget de la
transition, même quand le compte l'est pour le régime.** Un plancher de
62 ans coûte en moyenne 0,22 point de PIB par an de 2026 à 2070 ; 64 ans,
0,13 ; supprimer tout âge, 0,28. La proposition n'atteint l'équilibre en 2070
qu'à 65 ans.

## Ce qui fait l'écart

**(modèle)** Les trois composantes, écart à 65 ans ; un signe négatif
creuse le solde.

| Écart à 65 ans | Pensions servies | Cotisations | Garantie | Solde, garantie comprise |
|---|---:|---:|---:|---:|
| 62 ans, moyenne 2026-2070, points de PIB | +0,075 | -0,146 | +0,007 | -0,228 |
| 64 ans, moyenne 2026-2070, points de PIB | +0,036 | -0,092 | +0,004 | -0,132 |
| 62 ans, 2026, Md€ courants | +7,9 | -2,2 | +0,0 | -10,1 |
| 62 ans, 2030 | +10,5 | -6,9 | +0,1 | -17,5 |
| 62 ans, 2040 | +4,8 | -6,0 | +0,4 | -11,2 |
| 62 ans, 2050 | +0,2 | -8,1 | +0,4 | -8,7 |
| 62 ans, 2070 | -5,8 | -11,8 | +0,7 | -6,8 |
| 64 ans, 2026, Md€ courants | +3,4 | -1,3 | +0,0 | -4,6 |
| 64 ans, 2030 | +5,1 | -3,6 | +0,1 | -8,7 |
| 64 ans, 2070 | -3,0 | -7,6 | +0,4 | -5,0 |

- *Les pensions servies plus tôt* font l'écart des premières années :
  8 milliards en 2026, 10,5 en 2030, pour un plancher de 62 ans. Elles
  s'inversent après 2050 : qui est parti plus tôt touche une pension plus
  petite, et la masse des pensions est plus faible que sous 65 ans. C'est le
  compte actuariel : les cotisations de plus reviennent en pensions de plus.
- *Les cotisations en moins* durent : l'âge de 65 ans élargit l'assiette des
  revenus d'activité de 2,4 %, 64 ans de 1,2 %, 62 ans de 0,5 % (moyennes de
  `facteur_assiette`). C'est elles qui font l'essentiel de l'écart moyen, et
  tout l'écart d'après 2050.
- *La garantie vieillesse*, ouverte à 65 ans dans les trois cas, ne bouge
  presque pas : les pensions plus faibles de qui est parti plus tôt la font
  servir un peu plus après 65 ans, 0,007 point en moyenne.

## Ce que perd, par mois, qui part plus tôt

**(modèle)** La pension du scénario 6, pilier capitalisé compris, en euros
de 2026 par mois, selon l'âge de départ : le même cas type, qui part à
62 ans sans plus cotiser, ou travaille jusqu'à 63, 64 ou 65 ans. Les cas
types sont ceux du site, simulés par le portage sans plancher.

| Cas type, génération | Départ sous le droit | 62 ans | 64 ans | 65 ans | Perte à 62 ans | Perte à 64 ans |
|---|---:|---:|---:|---:|---:|---:|
| SMIC, carrière complète, 1970 | 61 ans ¾ | 1 005 | 1 150 | 1 229 | -224 (18 %) | -79 (6 %) |
| SMIC, carrière complète, 1990 | 62 ans | 1 068 | 1 207 | 1 284 | -216 (17 %) | -77 (6 %) |
| Salaire moyen, 1970 | 64 ans | 1 600 | 1 838 | 1 968 | -368 (19 %) | -130 (7 %) |
| Salaire moyen, 1990 | 64 ans | 1 740 | 1 975 | 2 105 | -366 (17 %) | -130 (6 %) |
| Carrière interrompue, 1970 | 64 ans | 1 293 | 1 495 | 1 606 | -314 (20 %) | -111 (7 %) |
| Carrière interrompue, 1990 | 64 ans | 1 412 | 1 616 | 1 728 | -316 (18 %) | -112 (6 %) |
| Cadre, 1970 | 66 ans | 2 903 | 3 387 | 3 653 | -750 (21 %) | -266 (7 %) |
| Cadre, 1990 | 66 ans | 3 310 | 3 811 | 4 088 | -778 (19 %) | -277 (7 %) |

Chaque année de départ anticipé coûte 6 à 7 % de la pension mensuelle, pour
toute la retraite : une année de cotisations en moins, et un diviseur plus
grand. Le salarié au SMIC, en carrière longue, part aujourd'hui à 62 ans ou
avant ; 65 ans le fait attendre trois ans, 62 ans le laisse partir, avec
216 à 224 € de moins par mois que s'il avait travaillé jusqu'à 65.

## Le trou entre le départ et la garantie

La garantie vieillesse s'ouvre à 65 ans, l'âge de l'ASPA
(`MinimumVieillesse.AGE_OUVERTURE`). Sous un plancher de 62 ans, le salarié
au SMIC de la génération 1970 part avec 1 005 € par mois **(modèle)**, sous
les 1 050 € d'une personne seule : rien ne le complète avant 65 ans. Celui de
1990, avec 1 068 €, passe juste au-dessus.

**(à côté)** Si la garantie suivait le plancher : le même coût, la garantie
ouverte au départ de chacun, ou à l'âge plancher pour qui est parti avant
lui. On ne change que l'année d'ouverture de chaque départ
(`cout._volet`, remplacé le temps du calcul sous `memoire.modele_modifie()`) ;
le barème, la distribution déplacée des pensions, le recours de moitié et la
reprise sur la succession restent ceux du modèle.

| La garantie ouverte au plancher | 62 ans | 64 ans |
|---|---:|---:|
| Ayants droit de plus, 2026 | 656 000 | 255 000 |
| Bénéficiaires de plus, au recours de moitié, 2026 | 328 000 | 127 000 |
| Dépense de plus, 2026, Md€ de 2026 | 1,7 | 0,65 |
| Bénéficiaires de plus, de 2040 à 2070 | 200 000 | 85 000 |
| Dépense de plus, de 2040 à 2070, Md€ de 2026 par an | 1,0 | 0,43 |
| Moyenne 2026-2070, points de PIB, brute | +0,031 | +0,013 |
| Moyenne 2026-2070, nette de la reprise sur succession | +0,021 | +0,009 |

À 65 ans, la garantie a 5,5 millions d'ayants droit en 2026, dont 2,8 la
réclament, pour 14,1 milliards. Ouvrir la garantie au plancher y ajouterait
12 % en 2026 à 62 ans, et moins de 5 % à 64 ans. Ce calcul lit, pour les
partants de 62 à 64 ans, la distribution des pensions de tous les retraités,
déplacée de leur moyenne : s'ils sont plus modestes que les autres, il les
sous-compte. Le choix n'est pas tranché ici.

## L'hypothèse de comportement

Celle du modèle : **chacun part à l'âge que le droit en vigueur donne à sa
génération, mais pas avant le plancher**, et la moitié de ceux que le
plancher fait attendre travaillent jusqu'à lui
(`Parametres.part_reportes_en_emploi`, IPP, rapport n° 61). Un plancher de
62 ou de 64 ans ne touche donc que ceux que le droit fait partir plus tôt :
les carrières longues, les catégories actives, les inaptes. Personne ne part
plus tôt que sous le droit. Or, sous la liberté de l'âge, certains de ceux
qui partent à 64 ans aujourd'hui partiraient à 62 ou 63 ans, avec une
pension plus petite. **Le coût d'un plancher de 62 ans est donc une borne
basse.** Le modèle ne sait pas faire partir la grille avant l'âge du droit ;
cette hypothèse inverse n'est pas chiffrée.

## Reproduire

- Le solde : `memoire.cout(Parametres(age_legal_liberal=62.0))`, lu comme
  `scripts/chiffrage_plf.py` lit le sien (`Chiffrage`), vingt-cinq secondes
  par âge.
- Les pensions : `pont.carrieres`, sur `CasType.options(génération, âge)`,
  sous `Parametres(age_legal_liberal=None)`, scénario `notionnel_liberal` ;
  la pension totale ramenée aux euros de 2026 par le déflateur de la pension
  du système actuel (`pensions_euros_constants`).
- La garantie au plancher **(à côté)** : `memoire.cout` sous le plancher, une
  fois tel quel, une fois `cout._volet` remplacé par une fonction qui avance
  `annee_ouverture_garantie` de 65 ans moins le plancher, sans la faire
  passer avant `annee_liquidation` ; on lit `ligne.garantie` (ayants droit,
  bénéficiaires, `cout_constants`) et `part_pib`, ligne par ligne de
  `cout.avenir`.

## Ce que le propriétaire tranche

Deux questions : l'âge plancher, 62, 64 ou 65 ans ; et, sous 65 ans, si la
garantie s'ouvre au plancher ou reste à 65 ans.

## Ce que le propriétaire a tranché, le même jour

Sur le tableau des trois âges, aux deux questions posées avec leurs
options : l'âge, « 65 ans » ; la garantie, « Reste à 65 ans » (décision 68 de
`docs/feuille_de_route_programme.md`). Le défaut de la proposition ne
change pas, ni le modèle, ni le site : le message des 45-62 ans sera celui de
65 ans, « comme nos voisins », et non la liberté de l'âge. La consigne
donnait à cette décision le numéro 34 ; d'autres sessions l'avaient pris
entre-temps, elle prend le premier libre.
