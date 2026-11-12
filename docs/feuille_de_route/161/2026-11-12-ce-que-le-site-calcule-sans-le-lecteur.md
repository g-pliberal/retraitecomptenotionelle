# Ce que le site calcule sans que le lecteur y change rien : mesuré page par page, rien de plus à garder en Python seul

**La conclusion.** Le principe du propriétaire — ce qui se calcule à
l'avance reste en Python — est déjà appliqué jusqu'au bout. Huit pages sur
neuf ne dépendent pas du lecteur, et elles sont écrites toutes faites à la
fabrique : le navigateur ne les recalcule que si l'adresse porte des réglages
ou si l'écran ne convient pas au dessin, et ce recalcul n'appelle aucune
règle de droit ni aucune simulation. Le JavaScript que seules ces pages
atteignent tient en 187 fonctions, 1 001 lignes au plus, sur les 54 583 des
modules de calcul chargés : 367 lisent les agrégats que le Python a figés,
143 sont la garantie de population, déjà instruite (question 1), le reste lit
le paquet pour l'afficher. Dans le simulateur, rien de ce qui pèse n'est
indépendant du lecteur, hors la mise en tables du paquet. Aucun élément de
plus n'est à sortir du JavaScript ; rien n'est modifié.

**La demande.** Le propriétaire, le 12 novembre 2026 : « Je me demande s'il
n'y a pas des choses légitimes à garder en python et ne pas porter en
JavaScript. En effet, certains calculs peuvent se faire à l'avance. » La
question avait toujours été posée dans l'autre sens — que retirer du
Python (note de décision 0006, inventaire du 9 novembre) ; la note de la
question 1 avait trouvé au passage un calcul que le site refait sans que
rien n'y vienne du lecteur, la garantie de population. Cette étape cherche
s'il y en a d'autres.

**La méthode.** Sur 6505133, des essais jetables, hors du dépôt, non
commités. Un chargeur de node enveloppe chaque fonction et chaque méthode
des modules de calcul de `moteur/js/` — tout sauf le site, `pages.js`,
`gabarit.js`, `routeur.js`, `adresses.js` — et relève, pour chaque appel
venu du site, la fonction, l'empreinte de ses arguments, son temps et les
fonctions qu'il atteint. Chaque page est rendue par `rendre`, comme le fait
`web/site.mjs`, dans un processus à elle : les neuf sous les réglages par
défaut ; le simulateur sous deux lecteurs qui diffèrent en tout — la
carrière et onze réglages — et sous les deux mêmes carrières sans réglage ;
Coût sous des réglages. Un appel dont la fonction et les arguments se
retrouvent sous les deux lecteurs ne dépend pas du lecteur. Les temps cités
sont ceux d'un rendu sans instrument, dans node.

## Les huit pages sans lecteur

`rendre` ne passe le lecteur qu'au simulateur. L'accueil, Risque, Méthode,
Partager et Saviez-vous ne reçoivent que le paquet ; Carrières types, Coût et
Droits non cotisés se rendent sous les réglages de référence quoi que
l'adresse demande, depuis l'action 150 (`agregee`, `pages.js:494`). Mesuré
sur Coût : sous onze réglages, trois appels sur 9 917 diffèrent, ceux qui
lisent les réglages pour les reporter dans les liens.

Ces pages sont donc calculées à l'avance en entier : `construire_pages.py`
les écrit à la fabrique, et un lien vers une autre page charge son dossier
(`naviguer`, `routeur.js:1463`). Le navigateur n'en recalcule une que dans
deux cas (`peutHydrater`, `routeur.js:3344`) : l'adresse porte des réglages,
ou la colonne ne convient pas au dessin.

