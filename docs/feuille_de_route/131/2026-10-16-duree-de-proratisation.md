# La durée de proratisation arrêtée au trimestre civil qui précède la date d'effet

Le reste que la note de R. 173-4-3 (`2026-10-16-r-173-4-3-au-trimestre-civil.md`)
avait trouvé en chemin : la durée de chaque régime que la proratisation lit,
`Durees.cumul_plafonne`. Pris par une session ouverte le 16 octobre 2026 sur la
question du propriétaire, « les tâches à effectuer sans avoir besoin de mes
décisions » : celle-ci n'en attendait aucune.

**Ce que faisait le moteur.** `cumul_plafonne` bornait chaque année par le plus
grand de deux plafonds : celui de la carrière (`Carriere.plafond_trimestres`),
qui vaut quatre pour une année sans ligne, et celui des périodes assimilées,
qui l'année de la date d'effet ne compte que les trimestres civils écoulés.
Une période assimilée de cette année sans ligne de carrière — stage, sportif,
congé de naissance — y validait donc jusqu'à quatre trimestres. Le stagiaire
de la note de R. 173-4-3, né en 1952, en stage de janvier à mai 2016, parti le
1er juin : sa pension du régime général se proratisait sur 118/164, quand la
durée tous régimes et celle que R. 173-4-3 compare n'en comptaient que 117.

**La règle, lue.** R. 351-1 CSS (LEGIARTI000006749339, rédaction du 21 décembre
1985, toujours en vigueur) : les droits se déterminent sur les cotisations
« arrêtées au dernier jour du trimestre civil précédant la date prévue pour
l'entrée en jouissance de la pension » et sur « le nombre de trimestres
d'assurance valables pour le calcul de la pension ». La Cnav en tire l'arrêt
du compte : la durée « au sens de l'article L.351-1 3ème alinéa » — celle qui
proratise — « est arrêtée au dernier jour du trimestre civil précédant la date
d'effet de la pension » et « comprend [...] les trimestres assimilés »
(circulaire n° 2004/29, point 2121) ; l'arrêt du compte « limite[...] la
validation des périodes d'assurance » à ce jour (n° 51/98, point 1321 ;
n° 2002/71, point 132 ; n° 82/97, point 21 ; n° 2010/54, note 2, point 63).
Lues par la recherche de la base de la Cnav, R. 351-1 dans l'index LEGI.

**Ce qui est fait.** Le plafond d'une année est une méthode,
`Durees.plafond(table, annee)` (`plafond` en JavaScript) : les trimestres
civils de l'activité qui en couvre le plus, quatre pour l'année pleine d'une
période assimilée (R. 351-12), et, l'année de la date d'effet, ceux qui
précèdent le trimestre civil de l'effet, même sans ligne. `cumul_plafonne` le
lit, et `duree_du_regime_aligne` aussi : la durée que R. 173-4-3 compare est
celle de L. 351-1 (point 2121), et les deux ne divergent plus. Elles
divergeaient encore sur une année que la carrière ne couvre qu'en partie et
qu'une période assimilée complète : née en 1995, en stage de janvier à
septembre 2015, salariée depuis octobre, l'assurée compte quatre trimestres en
2015 dans les deux durées (176), quand R. 173-4-3 n'en comptait qu'un (173).
`test_la_duree_qui_proratise_s_arrete_au_trimestre_civil_qui_precede_l_effet`
rejoue les deux carrières dans les deux moteurs ; le test de R. 173-4-3 partage
avec lui son stagiaire (`_stagiaire_de_2016`). La fiche
`taux_plein_et_proratisation` lit R. 351-1 et les circulaires, et rattache la
rédaction : le cliquet des textes passe de 9 723 à 9 722.

**Ce qui bouge.** Seules les carrières qui déclarent une période assimilée
l'année de leur départ, sans ligne de carrière cette année-là, ou sur une année
partielle : aucun des 868 témoins de simulation ni des 75 rendus de page
(`resumer_temoins.py`), dont les chronologies n'en déclarent pas ; la saisie
des périodes assimilées vient à l'étape 5 du sixième domaine (action 130).

**Reste, trouvé en chemin.** Le régime des non-salariés agricoles prend « en
compte [...] les 4 trimestres de l'année de cessation d'activité même s'il
s'agit de l'année d'arrêt du compte au régime général » (circulaire Cnav
n° 2004/8, point 3232, qui renvoie aux circulaires n° 83/83 et 27/89) ; le
moteur borne la ligne de l'année du départ aux trimestres civils écoulés dans
tous les régimes (`Carriere.part_retenue_ligne`), celle de l'exploitant
comprise. À lire au code rural avant d'écrire : une étape à part, avec ses
témoins.

**Ce qui attend le propriétaire.** Rien.
