# Étape 3, vingt-quatrième partie : la dépense nette sur la page Coût, à côté de la brute

**La demande.** Vague du 28 octobre 2026, une session par tâche qui se mène
sans le propriétaire, celle-ci seule sur les pages : le point du site « la
dépense nette » du bloc de l'étape, le point 1 de « Ce qui reste » de la note
du taux effectif (24 octobre) — la dépense nette à côté de la brute, dans le
bilan ; le paragraphe « Et en BRUT, des deux côtés », qui disait la masse
nette « au plus » au taux plein ; puis le registre. Ni la phrase des poids, à
une session suivante, ni ce que le bloc réserve au propriétaire.

**Le bilan de la bascule.** Le tableau « Recettes et dépenses, poste par
poste », que `bilanBascule` tire du bilan figé à l'année de bascule, porte
sous le solde une ligne « Pour mémoire, dépenses nettes des prélèvements
sociaux des retraités », pour le système actuel et la proposition
(`depenseNette`) : en 2026, 393,8 Md€, 13,16 % du PIB, pour 422,5 et 14,13 en
brut ; 247,2 Md€, 8,27 %, pour 265,3 et 8,87. Sa part, 93,2 % des dépenses des
deux côtés, dit le même taux pour les deux systèmes. La ligne suit le solde et
ne le change pas : le compte reste en brut des deux côtés, ses ressources
comptant la CSG prélevée sur les pensions. Le graphique de tête, que le code
nomme aussi `bilan`, n'a pas reçu de courbe nette : posée à côté des
ressources brutes, elle aurait fait lire un solde qui n'existe pas.

**« Et en BRUT, des deux côtés ».** La masse nette y était chiffrée au taux
plein, 9,1 %, et dite « au plus » : c'en était au contraire la plus petite
valeur, les pensions modestes étant exonérées ou au taux réduit. Elle l'est
désormais au taux que le bilan figé porte cette année-là (`tauxEffectif`,
`anneeTauxEffectif`) : 6,8 %, ce que la DREES mesure en 2022, dernière année
publiée ; 12,75 % du PIB en 2024, 374 Md€, pour 13,68 % et 401 Md€ en brut,
avant l'impôt sur le revenu, que l'Ageing Report retire aussi. Le paragraphe
nomme la cotisation maladie des complémentaires, que la nette de la DREES
déduit. La CSG « circulaire » du paragraphe suivant reste au taux plein, une
borne haute, juste : le taux effectif mêle la CSG aux trois autres
prélèvements.

**Le registre.** Le prélèvement effectif de TAXIPP et la dépense nette de
l'Ageing Report passent à `repris` (138.3), chacun avec sa vérification
datée.

**Les tests**, vus rouges pour la raison attendue avant le code, la valeur
tirée de la DREES et non du code — 117 € de prélèvements sur 1 719 € de
pension moyenne en 2022 : `test_web.py`, la ligne du bilan de la bascule et la
masse nette des sources ; `test_affirmations.py`, le contrôle
`compte_en_brut_et_recette_circulaire`, qui exige la nette au taux de la
DREES, sous la brute et au-dessus de ce que le taux plein en laisserait, et sa
ligne au catalogue.

**Ce que ça déplace.** Les cinq rendus de la page Coût et sa page toute
faite ; aucun témoin de simulation. Coût tout déplié passe à 33 243 mots, sous
ses 33 250 : le paragraphe récrit rend les mots que la ligne et la phrase du
taux coûtent. Aucune donnée ni le paquet : la page lit ce que le bilan figé
porte depuis le 24 octobre.

**Ce qui reste**, de cette partie ; le reste de l'étape est dans son bloc.

1. *La CSG « circulaire » au taux effectif* : il faudrait la part de la CSG
   dans ce que les prélèvements prennent, que la CCSS publie en masse (23,7 Md€
   sur les retraites en 2023), et la part qu'en reçoit la vieillesse.
2. *Les montants de 2023 et 2024* et *l'impôt sur le revenu des pensions* : les
   points 2 et 3 de la note du taux effectif, inchangés.
