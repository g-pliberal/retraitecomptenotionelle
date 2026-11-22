# Note de décision 0009 — le droit daté dans les versions de fiche

*Décidée le 16 novembre 2026 par le propriétaire, qui avait demandé un
diagnostic de l'architecture du dépôt, puis voulu discuter de la règle qui
range dans les versions de sa fiche un paramètre que plusieurs lois
réécrivent. Le brouillon du 15 novembre allait trop loin. Quatre essais sur
le papier, le 16, en ont gardé l'idée et corrigé les règles, et les quatre
points qu'ils laissaient ouverts ont été examinés le même jour, sur
Légifrance et dans les fichiers du dépôt. Sa réponse : « On adopte la note 0009 maintenant ». Les
essais et le brouillon, qu'ils citent, sont sous `docs/decisions/0009/`. La
note précise le contrat C.2, l'annexe B et la phase 6 du chemin ; elle ne
touche à aucun principe.*

## Le problème

Le droit des retraites se lit sur deux axes à la fois : la loi en vigueur à
une date que le texte nomme, le plus souvent la date d'effet de la pension,
et la génération, ou une autre date, que cette loi vise. La réforme de 2023
vise les pensions qui prennent effet à compter du 1er septembre 2023, pour
les assurés nés à compter du 1er septembre 1961. Le contrat C.2 porte déjà
les deux : la version a ses bornes, et chacun de ses paramètres sa date qui
décide (§ 4.1 et 4.2).

Mais le droit daté d'une règle s'écrit aujourd'hui à plusieurs endroits,
quand le principe 2 n'en veut qu'un :

- **Une table par loi.** Les fiches de l'âge légal, de la durée requise et
  de l'âge d'annulation de la décote sont conformes, mais sans versions.
  `age_ouverture_requis.csv` applique les rédactions successives de
  L. 161-17-2 et D. 161-2-1-9, « la plus récente l'emportant ». Ce que la
  fusion efface est recopié dans `age_ouverture_avant_reforme_2023.csv` et
  `age_ouverture_avant_suspension.csv`, et de même pour la durée requise. Le
  moteur les lit par une classe par loi, et un droit contrefactuel pose une
  table sur l'autre (`TableRecouverte`). La table fusionnée ne dit pas quelle
  loi valait à quelle date : elle ne sait pas résoudre un renvoi daté.
- **Les valeurs de repli des fichiers de régime.** Les périodes renvoient à
  50 fiches par 2 570 interrupteurs. Ces renvois sont le plus souvent le
  droit du régime, mais ils sont datés à l'année, sans texte cité, et chacun
  garde une valeur que le moteur lit quand la table ne répond pas : 562 pour
  l'âge légal, 469 pour l'âge du taux plein, souvent l'âge « cible » d'une
  réforme, que l'en-tête de la table dit faux.
- **Des chiffres de la loi dans le code**, comme le 1er janvier 2004 et les
  65 ans de la surcote (`SURCOTE_DEPUIS`, `SURCOTE_AGE_MAJORE`), et des
  nombres recopiés d'un calcul sur une autre fiche, comme une porte de la
  carrière longue, « l'âge prévu à l'article L. 161-17-2 minoré de deux ans
  et six mois », stockée en 60 ans et 6 mois.

Le § 11 nomme ce cas le pire : « une migration arrêtée à mi-chemin, avec
l'ancien registre et la fiche vivant côte à côte ». Sur les 272 fiches de la
carte, le moteur en lit 80 par leurs versions, et 69 n'en ont aucune
(action 191, au 9 novembre 2026).

La preuve, elle, ne tient pas au code. C.2 demande déjà à chaque version ses
exemples officiels, ou « aucun trouvé », mais rien ne l'exige : 65 fiches sur
267 sont confrontées à un exemple (tableau de bord, au 15 novembre 2026). Le
champ `code` de la fiche nomme ses fonctions en prose, que rien ne vérifie,
et 130 fiches sur 267 seulement sont citées dans le code par leur
identifiant.

## La décision

### Le droit daté d'une règle vit dans les versions de sa fiche

Une règle qui a sa fiche, et que plusieurs textes réécrivent, vit dans les
versions de cette fiche : une version par réforme qui la réécrit, et par
public qu'elle vise. Pas une version par rédaction d'article dans LEGI :
D. 351-1-1 a six rédactions et la carrière longue cinq versions, car celle du
1er janvier 2026 « réécrit le I sans changer une valeur » ; D. 351-1-4 en a
cinq et la surcote quatre, car le même décret, le n° 2025-1410, y reprend la
rédaction de 2011 sans en changer une phrase.

### Une version porte ce que dit son texte

Elle porte ce que son texte écrit, et rien d'autre :

- **une table**, quand le texte en écrit une : les portes de la carrière
  longue, génération par génération ;
