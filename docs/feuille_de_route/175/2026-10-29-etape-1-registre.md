# Étape 1 : le registre de la base de législation de la Cnav

**Le 29 octobre 2026, ce qui est fait.**

- *Le module commun*, `scripts/fetch/cnav_api.py` : l'adresse de l'API,
  l'en-tête des requêtes et la lecture d'une réponse déjà téléchargée — la
  liste entière de `/baremes` ou un seul barème, avec ou sans la marque
  d'ordre des octets, trois variantes jusque-là. Onze récupérateurs y passent :
  les dix de l'action et `cnav_revalorisation_salaires.py`, qui lit les
  circulaires sous `/Pdf/`. Relancés sur la base, les quatre qui écrivent un
  fichier versionné l'ont réécrit à l'octet près — le témoin des coefficients
  des salaires, sa date de récupération à part —, et les autres ont rendu leurs
  séries ; d'`ines.py`, seule la lecture des seuils de la CSG, Ines demandant R.
- *Le récupérateur de la base entière*, `scripts/fetch/cnav_legislation.py`,
  qui lit tout ce que servent les 25 routes que le script du site appelle :
  les collections, d'un appel chacune — barèmes, exposés, listes, les trois
  des fenêtres d'information (`/lexique`, `/exemple`,
  `/complementInformation`) et les avis de mise à jour (`/mises-a-jour`) — ;
  les deux menus, et les barèmes de chacune des 76 entrées du menu des barèmes
  (`/baremes/baremesByMenuId/<id>`, la seule route qui dise le thème d'un
  barème) ; les documents que les barèmes joignent, que le site sert hors de
  l'API (`Bareme/Pages/doc_communs/`), de page en page ; puis les références
  que tout cela lie, une à une, quatre à la fois, et celles qu'elles citent, de
  proche en proche. Avec `--chercher`, il mène aussi la recherche de la base
  (`/search/custom`), qui sert des références que rien ne lie : plafonnée à
  250 résultats par requête et sans compteur, elle se mène par année depuis
  1900, par mois de chaque année, par nature de texte et par mot du droit,
  1 792 requêtes en une dizaine de minutes. Ce que chaque référence cite,
  `citations.csv` le garde : c'est ce qui permet de relire la base sans
  redemander ce qui n'a pas changé. Une référence ne se relit que si le
  registre ne la porte pas, sans titre, ou si un objet qui la lie est neuf ou
  que sa date de modification dit changé (`--tout` les relit toutes) ; une
  lecture ordinaire prend trois minutes. La base a répondu 500 à `/expose`
  deux fois de suite, puis l'a servi : une route se redemande quatre fois, une
  référence deux, et en minuscules si elle est liée sous une majuscule.
- *Le registre*, `data/reference/legislation/cnav/`, un fichier par genre :
  386 barèmes (l'API en sert 397, onze deux fois à l'identique), 633 exposés,
  323 listes, 7 007 références, 394 fenêtres, 192 avis de mise à jour et 134
  documents joints ; 9 069 objets, et 11 721 citations entre références. Les
  références : celles que lient les objets de la base, celles qu'elles citent,
  et 2 509 que seule la recherche sert — des accords, des arrangements
  administratifs, des circulaires anciennes. Les PDF de `/Pdf/` sont des
  références à part entière, servies sous leur nom
  (`circulaire_cnav_2025_29_22122025.pdf`) : ce sont surtout les circulaires
  d'après 2015, dont les dix que lit `cnav_revalorisation_salaires.py`. Les
  fenêtres : 269 entrées du lexique, 86 compléments, 37 exemples, et deux que
  des objets lient sans que l'API les serve ; leur nature (`exemple`,
  `lexique`, `complement`), que leur nom ne dit pas (`ex_delai.aspx` est un
  complément), a sa colonne. Les avis, nommés de leur identifiant, disent
  quels barèmes et exposés ont changé, et selon quelle circulaire, avec le
  jour de la mise à jour. Les documents : 45 pages et 36 PDF que les barèmes
  joignent, et les pages qu'elles lient à leur tour — les tableaux des taux de
  change par pays, leur « vision globale », les assiettes maximales des
  indépendants, les coefficients d'avant 2013 —, nommés de leur chemin sous
  `doc_communs/`, avec la date que le site en donne. Le registre ne garde que
  des noms, des titres, des thèmes et des dates — celle de la version qui a
  reçu son sort, sauf pour une référence, dont il garde le jour du texte ;
  l'API ne date pas une liste. Une référence ou un document y reste quand plus
  rien ne le lie : la base le sert encore.
