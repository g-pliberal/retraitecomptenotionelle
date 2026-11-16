# Note de décision 0009 — la version de fiche, unité du droit

**Ne pas adopter en l'état (16 novembre 2026).** Deux de ses piliers ne
tiennent pas : le droit s'écrit par renvois (« l'âge prévu à l'article
L. 161-17-2 », « augmenté de cinq années », « minoré de deux ans et six
mois »), que la table entière de chaque version et la fin des interrupteurs
couperaient ; et les 870 périodes des 80 régimes calculés portent bien plus
de droit daté que les 2 570 renvois comptés ici, sans plan pour lui. Seule
l'idée des deux axes tient. L'essai sur l'âge du taux plein
(`essai-0009-age-du-taux-plein.md`, même dossier) le confirme, et montre que
les renvois des régimes sont, le plus souvent, le droit de chaque régime.
Trois autres essais, sur l'âge légal, la surcote et la carrière longue
(`essais-0009.md`, même dossier), confirment les deux axes et changent encore
trois règles : une version peut renvoyer à sa propre rédaction antérieure,
elle se choisit à la date que nomme le texte, et un renvoi dit à quelle date
il lit sa cible.

*Brouillon du 15 novembre 2026, revu le 16 après une recherche de
contre-exemples ; à décider. Le propriétaire avait demandé un
diagnostic de l'architecture du dépôt, puis voulu discuter, avant de la
valider, de la règle qui range dans les versions de sa fiche un paramètre que
plusieurs lois réécrivent. Cette note la soumet, élargie à ce qui la fait
tenir : le fichier de régime sans droit daté, et le lien de chaque version à
son code et à sa preuve. Elle précise le contrat C.2, l'annexe B et la
phase 6 du chemin ; elle ne touche à aucun principe.*

## Le problème

Le droit des retraites se lit sur deux axes à la fois : la loi en vigueur à
la date d'effet de la pension, et la génération, ou une autre date, que
cette loi vise. La réforme de 2023 vise les pensions qui prennent effet à
compter du 1er septembre 2023, pour les assurés nés à compter du
1er septembre 1961. Le contrat C.2 porte déjà les deux : la version a ses
bornes, et chacun de ses paramètres sa date qui décide (§ 4.1 et 4.2).

Mais le droit daté s'écrit aujourd'hui à trois endroits, quand le principe 2
n'en veut qu'un :

- **Les périodes des fichiers de régime.** 50 fiches y sont désignées par
  2 570 renvois, les interrupteurs ; chacune déclare la valeur que le moteur
  lit (`code.interrupteurs`). La phase 6 les a gardés comme renvois
  (annexe B), sans échéance, alors que le § 13.4 les dit nés d'un
  contournement du noyau.
- **Les versions des fiches.** Sur les 272 fiches de la carte, le moteur en
  lit 80 par leurs versions, et 69 n'en ont aucune (action 191, au
  9 novembre 2026).
- **Une table par loi.** Les fiches de l'âge légal, de la durée requise et
  de l'âge d'annulation de la décote sont conformes, mais sans versions.
  `age_ouverture_requis.csv` applique les versions successives de
  D. 161-2-1-9 dans l'ordre, « la plus récente l'emportant ». Ce que la
  fusion efface est recopié dans `age_ouverture_avant_reforme_2023.csv` et
  `age_ouverture_avant_suspension.csv`, et de même pour la durée requise. Le
  moteur les lit par une classe par loi, et un droit contrefactuel y pose une
  table sur l'autre (`TableRecouverte`).

Le § 11 nomme ce cas le pire : « une migration arrêtée à mi-chemin, avec
l'ancien registre et la fiche vivant côte à côte ».

La preuve, elle, ne tient pas au code. C.2 demande déjà à chaque version ses
exemples officiels, ou « aucun trouvé », mais rien ne l'exige : 65 fiches sur
267 sont confrontées à un exemple (tableau de bord, au 15 novembre 2026). Le
champ `code` de la fiche nomme ses fonctions en prose, que rien ne vérifie,
et 130 fiches sur 267 seulement sont citées dans le code par leur
identifiant.

## La décision

### Le droit daté ne s'écrit que dans les versions de fiche

