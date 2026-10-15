# Étape 4, troisième partie : la fabrique lit ses PDF par le lecteur du site, le cœur Python retiré

**La demande.** Le propriétaire veut le troisième temps dans la même session :
la fabrique lit par le lecteur du site, puis le cœur Python part, les valeurs
identiques.

**Basculer** (commit c14ef58). `scripts/fetch/lecture_pdf.py` garde son chemin
et ses fonctions, sous ses deux noms d'import — les quatorze scripts ne
changent pas —, mais elles demandent au lecteur du site, par node :
`scripts/fetch/lecture_pdf.mjs` reçoit le document sur son entrée standard et
rend `lignesPdf`, `lignesParPage`, `fragmentsParPage` ou `contenuDeLaPage`.
Les deux derniers sont des exports nouveaux du lecteur : les fragments page
par page, et le contenu d'une page prise dans l'arbre des pages, que seul le
Python savait trouver. Les huit dernières réponses se gardent ; sans node, la
lecture s'arrête net. Ce que la fabrique seule utilise reste en Python,
au-dessus du lecteur : la lecture par abscisse et les rectangles peints, avec
la composition des matrices des tracés, six lignes, le seul double qui reste.

`cnavpl_recueils.py` refaisait sa propre lecture avec six fonctions internes :
les chaînes collées flux par flux, dans l'ordre du fichier, sans table de
police — son `group(9)` désignait un autre groupe que le nom de la police, le
défaut que le lecteur avait corrigé chez lui. Il colle désormais les lignes du
lecteur, et ses cinq recueils, de 2021 à 2025, rendent les mêmes valeurs. Les
tests du lecteur, `tests/test_lecture_pdf.py`, et deux de `tests/test_donnees.py`
lisent par node, et se sautent sans lui.

**Vérifier.** Les onze scripts, lancés avec le module livré, écrivent les mêmes
24 fichiers qu'avec le lecteur Python du deuxième temps — le jaune à l'ordre
près de ses incohérences — ; la certification rend les mêmes 132 valeurs ; les
trois scripts de la CCSS lisent deux fois plus vite, de 52 à 64 secondes contre
100 à 122.

**Retirer.** Le cœur Python — objets, flux, tables, jetons, fragments,
assemblage, arbre des pages — part, avec le banc `scripts/banc_lecture_pdf/`,
dont l'office était de le confronter au lecteur du site : `lecture_pdf.py`
passe de 1 055 lignes à 382, l'adaptateur et ce que la fabrique seule
utilise. Rien ne se perd : l'histoire du module — les barèmes de la CNBF, le
jaune budgétaire, le relevé d'info-retraite, les tracés — et les détails que
ses commentaires gardaient seuls — la chronologie de la CARMF, le rapport de
1995 à la CCSS, l'origine de « 5DSSRUW », « Priseenchargedecotisations » —
sont passés dans le JavaScript ; `scripts/conservation.py --depuis HEAD` : rien
de perdu. La carte compte 68 paires, et `lecture-pdf.js` est du JavaScript
seul. Tests : 2 402 rapides, 7 du site, 1 454 de contrôle, 52 de node.

**Ce qui suit.** De l'étape 4, il reste `cycle_de_vie.py`, après l'étape 10 de
l'action 138. Les défauts communs du lecteur — les insécables de la dernière
ligne, les polices d'un `/Contents` rangé à part, les programmes de police lus
comme du texte, les polices WinAnsi sans table, dont « … » s'écrit `\x85` — se
corrigent désormais une fois, dans le lecteur unique ; chacun déplacera des
valeurs de la fabrique, à refaire et à relire. Les deux fichiers de tests du
lecteur, l'un en Python par node, l'autre pour node seul, rejouent les mêmes
documents : un seul pourrait suffire.
