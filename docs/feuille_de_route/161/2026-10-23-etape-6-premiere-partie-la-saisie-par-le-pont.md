# Étape 6, première partie : trois paires relues, et la fabrique qui bâtit ses carrières par la saisie du portage

**La demande.** La vague du 23 octobre 2026 : la session de suivi « Qu'est-ce
qu'il reste à faire ? » lance, sur la demande du propriétaire (« Fait ça », en
réponse à l'offre d'une session par chantier qu'une session peut mener seule),
douze sessions en parallèle, une étape chacune. Celle-ci tient l'action 161,
étape 6 : la première paire du moteur de la carte que la session peut retirer
seule, relue d'abord, puis la fabrique qui passe par le pont pour elle, puis le
retrait du jumeau Python ; d'une paire de données, la relecture au
propriétaire, et la suivante ; les paires du coût et de l'équilibre laissées
aux étapes 3 et 7 de l'action 138.

**La paire choisie.** Les trois premières de la carte ne se retirent pas
seules : `donnees/credits_ministeres.py` et `donnees/agregats.py` sont des
données, que le propriétaire tranche ; `contributions_equilibre.py` est à
l'action 138. La quatrième, `contexte.py`, est la première du moteur : la
fabrique l'atteint par six scripts, et 51 fichiers de tests.

**Pour le propriétaire : les crédits des ministères** (rang 1). Le Python lit
le fichier certifié (une seule année, la fiabilité la plus basse), et
`construire_donnees.py` n'en écrit au paquet que les parts. Les deux côtés
recalculent ensuite trois choses : la contribution employeur (T2 et T3 CAS),
ce qui va au compte « Pensions » (avec la retenue), et l'ordre des ministères.
Relus ligne à ligne : mêmes formules, même ordre d'addition (de gauche à
droite, depuis zéro), même refus d'un ministère absent ; aucun écart. Le calcul
du Python ne sert qu'à ses tests (`test_sre_jaune_ministeres.py`, la
comparaison de `test_web.py`) ; la page Coût calcule en JavaScript. À trancher :
le Python garde-t-il ces trois calculs, ou seulement le chargeur, ses tests
passant au portage ?

**Pour le propriétaire : la table des agrégats** (rang 3). Le Python porte les
écrivains de la table (`figer_*`), qui ne tournent qu'à la fabrique et restent
par la règle de l'endroit, et des lecteurs qui ne servent qu'aux tests
(`test_agregats.py`, `test_bilan_compte.py`, deux de `test_web.py`) : aucun
script ni module ne les lit. Relue accesseur par accesseur, par un agent, ses
constats vérifiés aux lignes citées ici : aucun écart ne change une valeur ni
un dernier bit. Les
écarts sont de refus et de forme. Une ligne de dette interrogée sur un système
absent lève un `KeyError` en Python et rend `undefined` en JavaScript, puis
`NaN` dans `dettePublique` (`agregats.py:809`, `agregats.js:431`) ; de même
`ressources_meur` sur le solde dérivé (`agregats.py:610`, `agregats.js:262`) ;
une table vide lève en Python et rend 0 en JavaScript. La clé de la dette au
taux décalé s'écrit `repr(float(ecart))` d'un côté, `String(ecart)` de l'autre
(`agregats.py:928`, `agregats.js:533`) : les mêmes pour ±0,01, distinctes pour
un écart entier ou sous 10⁻⁴. Le JavaScript lit une clé de génération écrite
en chaîne, que le Python refuse. Le docstring promet qu'« une lecture qu'elle
ne porte pas lève une erreur, plutôt que de rendre un zéro »
(`agregats.py:21`) : la dette et son stock rendent 0 hors de la table, et le
solde moyen 0 sur une fenêtre vide, des deux côtés. Rien n'a été corrigé : le
jumeau qui reste se tranche d'abord. Neuf accesseurs du JavaScript ne sont
comparés au lecteur Python par aucun test : la décomposition, la dette au taux
décalé, la dette publique, le taux de TVA requis… À trancher : les lecteurs Python
restent-ils, ou les tests lisent-ils la table par le portage ?