- **une valeur** : « l'âge prévu au 1° de l'article L. 351-8 est fixé à
  soixante-cinq ans » (R. 351-27, jusqu'en 2011) ;
- **un renvoi à une autre fiche**, avec son opération : « l'âge prévu à
  l'article L. 161-17-2 augmenté de cinq années ». Le renvoi nomme la fiche
  qu'il lit et la date qui choisit la version lue, le plus souvent la date
  d'effet de la pension. La fiche `age_reference_decote_ieg` l'écrit déjà
  ainsi, par son champ `lit` et un paramètre ;
- **un renvoi à sa propre rédaction antérieure**, pour ce que le texte lui
  laisse : la loi de 2025 écrit l'âge légal des nés à compter du
  1er septembre 1961, et pour les autres, « il est celui applicable en
  application du présent article dans sa rédaction antérieure ».

Une version ne recopie pas ce que son texte renvoie ailleurs : la table par
génération de l'âge du taux plein, qu'aucun texte n'écrit, disparaît. Chaque
partie d'une version cite le texte qui la décide, car deux textes en vigueur
peuvent se contredire : D. 161-2-1-9, que la loi de 2025 n'a pas réécrit, dit
encore 63 ans pour les nés en 1964, et la loi l'emporte.

### La version se choisit à la date que nomme le texte

Les bornes se lisent dans la disposition d'application du texte, par une
session qui suit `docs/veille_droit.md`, et non dans les dates de vigueur de
LEGI. La suspension est en vigueur au 31 décembre 2025, mais pour les pensions
prenant effet à compter du 1er septembre 2026. La rédaction de D. 351-1-4 qui
porte la surcote à 1,25 % entre dans LEGI le 1er avril 2009, pour les
trimestres accomplis depuis le 1er janvier 2009.

Cette date est le plus souvent la date d'effet de la pension. Elle est
l'échéance pour les pensions servies (`vise`) : l'avenant n° 17 de
l'Agirc-Arrco supprime le coefficient de solidarité pour les retraites prenant
effet à compter du 1er décembre 2023, et au 1er avril 2024 pour celles qu'il
minorait déjà.

Deux dates peuvent décider, l'une dans l'autre. Chaque rédaction de
D. 351-1-4 vaut pour les pensions qui prennent effet après elle (celles de
2011 et de 2026 le disent), et y donne à chaque trimestre le taux de sa date :
la date d'effet choisit la version, la date du trimestre la ligne, comme la
génération choisit la ligne de l'âge légal. Une pension mêle ainsi plusieurs
taux, dans une seule version. Borner les versions par la date du trimestre,
comme 18 fiches le font (`periode.debut`), revient au même tant qu'aucune
rédaction ne change le droit des trimestres accomplis avant elle ; celle de
2006, lue dans LEGI, change celui des trimestres de 2004 à 2006 (« Ce qui
reste ouvert »). Les renvois de la surcote à l'âge légal et à la durée requise
suivent la date d'effet.

### La ligne de partage avec la table datée

Une table datée (C.3) porte des valeurs qu'une date choisit, et se lit sans le
code : la valeur du point, les coefficients de revalorisation, même les cinq
de 2020, qui ne tiennent qu'au montant de la retraite. Une règle dont la forme
change au point qu'une ligne ne se lit plus sans le code va en versions,
quelle que soit la date qui les choisit : la surcote, dont la table a dû
prendre trois colonnes de règle (`rang_minimum`, `apres_65_ans`,
`trimestres_maximum`) que seul le code explique.

### Le fichier de régime garde son droit propre et ses renvois

Il dit qui il couvre, le droit qu'aucune fiche ne porte, et les fiches
auxquelles il renvoie. Un renvoi est le droit du régime, à sa date : le régime
général renvoie à l'âge du taux plein depuis 1983, quand la Banque de France
gardait un âge de 55 ans jusqu'en 2007 et la MSA des non-salariés un âge de
65 ans jusqu'en 1985. L'annexe B avait raison de garder les renvois.

Chaque renvoi, et chaque période de droit propre, prend la date du texte qui
la fait, au jour et non à l'année, et cite ce texte. Le renvoi perd sa valeur
de repli. Les dates de bascule se relisent une à une, en commençant par
celles qui changent un résultat. Des 96 renvois aux deux fiches d'âge, 51
courent dès le début du régime. 35 commencent quand la valeur du régime est
encore celle de la règle commune, 60 ans avant juillet 2011 ou 65 ans avant
juillet 2016 : leur date ne change aucun résultat, qu'elle soit du droit ou
une coupure de fichier (le régime général ne renvoie à l'âge légal qu'à partir
de 1994, quand son âge était déjà de 60 ans). Les huit régimes qui renvoient
à l'âge du taux plein depuis 2011 en sont. 10 peuvent en changer un : 8
remplacent une valeur différente (55 ans à la Banque de France avant 2008,
pour les deux âges ; 65 ans à la CNBF avant 2004 et à la Cavimac avant 2007 ;
60 ans pour le taux plein dans les trois régimes de la fonction publique
avant 2004 ; la table de la CRPCEN avant 2025), et 2 gardent 60 ans jusqu'en
2013, après que l'âge légal a bougé (les régimes d'artisans et de commerçants
d'avant 1973). La phase 6 se clôt quand les renvois sont datés, cités et sans
repli, et non quand ils disparaissent.

### Le code se relie aux versions

Le champ `code` cesse d'être de la prose : il nomme les fonctions qui
appliquent la fiche, par leur chemin et leur nom sous `moteur/js/`, et une
version qui change de formule nomme la sienne. Une fonction peut appliquer
plusieurs fiches, une par branche : `ageTauxPlein` en applique cinq. Chaque
fonction de règle nomme les fiches qu'elle applique, dans une étiquette que le
test lit. Un test vérifie les deux sens : aucune fiche exécutable sans
fonction, aucune fonction de règle sans fiche, aucun nom qui n'existe pas. Un
minimum ou un plafond entre deux fiches, comme l'âge du parent de trois
enfants qui borne l'âge du taux plein, se déclare dans une fiche de relation
(§ 6.2), comme `plafond_limite_age_fonction_publique` le fait déjà.

La fonction reçoit la date qui choisit chaque version qu'elle lit. Quand un
âge dépend de la date d'effet, le moteur ne déduit plus le premier départ
possible de l'âge (`ouvertureSous`) : il cherche la première date dont la
version ouvre le droit. Les lois de 2010, 2011, 2023 et 2025 ont visé des
générations qui ne pouvaient pas encore partir, si bien que la recherche rend
la même date que la table d'aujourd'hui ; un test le vérifie, réforme par
réforme. Celle de 2011 n'a pas de disposition d'application dans LEGI, et n'en
a pas besoin : elle relève l'âge des nés de 1952 à 1955, dont aucun ne
pouvait partir avant septembre 2012 sous la loi de 2010 ; elle entre en
vigueur le 23 décembre 2011, son décret le 31, et aucune pension ne prend
effet entre les deux, faute d'un premier du mois. Les chiffres de la loi
quittent le code des règles pour les versions.

### Chaque version reprise a deux preuves, ou dit ce qui manque

La certification lit ses valeurs dans le texte ; l'exemple officiel montre
son application, la date d'effet et la coupure au mois. Une version que
l'action 191 reprend a les deux, ou « aucun trouvé » avec ce qui a été
cherché. Les exemples couvrent aujourd'hui surtout les dernières versions :
les cinq de l'âge légal valent pour la suspension, les onze de la carrière
longue pour les générations 1964 à 1971 ; la surcote a un exemple pour chacun
de ses taux, mais aucun pour une pension d'avant 2009, ni pour un cinquième
trimestre d'avant 2007, là où le texte et le barème du dépôt divergent. Les
témoins restent l'alarme des régressions ; ils ne prouvent pas la loi.

### Un scénario qui garde une loi passée est une couche

Il devient une couche qui prolonge une version (C.4), sans table posée sur
une autre. Quand la loi gardée est close, comme l'âge de 2011 (62 ans dès
1955) ou celui de 2023 (64 ans dès 1968), la couche la reprend telle quelle :
les deux copies de l'âge légal sont les tables de ces deux versions. Quand
elle tenait en un mécanisme, la couche calcule ce qu'aucun texte n'a publié,
et le marque `supposée` : le minimum contributif d'avant 2023 au-delà de
cette date, que la réforme a relevé et revalorise désormais « sur la base du
Smic ». La carrière longue fait déjà ainsi (`avant`).

### Cinq cliquets tiennent la décision

Ne peuvent plus que baisser : les valeurs de repli des renvois de régime ;
les renvois sans texte cité ; les copies d'avant réforme, nommées une à une
(`age_ouverture_avant_reforme_2023.csv`, `age_ouverture_avant_suspension.csv`,
`duree_requise_avant_reforme_2023.csv`, `duree_requise_avant_suspension.csv`),
et non par leur suffixe, que portent aussi des tables d'avant une date qui
sont du droit (`pension_minimum_avant_1983.csv`) ; les versions reprises sans
leurs deux preuves ni ce qui manque ; les chiffres de la loi dans le code des
règles, nommés un à un par l'étape qui pose les cliquets. Ce sont des tests
de la suite, comme les cliquets des textes de la phase 2 ; cette note les
fait entrer (§ 13.4).

## Ce qui ne change pas

