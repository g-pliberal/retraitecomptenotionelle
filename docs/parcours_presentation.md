# Présenter le site en vingt minutes

Ce document est écrit pour quelqu'un qui présente le site sans l'avoir vu.
Il dit dans quel ordre ouvrir les pages, ce qu'il y a à montrer sur chacune,
ce qu'il faut dire, et ce qu'on va vous demander.

**Ses chiffres sont ceux que le site affiche**, et `tests/test_parcours.py`
l'exige : il rejoue les adresses données plus bas, rend chaque page, et
compare tout montant et tout pourcentage écrits ici à ce que le lecteur verra.
Le document a d'abord porté les chiffres d'une matinée, figés dans un fichier
que rien ne relisait ; le modèle a bougé quatre fois dans la journée, et le
parcours annonçait une baisse de salaire là où l'écran montrait une hausse de
trois cents euros. Un chiffre qui dérive fait donc échouer la suite, et
nomme sa ligne.

## Avant de partir

- **L'adresse à ouvrir, et la seule :**
  <https://g-pliberal.github.io/retraitecomptenotionelle/>. Ne pas présenter
  depuis `partiliberalfrancais.fr/retraite/` : cette copie a un jour et demi
  de retard, et il lui manque le pilier capitalisé.
- **Il faut le réseau.** Le site pèse moins d'un mégaoctet et se charge en
  une seconde, mais une copie ouverte depuis le disque ne fonctionne pas : le
  navigateur refuse de charger les données en local. Prévoir un partage de
  connexion depuis un téléphone si la salle n'a pas de wifi.
- **Régler le zoom du navigateur à 125 % ou 150 %** avant de projeter, et
  tester les trois adresses de la section « Trois carrières prêtes à cliquer »
  une fois, chez soi, pour les avoir dans l'historique.
- **Tout se calcule dans le navigateur.** Rien n'est envoyé, rien n'est
  conservé : on peut le dire en salle, et taper une vraie carrière sans gêne.
- **Le site n'a aucune valeur officielle**, et il le dit en bas de chaque
  page. Si quelqu'un veut ses droits réels, c'est info-retraite.fr.

## Le même parcours en diaporama, hors ligne

`docs/presentation_20_septembre_2026.pptx` reprend ce parcours en dix-huit
diapositives, avec les captures des pages du site prises le 20 septembre au
matin et, sous chaque diapositive, les notes du présentateur : ce qu'il faut
dire, et la réponse aux questions attendues. Il ne dépend d'aucun réseau.
Ouvrir en mode présentateur pour lire les notes.

**Ses chiffres, eux, sont ceux de cette matinée-là**, et aucun test ne les
relit : un fichier binaire ne se compare pas à une page. Il porte sa date
dans son nom pour cette raison. Avant de le projeter, ouvrir le site à côté
et vérifier les quatre montants de la page Simuler ; s'ils ont bougé, c'est
ce document-ci qui fait foi, puisque son test le tient.

## L'idée en une phrase

Un compte à votre nom, en euros. Chaque cotisation y est inscrite, le compte
est revalorisé chaque année au rythme des salaires du pays, et au départ la
pension est le solde divisé par le nombre d'années qu'il vous reste à vivre
en moyenne. Pas de trimestres, pas de barèmes, pas de surprise. Rien n'est
placé : les cotisations de l'année paient les pensions de l'année, c'est
toujours la répartition. C'est le système de la Suède, de l'Italie, de la
Pologne et de la Lettonie.

## Le parcours, page par page

La barre du haut porte dix onglets, groupés en quatre : **le programme**
(Programme), **la preuve** (Simuler, Trajectoire, Cas types, Coût, Risque,
Avantages), **la confiance** (Méthode, Données), **faire connaître**
(Partager). Le parcours ci-dessous en montre six, dans l'ordre, et laisse
les quatre autres pour les questions.

### 1. Programme — trois minutes

C'est l'accueil. Descendre lentement, sans rien cliquer.

