# Le relevé des lectures au moteur JavaScript : ce que lit le modèle, observé sur le moteur qui calcule

Action 161, suite de `2026-11-16-la-grille-large-sur-le-simulateur-de-donnees.md`.
Aucune règle, aucune donnée, aucun témoin n'a bougé ; le moteur Python reste
en place.

`scripts/lectures_du_modele.py` relève ce que lisent les calculs que la
mémoire garde, pour que l'empreinte n'ignore rien qu'ils lisent
(`memoire.HORS_DU_MODELE`, les champs documentaires des fiches). Il simulait
deux carrières par statut au moteur Python, exprès. Il observe désormais le
moteur qui calcule :

- le portage simule ces carrières (`pont.simulations`) ;
- sous `RELEVE_DU_PAQUET`, `pont.mjs` écrit chaque clé du paquet que son
  moteur lit (`sousLeReleve`, un `Proxy` sur le paquet) ;
- le moteur JavaScript ne lit que le paquet : la fabrique
  (`construire_donnees.construire`) rebâtit ensuite, dans le processus du
  relevé, les seules clés lues, les autres laissées à `None`, et ce qu'elle
  lit pour elles se note, fichiers et champs des fiches, comme le reste.

Rebâtir les clés lues seules, et non toutes en notant chacune à part,
évite qu'une mémoire des chargeurs, chauffée par une clé que le moteur ne
lit pas, cache la lecture d'une autre. Le relevé dit aussi les clés du
paquet que le moteur ne lit pas (`paquet.non_lues`) : 26, dont les crédits
des ministères, la certification, les sources citées, le bilan et les
agrégats.

**Vérifié, avant et après** (`--json`, 40 secondes chacun) : aucun fichier,
aucun module, aucun champ de fiche relevé avant ne manque ; douze fichiers
de plus, que le moteur JavaScript lit par le paquet et que le Python ne
lisait pas (les profils de salaire, le Smic annuel, l'assiette de l'AVPF…),
tous déjà sous l'empreinte ; rien hors du modèle, aucun champ documentaire.
Sous la sonde, le relevé n'exécute plus que des chargeurs et des types du
pont logés dans les fichiers du droit (`scenarios.actuel`, `carriere.py`),
que la fabrique appelle : ceux que la note 0009 doit reloger.

**Tests.** `test_outillage.py` : `test_le_pont_releve_les_cles_du_paquet_que_le_moteur_lit`
et `test_le_releve_des_lectures_observe_le_moteur_javascript` (neufs) ;
`lectures_du_modele` rejoint les scripts de `test_chargeurs_a_part.py` qui ne
bâtissent plus le `Simulateur`. Vus rouges, puis verts. `-m rapide` : vert.

**Reste.** `contexte.simulateur`, que lisent la fabrique et le bilan du
compte ; le retrait des règles, avec l'accord du propriétaire.
