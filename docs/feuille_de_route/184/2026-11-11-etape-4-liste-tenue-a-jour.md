# Étape 4 : la liste des textes tenue à jour — les textes généraux par leurs articles cités, l'inscription, GitHub qui la lance chaque lundi

**Reprise, au 11 novembre 2026.** Rien n'est commencé. Le propriétaire a
tranché le 11 novembre : les quatre textes généraux de la fonction publique
n'entrent dans la liste de contrôle des textes que par les articles qu'une
fiche cite, et GitHub lance l'inscription des rédactions nouvelles chaque
lundi. Trois gestes, dans l'ordre, chacun son test d'abord : le périmètre et
la sélection de `scripts/textes.py` ; l'inscription des rédactions en
attente, pour de bon ; le workflow `index-dila.yml`, qui est une garde, et
dont l'accord est donné plus bas, mot pour mot. L'étape 5 retouche le même
workflow : rattraper `main` avant d'y toucher. Aucune règle du scénario 1
n'est en jeu. Commencer par « Ce qu'il y a à faire », ci-dessous.

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
