# Relecture de la fiche 5 et du taux effectif (file A)

File R-A, le 3 novembre 2026 : relecture indépendante des commits 0521e59,
127aa4a et a78366a (session A, actions 178, étape 2, et 138, étape 3 ; note
`2026-11-03-etape-2-fiche-5-pensions-de-2023-et-2024.md`). Chaque source a
été téléchargée ici de son miroir et vérifiée à son empreinte, sans rien
reprendre de la session ni de mémoire ; chaque chiffre a été refait par des
scripts écrits pour la relecture, hors du dépôt. Rien n'a été modifié : ni
donnée, ni code, ni test, ni bloc « Reprise » ; le paquet refait pour la
vérification l'a été hors commit, puis remis en l'état.

**Verdict.** **Conforme** sur tous les points décisifs : les empreintes, les
huit cellules et leur champ, les 60 valeurs de 2008 à 2022, le taux de chaque
année, la masse nette de 2024 et le bilan de 2026 se refont à l'euro et au
centième près ; les deux moteurs rendent ces valeurs, et le paquet de `main`
porte la part de A. **Écarts** : deux faibles — la conclusion sur le
« demi-point », plus nette dans le bloc « Reprise » et au journal de veille
que la preuve ne le permet (point 5) ; une affirmation sans source sur la
dépense servie à l'étranger (point 2) ; un négligeable — « page 55 du PDF »
est le folio 55, la page 56 du fichier (point 2).

## 1. Les sources, à leur empreinte

| Fichier | Où | SHA-256 | Constat |
|---|---|---|---|
| `drees_panorama_retraites_2026_classeurs.zip` | release `documents-apportes` | `ec7503f8…aaf64911` | celle du manifeste (`data/sources.yaml`), 36 membres : conforme |
| `fiche_05.xlsx`, membre de l'archive | | `e7cdfaf8…babf0af2` | celle de son champ `contenu` : conforme |
| PDF du panorama, édition 2026 | miroir de l'UNSA | `9eb36a06…86735e9be`, 9 983 866 octets | celle du manifeste : conforme |
| Tableau 2.1-a, fin 2022 | portail de la DREES (`1393_les-effectifs-et-montants-de-pension-des-retraites`) | — | `curl: (35) Recv failure: Connection reset by peer`, comme pour A ; aucune copie au dépôt (`data/brut/` est ignoré) : **non vérifié, faute de source** |

## 2. Les huit cellules et le champ

Feuille « F05_Tableau 1 compl_bis », lue par openpyxl 3.1.5 :

- B2 : « Tableau 1 complémentaire bis. Montant mensuel moyen de la pension
  des retraités résidant en France ou à l’étranger » ; dans B31, le champ :
  « Retraités ayant perçu un droit direct au cours de l’année n, résidant en
  France ou à l'étranger, vivants au 31 décembre de l’année. », et les
  sources : « Drees, EIR, modèle ANCETRE. » : conforme, mot pour mot.
- Les en-têtes : I5 « Pension de droit direct, y compris majoration pour 3
  enfants ou plus », I6 « Brute », I7 « Ensemble » ; L6 « Nette », L7
  « Ensemble » ; O5 « Pension totale (droit direct , droit dérivé et
  majoration pour 3 enfants ou plus) », O6 « Brute », O7 « Ensemble » ; R6
  « Nette », R7 « Ensemble » : conforme. Ce sont des pensions mensuelles
  moyennes, « en euros courants » (C4).
- B27 vaut 2023, B28 2024 ; I27 1 608, L27 1 495, O27 1 764, R27 1 643 ;
  I28 1 693, L28 1 573, O28 1 855, R28 1 727 ; chacune un entier, sans
  formule, au format `#,##0` : **conforme**, les huit, à la cellule.
- La série s'arrête à la ligne 28 : aucune année 2025, et le texte de la
  fiche parle de « fin 2024 ». 2024 est bien la dernière année publiée.
- Le tableau 1, des seuls résidents en France : feuille « F05_Tableau 1 »,
  B2 « … des retraités résidant en France » ; F27 1 752, G27 1 626, J27
  1 920, K27 1 785. Au PDF, folio 55, la ligne 2024 du tableau 1 : « 1 705
  1 383 2 186 1 752 1 626 1 668 2 216 1 920 1 785 », et son champ
  « … résidant en France, vivants au 31 décembre de l’année » : conforme.
- **Une preuve de plus**, que A ne cite pas : le texte de la fiche, au
  folio 54, imprime lui-même I28 : « s’élève à 1 752 euros (tableau 1),
  contre 1 693 euros pour l’ensemble des retraités résidant en France ou à
  l’étranger. »
- Le champ du fichier est bien « France et étranger », sans le tableau
  2.1-a : sa valeur de 2022, 1 719 € bruts toutes pensions, est O26 de la
  feuille complémentaire bis, et non J25 du tableau 1 (1 786 €).
- **Négligeable.** Le tableau 1 est au folio 55, qui est la page 56 du
  fichier PDF ; « page 55 du PDF » (la note, et le test
  `test_la_pension_moyenne_du_depot_est_celle_du_panorama_jusqu_en_2022`)
  s'entend du folio.
