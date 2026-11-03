# Étape 2, les grilles de l'État d'avant le Noyau RH : lues au LEGI depuis les années 1990, rien avant 1990

**Le 3 novembre 2026 : les grilles de l'État que le LEGI garde sont entrées
dans le dépôt, à part de celles du Noyau RH, et certifiées : 484 textes, 1 795
grilles, 21 078 périodes d'échelons, dont 3 444 commencent avant 2005 et 1 152
avant 1995. Elles redonnent le noyau là où les deux couvrent le même corps — les
professeurs des écoles, certifiés et agrégés depuis 1990, les attachés depuis
1995 — et précèdent le noyau pour la catégorie C, dont les échelles du
1er avril 1998 sont, indice pour indice, celles de la territoriale. Avant 1990,
ni le LEGI ni le JORF de la DILA ne reproduisent les tableaux : les grilles des
instituteurs et des certifiés d'avant 1989 ne sont que dans le Journal officiel
imprimé.**

Demande : la session d'orchestration du 3 novembre 2026, file B, troisième
vague : « les grilles de l'État antérieures à ce que couvre le Noyau RH du
CISIRH (avant 1989 pour les enseignants, avant 2005 à 2011 pour les autres
corps), lues dans les textes officiels par l'index LEGI et JORF » ; pas de
site ; la question de la durée des échelons, posée au propriétaire, à ne pas
trancher.

- *Le récupérateur* (`scripts/fetch/dila_legi_grilles.py`, test
  `tests/test_grilles_etat_legi.py`). Un quatrième versant, l'État, écrit sous
  `data/reference/grilles/etat_legi/` : le dossier `etat` reste au noyau. Le
  versant se lit au titre — un cadre d'emplois, la police municipale, les
  sapeurs-pompiers professionnels, la Ville de Paris sont de la territoriale ;
  un hôpital, l'Assistance publique de l'hospitalière ; un ministère, l'État —,
  puis, quand le titre le tait, aux visas : l'arrêté du 11 mai 2007 « fixant
  l'échelonnement indiciaire des grades et emplois de la catégorie C » vise les
  décrets des fonctionnaires hospitaliers. Les fonctionnaires de La Poste et de
  France Télécom restent à l'État.
- *Ce que l'analyseur apprend*, pour tous les versants civils : les échelles
  annoncées par leur numéro d'ordre (« 1° En ce qui concerne l'échelle 1 »,
  « 2° … les autres échelles ») ; l'en-tête « CORPS, GRADES, CLASSES ET
  ÉCHELONS » ; la date écrite entre « applicable » et le groupe ; la note que le
  LEGI met en tête d'un article (« Conformément aux dispositions de… ») ; le
  second tableau d'un article, annoncé par sa propre phrase, qui ouvre un bloc
  et prend le nom écrit après « suit » ; la colonne datée en mots (« A compter
  de la date d'entrée en vigueur du présent arrêté ») ; la date qui ouvre la
  phrase (« I. ― A compter du 1er janvier 2015, l'échelonnement… »), qui date le
  tableau. Les militaires n'en lisent rien de plus : leurs fichiers sont
  identiques à l'octet.
- *Les chiffres de l'État.* 484 textes, dont 398 avec une grille lue ; 1 795
  grilles ; 21 078 périodes, dont 1 128 en lettre de hors-échelle ; 1 354
  versions d'articles lues, 380 non lues (97 valeurs hors des lignes, 70 sans
  échelon, 37 en caractères, 22 reclassements). Les périodes commencent dans les
  années 1970 pour 48 d'entre elles, 1980 pour 192, 1990 pour 2 042, 2000 pour
  2 799, 2010 pour 12 580, 2020 pour 3 417 ; la première, le 24 octobre 1970.
- *La certification.* `scripts/verifier_donnees.py` certifie le rang (21 071) et
  l'indice (19 946) de chaque période ; les 7 et 4 de colonne présumée passent
  au niveau `estimee`. Le journal ne reçoit que les traces des grilles.
- *Le recoupement* (mesure de la session, par des scripts qu'elle n'a pas
  versés). Des 1 795 grilles, 1 125 redonnent à une date au moins, indice pour
  indice, une grille du noyau ; 33 commencent avant elle (327 périodes) ; 670
  n'en ont aucune, dont 225 commencent avant 2005. Le test retient : les
  professeurs des écoles (arrêté du 22 août 1990) et les certifiés (arrêté du
  30 mai 1990) de classe normale, égaux au noyau en 1995 et 2005 ; les agrégés
  (même date), en 1990, 2000 et 2009 ; les attachés d'administration centrale
  (arrêté du 23 août 1995), égaux en 2000 et 2009 à la grille des attachés
  d'administration de recherche et de formation, quand le noyau ne date la leur
  que d'octobre 2011 ; les échelles 2 à 5 de la catégorie C au 1er avril 1998,
  égales à celles de la territoriale (décret n° 87-1108), quand le noyau ne date
  ses échelles de la catégorie C que du 1er novembre 2006.
- *Ce que les deux autres versants y gagnent.* Des textes que le titre ne
  rangeait nulle part : 22 à la territoriale (police municipale,
  sapeurs-pompiers professionnels, Ville de Paris, gardes champêtres…), 11 à
  l'hospitalière, dont les arrêtés du 11 mai 2007 et du 3 décembre 2008 de sa
  catégorie C, qui comblent en partie le trou de 2006 à 2014 que la note de la
  territoriale et de l'hospitalière signalait ; 5 401 périodes au lieu de 4 521,
  3 460 au lieu de 3 024. Dix-sept clés de grilles nettoyées (« l'échelle 1 »
  devient « échelle 1 », comme dans les versions suivantes). Aucune valeur
  publiée ne change de date ni d'indice, sauf deux corrections : l'arrêté du
  29 janvier 2014 de la catégorie C de l'hospitalière, dont l'article 2 lisait
  les échelles 4 et 5 comme une seule grille à deux dates et datait de
  février 2014 l'échelle 3 de 2015 (désormais au 1er janvier 2015 ; l'article 1er,
  ses valeurs de 2014, est lu, et les deux articles font deux grilles,
  « -article-1 » et « -article-2 », la seconde prenant le relais en 2015) ; et
  les moniteurs d'atelier, dont le texte dit « A compter du 1er août 1994 » quand
  la donnée datait leur grille de 1993.
