# Correction de la ligne 4 de la file : la réversion de la CARCDSF servie

Quatrième ligne de la file `2026-11-13-corrections-decidees.md`, décidée par le
propriétaire le 13 novembre 2026. Une ligne, rien d'autre.

**Le texte, relu à l'index du Journal officiel** (à jour du 11 novembre 2026). Statuts de
2007, articles 39 à 49 (arrêté du 1er octobre 2007, JORFARTI000002063756, en vigueur le
11 octobre) ; statuts de 2011, articles 32 à 42 (arrêté du 13 avril 2011,
JORFARTI000023909792, en vigueur le 1er juillet) ; règlement de 2026, articles 9 à 19
(arrêté du 10 juillet 2026, JORFARTI000054435749, en vigueur le 18 juillet). Les trois
disent la même règle, aux mots « chirurgien-dentiste », « adhérent » puis « affilié »
près : le conjoint survivant « reçoit à 65 ans ou à partir de 60 ans en cas d'inaptitude au
travail, une retraite de réversion du régime complémentaire », « égale à 60 % de la
retraite complémentaire versée ou qui aurait été versée au titulaire » ; elle « n'est
accordée au conjoint survivant que si la date du mariage a précédé de deux ans au moins la
date du décès », sauf « enfant issu du mariage » ; elle « est supprimée en cas de
remariage » ; « L'ex-conjoint divorcé non remarié est assimilé à un conjoint survivant »,
et le partage se fait « au prorata de la durée respective de chaque mariage » ; la
« bonification de 10 % pour enfants » s'y applique. Les arrêtés de 2012 et de 2017 n'en
disent rien ; celui du 27 décembre 2023 n'y touche que pour l'autre régime de la caisse,
les prestations complémentaires de vieillesse (article 35 bis). La caisse le confirme
(« Condition d'attribution de réversion dans les régimes RC et PCV », janvier 2024) : 65
ans, deux ans de mariage, 60 %, 10 % « si le conjoint a eu au moins 3 enfants avec le
titulaire », aucune condition de ressources. Aucun exemple chiffré publié. Le texte
tranche ce que la ligne dit.

**Le test d'abord** (`tests/test_reversion.py`, section « la complémentaire des
chirurgiens-dentistes et des sages-femmes »), vu rouge sur le premier cas posé (taux nul,
motif `non_portee`). Posés à la main : les deux cas de la note du 5 novembre, 60 % ×
6 912,27 = 4 147,36 € et 60 % × 9 423,69 = 5 654,21 €, au premier jour du mois qui suit le
décès ; la survivante née le 10 mars 1960, servie le 1er avril 2025 ; les statuts de
2007 ; deux ans de mariage, ou un enfant ; le remariage, et le pacte civil qui ne retire
rien ; les deux tiers à la survivante de 240 mois devant une précédente de 120 ; la
bonification, 60 % × 6 912,27 × 1,10 = 4 562,10 € ; rien pour un décès du 10 octobre 2007.
Puis le dentiste du formulaire (né le 1er juin 1950, parti à 65 ans, mort en juin 2020),
seul, avec trois enfants et marié en 2019 : servi par le portage, refait au bit près par
le moteur Python (`servi_et_refait`).

**L'effet aux cas posés** : 4 147,36 € par an au lieu de rien, et 5 654,21 € au second.

**La correction.** Une fiche, `reversion_carcdsf`, quatre versions sur la date du décès :
avant le 11 octobre 2007, non portée (le règlement de 1955 n'est à l'index que par des
notices) ; puis les trois textes, aux mêmes paramètres. Les deux moteurs la lisent
(`Reversions.FICHES`) par la branche qui sert déjà l'Agirc-Arrco, où deux paramètres
entrent : `mariage_minimum_annees`, la durée du mariage au décès sauf enfant (motif
`mariage`), et `portee: false`, que seule la complémentaire des indépendants savait dire.
L'âge, le partage, le remariage et la majoration reversée étaient des paramètres déjà
lus. Dans la fiche `carcdsf_minoration_age_seul`, l'erreur n'est plus déclarée : elle est
racontée au champ `effet`.

**Ce que la correction déplace.** Aucun témoin de simulation, aucune page : aucun témoin ne
porte un dentiste mort. Le paquet porte la fiche de plus.

**Ce que la correction laisse, déclaré dans la fiche `reversion_carcdsf`.**

- La réversion part à 65 ans : ni à 60 ans pour le survivant inapte, ni par anticipation
  dès 60 ans (minorée par l'âge en 2007, de 1,25 % par trimestre depuis 2011), que le
  survivant demande et que la saisie ne dit pas.
- La version se choisit au décès : le survivant d'un décès d'avant le 11 octobre 2007 n'a
  rien, même s'il atteint 65 ans sous les statuts de 2007.
- La bonification reversée est celle du défunt : ses enfants sont tenus pour ceux du
  survivant, et tout enfant déclaré lève la condition de mariage.
- Les sages-femmes d'avant le 1er juillet 2011, que les statuts de 2007 ne nomment pas.
- La date d'effet au mois, non au trimestre civil qui suit la demande (ligne 12).

**La classe, pour les lignes suivantes.** L'autre régime de la caisse, les prestations
complémentaires de vieillesse, que la caisse reverse aussi à 60 %, reste non porté, comme
la réversion de la CAVAMAC (ligne 30), de la CAVEC, de la CARPV et des autres sections : la
file ne nomme que la CAVAMAC. Chacune n'est plus qu'une fiche à écrire, si son texte tient
dans ces paramètres.

**Vérifié** : `python -m pytest -m rapide`, `test_reversion.py`, `test_carte.py`,
`test_sections_sante.py`, `test_sections_liberales.py`, `test_pont.py`, `test_donnees.py`,
les confrontations légères (`test_oracle.py`, `test_destinie.py`,
`test_estimation_officielle.py`, `test_verification.py`), `tests/js/moteur.test.js`, verts.