- *Les thèmes* : un barème prend l'entrée du menu qui le nomme, ou celle de la
  page d'accueil qui le lie (377 sur 386) ; un exposé, celle de son `menuId`
  (629 sur 633) ; une liste, une fenêtre, un document ou une référence, le
  premier niveau du thème de chaque objet qui le lie ; un avis, celui des
  barèmes et des exposés qu'il met à jour (146 sur 192). Une référence que
  seules d'autres références citent, ou que seule la recherche sert, n'en a
  pas : passé de citation en citation, le thème en donnait plus de cinq à
  1 637 références, et seize à un article de code que toute la base cite ;
  `citations.csv` dit qui la cite.
- *Au départ*, 37 objets sont `branche` : les 20 barèmes des neuf `cnav_*.py`
  qui nomment l'API, la page des coefficients des salaires et la page jointe
  dont `cnav_revalorisation_salaires_anciennes.py` lit les valeurs, les deux
  fiches jointes de la valeur du point RVB que lit
  `cnav_points_avant_1973.py`, les trois barèmes de la CSG de 2023 à 2025
  qu'`ines.py` compose année par année, et les dix PDF des coefficients des
  salaires, chacun avec la série versionnée qu'il nourrit — ou, pour le
  maximum de la réversion et le plafond de l'ASPA, que son contrôle garde. Le
  reste est `a_lire`.
- *Les tests*, `tests/test_cnav_legislation.py`, vingt et un cas, rapides : le
  module, le passage des onze récupérateurs par lui, la lecture des liens et
  des documents joints, les thèmes, la fermeture des références et ses
  racines, les fenêtres par leurs collections, les dates, la recherche, la
  règle d'inscription, la relecture, les reprises, la casse ; et le registre
  lui-même — aucun objet sans l'un des cinq sorts, un renvoi qui existe et que
  le dépôt versionne (la série et le script qui le nomme, le test, la fiche),
  ce que nomme le code d'un récupérateur toujours `branche` sur lui, chaque
  citation entre deux références du registre. Le registre est hors de
  l'empreinte de la mémoire des calculs (`memoire.HORS_DU_MODELE`) : un sort
  écrit ne refait pas le coût.

**Deux relectures, le même jour, à la question du propriétaire** — « On est
sûr d'avoir tout fini sur l'étape 1 ? », puis « Est-ce qu'on est sûr qu'on n'a
rien oublié maintenant ? ». La première, contre le texte de l'étape, a trouvé
dans le registre d'abord poussé (2 298 références, quatre genres) la page des
coefficients des salaires `a_lire` quand un récupérateur la lit, les 2 020
textes que les références citent, et les fenêtres d'information. La seconde,
contre les 25 routes que le script du site appelle, a trouvé les fenêtres que
rien ne lie (216, servies par leurs trois collections), les avis de mise à
jour, les documents joints, et les références que seule la recherche sert. Le
propriétaire a tranché chaque fois pour l'exhaustivité. Une troisième passe, à
son « Cherche encore », n'a plus rien trouvé dans la base : les onze pages de
l'application sont celles que le registre couvre ; la recherche, menée par
genre, sert 632 exposés, 386 barèmes et 194 listes, tous au registre ; aucune
adresse du site, dans tout ce qui a été lu — pages jointes et références
comprises —, ne mène à un objet qu'il n'a pas ; les 75 références que la base
nomme sans les servir ne le sont sous aucune forme, ni en PDF sous `/Pdf/` ;
deux images seulement portent un contenu, dans des fenêtres d'exemple ; le
champ `imageRef` est vide partout. Ce qui reste hors du registre, et
pourquoi : la zone libre de l'accueil (`/zone-libre`, la présentation du
site), `/documents`, vide, les routes de navigation des menus, et les scripts
de valeurs que chargent les pages jointes, qui font partie de leur page ; les
textes d'autres sites que la base cite — 6 016 liens vers Légifrance, 166 vers
le CLEISS —, que l'étape 4 lit dans l'objet qui les cite.

