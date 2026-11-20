# Action 194, étape A : la carte de justesse, calculée depuis les preuves

Le 20 novembre 2026. Aucun résultat du simulateur n'a bougé : l'étape ajoute
un module qui lit, un bloc au tableau de bord et un cliquet.

## Ce qui est fait

**Le calcul** est dans `src/retraite_notionnelle/noyau/justesse.py`. Une
partie est une règle sur une période : une version de fiche, ou la fiche
entière tant qu'elle n'est pas découpée. La carte en compte 918 ce jour : 849
versions et 69 fiches sans version. Chaque partie reçoit l'un de six états,
dans cet ordre :

1. hors champ, quand la fiche se dit `pas_encore_modelisee` ;
2. fausse, quand un écart y est établi — un exemple officiel en écart connu,
   un cas de preuve en écart connu — ou quand la fiche se dit `manquante` ;
3. approchée, quand la fiche se dit `approchee` et que l'approximation touche
   cette version (toutes, si l'une de ses approximations ne nomme pas ses
   versions) ;
4. prouvée avec témoin, quand le texte est tracé, qu'une grille indépendante
   est verte et qu'un témoin au moins concorde ;
5. prouvée au texte seul, sans témoin ;
6. non vérifiée, sinon : « conforme » et « transcrite » sont des mots que la
   fiche écrit, et ne prouvent rien.

Le texte est tracé au sens du cliquet des lectures sans trace de la note de
décision 0009 : chaque texte cité par la version dit sa date de lecture ou sa
citation. Un test tient les deux règles égales sur toutes les versions. Une
version supposée, ou une fiche sans version, ne peut pas être prouvée.

**Le format d'une preuve** est décrit en tête du module. Un fichier par
preuve, sous `data/reference/preuves/`, qui dit sa sorte (grille
indépendante, exemple officiel, moteur extérieur, simulateur de caisse,
notification de pension), sa source, les parties qu'il couvre et ses cas. Un
cas suit le schéma d'un exemple officiel, et se rejoue par la même
confrontation (`tests/test_oracle.py`, `_confronter`) : ce qui sait rejouer
les 220 exemples sait rejouer une grille. Une grille dit en plus comment elle
s'est passée du code et quels seuils ses cas couvrent. Le dossier n'existe pas
encore : il naîtra avec la première grille.

**Les exemples officiels ne sont pas recopiés.** Ils témoignent déjà pour les
fiches et les versions qui les citent, et le module les lit là. Deux règles,
choisies pour que le doute profite au faux : un exemple d'accord ne témoigne
que pour la version qui le cite ; un exemple en écart que seule la fiche cite
marque toutes ses versions.

**Le cliquet** est `tests/cliquets_de_justesse/prouvees.yaml`. La liste des
parties prouvées ne peut que s'allonger : une partie inscrite qui n'est plus
prouvée fait échouer `test_aucune_partie_prouvee_ne_recule`, que le filet des
fichiers communs joue avant chaque envoi. On répare, ou l'on passe la partie
sous `retirees` avec le jour et une raison de huit mots au moins.

**Le tableau de bord** porte la carte en section 1, famille de régimes par
famille (celles de l'inventaire), et la liste des parties fausses en
section 2.

## Ce que la carte dit ce jour

Aucune partie prouvée sur 918. 14 fausses, 633 approchées, 204 non
vérifiées, 67 hors champ. 240 parties ont un texte tracé, 82 un exemple
officiel d'accord, 158 sont des versions supposées.

Les 14 parties fausses tiennent à dix fiches : la réversion (régime général,
Agirc-Arrco, fonction publique, RAFP), la majoration en capital de la RAFP,
le minimum de pension des industries électriques et gazières, la décote
d'avant 1983, la pension maximale du régime général, le coefficient
d'anticipation de l'Ircantec et la liquidation régime par régime. Aucune ne
porte de numéro d'action : le registre des exemples officiels n'en a pas le
champ, et seule une preuve du nouveau format en nomme un.

## Ce que la carte ne sait pas encore

- **Les erreurs connues hors des exemples officiels.** Une erreur que sa
  fiche déclare en approximation reste « approchée ». Les points de la CIPAV,
  l'ASV des auxiliaires médicaux ou la complémentaire des médecins n'y sont
  donc pas « fausses » : il leur faut une preuve qui porte l'écart et son
  action. C'est le premier usage du format, à faire à l'étape E, ou plus tôt
  si le propriétaire le demande.
- **Les autres moteurs.** 43 fiches racontent en prose une confrontation à
  OpenFisca, Trajectoire ou Destinie. La carte les compte sans les tenir pour
  témoins : rien n'y dit, cas par cas, ce qui concorde. L'étape C leur
  donnera des preuves.
- **TRAJECTOiRE 3.3.2, quantité par quantité.** Sa confrontation, arrivée
  sur `main` le même jour (action 137, `tests/temoins/trajectoire_3/`), dit
  cas par cas ce qui concorde : 541 quantités sur 818, sur 85 carrières. Le
  tableau de bord la montre à côté de la carte. Elle ne change l'état
  d'aucune partie : chaque cas est une carrière entière, que rien ne rattache
  à une règle. C'est un témoin de l'étage des régimes de bout en bout, à
  brancher à l'étape C.
- **43 parties ont un exemple officiel que leur fiche cite sans dire pour
  quelle version.** Il ne témoigne pour aucune, tant qu'il n'est pas rattaché.
- **Les quatre autres étages** de la proposition : les barèmes, les régimes
  de bout en bout, les cas types, les totaux. Le format a un champ `etage`,
  qui ne connaît que `regle`.
- **L'indépendance d'une grille** se déclare et ne se contrôle pas : la
  session qui l'écrit ne doit pas lire le code, et le dépôt ne sait pas
  l'imposer.
- **Le compte des fiches par famille** diffère de celui de la proposition du
  20 novembre, qui regroupait les régimes à la main : la carte suit les huit
  familles de l'inventaire, où les salariés agricoles sont avec les
  exploitants.

## Par quoi continuer

L'étape B, dans une session neuve : le balayage de cohérence et la
neutralisation. Elle ne prouve aucune partie ; elle dit où regarder d'abord.
Puis le point d'arrêt que le propriétaire a demandé.