Les neuf principes ; le partage des versions et ses deux erreurs (§ 4.1) ;
les quatre sortes de dates qui décident (§ 4.2) ; les droits maintenus,
écrits en bornes (§ 4.3) ; les univers en couches (§ 4.8) ; les renvois des
régimes, que l'annexe B garde ; le JavaScript qui fait foi et ce qui reste en
Python (notes 0003, 0005 et 0006). Aucun résultat chiffré ne bouge : une
migration qui en déplace un s'arrête et le dit. Un cas que la règle ne sait
pas écrire revient à une note.

## Les cas qui l'ont éprouvée

Quatre fiches, choisies parce qu'elles risquaient le plus de casser le
format, ont été écrites en versions sur le papier le 16 novembre :

- **L'âge du taux plein** : ses trois versions sont des renvois, à un décret,
  puis à l'âge légal augmenté de cinq ans, puis de trois. La table par
  génération du dépôt n'est écrite dans aucun texte. 23 des 47 régimes qui y
  renvoient ont d'abord une valeur à eux. `ageTauxPlein` applique cinq règles.
- **L'âge légal** : la loi de 2025 renvoie à sa rédaction antérieure ; le
  décret en vigueur contredit la loi ; les deux copies d'avant réforme sont
  deux versions closes.
- **La surcote** : chaque rédaction vaut pour les pensions qui prennent effet
  après elle, et donne à chaque trimestre le taux de sa date ; le rang d'un
  trimestre se compte depuis le premier de 2004. L'essai bornait les versions
  par la date du trimestre ; la relecture des cinq rédactions, le même jour,
  a montré que celle de 2006 ne le permet pas sans sa disposition
  d'application.
- **La carrière longue** : rangée en versions dans un tableau depuis
  l'action 27. Sa porte des vingt ans de 2023, pour la génération 1964, se lit
  contre l'âge légal de 2023 : 63 ans moins deux ans et six mois, soit 60 ans
  et 6 mois. Lue contre la table fusionnée, qui donne 62 ans et 9 mois, elle
  donnerait 60 ans et 3 mois, trois mois trop tôt pour les pensions de
  septembre 2023 à août 2026. C'est la preuve que les deux axes sont
  nécessaires.

Le brouillon avait déjà éprouvé le coefficient de solidarité de
l'Agirc-Arrco (deux publics, l'un borné par l'échéance), la durée des régimes
spéciaux depuis 2008 (la date où les conditions sont remplies), la durée des
générations 1953 à 1957 et la suspension de 2025 (une réforme remplie de
plusieurs textes), la revalorisation de 2020 (table datée) et le minimum
contributif dans le droit du 31 août 2023 (une couche `supposée`).

Ce n'est pas une preuve : les régimes en points, la réversion et les régimes
spéciaux n'ont pas été essayés, et la migration de l'âge légal reste
l'épreuve qui compte.

## Les solutions écartées

- **Un fichier par loi**, la forme de legiretraite, de la DREES, et celle de
  l'âge légal aujourd'hui : un seul axe, la génération. Chaque loi y ajoute un
  fichier et une classe, et chaque scénario qui garde une loi passée, un
  mécanisme à part.
- **La table fusionnée**, la loi la plus récente l'emportant : elle efface la
  loi d'avant, dont ont besoin les pensions liquidées sous elle, les scénarios
  qui la gardent et les renvois qui la lisent à leur date.
- **La table entière dans chaque version**, que proposait le brouillon : elle
  recopie ce que le texte renvoie ailleurs, et invente des tables qu'aucun
  texte n'écrit.
- **Une version qui ne porte que ce qu'elle change, en règle générale** : lire
  une version demanderait de recomposer la table. Elle n'est admise que là où
  le texte l'écrit, comme la loi de 2025.
- **La fin des renvois des régimes**, que proposait le brouillon : ils sont le
  droit de chaque régime.
- **Une fonction, une fiche**, que proposait le brouillon : une fonction
  applique souvent plusieurs règles ; c'est la branche qui nomme sa fiche, et
  la fiche de relation qui en lie deux.
- **Le rangement d'OpenFisca-France-Pension**, par génération puis par date
  d'effet : il a les deux axes, mais une loi nouvelle touche chaque
  génération ; sa table de l'âge légal compte 419 lignes.
- **Une version par rédaction d'article de LEGI** : la vigueur d'un article
  n'est pas la borne d'une version.
- **Tout en tables datées (C.3)** : une table n'a qu'une date qui décide, et
  une loi qui vise des générations parmi les pensions d'une date d'effet en
  demande deux.

## Ce qui reste ouvert

Les quatre points que laissait la réécriture ont été examinés le 16 novembre,
sur Légifrance et dans les fichiers du dépôt. Les bornes de la loi de 2011
sont lues, et n'ouvrent aucune fenêtre (« Le code se relie aux versions »).
La disposition d'application du décret n° 2011-620 n'importe pas : LEGI n'en
montre aucune, ses rédactions entrent en vigueur le 3 juin 2011, et la
première date d'effet qui suit est le 1er juillet, celle de la loi de 2010.
Les rédactions de D. 351-1-4 de 2011 et de 2026 ne déplacent aucun résultat.
La première, du décret n° 2010-1734, pour les pensions prenant effet à compter
du 1er juillet 2011, remplace le soixantième anniversaire par l'âge légal :
les nés avant juillet 1951 gardent 60 ans, et les autres ne pouvaient pas
partir avant novembre 2011. La seconde, du décret n° 2025-1410, pour les
pensions prenant effet à compter du 1er janvier 2026, reprend la première
phrase pour phrase. Les dates de bascule des régimes sont comptées (« Le
fichier de régime garde son droit propre et ses renvois »). Restent deux
points, qui n'empêchent pas d'adopter la note :

- **La surcote des trimestres de 2004 à 2006.** Depuis 2006, D. 351-1-4
  donne ses taux « pour chaque trimestre accompli à compter du 1er janvier
  2004 » : 0,75 % du premier au quatrième trimestre, 1 % au-delà, et 1,25 %
  après soixante-cinq ans, quel que soit le rang. Le barème du dépôt garde
  0,75 % à tous les trimestres de 2004 à 2006, sur deux appuis : la
  circulaire Cnav 2018-04, qu'il résume ainsi, chaque trimestre garde le taux
  en vigueur à la date où il a été accompli ; et le décret n° 2006-1611, que
  `reformes.yaml` dit applicable « pour les trimestres accomplis à compter du
  1er janvier 2007 », sans identifiant. LEGI n'attache aucune disposition
  d'application à l'article, la page du décret ne s'ouvre pas, et aucun des
  quatre exemples officiels n'a de cinquième trimestre avant 2007. Si le
  décret ou la circulaire le disent en toutes lettres, le dépôt a raison, et
  des versions bornées par la date du trimestre disent juste ; sinon, le
  dépôt sert 0,75 % à des trimestres auxquels le texte donne 1 % ou 1,25 %,
  pour les pensions prenant effet depuis le 17 décembre 2006. C'est une
  question du scénario 1, à trancher avant de migrer la surcote.
