# La page « Méthode » : le moteur du site fait foi, son jumeau Python tenu au bit près

**La demande.** Le 31 octobre 2026, le propriétaire confie à une session du
site ce que le site disait encore à l'inverse de la note de décision 0005 :
le dépliant « Comment ce site est construit, et comment on le vérifie » de la
page Méthode (`methodeConstruction`, `moteur/js/pages.js`), qui appelait le
Python « le modèle de référence » et le JavaScript son « portage » ; ce qui le
tient, la phrase en gras au catalogue et son contrôle, et le test de
`test_web_revues.py` ; l'en-tête de `test_web.py` et un docstring ; deux
passages du README. La note 0005 renvoyait cette page au jour où les
confrontations passeraient au portage ; le propriétaire l'avance, sous une
règle : chaque phrase vraie aujourd'hui, et encore vraie quand une autre
session, en ce moment, fait passer au portage les confrontations à OpenFisca,
aux exemples officiels, à Destinie et à « Mon estimation retraite ». La page
ne dit donc pas lequel des deux exemplaires les sources éprouvent : le modèle
l'est, et ses deux exemplaires sont identiques au bit près. Aucun calcul ne
bouge, et aucun fichier de l'autre session n'est touché.

**Le test d'abord.** `test_la_methode_dit_comment_le_site_est_construit`
exige le lien vers `moteur/js/` à côté de ceux vers `src/` et `tests/`, et,
dans le texte balises retirées : le moteur « écrit en JavaScript, sans aucune
bibliothèque », qui « tourne entièrement dans votre navigateur » ; « C'est lui
qui fait foi. » ; le jumeau qu'il « garde », les deux exemplaires
« identiques au bit près », le modèle « confronté aux sources » ; « Le coût
pour toute la population », qui « se calcule en Python, une fois » ; chaque
page figée en témoin. Il refuse « modèle de référence » et « portage ». Vu
rouge sur le lien manquant. Au catalogue, `methode.portage_javascript` devient
`methode.le_moteur_du_site_fait_foi`, d'extrait « C'est lui qui fait foi. »,
et son contrôle `le_moteur_du_site_fait_foi` remplace
`portage_compare_aux_temoins` : rouges, l'extrait absent de la page et
l'ancienne phrase en gras hors du catalogue ; verts une fois la page récrite.

**La page.** Trois paragraphes, pour un lecteur qui n'est pas développeur. Le
moteur qui calcule une carrière est écrit en JavaScript, sans bibliothèque, et
tourne dans le navigateur : c'est lui qui fait foi. Le modèle est confronté
aux sources ; écrit d'abord en Python, il y garde un jumeau tant que la
migration n'est pas finie, et les deux sont tenus identiques au bit près —
« jusqu'au dernier chiffre que l'ordinateur retient » : les carrières témoins
sont calculées par le moteur du site, le jumeau doit refaire chaque calcul.
Le coût pour toute la population se calcule en Python, une fois, à la
fabrique, et arrive tout fait avec les données ; les carrières qu'il
additionne, le moteur du site les simule (`cout._par_le_portage` : le modèle
intact, sur les données du dépôt). Le texte des pages n'est écrit qu'une fois,
en JavaScript. Le paragraphe des données et les liens ne changent pas.

**Ce que le contrôle tient.** La phrase porte sur la vérification même, et
le contrôle la lit où elle est : deux cents témoins de simulations au moins
(la page dit « des centaines » ; l'ancien contrôle se contentait de cent) ;
`tests/js/moteur.test.js`, qui les rejoue ; dans `tests/test_pont.py`, lu et
non touché, `test_les_temoins_se_simulent_par_le_portage_sans_le_moteur_python`
et `test_le_moteur_python_refait_chaque_temoin`. Le jour où le dernier
jumeau se retire, le second part, le contrôle tombe, et la page se récrit
avec lui. Si l'autre session renomme l'un des deux, le contrôle suit le nom.

**Le README.** Les deux passages signalés disaient faux : `moteur/js/` « un
portage en JavaScript » devient « le moteur qui calcule, en JavaScript et sans
aucune bibliothèque » ; « le modèle de référence s'appelle directement »
devient « le modèle s'appelle aussi en Python : le coût s'y calcule, et le
moteur d'une carrière y garde un jumeau, tenu au bit près sur celui du site,
qui fait foi ». La relecture en a trouvé trois autres : dans l'arbre du
dépôt, `js/` était le « portage du modèle », et les témoins « figés depuis le
modèle Python » — ils le sont depuis le JavaScript du site, depuis le commit
8a3138a ; et `construire_donnees.py` ne produit plus `moteur/style.css`, sa
propre source depuis la phase 8, quand le README le disait fabriqué « depuis
la feuille de style du module Python ». `verifier_prose.py --corriger` a
refait le poids compressé du moteur, 902 → 903 Ko, que le dépliant allonge.

**`test_web.py`.** L'en-tête disait le modèle Python « qui fait foi » : ce
que les tests confrontent aux pages vient du Python — les agrégats, qui ne se
calculent que là, et les simulations du jumeau, que les témoins tiennent au
bit près sur le JavaScript. Le docstring de
`test_le_portage_javascript_retrouve_les_chiffres_du_modele`, dont le nom
reste (conftest et les notes le citent) : le moteur du site passe ses essais
et ses témoins.

**Rien ne bouge.** `resumer_temoins.py` : 913 témoins de simulation, aucun ne
bouge ; 85 rendus de page, dont un change, `methode`. `construire_pages.py`
refait `methode/index.html`, et elle seule.

**Tests.** 3 528 rapides ; 36 du site, le navigateur compris ; le test de la
page ; au catalogue, la forme, l'extrait, le contrôle, rien d'échappé et
aucun orphelin ; `test_pages_en_dossier.py` ; les 47 de `test_prose.py` ;
le journal de veille.

**Ce qui suit.** Rien pour cette étape. L'action reprend où son bloc
« Reprise » la laisse.