- Le titre, puis les **quatre grands chiffres** : 1 050 € par mois au
  minimum pour une personne seule (1 600 € pour un couple) ; 18 % + 5 % de
  cotisation au lieu de 28 % ; 1 compte en euros ; 100 % de ce qui est cotisé
  revient.
- **« Comment ça marche, en trois gestes »** : on inscrit, on revalorise, on
  divise. C'est la phrase de la section précédente, et c'est tout le modèle.
- Le tableau **« Le plancher regarde chacun, pas le couple »** : à 300 € et
  1 500 € de pension dans un couple, l'ASPA ne sert rien, la garantie sert
  500 € au premier. C'est l'exemple le plus parlant de la page.
- Le tableau **« Ce que cela change »** : sept lignes, aujourd'hui contre le
  programme. Deux à lire à voix haute : « Changer de métier : changer de
  régime, et de règle de calcul → rien, le compte est le même » et « Tenir
  l'équilibre : une réforme tous les huit ans en moyenne → un chiffre publié
  chaque année ».
- Le bloc « Et vous, ça donne combien ? » en haut de page est un raccourci
  vers le simulateur : on peut y saisir une date de naissance et un statut et
  cliquer « Calculer », ça ouvre la page Simuler déjà remplie. Le parcours
  passe plutôt par l'onglet, pour montrer la page entière.

### 2. Simuler — six minutes, c'est le cœur

Onglet **Simuler**. L'exemple est déjà rempli : né en janvier 1975, premier
emploi en janvier 1996 comme salarié du privé non cadre, 3 500 € net par
mois, départ en janvier 2039 à 64 ans. **Cliquer « Calculer les quatre
systèmes »** sans rien changer.

Quatre lignes apparaissent, une par système. Chaque ligne a deux chiffres :
à gauche le salaire net pendant qu'on cotise, à droite la pension nette,
tout en euros d'aujourd'hui, par mois. Ce que l'exemple donnait le
20 septembre :

| Système | Pension nette par mois | Écart au système actuel |
|---|---|---|
| 1. Système de répartition actuel | 2 807 € | référence |
| 2. Ce que vous avez cotisé, part salariale seule | 775 € | -72,4 % |
| 3. Ce que vous avez cotisé, part salariale + patronale | 1 926 € | -31,4 % |
| 4. La proposition du Parti libéral français | 1 967 € | -29,9 % |

Comment les lire, et c'est la chose la plus importante de la présentation :

- **Le système 1 est la référence** : le droit en vigueur, minima et
  majorations compris, recalculé règle par règle sur cette carrière. Sa ligne
  porte un troisième chiffre, plus récent que le reste de ce parcours, et il
  vaut d'être lu à voix haute : **financé, 2 556 €**, soit 91 % de ce qu'il
  promet. Le reste attend des cotisations que personne n'a versées. La barre
  sous la ligne le montre, et la page Risque le chiffre.
- **Les systèmes 2 et 3 ne sont pas des propositions.** Ce sont des
  contrefactuels : la même carrière recalculée depuis 1941 comme si le compte
  avait toujours existé, avec la seule part salariale (2), puis les deux parts
  (3). L'écart entre 2 et 3 mesure exactement une chose : ce que verse
  l'employeur. Ne pas s'attarder sur le 2.
- **Le système 4 est la proposition**, et il se lit contre le 3 : même
  compte jusqu'à 2026, puis 18 % pour tous, 5 % capitalisés par-dessus, 5 %
  rendus que l'exemple suppose replacés au même endroit, et une garantie
  vieillesse payée par l'impôt. Son grand nombre est annoncé « retraite
  jusqu'à » : c'est le seul des quatre qui dépende d'une décision de
  l'assuré. La ligne sous lui écrit le plancher — répartition plus rente
  capitalisée obligatoire, touché sans rien ajouter — puis ce que les cinq
  points rendus ajoutent si on les place, sur un pilier sans risque.