- **Le droit d'avant 1985, un chantier de données, pas de format.** L'index
  n'a pas l'ancien code. Légifrance montre l'article 9 de l'ordonnance
  n° 82-270, qui la fait entrer en vigueur le 1er avril 1983 (dès le
  1er juillet 1982 pour deux publics), mais pas son article 1er, qui définit
  le taux plein : il se lit au Journal officiel. Les fiches font déjà avec.
  Des 271 versions qui couvrent des pensions d'avant le 21 décembre 1985, 171
  sont `lue`, dans les textes qui ont écrit la règle (ordonnances, lois,
  articles de l'ancien code cités par leur numéro) ; 100 sont `supposée`,
  dont 73 sans texte, au régime général surtout pour dire qu'un dispositif
  n'existait pas encore. Le format le dit déjà : une version cite ce qu'elle
  a, et son statut ce qui manque.

## La migration

Rien ne change dans le code avec cette note. Au commit qui l'ajoute, le
document d'architecture change le contrat C.2 (le renvoi daté, le renvoi à la
rédaction antérieure, le champ `code`, les deux preuves), la ligne entre C.2
et C.3, l'annexe B (les renvois datés, cités, sans repli) et la ligne 6 du
chemin, avec sa version datée sous `docs/architecture/versions/`. Le contrat
s'enrichit sans rien perdre, hors la prose du champ `code`, qu'un script
convertit d'un coup, comme un changement du noyau le demande : les fiches
d'aujourd'hui restent valides.

Elle s'applique dans l'action 191, une étape par session, sur Fable 5.2,
puisque chacune réécrit une règle du scénario 1. L'action 161 devait finir
avant, pour qu'aucune règle ne se migre dans deux moteurs ; au 16 novembre,
plus aucun test n'exécute de règle Python, hors les deux fichiers de la
façade, et chaque étape vérifie d'abord qu'elle n'a que le JavaScript à
toucher. Le mécanisme existe : la retraite progressive se lit par ses
versions (`fiches_datees`, `version_aux_dates`).

L'ordre :

1. Les cinq cliquets.
2. L'âge légal, que les autres fiches lisent : ses versions, renvoi de 2025
   compris ; la recherche de la première date de départ, avec le test qui la
   compare à la table pour chaque réforme ; la fin des deux copies et de
   `TableRecouverte`.
3. L'âge du taux plein, la durée requise, la carrière longue, dont le renvoi
   de 2023 remplace le nombre recopié, et la surcote, en versions choisies à
   la date d'effet, chaque trimestre au taux de sa date, une fois lue la
   disposition d'application du décret n° 2006-1611.
4. Les renvois et le droit propre des régimes, domaine par domaine : datés au
   jour de leur texte, cités, sans valeur de repli ; d'abord les dix dates de
   bascule qui peuvent changer un résultat.

Chaque étape est finie quand ses copies et ses classes par loi sont parties,
qu'aucun résultat n'a bougé, et que chaque version porte ses deux preuves ou
dit ce qui manque.

## Rectificatif du 16 novembre 2026

Le jour de son adoption, la note a été relue par un avis extérieur, confronté
aux textes et au dépôt. Trois de ses phrases étaient fausses, et cinq
précisions s'y ajoutent. Sa direction tient.

**Ce qui était faux.**

- **Le champ `code` est déjà vérifié, dans un sens.** Il n'est pas « en
  prose, que rien ne vérifie » : 240 des 241 fiches qui ont un code nomment
  leurs fonctions sous la forme « fichier : nom » que lit
  `tests/outils_carte.py`, et `test_le_code_de_chaque_fiche_tient` échoue sur
  un fichier ou un nom qui n'existe pas ; une seule fiche reste en prose
  (`EN_PROSE`). Aucun script n'a donc à le convertir. Ce que la note ajoute
  tient : l'étiquette de chaque fonction de règle, le test dans l'autre sens,
  la fonction de chaque version qui change de formule.
- **legiretraite n'a pas un fichier par loi.** Le relevé du dépôt
  (`docs/archives/releve_des_autres_modeles/drees.yaml`) lui donne un fichier
  par paramètre (`aod.csv`, `dureeRequise.csv`), par génération, caisse et
  catégorie. La solution écartée, un fichier par loi, est celle de l'âge
  légal du dépôt (`age_ouverture_requis.csv` et ses deux copies d'avant
  réforme), et non celle de legiretraite ou de la DREES.
- **La surcote des trimestres de 2004 à 2006 est tranchée.** L'article 3 du
  décret n° 2006-1611 du 15 décembre 2006 le rend applicable « aux pensions
  prenant effet à compter du 1er janvier 2007 », et l'exemple 3 de la
  circulaire Cnav 2007/5 du 16 janvier 2007 l'applique. Pour ces pensions,
  les trimestres accomplis depuis 2004 prennent 1 % à partir du cinquième,
  et 1,25 % après soixante-cinq ans : le dépôt, qui leur garde 0,75 %, a
  tort, à compter du 1er janvier 2007 et non du 17 décembre 2006. La forme
  que la note prévoit est la bonne : la version se choisit à la date
  d'effet, la ligne à la date du trimestre. La correction déplace des
  résultats : elle se fait en étape à part, sur l'accord du propriétaire,
  avant que l'étape 3 migre la surcote sans rien déplacer.

**Ce qui se précise.**

- **Deux renvois.** Un renvoi daté nomme la fiche, son opération et la date
  qui choisit la version. Un renvoi à une rédaction antérieure nomme la
  version par son identifiant, qui ne bouge pas quand une version s'insère
  ou que des bornes se corrigent. Le contrat de la fiche laisse encore
  `contenu` libre : la forme des deux renvois s'y écrit, et se teste, au
  début de l'étape 2, la première qui en porte un.
- **Un renvoi qui ne trouve aucune version, ou qui boucle, arrête le
  calcul** et nomme ses fiches. Les trous et les chevauchements des versions
  sont déjà refusés (`noyau/partage.py`, `moteur/js/versions.js`).
- **La recherche du premier départ** essaie chaque premier du mois, de l'âge
  le plus bas que porte une version au plus haut, et dit quand aucune date
  n'ouvre le droit.
- **L'étape 2 finit** quand un vrai consommateur lit l'âge légal par ses
  versions, qu'un scénario garde une loi passée, et qu'un test ajoute une
  réforme fictive et vérifie qu'elle ne change qu'une version.
- **Une table fusionnée peut se fabriquer** depuis les versions, pour
  l'affichage ou la comparaison, et jamais s'écrire à la main.

Faute d'exemple officiel, un cas calculé à la main tient le code, et se
déclare comme tel : il éprouve le code contre la lecture, non la lecture
contre le texte, et l'erreur de la surcote y aurait survécu. Contre le
rangement d'OpenFisca-France-Pension, l'argument est qu'une loi nouvelle
touche chaque génération, et non le nombre de ses lignes.

## Rectificatif du 19 novembre 2026

