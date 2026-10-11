# Étape 3, la seconde règle : le temps partiel des fonctionnaires

**Le 11 octobre 2026, la demande.** Le propriétaire : « Action 136, étape 3 :
le temps partiel des fonctionnaires est compté à temps plein dans les
services. Porte la quotité dans la saisie et dans les services de la famille
fonction_publique, dans les deux moteurs (fiche
`temps_partiel_fonction_publique`). Suis la liste de contrôle « un champ de
saisie de plus » de `moteur/CLAUDE.md`. » La première règle de l'étape, le
départ anticipé des parents de trois enfants, l'action 138 l'a reprise
(chantier 138.17 au registre des autres modèles).

**Ce qui a été lu.** L'index LEGI, mis à jour le jour même. L. 11, 1°, du
code des pensions fait la règle : la période à temps partiel est « comptée
pour la fraction de sa durée », dans ses rédactions du 2 avril 1982, du
27 juillet 1991 et du 1er septembre 2023 ; la dernière compte à temps plein
cinq temps partiels — de droit pour élever un enfant, de présence parentale,
accordé au titre du 2° de L. 9, de proche aidant, thérapeutique. L. 5 le
compte en entier pour ouvrir le droit ; L. 14, I, en entier dans la durée
d'assurance, depuis 2004 ; L. 11 bis ouvre la surcotisation, quatre trimestres
au plus, huit à l'agent handicapé à 80 % ; L. 9, 1°, et R. 9 comptent le temps
partiel de droit d'un enfant né depuis 2004 jusqu'à ses trois ans. Pour la
CNRACL, l'article 13 du décret n° 2003-1306, et avant lui l'article 10 du
décret n° 65-773 ; l'article 60 de la loi n° 84-53 paie six septièmes du
traitement à 80 %, trente-deux trente-cinquièmes à 90 %. La page « La formule
de calcul » du SRE, relue : son exemple, Pierre P., dix ans à 80 % sur
trente-neuf, retient 148 trimestres. La fiche fondait la règle sur L. 14, I :
c'est L. 11, 1°.

**Ce qui est fait.**

- *La saisie.* Un champ « Temps partiel » dans les options de modélisation, à
  côté des interruptions et sous leur forme : « 2005:2014:80 », des années
  entières et une quotité de 1 à 99 %. Il se refuse mal formé, hors de toute
  carrière, à l'envers, ou quand deux quotités se disputent une année ;
  l'adresse le porte. Les deux saisies le lisent, le vérifient et le réécrivent,
  et refusent par la même phrase. Les revenus saisis sont ceux d'un temps
  plein, et la bulle du champ le dit, comme elle dit de ne pas déclarer les
  temps partiels que la loi compte à temps plein.
- *La chronologie.* La quotité est un attribut de la période d'activité, que
  le contrat C.1 prévoyait : un parcours coupe ses métiers principaux au
  1er janvier des années où elle change (`emploi_1`, `emploi_1_2`…), une ligne
  de relevé la porte. Sans temps partiel, aucune période n'est coupée.
- *La carrière.* La quotité d'une ligne mêle celle du temps partiel et celle
  des mois de retraite progressive (`_quotite_de_l_annee`) ; elle réduit le
  revenu d'un parcours, laisse celui d'un relevé, déjà perçu, et la
  prolongation d'un relevé ramène sa dernière année au temps plein par elle.
  Une année d'interruption n'en a pas ; une activité cumulée garde le temps
  plein.
- *Les services.* Rien à y écrire : ceux de la famille fonction_publique
  lisaient déjà la quotité des lignes, au jour, depuis la retraite
  progressive, et la liquidation le traitement à temps plein (L. 15). Trente-neuf
  ans dont dix à 80 % font 148 trimestres au lieu de 156, la durée d'assurance
  et la durée de services qui ouvre les droits restant entières ; à temps
  partiel jusqu'au départ, le fonctionnaire ne perd que ses services. L'exemple
  du SRE entre aux témoins officiels sur ses services
  (`sre_temps_partiel_pierre`), et non sur sa pension : la page la divise par
  168 trimestres requis, quand sa table et L. 161-17-3 en donnent 167.
- *Les témoins.* Trois simulations : le fonctionnaire de l'exemple ; une
  salariée à mi-temps que sa retraite progressive reprend à son mois ; une
  territoriale dont le relevé est à 70 %, prolongé jusqu'au départ à temps
  plein puis à 90 %. Aucune des 804 autres ne bouge, les retraites progressives
  comprises, au bit près ; onze pages du simulateur gagnent le champ, et rien
  d'autre. Les tests : `tests/test_temps_partiel.py`, dont la lecture des deux
  moteurs, et le formulaire qui renvoie le champ (`test_formulaire.py`).
- *La fiche* passe de `manquante` à `approchee`, ses quatre approximations
  dites ; le cliquet des textes descend de 9 822 à 9 812 rédactions sans
  statut ; le registre des autres modèles dit repris l'avantage d'OpenFisca
  (136.3), et celui des sources, l'exemple de Pierre P. rejoué sur ses services.

**Ce qui ne bouge pas.** Aucun résultat sans temps partiel déclaré : le champ
vide laisse chaque année à temps plein, comme avant.

**Ce qui reste.** La surcotisation (L. 11 bis), un choix borné à quatre
trimestres, qui demande une saisie de plus et le taux de sa retenue ; la
rémunération à six septièmes et trente-deux trente-cinquièmes, que le modèle
ramène à la quotité, comme pour la retraite progressive ; le mi-temps d'avant
1982, que l'index ne porte pas ; le minimum garanti, dont il faut vérifier
qu'il lit les services réduits ; et la confrontation à l'oracle, la fin de
l'étape : OpenFisca réduit lui aussi les services de la quotité, et aucun
profil à temps partiel ne lui a encore été passé.
