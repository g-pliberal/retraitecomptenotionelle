# Correction de la ligne 25 de la file : la CARCDSF majore de 1 % les trimestres d'avant 2024, depuis 67 ans

Vingt-cinquième ligne de la file `2026-11-13-corrections-decidees.md`, décidée par le
propriétaire le 13 novembre 2026. Une ligne, rien d'autre.

**Le texte, relu aux index JORF et LEGI** (à jour du 11 novembre 2026).

- Statuts de 2024, article 35, I (JORFARTI000048880707), en vigueur le 10 janvier
  2024 : « a) A taux plein sans application de coefficients de minoration, à partir de
  l'âge prévu au 1° de l'article L. 351-8 du code de la sécurité sociale » ; « c) […]
  Les affiliés qui poursuivent leur activité libérale au-delà de l'âge prévu au a du
  présent I […] bénéficient d'une majoration de leur pension […]. Cette majoration est
  égale à 1 % par trimestre civil entier d'exercice libéral suivant le dernier jour du
  trimestre civil incluant l'âge […] et accompli avant le 1er janvier 2024, dans la
  limite de 20 %. Cette majoration est égale à 1,25 % par trimestre civil entier
  d'exercice libéral […] accompli à compter du 1er janvier 2024, dans la limite de
  25 %. »
- Règlement de 2026, article 3, I (JORFARTI000054435749), en vigueur le 18 juillet
  2026 : les mêmes mots.
- L. 351-8, 1° (LEGIARTI000047452736, du 1er septembre 2023 ; LEGIARTI000051289852,
  du 28 février 2025, inchangé sur ce point) : « Les assurés qui atteignent l'âge prévu
  au premier alinéa de l'article L. 161-17-2 augmenté de trois années ». Le premier
  alinéa de L. 161-17-2 fixe cet âge « à soixante-quatre ans pour les assurés nés à
  compter du 1er janvier 1968 » (1969 dans la rédaction du 31 décembre 2025) : 67 ans,
  sans table par génération.

Le texte tranche ce que la ligne dit : deux taux selon la date du trimestre, et un
âge de départ du décompte de 67 ans pour toutes les générations.

**L'erreur.** Aux pensions qui prennent effet depuis 2024, le modèle majorait de
1,25 % tous les trimestres ; et il lisait l'âge du taux plein à la génération, comme
sous les statuts de 2017 (65 ans avant juillet 1951, 66 ans et 2 mois en 1953, 66 ans
et 7 mois en 1954), d'où un décompte parti trop tôt pour les nés avant 1955.

**Le test d'abord** (`tests/test_sections_sante.py`,
`test_la_carcdsf_majore_de_1_pour_cent_les_trimestres_d_avant_2024_depuis_67_ans`), vu
rouge sur ses quatre cas, puis vert ; servis par le portage et refaits au bit près par
le moteur Python (`servi_et_refait`). Dentiste au double du salaire moyen depuis ses
20 ans, euros de 2026 ; chaque attendu est la pension du taux plein multipliée à la
main par la majoration du texte :

- né le 1er janvier 1955, 67 ans le 1er janvier 2022, pension au 1er janvier 2025 :
  sept trimestres à 1 % (avril 2022 à décembre 2023) et quatre à 1,25 %,
  15 710,0892 × 1,12 = **17 595,30 € par an, au lieu de 17 870,23 €** (274,93 € de
  trop) ;
- né le 1er janvier 1953, 67 ans le 1er janvier 2020, pension au 1er avril 2024 :
  quinze trimestres à 1 % (avril 2020 à décembre 2023) et un à 1,25 %,
  15 725,3600 × 1,1625 = **18 280,73 € au lieu de 19 656,70 €** (1 375,97 € de trop) ;
- né le 1er janvier 1954, 67 ans le 1er janvier 2021, pension au 1er avril 2024 : onze
  trimestres à 1 % et un à 1,25 %, 15 542,2154 × 1,1225 = 17 446,14 € au lieu de
  18 262,10 € ;
- né le 1er janvier 1950, 67 ans le 1er janvier 2017, pension au 1er juillet 2024 :
  vingt-sept trimestres d'avant 2024, 20 % au plus, et deux à 1,25 %,
  16 342,8792 × 1,225 = 20 020,03 € au lieu de 20 428,60 €.

Les deux cas tenus depuis la ligne 24 dont tous les trimestres suivent 2024 (né en
1957, 1,0875 ; né en 1958, 1,1375) ne bougent pas.

**La correction.** Deux paramètres neufs (`regimes/_schema.yaml`, `PeriodeRegime`, le
paquet par `_regles_des_sections`), posés aux trois périodes de
`carcdsf_complementaire.yaml` depuis 2024 : `surcote_par_trimestre_depuis: 2024` et
`surcote_par_trimestre_d_avant: 0.01`. Sous eux, `surcotePoints`
(`moteur/js/droit/liquider.js`) et son jumeau comptent à part les trimestres civils
d'exercice d'avant le 1er janvier 2024 et ceux d'après, bornent chacun des deux
décomptes à `surcote_trimestres_maximum` (vingt : 20 % à 1 %, 25 % à 1,25 %), et
appliquent à chacun son taux. Les mêmes périodes ne renvoient plus à la table des
âges par génération (`age_taux_plein_par_generation`) : l'âge du taux plein y est 67
ans. La minoration n'en bouge pas : la table rend déjà 67 ans depuis la génération
1955, et les nés d'avant ont passé 67 ans en 2024.

Aucun témoin de simulation ne bouge.

**La fiche.** `carcdsf_minoration_age_seul` : les deux paramètres aux versions de 2024
et de 2026 ; l'écart sort des approximations et passe à l'histoire.

**Ce qui reste déclaré.** Le texte borne la première majoration à 20 % et la seconde à
25 %, sans dire si elles se cumulent. Le modèle borne chacune à part et les
additionne, la lecture la plus favorable à l'affilié : nul tant que le total ne passe
pas 25 %, ce qui demande une pension prise après 72 ans, depuis avril 2025 ; né le
1er janvier 1950, pension au 1er janvier 2026, 1,30 au modèle, 1,25 si la limite vaut
pour le tout. La question reste à poser au propriétaire (`a_relire` de la fiche).
Restent aussi les trois points de la ligne 24 : la cessation en cours d'année, la
condition d'être à jour de ses cotisations, l'exercice d'avant le 1er juillet 2011.

**La classe, pas le cas.** Aucune autre période du catalogue ne renvoie à
`surcote_trimestres_civils_d_exercice`, et aucune autre fiche lue ne porte deux taux
selon la date du trimestre. La pension du 1er janvier 2024, que la période de 2024
sert neuf jours avant ses statuts, est la ligne 26.

**Fichiers fabriqués refaits ici** : le paquet (`construire_donnees.py`) ; les témoins
(`construire_temoins.py`), inchangés.

**Vérifié** : `python -m pytest -m rapide` ; `test_sections_sante.py`,
`test_sections_liberales.py`, `test_sections_juridiques.py`, `test_carte.py`,
`test_donnees.py`, `test_coupures_au_mois.py`, `test_facade.py`,
`test_facade_jumeau.py`, `test_versions.py`, les confrontations légères
(`test_oracle.py`, `test_destinie.py`, `test_estimation_officielle.py`,
`test_verification.py`), `test_pont.py -k refait`, verts.
