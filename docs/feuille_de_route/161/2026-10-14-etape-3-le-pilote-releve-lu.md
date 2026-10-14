# Étape 3 : le pilote, le lecteur du relevé — relu, confronté, son jumeau Python retiré

**La demande.** Mener la méthode de la note de décision 0003 sur une première
paire, la plus facile de la carte : `web/releve_lu.py` (1 112 lignes) et
`moteur/js/releve-lu.js`, que le site charge pour lire le relevé qu'un lecteur
dépose, et que ni le coût ni la fabrique n'atteignent.

**Relever** (`python scripts/jumeaux.py releve_lu`). Le jumeau Python était
importé par `scripts/estimation_officielle.py`, `tests/test_affirmations.py` et
`tests/test_releve_lu.py`, et six textes à tenir le citaient : l'arbre du
README, deux entrées de `data/reference/referents.yaml`, l'annexe B de
l'architecture, la partie 5 des limites, `web/__init__.py`, et l'en-tête du
JavaScript, qui s'en disait le portage. Côté JavaScript, `index.html`
l'importe, et `tests/test_releve_lu.py` le faisait lire à node par
`tests/js/comparer-releve.mjs`, contre le Python.

**Mesurer.** Les tests de concordance exécutaient 97 % du Python (480 lignes
sur 497) et 99 % du JavaScript (596 sur 604). Jamais exécutées côté
JavaScript : l'écriture d'une plage d'années (« 1990 à 2003 ») dans les notes,
la fusion de deux interruptions voisines, deux refus de ligne.

**Relire.** Les deux lecteurs, fonction par fonction : mêmes constantes, mêmes
tables de régimes et de motifs, mêmes marqueurs, même arrondi, mêmes règles de
lecture, mêmes notes au mot près. Quatre différences :

1. **Les accents.** Le Python effaçait toute marque qui se combine à sa lettre
   (catégorie Unicode « Mn »), le JavaScript les seules de U+0300 à U+036F :
   une marque plus rare restait, la ponctuation la changeait en espace, et le
   nom d'un régime ou d'un motif se coupait en deux. Corrigé dans le
   JavaScript (`\p{Mn}`).
2. **Un compte de trimestres étiqueté qui n'est pas entier.** « 2,5 trim. » :
   le Python en comptait deux (`int`), le JavaScript gardait 2,5, qui passait
   tel quel à la saisie. Corrigé dans le JavaScript (`Math.trunc`).
3. **Les chiffres.** Le `\d` du Python lit tout chiffre Unicode, celui du
   JavaScript les seuls chiffres ASCII. Un relevé n'en écrit pas d'autres, et
   ne pas lire un chiffre exotique pour un nombre est le plus sûr : rien n'a
   changé.
4. **Le tri des interruptions** avant leur fusion ne prend pas les mêmes clés,
   sans effet : une année ne porte qu'une interruption.

**Confronter.** Avant que le Python parte, un banc a fait lire aux deux 8 000
relevés tirés des quatorze relevés d'essai des tests, mutés — accents et
marques rares, majuscules, espaces insécables, unités (€, EUR, trim., pts),
décimales, dates et périodes, numéros de sécurité sociale, lignes de bruit,
années consécutives d'un même motif, lignes mêlées —, sous trois
convertisseurs : aucun, celui d'essai, le barème du modèle. Avant correction,
18 cas sur 4 000 s'écartaient, tous par la marque rare, puis 10 sur 6 000,
tous par les trimestres non entiers : les deux écarts de la relecture, et
aucun autre. Après correction, 0 sur 8 000, et le banc a exécuté les 604
lignes de code du lecteur JavaScript.

**Corriger** (commit d54a914) : les deux écarts, dans le JavaScript, et un
relevé d'essai qui les tient (`ecarts_de_la_relecture`). Aucun témoin n'a
bougé.

**Figer.** La lecture des relevés d'essai par le jumeau Python, sans barème et
au convertisseur d'essai (cent euros le point), est figée dans
`tests/temoins/releves_lus.json` : la référence du lecteur du site, au
caractère près. Le barème du modèle n'y entre pas, qui bouge avec les données ;
ses conversions gardent leurs tests. Une lecture qui change exprès se refige,
dans un commit à elle :
`REFIGER_LES_RELEVES_LUS=1 python -m pytest tests/test_releve_lu.py -k figee`.

**Brancher** (commit 8333cc5). `tests/js/lire-releve.mjs` remplace
`comparer-releve.mjs` : il rend la lecture entière, sous les trois
convertisseurs, et `tests/test_releve_lu.py` lit par lui, d'un seul appel pour
les relevés d'essai. L'estimation officielle lit par le pont du Python vers le
site (`web/site.py`), comme le contrôle des affirmations : un adaptateur de
vingt lignes y rend la lecture que le script attendait, et prend `arrondi` au
lecteur.

**Retirer.** `web/releve_lu.py` est parti, les témoins, le paquet, la prose et
le tableau de bord identiques. Ses explications sont passées dans le
JavaScript, rien ne s'en perd : le docstring du module — ce que le relevé
donne et ne donne pas, les francs, les points — et vingt-trois commentaires,
de la ligne de doublure qui faisait deux millions d'euros à la règle du statut
de l'année. Les six textes nomment le lecteur du site. Tests : 2 402 rapides,
7 du site, 817 de la zone, 44 de node. La carte compte 69 paires, et
`releve-lu.js` est désormais du JavaScript seul.

**Signalé à la zone des données.** Les deux entrées de `referents.yaml` qui
citaient le lecteur disent que les points du relevé sont « lus, et jetés » :
c'était vrai avant l'action 138 (étape 11) ; le site les convertit depuis,
quand il passe le barème. Le renvoi est corrigé, l'affirmation est à reprendre.

**Ce qui suit.** L'étape 4 : les deux autres paires hors du coût et de la
fabrique. `scripts/fetch/lecture_pdf.py`, que quatorze scripts de la fabrique
lisent — douze lecteurs de sources, la certification des données,
l'estimation officielle — et le site par `lecture-pdf.js` : une paire « aux
deux endroits », à trancher à sa relecture. Puis `cycle_de_vie.py`, une fois
l'étape 10 de l'action 138 faite, qui en affiche le jumeau.
