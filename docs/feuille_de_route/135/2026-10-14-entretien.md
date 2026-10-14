# L'entretien du 14 octobre : la tête détachée publiée, l'action 119 archivée, les textes inscrits

**Le 14 octobre 2026, la demande** (session d'entretien, une de cinq) : faire
publier `scripts/pousser.sh` depuis une tête détachée ; clore l'action 119 si
elle n'a plus d'étape ; relancer `python scripts/textes.py --inscrire`, que la
session de l'action 145 avait laissé la nuit précédente.

- *La tête détachée.* Une session créée par une autre session part détachée,
  et le script refusait (« HEAD détachée, rien poussé ») : deux sessions de
  nuit l'ont subi. Il publie désormais `HEAD` sur `main` comme d'habitude ; la
  branche de session reste vide, et les deux blocs qui la font suivre (la
  référence distante, l'amont local) ne font rien. Tous les autres refus
  demeurent, sur le même chemin. `tests/test_pousser.py` éprouve, sur des
  dépôts jetables, quatre cas détachés : la publication sans branche créée
  ni tête rattachée, le rebasage sur un `main` qui a avancé, le refus d'un
  conflit, le refus d'une adresse nominative.
- *L'action 119.* Sa section le confirme : toutes ses étapes sont faites, et
  ses deux restes — l'arrêté de 1982 et la solidarité de 1979, estimés faute
  du fac-similé du Journal officiel, que Légifrance ne met pas en données
  ouvertes ; ce qu'achètent les huit taux spécifiques de l'Arrco des cultes —
  vont au propriétaire, aucun à une session. Le « Ce qui reste » de la
  section, plus ancien, ne liste que des points faits depuis. Section passée
  telle quelle à la fin de `docs/archives/feuille_de_route.md`, statut
  `fait`, son bloc « Reprise » gardé et suivi d'un paragraphe de clôture ;
  ses notes sous `docs/archives/feuille_de_route/119/`.
  `conservation.py --depuis HEAD` ne relève que le titre, dont le statut
  change ; le tableau de bord, refait.
- *Les textes.* L'index LEGI, absent du conteneur, récupéré de la release
  puis mis à jour (incréments jusqu'au 13 octobre). L'inscription ajoute
  41 textes et 1 045 rédactions « à examiner », et clôt la fin de cinq
  rédactions que des suivantes remplacent ; pour l'essentiel, les textes que
  citent les fiches du 13 octobre ; relancée, elle n'ajoute rien. Le cliquet
  reste à 9 773 rédactions sans statut.

Reste au propriétaire : les deux restes de l'action 119 ci-dessus.
