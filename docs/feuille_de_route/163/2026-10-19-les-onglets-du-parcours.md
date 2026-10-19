# Les onglets du parcours

**Le 19 octobre 2026, la demande.** La vague du 19 octobre confie à une
session ce que la note des chiffres en lettres laissait écrit à la main : les
noms des onglets que `docs/parcours_presentation.md` gardait d'avant — Risque,
Cas types, Avantages, Données, pour Pourquoi changer, Carrières types, Droits
non cotisés, Méthode et sources (`TITRES`, dans `moteur/js/pages.js`) —, et
les titres de ses sections, que `PAGES_DES_SECTIONS` nomme
(`tests/test_parcours.py`).

**Ce qui avait dérivé.** Le parcours faisait ouvrir quatre onglets que la
barre n'a plus, et un cinquième sous un nom tronqué, Méthode : dans les
titres de quatre sections, dans cinq « Onglet **…** » et dans cinq « la
page … » ou « la section … ». Données n'était plus
une page : son adresse mène, depuis le 23 septembre, à la partie « D'où
viennent les chiffres » de Méthode et sources (`ANCIENNES_ROUTES`), et
`PAGES_DES_SECTIONS` rendait encore la section 6 sous `/donnees`. Le
paragraphe qui décrit la barre lui donnait huit onglets en deux voix : elle
en porte neuf, en trois groupes, Le saviez-vous ? ayant rejoint Partager le
4 octobre (`GROUPES_NAVIGATION`, dans `moteur/js/gabarit.js`).

**Le test d'abord.** `test_le_parcours_nomme_les_onglets_comme_la_barre`,
vu rouge sur les quatorze désignations d'avant, exige que chaque section
numérotée porte le nom de l'onglet de sa page ; que chaque « Onglet **…** »,
chaque « page … » et chaque « section … » suivis d'une majuscule nomment un
onglet de `TITRES` ; et que le paragraphe « La barre du haut » la nomme
groupe par groupe, dans l'ordre de `GROUPES_NAVIGATION`. Il lit les deux
tables par node, et il est du filet `-m site` (`SITE`, dans
`tests/conftest.py`) : une retouche des pages qui renomme ou déplace un
onglet le fait tomber avant l'envoi, et la session des pages reprend le
parcours avec elle.

**Ce qui est récrit.** Les quatre titres et `PAGES_DES_SECTIONS`, la
section 6 rendue sous `/methode` comme `HORS_PAGE` ; les désignations ; la
section 6, qui fait ouvrir Méthode et sources puis descendre jusqu'à « D'où
viennent les chiffres » au lieu d'un onglet Données ; la description de la
barre, sans compte d'onglets, que la liste dit ; et Le saviez-vous ? parmi
les pages gardées pour les questions, d'après sa description
(`DESCRIPTIONS`, dans `pages.js`).

**Ce que le test ne voit pas.** Un nom d'onglet écrit nu, sans « Onglet »,
« page » ni « section » : les renvois des questions attendues — « Simuler,
deuxième adresse, et Carrières types, ligne du fonctionnaire » —, récrits à
la main, et justes au 19 octobre. Ailleurs, les noms d'avant restent dans
trois fiches des limites, dans des commentaires du code et du catalogue des
affirmations, et dans le diaporama du 20 septembre, daté.

**Vérifié.** `tests/test_parcours.py` et `tests/test_niveaux.py` passent,
37 tests ; le filet du site, 9 ; la suite rapide, 2 841 ;
`tests/test_conservation.py` et `tests/test_prose.py`, 56 ;
`verifier_prose.py` dit vraie la prose déclarée.
