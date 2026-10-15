# Étape 4, deuxième partie : les deux lecteurs PDF alignés, cas par cas

**La demande.** Le propriétaire veut le deuxième temps dans la même session
que le premier : aligner le lecteur du site sur le lecteur Python, qui fait
foi tant que la paire existe, en gardant pour chaque cas rare le meilleur des
deux comportements — ne jamais perdre un document entier, suivre la norme
PDF —, un commit par cas, jusqu'à ce que le banc ne montre plus aucun écart.

**Sept cas, sept commits, chacun tenu par un test des deux côtés** — dans
`tests/test_lecture_pdf.py` et sa réplique, `tests/js/lecture-pdf.test.js` :

| Commit | Cas | Ce qui change | Pourquoi |
|---|---|---|---|
| cf251a2 | les espaces du texte, `\x1c` à `\x1f` et `\x85` | le JavaScript | le Python fait foi ; 33 documents de la fabrique sur 36 s'en écartaient |
| a96be2b | l'échappement octal au-delà de `\377` | le Python | la norme ignore le débordement : « `\501` » est « A » |
| 07d8cf7 | la destination de table abîmée | les deux | trois chiffres faisaient lever le Python, et tout le document était perdu : ils se complètent d'un zéro, comme toute chaîne hexadécimale de la norme ; ce qui n'est pas de l'UTF-16 rend « � » des deux côtés |
| edf7687 | la table ToUnicode vide | le JavaScript | elle se lit comme aucune table, comme une police qui n'en a pas ; le site perdait les lettres accentuées |
| 7239742 | les codes que cp1252 ne définit pas | le JavaScript | « � », comme le décodeur du Python, et non un caractère de contrôle invisible |
| 73106ab | les octets parasites après un flux | le JavaScript | zlib ignore ce qui traîne, si long soit-il : la somme qui clôt le flux se cherche dans toute l'entrée, non dans son dernier kilo-octet |
| 7cf4f94 | les espaces de la syntaxe PDF | le JavaScript | l'insécable n'en est pas une, ni pour `\s` sur des octets en Python ni pour la norme : la syntaxe dit sa classe, `[ \t\n\r\f\v]` |

Le dernier n'était pas parmi les sept cas de la relecture : il s'est montré en
relevant exactement ce que chaque langage tient pour espaces — `str.strip` et
`\s` sur une chaîne, `\s` sur des octets, `trim`. Le décodeur des destinations
a été confronté à celui du Python sur 100 000 chaînes tirées au hasard avant
d'entrer dans le lecteur.

**Confronter sur des documents fabriqués** (`synthetique.py`). Les dix-neuf
documents des cas relevés se lisent pareil ; aucun écart sur 5 000 documents
tirés au hasard sans risque, sur 3 000 avec chaque risque pris seul, sur 5 000
avec tous à la fois.

**Confronter sur les vrais documents** (`fabrique.py tout`). Les 36 documents
de la fabrique se lisent pareil à tous les niveaux — objets, flux, tables,
fragments, lignes, lignes par page —, sans plus une chaîne d'écart, et le
lecteur du site les lit en 106 secondes contre 156. Les onze scripts écrivent
les mêmes fichiers avec l'un et l'autre lecteur, les textes intégraux de
`sites_institutionnels.py` compris, le jaune à l'ordre près de ses
incohérences, qui varie d'un lancement du Python à l'autre ; la certification
rend les mêmes 132 valeurs. Les deux changements du Python, l'octal et les
destinations, ne déplacent aucune valeur : ses extraits sont ceux du premier
temps.

**Ce qui suit.** Le troisième temps : la fabrique lit par node, sous les deux
noms du module (`lecture_pdf`, `fetch.lecture_pdf`), à travers l'adaptateur
dont `scripts/banc_lecture_pdf/lecteur_site.py` est l'ébauche ; l'arbre des
pages passe au JavaScript pour les aplats, qui restent en Python ;
`cnavpl_recueils.py` est rebranché sur des fonctions publiques ; les tests de
`tests/test_lecture_pdf.py` lisent par l'adaptateur ; puis le cœur Python part
dans un commit à lui, avec le banc, les valeurs identiques. Les défauts communs
— les insécables de la dernière ligne, les polices d'un `/Contents` rangé à
part, les programmes de police lus comme du texte, et les polices WinAnsi sans
table, dont « … » s'écrit `\x85` — viennent ensuite, corrigés une fois.
