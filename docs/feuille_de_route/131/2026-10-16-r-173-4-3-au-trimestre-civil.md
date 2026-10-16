# R. 173-4-3 : les durées arrêtées au trimestre civil qui précède la date d'effet

Le dernier reste de R. 173-4-3 (section 131, « Puis R. 173-4-3, porté »). La
circulaire Cnav n° 2004/29, relue par la recherche de la base de la Cnav
(`/api/v1/search/custom`, phrase « Années SAM maxi »), arrête la durée du
régime général « au dernier jour du trimestre civil précédant la date d'effet
de la pension » (point 2121), et celle des autres régimes alignés « au dernier
jour du trimestre civil qui précède la date d'effet de la pension du régime
général » (point 2122).

**Ce que faisait le moteur.** Une ligne de carrière de l'année de la date
d'effet est déjà bornée aux trimestres civils écoulés (`trimestres_civils`) :
pour elle, rien ne changeait. Mais une période assimilée de cette année sans
ligne de carrière — stage, sportif, congé de naissance, apprentissage —, que
`compter` arrête à la date d'effet même, n'était bornée qu'aux quatre
trimestres de `Carriere.plafond_trimestres`, faute de ligne. Né en 1952,
salarié puis artisan jusqu'en 2015, en stage de janvier à mai 2016, parti le
1er juin : le stage valide deux trimestres en 2016, et `duree_du_regime_aligne`
en comptait deux, quand la durée tous régimes, par `plafond_de_l_annee`, n'en
comptait qu'un.

**Ce qui est fait.** `liquider.duree_du_regime_aligne`
(`dureeDuRegimeAligne`) borne chaque année aussi par
`compter.plafond_de_l_annee` : 117 trimestres et non 118 dans l'exemple, que
`test_r_173_4_3_arrete_les_durees_au_trimestre_civil_qui_precede_l_effet`
rejoue dans les deux moteurs. La seconde répartition de R. 173-3-2, qui lit la
même durée, en profite. Aucun témoin ne bouge. La fiche
`salaire_annuel_moyen` cite les points 2121 et 2122.

**Reste, trouvé en chemin.** La durée de chaque régime que la proratisation
lit, `Durees.cumul_plafonne` (`trimestres_par_regime`), borne la même année
par `max(plafond de la carrière, plafond des assimilées)` : sans ligne, quatre
trimestres. Le régime général de l'exemple se proratise sur 118/164 au lieu de
117/164. Même correctif probable (`min` avec `plafond_de_l_annee` l'année de
l'effet), mais il touche la proratisation de tous les régimes : une étape à
part, avec ses témoins.
