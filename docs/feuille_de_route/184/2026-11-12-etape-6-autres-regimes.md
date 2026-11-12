# Étape 6, lot « les autres régimes » : 29 rédactions en vigueur lues, sur 20 fiches

**La commande.** La session d'orchestration a confié à cette session, le
11 novembre 2026, un des quatre lots de la passe de lecture
(`2026-11-11-etape-6-passe-de-lecture.md`) : vingt fiches, vingt-neuf lectures
de rédactions en vigueur ou à venir que ces fiches n'avaient pas lues. Le lot
est fait en entier : `python scripts/textes.py --non-lues <fiche>` rend zéro
rédaction en vigueur ou à venir pour chacune des vingt. Menée sur Fable 5.2,
dans l'index LEGI du dépôt à jour au 11 novembre 2026. Ni `src/` ni `moteur/`
ne sont touchés.

**Le compte.** Quatre rédactions sont citées par la version qui les applique,
quatorze sont sans effet, onze sont à rattacher. Le cliquet baisse de quatre,
de 9 262 à 9 258, les lots de la fonction publique et des non-salariés
agricoles ayant poussé avant celui-ci : quatre des vingt-neuf n'avaient aucun
statut, les autres attendaient « à examiner » ou étaient déjà citées par une
autre fiche.

## Ce qui change une règle

Une seule rédaction change ce que le modèle calcule.

- **Règlement du régime complémentaire des indépendants, article 12**
  (LEGIARTI000054908824), **au 1er janvier 2027**, par les arrêtés du
  6 octobre 2025 (NOR TSSS2527351A) et du 21 septembre 2026 (NOR
  TRSS2624955A). « Lorsque l'assuré bénéficie d'une fraction de pension au
  titre de la retraite progressive par application de l'article 28 du présent
  régime, le coefficient d'abattement ne peut excéder le taux prévu à la
  deuxième ligne du tableau de l'annexe 2. » Le modèle sert la fraction de la
  complémentaire sous l'abattement entier, jusqu'à 22 %. Quelle ligne est la
  deuxième, l'index ne le dit pas : il rend l'annexe 2 à plat, de vingt
  trimestres (22 %) à un (1 %). À lire sur Légifrance avant d'écrire la règle.
  Fiche : `abattement_rci` (`sources.a_relire`, `textes_a_rattacher`). Le
  reste de la rédaction est un renvoi mis à jour, le 6° de L. 351-8 au lieu du
  III de l'article 20 de la loi n° 2010-1330.
- À la même date, **l'article 28 du même règlement** (LEGIARTI000054908892),
  qu'aucune fiche du lot ne cite : « L'assuré ne peut prétendre au bénéfice du
  dispositif de complément différentiel de points mentionné aux articles 9-1 à
  9-6 du présent règlement, lorsqu'il demande à bénéficier de la fraction de
  pension au titre de la retraite progressive. » Vu en lisant l'article 12 ;
  ce que le modèle en fait n'est pas vérifié.

## Ce qui change le droit sans changer ce que le modèle calcule

Ces rédactions sont « à rattacher » dans leur fiche, qui dit ce qui change.

- **Décret n° 49-579, article 4, et décret n° 50-28, article 2**, au
  1er juillet 2026 (`decret_2026_418_liberaux`). Ce sont les articles 3 et 5
  du décret n° 2026-418, que la fiche avait lus au Journal officiel. Les
  dispenses de la CARMF (deux premières années avant 40 ans, semestre qui suit
  les 75 ans) y sont : ce sont les deux erreurs déjà déclarées par
  l'action 130, rien de neuf. À l'article 2 du décret n° 50-28, une phrase
  n'a pas été confrontée au modèle : « L'affiliation ou la radiation prend
  effet au premier jour du trimestre civil suivant le début ou la fin de
  l'activité professionnelle. »
- **Loi n° 87-563, Saint-Pierre-et-Miquelon** : l'article 3 affilie depuis le
  1er décembre 2024 le détenu sous contrat d'emploi pénitentiaire, statut que
  le modèle n'a pas ; l'article 6 adapte depuis le 28 décembre 2023
  l'assurance vieillesse des parents au foyer, que la fiche ne porte pas ;
  l'article 9 rend applicable depuis 2015 la retraite complémentaire
  obligatoire, que le modèle route déjà.
- **Décret n° 2004-1056, article 21**, au 2 janvier 2025
  (`depart_anticipe_parents_trois_enfants`) : un IV nouveau range hors des
  emplois insalubres les services d'avant l'affiliation. Il n'est d'aucune
  fiche ; à rattacher à la règle des emplois insalubres des ouvriers de l'État.
- **Décret n° 73-937, article 2**, depuis 1990 : les conditions de durée
  d'exercice des avantages d'avant 1973 sont supprimées. C'est la
  reconstitution de carrière, que `points_avant_1973_independants` déclare ne
  pas porter ; `decote_avant_1983` la renvoie à cette fiche.
- **Décret n° 68-382, article 6** (2014), et **décret n° 62-420, article 2**
  (2020) : hors du sujet de `limite_age_opera` et de la période de
  `raap_classe_speciale`, qui les nomment dans une lecture ; les fiches sœurs
  `decote_opera_de_paris` et `raap_taux_amenage_racd_racl` les ont à rattacher.

## Une question ouverte

