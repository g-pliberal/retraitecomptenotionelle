# Étape 8, cinquième partie : les montants de la MSA, l'Info presse de 2023 et les plans de revalorisation de 1997 à 2002

**Le 14 octobre 2026, la demande.** « Les montants de la MSA de 2015 à 2017 et
de 2019, le communiqué de la MSA du 14 février 2023, puis les plans de
revalorisation de 1994 à 2002, lus à leur source et certifiés » (tâche 6 des
dix-neuf sessions du jour).

**Ce qui est fait.**

- *L'Info presse du 14 février 2023*, retrouvée sur msa.fr : « soit un montant
  de 1 138,63€ net par mois ». Elle entre dans `PUBLIES` du récupérateur
  `msa_smic_net_agricole.py`, que `--verifier` relit ; 2023 passe de `haute` à
  `certifiee` dans `complement_differentiel_rco.csv` (commit 9455778).
- *Les plans de revalorisation*, lus dans l'index JORF : décrets n° 97-163,
  99-141, 2000-261, 2001-170, 2002-297 et 2002-298 ; dans l'index LEGI,
  L. 732-54-1 à L. 732-54-4 de 2001, D. 732-110 à D. 732-120 et D. 732-141 à
  D. 732-147 de 2005 à 2009. La fiche `majoration_retraite_proportionnelle`
  en tient six versions, de la date d'effet : rien avant 1997 ; 26,933 points
  par année de chef, servis au tiers en 1997, aux deux tiers en 1998, entiers
  en 1999 et 2000, minorés sous vingt-deux ans et demi de chef (15, 15, 20,
  20, 20 %, puis 15, 15, 10, 10, 10 % en 2000) ; 29,23 en 2001 ; de 2002 à
  2008, A = (MV1 - AVTS) / (37,5 × VP), et C = (MV2 - AVTS) / (37,5 × VP)
  pour le chef de moins de dix-sept ans et demi qui en a dix-sept et demi
  d'activité agricole.
- *Le modèle*, dans les deux moteurs (`majoration_retraite_proportionnelle`,
  `majorationRetraiteProportionnelle`), lu dans `completer` avant la PMR : au
  taux plein, avec dix-sept ans et demi de chef, P = (A - n) × DCE. L'AVTS de
  la formule est la retraite forfaitaire d'une carrière complète du modèle,
  que D. 732-144 lui égale : une carrière complète de chef partie en 2002
  touche exactement le minimum vieillesse, 6 832,58 €, au lieu de 4 484,84 €.
  La période 1990-2002 de `msa_non_salaries` déclare désormais les minima des
  exploitants, que la version de chaque fiche ouvre ou non.
- *Les tests* (`test_minima_agricoles.py`, cinq de plus et quatre cas
  comparés entre les deux moteurs) : la carrière complète de 2002 au minimum
  vieillesse ; le tiers, les deux tiers et 29,23 ; la minoration à vingt ans
  de chef ; rien avant 1997 ni sans le taux plein ; le minimum du couple.

**Ce que la vérification a trouvé.**

- *Aucun montant de la MSA pour 2015 à 2017 ni pour 2019.* Les réponses
  ministérielles ne donnent que les pourcentages (73, 74, 75 %) ; le tableau
  de bord des retraites des non-salariés agricoles n'écrit pas le montant ; la
  page de la MSA d'Auvergne, qui portait 2025, ne porte plus que 2026 ;
  l'archive du web refuse la connexion de la session. Ces années restent
  `moyenne`.
- *Le Sénat répond 500* au rapport n° 315, que `--verifier` relit pour 2018 :
  la page, non le montant ; le reste de la vérification passe.
- *D. 732-144 écrivait « 35,5 »* dans sa codification de 2005 ; la rédaction
  du 12 octobre 2006 revient aux 37,5 du décret n° 2002-298. Le moteur garde
  37,5.
- *La moyenne n* : le décret ne dit pas sur quelles années d'une carrière de
  plus de trente-sept ans et demi elle se prend ; le moteur divise par la
  durée agricole plafonnée, ce qui donne à une carrière complète le minimum
  exactement.

**Ce qui reste**, de cette partie :

1. Un montant de la MSA pour 2015 à 2017 et 2019 (Chiffres utiles, archive du
   web depuis un poste qui l'atteint).
2. Des plans, ce que la liquidation ne sert pas : les pensions d'avant 1997
   révisées dès 1997 (article 2 du décret n° 97-163, vingt points puis 23,9,
   26,96, 26,23) ; le service au tiers puis aux deux tiers, les relèvements de
   2001 et 2002 et le A qui suit chaque année le minimum vieillesse, pour les
   pensions déjà liquidées ; avec l'étape des pensions déjà liquidées.
3. Les points des conjoints et des aides familiaux (plan de 1994, D. 732-110,
   D. 732-118 à D. 732-131, D. 732-145), que le statut du modèle, qui ne
   distingue pas l'aide familial du conjoint collaborateur, ne permet pas ; la
   majoration de la retraite forfaitaire de L. 732-54-3.
4. L'affichage : le code `majoration_retraite_proportionnelle` est un avantage
   de plus, que les pages ne nomment pas encore (session du site).
