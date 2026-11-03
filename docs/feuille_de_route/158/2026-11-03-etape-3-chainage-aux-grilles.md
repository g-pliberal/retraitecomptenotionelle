# Étape 3, le chaînage : chaque durée d'échelon et chaque reclassement rattaché à sa grille, à son corps et à sa période, ou déclaré

**Le 3 novembre 2026 : des 1 675 grades des 778 tableaux de durées, 498 sont
rattachés à une grille du dépôt, avec leur corps, leur période et la citation
qui le prouve ; les 1 177 autres sont déclarés, chacun avec sa raison. Des 862
groupes des 450 tableaux de reclassement, 18 le sont, tous à l'État ; 844 sont
déclarés. Rien ne se rattache sur le seul libellé : un texte d'échelonnement
commun à plusieurs corps vise des statuts dont les grades portent le même nom.
`a_lire_au_jorf.csv` dresse, sans les lire, les 264 cas (137 textes à tableau
abîmé au LEGI, 127 où il y manque peut-être) qu'une lecture au Journal
officiel viserait.**

Demande : la session d'orchestration de la vague 6, file B3, le 3 novembre
2026 : rattacher les durées (778 tableaux, 14 521 lignes) et les
reclassements (450 tableaux), entrés, certifiés et relus trois fois (R-B2-ter),
chacun à la grille, au corps et à la période qu'il régit ; déclarer, avec sa
raison, ce que le texte ne rend pas certain ; dresser la liste des corps dont
un tableau manque ou est abîmé au LEGI ; ne pas toucher au site. Exigence du
propriétaire, le même jour : aucune erreur, tout prouvé par écrit, jamais de
mémoire.

- *La source.* L'index LEGI publié (`dila_index.py legi --recuperer`, dump du
  13 juillet 2025, à jour de l'incrément 20261102-213929, celui de B2-ter et
  de R-B2-ter), récupéré sans reconstruction ; les visas de chaque texte de
  grille (la notice LEGITEXT, qui porte les visas et les signatures, sans les
  articles) et le texte des articles qui fixent les grilles. Le Noyau RH du
  CISIRH (juillet 2026), déjà au dépôt (`grilles/etat/`). Le JORF n'a pas été
  ouvert : rien de ce qui suit n'en dépend.
- *Le script* (`scripts/fetch/dila_legi_chainage.py`, trois secondes). Il ne
  lit ni durée ni indice : il relie. Il écrit sous
  `data/reference/grilles/chainage/` `durees.csv`, `reclassements.csv` et
  `a_lire_au_jorf.csv`.

## Ce qui prouve un rattachement

*Le piège, vu dans le texte.* Le décret n° 95-370 (agriculture), art. 25
(LEGIARTI000034773631, du 1er septembre 2017 au 1er avril 2025 au dépôt),
écrit : « Ingénieur de recherche hors classe : Echelon spécial 4e échelon -
3e échelon 3 ans 2e échelon 3 ans 1er échelon 2 ans ». Le décret n° 2017-171
(LEGITEXT000034028389), « modifiant et fixant l'échelonnement indiciaire
afférent à divers corps et emplois de catégorie A de la fonction publique de
l'Etat », vise « le décret n° 95-370 du 6 avril 1995 modifié fixant les
dispositions statutaires applicables aux ingénieurs et aux personnels
techniques de formation et de recherche du ministère de l'agriculture et de la
pêche », et a une grille « Ingénieur de recherche hors classe » ; mais son
art. 116 (LEGIARTI000034028850) la fixe pour « le corps des ingénieurs de
recherche régi par le décret du 31 décembre 1985 susvisé » : un autre corps,
et quatre échelons (« 4 HEA HEA 3 1021 1027 2 906 912 1 807 813 »), non cinq.
Le même libellé, le même visa, une autre grille : le libellé et le visa ne
suffisent pas.

*Les conditions*, toutes ensemble (docstring du script) :

1. *Un texte qui relie le statut à la grille.* Au LEGI, le texte
   d'échelonnement vise le statut par son numéro, et : soit il ne vise, parmi
   les décrets statutaires, que lui (lien `visa`) ; soit l'article qui fixe la
   grille nomme le statut, à chacune de ses versions de la période, par son
   numéro ou par sa date, la date seulement si aucun autre décret de ses visas
   ne la porte (lien `article`). Au Noyau RH, le corps cite le statut parmi ses
   textes (lien `noyau`). Les lois statutaires générales (n° 84-16, 84-53…) et
   les décrets de rémunération ne comptent pas parmi les décrets statutaires.
2. *Le même libellé*, après `normaliser` : sans accents, ni casse, ni
   ponctuation, au singulier (« principaux » → « principal »), sans le
   « (article N) » que le lecteur des grilles ajoute ; au noyau, sans « de
   l'État ».