Le 18 novembre, le propriétaire a fait évaluer la note de nouveau, par un avis
indépendant, mené sans lire aucune évaluation antérieure. Ses comptes ont été
refaits sur le dépôt, ses textes relus dans l'index LEGI, et la recherche du
premier départ essayée sur chaque jour de naissance de 1923 à 1975. Sa
direction tient, et les affirmations de droit relues tiennent toutes. Deux de
ses phrases étaient fausses, et neuf précisions s'y ajoutent, dans l'ordre des
étapes qu'elles précèdent : au 18 novembre, ni les cliquets ni l'âge légal
n'étaient commencés. L'évaluation et les scripts de ses comptes sont sous
`docs/decisions/0009/`. Le corps de la note, gelé, garde les phrases que ses
deux rectificatifs corrigent : elle se lit avec eux.

**Ce qui était faux.**

- **« Aucun résultat chiffré ne bouge » ne tient pas à l'étape 4.** Dater un
  renvoi au jour de son texte déplace les pensions qui prennent effet entre ce
  jour et la coupure d'année du fichier. La note le sait, dont l'étape 4
  commence par « les dix dates de bascule qui peuvent changer un résultat » ;
  elle promet pourtant qu'aucun ne bouge, en fait la fin de chaque étape, et
  laisse « inchangés » à la ligne 6 du chemin. Relues au texte le 17 novembre,
  cinq de ces dix dates étaient fausses, et l'une cachait une erreur de
  règle : la décote de la Banque de France n'est pas celle de la fonction
  publique. L'étape 4 a donc deux sortes de commits. Le rangement ne déplace
  rien : un texte cité, une valeur de repli que plus rien ne lit, une date au
  jour qui tombe où le fichier coupait déjà. La correction déplace des
  résultats : elle a son test tiré du texte et l'accord du propriétaire, comme
  le premier rectificatif le demande pour la surcote. « Aucun résultat n'a
  bougé » ne clôt que le rangement, et la ligne 6 du chemin le dit désormais.
- **L'étape 2 ne finit pas `TableRecouverte`.** L'ordre de la migration lui
  donne « la fin des deux copies et de `TableRecouverte` ». Or `_sousLeDroit`
  pose aussi cette classe sur la durée requise, qui ne migre qu'à l'étape 3.
  L'étape 2 retire les deux copies de l'âge légal et leurs deux classes ;
  `TableRecouverte` part à l'étape 3, avec les deux copies de la durée
  requise.

**Ce qui se précise.**

- **Le cinquième cliquet se relève, il ne se choisit pas.** Une liste de
  chiffres « nommés un à un » ne garde que ce qu'elle nomme. Un test relève
  donc, dans le moteur hors du site, toute constante nommée dont la valeur
  porte une année ou une date, et toute année écrite en clair dans le code :
  131 constantes au 18 novembre, dont 77 dans le code des règles
  (`moteur/js/droit/`, `regimes.js`, `scenario-actuel.js`). Une liste dit de
  chacune si elle est du droit à migrer, et vers quelle fiche, ou pourquoi
  elle n'en est pas. Le nombre des premières ne peut que baisser, et une
  constante neuve que la liste ne classe pas fait échouer le test. Les
  chiffres de la loi sans date, un âge, un taux, s'y ajoutent à la main, comme
  la note le prévoyait.
- **La table d'une version reste lue dans LEGI, par le récupérateur.** La note
  dit ce qu'une version porte, non qui l'écrit. La table de l'âge légal n'est
  pas saisie : `scripts/fetch/dila_legi_parametres_retraite.py` la lit dans
  LEGI, rédaction par rédaction. Il lit déjà la date d'application en tête de
  chacune (`date_effet`), et résout déjà le renvoi de 2023 de la carrière
  longue contre l'âge légal de la date d'effet ; il ne lui reste qu'à ne plus
  fusionner (`_par_version`). La table d'une version tient donc dans un
  fichier indexé par version, comme `carriere_longue.csv` l'est par date
  d'effet et par génération ; celle que LEGI ne porte pas y entre lue à la
  main, à son niveau de fiabilité. La fiche déclare la version, ses bornes,
  ses textes, son statut et ses renvois, et désigne ses lignes. Aucune table
  ne se recopie à la main dans une fiche : la certification reculerait, et
  trois fiches dépassent déjà 100 000 octets. Ce récupérateur et
  `scripts/verifier_donnees.py`, qui certifie ses tables, sont dans le
  périmètre de l'étape 2 ; les deux copies d'avant réforme, lues à la main,
  passent ainsi sous leur contrôle.
- **Un renvoi nomme une valeur, et se contrôle à la fabrication.** L. 351-8 ne
  lit pas l'âge légal de l'assuré : depuis 2023, il lit « l'âge prévu au
  premier alinéa de l'article L. 161-17-2 », 64 ans quelle que soit la
  génération. Un renvoi nomme donc la valeur qu'il lit dans la version, non la
  fiche entière. Son opération ajoute une durée ou en retranche une, ce qui
  suffit aux quatre essais ; toute autre passe par une fonction que nomme le
  champ `code`, sans quoi le format devient un langage. Un renvoi se contrôle
  quand les données se fabriquent, d'une fiche à l'autre : sur toute l'étendue
  des bornes de sa version, la fiche lue a une version et une seule, et aucune
  chaîne ne boucle. Le contrôle d'aujourd'hui ne regarde qu'une fiche à la
  fois (`noyau/partage.py`) ; celui-ci entre par ce rectificatif (§ 13.4).
  L'arrêt du calcul, que pose le premier rectificatif, ne reste que comme
  ceinture : sur un site statique, il laisse au lecteur une page qui ne répond
  plus.
- **L'étape 2 se mène en trois sessions, et finit sur un point d'arrêt.**
  Chacune laisse les résultats identiques. La première fait des versions la
  source : le récupérateur les écrit, la fiche les déclare, et la table
  fusionnée comme les deux copies deviennent des vues fabriquées depuis elles,
  aux mêmes valeurs, sans toucher au moteur. C'est la règle du chemin : ce qui
  passe dans une fiche devient une vue fabriquée dans le même commit. La
  deuxième fait lire l'âge légal au moteur par ses versions, avec la recherche
  du premier départ. La troisième fait des deux droits contrefactuels des
  couches, et retire les deux copies. À la fin de l'étape 2, on compte ce
  qu'elle a coûté, en sessions et en commits, et le propriétaire décide de
  l'étape 3 : la note n'avait ni estimation ni règle d'arrêt.
