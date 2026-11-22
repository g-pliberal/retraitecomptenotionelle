# Étape 6, à part : les écarts que les circulaires de 2004, 2005 et 2023 à 2026 montrent au modèle, corrigés

Le propriétaire a fait lire, le 22 novembre 2026, des circulaires de la Cnav restées
`a_lire` ou `limite` ; la lecture a relevé quatre écarts au modèle (notes privées du
projet, hors du dépôt : les mentions légales de la Cnav en interdisent l'extraction
substantielle). Cette session les a vérifiés au texte, dans l'index LEGI à jour au
16 novembre 2026, puis corrigés ou trouvés déjà corrigés. Sur Opus 5.5.

## 1. Mayotte : le taux plein des pensions de septembre 2023 à décembre 2025

**Confirmé, corrigé.** La circulaire Cnav n° 2026/30 du 22 septembre 2026 met le
taux plein à soixante-sept ans pour tous les nés depuis 1961. Le texte s'y prête :
l'article 10 du décret n° 2003-589 (LEGIARTI000026514415, en vigueur du 21 octobre
2012 au 1er janvier 2026) dit « l'âge prévu à l'article 2 augmenté de cinq
années », et l'article 2 dans la rédaction du décret n° 2024-766
(LEGIARTI000049915788) garde son 7°, « Soixante-deux ans pour les assurés nés à
compter du 1er janvier 1961 », avant les 8° à 14° qui relèvent l'âge d'ouverture.
Le texte est ambigu pour les nés depuis 1962 ; la pratique publiée de la caisse le
tranche, et le scénario 1 est le droit tel que la caisse l'applique. La table
`mayotte_2023` de `ages_regimes.csv` portait l'âge d'ouverture augmenté de cinq
ans, de 67 ans et 3 mois pour 1962 à 69 ans pour 1969 ; elle porte 67 ans.
**Effet** : un Mahorais né en 1962 ou 1963, parti en 2024 ou 2025 sans la durée,
avant 67 ans et 6 mois, perd un ou deux trimestres de minoration de moins (2,5 %
de pension chacun). Test : `tests/test_mayotte.py`,
`test_de_2023_a_2025_le_taux_plein_de_mayotte_est_a_67_ans_des_1961`.

## 2. Mayotte : la bascule du calendrier de la suspension

**Déjà juste.** La fiche du régime ouvre la période `mayotte_2026_09` aux pensions
prenant effet depuis le 1er septembre 2026 (`date_effet`), comme la circulaire ;
son étiquette annuelle (2027) n'y change rien. Un test le tient désormais :
`test_le_calendrier_de_la_suspension_vaut_a_mayotte_des_septembre_2026` (né en
février 1964 : 62 ans et 9 mois en août 2026, 62 ans et 6 mois dès septembre).

## 3. La clause de sauvegarde de la carrière longue de 2023

**Déjà corrigé le 20 novembre 2026** (fiche `carriere_longue_sauvegarde_de_2023`,
action 191) : les trois exemples de la circulaire n° 2023-14, point 9.2, y sont
rejoués et passent. Rien à faire.

## 4. Le minimum contributif d'une pension proratisée, de 2004 à 2008

**Confirmé, plus large que relevé, corrigé.** La circulaire n° 2004/8 (point 423,
exemple 4241) et la n° 2005/36 du 29 juillet 2005, lue cette fois par l'API de la
base (points 331, 333, 3331 et 3332, et sa fiche de synthèse), disent la même
règle : quand la durée totale d'assurance, française et étrangère, n'excède pas la
« limite de déclenchement » — la durée requise de L. 351-1, 160 trimestres alors —,
le minimum se proratise sur cette durée « éventuellement ramenée à la " durée de
proratisation " » ; au-delà, sur l'ensemble des périodes. Le moteur
(`plancherInternational`, `moteur/js/droit/completer.js`) divisait toujours par la
durée totale non limitée ; la majoration suivait déjà les trois cas. La distinction
ne joue que quand la durée de proratisation est inférieure à la durée requise de
160 trimestres, pour les générations nées avant 1948 ; elle ne touche ni l'exposé actuel de la Cnav ni les
générations suivantes. **Effet** : né en 1944, 140 trimestres au régime général et
15 en Allemagne, pension de 2004 : le minimum × 140/152, non × 140/155, soit +2 %
(5 996,63 € contre 5 880,63 € par an au minimum de 6 511,06 €). Test :
`tests/test_etranger.py`,
`test_le_minimum_international_se_proratise_sur_la_duree_de_proratisation_jusqu_a_160`,
qui rejoue l'exemple de 2004 et trois de 2005. Approximation déclarée : la
circulaire (point 4422) ne la prescrit, pour un accord bilatéral, que s'il prévoit
la proratisation sur la durée maximale ; le modèle l'applique à tous.

**Relecture.** Fable étant indisponible jusqu'au 25 novembre (limite atteinte), les
deux corrections ont été relues par un relecteur Opus indépendant : justes, avec
quatre défauts de prose de la fiche, corrigés (générations, phrase tronquée,
renvoi au point, accords bilatéraux).

## 5. Le registre

Les 77 circulaires de 2023 à 2026 restées `a_lire` sont rangées
(`data/reference/legislation/cnav/references.csv`) d'après leur objet : barèmes que
les séries du dépôt prennent ailleurs (plafond, Smic, taux, RCI, Aspa, minimum
contributif, CSG), `limite` vers la fiche qui s'en sert ; prestations que le modèle
ne sert pas (ASI, tierce personne, veuves de guerre, salaires forfaitaires des
hôtels-cafés-restaurants, avantages en nature, paiement des rachats) et procédure
(droit de communication, oppositions, rectification d'un indu), `hors_modele`.

## Reste

La circulaire n° 2025/33 fixe l'assiette AVPF de 2026 sur le Smic de janvier 2026
quand R. 381-3 dit celui du 1er juillet de l'année précédente (+1,2 %) : la
pratique diffère du texte, question soumise au propriétaire. Les écarts « moyens »
du récapitulatif des circulaires (note du 16 novembre) restent à reprendre. Même
classe d'erreur à chercher ailleurs : une table qui écrit le taux plein à l'âge
d'ouverture augmenté de cinq ans quand le texte renvoie à un âge fixe.
