# Étape 4 : la liste des textes tenue à jour — les textes généraux par leurs articles cités, l'inscription, GitHub qui la lance chaque lundi

**La demande, le 11 novembre 2026.** La session qui a mesuré les outils (note
`2026-11-11-sorties-et-temps-des-outils.md`) a demandé au propriétaire :
« Êtes-vous d'accord pour que GitHub lance l'inscription chaque lundi ? Cela
modifie un workflow, donc une garde. Sur les 1 942 rédactions en attente, 856
viennent de quatre textes généraux de la fonction publique (lois n° 84-16,
84-53 et 86-33, décret n° 85-1148). Faut-il les inscrire en entier, ou
seulement les articles que les fiches citent ? Je recommande les seuls
articles cités. » Sa réponse : « oui pour les deux, articles cités
seulement ». Le second « oui » porte sur la passe de lecture, l'étape 6.

**Ce qui est su, mesuré le 11 novembre** sur l'index LEGI à jour de ce jour.

- La dernière inscription date du 3 novembre
  (`data/reference/textes/inscription.yaml`). Rejouée à blanc, elle apporterait
  1 942 rédactions « à examiner » : 1 834 de 52 textes nouveaux à la liste,
  108 de textes qui y sont déjà.
- `selection()` de `scripts/textes.py` fait entrer un code par le seul article
  cité, avec toutes ses rédactions, et tout autre texte en entier
  (`perimetre.yaml`, `textes_cites`).
- Les quatre textes généraux, sous le titre que l'index leur donne, et ce
  qu'ils apporteraient par leurs seuls articles cités :

| Titre dans l'index | Rédactions | Articles cités | Rédactions gardées |
|---|---|---|---|
| Loi n° 84-16 du 11 janvier 1984 portant dispositions statutaires relatives à la fonction publique de l'Etat (1). | 126 | 34 | 21 |
| Loi n° 84-53 du 26 janvier 1984 portant dispositions statutaires relatives à la fonction publique territoriale (1). | 286 | 57 | 29 |
| Loi n° 86-33 du 9 janvier 1986 portant dispositions statutaires relatives à la fonction publique hospitalière. | 158 | 41 | 28 |
| Décret n° 85-1148 du 24 octobre 1985 modifié relatif à la rémunération des personnels civils et militaires de l'Etat, des personnels des collectivités territoriales et des personnels des établissements publics d'hospitalisation | 286 | 3 et 7 | 73 |

  Les trois lois sont citées par la fiche `taux_plein_a_soixante_cinq_ans`,
  le décret par `marins_salaire_de_reference`. Des 856 rédactions, 151
  restent, 705 sont écartées : l'inscription apporterait 1 237 rédactions.
  Ces comptes valent pour l'index et les fiches du 11 novembre ; ils se
  refont le jour de l'étape.

**Ce qu'il y a à faire.**

1. *Le périmètre.* `data/reference/textes/perimetre.yaml` déclare les textes
   généraux qui n'entrent que par leurs articles cités, chacun sous son titre
   et avec son pourquoi, comme il le fait pour les codes ; `selection()` les
   traite comme un code hors de ses chapitres. Le test d'abord, dans
   `tests/test_textes.py`, sur une table `doc` de poche, à la manière de
   `test_deux_textes_du_meme_jour_ne_partagent_pas_une_cle` : un décret de
   régime cité entre en entier, un texte général déclaré n'apporte que les
   rédactions de l'article cité. D'autres textes généraux pourront s'y
   déclarer de même ; la décision du propriétaire ne porte que sur ces quatre.
2. *L'inscription.* `python scripts/fetch/dila_index.py legi --recuperer`,
   puis `--mettre-a-jour`, puis `python scripts/textes.py --inscrire`. Dire
   dans la note combien de rédactions entrent, contre les 1 237 attendues, et
   d'où vient l'écart s'il y en a un. Les rédactions inscrites sont « à
   examiner » : le cliquet ne bouge pas (`python scripts/textes.py`,
   `tests/test_textes.py`).
3. *Le workflow.* Dans `.github/workflows/index-dila.yml`, pour LEGI, après
   la mise à jour de l'index : l'inscription, puis le commit sur `main` de ce
   qu'elle écrit, sous `github-actions[bot]`, sans forcer et sans course avec
   une session qui pousse — lire comment `tests.yml` et
   `scripts/publier_fabrique.sh` publient ce que GitHub fabrique, et reprendre
   ce chemin. Un envoi fait avec le jeton d'un workflow ne déclenche pas
   `tests.yml` : s'assurer que le tableau de bord et les chiffres ancrés
   suivent, et que la suite complète juge ce commit. Le commit porte
   `Garde-modifiée:` et sa raison ; l'accord est celui de la demande
   ci-dessus. Le test d'abord, là où les workflows ont les leurs.
4. *La procédure.* `docs/veille_droit.md` dit encore à chaque session de
   lancer l'inscription en ouvrant : y dire ce que GitHub fait désormais, et ce
   qui reste à la session.

**Fini quand** : les trois comportements ont leur test, vu rouge puis vert ;
`python -m pytest -m rapide` et les tests de la zone passent ; la liste est
inscrite et poussée ; le workflow a tourné une fois à la main, ou la note dit
pourquoi il ne l'a pas pu ; cette note raconte l'étape, son bloc « Reprise »
ôté ; l'entrée du journal de veille est écrite.

**Ce qui a été fait, le 11 novembre 2026.** Les quatre gestes, chacun son
test d'abord, vu rouge puis vert.

