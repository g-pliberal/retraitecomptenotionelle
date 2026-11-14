# Correction de la ligne 26 de la file : la CARCDSF sert ses statuts de 2017 jusqu'au 9 janvier 2024

Vingt-sixième ligne de la file `2026-11-13-corrections-decidees.md`, décidée par le
propriétaire le 13 novembre 2026. Une ligne, rien d'autre.

**Le texte, relu à l'index JORF** (à jour du 11 novembre 2026).

- Arrêté du 27 décembre 2023 (JORFTEXT000048880697), publié le 9 janvier 2024 : son
  corps ne tient que les visas, « Arrêtent » et les signatures ; aucune date d'entrée
  en vigueur. Son annexe (JORFARTI000048880707) récrit l'article 35 — « 1,25 % par
  trimestre manquant […] dans la limite de 15 % » — sans dire à quelles pensions il
  s'applique : « 1er janvier 2024 » n'y borne que les trimestres de la majoration.
  Publié le 9, il entre en vigueur le 10.
- Statuts de 2017, article 35 (JORFARTI000036251928), en vigueur jusque-là : taux
  plein à l'âge écrit génération par génération (« 66 ans et 2 mois pour les assurés
  nés à compter du 1er janvier 1953 », « 67 ans pour les assurés nés à compter du
  1er janvier 1955 »), « 1,50 % par trimestre manquant » pour les nés depuis 1955,
  sans limite, 1 % par trimestre civil d'exercice au-delà, 20 % au plus ; l'inapte et
  l'ancien déporté sans minoration, l'ancien combattant non nommé.

Le texte tranche ce que la ligne dit : une pension qui prend effet le 1er janvier 2024
se liquide aux statuts de 2017.

**L'erreur.** Le modèle liquidait toute l'année 2024 par les statuts de 2024 : la
pension du 1er janvier recevait la minoration bornée à 15 %, la majoration comptée
depuis 67 ans, et l'ancien combattant y était servi sans minoration.

**Le test d'abord** (`tests/test_sections_sante.py`,
`test_la_carcdsf_sert_ses_statuts_de_2017_jusqu_au_9_janvier_2024`), vu rouge sur
quatre de ses six cas, puis vert ; servis par le portage et refaits au bit près par le
moteur Python (`servi_et_refait`). Dentiste au double du salaire moyen depuis ses
20 ans, euros de 2026 ; chaque attendu est la pension du taux plein multipliée à la
main par le coefficient du texte :

- né le 1er octobre 1961, pension au 1er janvier 2024, à 62 ans et 3 mois : dix-neuf
  trimestres entiers avant 67 ans à 1,50 %, 14 007,1918 × 0,715 = **10 015,14 € par
  an, au lieu de 11 906,11 €** (1 890,97 € de trop) ;
- le même, ancien combattant : 10 015,14 € au lieu de 14 007,19 € ; inapte :
  14 007,19 €, inchangé ;
- né le 1er janvier 1958, pension au 1er janvier 2024, à 66 ans : quatre trimestres,
  14 556,6256 × 0,94 = 13 683,23 € au lieu de 13 828,79 € ;
- né le 1er janvier 1953, pension au 1er janvier 2024, à 71 ans : taux plein le
  1er mars 2019, dix-neuf trimestres civils d'avril 2019 à décembre 2023,
  15 472,3486 × 1,19 = 18 412,09 € au lieu de 17 793,20 € (619 € de trop peu) ;
- né le 1er novembre 1961, pension au 1er février 2024 : les statuts de 2024,
  14 214,8130 × 0,85 = 12 082,59 €, inchangé.

**La correction.** Deux bornes au jour dans `carcdsf_complementaire.yaml`
(`date_effet`, comme aux lignes 21 et 22) : la période de 2023 liquide jusqu'au
9 janvier 2024, celle de 2024 depuis le 10. Aucune ligne des deux moteurs ne change.
Aucun témoin de simulation ne bouge.

**La fiche.** `carcdsf_minoration_age_seul` : l'écart sort des approximations et passe
à l'histoire ; la phrase sur l'ancien combattant du 1er janvier 2024 part avec lui.

**Ce qui reste déclaré.** Le compte du trimestre entamé sous « 1,50 % par trimestre
manquant », que le texte ne dit pas : le modèle le compte entier (né le 1er septembre
1961, pension au 1er janvier 2024 à 62 ans et 4 mois : 0,715 ; 0,73 si seuls les
dix-huit trimestres entiers comptent) ; une approximation de la fiche le porte
désormais seul. Ce que la caisse a servi aux pensions du 1er janvier 2024 n'est pas
lu (`a_relire`).

**La classe, pas le cas.** Les autres arrêtés de la CARCDSF sont bornés au jour par
les lignes 21 et 22. Les autres caisses dont un texte coupe l'année sont aux lignes
de la file qui les nomment (la CAVAMAC, ligne 28) ; je n'ai pas cherché au-delà.

**Fichiers fabriqués refaits ici** : le paquet (`construire_donnees.py`) ; les témoins
(`construire_temoins.py`), inchangés.

**Vérifié** : `python -m pytest -m rapide` ; `test_sections_sante.py`,
`test_sections_liberales.py`, `test_sections_juridiques.py`, `test_carte.py`,
`test_donnees.py`, `test_coupures_au_mois.py`, `test_versions.py`, les confrontations
légères (`test_oracle.py`, `test_destinie.py`, `test_estimation_officielle.py`,
`test_verification.py`), `test_pont.py -k refait`, verts.