**La paire du contexte, relue.** Fonction par fonction, de `refusDePension` à
`Montants` : aucun écart de calcul. Différences voulues : le `cout()` et les
`avantages()` du Python calculent sous les règles du contexte, ceux du
portage lisent la table figée depuis l'action 150 ; `population()` n'est
qu'en Python, `agregats()`, le balayage des âges et le contrôle du relevé
qu'en JavaScript. Sans effet aujourd'hui : `departsDeLEstimation` tait toute
erreur qui n'est pas une faute de programme, le Python seulement un refus de
la saisie ou du modèle. Deux commentaires : celui de `verifierStatutsOuverts`
s'était égaré au-dessus d'une autre fonction (be43daa) ; celui de
`AGREGATS_MEMORISES` en Python compte deux agrégats par jeu de règles, la
restitution en fait un troisième.

**Le chemin.** Le contexte du Python est deux choses. D'un côté, la saisie :
d'une requête, la carrière, que le site bâtit chez son lecteur — elle n'aura
qu'un exemplaire, le JavaScript. De l'autre, le centre du coût : les données
et les agrégats sous un jeu de règles, que seule la fabrique calcule — il
reste en Python. Mais la carrière, une fois bâtie, le moteur Python la simule
encore, qui garde ses jumeaux tant que le coût le lit ; et les témoins de
simulations sont le seul dispositif qui le confronte au portage. Les faire
simuler par le portage aurait laissé le moteur Python sans confrontation, et
la note 0003 veut des témoins identiques, à l'octet, à ceux du moteur Python.
D'où le pont dans l'autre sens : le portage bâtit la carrière, le Python la
simule.

**Le pont dans l'autre sens** (ba2bf24). `pont.carrieres_des_saisies` envoie
des requêtes au portage, qui les lit par sa saisie, en bâtit la carrière et
les paramètres, et les rend en données ; le Python les relit sous ses types
(`carriere_des_donnees`, `parametres_des_donnees`), refuse un champ qu'il ne
connaît pas, et redonne aux nombres libres de la chronologie, que le contrat
C.1 ne type pas, le flottant qu'il leur donne (`FLOTTANTS_DE_LA_CHRONOLOGIE`).
Sur les 889 requêtes des témoins, la carrière et les paramètres reviennent
identiques à ceux de la saisie Python, comparés en JSON, chaque nombre sous
son type ; le test, du niveau complet, prend dix secondes. Un test rapide, sans
node, éprouve la relecture ; trois mutations du code le font rougir.

**La fabrique.** Les témoins de simulations simulent au moteur Python la
carrière que le portage bâtit (eac3add), un simulateur par jeu de paramètres :
`construire_temoins.py --verifier` les trouve à jour, les 889, octet pour
octet. Le budget de calcul mesure les mêmes carrières, sous 34 simulateurs, et
le relevé des lectures ne charge plus ni `contexte.py` ni `saisie.py`
(2cd2d4d). La confrontation à « Mon estimation retraite » fait bâtir au
portage la carrière du relevé qu'elle a prolongé, sans qu'il la prolonge une
seconde fois (`"prolonger": False`), et ne prend plus de contexte (b6e53a4).
Restent au contexte Python, dans la fabrique, `_bilan` et `_agregats` de
`construire_donnees.py` et `bilan_compte.py` : le centre du coût.

**Tests.** 2 950 rapides ; ceux de la zone : le pont, la confrontation, la
liquidation, l'outillage du budget et des lectures, les témoins à jour.

**Ce qui suit.** Le retrait de la saisie du contexte Python, en trois lots.
1. Les tests qui en dépendent, une trentaine de fichiers : qui éprouve une
règle du moteur par une saisie simule la carrière que le pont rend
(`carrieres_des_saisies`, puis `Simulateur(parametres).simuler`), ses
assertions inchangées ; qui éprouve la saisie elle-même — un refus,
l'échelle, `Montants`, les départs de l'estimation — passe au portage, par
`site()` ou `node --test`. Le test du pont qui compare à la saisie Python
perd alors sa référence ; les témoins le relaient. 2. Le centre du coût reste
en Python, sans jumeau : `contexte.py` réduit à lui, ou un module à lui ; et
`contexte.js` cesse de se dire le portage d'un fichier qui ne le porte plus.
3. Le retrait : les explications du Python passent dans `contexte.js`, qui
y renvoie vingt-trois fois (« Voir … contexte.py », « … du Python »), puis les
fiches, les mentions et les textes à tenir (`python scripts/jumeaux.py
contexte`). `saisie.py`, la paire
suivante, perd alors son dernier lecteur dans `src/`.