- **Une couche garde une réforme, non une fiche.** Les deux droits
  contrefactuels ne changent aujourd'hui que trois règles, l'âge légal, la
  durée requise et la carrière longue (`_sousLeDroit`), quand dix-neuf fiches
  déclarent la réforme de 2023 et douze la suspension, par leur champ
  `reformes`. L'âge du taux plein est de ces dix-neuf. Sa table par
  génération, qu'aucun des deux droits ne recouvre, donne 67 ans sous les
  trois états du droit ; ses versions seront des renvois, l'âge légal plus
  cinq ans, puis celui du premier alinéa plus trois. Si la couche du 31 août
  2023 ne garde que l'âge légal de 2011, la version de 2023 y lira 62 ans plus
  trois, soit 65 ans. Un univers qui écarte une réforme garde donc, dans
  chaque fiche qu'elle a réécrite, la version d'avant : c'est « remplacer une
  version » (C.4), depuis la date d'effet de la réforme, et non une opération
  de plus. La liste des fiches se calcule depuis leur champ `reformes` :
  chacune est gardée, ou déclarée hors de la couche avec sa raison, pour que
  rien n'y reste par oubli. Le test de l'âge du taux plein sous les trois
  états du droit s'écrit avant le premier commit de l'étape 2 : le fichier qui
  tient ces deux droits, `tests/test_droits_contrefactuels.py`, ne contrôle
  pas cet âge.
- **La recherche du premier départ vaut pour toute règle qui ouvre un droit.**
  Pour l'âge légal, elle rend la date de la table : aucun écart sur les 19 358
  jours de naissance de 1923 à 1975, aucun droit ouvert puis refermé. Pour les
  portes de la carrière longue, elle compte. Le moteur lit la porte dans le
  texte de la date déclarée (`CarriereLongue.portes`), et le décret
  n° 2026-345 abaisse d'un trimestre la porte des vingt ans des générations
  1966 à 1970, pour les pensions prenant effet à compter du 1er septembre
  2026. Sur la table du dépôt, hors du moteur et la durée supposée acquise,
  pour un départ déclaré le mois qui précède cette bascule, la porte s'ouvre
  plus tôt par la recherche que par l'âge du texte de la date déclarée à 1 856
  jours de naissance sur les 2 617 essayés ; à la bascule de 2023, l'écart va
  dans l'autre sens. L'étape 3 commence par vérifier ce que le moteur rend
  pour un départ déclaré avant une bascule : un résultat qui bouge là est une
  correction, non une régression. Elle dit aussi à quelle date se comptent les
  durées pendant la recherche, aujourd'hui celle du départ déclaré. La
  recherche peut ne s'arrêter qu'aux dates où une version change, comme
  `ouvertureDe` le fait déjà pour les périodes de régime ; l'essai de chaque
  premier du mois, que décrit le premier rectificatif, sert alors d'oracle au
  test.
- **L'étape 4 se compte et s'ordonne avant de commencer.** La note compte les
  45 dates de bascule des renvois aux deux fiches d'âge. Tous renvois
  confondus, les 80 fichiers de régime portent 216 changements de renvoi après
  la première période d'un régime : 173 débuts, 41 fins et 2 changements de
  cible. 180 tombent sur une frontière coupée à l'année, et 38 périodes sur
  873 seulement sont datées au jour. L'étape relève d'abord ceux dont le texte
  n'est pas dans l'index, puis avance par poids dans les résultats, les
  régimes les plus peuplés et les dates d'effet récentes d'abord, dans un
  budget que fixe le propriétaire. Une valeur de repli ne se retire qu'une
  fois montrée morte : celle de l'âge légal l'est, sa table commençant à la
  génération 1900 ; celle de l'âge du taux plein répond encore avant la
  génération 1930.
- **Les corrections n'attendent pas la migration.** Le moteur date déjà une
  période au jour (`date_effet`, `periodeALEffet`). Les cinq renvois que la
  relecture du 17 novembre a trouvés faux, à la Banque de France, à la Cavimac
  et dans les régimes d'artisans et de commerçants d'avant 1973, peuvent donc
  se corriger dès l'accord du propriétaire, en parallèle des étapes 1 à 3,
  comme la surcote l'a été le 17 novembre.
- **Sans exemple officiel, une seconde lecture.** Une version sans exemple n'a
  qu'une preuve, et le premier rectificatif dit pourquoi un cas calculé à la
  main n'en fait pas une seconde. L'erreur de la surcote passait tous les
  tests : c'est une relecture qui l'a trouvée. Quand une telle version décide
  de pensions dans un régime peuplé ou à des dates d'effet récentes, son texte
  est relu par une session qui n'a pas vu la première lecture, et la fiche le
  note à ses sources.

Contre le tout en tables datées, l'argument n'est pas qu'une table n'a qu'une
date qui décide : `carriere_longue.csv` en a deux, et c'est la forme que prend
la table d'une version. Il est celui de la ligne de partage : une table porte
des valeurs, non un renvoi ni une règle dont la forme change.

## Amendement du 19 novembre 2026 : un sixième cliquet

Le 19 novembre, le propriétaire a demandé que le dépôt fasse mieux que les
autres modèles, et d'abord qu'il s'aperçoive seul d'une loi modifiée. Un
sixième cliquet s'ajoute aux cinq, à l'étape 1 ; il entre par cette note
(§ 13.4). Ses comptes sont ceux du 19 novembre, sur la liste des
rédactions lue dans l'index LEGI le 16 ; le script qui les refait est sous
`docs/decisions/0009/sixieme-cliquet/`.

**Ce que le dépôt faisait déjà.** Depuis l'action 184, GitHub met à jour
l'index LEGI chaque lundi et inscrit « à examiner » toute rédaction nouvelle
du périmètre, et la veille range parmi les fiches à relire celle dont un
article cité a une rédaction en vigueur ou à venir qu'elle n'a pas lue. Deux
trous y restaient. Rien n'échouait : c'était une ligne de la veille, que ne
lit que la session qui touche au scénario 1. Et une rédaction qu'une fiche
avait rattachée ne se montrait plus aux autres fiches qui citent le même
article : la veille montrait une fiche, quand 83 couples d'une fiche et d'une
rédaction en vigueur ou à venir étaient sans un mot de la fiche, 48 rédactions
pour 51 fiches, dont 18 rédactions qui commencent en 2026 ou après.

**L'alarme « loi modifiée ».** Toute rédaction en vigueur ou à venir d'un
article qu'une fiche cite a sa réponse dans cette fiche : une de ses versions
la compte parmi ses textes, ou la fiche la déclare sans effet sur elle, avec
le mot à mot qui le montre (`textes_sans_effet`). C'est la suite de la
décision : une version par réforme qui réécrit la règle, et non par
rédaction ; une rédaction qui ne change rien se dit donc telle. La réponse
d'une fiche ne vaut que pour elle. Une rédaction que l'index apporte après la
pose du cliquet n'a pas de dette admise : quatorze jours après son
inscription, la suite échoue tant qu'une fiche qui cite son article n'a pas
répondu ; d'ici là, la veille et le tableau de bord la montrent. Le délai
tient à ce que l'inscription du lundi est commitée par GitHub : sans lui,
`main` rougirait sans qu'aucune session y soit pour rien, et la première
venue aurait à lire une loi avant son travail. Les rédactions d'avant la pose
font une dette, en deux nombres qui ne peuvent que baisser : 435 couples où
la fiche cite la rédaction sans l'avoir coupée en version, dont 269 dans les
70 fiches encore sans version, que la migration résorbe ; 83 où elle n'en dit
rien, à lire d'abord. Un compte seul ne suffirait pas : une rédaction neuve
remplace celle qu'elle abroge, et le nombre ne bouge pas. L'alarme tient donc
à la date d'inscription, non au compte.

