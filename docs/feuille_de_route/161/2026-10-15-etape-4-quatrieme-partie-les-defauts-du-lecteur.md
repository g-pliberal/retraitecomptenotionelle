# Étape 4, quatrième partie : les défauts communs du lecteur PDF, corrigés un à un

**La demande.** Le propriétaire veut corriger les défauts que le lecteur
Python et le lecteur du site partageaient, et que l'alignement avait gardés :
chacun dans son commit, avec son test, en mesurant ce qu'il déplace dans les
36 documents que la fabrique télécharge et dans ses valeurs — les onze
scripts et la certification, `scripts/verifier_donnees.py` —, et en relisant
chaque valeur qui bouge. La mesure se fait sur le banc des parties
précédentes, une copie du dépôt et le cache réseau de la fabrique, hors du
dépôt ; chaque correctif se mesure contre le précédent.

**1. Le `/Contents` rangé dans un objet à part** (commit 0b4c661). La norme
permet qu'une page désigne par `/Contents` un objet qui n'est qu'un tableau
de flux. Le jaune pensions du PLF 2027 range ainsi les 250 siennes : le
lecteur n'y rattachait pas les polices de la page, qui prenaient celles du
document, la dernière de chaque nom, et ses flux se lisaient chacun pour soi.
`fluxDesContenus` lit les trois formes, pour les polices, le regroupement des
flux d'une page et le contenu d'une page. Mesure : seul ce document change,
lu désormais avec ses accents — « décembre » pour « dcembre ». Ses 41 785
valeurs gardent leurs nombres, mais deux lignes du tableau B-1, dont la clé
vient de l'intitulé, changent de nom : `dparts_pour_invalidit` devient
`departs_pour_invalidite`, `dparts_pour_motifs_familiaux`
`departs_pour_motifs_familiaux`. Les 16 lignes de `bonifications_jaune.csv`
sont renommées dans le même commit, mêmes nombres, même niveau, sans quoi la
certification les aurait ajoutées en double ; elle redevient identique, 100
valeurs sur 100. L'édition 2026, lue à part, avait déjà ses accents : la
phrase de `sre_jaune_pensions.py` qui accusait une police du document est
corrigée, son histoire gardée.

**2. Les flux qui ne portent pas de texte** (commits 50faaf8 et 0d174e2). Le
lecteur lisait tout flux où paraissait « Tj », les images seules écartées.
Ne se lisent plus que les flux que la norme fait porteurs de texte, les
contenus de page et les formulaires ; un document qui n'en désigne aucun — un
PDF fabriqué à la main, comme ceux des tests — se lit comme avant. Mesure :
31 documents perdent 258 lignes, aucune n'est ajoutée, et les pages qui
restent gardent leur ordre. Elles venaient de 167 programmes de police, une
ligne de charabia chacun — « OS/2 », « cmap », « prep », « Macintosh » —,
de quatre métadonnées XMP, de deux tables des références, de deux flux
d'indications de la linéarisation, d'un profil de couleur et d'une palette ;
et, pour 81 d'entre elles, de deux pieds de page qu'aucune page ne pose, dans
un rapport à la CCSS, qui en rendaient avec les polices d'autres pages un
double mutilé de la liste des membres (« M. Dav R -L AUZ CfdtnnuvaceuvrFO) »),
dont la version lisible reste. Les valeurs des onze scripts sont identiques,
sauf l'extrait brut du règlement du CESE, que personne ne lit, qui perd ses
quatre lignes finales de charabia ; la certification est identique. Le
second commit corrige le compte que donnait le commentaire du lecteur, qui
parlait de six flux de linéarisation.

