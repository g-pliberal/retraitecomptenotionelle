# L'année de cessation de l'exploitant agricole, comptée pour ses quatre trimestres

Le reste que la note de la durée de proratisation
(`2026-10-16-duree-de-proratisation.md`) avait trouvé en chemin : le régime
des non-salariés agricoles prend « en compte [...] les 4 trimestres de
l'année de cessation d'activité même s'il s'agit de l'année d'arrêt du compte
au régime général » (circulaire Cnav n° 2004/8, point 3232), quand le moteur
bornait la ligne de l'année du départ aux trimestres civils écoulés, celle
de l'exploitant comme les autres.

**La règle, lue.** Code rural, L. 731-10-1 (LEGIARTI000019950453, en vigueur
depuis le 19 décembre 2008) : les cotisations des non-salariés agricoles
« sont fixées pour chaque année civile », la situation du chef « appréciée
au premier jour de l'année civile », et « en cas de cessation d'activité au
cours d'une année civile, le chef d'exploitation ou d'entreprise agricole est
tenu au paiement des cotisations [...] au titre de l'année civile entière » ;
au prorata, seulement au décès, et, par R. 731-83 (LEGIARTI000006597265), pour
qui quitte l'agriculture pour une autre activité. Une année dont les
cotisations sont acquittées vaut quatre trimestres de la durée de L. 351-1,
celle qui proratise : R. 732-48 (LEGIARTI000053328383) pour les années d'avant
2016, D. 732-48-1 (LEGIARTI000053352415) pour le collaborateur de 2016 à 2025.
La pratique d'aujourd'hui : l'exposé « Durée d'assurance pour le taux plein »
de la base de la Cnav, qui cite la circulaire n° 2026/22, retient pour le
taux « les 4 trimestres de l'année de cessation d'activité validés par ce
régime [...] même s'il s'agit de l'année d'arrêt du compte » (circulaire
n° 83/83, lettre Cnav du 20 juin 2011) ; la circulaire n° 2004/37 (point 131)
précise que ces règles « ne remettent pas en cause les bornes de la période
de référence » de la surcote. Le ministre de l'agriculture, répondant le
3 février 2026 à la question écrite n° 10883, maintient l'annualité, « y
compris lorsque [la cessation] survient en cours d'année », qui fait valider
« 4 trimestres supplémentaires au titre de leur retraite », et n'envisage
« aucune évolution sur le sujet ». La règle vaut donc encore, pour les deux
durées, celle du régime et celle du taux ; elle date au moins des circulaires
de 1983 et 1989, L. 731-10-1 la portant au code depuis 2008.

**Ce qui est fait.** `Carriere.annee_de_cessation_agricole`
(`anneeDeCessationAgricole` en JavaScript) : l'année de la date d'effet,
quand toutes les lignes cotisées de cette année sont agricoles (exploitant,
collaborateur), et qu'une ligne agricole cotisée l'année d'avant fait de
l'assuré un exploitant au 1er janvier. La ligne agricole de cette année
compte alors quatre trimestres (`trimestres_retenus`), l'année a quatre de
plafond (`_plafonds_trimestres`, `compter.plafond_de_l_annee`), et la durée
du régime comme la durée tous régimes les comptent. Ce qui se compte entre
deux dates n'en lit que les trimestres des mois écoulés, par une méthode
neuve, `trimestres_ecoules` : la répartition des trimestres d'une ligne sur
ses mois (`trimestres_de_la_ligne_entre`) et les trimestres cotisés après
l'âge, que lit la surcote en points du régime agricole de 2026
(`_trimestres_cotises_apres`). Sans elle, un exploitant né en 1975, parti en
février 2039, gagnait quatre trimestres de surcote.
`test_l_exploitant_agricole_compte_les_quatre_trimestres_de_l_annee_ou_il_cesse`
rejoue trois carrières dans les deux moteurs : l'exploitant parti le
1er août 2024 (140 trimestres au régime, 160 tous régimes, et non 138 et
158), le salarié qui part la même année, l'exploitant installé l'année de son
départ. La fiche `taux_plein_et_proratisation` lit L. 731-10-1, R. 731-83,
R. 732-48, l'exposé et la réponse ministérielle, et rattache D. 732-48-1 : le
cliquet des textes descend d'une rédaction, à 9 720 avec une autre session.

**Ce qui bouge.** Onze des 868 témoins de simulation au scénario 1, tous des
exploitants ou des collaborateurs agricoles, tous en hausse : +1,87 % en
médiane, de +0,48 % (`enfants_exploitante_agricole`) à +4,29 %
(`statut_exploitant_agricole_1965`) ; six aux scénarios 3 et 5, rien aux
scénarios 2, 4 et 6 (`resumer_temoins.py`, après `regenerer.py`). Les rendus
de sept pages qui agrègent (avantages, cas types, coût) suivent, refaits par
GitHub.

Quatre tests des minima agricoles (`test_minima_agricoles.py`, zone de la
session de l'action 138) comptaient une année de chef de moins : leurs chefs
partent en février, et l'année du départ y entre désormais (vingt et un ans
au lieu de vingt, treize au lieu de douze). Seuls leurs chiffres attendus ont
changé, pas le code des minima ; et leur chef naît un 15 janvier déclaré,
car sous les présomptions décalées il partait un 1er janvier, sans année de
cessation. L'exemple de la MSA de la réforme de 2026
(`test_la_reforme_agricole_rend_l_exemple_de_la_msa`) décrit un exploitant
« de 1994 à 2026 » : la carrière du test part désormais le 1er janvier 2027,
et non en février, où elle compterait une douzième année depuis 2016.

**Reste, trouvé en chemin.** Les cotisations et les points de l'année de
cessation restent ceux des mois de la ligne : L. 731-10-1 en fait payer
l'année entière, ce qui porterait les points de la retraite proportionnelle
d'avant 2026, ceux de la RCO et le revenu de l'année depuis 2016 (une étape à
part, qui touche aux montants). Une cessation avant l'année du départ, sans
autre activité ensuite, n'est pas comptée pleine non plus : le moteur ne la
regarde que l'année de la date d'effet. L'année d'installation, que la
réponse ministérielle dit exonérée jusqu'à l'année suivante, n'est pas lue au
texte.

**Ce qui attend le propriétaire.** Rien.
