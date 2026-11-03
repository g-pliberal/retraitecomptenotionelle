# Retouches de la relecture R-M2-bis : une empreinte, un commentaire, un témoin de page

**Le 3 novembre 2026, file M2-ter.** La relecture R-M2-bis
(`2026-11-03-relecture-corrections-r-m2.md`, b5cbc57) jugeait conforme le
travail de M2-bis (cc55cdd et 06e2e9a, note
`2026-11-03-corrections-de-la-relecture-r-m2.md`), et relevait trois écarts
faibles, de documentation. Chacun est revérifié ici, aux objets du dépôt, chez
GitHub et dans le code ; aucune règle, aucune donnée, aucune valeur attendue ne
change.

## 1. Les deux empreintes : l'une morte, l'autre non

- **8f5447b n'existe pas.** `git cat-file -t` ne la trouve pas, ni dans le
  clone approfondi à 619 commits de `main` (`git fetch --deepen=300`), ni chez
  GitHub (`get_commit` : « No commit found for SHA: 8f5447b »). *Erratum* : là
  où la note de M2-bis écrit « corrigé (8f5447b) » (titre du § 1) et où son
  entrée du journal de veille écrit « dans les deux moteurs (8f5447b) »
  (`2026-11-03-action-177-corrections-de-la-relecture-r-m2.yaml`, `trouve`),
  lire **cc55cdd** (cc55cdd38453), « Action 177 : le conjoint collaborateur à
  l'option cotise au RCO sur l'avant-dernière année », le commit publié qui
  porte la règle dans les deux moteurs et son test.
- **e24714d existe**, contrairement à ce que dit R-M2-bis : e24714d123e6,
  « Action 161 : le levier du jumeau réservé aux confrontations, qu'un test
  tient », du 3 novembre 2026 à 05:00 UTC, ancêtre de `main`
  (`git merge-base --is-ancestor`), et GitHub le sert. Il précède de
  29 commits eab4dae, parent de f716130 (« Action 177, étape 9 : le RCO des
  artisans cotise sur l'avant-dernière année ») : il est bien « avant le
  travail ». Il est à 67 commits de b5cbc57,
  hors d'un clone superficiel de 50 commits, comme celui qu'une session reçoit
  (`.git/shallow`) ; d'où, sans doute, le verdict de la relecture. Son témoin
  des simulations est le même objet que celui d'eab4dae (blob b8d31778a2f7 aux
  deux) : la mesure du § 3 de M2-bis, « sur les témoins de e24714d (avant le
  travail) », est exacte telle qu'écrite, et eab4dae donne les mêmes chiffres.
  Rien à corriger.

*Le régime.* Les notes de `docs/feuille_de_route/<action>/` sont des récits
(`data/reference/prose/zones.yaml`, en tête de la feuille de route), vivantes
tant que leur action est ouverte ; mais un récit ne se réécrit pas
(`docs/fraicheur.md`, CLAUDE.md, « Rien ne se perd »), et
`scripts/conservation.py --depuis` exige chaque paragraphe à l'identique.
L'empreinte n'est donc pas corrigée en place : l'erratum est ici, avec un seul
renvoi, un paragraphe daté ajouté à la fin de la note de M2-bis, sans rien
réécrire, comme M2-bis l'avait fait dans la note de l'étape 9. L'entrée du
journal de veille n'est pas touchée.

## 2. Le commentaire de `tests/test_cout.py`

« la correction ne touche que les années d'avant 2009 » était inexact. Ce que
disent la fiche et le code :

