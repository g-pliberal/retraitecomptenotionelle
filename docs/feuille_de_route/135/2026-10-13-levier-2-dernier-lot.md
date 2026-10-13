# Le levier 2, étape 4 : le dernier lot, treize tests qui déclarent leur date

**Le 13 octobre 2026, la demande** : le dernier lot du levier 2, les treize
tests rapides qui dépendaient encore des présomptions, un dans chacun de
treize fichiers, `test_cultes.py` en dernier, que l'action 119 touche en
parallèle. Aucun montant ni aucune date attendus n'ont changé, et rien de ce
lot ne s'écrit dans les pages.

- *Onze tiennent au jour de naissance*, que le test racontait sans le
  déclarer. Présumé le 15, il fait partir l'assuré le mois qui suit son
  anniversaire ; le 1er, le mois même (l'autre branche de R. 351-37), et
  chaque date racontée recule d'un mois : les départs de février 2039 de la
  réversion et du relevé prolongé, de juillet 2029 de l'expatrié, de juillet
  2027 de l'invalide, de février 2026 du mineur, ceux de la fonctionnaire
  partie en 2012 ; et, avec eux, le traitement que liquide la pension unique
  de l'État et de la CNRACL, la coupure du chômeur, les trimestres de surcote
  de l'actif né en 1969 et du fonctionnaire né en 1948. Le 15 se déclare dans
  l'outil qui construit la carrière : `_carriere` de
  `test_interpenetration.py`, de `test_invalidite.py` et de `test_cultes.py`,
  `_mines`, `_pensions` de `test_versements_uniques.py`, la carrière du
  chômeur de `test_chomage_complementaires.py`, le parcours de
  `test_etranger.py` ; à l'appel, quand l'outil prend déjà le jour
  (`_calculer` de `test_cnracl.py` et de `test_fonction_publique_etat.py`) ;
  dans la saisie, `1975-01-15`, pour `test_reversion.py` et
  `test_releve_prolonge.py`. Les commentaires qui disaient « le 15, faute de
  jour dit » ou « jour présumé » disent le jour déclaré.
- *Le ministre du culte de `test_cultes.py`* naissait, à son docstring, « le
  1er décembre 1949 » : né un 1er, il partirait à soixante ans le 1er
  décembre 2009, et non le 1er janvier 2010 que le test raconte, et que seule
  la présomption du 15 lui donnait. Il naît le 15. L'action 119 n'avait rien
  poussé dans le fichier ce jour-là.
- *Les enfants de `test_services_fonction_publique.py`.* La limite de trois
  ans par enfant du 1° de L. 9 s'y vérifie sur des enfants que la présomption
  faisait naître aux trente ans de leur mère, en 2005 ; à vingt-sept ans, en
  2002, la bonification change, et la fonctionnaire compte 164 trimestres au
  lieu de 161. `_pension` déclare leur naissance en 2005, depuis le 1er
  janvier 2004 que le 1° de L. 9 exige. Le modèle n'applique pas cette
  condition, et la fiche `services_et_duree_fonction_publique` le dit, faute
  de connaître l'année des enfants ; la raison ne tient plus — la saisie la
  déclare (`naissances`), la présomption la pose sinon —, et l'approximation
  revient au modèle. Le congé de 2000 à 2004 y précède les naissances : le
  modèle ne rapproche pas le congé de l'enfant pour qui il est pris.
- *`test_droit.py`, un test du mécanisme.* Il vérifie que la ligne du relevé
  qui porte la majoration d'un enfant dit sa présomption,
  `naissance_des_enfants` ; il lit donc la date au vocabulaire, comme
  `test_chronologie.py`, au lieu d'écrire le 15 janvier 2000.

**Mesuré** : sous les présomptions décalées, aucun test rapide n'échoue plus ;
2 165 passent, 19 sont sautés, 17 confrontations au portage et 2 tests qui
demandent l'index LEGI, absent du conteneur. Sous celles du vocabulaire, les
2 182 passent, les deux mêmes sautés. Les treize fichiers entiers passent
sous les deux.
