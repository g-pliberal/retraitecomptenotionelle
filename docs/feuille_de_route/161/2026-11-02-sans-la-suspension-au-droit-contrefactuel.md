# Le coût sous un modèle modifié : « sans la suspension » au droit contrefactuel du moteur — les deux écarts vérifiés, la copie retirée

**La demande.** La réponse du propriétaire, ce 2 novembre 2026, transmise par
la session d'orchestration, à la question que posait la note
`2026-11-02-les-donnees-d-ailleurs.md` : oui. La colonne « sans la
suspension » de `scripts/facteurs_depense.py` passe au droit contrefactuel du
moteur, `loi_2023_sans_suspension`, même si ses chiffres bougent d'un
centième de point de PIB au plus ; vérifier au passage les deux écarts de
construction que la note décrivait, et dire lequel des deux calculs est le
plus juste. Le site n'est pas touché : la file D y travaille.

**Le premier écart, la carrière longue.** Les textes, tels que
`carriere_longue.csv` les porte, lus et certifiés : sous la loi de 2023, la
borne des vingt ans de D. 351-1-1, II (version du 1er septembre 2023) donne
61 ans à la génération 1966, 61 ans et 3 mois à 1967, 61 ans et demi à 1968,
61 ans et 9 mois à 1969, 62 ans à partir de 1970 ; le décret n° 2026-345 du
7 mai 2026, pris avec la suspension pour les pensions prenant effet à compter
du 1er septembre 2026, les avance d'un trimestre — 60 ans et 9 mois à 1966,
puis un trimestre par génération jusqu'à 62 ans en 1971. La copie gardait le
décret de 2026 avec l'âge légal de 2023, deux lois mêlées ; le droit
contrefactuel l'ôte (`CarriereLongue.avant`). Le contrefactuel est exact. Sur
la grille : le salarié au SMIC entré à 18 ans, sa seule carrière longue, né en
1967 ou en 1968, part en mai 2028 et en août 2029, non en février 2028 et en
mai 2029. Son poids : presque rien.

**Le second écart, la complétude.** La complétude d'une génération est sa durée
validée moyenne rapportée à sa durée requise (`CarrieresIncompletes`). Pour les
générations 1954 à 2000, ces durées sont projetées
(`duree_assurance_generations.csv` : l'EIR de 2020 prolongé par TRAJECTOiRE
sous les hypothèses du COR de juin 2026), donc sous le droit d'alors, la
suspension comprise. La copie les rapportait à la durée requise sans la
suspension, 171 et 172 trimestres pour 1964 et 1965 au lieu de 170 : la
complétude de ces deux générations baissait de 0,6 et 1,2 %, et leurs
pensions avec elle, quand la grille les fait déjà travailler jusqu'à la
durée plus longue. Le contrefactuel garde le rapport du COR, durée et
exigence sous le même droit : cohérent, non exact — il faudrait des durées
projetées sans la suspension, que le dépôt n'a pas. C'est presque tout
l'écart.

**La mesure de chacun.** Un calcul hybride, la copie retouchée sous le droit
contrefactuel — sa complétude et la carrière longue de 2023 —, par le
portage, sur le paquet de la copie, en 50 secondes. La copie, l'hybride, le
contrefactuel : sur 2022-2030, la variation de la dépense, +0,4224, +0,4226,
+0,4312 point de PIB ; l'effet de la prestation, −0,1697, −0,1696, −0,1613 ;
la dépense de 2070, 15,7817, 15,7817, 15,7808 points ; les retraités de 2030,
17 759 679, 17 759 679, 17 759 560. La carrière longue déplace la quatrième
décimale ; la complétude, la deuxième.

**Le plus juste, pour « sans la suspension ».** Le droit contrefactuel, sur les
deux points : exact pour la carrière longue, cohérent pour la complétude, où la
copie mêlait deux lois.

**Le remplacement.** `scripts/facteurs_depense.py` calcule la colonne sous
`DROIT_SANS_SUSPENSION`, par `parametres(projection, droit)`, que `modele` et
`recomptee` prennent à la place d'une racine ; `reforme_entiere` et
`REFORME_2023_ENTIERE` partent, avec trois imports. La colonne se calcule sur
les données du dépôt : la mémoire des calculs la garde, quand la copie la
refaisait à chaque lancement. Le script, lancé avec `--sans-suspension`, rend
sur 2022-2030 une dépense de +0,43 point et non +0,42, une prestation de
−0,16 et non −0,17 ; la ligne « la suspension » du départage reste à +0,06.
Aucun chiffre ancré, aucune page n'en dépend.

**Ce qui reste du chemin de la copie.** Le paquet des données d'ailleurs, sa
garde et l'aiguillage (note précédente) restent, avec leurs tests de
`tests/test_pont.py`, qui bâtissent leur propre copie : aucun script du dépôt
ne s'en sert plus, mais ils ferment le défaut latent, et le jumeau Python, qui
calculait ces données, partira.

**Tests.** Vu rouge d'abord (le script n'avait pas de `parametres`) :
`test_sans_la_suspension_la_grille_part_sous_la_loi_de_2023_entiere`
(`tests/test_facteurs_depense.py`, rapide), les jumeaux Python empêchés de
calculer, ses dates posées à la main depuis les textes — le salarié au salaire
moyen des générations 1964 et 1965 en novembre 2027 et en février 2029, le
salarié au SMIC de 1967 et de 1968 en mai 2028 et en août 2029. Les deux tests
de la copie de la note précédente partent avec elle. Puis `-m rapide`, les
tests de `facteurs_depense`, et le script lancé de bout en bout.

**Ce qui reste.** Les sous-étapes 3 à 6 du plan, une par session : la
proposition prospective en univers, le stock à l'âge légal, le régime unique
par barème, puis le levier `pont.par_le_jumeau()` réservé aux confrontations.
