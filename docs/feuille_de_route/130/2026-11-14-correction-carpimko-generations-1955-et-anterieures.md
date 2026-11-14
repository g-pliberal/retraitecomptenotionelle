# Correction de la ligne 19 de la file : la CARPIMKO ne majore pas avant l'âge légal de la base les générations 1955 et antérieures

Dix-neuvième ligne de la file `2026-11-13-corrections-decidees.md`, décidée par le
propriétaire le 13 novembre 2026. Une ligne, rien d'autre.

**Le texte, relu aux index JORF et LEGI** (à jour du 11 novembre 2026). Statuts
approuvés par l'arrêté du 31 juillet 2015, annexe (JORFARTI000031255547). Article
12 ter : « Lorsque la liquidation de la retraite est ajournée au-delà de l'âge auquel
elle aurait pu être liquidée sans abattement, les assurés peuvent bénéficier d'une
majoration de leur pension. » Article 11, 2°, a : le taux plein avant l'âge de la table
va aux assurés « liquidant leur pension du régime de base sans abattement » ; l'article
12 quater, 1°, « Par dérogation aux dispositions de l'article 11 », donne à la
« GÉNÉRATION 1955 ET ANTÉRIEURE » l'« Age prévu à l'article 11.2 (a) 60 ans ». La base
ne se liquide qu'à son âge légal : L. 643-3, I (LEGIARTI000028498667), « à partir de
l'âge prévu au premier alinéa de l'article L. 351-1 » ; D. 161-2-1-9
(LEGIARTI000025089933, du 31 décembre 2011 au 1er septembre 2023), « Soixante et un ans
et sept mois pour les assurés nés en 1954 », « Soixante deux ans pour les assurés nés à
compter du 1er janvier 1955 ». Arrêté du 27 décembre 2023, annexe, 3° et 6°
(JORFARTI000048880643, publié le 9 janvier 2024) : il récrit l'article 12 quater sans
son 2°, et ôte de l'article 12 le renvoi aux assurés nés avant 1956.

Le texte tranche ce que la ligne dit, pour ces générations et ces années : dans la
lecture que le modèle garde, la pension ne se liquide sans abattement avant 65 ans
qu'avec la base, donc pas avant son âge légal ; dans l'autre lecture (4 % par année
avant 65 ans, la durée fût-elle atteinte), rien n'est majoré avant 65 ans. Aucune des
deux ne majore avant l'âge légal de la base.

**L'erreur.** Le modèle faisait courir la majoration de l'âge où la durée est atteinte,
cherché depuis l'âge minimal de la table de la caisse, 60 ans pour ces générations.

**Le test d'abord** (`tests/test_sections_liberales.py`,
`test_la_carpimko_ne_majore_pas_avant_l_age_legal_de_la_base_les_nes_avant_1956`), vu
rouge (1,0375 où le texte donne 1,0125), puis vert. Auxiliaires médicaux entrés à vingt
ans, au double du salaire moyen, leur durée atteinte avant l'âge légal de leur base.

| né le | âge légal de la base | pension au | trimestres civils entiers d'ajournement | servi avant | servi depuis |
|---|---|---|---|---|---|
| 10 décembre 1954 | 10 juillet 2016 | 1er janvier 2017 | un, octobre à décembre 2016 | 1,0375, 5 681,23 € | 1,0125, 5 544,34 € |
| 10 décembre 1954 | 10 juillet 2016 | 1er janvier 2018 | cinq | 1,0875 | 1,0625 |
| 10 décembre 1955 | 10 décembre 2017 | 1er janvier 2019 | quatre, ceux de 2018 | 1,0750 | 1,0500 |
| 10 décembre 1956 | le texte ne tranche pas | 1er janvier 2020 | la lecture du modèle | 1,0625 | 1,0625 |

L'effet au cas posé de la ligne : 5 681,2345 / 1,0375 = 5 475,8887 € sans coefficient,
× 1,0125 = 5 544,34 €, 136,90 € par an de moins. Le test passe par `servi_et_refait` :
le moteur Python refait chaque cas au bit près. Un second test tient la donnée : la
borne est aux périodes qui liquident du 3 octobre 2015 à la fin de 2023, et à aucune
autre.

**Le code.** Un paramètre de période, `surcote_age_legal_de_la_base_jusqu_a_la_generation`
(schéma, chargeur, paquet), que `surcotePoints` et `surcote_points` lisent avec
`surcote_depuis_la_duree` : jusqu'à cette génération, l'âge où la durée est atteinte
n'est pas retenu avant l'âge légal de droit commun de la génération. Il vaut 1955 aux
périodes de 2016 à 2023 de `carpimko_complementaire.yaml`.

**Ce que la correction déplace.** Aucun des témoins de simulation ni de page. Fabriqués
refaits : le paquet et les témoins, rien d'autre.

**Les fiches.** `carpimko_ages_2015` : l'erreur sort des approximations et passe à
l'histoire (`effet`) ; l'approximation garde le point que le texte ne tranche pas, les
générations 1956 à 1960 de 2015 à 2024 et toutes depuis 2024 ; celle des 4 % par année
reprend les chiffres du modèle corrigé (rien dans la première lecture, 725,56 € dans la
seconde, au lieu de 136,90 € et 862,45 €). `surcote_par_age_seul` : le paramètre nommé
dans la description du code. Les limites ne nommaient pas cette erreur : rien à y
récrire.

**La classe, pas le cas.** `surcote_depuis_la_duree` n'est porté que par la CARPIMKO :
aucun autre régime ne compte une majoration depuis la durée atteinte.

**Ce qui reste déclaré.** La pension du 1er janvier 2024, que la période de 2024 sert
alors que les statuts de 2024 n'entrent en vigueur que le 10 : sans effet ici, le né de
1955 ayant 62 ans depuis vingt-quatre trimestres au moins, plus que les vingt de la
limite. Les 4 % par année de ces générations quand elles ont leur durée, non tranchés.
La majoration avant l'âge légal de la base pour les générations 1956 à 1960, et pour
toutes depuis 2024, non tranchée. Le décompte en trimestres écoulés depuis l'âge, et non
en trimestres civils : né le 10 décembre 1954, pension du 1er novembre 2016, le modèle
majore d'un trimestre (trois mois écoulés depuis le 10 juillet) quand aucun trimestre
civil entier ne tient entre les deux dates ; la date d'effet de ces années, dont
l'article n'est pas lu, dit si une telle pension existe. Le bloc « Reprise » de l'action
130 n'est pas récrit : la file dit où elle en est.