- **Pourquoi la proposition sert moins que le système actuel sur cet
  exemple :** parce que le système actuel sert à ce salarié plus que ce qu'il
  a cotisé — c'est ce que la page Avantages chiffre. Ces pensions sont
  calculées avant le réglage annuel du système, que la page Cas types
  explique, et ce réglage ne joue pas en faveur de la proposition : voir plus
  bas, la question viendra.

Puis, sous les quatre lignes, le bloc **« Et pendant que vous cotisez »** :
une réforme change aussi la fiche de paie. Sur l'exemple, le salaire net
mensuel passe de 3 840 € à 4 137 €, soit **+297 € par mois** à coût du
travail inchangé pour l'employeur, et +48 916 € sur les treize années qui
restent avant le départ. C'est le net plein : la proposition prélève 23 %
pour la retraite et rien d'autre, quand le droit en vigueur en prélève 28.
Celui qui verse en plus les 5 % volontaires retrouve l'effort d'aujourd'hui,
et c'est l'hypothèse que la ligne 4 retient. C'est un argument que personne
n'attend d'un simulateur de retraite : le montrer.

Tout ce qui suit sur la page est replié sous « Pour aller plus loin » : le
détail du calcul, d'où vient l'écart, qui verse la cotisation, le pilier
capitalisé. Ne rien ouvrir sauf si on le demande. En bas de page, le
résultat complet est consultable en JSON.

**L'adresse de la page contient toute la saisie.** Après un calcul, on peut
la copier et l'envoyer : celui qui l'ouvre retrouve la même simulation.
C'est ainsi que sont faites les trois adresses ci-dessous.

### Trois carrières prêtes à cliquer

Chaque adresse ouvre le simulateur avec la carrière déjà calculée. Toutes
sont nées en janvier 1975 et partent en janvier 2039 à 64 ans, sauf la
dernière. Les montants sont nets, par mois, en euros de 2026.

**Au SMIC toute sa vie**, salarié du privé non cadre depuis 1996 à 1 443 €
net :
<https://g-pliberal.github.io/retraitecomptenotionelle/#/simuler?naissance=1975-01-01&debut=1996-01-01&statut=salarie_prive_non_cadre&salaire=1443&unite_revenu=euros_mois&montants=net&liquidation=2039-01-01>

| Système | Pension nette par mois | Écart |
|---|---|---|
| 1. Actuel | 1 243 € | référence |
| 3. Ce qui a été cotisé, deux parts | 970 € | -22,0 % |
| 4. La proposition | 992 € | -20,3 % |

À montrer avec le plancher en tête : la garantie vieillesse, 1 050 € pour
une personne seule dès 65 ans, passe au-dessus de cette pension. Elle n'est
pas dans la ligne parce que cette carrière part à 64 ans, un an avant l'âge
de la garantie ; le dépliant « Le système 4 : un taux pour tous, et une
garantie payée par l'impôt », sous les résultats, en donne la règle.

**Fonctionnaire titulaire de l'État**, entré en septembre 1998, 3 000 € net :
<https://g-pliberal.github.io/retraitecomptenotionelle/#/simuler?naissance=1975-01-01&debut=1998-09-01&statut=fonctionnaire_etat&salaire=3000&unite_revenu=euros_mois&montants=net&liquidation=2039-01-01>

| Système | Pension nette par mois | Écart |
|---|---|---|
| 1. Actuel | 2 755 € | référence |
| 3. Ce qui a été cotisé, deux parts | 3 344 € | +21,4 % |
| 4. La proposition | 3 382 € | +22,8 % |