1. *Le périmètre.* `perimetre.yaml` porte une liste `textes_generaux`, chaque
   texte sous le titre que l'index lui donne et avec son pourquoi ; les quatre
   textes de la décision y sont. `selection()` traite un texte général déclaré
   comme un code hors de ses chapitres : seul l'article cité entre, avec
   toutes ses rédactions. Deux tests dans `tests/test_textes.py` : sur une
   table de poche, un décret de régime cité entre en entier et un texte
   général déclaré n'apporte que l'article cité ; sur le dépôt, les quatre
   textes sont déclarés, chacun avec son pourquoi.
2. *L'inscription.* Sur l'index LEGI mis à jour jusqu'à l'incrément du 11
   novembre 2026 (20261111-211545), `textes.py --inscrire` a apporté 1 237
   rédactions « à examiner », le compte attendu, sans écart : 21 de la loi
   n° 84-16 (article 34), 29 de la loi n° 84-53 (article 57), 28 de la loi
   n° 86-33 (article 41), 73 du décret n° 85-1148 (articles 3 et 7), soit 151 ;
   sans la déclaration, il en serait entré 1 942. Elles viennent de 59 textes,
   dont 52 nouveaux à la liste ; 366 sont en vigueur ou à venir. La liste
   tient 17 625 rédactions de 279 textes, contre 16 388 de 227. Le cliquet n'a
   pas bougé : 9 283 rédactions sans statut.
3. *Le workflow.* `.github/workflows/index-dila.yml`, pour LEGI seul et une
   fois l'index publié : il installe le paquet, lance
   `scripts/publier_inscription.sh python scripts/textes.py --inscrire`, puis,
   si un commit est parti, `gh workflow run tests.yml` sur la même branche,
   ce qui lui demande la permission `actions: write`. Le script est neuf. Il
   se place sur le dernier `main`, inscrit, commite ce qui a changé sous
   `data/reference/textes/` et cela seul, sous l'identité noreply du robot,
   et pousse sans forcer. Poussée refusée, parce qu'une session a poussé
   entre-temps, il refait l'inscription sur la nouvelle tête, trois fois au
   plus : l'inscription ne coûte que quelques secondes, la refaire vaut mieux
   que rebaser un fichier de 17 000 lignes. Rien d'écrit, rien de commité.
   `tests.yml`, lancé par `workflow_dispatch`, repart du dernier `main`,
   refait le tableau de bord et les chiffres ancrés, et juge. Quatre tests
   dans `tests/test_outillage.py`, les trois premiers dans un dépôt jetable :
   l'inscription se publie sur le dernier `main` ; elle se refait quand une
   session la devance ; une inscription qui n'écrit rien ne commite rien ; le
   workflow enchaîne les étapes dans cet ordre, pour LEGI seul. Le commit
   porte `Garde-modifiée:`, sur l'accord cité plus haut, relu à sa source : le
   message du propriétaire dans la session qui l'a demandé.
4. *La procédure.* `docs/veille_droit.md`, « Au début » : la session ne lance
   plus l'inscription en ouvrant ; elle ne la lance que pour un texte qu'elle
   vient de citer ou paru dans la semaine, et déclare d'abord un texte général
   au périmètre. `docs/architecture.md`, § 6.6, « Où elle vit », dit les deux
   mêmes choses.

**Les comptes, pour l'étape 6.** Le 11 novembre 2026, après l'inscription :
100 rédactions en vigueur ou à venir que les fiches n'ont pas lues, sur 59
fiches, contre 92 sur 56 avant elle ; comptées par fiche, une rédaction que
deux fiches citent valant deux, 118 contre 110. En tout, passées comprises,
2 539 rédactions non lues sur 173 fiches, contre 2 290 sur 168. Les huit
rédactions en vigueur ou à venir qui s'ajoutent touchent cinq fiches :
`assiette_rco_independants` (décret n° 2012-443, article 4),
`decret_2026_418_liberaux` (décret n° 49-579, article 4 ; décret n° 50-28,
article 2), `marins_salaire_de_reference` (décret n° 48-1108, article 1 ;
décret n° 85-1148, article 3), `taux_plein_a_soixante_cinq_ans` (R. 653-2 du
code de la sécurité sociale ; loi n° 86-33, article 41) et
`un_statut_par_annee` (R. 711-24 du même code).

**Le workflow, lancé une fois à la main**, le 11 novembre 2026 à 23 h 44 UTC,
sur `main` (course 43122145529 d'« Index DILA »), a réussi en deux minutes.
Pour LEGI : l'index mis à jour et publié, le paquet installé, le dernier
`main` pris, l'inscription lancée. Elle a répondu « 0 rédactions nouvelles
inscrites », l'index étant celui que la session venait de lire, et le script
« Rien de neuf à la liste des textes : rien commité ». Ce que cette course n'a
donc pas montré sur GitHub : la poussée du commit par le jeton du workflow, et
le lancement de `tests.yml` qui la suit. Seuls les tests du dépôt jetable les
tiennent. La première course qui trouvera un incrément nouveau, celle du lundi
16 novembre 2026 à 4 h UTC, les jouera : y regarder qu'un commit « Inscrit par
GitHub » arrive sur `main` et qu'une course de « Tests » le suit.

**Ce qui reste, et qui revient au propriétaire.** `scripts/publier_inscription.sh`
pousse sur `main` depuis GitHub, comme `scripts/publier_fabrique.sh`, mais
n'est pas dans la liste des gardes de `scripts/pousser.sh` : une session peut
le retoucher sans accord. L'y ajouter retouche `pousser.sh`, qui est une
garde, et l'accord du 11 novembre ne portait que sur le workflow : la question
est posée au propriétaire, rien n'est fait. Chaque lundi, l'inscription
commite au moins `inscription.yaml`, qui dit jusqu'où l'index a été lu, et la
suite complète tourne donc une fois de plus par semaine.