- **Faible.** « celui de la dépense à laquelle le modèle applique le taux,
  qui paie aussi les pensions servies à l'étranger, sans CSG » (la note,
  « Le champ ») n'a pas de source : l'en-tête de `pensions_droits.csv`
  (sous-postes E11-21.1 et E11-22.1 des comptes de la protection sociale) ne
  dit rien des pensions servies à l'étranger, et la note n'en cite aucune.
  Vraisemblable, non prouvé ; le choix du champ n'en dépend pas, que la
  continuité de la série de 2008 à 2022 suffit à fonder.

## 3. Les 60 valeurs de 2008 à 2022, et les 52 cases du test

- Les 68 lignes de `pensions_brutes_nettes.csv` (2008 à 2024, quatre
  indicateurs), confrontées par script aux colonnes I, L, O et R des lignes
  12 à 28 : 68 égales, aucun écart, toutes `certifiee`. Les 60 de 2008 à
  2022 sont celles du classeur à l'euro près : conforme. Les nettes de 2020
  à 2022 sont donc celles que la feuille dit révisées (B31 : « Après
  correction d'une erreur dans les taux de prélèvements appliqués, la
  pension nette a été révisée pour les années 2020 à 2022 par rapport à
  l'édition précédente de cet ouvrage. ») : la citation est exacte.
- La feuille réduite du test (`PENSIONS_MOYENNES_F05`,
  `tests/test_drees_panorama_2024.py`) : 52 cases, chacune confrontée à sa
  cellule du classeur : aucun écart. `PENSIONS_MOYENNES_2023_2024` et ses
  renvois de cellule : conformes.

## 4. Le taux effectif, refait

Un moins la nette sur la brute, toutes pensions (colonnes O et R : pension
mensuelle moyenne de l'ensemble, en euros courants) :

| Année | Brute | Nette | Brute − nette | Taux |
|---|---|---|---|---|
| 2022 | 1 719 (O26) | 1 602 (R26) | 117 | 6,806 % |
| 2023 | 1 764 (O27) | 1 643 (R27) | 121 | 6,859 % |
| 2024 | 1 855 (O28) | 1 727 (R28) | 128 | 6,900 % |

+0,094 point de 2022 à 2024 ; de droit direct (I et L), 108 / 1 565 =
6,901 % et 120 / 1 693 = 7,088 % : conforme à la note. Les tests posent ces
fractions (`1.0 - 1727.0 / 1855.0`, `1.0 - 1643.0 / 1764.0`), non une sortie
du code : conforme.

## 5. Ce que la source ne tranche pas

- Les citations de la note du 14 octobre
  (`138/2026-10-14-etape-3-csg-effective.md`, « Une réserve sur 2023 »,
  lignes 56 à 62) — 5,4 % et 6,1 %, 22,3 % et 30,3 % d'exonérés, 23,7 Md€,
  6,3 %, « près d'un point », « sans doute bas d'un demi-point » — sont
  exactes. Le « point 2 de son « Ce qui reste » » est celui de la note du
  24 octobre (`138/2026-10-24-etape-3-le-taux-effectif.md`, lignes 87 à
  89) : exact.
- Les chiffres de la CCSS et d'Ancetre : A les déclare cités, non relus ; je
  ne les ai pas relus non plus : **non vérifiés, faute de source ouverte**.
  Le tableau 2.1-a : non relu, déclaré (point 1).
- **Faible.** Le bloc « Reprise » (« le taux de 2022, tenu, n'était pas bas
  d'un demi-point ») et le journal de veille (« le demi-point que la note du
  14 octobre craignait n'y est pas ») concluent plus net que la preuve. Ce
  qui est prouvé : la mesure de la DREES ne monte que de 0,05 point en 2023
  (de 6,806 à 6,859 %), et c'est le critère que les notes du 14 et du
  24 octobre s'étaient donné. Ce qui ne l'est pas : la CCSS, telle que la
  note du 14 octobre la cite, compterait la CSG seule à 6,3 % des masses,
  « près d'un point » de plus avec la CRDS, la CASA et la cotisation
  maladie, soit de l'ordre de 7,3 %, contre 6,86 % : un écart d'environ
  0,4 point que la mesure de la DREES n'explique pas. Le corps de la note de
  A le déclare ouvert (« ces deux points restent ouverts ») ; la conclusion
  devrait dire « selon la mesure de la DREES ». Aucun chiffre n'en dépend.

## 6. La masse nette et le bilan de 2026, refaits

- *La masse de 2024* : `pensions_droits.csv`, droit direct 359 717,10 M€
  et dérivé 41 709,29 M€, soit 401 426,39 M€ ; le PIB de 2024,
  `pib_courant.csv`, 2 935 236 M€ ; 13,676 % du PIB (page : « 13,68 % en
  brut, 401 Md € »). Nette : 401 426,39 × 1 727 / 1 855 = 373 726,9 M€,
  12,732 % du PIB (page : « 12,73 % du PIB en 2024, 374 Md € ») ; avant,
  × 1 602 / 1 719 = 374 104,2 M€, 12,745 %, affiché 12,75 % : conforme. Ces
  deux séries sont certifiées au dépôt ; A n'y a pas touché, et je ne les ai
  pas reconfrontées à leurs sources.
- *Le bilan de 2026* (« Ressources et dépenses du système de retraite en
  2026 ») : la dépense brute du modèle, 14,1262 % du PIB pour le système
  actuel et 8,8828 % pour la proposition, convertie au point de PIB de 2025
  (2 991 056 M€) ; nette, × 1 727 / 1 855 : 393 367 M€, 13,151 % et
  93,10 % (affiché 393,4 Md €, 13,15 %, 93,1 %), 247 357 M€ et 8,270 %
  (247,4 Md €, 8,27 %, 93,1 %) ; avant, × 1 602 / 1 719 : 393 764 M€ et
  13,165 % (393,8 Md €, 13,16 %, 93,2 %), 247 607 M€ et 8,278 % (247,6 Md €,
  8,28 %) : conforme, avant et après.
- *Ce qui ne bouge pas* : des 1 289 lignes de tableau de `cout/index.html`,
  avant et après 127aa4a, une seule diffère, « Pour mémoire, dépenses nettes
  des prélèvements sociaux des retraités » ; le brut (422,5 et 265,7 Md €),
  le solde (−4,8 et −23,5 Md €) et les tableaux de la dette restent les
  mêmes. Le texte ne change qu'en trois passages (6,9 %, « mesure en 2024 »,
  12,73 %). Aucun témoin de simulation dans le commit ; `pages.js` et
  `cout.py` intacts ; `depenses.py` ne change qu'en commentaires et
  docstrings ; la page Méthode passe à 226 séries et 441 779 valeurs (+1,
  +8) : conforme.

## 7. Les tests, les deux moteurs et le paquet

- Les fichiers de A (`test_drees_panorama_2024.py`, `test_depense_nette.py`,
  `test_cout.py`, `test_agregats.py`, `test_donnees.py`) : 389 verts.
- Sous `PRESOMPTIONS_DECALEES=1` : les deux fichiers `rapide` de A et
  `test_donnees.py` passent ; 15 échecs, tous dans `test_cout.py` et
  `test_agregats.py`, de niveau `complet`, que la garde (`-m rapide`) ne
  rejoue pas : chacun compare le bilan figé, calculé aux présomptions du
  vocabulaire, au modèle recalculé sous d'autres (le premier écart lu : la
  dépense nette du rétroactif en 2002, 0,021728 contre 0,021749). Les lignes
  de A n'y sont pas en cause : l'égalité des taux, première assertion de
  `test_la_table_porte_le_taux_effectif_et_la_depense_nette`, passe.
- Les deux tests de `test_web.py` que A a récrits (le bilan de la bascule, la
  masse nette des sources) : verts, avec et sans la variable.
- `-m site` : 34 verts, 2 rouges
  (`test_le_portage_javascript_retrouve_les_chiffres_du_modele`,
  `test_les_temoins_du_portage_sont_a_jour`), sur les cultes et le SMIC du
  mois (file M5, en cours). `-m rapide` : 4 248 verts, 4 rouges et
  9 erreurs, tous sur la majoration pour enfants de l'Agirc-Arrco, que le
  portage ne rend pas encore comme le Python (file M3, en cours). Aucun ne
  touche au taux ni à la fiche 5.
- *Le paquet* : `moteur/donnees.json` de `main` (e4d9994) porte 0,0680628 en
  2022, 0,0685941 en 2023 et 0,0690027 sur 47 années, de 2024 à 2070, soit
  1 − 1 602 / 1 719, 1 − 1 643 / 1 764 et 1 − 1 727 / 1 855.
  `python scripts/construire_donnees.py` n'y change que 1 084 lignes
  ajoutées, toutes de la règle `majoration_enfants_agirc_arrco` (M3), et rien
  des taux : la part de A y est. Copie remise propre ensuite.

## Les sources ouvertes

- `drees_panorama_retraites_2026_classeurs.zip`, SHA-256
  `ec7503f813b0a7e38b76c6aade302afa482f927e7d83386922be0522aaf64911`, et son
  membre `fiche_05.xlsx`,
  `e7cdfaf8e704fa7a6f9cbf622c5ed380539b9877f4942e1034024d41babf0af2` :
  feuilles « F05_Tableau 1 compl_bis » et « F05_Tableau 1 ».
- `les_retraites_et_les_retraites_-_edition_2026-1.pdf`,
  `9eb36a06639af0f4298d281b41acbde4236e47fc73e40c673f153ad86735e9be` :
  folios 54 et 55.
- Au dépôt : `pensions_brutes_nettes.csv`, `pensions_droits.csv`,
  `pib_courant.csv`, `cout/index.html` (avant et après 127aa4a),
  `moteur/donnees.json` (par recherche ciblée), les notes de l'action 138 du
  14 et du 24 octobre.
- Non ouverts : le tableau 2.1-a (connexion coupée), le rapport de la CCSS de
  mai 2024, les données d'Ancetre 2023.
