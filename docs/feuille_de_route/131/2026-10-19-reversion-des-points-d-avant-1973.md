# La réversion des points d'avant 1973 des artisans et commerçants, et son minimum avec la pension alignée (D. 634-14)

Le reste que la note de D. 634-6 (`2026-10-19-minimum-de-d-634-6.md`, « Restes,
trouvés en chemin ») avait laissé : le minimum de la réversion de l'artisan ou
du commerçant, que D. 634-14 borne comme D. 634-6 borne son minimum
contributif. Lu, il demandait d'abord ce qu'il borne : la réversion des points
d'avant 1973, que le moteur ne servait pas — sa ligne disait « pas encore
portée ».

**La règle, lue.** D. 634-14, depuis le 1er janvier 1990 (LEGIARTI000006738001),
et avant lui l'article 7-2 du décret n° 73-937, ajouté par le décret n° 76-214
au 5 mars 1976 (LEGIARTI000006765831) : pour le minimum de la réversion, « il
est tenu compte, le cas échéant, du montant cumulé de la pension de réversion
allouée au titre des périodes d'assurance postérieures au 31 décembre 1972
dont justifiait l'assuré décédé et de l'avantage de réversion alloué au titre
des périodes d'assurance et d'activité non salariée de l'assuré antérieures
au 1er janvier 1973 ». Cet avantage, l'article 9 du même décret le dit depuis
1990, en cinq rédactions (LEGIARTI000006765834 à 026474709) : il est accordé
« lorsque sont remplies les conditions fixées aux articles L. 353-1, L. 353-2,
ou L. 353-3 », « compte tenu » de D. 353-1 et des articles qu'il cite, et vaut
52 % des points depuis décembre 1982, 54 % depuis 1995, majoré comme L. 353-6
le dit depuis le 7 octobre 2012 ; avant 1990, son article 13-5, que l'index
n'a que dans sa rédaction de 1984 (LEGIARTI000006765860), renvoyait de même au
régime général. Avant 1976, les décrets n° 64-994 (articles 31 à 33) et
n° 66-248 (articles 21 et 22) en servaient la moitié des points à
soixante-cinq ans, sans minimum. La circulaire du RSI n° 2010/016 sert la
majoration de 11,1 % sur « les deux composantes des pensions de réversion
servies par le RSI : la pension ancien régime en points [...] et la pension du
régime aligné », chacune à 54 % ; la n° 2012/016 range le « complément
minimum » dans « le montant du régime aligné à servir ». Aucune ne dit la durée
qui proratise le minimum ; aucun exemple publié : les tests sont des cas posés
à la main depuis le texte.

**Ce qui est fait.** Les droits d'avant 1973, `cancava_avant_1973` et
`organic_avant_1973`, entrent dans la fiche `reversion`, et deux paramètres de
ses versions les disent : `droits_d_avant_1973`, chacun et la caisse qui lui
succède, sans les majorations pour enfants, que l'article 9 ne cite pas ;
`minimum_avec_les_droits_d_avant_1973`, faux avant juillet 1974 (pas de
minimum), vrai depuis. Le minimum de la réversion (`_groupes_du_minimum`,
`groupesDuMinimum`) compte chaque régime sous sa tête de succession à la
liquidation du défunt, et les droits d'avant 1973 avec la caisse qui leur
succède : les réversions d'un même régime n'ont qu'un minimum, sur leurs durées
réunies, que la première ligne alignée sert en complément des autres ; les
majorations forfaitaires de 1982 et 1995 suivent (`_majorations_ulterieures`,
`autres`). Quatre tests de règle (`test_reversion.py`) : les points reversés à
52 et 54 % ; le minimum du montant cumulé, 2 182,74 € et 540 € pour la veuve du
commerçant mort en 2000, les 45/60 du minimum moins 260 € en 1990, le minimum
entier moins 500 € en 1980 ; le RSI qui sert le minimum des années de la
CANCAVA ; pas de majoration de 10 % sur les points. Un cinquième, dans les deux
moteurs (`test_les_deux_moteurs_reversent_les_droits_d_avant_1973`), sur trois
carrières entières. La fiche le dit : intitulé, lectures, versions qui citent
les rédactions, deux approximations, une lecture divergente, l'historique.

**La lecture.** D. 634-14 ne dit que « le montant cumulé » : le modèle compte
pour le proratiser les deux durées du défunt, celles d'avant 1973 comprises,
comme D. 634-6 le dit du minimum contributif, la réversion bornée
« correspond[ant] » à toutes deux (D. 353-1). De juillet 1974 au 4 mars 1976,
l'article 7-2 est appliqué avant sa date, avec les conditions du régime
général, que le décret de 1964 ne posait pas encore. La fiche le déclare.

**La classe.** La même erreur, sans les droits d'avant 1973 : la part du
minimum comptait chaque caisse à part, et la CANCAVA que le RSI ou le régime
général liquide avec lui gardait sa part du prorata sans ligne pour la servir.
La veuve de l'artisan né en 1950, 132 trimestres à la CANCAVA et 19 au RSI, mort
en 2015, avait 19/151 du minimum : elle a le minimum entier. Corrigé avec la
règle, par la tête de succession, que la liquidation lit déjà. La liquidation
unique faisait déjà un régime des régimes alignés.

**Ce qui bouge.** Les trois carrières du test : la veuve de l'artisan né en
1928, mort en 2000, reçoit 2 208,77 € de réversion alignée et 513,97 € de ses
points, au lieu de 2 722,74 € et rien, le total au minimum ; celle du
commerçant, 2 083,96 € et 638,78 € ; celle de l'artisan né en 1950,
3 315,45 € et 91,02 € au lieu de 1 680,45 € et rien, plus 1 726 € par an.
Aucun des 888 témoins de simulation ne bouge (`resumer_temoins.py`, après
`regenerer.py`) : aucun n'a de points d'avant 1973 avec un décès, ni de
réversion du RSI sous son minimum ; les agrégats du coût restent les mêmes. Un
rendu de page, le programme, bouge par la mesure `dette_2070_proposition`
(75 → 76 %), comme la note de D. 634-6 le disait : elle tient aux commits
d'avant celui-ci, que GitHub n'a pas encore refaits. Le paquet grossit de
7 Ko. Les fichiers fabriqués, refaits pour mesurer, ne sont pas commités.

**Restes, trouvés en chemin.** La réversion de la complémentaire des
artisans d'avant 2013 (`rco_artisans`) ne se sert pas pour un décès d'avant
2013 : la fiche `reversion_rci` le dit déjà. Le régime général et le RSI, qui
ne font qu'un pour D. 353-1 depuis le 25 mai 2020 (« dans le régime général ou
le régime social des indépendants »), ne sont un régime du minimum que quand la
liquidation du défunt les réunit, depuis 2018 : la réversion d'après 2020 d'un
défunt qui avait une pension de chacun garde deux minima au prorata, que la
fiche déclare. Une circulaire de la CANCAVA, de l'ORGANIC ou du RSI qui
applique D. 634-14 et dise la durée de son minimum ; le texte de l'article 13-5
de 1976.

**Ce qui attend le propriétaire.** Rien de neuf.
