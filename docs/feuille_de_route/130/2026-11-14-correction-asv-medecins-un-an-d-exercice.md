# Correction de la ligne 17 de la file : l'ASV des médecins n'est pas attribuée avant un an d'exercice

Dix-septième ligne de la file `2026-11-13-corrections-decidees.md`, décidée par le
propriétaire le 13 novembre 2026. Une ligne, rien d'autre.

**Le texte, relu à l'index LEGI** (à jour du 11 novembre 2026). Décret n° 72-968,
article 7, du 15 février 1985 au 1er juillet 2026 (LEGIARTI000006765959) : « La
prestation supplementaire de vieillesse est attribuée aux médecins ayant exercé,
pendant au moins un an, leur activité professionnelle non-salariée dans le cadre des
conventions ou adhésions personnelles prévues par les textes législatifs ou
réglementaires alors en vigueur. » La rédaction du 1er juillet 2026
(LEGIARTI000054168425) garde les mêmes mots, au pluriel des « prestations
complémentaires de vieillesse ». Avant : dix ans (décret n° 71-542, article 7,
LEGIARTI000006766682, jusqu'au 15 février 1985). Le décret n° 85-205 du 12 février
1985 (JORFTEXT000000520378) fait le passage. Le texte tranche ce que la ligne dit.

**L'erreur.** Le modèle ne posait aucune durée. Et il ne pouvait pas la lire sur ses
lignes : le moteur ne connaît qu'un statut par année civile, et l'année d'un
changement de métier va entière au métier qui en occupe le plus de mois. Neuf mois de
médecin, de janvier à septembre 2000, y font l'année 2000 entière, 27 points. La
durée se compte donc sur les périodes d'activité déclarées, que la carrière garde
datées au mois (sa chronologie), et non sur les lignes.

**Le test d'abord** (`tests/test_sections_sante.py`,
`test_l_asv_n_est_pas_attribuee_au_medecin_qui_a_exerce_moins_d_un_an` et
`test_la_fiche_de_l_asv_porte_la_duree_d_exercice_de_l_article_7`), vus rouges
(367,01 € servis où le texte ne donne rien ; le champ absent du catalogue), puis
verts. Le cas posé de la note `2026-11-06-e16-asv-medecins-points.md` : homme né le
1er janvier 1960, salarié du privé non cadre depuis ses 22 ans, médecin libéral à ses
40 ans, salarié ensuite, parti à 65 ans, au salaire moyen.

| médecin | exercice | servi avant | servi depuis |
|---|---|---|---|
| de janvier à septembre 2000 | neuf mois | 27 points × 11,82 € × 1,15 = 367,01 € | rien |
| toute l'année 2000 | douze mois | 367,01 € | 367,01 € |

L'effet au cas posé : 367,01 € par an de moins, ce que la ligne annonce. La
complémentaire de la CARMF, que l'article 7 ne régit pas, reste servie.

**La correction.** Un champ de la fiche de régime, `exercice_minimum_annees`
(`_schema.yaml`, `donnees/regimes.py`, le paquet par `construire_donnees.py`), posé à
1 sur les vingt-cinq périodes de l'ASV depuis celle de 1985, et lu à la période de la
date d'effet. Dans les deux moteurs (`anneesDExercice`, `annees_d_exercice`, dans
`droit/liquider`), l'exercice est la somme des mois des périodes d'activité déclarées
dont le statut cotise au régime, jusqu'à la date d'effet ; une carrière posée ligne à
ligne, sans période déclarée, garde la somme des fractions d'année de ses lignes.
Sous la durée, le régime garde sa ligne, à zéro, avec sa raison : « prestation non
attribuée : moins d'un an d'exercice dans le régime (décret n° 72-968, article 7) ».
Aucun témoin ne bouge : aucun ne porte un médecin de moins d'un an.

**Ce qui reste déclaré** (fiche `asv_medecins_points`, approximations) : les dix ans
d'avant le 15 février 1985, lus et non portés, le modèle ne comptant pas au régime
l'exercice d'avant 1972 ; les pensions du 1er janvier et du 1er février 1985, à qui
la période de 1985 demande un an et non dix ; les cotisations du médecin à qui rien
n'est attribué, dont le décret ne dit rien et que le compte notionnel garde ; le
décompte des trimestres, non confronté aux articles 2 et 3.

**La même erreur ailleurs**, non corrigée ici (une ligne, rien d'autre), à inscrire :
l'article 7 du décret n° 71-542 vaut pour tous les « praticiens et auxiliaires
médicaux conventionnés » jusqu'à sa codification du 21 décembre 1985. Les quatre
autres régimes de prestations complémentaires (`asv_chirurgiens_dentistes`,
`asv_sages_femmes`, `asv_auxiliaires_medicaux`, `asv_directeurs_laboratoire`) ne
portent aucune durée d'exercice, et leur texte n'est pas relu sur ce point.

**Tests.** `python -m pytest -m rapide`, `tests/test_sections_sante.py`,
`tests/test_sections_liberales.py`, `tests/test_pcv_sante.py`, `tests/test_donnees.py`,
les confrontations légères et `tests/test_pont.py -k refait` : verts. Refaits : le
paquet et les témoins, ces derniers identiques.
