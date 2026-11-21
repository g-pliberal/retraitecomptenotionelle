# Action 194, étape B : les deux filets de la carte de justesse

Le 21 novembre 2026, sur Opus 5.5 (le dépôt veut Fable 5.2 pour les étapes
qui écrivent une règle du scénario 1 ; celle-ci n'en écrit aucune). Aucun
résultat du simulateur n'a bougé : l'étape ajoute un module qui lit, un
script, un rapport, un cliquet et une section du tableau de bord. Puis le
point d'arrêt que le propriétaire a demandé.

## Ce qui est fait

**Le module** `src/retraite_notionnelle/noyau/filets.py` porte les règles des
deux filets ; **le script** `scripts/filets.py balayage | neutralisation` les
fait tourner sur le moteur du jour, par le pont (`pont.mjs`, demande
`simulations`), sur quatre cœurs, et récrit sa moitié du rapport,
`tests/cliquets_de_justesse/filets_rapport.yaml`. Le balayage dure 30 minutes
(528 615 calculs), la neutralisation 50 minutes (environ 750 mutations) : ni
l'un ni l'autre ne tourne dans la suite, ni à GitHub. Le rapport est celui du
`main` du 21 novembre à 8 heures (`fda01bd`), l'étape 3 de l'action 191, la
durée requise prouvée et la décote de l'hiver 2002-2003 comprises.

**Le cliquet** `tests/cliquets_de_justesse/filets.yaml` tient les deux
comptes, qui ne peuvent que baisser ; `tests/test_filets.py` en tient le
rapport sous lui, et rejoue l'échantillon fixe du rapport (200 paires : un
exemple de chacun des 150 groupes d'anomalies les plus nombreux, 50 paires
saines prises aux bornes) sur le moteur du jour, en six secondes. Les deux
tests sont au filet des fichiers communs.

**Le tableau de bord** porte, à part de la carte, la section « Les filets de
la carte » (`filets_de_la_carte`, dans `scripts/tableau_de_bord.py`) : elle
ne change l'état d'aucune partie.

## Le balayage de cohérence

Les treize cas types du coût, chacun d'un seul statut, écrits en part du
salaire moyen de chaque année, d'un profil plat (le cas au SMIC à la moitié
du salaire moyen) ; générations 1940 à 1990 ; départs par trimestre, de
60 ans (ou deux ans avant l'âge du cas type quand un statut ou des services
datent son départ) à 70 ans ; un départ que le droit n'ouvre pas ne se
compare pas (81 560 paires).

**Les baisses** : (a) salaire 20 % plus haut une année (la deuxième de la
carrière, celle des 40 ans, la dernière entière), (b) début avancé d'un an,
(c) départ un trimestre plus tard ; générations nées en janvier. Une baisse
de plus d'un millionième est admise si une ligne de
`tests/cliquets_de_justesse/baisses_legales.yaml` la rattache à un texte
cité, ou, en (c), si une borne de version tombe entre les deux départs. La
liste est vide : les quatre baisses légales du brief (années d'avant 1948,
prorata des régimes alignés avant 2017, seuil de la fonction publique,
écrêtement du minimum contributif) supposent une carrière de plusieurs
statuts, et aucune n'est apparue. Une ligne ne s'inscrit qu'après lecture de
son texte.

**Les sauts** : entre deux générations nées à un mois d'écart, au même âge,
le taux de remplacement et la pension bougent tous deux de plus de 1 %
(seuil relatif, retenu après la première passe). Un saut est admis quand une
borne tombe à la génération d'après, au départ d'après ou à la date où une
pension est servie : une table du paquet par année, une ligne de table de
version, une revalorisation ou une valeur de service datée, une borne de
version. Deux règles se sont ajoutées après la première passe, chacune par
son test : un saut qui suit un trimestre validé de plus, dans son sens (la
durée se compte au trimestre, validé au salaire de l'année civile,
L. 351-2), avait fait 2 900 « sauts » sur deux cas ; et un saut du seul
dénominateur au 1er janvier, sans saut de la pension, n'en est pas un.

**Le résultat : 3 052 anomalies à expliquer**, en 503 groupes (sorte, cas
type, génération). Ce sont des pistes, non des erreurs établies ; aucune
n'est corrigée ici. Par famille, de la plus nombreuse :

1. **Le dernier traitement au 1er février** (fonctionnaires sédentaires et
   actifs, agent de conduite de la SNCF, IEG, militaire : 2 000 pensions
   environ). Partir le 1er février plutôt que le 1er janvier fait prendre le
   traitement de l'année nouvelle. Né en octobre 1956, fonctionnaire de
   l'État parti à 65 ans et 3 mois : 28 938,60 € par an au 1er janvier 2022,
   30 554,53 € au 1er février (+5,6 %, le traitement passe de 35 480 € à
   37 461 €). La question est de texte : la condition des six mois
   (L. 15 du code des pensions) porte sur l'indice, non sur la valeur du
   point ; le profil plat fait monter le salaire au 1er janvier, ce que le
   moteur peut lire comme un changement d'indice ou comme une mesure
   générale.