3. *Une période commune* : l'intersection du tableau (fin exclue) et de la
   grille ou du grade (fin incluse).
4. *Les mêmes échelons.* Au LEGI, les rangs du tableau sont ceux de la grille
   pendant la période, stagiaire et élève mis à part. Au noyau, le rang ordonne
   sans numéroter : la grille 00422 des gardiens de la paix met au rang 1 un
   échelon « provisoire », au 2 l'élève, au 3 le stagiaire, au 4 le 1er
   échelon (lignes de `grilles/etat/echelons.csv`) ; c'est donc le nombre
   d'échelons, élève, stagiaire et provisoires mis à part, qui se compare.
5. *Une seule grille à la fois* pour un grade d'un tableau, un seul corps au
   noyau.

Deux versions d'un même article que le LEGI fait valoir ensemble (colonne
`chevauche`, trois paires) ne se rattachent pas sur leur recouvrement : le
chaînage ne choisit pas, et le déclare (n° 91-868, art. 7, du 1er janvier au
23 septembre 2017, quatre grades). L'en-tête de `durees/tableaux.csv` et la
documentation du lecteur des durées, qui disaient « le rattachement aux
grilles choisit », le disent.

*Les reclassements*, à l'État seulement, par le Noyau RH : la date est celle
que le lecteur a lue (`effet`, 87 groupes), ou celle qui ouvre la phrase
(« Au 1er juillet 2011, les membres… », 92 groupes), que le lecteur ne retient
pas ; le corps, celui que le noyau rattache au texte du tableau ou au statut
que la phrase nomme par son numéro ; le libellé du tableau, où
l'aplatissement colle le grade d'origine et le grade d'accueil, se coupe d'une
seule façon en deux grades de ce corps (ou des corps qu'il absorbe), en vigueur
la veille et le jour ; les échelons d'origine et d'accueil sont parmi ceux de
leurs grilles, comptés comme au point 4.

## Les valeurs des tests, posées à la main

`tests/test_chainage_grilles.py`, 11 tests, vus rouges (le module manquait),
puis le test du reclassement rouge sur une vraie différence (le rang du noyau,
point 4 ci-dessus), puis verts.

1. *Le visa, à la territoriale.* Décret n° 2016-201 (LEGITEXT000032117021),
   art. 24 (LEGIARTI000032117092), du 1er mars 2016 au 1er janvier 2017 :
   « Ingénieur hors classe Echelon spécial - - 5e échelon - - 4e échelon 2 ans
   et 9 mois 3 ans 3e échelon 2 ans et 3 mois 2 ans et 6 mois 2e échelon 2 ans
   et 3 mois 2 ans et 6 mois 1er échelon 1 an et 9 mois 2 ans » : les échelons
   1 à 5 et le spécial, six. Décret n° 2016-203 (LEGITEXT000032116807),
   « portant échelonnement indiciaire applicable aux ingénieurs territoriaux » :
   ses décrets statutaires visés se réduisent à un, « Vu le décret n° 2016-201
   du 26 février 2016 portant statut particulier du cadre d'emplois des
   ingénieurs territoriaux » (l'autre visa statutaire est la loi n° 84-53) ; son
   art. 1 (LEGIARTI000032116817), du 1er mars 2016 au 1er janvier 2017 :
   « Ingénieur hors classe Echelon spécial HEA 5e échelon 1015 4e échelon 985
   3e échelon 946 2e échelon 920 1er échelon 871 » : six. Période :
   [2016-03-01, 2017-01-01) ∩ [2016-03-01, en vigueur] = [2016-03-01,
   2017-01-01). Attendu : `territoriale`, LEGITEXT000032116807,
   `ingenieur-hors-classe`, du 2016-03-01 au 2017-01-01, lien `visa`.
2. *Le noyau, à l'État.* Décret n° 90-680 (LEGITEXT000006076298), art. 24
   (LEGIARTI000034948501), « Conformément à l'article 11 du décret
   n° 2017-1736 du 21 décembre 2017, les présentes dispositions entrent en
   vigueur le 1er janvier 2021 », au dépôt du 1er janvier 2021 au 6 août 2023
   (avec la version qui le redit, LEGIARTI000044268708) : « Professeur des
   écoles de classe exceptionnelle Spécial ― 4e échelon ― 3e échelon 2 ans
   6 mois 2e échelon 2 ans 1er échelon 2 ans » : cinq. Noyau RH : texte 160,
   « Décret n° 90-680 du 1er août 1990 relatif au statut particulier des
   professeurs des écoles », origine du corps 00021 et du grade 04235,
   « Professeur des écoles de classe exceptionnelle », grille 03313, depuis
   le 1er septembre 2017 ; la grille a, pendant la période, les rangs 1 à 4 et
   le 5 (« exceptionnel », lettre A, jusqu'au 6 août 2023 ; puis sans nature) :
   cinq. Période : [2021-01-01, 2023-08-06) ∩ [2017-09-01, en vigueur]. Le
   noyau y écrit d'ailleurs les durées du tableau : 24, 24, 30 mois aux rangs
   1 à 3, 0 au rang 4 jusqu'au 5 août 2023.
3. *Le texte commun* : le piège ci-dessus ; attendu, aucun rattachement du
   n° 95-370 à la grille de LEGITEXT000034028389. Il est déclaré : « le texte
   LEGITEXT000034028389 vise 65 décrets statutaires (2001-1038, 2001-1174,
   2002-262, 2002-53, 2002-853, …) et l'article de sa grille
   ingenieur-de-recherche-hors-classe ne nomme pas le n° 95-370 ».
4. *Le reclassement.* Décret n° 2004-1439, art. 23-1 (LEGIARTI000023734900) :
   « Au 1er juillet 2011, les membres du corps d'encadrement et d'application
   de la police nationale sont reclassés conformément au tableau de
   correspondance suivant : […] Gardien de la paix Gardien de la paix Echelon
   exceptionnel 12e échelon […] 1er échelon 1er échelon Ancienneté acquise » :
   à l'origine, les échelons 1 à 11 et l'exceptionnel (douze), à l'accueil les
   échelons 1 à 12. Noyau RH : texte 296 (n° 2004-1439), origine du grade
   02780 « Gardien de la paix », corps 00172 ; sa version jusqu'au 30 juin 2011
   a la grille 00422 (rangs 4 à 14 et 15 « exceptionnel », élève, stagiaire et
   provisoire mis à part : douze), celle du 1er juillet 2011 la grille 02783.
   Attendu : date 2011-07-01 (lue dans la phrase), corps 00172, 02780/00422
   → 02780/02783.
5. *Le tableau abîmé.* Décret n° 96-1113, art. 14 (LEGIARTI000042571828), rouvert
   ici : « Professeur technique hors classe 7e échelon - 6e échelon 3 ans 4e
   échelon 2 ans 6 mois » : le 5e manque (B2-ter l'a prouvé au JORF). Attendu
   dans `a_lire_au_jorf.csv`, cas `abime`.
6. *Les règles* : `normaliser`, `nomme` (l'art. 116 du n° 2017-171 nomme « le
   décret du 31 décembre 1985 », non le n° 95-370), `date_de_la_phrase` (une
   date au milieu de la phrase est celle d'un texte cité) ; et la totalité :
   chaque grade de chaque tableau est rattaché ou déclaré, aucun rattachement
   ne couvre un chevauchement.

*Contre-lecture d'un échantillon* (tirage au hasard, graine 20261103, quatre
liens `article`), chaque article rouvert : n° 97-511 → LEGIARTI000036490376,
« aux attachés économiques régis par le décret du 21 mai 1997 susvisé » ;
n° 2003-770 → LEGIARTI000036489986, « membres du corps de l'inspection du
travail régis par le décret du 20 août 2003 susvisé » ; n° 2007-400 →
LEGIARTI000035645170, « au corps de catégorie A régi par le décret n° 2007-400
du 22 mars 2007 susvisé » ; n° 2005-1204 → LEGIARTI000019568454, l'arrêté du
26 septembre 2005 « fixant l'échelonnement indiciaire applicable au corps des
techniciens de police technique et scientifique de la police nationale », qui
nomme le n° 2005-1204 dans une note du LEGI et dans un renvoi (« dans les
conditions prévues par le décret n° 2005-1204 ») : le rattachement est juste,
l'arrêté étant propre à ce corps, mais la preuve tient à un renvoi ; une
relecture dira si la règle doit exiger que la phrase qui annonce la grille
nomme le statut.

## Les comptes

| | Grades de tableaux | Rattachés | Déclarés seulement |
|---|---|---|---|
| Durées, État | 1 018 | 277 | 741 |
| Durées, territoriale | 352 | 164 | 188 |
| Durées, hospitalière | 186 | 41 | 145 |
| Durées, militaires | 119 | 16 | 103 |
| Durées, ensemble | 1 675 | 498 | 1 177 |
| Reclassements | 862 | 18 | 844 |

218 des 778 tableaux de durées ont au moins un grade rattaché. Les 573 lignes
rattachées : 153 au noyau (27 corps, 76 grilles), 154 et 42 aux grilles de
l'État au LEGI (lien `article`, `visa`), 45 et 119 à la territoriale, 11 et 33 à
l'hospitalière, 16 aux militaires (`article`) ; 261 grilles du LEGI en tout.

*Pourquoi les autres sont déclarés* (durées ; la raison la plus avancée) :
aucune grille des textes qui visent le statut, ni aucun grade du noyau, ne
porte le libellé (560) ; le tableau ne nomme pas le grade de ses lignes, groupe
vide (239) ; aucun texte de grille ne vise le statut, ni le noyau ne le cite
(138) ; le libellé est celui d'une grille, mais à d'autres dates (100) ; les
échelons diffèrent (75) ; texte commun, l'article ne nomme pas le statut (40) ;
plusieurs grilles ou plusieurs corps aux mêmes dates (25). Reclassements : la
phrase n'écrit pas la date (398, voir plus bas) ; hors de l'État (220) ; groupe
vide (124) ; le libellé ne se coupe pas en deux grades du corps (66) ; aucun
corps du noyau (34) ; échelons (1) ; plusieurs coupes (1).

## Ce que le texte ne tranche pas, ou que la donnée ne dit pas

- *La date d'un reclassement sans date écrite.* Le lecteur des reclassements
  prend alors l'entrée en vigueur de l'article (`debut`). Elle n'est pas
  prouvée : le décret n° 2017-786 (LEGIARTI000034750747) reclasse « Au
  1er septembre 2017 » par un article que le LEGI fait valoir dès le 8 mai 2017,
  et le lecteur ne lit pas cette date, qui ouvre la phrase (sa règle veut
  « reclassés » ou « intégrés » à un mot près après la date). Le chaînage la lit ; sans date écrite, il
  déclare (398 groupes). Le lecteur est à reprendre sur ce point.
- *Les grades nommés autrement.* Un statut écrit « Premier grade : classe
  normale », la grille « Grade de classe normale » ; le lecteur des grilles
  garde des en-têtes (« TABLEAU III GRADE Technicien de classe normale »).
  Aucune équivalence n'est devinée : déclaré.
- *Les reclassements de la territoriale et de l'hospitalière* : leurs grilles
  ne sont qu'au LEGI, dont les libellés ne se coupent pas sans deviner.
- *Le cas `manque` de la liste* mesure un écart, non un manque prouvé : le
  texte vaut au LEGI plus de trois mois avant son premier tableau de durées.
  Les durées ont pu être écrites ailleurs : les statuts des professeurs des
  écoles (n° 90-680), certifiés (n° 72-581), agrégés (n° 72-580), d'EPS
  (n° 80-627) et de lycée professionnel (n° 92-1189) n'ont de tableau qu'à
  partir du 1er septembre 2017, quand le Noyau RH porte, pour la classe
  normale des professeurs des écoles, trois durées avant 2017 (note de
  l'étape 1).
- *Le simulateur ne propose aucun corps.* Le formulaire n'a pas encore son
  champ (étape 4 de l'action) : la liste vaut pour tous les statuts du dépôt.
  Parmi les corps les plus nombreux que l'étape 1 nomme, elle porte, au titre
  du tableau abîmé : les agents de maîtrise territoriaux (n° 88-547, dessiné en
  caractères ; n° 2005-1484, en fiches), les attachés territoriaux
  (n° 87-1099, dessiné), les rédacteurs territoriaux (n° 87-1105, dessiné),
  les techniciens territoriaux (n° 88-549, dessiné), les infirmiers
  territoriaux (n° 92-861, dessiné), les adjoints techniques des
  établissements d'enseignement agricole publics (n° 94-955, fiches) ; au titre de l'écart, les cinq corps enseignants
  ci-dessus, les attachés territoriaux et les agents de maîtrise territoriaux,
  les infirmiers de l'hospitalière (n° 88-1077).

## Ce qui n'a pas été vérifié, ce qui reste

- Les 498 rattachements ne sont pas relus un à un : quatre liens `article`
  l'ont été (ci-dessus) ; les liens `visa` et `noyau` reposent sur la règle et
  sur les tests 1, 2 et 4. Une relecture indépendante, contre les sources,
  suit.
- Ni le JORF ni les tableaux refusés n'ont été ouverts ; la liste ne dit pas
  ce qu'ils contiennent.
- La carrière ne se déroule pas encore de bout en bout : 1 177 grades de
  tableaux sont déclarés, et les reclassements de la territoriale et de
  l'hospitalière ne sont pas rattachés. Pour en rattacher davantage sans
  deviner : lire la date du reclassement qui ouvre la phrase dans le lecteur
  des reclassements ; lire le grade écrit avant l'en-tête (groupe vide) ;
  ôter des libellés de grilles les en-têtes que le lecteur des grilles garde ;
  puis relire ce qui reste à la main.

*Pour les autres files.* Rien pour le site, ni pour le paquet : ni le modèle
ni son portage ne lisent `grilles/`. Des fichiers partagés ont reçu des
lignes : `data/sources.yaml` (l'entrée `dila_legi_chainage`, et une phrase de
celle des durées).
