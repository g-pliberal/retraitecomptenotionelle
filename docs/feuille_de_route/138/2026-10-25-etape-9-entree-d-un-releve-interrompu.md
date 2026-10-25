# Étape 9, suite de la huitième partie : l'entrée d'un relevé qu'ouvre une interruption

**La demande.** Dix-neuvième vague, le 25 octobre 2026 : une session par
tâche, que le propriétaire ne suit pas pas à pas, celle-ci seule du lot sur
la carrière. Le point « au modèle, l'entrée d'un relevé qu'ouvre une
interruption » du bloc « Reprise » de la huitième partie, que la note
« dates de pension du formulaire »
(`2026-10-25-etape-9-dates-de-pension-du-formulaire.md`, « Trouvé en
chemin ») laissait au modèle : sur un relevé, la carrière datait l'entrée
dans une affiliation de la première année qui la nomme, année d'interruption
comprise (`Carriere.entree`), et `Saisie.dateEntree` la suivait ; le
formulaire, de la première année d'emploi.

**Ce que disent les textes**, relus le jour même dans l'index du JORF de la
DILA. Le libéral non réglementé relève du régime général et du RCI quand il
crée son activité depuis le 1er janvier 2019 ; ceux « affiliés avant le
1er janvier 2019 » à la CNAVPL et à la Cipav « restent affiliés à ces
caisses » (loi n° 2017-1836, art. 15, 8°, JORFARTI000036339157). Les régimes
fermés en 2023 le sont aux « recrutés » depuis le 1er septembre (loi
n° 2023-270, art. 1er, JORFARTI000047445082 : L. 2142-4-2 du code des
transports pour la RATP, L. 142-9 du code monétaire et financier pour la
Banque de France, la CRPCEN en III, les IEG en V). L'entrée est chaque fois
un recrutement ou une installation, un fait d'activité, qu'une ligne de
relevé ne dit que par une année d'emploi.

**Ce qui est fait.**

- *Les tests* (`tests/test_fiche_date_d_entree.py`, trois tests, cinq cas),
  vus rouges. Le relevé salarié de 2008 à 2017, puis libéral non
  réglementé, sans activité en 2018 et actif depuis 2019, date l'entrée de
  2019, et le compte de 2020 reçoit le régime général et le RCI : la
  carrière la datait de 2018, et portait la CNAVPL et la Cipav ; installé
  en 2018, il les garde. Le portage bâtit la même carrière de la saisie du
  relevé et de ses interruptions, et la saisie la date comme elle. L'agent
  de la RATP au chômage en 2023 sous le statut, au travail depuis 2024, se
  refuse, 2024 à l'appui ; il passait, sous le régime de la RATP. La
  naissance se déclare en 1985, l'année seule : ni le jour ni le sexe n'y
  comptent.
- *La correction* : l'entrée est la première année d'emploi du statut, ou,
  s'il n'en a aucune, sa première ligne (`Carriere._entrees` ; dans
  `carriere.js`, `anneeDEntree`, que `Carriere.entree` et
  `Saisie.dateEntree` partagent). Le parcours n'en change pas : ses métiers
  datent l'entrée (`dates_entree`). Le refus d'un statut fermé
  (`verifierStatutsReleve`) lit la même date, et le dit : « la première
  année déclarée en emploi sous ce statut ». Le formulaire n'a pas bougé.

**Ce que montrent les mesures.** Ni les témoins de simulation (909) ni ceux
des pages (82) ne bougent (`construire_temoins.py --verifier`, le
25 octobre).

**Trouvé en chemin.** La CRPCEN et les IEG ne gardent leur régime qu'à qui
en remplit les conditions d'affiliation « sans aucune interruption » depuis
le 1er septembre 2023 (loi n° 2023-270, art. 1er, III et V). La carrière
date l'entrée du premier recrutement, sur un parcours comme sur un relevé :
le clerc de notaire de 2010 à 2023, salarié du privé en 2024, revenu en
2025, y garde la CRPCEN. Au modèle, avec son test.

**Ce qui reste**, une session par point : le plafond de 2027 ; au modèle,
le retour à la CRPCEN et aux IEG après le 1er septembre 2023 (« Trouvé en
chemin ») ; la limite 5 ante ter (2), en fin d'étape ; au propriétaire, la
CAMIEG, l'écrêtement du minimum de la SNCF, l'ASPA de l'article 23, et les
textes au fac-similé de la note « seuil de février 1991 ».
