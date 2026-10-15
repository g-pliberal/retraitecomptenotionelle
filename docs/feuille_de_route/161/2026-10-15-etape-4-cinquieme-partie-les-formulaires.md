# Étape 4, cinquième partie : les formulaires pris pour des images, lus, et la fabrique qui les lit sans se tromper

**La demande.** La quatrième partie avait laissé au propriétaire un cinquième
défaut : l'écart des images, la chaîne « /Image » cherchée dans le
dictionnaire d'un flux, écartait 382 formulaires porteurs de texte, et les
lire égarait `ccss_regimes.py`. Le propriétaire demande de le corriger, en
relisant ce qui bouge.

**Ce que la relecture a montré.** `ccss_regimes.py` cherchait les chiffres
d'un tableau « Données générales » au voisinage de son titre, dans l'ordre du
fichier. Or les rapports à la CCSS collent leurs tableaux depuis Excel, en
formulaires que la page pose : la page porte le titre, le formulaire les
lignes, et le rang d'un formulaire dans le fichier ne dit rien de la page qui
le pose — le rapport de 2018 range ceux d'une fiche juste après sa page,
celui de 2023 juste avant. Lire les formulaires retrouvés l'égarait de deux
façons : sa lecture, qui ne s'arrêtait qu'au titre « Données générales »
suivant, enchaînait sur le compte de la branche vieillesse de la MSA salariés,
dont l'intitulé « CHARGES NETTES (hors transfert d'équilibrage) » écrasait la
valeur toutes branches (11 345 M€ devenus 5 884 en 2016) ; et un formulaire
retrouvé, posé entre un titre et ses chiffres, repoussait l'en-tête au-delà
des trente lignes où on le cherchait, si bien que le tableau des autres
régimes de 2018 disparaissait. Mais ces erreurs n'étaient pas nouvelles : avec
l'ancienne lecture déjà, la MSA salariés de 2019 portait les charges de sa
seule branche vieillesse, les trois tableaux des régimes complémentaires d'une
même page se lisaient tous à partir du premier formulaire, et la CNAVPL de
2023 portait les effectifs des autres régimes, rangés après sa page.

**1. Le lecteur dit quels formulaires chaque page pose** (commit 983ed1e).
`pagesEtFormulaires` — `pages_et_formulaires` pour la fabrique — rend les
pages de `lignesParPage` et, pour chacune, les formulaires qu'elle pose par
`Do`, nommés dans ses ressources ou celles qu'elle hérite de l'arbre, dans
l'ordre de son contenu, ceux qu'ils posent à leur tour compris. Rien de ce
que le lecteur rendait ne change : les 36 documents gardent leurs pages, et
3 694 formulaires se rattachent à 1 927 pages ; la page de la CNAVPL de 2023
retrouve ses cinq formulaires, rangés avant elle.

**2. `ccss_regimes.py` lit le formulaire de son titre** (commit 14d0e3d). Le
k-ième titre « Données générales » d'une page lit le k-ième des formulaires
qu'elle pose qui s'ouvrent sur une ligne d'années et portent des effectifs,
et lui seul : l'appariement tombe juste pour les 241 tableaux qui en ont ; un
seul, écrit dans sa page, garde la lecture de voisinage, désormais bornée à la
ligne d'années du tableau suivant et aux pages qui ne sont pas des
formulaires. L'en-tête d'un formulaire se lit même désordonné, ses années
remises dans l'ordre (« % 2017 % 2018 (p) % 2019 (p) % 2016 » à l'ENIM en
2018), ou une année coupée (« 2 015 ») ; et une ligne dont les montants se
suivent sans taux entre eux se partage également entre les années — « 157 784
166 049 174 544 183 494 » rendait 157, 784, 166 et 49. Mesure, sur l'ancienne
lecture : de 5 866 valeurs à 2 881. Partent 3 402 valeurs : 3 123 sont des
lignes d'autres tableaux, des comptes de résultat surtout (« Droits propres »,
« PRESTATIONS SOCIALES NETTES »), que l'ancien script versait dans les données
générales ; des 279 qui en ont l'allure, 96 passent sous le bon tableau, 100
tombent à la réconciliation entre rapports, et les 83 autres, relues par
échantillon, étaient mal attribuées ou portaient l'intitulé d'un compte de
résultat — la SNCF garde son 2 155 sous l'intitulé du tableau lui-même.
Viennent 417 valeurs, dont 399 de données générales ; 197 changent, et ce
sont des corrections : les charges de la MSA salariés, de 5 899 à 11 534 M€,
celles du régime complémentaire de la CNAVPL, de 336 — le chiffre de son
invalidité-décès — à 3 431. Les désaccords entre rapports tombent de 450 à
186, les écarts de magnitude de 370 à 167, et l'identité « bénéficiaires =
droits directs + droits dérivés » tient pour 84 % des triplets au lieu de
50 %. `ccss_regimes.json` n'a pas de lecteur dans le dépôt. Quatre tests
nouveaux, `tests/test_ccss_regimes.py`, au niveau contrôle.

**3. Une image se reconnaît à son `/Subtype`** (commit 0b02554). Les 382
formulaires se lisent : 15 documents gagnent 9 182 lignes, et n'en perdent
aucune. `ccss_regimes.json` est le même avec ou sans eux.
`ccss_transferts_retraite.json` corrige dix valeurs du FSV — ses prestations
et ses cotisations de 2015 à 2020, lues jusqu'ici de travers, 17 M€ pour
11 153 — et en gagne deux, les cotisations de 2015 et 2016 : la certification
des transferts passe de 65 à 77 valeurs identiques à la référence, ses écarts
de 20 à 10. `ccss_impots_retraite.py` lit ses rapports de 2014 et 2015, sans
valeur neuve. Les huit autres scripts et le reste de la certification sont
identiques.

**Les tests.** 2 402 rapides, 7 du site, 1 486 de contrôle, 31 de node.

**Relevé en passant, et laissé.** Les dix écarts qui restent à la
certification des transferts, le FSV de 2021 à 2025, que
`ccss_transferts_retraite.py` lit de travers. Dans un tableau de données
générales, un intitulé répété — « droit direct » sous la vieillesse puis sous
l'invalidité, à l'ENIM et au FSPOEIE — est écrasé par sa seconde occurrence.
L'identité ne tombe pas non plus juste à la MSA, qui compte à part les
retraités de droit direct et dérivé. Restent 186 désaccords entre rapports,
révisions de périmètre ou lectures fausses, que la réconciliation écarte.