Un paramètre que plusieurs lois réécrivent vit dans les versions de sa
fiche : une version par réforme qui le réécrit, et par public qu'elle vise.
Ses bornes sont celles que C.2 connaît déjà : la date d'effet pour les
pensions qui prennent effet, l'échéance pour les pensions servies (`vise`),
et toute autre date qui décide que nomme le texte. L'avenant n° 17 de
l'Agirc-Arrco, du 22 novembre 2023, en donne deux : le coefficient de
solidarité disparaît pour les retraites prenant effet à compter du
1er décembre 2023, et au 1er avril 2024 pour celles qu'il minorait déjà.

Chaque version porte sa table entière, indexée par la date qui décide de sa
valeur : la génération pour l'âge légal, la date où les conditions sont
remplies pour la durée des régimes spéciaux depuis 2008, la date d'ouverture
pour celle des militaires depuis 2023. Chaque ligne cite son texte, car une
réforme se remplit parfois de plusieurs : quatre décrets pour les cinq
générations de 1953 à 1957 ; la loi de 2025 pour les assurés nés à compter
du 1er septembre 1961, et pour les autres le décret qu'elle n'a pas réécrit.
Il n'y a plus de table fusionnée, de copie d'avant réforme, ni de classe par
loi.

Les bornes se lisent dans le texte (« pensions prenant effet à compter
du… »), par une session qui suit `docs/veille_droit.md`, et non dans les
dates de vigueur de LEGI. La suspension de 2025 est en vigueur au
31 décembre 2025, mais ne vise que les pensions prenant effet à compter du
1er septembre 2026.

La ligne de partage avec la table datée (C.3) n'est pas le changement de
règle. La table datée reste pour les valeurs qui ne dépendent que d'une
date, même quand un texte en change la forme : la revalorisation de 2020, à
cinq coefficients selon le montant de la retraite, y tient en cinq lignes.
La version est pour une règle, et pour les valeurs qui dépendent de deux
dates : la loi de la date d'effet, et la génération ou l'autre date que
cette loi vise.

Un scénario qui garde une loi passée devient une couche qui remplace une
version (C.4), sans table posée sur une autre. Quand la loi gardée tient en
une table close, comme l'âge de 2010 ou la durée de 2014, la couche la
reprend telle quelle. Quand elle tenait en un mécanisme, la couche calcule ce
qu'aucun texte n'a publié, et le marque `supposée` : le minimum contributif
d'avant 2023 au-delà de cette date, que la réforme a relevé et revalorise
désormais « sur la base du Smic ».

### Le fichier de régime ne porte plus de droit daté

Il dit qui il couvre et quelles fiches s'y appliquent. La valeur de chaque
interrupteur passe dans une version de la fiche à laquelle il renvoie, et
`code.interrupteurs` disparaît avec le dernier. Cela clôt ce que la phase 6
avait laissé ouvert.

### Chaque version nomme son code, et chaque fonction sa fiche

Le champ `code` cesse d'être du texte libre. Il nomme les fonctions qui
appliquent la fiche, par leur chemin et leur nom sous `moteur/js/` ; une
version qui change de formule nomme la sienne. Chaque fonction nomme sa
fiche dans une étiquette que le test lit. Un test vérifie les deux sens :
aucune fonction de règle sans fiche, aucune fiche exécutable sans fonction,
aucun nom qui n'existe pas.

Les exemples que C.2 demande deviennent exigibles pour chaque version que
l'action 191 reprend : un exemple officiel au moins, ou « aucun trouvé »
avec ce qui a été cherché. Les témoins restent l'alarme des régressions ;
ils ne prouvent pas la loi.

### Quatre cliquets tiennent la décision

Ne peuvent plus que baisser : les renvois par interrupteur ; les copies
d'avant réforme, nommées une à une (`age_ouverture_avant_reforme_2023.csv`,
`age_ouverture_avant_suspension.csv`, `duree_requise_avant_reforme_2023.csv`,
`duree_requise_avant_suspension.csv`), et non par leur suffixe, que portent
aussi des tables d'avant une date qui sont du droit
(`pension_minimum_avant_1983.csv`) ; les versions reprises sans exemple ni
« aucun trouvé » ; les fonctions de règle sans fiche. Ce sont des tests de
la suite, comme les cliquets des textes de la phase 2 ; cette note les fait
entrer (§ 13.4).