| page | premier rendu | rendu suivant | ce que le rendu appelle |
|---|---:|---:|---|
| accueil | 53 ms | 5 ms | la mise en tables du paquet, le coût figé, la garantie (2 chiffrages de population, 9 compléments d'une personne) |
| Carrières types | 18 ms | 3 ms | les cas types figés, les comptes |
| Coût | 122 ms | 29 ms | la mise en tables, le coût figé, les dépenses, la garantie (9 chiffrages) |
| Droits non cotisés | 97 ms | 25 ms | la mise en tables, les avantages figés |
| Risque | 10 ms | 1 ms | le bilan figé |
| Méthode | 49 ms | 10 ms | la mise en tables, treize coefficients d'indexation |
| Partager | 5 ms | 1 ms | le bilan figé |
| Saviez-vous | 5 ms | 1 ms | rien |

Aucune de ces pages n'atteint une fonction de `droit/`, ni `simuler`, ni
`liquider`. Leurs appels au calcul : 3 467 lectures d'agrégats
(`agregats.js`, 61 fonctions), puis des accesseurs du paquet — les dépenses
(991), le bilan (491), les séries macroéconomiques (479), les régimes (407),
les comptes (256).

## Le JavaScript qui ne sert qu'à elles

Des 437 fonctions que ces pages atteignent, 187 ne sont jamais atteintes
sous un appel propre à l'un des deux lecteurs du simulateur. C'est un
majorant : un troisième lecteur ne peut qu'en retirer.

| module | fonctions | lignes | ce que c'est |
|---|---:|---:|---|
| `agregats.js` | 92 | 367 | les lecteurs de la table que le Python fige : le principe, déjà appliqué |
| `garantie.js` | 5 | 143 | la garantie de population : le cas de la question 1 |
| `equilibre.js` | 25 | 138 | les accesseurs des comptes, et `depenseMaximaleToutesVariantes`, que la question 1 fait déjà quitter le Python |
| `depenses.js`, `caracteristiques.js`, `frontiere.js`, `credits-ministeres.js`, `inventaire.js` | 30 | 174 | des tables du paquet, lues pour être affichées |
| `regimes.js`, `contexte.js`, `bilan.js` | 26 | 135 | des accesseurs de plus sur des objets que le simulateur lit aussi |
| six autres modules | 9 | 44 | de une à trois lignes par fonction |
| **total** | **187** | **1 001** | sur 54 583 lignes chargées, soit 1,8 % |

Hors la garantie, ce sont des lectures du paquet, que les notes 0005 et 0006
rangent en JavaScript : aucun calcul qu'une règle décide. Les figer
retirerait au plus 491 lignes, pour autant de blocs de plus dans le paquet
et dans sa fabrique.

## Dans le simulateur

Les appels du site qui ne dépendent pas du lecteur y pèsent 7 ms sur 2 172
tracés : des libellés de régimes et de la mise en forme.

À l'intérieur du moteur, les arguments des 163 fonctions les plus lourdes
ont été relevés à toute profondeur — 8 ms ou plus de temps cumulé, 5 000
appels au plus, les quatre cents premiers appels de chacune. Seule la mise
en tables du paquet ne dépend pas du lecteur : `Simulateur` et, sous lui,
`CatalogueRegimes`, `Regime`, `ValeursPoint`, `DonneesMacro`,
`ContributionsEmployeurPubliques`. Un `Simulateur` se bâtit en 27 ms la
première fois, 10 à 15 ensuite ; le rendu d'une carrière en bâtit neuf sous
onze réglages, seize sous les réglages par défaut, un par jeu de paramètres,
et `Contexte` les garde (`contexte.js:175`). Le catalogue des régimes ne
dépend que de `conventions_cor` et se rebâtit pourtant avec chacun, 5 ms
pièce : un partage possible, en JavaScript, de 45 à 80 ms sur un premier
rendu d'une seconde. Ce n'est pas un calcul à porter ailleurs : le paquet
est déjà ce que le Python a préparé, et ces classes ne font que l'indexer.

Deux fonctions paraissaient indépendantes du lecteur et ne le sont pas :
`pilote.pointFixe` et `moyenneAnnuelle` (`prelevements-historiques.js:138`)
reçoivent une fonction en argument, que l'empreinte ne distingue que par son
nom ; celle de `moyenneAnnuelle` porte les parts de la pension du lecteur.

## Ce qui est vérifié, ce qui est déduit

*Mesuré* : les temps de rendu des neuf pages, sans instrument, un premier
rendu et le suivant dans le même processus ; les appels de chaque page et ce
qu'ils atteignent ; les 187 fonctions et leurs lignes ; les arguments des 163
fonctions lourdes sous quatre lecteurs ; la construction d'un `Simulateur`.

*Vérifié en lisant le code* : ce que `rendre` passe à chaque page ; les deux
cas où le routeur recalcule ; le chargement d'un dossier à chaque changement
de page ; les deux faux indépendants.

*Limites.* Les temps sont ceux de node sur ce conteneur : un téléphone est
plus lent, et le navigateur charge d'abord le paquet, que rien ici ne mesure.
Deux carrières seulement, de salariés du privé : les 187 fonctions sont un
majorant, et les branches des autres régimes ne sont pas exercées. À
l'intérieur du moteur, une fonction légère, ou appelée plus de cinq mille
fois, n'a pas été relevée. Un objet de plus de trois mille valeurs n'a pas
d'empreinte : c'est le cas de l'objet qui porte la méthode — le simulateur,
le contexte, la carrière — pour 104 des 163 fonctions, les plus lourdes
comprises. Leurs autres arguments diffèrent d'un lecteur à l'autre, sauf à
298 appels sur 10 681, des lectures par nom de régime ou par date sur un
tel objet. Une fonction passée en argument, ou appelée par une table bâtie
au chargement du module, échappe à l'instrument.

## Ce que le propriétaire tranche

Rien de neuf. La seule décision que cette mesure touche est déjà posée : la
garantie de population, à la question 1
(`2026-11-12-question-1-la-zone-grise.md`), que le critère de la note 0006
enverrait au Python seul et que sa session recommande en JavaScript seul. Le
partage du catalogue des régimes entre les simulateurs est une économie
possible, hors de cette action.