2. **Le complément différentiel de la complémentaire des exploitants**
   (1 043 baisses, a, b et c) : la pension baisse de quelques dizaines de
   centimes quand la base monte. Né en janvier 1959, parti à 64 ans et
   3 mois en 2023, un salaire 20 % plus haut en 1980 : 13 663,72 € puis
   13 663,47 € par an. Un complément
   différentiel devrait laisser le total plat : la baisse est une erreur
   d'arrondi ou d'assiette, minuscule mais réelle.
3. **Un départ plus tard qui augmente la décote, de novembre 2002 à février
   2003** (artisan, cadre, contractuel nés en 1940 et 1941), relevée à la
   première passe : artisan né en janvier 1940, parti à 62 ans et 9 mois,
   11 859,59 € ; un trimestre plus tard, 11 534,39 € (−2,7 %). Une autre
   session l'a lue au texte la même nuit : la durée requise change de
   version au 1er janvier 2003, et la baisse est désormais admise par ces
   bornes de version.
4. **Le contractuel public né en 1951 à 1953, parti tard**, relevé à la
   première passe (+5,7 % pour un mois de naissance de plus) : après les
   corrections publiées dans la nuit, il ne saute plus que de 0,6 % (19 880,71 € puis 20 001,04 €).
5. **La surcote d'un régime spécial** (IEG, né en mars ou avril 1954, parti
   à 63 ans et 9 mois) : un trimestre de surcote perdu en décalant la
   naissance d'un mois (43 474,29 € puis 42 929,24 €).

Le reste tient à quelques pensions : la carrière interrompue et le cadre nés
en 1976 et 1977, partis à 64 ans et quart (−1,8 %), l'artisan né en 1948 et
1949 parti en 2018.

## La neutralisation

Chaque partie de la carte mutée dans une copie des données, le paquet
rebâti par la fabrique, les 937 témoins de simulation rejoués quand il a
changé. Trois mutations, dans l'ordre : les nombres du contenu de la version
(+1 sur un entier, ×1,01 sur un réel) ; ceux de la source que la fiche nomme
(`code.parametres` : colonnes d'un CSV, clés d'un YAML de régime), pour la
fiche entière ; ses interrupteurs inversés. L'aller-retour du YAML et du CSV
sans mutation rend le paquet au bit près, vérifié une fois.

**Sur 949 parties, 494 gardées, 192 non gardées, 263 hors d'atteinte.** Une partie non
gardée change le paquet sans qu'aucun témoin bouge : la règle n'est pas
surveillée. Une partie hors d'atteinte ne change pas le paquet : ses
paramètres de version ne sont que la copie, en prose, de ce que le moteur lit
ailleurs (plus de la moitié des fiches découpées ne portent pas leurs
versions au paquet), et sa fiche ne nomme pas de source qu'on sache muter. 362 parties ne
sont gardées que par la source de leur fiche : la garde vaut pour la fiche,
non pour chaque version. Les non gardées les plus nombreuses : la
majoration de la retraite proportionnelle, le minimum contributif (huit
versions), le complément différentiel de la complémentaire agricole, le
versement unique de l'Agirc-Arrco, la pension majorée de référence, la
réversion. Le tableau de bord les nomme, par famille.

## Ce que les filets ne voient pas

- Les exemples officiels ne sont pas rejoués sous mutation : leur
  confrontation passe par le pont du droit, fonction par fonction, et non par
  des requêtes. La garde est une borne basse.
- Une borne de version n'est pas mutée d'un jour : une partie gardée l'est
  par sa valeur, non par sa date.
- Le balayage ne parcourt que des carrières d'un seul statut, d'un profil
  plat : les baisses des carrières de plusieurs régimes, et ce que le profil
  d'un cas type change, restent hors de vue.
- Toute table par année du paquet admet un saut au 1er janvier : le filet ne
  voit bien que les sauts en cours d'année.

## Ce que l'étape a coûté

Une session, trois commits au plus ; six fichiers neufs ou retouchés de code
et de tests, trois de données de test, la note ; deux passes complètes du
balayage et deux de la neutralisation, la dernière sur le `main` du jour
(30 et 50 minutes), sur quatre cœurs.

## Par quoi continuer

Le point d'arrêt : le propriétaire décide de la suite (étapes C à F). Les
pistes du balayage, triées par nombre de pensions, et les parties non
gardées, par famille, peuvent réordonner la preuve régime par régime
(étape E). La troisième piste (la décote qui monte en 2003) et la deuxième
(le complément différentiel) se vérifient au texte en premier.
