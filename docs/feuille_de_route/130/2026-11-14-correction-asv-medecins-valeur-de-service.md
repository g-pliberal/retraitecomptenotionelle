# Correction de la ligne 8 de la file : la valeur de service de l'ASV des médecins est celle du texte

Huitième ligne de la file `2026-11-13-corrections-decidees.md`, décidée par le
propriétaire le 13 novembre 2026. Une ligne, rien d'autre.

**Le texte, relu à l'index LEGI** (à jour du 13 novembre 2026). Décret n° 72-968,
article 2, du 28 mars 1999 au 1er janvier 2012 (LEGIARTI000006765945, 946 et 947) :
« La valeur du point de retraite est fixée à 102 F. » Décret n° 2011-1644, article 4,
dans sa rédaction en vigueur (LEGIARTI000052567955, du 14 novembre 2025, sans rédaction
plus récente) : pour les points liquidés à compter du 1er janvier 2011, « 15,55 euros
pour le premier semestre de l'exercice 2012 ; 13 euros à compter du second semestre de
l'exercice 2012 et jusqu'à l'exercice 2020 » ; pour ceux liquidés à compter du 1er
janvier 2017, « 11,31 euros jusqu'à l'exercice 2020, 11,36 euros pour l'exercice 2021,
11,48 euros pour l'exercice 2022, 11,71 euros pour les exercices 2023 et 2024 et 11,82
euros à compter de l'exercice 2025 ». Le texte tranche ce que la ligne dit : la valeur
est fixée en francs puis en euros courants, exercice par exercice, sans indexation.

**Le test d'abord** (`tests/test_sections_sante.py`), vu rouge sur sept des neuf années
(13,313333 € servis en 2002, 11,944317 € en 2024, 12,02685 € en 2026), par la requête du
formulaire, servie par le portage et refaite au bit près par le moteur Python
(`servi_et_refait`) : médecins nés un 1er janvier, au salaire moyen de 30 à 65 ans.

- `test_la_valeur_de_service_de_l_asv_des_medecins_est_celle_du_texte`, neuf pensions de
  2002 à 2026, chacune à la valeur que le texte donne à son exercice ;
- `test_l_asv_de_2002_et_de_2005_se_pose_a_la_main` : vingt-deux années à 30,16 points
  et huit à 27, 879,52 points × 15,55 € = 13 676,54 € ; 960,52 × 15,55 € = 14 936,09 € ;
- `test_passe_le_dernier_exercice_fixe_la_valeur_de_l_asv_suit_les_prix` : en 2027,
  11,82 € portés aux prix depuis 2026, et non depuis 2025.

**L'effet aux cas posés**, par an, en euros de l'année d'effet.

| Né en janvier | Pension | Avant | Après | Écart |
|---|---|---|---|---|
| 1937 | 2002 | 11 709,34 € | 13 676,54 € | 1 967,20 € de plus |
| 1940 | 2005 | 13 575,33 € | 14 936,09 € | 1 360,76 € de plus |
| 1950 | 2015 | 13 107,35 € | 12 923,84 € | 183,51 € de moins |
| 1953 | 2018 | 13 218,88 € | 12 979,15 € | 239,73 € de moins |
| 1959 | 2024 | 13 934,47 € | 13 661,11 € | 273,36 € de moins |
| 1961 | 2026 | 14 106,48 € | 13 863,87 € | 242,62 € de moins |

La file annonçait 1 967,02 €, 273,50 € et 242,76 € : le premier comptait 102 F à
15,5498 € et non 15,55 € ; les deux autres, 1 014,99 et 1 020,52 points, quand la même
requête en rend ce jour 1 014,45 et 1 019,93 — les points d'ajustement, que cette ligne
ne touche pas, ont bougé depuis le 13 novembre, sans que cette session cherche pourquoi.

**La correction**, dans les données seules : `regimes/asv_conventionnes.yaml`. Les
seize périodes de 1999 à 2025 perdent leur année d'ancrage (`valeur_point_annee: null`) :
`valeurPointFiche` (`moteur/js/droit/liquider.js`) et son jumeau rendent alors la valeur
écrite, sans coefficient de prix, ce que les deux codes savaient déjà faire. La période
ouverte en 2026 s'ancre en 2026 : 11,82 € cette année-là, puis les prix, faute de
texte. Aucune ligne de code ne change ; le schéma (`_schema.yaml`) dit ce que vaut une
valeur sans année.

**Ce que la correction déplace.** Le paquet (`moteur/donnees.json`). Deux tests voisins
épinglaient l'ASV d'un départ de 2027, 44 511,19 € et 22 383,12 € : ils passent à
43 745,64 € et 21 998,15 €, la valeur de 2027 partant de 2026 (1,75 % de hausse des
prix en 2026). Les témoins des médecins et les chiffres ancrés, GitHub les refait.

**Ce que la correction laisse, déclaré dans la fiche** `asv_medecins_points`
(approximations).

- Le premier semestre de 2012 : 13 € servis, quand le texte donne 15,55 € jusqu'au
  30 juin.
- Les pensions d'avant 1999 : le tarif de la consultation jusqu'en 1993, puis 100 F
  revalorisés comme le régime général ; le modèle garde 15,55 € de 2011 ramenés aux
  prix. Non mesuré.
- Ce que le texte fait de la valeur après la date d'effet, exercice par exercice.
- De 1999 à 2001, 102 F font 15,5498 € : 0,18 € par an au cas posé.
- Passé 2026, une projection sur les prix, à remplacer par chaque décret.

**Les écarts (c) à (g) de la relecture du 13 novembre**, repris dans la fiche, chacun
relu à l'index : (c) cinquante-deux fois la consultation dès le 1er janvier 1994
(D. 645-2, LEGIARTI000006738374 ; décret n° 94-564, article 1er, II), le décret
n° 95-442 ne touchant que les chirurgiens-dentistes ; (d) avant le code, le décret
n° 71-544, non un arrêté, résumé au Journal officiel (JORFTEXT000000685106) ; (e)
D. 645-3 s'arrête le 2 décembre 2004 ; (f) l'erreur, 2026 compris, passée à
l'historique ; (g) la citation de 2026, les points liquidés de 2006 à 2010, 102 F et
15,55 €, `nee_de` des 27 points (l'article 2 du 8 juillet 1994, LEGIARTI000006765944),
le décompte des trimestres. La fiche de régime tient encore 1994 à quarante-cinq fois
la consultation : c'est la ligne 9.

**La classe.** Les quatre autres ASV (`asv_chirurgiens_dentistes`,
`asv_auxiliaires_medicaux`, `asv_sages_femmes`, `asv_directeurs_laboratoire`) portent
elles aussi une valeur ancrée et menée aux prix ; leur fiche
(`asv_autres_professions_de_sante`) dit certaines valeurs « revalorisée sur les prix »,
d'autres fixées. Non relues ici, et hors de la file : à relire, valeur par valeur,
avant de dire s'il y a erreur.

**Vérifié** : `python -m pytest -m rapide`, les confrontations légères
(`test_oracle.py`, `test_destinie.py`, `test_estimation_officielle.py`,
`test_verification.py`), `test_pont.py`, `test_simulateur.py`, `test_sections_sante.py`,
`test_sections_liberales.py`, `test_carte.py`, `test_donnees.py`.
