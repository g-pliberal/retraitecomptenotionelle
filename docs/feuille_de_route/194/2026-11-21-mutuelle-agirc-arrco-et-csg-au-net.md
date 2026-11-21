# Action 194 : le salaire net retire la mutuelle, l'Agirc-Arrco au centième, la CSG de son année

*Le 21 novembre 2026, deux corrections de la fiche de paie écrites par une
session, réunies en un patch après la relecture, relu sous Opus (Fable
indisponible ce soir-là ; le propriétaire l'a voulu ainsi), puis publié.*

## Ce qui change

- **La complémentaire santé obligatoire** (décision du propriétaire du
  21 novembre : un forfait par défaut, la mutuelle du lecteur s'il la dit).
  La fiche de paie du salarié du privé porte 20 euros par mois pour lui et
  autant pour l'employeur en 2026, comme le simulateur de l'Urssaf, en part
  du plafond de la sécurité sociale. Pas avant 2016 : L. 911-7, I, est en
  vigueur depuis le 1er janvier 2016 (LEGIARTI000031686110). La part de
  l'employeur entre dans l'assiette de la CSG et de la CRDS, sans
  abattement (L. 136-1-1). La prévoyance des cadres (1,50 % de la tranche 1,
  accord du 17 novembre 2017) est ajoutée : elle ne change pas le brut, mais
  sa CSG sort du net. Un champ facultatif du simulateur, « Votre part de
  mutuelle d'entreprise », la remplace par celle du lecteur.
- **La part salariale de l'Agirc-Arrco** est celle que le régime et
  l'Urssaf publient, au centième de point : 3,15 % et 8,64 % au lieu de
  40 % exacts (3,148 % et 8,636 %), dans `agirc_arrco.yaml`,
  `arrco_cultes.yaml` et la version de 2019 de
  `cultes_retraite_complementaire.yaml`.
- **La CSG sur les parts patronales de santé et de prévoyance** prend le
  taux de son année (`prelevements_historiques.yaml`) : rien avant février
  1991, 2,4 % en 1995, 8,0 % de 2012 à 2017, 9,7 % depuis 2018. Le portage
  prenait 9,7 % pour toutes les années.

Exemples : au SMIC, le net passe de 1 443 à 1 421 euros par mois. Un salarié
né en 1975 qui saisit 2 500 euros nets remonte à un brut plus haut, 3 186
euros au lieu de 3 158 : sa pension du scénario 1 passe de 2 949 à 2 975
euros par mois (+0,9 %). Seize cas du simulateur de l'Urssaf
(`tests/temoins/brut_net_mon_entreprise.json`) tombent au centime, net, CSG
et ligne de l'Agirc-Arrco comprises. Deux témoins de simulation sur 937
bougent au scénario 1, les deux saisis en net. La version du paquet passe à
48.

TRAJECTOiRE et l'OCDE ne retirent pas la mutuelle de leur net : leurs
comparaisons se font avec une mutuelle nulle, à définition égale, et la
bulle « Comment ces chiffres sont comptés » du simulateur le dit.

## Ce qui reste

D'autres fiches de régime portent une part salariale qui ne tombe pas au
centième de point publié : leur liste est dans le journal
`2026-11-21-agirc-arrco-part-salariale.yaml`, chacune à relire contre son
barème publié avant d'y toucher : pour certaines, la fraction peut être
celle du texte.