## Ce qui ne change pas

Les neuf principes ; le partage des versions et ses deux erreurs (§ 4.1) ;
les quatre sortes de dates qui décident (§ 4.2) ; les droits maintenus,
écrits en bornes (§ 4.3) ; les univers en couches (§ 4.8) ; le JavaScript
qui fait foi et ce qui reste en Python (notes 0003, 0005 et 0006). Aucun
résultat chiffré ne bouge : une migration qui en déplace un s'arrête et le
dit. De même d'un cas que la règle ne sait pas écrire : il revient à une
note.

## Les cas qui l'ont éprouvée

Avant d'être soumise, la règle a été confrontée aux cas les plus difficiles
que le dépôt connaît. Aucun ne la met en défaut ; chacun en a précisé un
terme, écrit plus haut.

- **Le coefficient de solidarité de l'Agirc-Arrco** : deux publics, deux
  versions. Le fichier du régime, qui compte en années, le coupe au
  1er janvier 2024.
- **La durée des régimes spéciaux depuis 2008** : elle tient à la date où
  les conditions sont remplies. La table commune par génération demandait
  167 trimestres à un agent de conduite né en 1960, qui en doit 154 ;
  `duree_requise_calendriers.csv` l'a corrigé depuis.
- **La durée des générations 1953 à 1957** et **la suspension de 2025** :
  une réforme remplie de plusieurs textes ; d'où la ligne qui cite le sien.
- **La revalorisation de 2020** : cinq coefficients, une seule date qui
  décide ; elle reste en table datée.
- **Le minimum contributif dans le droit du 31 août 2023** : la couche
  prolonge une loi qu'aucun texte ne chiffre plus, et le dit. Le site ne le
  fait pas aujourd'hui, et l'écrit : son droit du 31 août 2023 ne change que
  l'âge, la durée et la carrière longue.

Ce n'est pas une preuve : la migration des trois premières fiches est
l'épreuve qui compte.

## Les solutions écartées

- **Un fichier par loi**, la forme de legiretraite, de la DREES, et celle de
  l'âge légal aujourd'hui : un seul axe, la génération. Chaque loi y ajoute
  un fichier et une classe, et chaque scénario qui garde une loi passée, un
  mécanisme à part.
- **La table fusionnée**, la loi la plus récente l'emportant : elle efface la
  loi d'avant, dont ont besoin les pensions liquidées sous elle et les
  scénarios qui la gardent.
- **Une version qui ne porte que ce qu'elle change** : lire une version
  demanderait de recomposer la table, et l'erreur de recouvrement
  reviendrait.
- **Le rangement d'OpenFisca-France-Pension**, par génération puis par date
  d'effet : il a les deux axes, mais une loi nouvelle touche chaque
  génération ; sa table de l'âge légal compte 419 lignes.
- **Une version par rédaction d'article de LEGI** : la vigueur d'un article
  n'est pas la borne d'une version.
- **Les interrupteurs gardés comme renvois**, ce que fait l'annexe B : deux
  sources pour une même information.
- **Tout en tables datées (C.3)** : une table n'a qu'une date qui décide, et
  une loi qui vise des générations parmi les pensions d'une date d'effet en
  demande deux.

## La migration

Rien ne change dans le code avec cette note. Au commit qui l'ajoute, le
document d'architecture change le champ `code` du contrat C.2, l'annexe B
et la ligne 6 du chemin, avec sa version datée sous
`docs/architecture/versions/`.

Elle s'applique dans l'action 191, après la fin de l'action 161 : sinon
l'âge légal se migrerait dans deux moteurs. Une étape par session, sur
Fable 5.2, puisque chacune réécrit une règle du scénario 1. Le mécanisme
existe déjà : la retraite progressive se lit par ses versions
(`fiches_datees`, `version_aux_dates`).

Les cliquets se posent d'abord. Viennent ensuite `age_legal_par_generation`,
`duree_requise_par_generation` et `age_annulation_decote` : leur étape est
finie quand les quatre copies et les classes par loi sont parties,
qu'aucun résultat n'a bougé, et que chaque version porte ses exemples ou
« aucun trouvé ». Les interrupteurs suivent, domaine par domaine, jusqu'au
dernier.
