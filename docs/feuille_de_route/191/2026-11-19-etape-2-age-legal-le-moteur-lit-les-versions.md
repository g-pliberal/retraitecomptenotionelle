# Étape 2 de la note 0009, deuxième session : le moteur lit l'âge légal par ses versions

**Reprise, au 19 novembre 2026.** L'étape 2 de la note de décision 0009 range
l'âge légal dans les versions de sa fiche, en trois sessions. Les deux
premières sont faites : la fiche `age_legal_par_generation` porte six
versions, et le moteur y lit l'âge légal, à la date d'effet de la pension.
Aucun résultat n'a bougé. Reste la troisième session, qui change les deux
droits d'avant réforme en couches et retire leurs deux copies de l'âge légal.
Elle attend l'accord du propriétaire. Commencer par le brief de cette
session, « Brief A2c », dans
`/mnt/project-files/architecture/191-briefs-amendes.md`. Au propriétaire
aussi : dire si les deux copies passent du niveau `haute` au niveau
`certifiee` ; faire relire par une autre session les versions de 1985 à
2011, sans exemple officiel ; et décider des lecteurs qui lisent l'âge de la
personne là où la loi dit peut-être celui de la date d'effet, listés plus
bas.

Le 19 novembre 2026, deuxième des trois sessions de l'étape 2 (« Brief
A2b »), ouverte par la session de coordination pendant que le propriétaire
dormait, comme une migration qui ne change aucun résultat. Elle suit la
première, dont la note est
`2026-11-19-etape-2-age-legal-les-versions-deviennent-la-source.md`.

**Ce que le paquet porte.** La fiche de l'âge légal entre dans les fiches que
le moteur lit (`FichesDatees.NOMS`, `fiches_datees` du paquet). Chaque version
y porte ses seules lignes, en étendues de générations, l'âge au mois exact
(`tables_de_version.pour_le_moteur`) ; la version de 2025 garde son renvoi à
sa rédaction antérieure pour les assurés nés avant le 1er septembre 1961, que
le moteur suit. La table fusionnée quitte le paquet (`ages_ouverture`), dont
la version monte à 46 : `age_ouverture_requis.csv` reste une vue fabriquée,
que lisent la fabrique, la certification et la prose, plus le moteur. Les
deux copies d'avant réforme y restent jusqu'à la troisième session.

**Ce que le moteur lit** (`AgesOuverture`, dans `moteur/js/regimes.js`).

- À la date d'effet d'une pension, la version qui vaut ce jour-là, et la
  ligne de la génération (`aLEffet`).
- Pour une personne, l'âge de la version sous laquelle son droit s'ouvre
  (`age`). Le moteur cherche la première date dont la version ouvre le droit
  (`premierDepart`) : il ne s'arrête qu'aux dates où une version change, et
  l'essai de chaque premier du mois lui sert de témoin dans les tests. Il rend
  `null` quand aucune date n'ouvre le droit.
- Un renvoi sans cible ou qui boucle, une fiche absente du paquet, une date
  sans version arrêtent le calcul et nomment la fiche et ses versions.

**La recherche du premier départ dans les départs** (`premiereOuvertureSous`,
dans `moteur/js/droit/departs.js`). La date où une unité ouvre sa pension ne
se déduit plus d'un âge par génération. Sous chaque version de l'âge légal,
dans l'ordre, le moteur date l'ouverture à l'âge que cette version oppose, et
la retient si elle tombe avant la fin de la version, au plus tôt à son
premier jour. Une ouverture qui ne lit pas l'âge légal ne se calcule qu'une
fois. `ouvertureSous`, qui date l'ouverture sous un seul âge légal, n'a pas
changé d'une ligne.

**De qui est l'âge légal.** Les neuf modules qui lisaient la table lisent
maintenant les versions, et chacun dit de qui il lit l'âge
(`moteur/js/droit/commun.js`) : l'assuré (`ageLegalDeLAssure`), dans
`categories.js`, `compter.js`, `departs.js`, `invalidite.js`, `liquider.js`
et `ouvrir.js` ; le conjoint survivant (`ageLegalDuConjointSurvivant`), dans
`reversion.js`, où la révision des ressources se fige à l'âge légal du
survivant, et non à celui de l'assuré décédé. `scenario-notionnel.js` lit
l'âge de l'assuré à sa seule année de naissance, comme avant.
`scenario-actuel.js` construit le lecteur, et pose encore dessus la copie
d'un droit contrefactuel (`TableRecouverte`).

**Les tests** (`tests/js/age-legal.test.js`, `tests/test_tables_de_version.py`).
Les âges attendus viennent des textes. La recherche rend la date de la table
fusionnée et celle de l'essai mois par mois, réforme par réforme (2010, 2011,
2023, 2025), puis pour chaque mois de naissance de 1900 à 1975, né le 1er ou
non ; aucun droit ne se referme. Une réforme fictive ne change qu'une
version, et le moteur la suit. Une loi fictive qui relèverait l'âge d'un
assuré qui pouvait déjà partir ne lui retire pas son premier départ : c'est
ce que la table ne savait pas dire.

**Rien n'a bougé.** Les témoins refaits sont identiques, octet pour octet, et
la table du coût aussi. Une grille de 72 150 carrières simples, sous le droit
en vigueur et les deux droits contrefactuels, rend la même chose avant et
après. Le correctif en attente de la complémentaire des auxiliaires médicaux
(`ecarts/2026-11-19-carpimko-carriere-longue.patch`) s'applique encore.

**Ce qui reste ouvert, au propriétaire.**

- **L'âge de la personne, ou celui de la date d'effet ?** Pour ne rien
  déplacer, chaque lecteur lit l'âge légal de la personne, qui est celui de
  la table d'hier. Là où un texte vise l'âge que la loi oppose à la date de
  la demande, les deux diffèrent pour qui ne pouvait pas encore partir. La
  retraite progressive en est le cas net : né en 1964, l'assuré y a droit à
  l'âge légal moins deux ans ; en 2025 la loi de 2023 lui donnait 63 ans,
  donc 61 ans, quand le moteur lit 62 ans et 9 mois, donc 60 ans et 9 mois.
  Corriger déplacerait des résultats : c'est une correction, à part, avec
  son test tiré du texte. Les autres lecteurs à relire ainsi : le cumul
  emploi-retraite, la substitution de la pension d'invalidité, la surcote
  depuis l'âge légal, la bonification du cinquième des militaires.
- **La fiabilité des deux premières versions.** L'âge d'un assuré dont le
  droit s'est ouvert avant le 1er juillet 2011 se lit désormais dans la
  version `soixante_ans`, lue à la main, donc `haute`, ou dans la version
  supposée d'avant 1985, `moyenne` ; la table disait `certifiee`. L'âge est
  le même, soixante ans. Un seul lecteur garde cette fiabilité, la
  bonification des militaires, déjà `moyenne` : aucun résultat ne la montre.
- **Avant la génération 1900**, la table ne répondait rien, et la valeur de
  la période servait ; les versions de soixante ans répondent pour tous. Le
  modèle ne couvre pas ces générations.
- La troisième session, les deux points laissés par la première, et la
  seconde lecture des versions de 1985 à 2011 restent à faire.

**Ce que la session a coûté.** Un commit, 23 fichiers, dont trois
nouveaux : le fichier d'essais, cette note et l'entrée du journal de veille. Ouverte à 23 h 10 UTC le 19 novembre 2026, close dans la nuit, sur
Fable 5.2. Deux fabrications du paquet, deux des témoins.