- *Ce que la donnée ne dit pas.*
  - Avant 1990, les tableaux. Le JORF de la DILA garde 2 246 textes de grilles
    de l'État d'avant 1990, leur titre et un résumé, sans tableau ; de 1990 à
    2006, 719 articles renvoient au Journal officiel imprimé (« Vous pouvez
    consulter le tableau dans le JO… ») et 70 seulement portent le leur, dont 26
    pour des textes que le LEGI n'a pas (magistrats de l'ordre judiciaire en
    1993, emplois fonctionnels), non lus ici : le JORF date un texte de sa
    publication, non de son effet. Les instituteurs (arrêtés de 1961, 1964…) et
    les certifiés d'avant 1989 ne se liront que d'un poste, sur Légifrance.
  - Un texte abrogé sans le dire reste ouvert au LEGI : l'arrêté du
    1er avril 1998 des échelles 1 à 5 de l'État y paraît encore en vigueur, quand
    le décret n° 2005-1229 les a remplacées au 1er octobre 2005, par un arrêté
    du 29 septembre 2005 que seul le JORF cite, sans son tableau ; la carrière
    devra l'arrêter au 30 septembre 2005, et la catégorie C de l'État n'a pas
    de grille d'octobre 2005 à octobre 2006.
  - La police et la pénitentiaire avant 2005 : les décrets de classement
    indiciaire n'en donnent que les bornes, et l'arrêté du 28 octobre 1996 des
    corps de la police n'est au LEGI que par ses modifications ; les finances
    publiques, peu avant 2008.
  - Des libellés encore longs (144 de plus de 110 caractères), que l'analyseur
    n'a pas su séparer de leur phrase ; le chaînage, à venir, les rattachera.
  - Les durées d'échelon, que ces textes ne donnent pas.

*Ce que cette tâche change à la question des durées d'échelon.* Les grilles de
l'État couvrent désormais les années 1990 et 2000 de la plupart des corps, mais
sans leurs durées : le noyau ne les donne qu'à partir de ses propres dates, et
avant, elles sont dans les statuts de chaque corps, au LEGI. Les faire d'abord
vaudrait donc pour ces grilles anciennes aussi ; le chaînage et les
reclassements, eux, relieront les grilles du LEGI à celles du noyau. La question
reste au propriétaire.

*Pour les autres files.* Rien pour le site. Des fichiers partagés ont reçu des
lignes : `scripts/verifier_donnees.py` (quatre certifications),
`tests/test_donnees.py` (les quatre séries et leur fichier),
`data/derive/certification.json` (les traces des grilles seules ; la date de
quatre séries d'autres zones, que la certification avait rafraîchie, rendue),
`data/sources.yaml` (l'entrée `dila_legi_grilles`).

*Ce qui reste de l'action 158, étape 2.* Dans l'ordre de la file : le chaînage
et les reclassements, du LEGI au noyau compris ; les durées d'échelon ; les
tableaux que l'index aplatit, et les 26 du JORF ; le minimum de traitement ;
les grilles d'avant 1990, d'un poste.
