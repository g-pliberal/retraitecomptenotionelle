# Action 130 : la réversion du FSPOEIE et de la complémentaire des cultes, servie

*Le 21 novembre 2026, une session a écrit la correction ; une autre l'a
relue sous Opus (Fable indisponible ce soir-là ; le propriétaire l'a voulu
ainsi), puis publiée avec la pile du soir.*

**Le défaut.** Le moteur cherche la fiche de réversion d'un régime dans le
champ `regimes:` des fiches `reversion*.yaml`. Un régime qu'aucune ne nomme
reçoit une ligne à 0 euro, motif `non_portee`. Sur les 80 régimes calculés,
51 étaient dans ce cas, dont le FSPOEIE (62 155 retraités de droit direct en
2024) et la complémentaire des cultes.

**Le FSPOEIE.** Fiche neuve, `reversion_fspoeie.yaml`, lue dans l'index
LEGI, en trois versions : avant le 5 janvier 1979, supposée (les rédactions
du décret n° 65-836 de ce temps manquent à l'index), la veuve seule ; de 1979
à 2003, décret n° 65-836, articles 16, 19, 20 et 21 : 50 % à la veuve, au
veuf sous condition d'âge et de plafond ; depuis le 1er janvier 2004,
décret n° 2004-1056, articles 25 à 32 : 50 % aux conjoints, sans âge ni
ressources. Partout, la condition de mariage de l'article 26 (deux ans de
services entre le mariage et la radiation, sauf enfant du mariage, ou quatre
ans de mariage), le partage au prorata des mariages et la perte au remariage
ou au concubinage notoire (article 32). Le moteur la lit par la branche de
la fonction publique, dont le texte est le jumeau.

**La complémentaire des cultes.** `arrco_cultes` rejoint
`reversion_agirc_arrco.yaml` : L. 921-1 du code de la sécurité sociale
affilie les ministres des cultes rémunérés à une institution de l'Arrco,
dont l'accord règle la réversion (60 % des points, 55 ans depuis 2019).

**Exemples** (simulateur de réversion d'info-retraite, 21 novembre 2026) :
un ouvrier de l'État à 1 800 euros par mois laisse 900 euros à sa veuve,
au lieu de 0 ; 100 euros de complémentaire des cultes en laissent 60.
Aucun témoin de simulation ne bouge : aucun n'a de défunt dans ces deux
régimes.

**Ce qui reste.** Quarante-neuf régimes calculés restent sans réversion ;
`docs/limites/4-regimes-incomplets.md` les nomme, et dit le sens de
l'erreur. La fiche du FSPOEIE ne porte ni le minimum de l'article 25, III,
ni la moitié de la majoration pour enfants, ni la pension d'orphelin. Le
journal `2026-11-21-reversion-fspoeie-et-cultes.yaml` dit ce qui suit : la
CAVIMAC, les exploitants agricoles, et un exemple publié par la Caisse des
dépôts pour le FSPOEIE.