**Le cinquième défaut, laissé à part : les formulaires pris pour des images.**
La première mesure du deuxième correctif lisait tous les formulaires. Elle a
montré que l'écart des images, la chaîne « /Image » cherchée dans le
dictionnaire du flux, écarte aussi les formulaires dont les ressources
nomment une image, « /Image869 » ou « /ImageC » : 415 des 3 858 formulaires
des 36 documents, dont 382 portent du texte, des graphiques et des tableaux
collés depuis Excel. Les lire ajoute 9 182 lignes à 13 documents, et déplace
des valeurs de la fabrique : `ccss_regimes.json` passe de 5 866 à 6 208
valeurs — 138 parties, 480 venues, 4 changées, dont les charges et les
produits 2016 de la MSA salariés « toutes branches », de 11 345 à 5 884 et
de 11 361 à 6 579 M€, parce que le tableau retrouvé de la seule branche
vieillesse porte le même intitulé ; à l'inverse, la certification de
`transferts_retraite` passe de 65 à 77 valeurs identiques à la référence, et
ses écarts de 20 à 10, le FSV de 2015 à 2020 se lisant juste. Les lire
demande donc d'apprendre à `ccss_regimes.py` à distinguer les branches : une
étape à part, de la zone des données, que le propriétaire décide. Le lecteur
garde l'ancien écart, et le dit dans un commentaire.

**3. L'insécable de la dernière ligne** (commit 587f2df). La dernière ligne
d'un document, et celle de chaque page, se rendait comme
`re.sub(r"\s+", " ", …).strip()`, qui fond les insécables en espaces, quand
toutes les autres se normalisent : « 1 339 945 1 654 » ne s'y découpait plus
en deux nombres. Elle se normalise désormais comme les autres. Mesure : les
lignes des documents entiers ne changent pas ; dans la lecture page par page,
20 dernières lignes de page, dans 14 documents, gardent leurs insécables,
comme le reste de leur page ; valeurs et certification identiques. La lecture
par abscisse de la fabrique, en Python, normalisait déjà toutes ses lignes.

**4. Les polices WinAnsi sans table** (commit 21f0c7a). Une police simple en
WinAnsiEncoding sans table ToUnicode se lisait en latin-1 : ses octets 0x80 à
0x9F sortaient en caractères de contrôle, et « … », 0x85, passait même pour
une espace — ôté au bord d'une ligne, changé en insécable quand il était posé
seul. Les 36 documents en comptent 443. Elle reçoit désormais une table sans
entrée, qui ne garde que le repli cp1252, et son hexadécimal se lit par un
octet, les codes de contrôle toujours écartés. Mesure : 7 412 lignes de 7
documents, au même nombre de lignes, et rien que des caractères rendus — 6 888
apostrophes, 2 131 euros, 585 tirets, 57 « œ » et « Œ », 36 « … », 10 puces
et guillemets ; dans l'hexadécimal, 832 « é », des « è », « à », « û », « ° »,
et des parenthèses que la lecture par deux octets changeait en flèches,
« ⤀ » pour « ) », 328 fois, « ⠀ » pour « ( », 165 fois. Les numéros de glyphe
écrits sur deux octets d'une police sans table (« <0048> »), que ni l'une ni
l'autre lecture ne rend, gardent la leur, sauf ceux dont l'octet haut n'est
pas nul : « ż » y devient « | ». Seul l'extrait brut du document du COR sur
les paramètres de la CNAV change parmi les valeurs, ses 296 lignes rendues à
leurs apostrophes et à leurs tirets ; la certification, qui y lit les taux
d'avant 1967, est identique.

**Les tests.** Quatre de plus dans `tests/test_lecture_pdf.py`, un par
défaut, chacun vu en échec sur le lecteur d'avant ; 2 402 rapides, 7 du site,
1 458 de contrôle, 31 de node.

**Relevé en passant, et laissé.** La certification compte déjà, avant ces
correctifs, 20 écarts sur `transferts_retraite`, des prestations et des
cotisations du FSV lues à 17 M€ pour 11 Md€ attendus : la lecture de la
source est fausse, et la certification sort en erreur, sur 12 points à
examiner. `ccss_regimes.json` n'a pas de lecteur dans le dépôt. La tolérance
de `sre_jaune_pensions.py` pour « dparts » et « bnficiaires » ne sert plus
qu'à ses tests fabriqués. Les polices communes du document (`polices`), le
repli quand aucune page ne rattache un flux, ne suivent pas les règles de
`tableDe` — un octet par code pour une police simple, cp1252 pour WinAnsi — ;
aucun flux des 36 documents ne s'en sert. L'hexadécimal d'une police qui a sa
table perd les codes que la table ignore, quand les chaînes littérales
prennent l'encodage.
