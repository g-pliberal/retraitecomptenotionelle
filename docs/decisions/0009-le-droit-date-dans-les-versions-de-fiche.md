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