**Chaque réforme déclarée a sa version.** Une fiche qui déclare une réforme
(`reformes`) a une version dont une borne commence à la date de cette
réforme. Sinon une liste dit, couple par couple, quelle version la porte à
une autre date, et selon quel texte ; pourquoi elle n'en fait naître aucune ;
ou qu'elle reste à faire. Le nombre des « à faire » ne peut que baisser, et un
couple que la liste ne classe pas fait échouer la suite : déclarer une
réforme dans une fiche oblige à dire où elle est portée. Au 19 novembre,
65 fiches déclarent 136 couples : 40 ont leur version à la date ; 49 sont
dans 23 fiches sans version, dont l'âge légal et la carrière longue, que les
étapes 2 et 3 migrent ; 47 sont dans une fiche dont aucune version ne
commence ce jour-là. L'égalité des dates ne suffit pas à faire la règle :
`age_ouverture_ieg_actifs` déclare la réforme de 2023, que le calendrier date
du 1er septembre 2023, et fait commencer sa version le 1er janvier 2025.
`test_toute_reforme_recente_a_sa_fiche` reste, qui tient l'autre sens : une
réforme récente a une fiche.

**Ce que l'alarme ne voit pas.** Un article neuf qu'aucune fiche ne cite
encore : il entre « à examiner », parmi 6 015 rédactions. Une disposition non
codifiée d'un texte hors du périmètre. Une circulaire, que tient la veille de
la base de la Cnav (action 175). Deux rédactions du même numéro en vigueur
ensemble, que la liste ne départage pas. Un avenant de l'Agirc-Arrco, tant
que GitHub ne met pas à jour KALI le lundi. Elle a le retard de l'index, une
semaine au plus, ajouté à celui que LEGI met à consolider un texte paru. Et
elle dit qu'un texte a changé, non que la fiche l'a bien lu : une déclaration
« sans effet » se relit comme toute lecture, et l'alarme n'en dispense pas.

**L'ordre.** L'étape 1 pose six cliquets. Le sixième n'écrit dans aucune
fiche et ne change aucune règle. Les 83 rédactions sans un mot se lisent
ensuite, dans une session à elles, les plus récentes et les régimes les plus
peuplés d'abord : chaque réponse est une lecture du droit, sur Fable 5.2.

## Rectificatif du 21 novembre 2026 : le modèle des étapes

Le 21 novembre, le propriétaire a décidé : « On travaille sous Opus 5.5 et on
fait relire par Fable ». Là où la note dit qu'une étape de l'action 191, ou
la lecture des rédactions sans un mot, se mène « sur Fable 5.2 », il faut
lire depuis cette date : sur Opus 5.5, et relue sur Fable 5.2 avant d'être
publiée (`CLAUDE.md`, « Le scénario 1 est le droit applicable »). Le reste de
la note ne change pas.

## Amendement du 22 novembre 2026 : les deux axes du fichier de régime

*Adopté le 22 novembre 2026, la classification des champs validée par le
propriétaire (point d'arrêt 1). Elle est écrite dans le code,
`src/retraite_notionnelle/donnees/axes.py` ; le relevé qui la fonde, champ par
champ, avec les lectures du moteur, est
`docs/decisions/0009/separation-des-axes/classification.md`.*

Le 22 novembre, le propriétaire a choisi de séparer complètement les deux
axes des fichiers de régime : « on prend complète alors ». Cet amendement
écrit le contrat de cette séparation. Il touche le § « Le fichier de régime
garde son droit propre et ses renvois » et la migration ; il ne change ni la
ligne de partage avec la table datée, ni les versions de fiche, ni les
cliquets. Ses comptes sont ceux de `main` au 22 novembre (389536e).

**Le problème.** Une période d'un fichier de régime porte ensemble deux sortes
de paramètres, que le moteur choisit sur deux axes. Les règles de la
liquidation se choisissent à la date d'effet de la pension (§ 4.6 de
l'architecture, `periodeDeLiquidation`) ; l'assiette, le taux et les points
se choisissent à l'année où le droit s'acquiert (`periodesActives`). Une
période coupée pour l'un l'est pour l'autre. Des 733 frontières entre deux
périodes contiguës, 420 ne changent que la cotisation : chacune recopie
toutes les règles de la liquidation, que rien n'a changées. 154 ne changent
que la liquidation, 89 les deux, 51 un montant servi seul ou la seule
structure, 19 un montant servi avec l'une ou l'autre ; les 62 autres suites
reprennent une tranche. Les 875 périodes ne portent ainsi que 319 lignes de
liquidation distinctes. Une règle de liquidation qui change en cours
d'année a dû prendre `date_effet` (21 régimes), et un taux de cotisation qui
change en cours d'année ne peut pas se dire du tout.

**Quatre familles.** Chacun des 144 champs de période appartient à une
famille, et une seule :

- *la liquidation* (92 champs) : une règle choisie à la date d'effet de la
  pension, ou à la date d'un fait que la règle nomme — l'ouverture du droit,
  le 31 mars 1983, le début de l'invalidité. Les âges, les durées, la décote,
  la surcote, le taux plein, le salaire de référence, les barèmes
  d'abattement, la carrière longue, la table de la valeur du trimestre des
  mines et le régime au titre duquel s'oppose le plafond de la majoration
  pour enfants, qui tiennent l'un et l'autre à la date d'effet ;
- *la cotisation* (39 champs) : un paramètre choisi à l'année où le droit
  s'acquiert. L'assiette et ses bornes, les taux et leurs parts, les
  forfaits et les classes, les points que l'année ouvre et ce qui les marque
  (`points_abattus_a_l_age`, `points_invalidite`), la dispense et
  l'exemption ;
- *le montant servi* (6 champs) : un montant en euros d'une année que le
  service revalorise ensuite — la valeur du point de la fiche, le forfait,
  le plafond de la majoration pour enfants — et son millésime ;
- *la structure* (7 champs) : ce qui décrit le régime ou découpe le fichier —
  `type_calcul`, constant dans chacun des 80 régimes, `points_de`, qui ne
  change qu'à l'Arrco des cultes, passée au barème de l'Agirc-Arrco en 2019,
  les bornes (`debut`, `fin`, `date_effet`), les notes et les textes des
  renvois.

Deux faits l'éprouvent. Les dix régimes dont deux périodes couvrent la même
année — les tranches — ne diffèrent, d'une tranche à l'autre, que par des
champs de la cotisation : l'axe de la liquidation n'a aucun chevauchement.
Et le moteur, instrumenté sur tous les témoins, lit les champs de la
cotisation sur une période de l'année ; quand il les lit sur la période de
la liquidation — l'assiette, au salaire de référence ; le barème des points
de la MSA, pour son coefficient de durée — la date d'effet et son année
donnent partout la même valeur.

**La forme.** Le fichier garde son en-tête et range ses paramètres en quatre
blocs, un par famille. Chaque bloc de lignes est complet ligne par ligne,
comme les périodes aujourd'hui : une ligne ne s'hérite pas de la précédente.

```yaml
structure:
  type_calcul: points
  points_de:                     # absent : le régime lui-même
    - {du: 2006-01-01, regime: arrco}
    - {du: 2019-01-01, regime: agirc_arrco}
liquidation:                     # au jour ; contiguës ; jamais deux à la fois
  - du: 1983-04-01
    au: 1994-01-01               # exclu ; absent : en vigueur
    textes: {...}                # les textes des renvois de la ligne
    notes: ...
    age_ouverture: 60
    ...
cotisation:                      # deux lignes du même jour : deux tranches
  - du: 1945-01-01
    au: 1951-01-01
    tranche: 2                   # la première tranche ne se numérote pas
    textes: {...}                # les renvois de cotisation ont les leurs
    notes: ...
    assiette: plafonnee
    taux_cotisation_retraite: 0.08
    ...
servi:                           # au jour
  - du: 1952-01-01
    valeur_point_euros: ...
    valeur_point_annee: 2026
```

Les trois axes datés s'écrivent de même, au jour, `[du, au)`. La cotisation
s'écrit au jour dès la migration, mais le chargeur n'y admet que des
1er janvier jusqu'au passage au jour : la forme ne changera plus, seule la
contrainte se lèvera. Une tranche se nomme par son numéro, et non plus par
l'ordre des périodes, qui n'est pas chronologique dans six régimes ; une
lecture de la cotisation à la date d'effet prend la tranche 1, celle que la
première période donne aujourd'hui. Les textes suivent la ligne qui ouvre le
renvoi : six renvois sont de la cotisation (`INTERRUPTEURS`), dont le barème
des points de la MSA. `taux_cotisation_annuels.csv`, qui date déjà les taux
de 8 régimes année par année, reste ce qu'il est pendant le gel : le
chargeur l'applique à la cotisation seule, et non plus à des périodes
entières. L'y fondre est une correction ordinaire, après.

**Ce que le moteur lit.** La liquidation d'une pension prend la ligne de
liquidation en vigueur à sa date d'effet, la structure, et la ligne servie
de la même date ; l'acquisition d'une année prend ses lignes de cotisation.
Les lectures croisées que le relevé a trouvées se rangent toutes sous ces
deux règles, à une autre date ou une autre année :

- une règle de liquidation lue à une autre date que l'effet : l'ouverture du
  droit (`ouvrir.js`, deux sites), le 31 mars 1983 (`tauxAcquisAu31Mars1983`,
  qui lit 1982), le début de l'invalidité (`invalidite.js`), la durée de
  chaque année (`dureeDeLAnnee`), l'année du départ (`departs.js`) ; la
  proposition, qui fusionne le droit d'une année (`fusion.js`) ;
- la structure lue à une année (`coordonner.js`, `revalorisation.js`) ;
- un paramètre de cotisation lu à l'année d'une ligne pendant la liquidation
  (`liquider.js`, l'assiette forfaitaire de chaque année ; `departs.js`, la
  part cotisée), ou à la date d'effet (l'assiette du salaire de référence,
  le barème des points de la MSA) ;