C'est le cas qui surprend, et il faut savoir le dire : l'État employeur
cotise pour ses fonctionnaires bien au-delà de ce qu'un employeur privé verse
(jusqu'à 82 % du traitement en 2026). Porté au compte, ce que l'État a
réellement versé donne une pension supérieure à celle que le régime sert.
Le compte rend ce qui a été cotisé, dans les deux sens.

**Née en 2000, salariée du privé au salaire moyen**, 2 751 € net, entrée en
septembre 2022, départ en janvier 2064 à 64 ans :
<https://g-pliberal.github.io/retraitecomptenotionelle/#/simuler?naissance=2000-01-01&debut=2022-09-01&statut=salarie_prive_non_cadre&salaire=2751&unite_revenu=euros_mois&montants=net&liquidation=2064-01-01>

| Système | Pension nette par mois | Écart |
|---|---|---|
| 1. Actuel | 2 462 € | référence |
| 3. Ce qui a été cotisé, deux parts | 1 593 € | -35,3 % |
| 4. La proposition | 1 838 € | -25,3 % |

C'est la carrière qui cotise presque entièrement après la bascule : la
rente capitalisée y pèse le plus, et l'écart entre 3 et 4 est le plus large
des trois exemples. Rappeler que le système 1 de cette génération est celui
que le Conseil d'orientation des retraites projette en déficit de 16 % de la
facture en 2070 : la colonne de référence n'est pas un point fixe.

Si quelqu'un veut sa propre carrière : les trois champs du haut, le statut
dans la liste (soixante-deux, du salarié du privé au député), le revenu net
mensuel. « Ajouter une période » permet un deuxième métier ou une
interruption ; « Coller un relevé de carrière » accepte un relevé
année par année. Ne pas ouvrir « Options de modélisation » en salle.

### 3. Cas types — trois minutes

Onglet **Cas types**. Une grille : treize carrières en lignes, sept
générations en colonnes, de 1940 à 2000. Chaque case dit ce que la pension
deviendrait, par rapport à aujourd'hui, pour la même carrière. Rouge :
moins. Vert : plus.

Trois choses à montrer :

- Les deux cartes en tête : la carrière la mieux traitée (chef d'exploitation
  agricole, +5 % pour la génération 2000) et la moins bien traitée (militaire
  non officier, -45 %), et les 50 points qui les séparent à carrière et à
  durée identiques.
- La ligne **« Fonctionnaire sédentaire (catégorie B) »**, qui va de -57 %
  pour la génération 1940 à +35 % pour la génération 1970 : la même règle
  donne des résultats opposés selon ce que l'État a réellement cotisé à
  chaque époque.
- Le sélecteur « Système affiché » : la grille se réécrit pour le système 2
  ou le 3, ce qui montre ce que chaque ingrédient déplace.

**La question qui vient à coup sûr : « tout est rouge, donc les pensions
baissent ? »** La page y répond dans son deuxième paragraphe, à lire tel
quel : ces pourcentages ne sont pas des baisses de pension. Chaque case
compare deux carrières calculées sous la même règle, et la grille mesure
l'écart entre ses lignes : ce qu'un militaire touche de plus ou de moins
qu'un artisan, à cotisation égale. Le niveau général dépend d'un réglage
annuel, le coefficient d'équilibre, que le modèle calcule mais n'applique
jamais. **Ne pas promettre de marge** : pour la proposition, ce coefficient
est inférieur à un sur toute la projection (0,90 en 2026, 0,79 au plus bas en
2049, 0,92 en 2070), et la page le dit dans la phrase qui suit. C'est le coût
de transition du taux unique : pendant trente ans, la caisse paie les
pensions de l'ancien système avec dix points de cotisation en moins. Ce qu'on
peut dire, et qui est vrai : le système actuel est à 0,84 en 2070 et ne se
règle jamais, la proposition se règle chaque année et son manque se résorbe
à mesure que les pensions de l'ancien système s'éteignent. La page Coût le
chiffre. Jusqu'au 20 septembre au matin, la page affirmait l'inverse, en
texte fixe ; la phrase est désormais calculée.

### 4. Coût — trois minutes

Onglet **Coût**. Trois chiffres en tête, à lire dans l'ordre :

| | |
|---|---|
| Versé aux retraités en 2025 | 422 Md € à 17,3 millions de personnes |
| Encaissé pour le payer | 417 Md € de cotisations et d'impôts |
| Manquant | 5,1 Md €, soit 1,2 % de la facture |

Puis le paragraphe « En clair » : sans rien changer, il manquerait 16 % de la
facture en 2070. Un système en comptes notionnels ne dépenserait pas moins,
il servirait le même argent réparti autrement, et se réglerait chaque année
au lieu d'attendre une réforme.

Deux graphiques, qui se lisent au survol :

- **« La retraite coûte-t-elle plus qu'elle ne rapporte ? »** : ce qui sort
  et ce qui rentre depuis 1959, en part du PIB, et à partir de 2026 ce que la
  proposition coûterait et encaisserait. Sources : DREES puis Conseil
  d'orientation des retraites, et c'est lui qui projette.
- **« Qui paie ? »** : les salaires pour 77 %, et l'impôt, dont la part a
  doublé en vingt ans, de 7 % en 2004 à 15 % en 2025.

Chaque graphique a un bouton « Partager » qui le télécharge en image. Le
reste de la page est replié : le détail des dépenses depuis 1959, le
coefficient d'équilibre, la dette, ce que coûte la garantie vieillesse,
les réserves à lire avant de citer ces chiffres. Ouvrir « Ce que coûte la
garantie vieillesse » seulement si on demande combien coûte le plancher.

### 4 bis. Risque — deux minutes, si on a le temps

Onglet **Risque**. La page est arrivée après ce parcours, et elle change
l'ordre des arguments : elle ne compare pas deux systèmes, elle dit ce que le
système actuel prend et ce qu'il ne rendra pas. Trois chiffres en tête, dans
cet ordre :

| | |
|---|---|
| Prélevé chaque mois sur un salaire moyen | 940 €, cotisation salariale et patronale réunies |
| Promis au-delà de ce que ces cotisations financent | 34 % de la pension |
| Non financé en 2070, sans rien changer | 16 % |

Le 940 € est le chiffre qui porte : c'est le premier poste de la fiche de
paie, avant l'impôt sur le revenu et avant la maladie, et plus de quatre cent
mille euros sur une carrière au salaire moyen. Le tableau qui suit le décline
du SMIC au double du salaire moyen.

Le reste de la page est replié, et deux dépliants valent d'être nommés si la
question vient : « La promesse a déjà été rompue », qui aligne 1993, 2003,
2010, 2014 et 2023, et « Il n'y a pas de problème », qui répond une par une
aux huit objections du discours rassuriste. La page cite ses sources en bas.

Si le temps manque, garder cette page pour les questions : elle répond seule
à « pourquoi changer ? ».

### 5. Avantages — deux minutes

Onglet **Avantages**. La page qui explique les écarts du simulateur : ce que
le système actuel verse sans que personne l'ait cotisé. Trois chiffres :
39 dispositifs en vigueur, du minimum vieillesse à la bonification du
cinquième ; 96,2 Md € en 2024 pour les 18 que le modèle sait chiffrer, dont
38,3 Md € de réversion, qui est lue et non calculée ; 12,9 Md € de pensions
servies avant l'âge légal. La page dit que ces deux montants sont des
planchers. Le graphique du haut compte les dispositifs année par année depuis
1831, où il n'y en avait qu'un.

Deux comptes se croisent sur cette page, et il vaut mieux le savoir avant
qu'on le demande : **39 dispositifs sont en vigueur aujourd'hui**, et le
tableau du bas en recense **45 dispositifs** depuis 1831, ceux d'hier
compris. Les 18 que le modèle chiffre se comptent sur les 45.

### 6. Méthode et Données — deux minutes, pour finir

Onglet **Méthode** : les trois opérations, en une phrase chacune, puis
« Qu'est-ce qui décide du résultat ? ». On peut s'arrêter au titre.

Onglet **Données**, et c'est la bonne page pour conclure : « Rien ici n'est à
croire sur parole. » 42 177 valeurs recontrôlées automatiquement contre le
fichier de l'institution qui les produit, sur 107 séries ; 89 régimes
recensés dont 72 calculés ; 36 institutions citées. Ce compte mesure la
fidélité de la recopie, non la justesse des pensions : si on vous le demande,
la réponse est que les pensions se contrôlent ailleurs, sur les exemples
publiés par les caisses, et que `docs/limites.md` dit lesquels. Le code et
les données sont publics sur GitHub, sous licence libre. La phrase de fin :
vérifiez plutôt que de nous croire.

### Les pages qu'on garde pour les questions

- **Trajectoire** : la même carrière suivie année après année, en cumul, ce
  qu'on aura réellement touché à 75, 86 et 95 ans. Utile si quelqu'un objecte
  que partir plus tôt « rapporte plus ».
- **Partager** : quatre cartes prêtes à publier, au format des réseaux, avec
  leur message rédigé.
- Les sections « Pour aller plus loin » de chaque page, toutes repliées.

## Les questions à attendre, et où est la réponse

- **« C'est de la capitalisation ? »** Non. Rien n'est placé, les cotisations
  de l'année paient les pensions de l'année. Seuls les 5 % du pilier
  capitalisé, en plus des 18 %, constituent un capital, sur des titres sans
  risque, transmissible. Programme, dépliant « La part capitalisée ».
- **« Les pensions baissent de 30 % ? »** Voir la section Cas types plus
  haut : les écarts mesurent la redistribution entre carrières, avant le
  réglage annuel. Ne pas laisser entendre que ce réglage relèverait les
  cases : pour la proposition, il les abaisserait, de 8 % en 2070 et
  davantage avant. Le système actuel, lui, est projeté en déficit de 16 % de
  la facture en 2070, sans règle qui le règle.
- **« Et les petites pensions ? »** Le plancher : 800 € par personne plus
  250 € pour qui vit seul, dès 65 ans, individualisé, payé par l'impôt.
  Programme, tableau du plancher, et Coût, dépliant « Ce que coûte la
  garantie vieillesse ».
- **« Pourquoi le fonctionnaire gagne ? »** Parce que l'État cotise pour lui
  bien plus qu'un employeur privé, et que le compte rend ce qui a été versé.
  Simuler, deuxième adresse, et Cas types, ligne du fonctionnaire.
- **« On cotise moins, donc on touche moins ? »** 18 + 5 font 23 contre 28
  aujourd'hui. Les cinq points rendus sont libres ; le simulateur les suppose
  replacés pour comparer à effort égal, et montre ce que ça change sur la
  fiche de paie. Simuler, bloc « Et pendant que vous cotisez ».
- **« D'où viennent les chiffres ? »** INSEE, Conseil d'orientation des
  retraites, DREES, Cnav, Légifrance. Page Données, et sous chaque graphique.
- **« C'est officiel ? »** Non, et chaque page le dit en bas. Seule la
  caisse fait foi.
- **« Qui a fait ça ? »** Un outil du Parti libéral français, modèle ouvert,
  code sous Apache 2.0, textes et infographies sous CC BY-SA 4.0. Le dépôt
  est public.

## Ce qu'il vaut mieux ne pas faire en salle

- Taper un salaire sans vérifier l'unité : le champ est en euros nets par
  mois, mais un sélecteur « Unité » permet « × salaire moyen ». Un 3 500
  saisi dans la mauvaise unité est refusé, avec un message clair.
- Ouvrir « Options de modélisation » : neuf règles d'indexation, tables de
  mortalité, projection du COR. C'est juste, et c'est trop pour vingt
  minutes.
- Passer du net au brut : le sélecteur existe, en haut des résultats, et
  toute la page suit. Garder le net, c'est ce que les gens connaissent.
- Chercher une explication au chiffre « coefficient de conversion » ou
  « capital notionnel rétroactif » sous les résultats : ils sont là pour qui
  veut vérifier, pas pour la présentation.
- Présenter depuis un téléphone : la page fonctionne, le chiffre d'abord et le
  reste replié, mais la grille des cas types demande un écran large.
