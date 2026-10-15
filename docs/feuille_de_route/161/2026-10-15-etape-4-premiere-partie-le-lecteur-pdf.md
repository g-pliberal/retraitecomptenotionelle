# Étape 4, première partie : le lecteur PDF — relu, son défaut du site corrigé, le choix du propriétaire mesuré sur les vrais documents

**La demande.** Le 15 octobre 2026, le propriétaire demande l'analyse de la
paire `scripts/fetch/lecture_pdf.py` et `moteur/js/lecture-pdf.js`, « et on
tranche après » ; puis la correction du défaut du site qu'elle trouve ; puis,
sur conseil, il choisit un lecteur unique, en JavaScript, mené en trois temps :
mesurer, aligner, basculer et retirer. Cette partie couvre l'analyse, la
correction et le premier temps.

**Relever** (`python scripts/jumeaux.py lecture_pdf`). Le Python (1 055 lignes)
est un sur-ensemble du JavaScript (784). Le site n'appelle que `lignesPdf`. La
fabrique appelle `lignes_pdf`, `lignes_par_page` (et sa lecture par abscisse),
`fragments_par_page`, `texte_de_ligne`, `texte_pdf` et `aplats_de_page` —
quatorze scripts et dix fichiers de tests —, et `cnavpl_recueils.py` refait sa
propre lecture avec six fonctions internes. Environ 340 lignes de Python n'ont
pas de jumeau : la lecture par abscisse, les aplats, l'arbre des pages. Une
dépendance cachée : le module se charge sous deux noms, `lecture_pdf` et
`fetch.lecture_pdf` (`ccss_transferts_retraite.py`).

**Relire.** Mêmes expressions régulières, mêmes calculs dans le même ordre,
donc au bit près, et sept différences :

| Cas | Python | JavaScript | Qui a raison |
|---|---|---|---|
| Flux comprimé qui finit par `\r` ou `\n` (0,74 % des flux) | le lit | perd la page, ou la police | le Python, corrigé le 14 octobre (action 159) sans être porté |
| Plus de 1 Ko d'octets parasites après un flux | le lit | le perd | le Python |
| Échappement octal au-delà de `\377` | mauvaise lettre | la norme PDF | le JavaScript |
| Destination de table à nombre impair de chiffres | lève, tout le document perdu | lit | le JavaScript |
| Table ToUnicode vide | texte brut | autre texte brut | aucun |
| Codes que cp1252 ne définit pas | `�` | caractère de contrôle | aucun |
| `\x1c` à `\x1f` et `\x85`, espaces pour `str.strip`, non pour `trim` | une chaîne qui n'a qu'eux devient une insécable | gardés | aucun : `\x85` est « … » en WinAnsi |

Trois défauts sont communs : la dernière ligne d'un document, et de chaque page
pour la lecture par page, perd ses insécables ; une page dont `/Contents`
désigne un tableau rangé dans un autre objet (la page 24 du jaune pensions du
PLF 2027) se lit flux par flux, avec les polices d'une autre page ; un
programme de police qui contient « Tj » par hasard se lit comme du texte, d'où
les lignes de charabia qui finissent bien des documents.

**Confronter sur des documents fabriqués** (`synthetique.py`). Sur 20 000
documents tirés au hasard, aucun écart hors des sept cas ; chacun, pris seul,
en produit.

**Corriger** (commit 1f18f72). Le flux qui finit par un retour à la ligne se
relit tel quel quand le premier essai échoue, comme dans le Python ; node
rejoue le test du Python, avec le cas du `\r` ; plus aucun écart sur 20 000
documents dont les flux finissent ainsi.

**Le choix du propriétaire.** Un seul lecteur, en JavaScript, que la fabrique
fait tourner par node (la règle de la note 0003 pour ce qui tourne aux deux
endroits) ; ce que seule la fabrique utilise — les aplats, la lecture par
abscisse, la lecture de `cnavpl_recueils.py` — reste en Python, au-dessus du
lecteur JavaScript, comme la même règle le veut. Le premier conseil était de
tout porter : moins de code traduit, moins de risque.

**Premier temps : mesurer sur les vrais documents.** Un banc provisoire,
`scripts/banc_lecture_pdf/` (`fabrique.py` dit comment le lancer), fait lire
aux deux lecteurs les 36 PDF que la fabrique télécharge (116 Mo, 259 683
lignes : barèmes de la CNBF de 2017 à 2023, jaune pensions du PLF 2027, deux
PAP de 2026, recueils de la CNAVPL de 2021 à 2025, quatorze rapports à la
CCSS de 2013 à 2025, brochures de la DGFiP, documents du COR, de la DG Trésor,
du CAS Pensions, du CESE et de l'Assemblée), et fait tourner les onze scripts
qui les lisent avec l'un puis l'autre :

- les objets, les flux dépliés et les tables des polices sont identiques dans
  les 36 documents ;
- les fragments et les lignes n'ont qu'une cause d'écart, la règle des
  espaces : 119 chaînes, qui, refaites sous la règle du Python, redonnent
  exactement ses fragments et ses lignes. Ce cas, jugé rare à la relecture,
  est fréquent : les « … » des polices sans table, le charabia des polices ;
- les onze scripts écrivent les mêmes valeurs, sauf deux écarts qui ne
  tiennent pas au lecteur : `sre_jaune_pensions.py` range ses 67 incohérences
  dans un ordre qui change d'un lancement du Python à l'autre, et les textes
  intégraux de `sites_institutionnels.py` diffèrent par les espaces (quatre
  lignes du document du COR, une de charabia) ; la certification qui lit un
  PDF (`verifier_donnees.source_taux_avant_1967`) rend les mêmes 132 valeurs ;
- le JavaScript lit plus vite : 87 secondes contre 138.

Hors du banc : le barème de la CNBF de 2024, dont le repli par archive.org ne
répond pas depuis une session dans le nuage ; l'estimation officielle, qui lit
le relevé d'une personne ; la lecture propre de `cnavpl_recueils.py`, qui
garde les fonctions internes du Python jusqu'au troisième temps, ses entrées
identiques.

**Signalé à la zone des données.** `sre_jaune_pensions.py` écrit ses
incohérences dans un ordre qui varie, ce qui fait bouger son extrait à chaque
lancement ; `dgfip_brochure_impot.py`, lancé aujourd'hui, récrit
`tests/temoins/brochure_impot_revenu.json` (cent vingt lignes de plus, une
table « personne_seule ») ; le barème 2024 de la CNBF n'est plus à son adresse.

**Ce qui suit.** Le deuxième temps, dans sa session : aligner le JavaScript sur
le Python, qui fait foi tant que la paire existe — la règle des espaces, dans
la lecture des chaînes blanches et la normalisation des lignes ; les octets
parasites ; les autres cas rares, un à un, aucun ne paraissant dans les 36
documents —, jusqu'à ce que `python -I scripts/banc_lecture_pdf/fabrique.py
tout` montre les 36 documents identiques à tous les niveaux et les mêmes
valeurs. Puis le troisième : la fabrique lit par node, sous les deux noms du
module (l'ébauche est `scripts/banc_lecture_pdf/lecteur_site.py`), l'arbre des
pages passe au JavaScript pour les aplats, `cnavpl_recueils.py` est rebranché,
et le cœur Python part dans un commit à lui, avec le banc. Les défauts communs
viennent ensuite, corrigés une fois, dans le lecteur unique.