- un montant servi lu à l'année d'acquisition : la valeur du point de la MSA,
  qui fait le barème de ses points (R. 732-70). Le montant servi se lit
  donc à toute date, et non seulement à la liquidation.

Trois lectures ne s'y rangeaient pas ; la relecture les a tranchées. Le
plafond de trimestres des mines s'applique sur la ligne de liquidation, et la
boucle annuelle ne lit à l'année que de quoi savoir si l'année y est soumise
(`acquerir.js`) : elle lira la même ligne, et ses deux champs, 120 trimestres
et 55 ans sur les 22 périodes, restent de la liquidation sans qu'aucune
valeur bouge. La caisse des membres du CESE pèse chaque annuité par la durée
requise de la période qui l'a acquise, 142 trimestres jusqu'au 31 août 2004,
149 ensuite (`annuitesAuTauxDeLeurAnnee`) : l'indicateur reste de la
liquidation, et ce poids devient un champ de cotisation propre à la caisse,
plutôt qu'une ligne de liquidation lue à l'année. `avantages_non_contributifs`
reste entier à la liquidation : tout ce que le moteur en lit passe par elle,
et les périodes assimilées, seules acquises l'année, n'ont aucun lecteur.

**Le choix à l'année ne se traduit pas en date.** Aujourd'hui, une lecture à
l'année prend la période dont les années couvrent cette année. Aucune date
fixe de l'année ne la reproduit partout : pour les champs de la liquidation,
le 1er janvier diffère d'elle sur 13 couples d'un régime et d'une année, le
1er juin sur 8, le 1er décembre sur 16, dans 21 régimes en tout. L'étape 3 donne
donc à chaque lecture à l'année la date que son texte nomme ; là où un témoin
bouge, la session s'arrête, comme le veut la règle du gel, et le dit.

**L'oracle.** Un script hors du dépôt rend, pour chaque régime, chaque
champ, chaque année d'acquisition de 1900 à 2070 et chaque date d'effet du
1er de chaque mois de cette plage, la valeur que le chargeur donne au moteur.
La migration doit rendre le même, au caractère près, de l'étape 2 à
l'étape 5. Il ne compare ni les bornes ni les notes, que la migration
récrit. C'est un outil de vérification et non une source : il n'entre pas
dans le dépôt, et s'est refait sur le `main` du jour où le gel a commencé
(033e864, le 22 novembre).

**L'étape 2, faite le 22 novembre.** Les 80 fichiers sont écrits en quatre
blocs : 322 lignes de liquidation, 58 de servi, 875 de cotisation. Un script
hors du dépôt les a migrés en recopiant le texte de chaque champ, ses
commentaires compris. Pendant le gel, le chargeur refait les périodes que le
moteur lit encore (`vue_ancienne`) : une par ligne de cotisation, dans l'ordre
du fichier, avec la liquidation, le servi et la structure en vigueur au
premier jour de sa date d'effet. C'est pourquoi la cotisation garde, pour
l'heure, une ligne par période d'hier, même quand rien n'y change : elle se
resserre quand la vue part. Une borne au jour d'une ligne de liquidation
rend sa `date_effet` à la période dont l'année est la plus proche. Une ligne
de cotisation sans `tranche` est de la tranche 1. La note d'une période est
allée à la ligne de liquidation qui s'ouvre le même jour, sinon à sa ligne de
cotisation : une règle de position, qui pose sur la liquidation des notes qui
parlent de cotisation ; elles se rangent à la main quand la vue part. Refaites
ainsi, les périodes des 80 régimes sont celles d'hier, à l'égalité près ;
l'oracle est identique, et le paquet du site, au caractère près.

**L'ordre.** Il ne change pas : la nouvelle forme devient la source et
l'ancienne une vue fabriquée (étape 2), le moteur la lit (3), puis le
Python, le paquet et les tests (4), la vue ancienne part (5), le passage au
jour suit (6), puis les lots de l'étape 4 de l'action 191 (7). Rien de ce que
la séparation remplace ne reste : `date_effet` et les périodes partent avec
la vue ancienne, et `periodesActives` avec elles.
