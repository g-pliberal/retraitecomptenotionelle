# Le rapport de la Cour sur les droits de succession : lu, publié, et le patrimoine des défunts qui recoupe la reprise

**Le 11 octobre 2026 : le rapport de la Cour des comptes, lu depuis le poste
du propriétaire, déposé sur la release, et recoupé avec la reprise sur
succession.**

- *La demande.* Le propriétaire, dans une session de bureau, fait faire ce
  qu'une session du cloud ne peut pas. Ce rapport en est : `ccomptes.fr` lui
  ferme la connexion, et il attendait dans `data/brut/` depuis le
  22 septembre sans avoir été lu. « Fais le point 4 » — le lire et en saisir
  les chiffres, ou le publier sur la release —, puis « Publier les deux ».
- *Ce que le rapport ne donne pas.* Le manifeste lui prêtait la distribution
  des successions déclarées par tranche d'actif net : elle n'y est pas. La
  DGFiP enregistre les déclarations dans une application de gestion, « et
  non de contrôle ou de production de statistiques » (p. 78), et les
  tableaux 9, 10 et 14, qu'on disait à lire d'abord, portent le contrôle
  fiscal. Le tableau 7 compte les déclarations de 2022 : 354 443, dont
  165 595 payantes (47 %), pour 673 637 décès ; plusieurs peuvent porter sur
  une même succession, et une succession en ligne directe d'actif brut
  inférieur à 50 000 € est dispensée de déclaration (p. 36).
- *Ce qu'il donne.* Son graphique n° 18 (p. 65) : le patrimoine moyen des
  personnes décédées en 2018, par décile de ce patrimoine, d'après la DG
  Trésor (document de travail n° 2021/5, microsimulation sur l'enquête
  Patrimoine 2014-2015 de l'INSEE) — 0, 7 000, 42 000, 81 000, 110 000,
  149 000, 198 000, 268 000, 408 000 et 1 350 000 €, une moyenne de
  261 300 €. Le zip de données de la Cour le porte (`G18.csv`) :
  `scripts/fetch/cdc_droits_succession.py`, le lecteur que le manifeste
  attendait, l'écrit dans `macro/patrimoine_defunts.csv` après en avoir
  confronté trois valeurs au texte de la page. Aucun calcul ne le lit
  (`memoire.HORS_DU_MODELE`).
- *Le recoupement.* Chaque décile porté à sa moyenne, une succession couvre
  au plus Σ 0,1·min(A, m) d'une avance A — une borne haute, `min` étant
  concave. La couverture que le modèle tire des ménages de retraités (COR,
  2018, `donnees/patrimoine.py`) la dépasse à toute avance :

  | Avance | Ménages de retraités | Leur quart le plus modeste | Défunts de 2018, au plus |
  |---:|---:|---:|---:|
  | 5 000 € | 97,8 % | 96,3 % | 90,0 % |
  | 20 000 € | 91,3 % | 82,0 % | 83,5 % |
  | 50 000 € | 83,3 % | 64,1 % | 79,8 % |
  | 100 000 € | 77,0 % | 48,1 % | 73,0 % |
  | 150 000 € | 71,9 % | 39,0 % | 65,9 % |

  De trois à neuf points au moins, entre 5 000 et 150 000 € : le patrimoine
  d'un ménage compte souvent celui de deux personnes, et un défunt sur dix
  ne laisse rien. C'est l'écart que `donnees/patrimoine.py` déclare — une
  avance par succession, qui surestime la couverture — et que
  `cout._reprises_successions` corrige en partie en confrontant au
  patrimoine l'avance multipliée par le nombre d'avances par succession. Le
  graphique en donne l'ordre de grandeur, toutes pensions confondues ; il ne
  dit rien des bénéficiaires, aux pensions basses, dont le quart le plus
  modeste reste la population. `tests/test_donnees.py` tient le recoupement.
- *La release.* Le PDF et le zip, retéléchargés de `ccomptes.fr` le même
  jour à l'empreinte identique, sont déposés sur `documents-apportes` avec
  l'accord du propriétaire, sous les conditions de reproduction du site,
  relues sur le site (source citée, document intact) : le manifeste les
  déclare en `miroir`, avec leur licence et leur mention, et
  `source_locale.py --recuperer` les rapporte dans une session du cloud.
- *Ce qui reste.* Rien ne change au point 1 : le fichier individuel de
  l'enquête Histoire de vie et Patrimoine, qui attend une inscription, et la
  phrase du programme. Le document de travail de la DG Trésor n'a pas été
  lu ; s'il ventile le patrimoine des défunts par âge ou par niveau de
  vie, il vaudrait mieux que le graphique. Reprendre sur le patrimoine des
  défunts plutôt que sur celui des ménages est un choix de modèle, qui
  baisserait les reprises : il revient au propriétaire, et n'est pas fait.
