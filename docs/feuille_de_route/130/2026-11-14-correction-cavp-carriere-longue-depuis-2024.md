# Correction de la ligne 11 de la file : la CAVP minore la carrière longue jusqu'à 65 ans seulement depuis 2024

Onzième ligne de la file `2026-11-13-corrections-decidees.md`, décidée par le
propriétaire le 13 novembre 2026. Une ligne, rien d'autre.

**Le texte, relu aux index JORF et LEGI** (à jour du 11 novembre 2026). Arrêté du
19 décembre 2023, publié le 9 janvier 2024 sans date d'effet propre, donc en vigueur le
10 (JORFARTI000048880592), annexe, II, 6°, qui récrit la fin de l'article 15 des
statuts : « L'affilié qui bénéficie d'une liquidation anticipée au régime de base, dans
les conditions prévues aux II, III et IV de l'article L. 643-3 en bénéficie dans les
mêmes conditions et modalités au régime complémentaire fonctionnant par répartition. »
puis « Par dérogation, en cas de liquidation anticipée dans les conditions prévues au
II de l'article L. 643-3, sa pension de retraite complémentaire est affectée d'un
coefficient de minoration égal à - 1,25 % par trimestre manquant jusqu'à l'âge de 65
ans. » Le règlement de 2026 (arrêté du 10 juillet 2026, annexe I, article 12,
JORFARTI000054436087) le reprend : « - 1,25 % par trimestre d'anticipation jusqu'à
l'âge de 65 ans ». Le II de L. 643-3 (LEGIARTI000053280388) est la carrière longue :
« L'âge prévu au premier alinéa du I est abaissé dans les conditions définies à
l'article L. 351-1-1 ». Le texte tranche ce que la ligne dit : la carrière longue ne
reçoit que la première pente, de son âge à 65 ans, sans la seconde (0,5 % de 65 ans à
l'âge du taux plein) ni la limite de vingt trimestres, que l'article 15 de 2009 posait
et que celui de 2011 n'a plus.

**L'erreur.** Le modèle opposait à la carrière longue la minoration de tous, les deux
pentes, dans la limite de vingt trimestres : trop sévère à 62 ou 63 ans (huit trimestres
à 0,5 % de trop), trop douce avant 60 ans (la limite de vingt).

**Le test d'abord** (`tests/test_sections_sante.py`), vu rouge (0,81 servi où le texte
donne 0,85 ; 11 035,07 € où il donne 11 580,01 €), puis vert :

- `test_la_cavp_minore_la_carriere_longue_jusqu_a_65_ans_seulement_depuis_2024`, huit
  cas posés à la main, servis par le portage et refaits au bit près par le moteur Python
  (`servi_et_refait`) : 0,85 à 62 ans (12 × 1,25 %), 0,90 à 63 ans, 0,65 à 58 ans
  (28 × 1,25 %), 0,75 à 60 ans ; 0,85 à la première date d'effet qui suit le 10 janvier
  2024, le 1er février ; 0,81 le 1er janvier 2024, sous les statuts de 2011 ; 0,86 et
  0,91 sans carrière longue, les deux pentes gardées ;
- `test_la_carriere_longue_de_la_cavp_se_pose_a_la_main` : les deux montants ;
- `test_chaque_version_de_la_cavp_est_portee_par_le_modele` : le paramètre neuf lu à
  chaque version de la fiche, chaque premier du mois ;
- `tests/test_coupures_au_mois.py` : la CAVP entre dans la liste des régimes dont une
  période se coupe au jour.

**L'effet aux cas posés** (pharmacien au double du salaire moyen, euros de 2026). Né le
10 mars 1965, entré à 19 ans, parti à 62 ans le 1er avril 2027 : 0,85 au lieu de 0,81,
11 035,07 / 0,81 × 0,85 = **11 580,01 € par an au lieu de 11 035,07 €, 544,94 € de
plus**. Né le 10 mars 1966, entré à 20 ans, à 63 ans le 1er avril 2029 : 0,90 au lieu de
0,86, 12 742,13 € au lieu de 12 175,81 €. Né le 10 mars 1966, entré à 15 ans, à 58 ans
le 1er avril 2024 : 0,65 au lieu de 0,75, **9 169,39 € au lieu de 10 580,06 €,
1 410,68 € de moins**. À 60 ans, 0,75 avant comme après.

**La correction.** Un paramètre de période, `carriere_longue_minoree_jusqu_au_palier`
(schéma, chargeur, paquet du portage) : quand la liquidation est ouverte par la carrière
longue, `abattementRegimeDeBase` et son jumeau `abattement_regime_de_base` rendent
1 − 1,25 % × les trimestres de l'âge du départ au palier de 65 ans, comptés au trimestre
supérieur. Le motif d'ouverture descend de `liquiderChaqueRegime` par
`abattementPoints`. Dans `cavp_complementaire.yaml`, la période de 2020 à 2025 est
coupée : 2020 à 2023, qui liquide jusqu'au 10 janvier 2024 (`date_effet`), et 2024 à
2025, qui porte le paramètre, comme celle de 2026. Les années bornent toujours
l'acquisition, dont rien ne change. La fiche `cavp_minoration_deux_pentes` : le
paramètre à chaque version, l'erreur passée à son histoire, relue ce jour.

**La classe, pas le cas.** Le même arrêté écrit la même dérogation à l'article 11 des
statuts du régime des prestations complémentaires de vieillesse de la caisse, celui des
biologistes conventionnés, et le règlement de 2026 la reprend (article 1er de son
annexe). Le modèle y sert `asv_directeurs_laboratoire` par la décote du régime de
base ; sa fiche, `asv_autres_professions_de_sante`, n'est pas lue au droit, et la file
ne porte pas cette ligne : à lire avec elle, non corrigé ici. Les autres sections à
deux pentes : aucune (seule la CAVP écrit `decote_palier_age`).

**Ce qui reste déclaré** dans la fiche : la date d'effet au trimestre civil (ligne 12
de la file) ; le trimestre entamé ; la valeur de service par génération ; le handicap
et l'inaptitude des III et IV de L. 643-3 ; la carrière longue servie avant 2024, que
les statuts de 2011 n'ouvraient pas (`liquidation_regime_par_regime`) ; aucun exemple
de la caisse pour une carrière longue liquidée depuis 2024.