- la fiche `assiette_rco_independants` : l'avant-dernière année jusqu'aux
  cotisations de 2008 (« depuis les revenus de 2009, sur celui de l'année »),
  la cotisation additionnelle de 0,10 % « due de 1985 à 1996 », et le forfait
  de l'artisan qui commence, le tiers puis la moitié du plafond, « jusqu'en
  2011 » (version `sans_forfait_2012` : le décret n° 2011-2038, article 3,
  JORFARTI000025055800, supprime ces alinéas de D. 635-7 au 1er janvier 2012) ;
- les données : `assiette_de_debut: {artisan: [3, 2]}` dans chaque période du
  RCO jusqu'à celle de 2010 à 2011 (`rco_artisans.yaml`), aucune dans
  `nric.yaml`, le forfait du commerçant restant déclaré ; le code
  (`droit/acquerir.py`) l'applique aux deux premières années d'exercice
  (`annees_deja_exercees`) ;
- la grille du coût : les générations de 1880 à 2020, de cinq en cinq
  (`cout.py`, `range(PREMIERE_GENERATION, DERNIERE_GENERATION + 1,
  PAS_GENERATIONS)`), l'artisan entré à 24 ans (`castypes.py`,
  `age_debut=24`). Celui de 1985 commence en 2009, au forfait en 2009 et 2010 ;
  celui de 1980 en 2004, avant 2009 ; celui de 1990 en 2014, après les
  forfaits.

La phrase dit désormais : « la correction touche pour l'essentiel les années
d'avant 2009 (l'avant-dernière année jusqu'en 2008, le 0,10 % de 1985 à 1996),
qui pèsent dans les pensions servies au départ bien plus qu'en 2070 ; les
forfaits de début valent jusqu'en 2011, et la grille en sert encore à
l'artisan né en 1985, qui commence en 2009 [...] : au forfait en 2009 et 2010,
sa pension pèse à l'horizon, non au départ ». Le test, ses valeurs et ses deux
tolérances (9 et 12 %) ne changent pas.

*Une remarque, non retouchée.* La phrase voisine, de l'étape 9 (c48cd2c), dit
que la correction « ôte de 0,1 à 2,3 % à la pension des artisans et des
commerçants d'avant 2009 » ; l'effet de la fiche ajoute « sauf l'artisane qui
commence sous le tiers du plafond, que le forfait relève ». Hors des trois
écarts relevés, laissée à la session qui reprendra l'action.

## 3. Le témoin de page que la note de M2-bis ne nommait pas

Entre cc55cdd^ et cc55cdd, `tests/temoins/pages.json` change 38 lignes, toutes
dans l'entrée `simuler_conjoint_collaborateur` (de la ligne 44362 à la 45450 ;
l'entrée va de la 42497 à la 45492) : aucune autre page ne bouge, et rien n'y
a bougé depuis (`git diff cc55cdd origin/main`). La page : une femme née en
1975, salariée du privé non cadre, puis conjointe collaboratrice d'artisan
depuis janvier 2010, sur « 50 % du revenu du chef d'entreprise »
(`metier2_statut`, `collaborateur: moitie`, `moteur/js/saisie.js`), partie à
64 ans, en février 2039. Ce qui bouge, lu
dans le diff et non refait à la main :

| Ce que la page affiche, sous son libellé | Avant | Après |
|---|---|---|
| « vraiment payé », en bref, en « € brut/mois » | 1 237 | 1 236 |
| « Le droit qui s'applique », sa pension | 1 299 € | 1 298 € |
| « Pension du système actuel », « dans les euros de son année de départ » | 20 403,07 € | 20 398,20 € |
| « Régime complémentaire obligatoire des artisans » | 673,49 points, 315,78 € | 663,10 points, 310,91 € |
| « Le système 2 verse [...] € par an de moins que le système 1 » | 9 554 | 9 550 |

La « retraite » affichée en bref, 1 357 €, ne bouge pas ; les autres lignes
sont les tableaux, la courbe et les tables par âge et par année qui en
dérivent. Pourquoi, au code (`revenu_a_l_option`, `droit/acquerir.py`) : ses
deux premières années, 2010 et 2011, n'ont pas de ligne à l'option deux ans
plus tôt et gardent le revenu de l'année ; 2012, la dernière année de la règle
(`assiette_annee_de_revenu` des périodes de 2010 à 2012), lit celui de 2010.
Ce que cc55cdd déplace est donc deux témoins, et non un : un de simulation,
`conjoint_collaborateur_au_tiers`, que la note de M2-bis dit, et ce témoin de
page.

**Ce qui reste.** Rien de ces trois écarts. L'action garde ce que dit son bloc
« Reprise », que ces retouches ne rendent pas faux.