**Ce que la lecture a trouvé.** La recherche est près d'être épuisée, sans
preuve de l'être : les années et les mois servaient 6 131 références ;
soixante mots du droit en ont ajouté 36, soixante autres 7 encore. Vingt et un
liens ne mènent à aucun objet — quinze listes d'organismes de liaison
(`organisme_liaison_*_list.aspx`), servies vides par leur propre route, deux
barèmes, dont `smic_smig_smic_mayotte_bar.aspx`, trois exposés, dont
`portail.aspx`, qui répondent 500. 78 objets nommés ne sont pas servis :
75 références, dont `CR_CN_2006006_13012006.aspx` et des PDF des accords avec
Andorre (`Andorre_SE_130-04.pdf`…), deux fenêtres, et un PDF joint au nom
accentué (`rci_valeur_achat_point_commerçant_avant_2013.pdf`), sous aucun
codage. Des références sont liées sous une majuscule fautive
(« Circulaire_cnav_… ») : l'API ne les sert qu'en minuscules, et le registre
les porte sous le nom servi. Dix-neuf références du premier rang ont une date
que leur titre contredit — la circulaire Unedic 97/18 « du 07/11/1997 », datée
de 1966 ; la circulaire RSI 2011/022 « du 30/11/2011 », de 2001 — : le
registre garde la date de l'API, et le titre la corrige. Une liste porte deux
contenus sous un nom (`periode_guerre_periode_guerre_list.aspx`, ses deux
titres joints) ; 24 listes ne sont liées par rien ; un exposé et une entrée du
lexique ne sont que des essais (`Test-bannière-Exposé.aspx`,
`TestVAlexique.aspx`). La suite complète de GitHub a rougi une fois, sur
`test_aucune_page_ne_se_decale_en_se_chargeant`, que l'étape ne touche pas et
qui passe ici : l'échec isolé, à pleine charge, que décrit la note de
l'action 174 du 27 octobre.

**Ce qui reste**, aux étapes 2 à 6, qui se mènent en parallèle. Les sorts : le
registre se lit par `grep ',a_lire,'` dans le fichier du genre, au thème de son
étape — les références sans thème par `citations.csv`, depuis celles qui les
citent —, et un sort s'y écrit à la main ; `scripts/fetch/cnav_legislation.py`
le garde. Pour l'étape 4, menée dans l'ordre de thèmes qu'elle propose, les 37
exemples des fenêtres. Pour l'étape 6, que le propriétaire a ouverte le même
jour, les 4 663 références sans thème : 2 158 textes publiés, que la liste de
contrôle des textes et l'index LEGI confrontent ; 2 228 circulaires, lettres,
instructions et notes, par période ; 107 accords ; 96 autres textes ; 74 que la
base nomme sans les servir. Pour l'étape 5 : la
comparaison des dates du registre à la base, que le récupérateur imprime déjà
(« modifiés ») ; les avis de mise à jour, qui datent chaque changement ; et la
recherche (`--chercher`), à relancer pour les références que rien ne lie
encore — la circulaire 2026-17 du 12 juin 2026, que rien ne liait, est entrée
par elle.
