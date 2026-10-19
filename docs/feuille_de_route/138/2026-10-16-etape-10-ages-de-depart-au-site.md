# Étape 10, première partie : plusieurs âges de départ côte à côte, sur la page des résultats

**Reprise, au 19 octobre 2026.** Fait : plusieurs âges de départ côte à côte
(16 octobre, `partirPlusTotOuPlusTard`) ; le 19, les droits contrefactuels —
la carrière saisie au 31 août 2023 et sous la loi de 2023 sans la suspension,
l'âge légal, la durée et la carrière longue recouverts
(`Parametres.droit_contrefactuel`), dans le dépliant « Avec ou sans la réforme
de 2023 » (`avecOuSansLaReforme`, `pages.js`). Reste, une session par point :
le contrôle d'un relevé ; l'indice majoré ; le solveur inverse. Puis le retrait
du jumeau `cycle_de_vie.py` (action 161). Détail : « Ce qui reste » de la note
`2026-10-19-etape-10-droits-contrefactuels.md`.

**La demande.** Le premier point de l'étape 10 de l'action, le reste 1 de la
note `2026-10-16-etape-9-ages-de-depart-au-portage.md` : montrer, pour la
carrière saisie, plusieurs âges de départ côte à côte, avec ce que le portage
calcule désormais — les flux, les conventions, l'âge d'équilibre, les revenus
nets, l'impôt. Ni les droits contrefactuels, ni le contrôle d'un relevé, ni
l'indice majoré, ni le solveur inverse. Session du 16 octobre, une parmi
treize, la seule sur les pages.

**Ce qui est fait.**

- `contexte.js` : `balayageDeLEstimation(saisie, pas = 1, cor = false)` rend,
  à chaque âge d'`agesBalayes`, le `Depart` de `balayageDUneCarriere`, après
  impôt (barème suivant les prix), et la comparaison qui en passe les
  montants aux euros de la page — le scénario 6 reporté liquide plus tard
  que les autres, et `Depart.annee` est celle du scénario 1. Les conditions
  de `departsDeLEstimation` (saisie par la pension, pensions datées par la
  saisie, départ passé) passent dans `_estimation`, que les deux partagent.
  Pas de jumeau Python : le site seul le montre.
- `pages.js` : le dépliant « Partir plus tôt ou plus tard », sous « Pour aller
  plus loin », entre la trajectoire et la fourchette. Chaque année de l'âge
  d'ouverture au taux plein automatique, trois tableaux : la pension nette du
  premier mois des quatre systèmes, en euros de la page ; le système 1 sur
  toute la retraite — années de retraite espérées, remplacement net et après
  impôt, patrimoine retraite en années de dernier revenu, multiple du
  minimum vieillesse ; le rendement réel des quatre systèmes. Puis l'âge
  d'équilibre de la génération dans le compte notionnel (`ageDEquilibre`).
  Convention de l'OCDE, dite dans une bulle.
- `tests/test_estimation_du_site.py` : le premier tableau, ligne à ligne,
  contre `balayage_d_une_carriere` du Python ; le premier et le dernier âge,
  contre `ages_de_l_estimation` ; rien pour qui est parti.

**Ce que montrent les mesures.** Le pas d'un an, et non d'un trimestre, tient
le dépliant à quatre ou cinq âges et à 150 à 270 ms de calcul par page dans
node. Pour un salarié né en 1985, le système 1 rend de +0,4 à +0,5 % réels par
an selon l'âge, le système 2 −2,8 %, le 3 autour de 0 %, le 4 −0,2 % ; son
âge d'équilibre est de 67 ans et 9 mois. 52 des 75 rendus de page témoins
gagnent le dépliant, sans autre changement.

**Ce qui reste** de l'étape, dans l'ordre, une session par point :

1. Les droits contrefactuels : au 31 août 2023, et la loi de 2023 sans
   suspension.
2. Le contrôle d'un relevé.
3. L'indice majoré.
4. Le solveur inverse.
5. Au dépliant, s'il le faut : la convention du COR en bascule (`cor`), le
   pas du trimestre, les systèmes 5 et 6 ; les âges de départ d'une carrière
   saisie par la pension ou déjà liquidée n'y sont pas, comme dans
   l'estimation officielle.
