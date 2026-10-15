# Étape 4, sixième partie : le fonds de solidarité vieillesse relu juste, de 2021 à 2025

**La demande.** Après la cinquième partie, la certification des transferts
gardait dix écarts : les cotisations et les prestations que le fonds de
solidarité vieillesse prend en charge, de 2021 à 2025, lues à quelques
centaines de millions d'euros quand la référence en dit quinze et quatre
milliards. Le propriétaire demande de les corriger. L'enjeu dépasse la
fabrique : cette série entre dans le retrait du modèle depuis le 19 septembre
2026 (`equilibre.py`, qui lit `transferts_retraite.csv`), et un
`verifier_donnees.py --appliquer` aurait remplacé la référence, juste, par
ces lectures fausses.

**Ce que l'enquête a montré.** Le script des transferts n'a pas changé depuis
le 19 septembre ; le lecteur de cette date, 226 lignes de Python, rejoué sur
le rapport de 2022, rend exactement la référence : 14 969 M€ de cotisations
en 2021, dont 14 560 sur la ligne de la CNAV. C'est le lecteur qui a changé,
de deux façons. L'écart des images, ajouté depuis, ignorait le formulaire qui
porte le compte de la CNAV (la cinquième partie l'a corrigé, et rendu les
années 2015 à 2020) ; et, le formulaire relu, sa ligne sortait défigurée,
« POises en cMaOge de cotisations paO le FSV 13 355 14 333 7E3… », que le
motif ne reconnaissait plus. Excel pose chaque cellule entre `q` et `Q`, et la
police d'une seule — une Type0 — avant des cellules qui n'en reposent aucune :
en PDF, la police est de l'état graphique, que `Q` rend, mais le lecteur
gardait la dernière posée, et traduisait les octets des cellules suivantes par
sa table, « r » devenant « O ». Le rapport de 2026, enfin, avait sa propre
difficulté.

**1. `Q` rend la police et l'interligne d'avant `q`** (commit a8ff162).
`q` sauve, avec le repère, la police et l'interligne, que `Q` rend. Mesure :
657 lignes de 11 documents se réparent, et ce n'était que du texte défiguré —
« ContOiLutionsE impts et taxes » redevient « Contributions, impôts et
taxes », « CSG LOute » « CSG brute », les virgules décimales reviennent
(« -14E9 » pour « -14,9 »), des montants perdus reparaissent, et des phrases
entières (« =OMNRI=é dÉ= NMT… » pour « En 2015, plus de 107 000 nouveaux
retraités du régime »). Parmi les valeurs, seules bougent celles des
transferts : le fonds de 2021 à 2024 retrouve exactement la référence (14 969,
13 522, 14 512 et 15 245 M€ de cotisations ; 3 771, 3 639, 3 908 et 4 325 M€
de prestations). Les dix autres scripts sont identiques.

**2. Un double signe tient la place d'un taux** (commit c132bea).
L'édition d'automne du rapport de 2026 écrit la ligne du fonds dans le compte
de la CNAV « 15 064 15 691 4,2 0 -- 0 -- - 0 - » : le fonds disparaît en
2026, ses colonnes de prévision sont nulles et leurs taux sans objet. La
fonction qui lit une ligne exige autant de taux, à un près, que l'en-tête de
colonnes « % », et sautait les « -- » sans les compter : la ligne se
rejetait, et 2025 tombait à 189 M€. Un double signe ne s'écrit que dans une
colonne de taux, et compte désormais comme un taux ; le tiret seul reste une
cellule vide. Le lecteur de septembre la rejetait aussi : la référence de
2025 a dû être lue dans l'édition de printemps du même rapport, la seule
parue le 19 septembre. Mesure : 2025 retrouve
la référence (15 880 et 4 625 M€) ; `ccss_regimes.json`, qui emprunte la
même fonction, gagne 4 valeurs (les produits AT-MP de la SNCF, des charges
financières de l'Ircantec) et en voit 2 écartées : le rapport de 2014
compte 187 et 42 bénéficiaires d'invalidité dans les autres régimes en 2012 et
2013, celui de 2015, sur un périmètre élargi, 1 846 et 1 618, et la
réconciliation écarte ce désaccord comme elle le doit.

**La certification sort propre** : les 87 valeurs des transferts sont
identiques à la référence, il ne reste aucun point à examiner, et le contrôle
rend 0 au lieu de 1. Le modèle ne bouge pas : il lit la référence, que la
fabrique retrouve. Deux tests nouveaux, l'un dans `tests/test_lecture_pdf.py`,
l'autre dans `tests/test_ccss_transferts_retraite.py`, au niveau contrôle ;
2 402 rapides, 7 du site, 1 488 de contrôle, 31 de node.
