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
- *Le récupérateur de la base entière*, `scripts/fetch/cnav_legislation.py` :
  les trois collections, les deux menus, les barèmes de chacune des 76 entrées
  du menu des barèmes (`/baremes/baremesByMenuId/<id>`, la seule route qui
  dise le thème d'un barème), les fenêtres d'information que ses objets
  ouvrent (`#/infosupp/`, `/main/findPopupDetailsByFileLeafRef/<nom>`), relues
  chaque fois, puis les références qu'ils lient, une à une, quatre à la fois,
  et celles que ces références citent, de proche en proche, sur quatre rangs
  de plus. Ce que chaque référence cite, `citations.csv` le garde : c'est ce
  qui permet de relire la base sans redemander ce qui n'a pas changé. Une
  référence ne se relit que si le registre ne la porte pas, sans titre, ou si
  un objet qui la lie est neuf ou que sa date de modification dit changé
  (`--tout` les relit toutes). La lecture entière a pris dix-huit minutes ; la
  suivante, 2 min 34 s, n'a redemandé que les 64 références sans titre, celles
  que l'API ne sert pas. Le même jour, la base a répondu 500 à `/expose` deux
  fois de suite, puis l'a servi : une route se redemande quatre fois, une
  référence deux, et en minuscules si elle est liée sous une majuscule.
- *Le registre*, `data/reference/legislation/cnav/`, un fichier par genre :
  386 barèmes (l'API en sert 397, onze deux fois à l'identique), 633 exposés,
  323 listes, 4 331 références et 178 fenêtres ; 5 851 objets, et 8 956
  citations entre références. Les références : 2 312 que lient les
  collections et les fenêtres, 2 019 que citent les références seules ; 3 567
  que la route du site ouvre, 764 PDF de `/Pdf/`. Les PDF sont des références
  à part entière : l'API les sert sous leur nom
  (`circulaire_cnav_2025_29_22122025.pdf`), et aucun ne porte le nom d'une
  référence de la route ; ce sont surtout les circulaires d'après 2015, dont
  les dix que lit `cnav_revalorisation_salaires.py`. Les fenêtres : 91 entrées
  du lexique, 57 compléments, 28 exemples, et deux que l'API ne sert pas ; leur
  nature (`exemple`, `lexique`, `complement`), que leur nom ne dit pas
  (`ex_delai.aspx` est un complément), a sa colonne. Le registre ne garde que
  des noms, des titres, des thèmes et des dates — celle de modification d'un
  barème, d'un exposé ou d'une fenêtre, de la version qui a reçu son sort,
  celle du texte d'une référence ; l'API ne date pas une liste.
- *Les thèmes* : un barème prend l'entrée du menu qui le nomme, ou celle de la
  page d'accueil qui le lie (377 sur 386) ; un exposé, celle de son `menuId`
  (629 sur 633) ; une liste, une fenêtre ou une référence, le premier niveau
  du thème de chaque objet qui la lie. Une référence que seules d'autres
  références citent n'en a pas (2 026) : passé de citation en citation, le
  thème en donnait plus de cinq à 1 637 références, et seize à un article de
  code que toute la base cite ; `citations.csv` dit qui la cite.
- *Au départ*, 34 objets sont `branche` : les 20 barèmes des neuf `cnav_*.py`
  qui nomment l'API, la page des coefficients des salaires dont
  `cnav_revalorisation_salaires_anciennes.py` lit le fichier, les trois
  barèmes de la CSG de 2023 à 2025 qu'`ines.py` compose année par année, et les
  dix PDF des coefficients des salaires, chacun avec la série versionnée qu'il
  nourrit — ou, pour le maximum de la réversion et le plafond de l'ASPA, que
  son contrôle garde. Le reste est `a_lire`.
- *Les tests*, `tests/test_cnav_legislation.py`, dix-sept cas, rapides : le
  module, le passage des onze récupérateurs par lui, la lecture des liens, les
  thèmes, la fermeture des références, la nature des fenêtres, les dates, la
  règle d'inscription, la relecture, les reprises, la casse ; et le registre
  lui-même — aucun objet sans l'un des cinq sorts, un renvoi qui existe et que
  le dépôt versionne (la série et le script qui le nomme, le test, la fiche),
  ce que nomme le code d'un récupérateur toujours `branche` sur lui, chaque
  citation entre deux références du registre. Le registre est hors de
  l'empreinte de la mémoire des calculs (`memoire.HORS_DU_MODELE`) : un sort
  écrit ne refait pas le coût.

**Le même jour, à la question du propriétaire** — « On est sûr d'avoir tout
fini sur l'étape 1 ? » —, une relecture de l'étape contre son texte a trouvé
trois manques dans le registre d'abord poussé (2 298 références, quatre genres,
33 `branche`). La page des coefficients des salaires que lit
`cnav_revalorisation_salaires_anciennes.py` était `a_lire` : elle est
`branche`, et le script la nomme. Les références citaient 2 020 autres textes,
dont 264 circulaires et 148 lettres, que le registre ne suivait pas ; et les
fenêtres d'information, dont les exemples, n'y étaient pas. Le propriétaire a
tranché : toutes les références, de proche en proche, et les fenêtres. Un
renvoi sous `data/brut/`, que GitHub ne verrait pas, est désormais refusé.

**Ce que la lecture a trouvé.** Vingt liens ne mènent à aucun objet : quinze
listes d'organismes de liaison (`organisme_liaison_*_list.aspx`), deux
barèmes, dont `smic_smig_smic_mayotte_bar.aspx`, trois exposés, dont
`portail.aspx`. 66 objets liés ne sont pas servis : 64 références, dont
`CR_CN_2006006_13012006.aspx` et des PDF des accords avec Andorre
(`Andorre_SE_130-04.pdf`…), et deux fenêtres. Des références sont liées sous
une majuscule fautive (« Circulaire_cnav_… », quatre au premier rang) : l'API
ne les sert qu'en minuscules, et le registre les porte sous le nom servi.
Dix-neuf références
du premier rang ont une date que leur titre contredit — la circulaire Unedic
97/18 « du 07/11/1997 », datée de 1966 ; la circulaire RSI 2011/022 « du
30/11/2011 », de 2001 — : le registre garde la date de l'API, et le titre la
corrige. Une liste porte deux contenus sous un nom
(`periode_guerre_periode_guerre_list.aspx`, ses deux titres joints) ; 24
listes ne sont liées par rien, et un exposé n'est qu'un essai de bannière
(`Test-bannière-Exposé.aspx`, « Transverse > Crise Covid 19 »).

**Ce qui reste**, aux étapes 2 à 5, qui se mènent en parallèle. Les sorts : le
registre se lit par `grep ',a_lire,'` dans le fichier du genre, au thème de son
étape — les références sans thème par `citations.csv`, depuis celles qui les
citent —, et un sort s'y écrit à la main ; `scripts/fetch/cnav_legislation.py`
le garde. Pour l'étape 4, les 28 exemples des fenêtres. Pour l'étape 5 : les
circulaires que rien ne lie encore, qui n'entrent au registre que liées — des
quatorze dernières (`/reference/dernieresCirculaires/`), une seule, la
2026-17 du 12 juin 2026 — ; et la comparaison des dates du registre à la base,
que le récupérateur imprime déjà (« modifiés »).