**Décret n° 2004-1056, article 7** (`limite_age_ouvriers_etat`). Depuis le
2 janvier 2025, les services d'après la limite d'âge comptent « dans les
conditions prévues aux articles L. 556-1, L. 556-5 et L. 556-7 du code général
de la fonction publique » : la rédaction est citée par la version de 2023, qui
applique ces trois exceptions. Du 1er septembre 2023 au 2 janvier 2025,
l'article ne nommait que la prolongation pour carrière incomplète. Les
services du maintien et de la prolongation de l'insalubre comptaient-ils alors
pour la pension ? Ni la pratique de la caisse ni ce que le modèle en fait ne
sont vérifiés ; la question est à `sources.a_relire`.

## Vu en passant, hors des fiches du lot

L'article 12 du décret n° 2004-1056, lu pour comprendre son article 16, a
trois rédactions de 2026 qui ajoutent des droits aux ouvriers de l'État : la
majoration des sapeurs-pompiers volontaires (8°, décret n° 2026-18, pensions
prenant effet à compter du 1er juillet 2026) ; « une bonification d'un
trimestre pour chacun de leurs enfants nés depuis le 1er janvier 2004, pour
les ouvrières ayant accouché postérieurement à leur recrutement » (2° bis,
décret n° 2026-699, à compter du 1er septembre 2026) ; la majoration des élus
locaux (9°, décret n° 2026-948, à compter du 1er janvier 2027). Aucune fiche
du lot ne cite cet article ; ce que le modèle en porte n'est pas vérifié.

## Le statut donné, fiche par fiche

| Fiche | Rédaction | Statut |
|---|---|---|
| `prime_speciale_sujetion_aides_soignants` | décret n° 91-613, art. 5, 2026, 2027 et 2028 | sans effet : seul le taux des employeurs de la CNRACL monte, déjà dans `contribution_employeur_public.csv` |
| `decret_2026_418_liberaux` | décret n° 49-579, art. 4 ; décret n° 50-28, art. 2 (1er juillet 2026) | à rattacher, par une lecture |
| `asv_autres_professions_de_sante` | décret n° 78-283, art. 3 (1er juillet 2026) | sans effet : un mot |
| `surcote_par_age_seul` | décret n° 79-262, art. 5 (1er juillet 2026) | sans effet : un fonds social |
| `abattement_rci` | règlement du RCI, art. 12 (2027) | à rattacher : change une règle |
| `retraite_anticipee_handicap` | règlement du RCI, art. 12 (26 juin 2024) | citée par la version de 2023 |
| | règlement du RCI, art. 12 (2027) | à rattacher : rien pour cette fiche |
| | décret n° 2004-1056, art. 16 (1er août 2026) | sans effet : le III est inchangé |
| `reversion_rci` | règlement du RCI, art. 17 (2027) | sans effet : un mot de grammaire |
| `organic_conjoints_de_commercants` | règlement du RCI, annexe 3 (2027) | sans effet : la note seule |
| `limite_age_ouvriers_etat` | décret n° 2004-1056, art. 7 (2 janvier 2025) | citée par la version de 2023 |
| `depart_anticipe_parents_trois_enfants` | décret n° 2004-1056, art. 21 (2 janvier 2025) | à rattacher : un IV qui n'est d'aucune fiche |
| `categorie_active_super_active` | loi n° 2010-1330, art. 35 (1er septembre 2023) | sans effet : renvois retirés |
| `decote_avant_1983` | décret n° 73-937, art. 2 (1990) | à rattacher, par une lecture |
| `points_avant_1973_independants` | décret n° 64-994, art. 5 (1986) | sans effet : typographie |
| `limite_age_opera` | décret n° 68-382, art. 6 (2014) | à rattacher, par une lecture |
| `mayotte_pension_de_base` | ordonnance n° 2002-411, art. 19 (2012) | citée par la version de 2002 |
| `raap_classe_speciale` | décret n° 62-420, art. 2 (2020) | à rattacher, par une lecture |
| `regies_ferroviaires_pensions_en_extinction` | loi n° 2003-1312, art. 80 (2014) | sans effet : le 23° est inchangé |
| `taux_plein_anciens_combattants_prisonniers` | décret n° 74-191, art. 1er (1985) | sans effet : le barème est passé à D. 351-2 |
| `saint_pierre_et_miquelon_pension_de_base` | loi n° 87-563, art. 1er (2015) | sans effet : « et veuvage » |
| | loi n° 87-563, art. 3, 6 et 9 | à rattacher |
| `marins_salaire_de_reference` | décret n° 85-1148, art. 3 (1er juillet 2023) | citée par la version de 1999 : le point de 59,0734 € du plafond |
| | décret n° 48-1108, art. 1er (2023) | sans effet : un nom de comité |

## Deux choses à savoir sur la méthode

- **« Sans effet » efface la rédaction pour toutes les fiches.** Une rédaction
  prend le statut le plus établi que lui donne une fiche : déclarée sans effet
  par l'une, elle sort de la liste des rédactions non lues des autres. Cette
  session ne l'a donc déclarée sans effet que là où rien ne change pour aucune
  règle ; quand la rédaction change le droit ailleurs que dans la fiche, elle
  est « à rattacher », avec ce qui change. D'où onze « à rattacher » pour une
  seule règle à écrire.
- **`sources.lu_le` est porté au jour de la lecture**, comme la consigne de
  l'étape le demande, mais seules les rédactions listées ont été relues, non
  les circulaires ni les exemples : chaque fiche le dit dans une lecture datée
  du 12 novembre. Aucune `prochaine_relecture` n'est repoussée.
