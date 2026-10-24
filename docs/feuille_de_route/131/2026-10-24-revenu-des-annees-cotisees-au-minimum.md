# Le revenu des années que le chef agricole a cotisées au minimum, tiré de ses cotisations

Un reste de la fiche `pension_non_salaries_agricoles_2026` : « le revenu des
années cotisées au minimum, que L. 732-24 déduit des cotisations et que le
moteur porte au plancher de six cents SMIC horaires ».

**La règle, lue.** Code rural, L. 732-24, I, 1°, second alinéa
(LEGIARTI000053280317) : « Pour les assurés dont les cotisations mentionnées
au 1° de l'article L. 731-42 [...] dont ils ont été redevables au titre des
années comprises entre 2016 et 2025 ont été portées à leur valeur minimale,
les revenus pris en compte pour l'application du premier alinéa du présent 1°
sont égaux au rapport entre les montants totaux des cotisations qu'ils ont
acquittées au titre de l'assurance vieillesse de base et les taux des
cotisations en vigueur pour l'année considérée ». Aucun décret n'en dit
davantage dans l'index LEGI. Les cotisations de base du chef de 2016 à 2025
(L. 731-42, rédactions de 2010 et de 2023) : l'AVI du 1°, 3,32 % (D. 731-121),
sur 800 SMIC horaires du 1er janvier au moins (D. 731-120, 1°), due « à
l'exception des personnes mentionnées à l'article L. 732-28 », les chefs à
titre secondaire ; l'AVA plafonnée du 2° a), 11,55 % (D. 731-122), et l'AVA
déplafonnée du 3°, 2,14 % en 2016 et 2,24 % depuis (D. 731-124), sur 600 SMIC
au moins (D. 731-120, 2°). La rédaction de D. 731-124 à 2,36 %, en vigueur
depuis le 7 juillet 2024, ne vaut que pour les périodes de 2026 (décret
n° 2024-688, articles 5 et 6) ; la notice de 2025 de la MSA d'Île-de-France
applique encore 3,32 %, 11,55 % et 2,24 %, sur 800, 600 et 600 SMIC. L'AVI
est au minimum sous 800 SMIC, et le revenu de l'année vaut alors
(3,32 % × 800 + 13,79 % × le plus grand du revenu et de 600) / 17,11 % : 638,81
SMIC au minimum, 639,04 en 2016, 719,40 à 700 SMIC, et le revenu lui-même à
800. Ce que la page de la MSA « 25 meilleures années » en dit, l'outil ne le
lit pas ; aucun exemple publié ne la chiffre.

**Ce qui est fait.** `liquider.revenu_des_cotisations_minimales`
(`revenuDesCotisationsMinimales`), sur les minimums et les taux de
`COTISATIONS_DE_BASE_DU_CHEF`. `salaire_de_reference` l'applique, sous
`affilie_avant_2016`, aux lignes du chef à titre exclusif ou principal
(`Carriere.qualite_agricole`), au revenu de ses mois porté à sa part cotisée
l'année où il cesse, avant le plancher de 600 SMIC, que gardent le chef à
titre secondaire et l'assuré affilié depuis 2016, que la phrase ne vise pas ;
`pension_des_non_salaries_agricoles` le passe à qui a des trimestres agricoles
avant 2016. `test_le_revenu_des_annees_cotisees_au_minimum_se_tire_des_cotisations`,
posé à la main, dans les deux moteurs : 6 179,48 € en 2016 à 3 000 €,
7 217,32 € en 2020 à 7 000 €, 9 000 € gardés ; le chef de 1990 à 2025, parti
en janvier 2028, a une moyenne de 0,638 81 et 0,719 40 fois celle du chef à
1 000 SMIC, et non 0,6 et 0,7. La fiche et `docs/limites/4-regimes-incomplets.md`
le disent.

**Ce qui bouge.** Rien sur les témoins : aucun des 892 témoins de simulation
ni des 79 rendus de page ne fait liquider après 2025 un chef dont l'AVI était
au minimum de 2016 à 2025 (`resumer_temoins.py`, après `regenerer.py`). Le
README suit le poids du portage, un kilo-octet de plus, et le tableau de bord
une rédaction de L. 731-42 passée d'« à examiner » à « à rattacher », le
cliquet des textes restant le même.

**Restes, trouvés en chemin.** Le collaborateur et l'aide familial : leur AVI
se prenait jusqu'en 2025 des revenus du chef, à 800 SMIC au moins ; quand elle
y était, leur revenu serait (3,32 % × 800 + 11,55 % × 400) / 14,87 %, 489,31
SMIC, et non le forfait de 400, mais le moteur ne connaît pas les revenus du
chef (un champ de saisie, pour une session du site). Les durées de R. 173-3-2,
que le texte arrête au 31 décembre de l'année d'effet pour le régime agricole
et au dernier jour du trimestre civil qui la précède pour les régimes alignés :
l'année de cessation, comptée entière depuis le 16 octobre, en couvre le cas
ordinaire, et la durée des régimes alignés de la première répartition
(`Durees.cumul_plafonne`) ne borne pas aux trimestres civils écoulés une
période assimilée sans ligne (note `2026-10-16-r-173-4-3-au-trimestre-civil.md`).
Les majorations de points de 1952 à 1972 (R. 732-67) renvoient à D. 732-76 et
D. 732-77 dans leurs rédactions d'avant 2026, et au barème d'avant 1990, que
le moteur ne lit pas.

**Ce qui attend le propriétaire.** Rien.
