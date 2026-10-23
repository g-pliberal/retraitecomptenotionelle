# modele-as, rejoué sur des revenus de dirigeant

**La demande**, le 23 octobre 2026 : la vague du jour, où la session de suivi
« Qu'est-ce qu'il reste à faire ? » lance, sur la demande du propriétaire
(« Fait ça », en réponse à l'offre d'une session par chantier qu'une session
peut mener seule), douze sessions en parallèle, une étape chacune. Pour
l'action 137 : « confronter `modele_as` au scénario 1, le premier des quatre
que le tableau de bord met en tête (code ouvert, jamais confronté, sans
dépendance au registre), son calcul rejoué sur des revenus de dirigeant […].
Ce que tu trouves va au registre (`data/reference/referents.yaml`) ; un écart
chez nous se corrige par le test qui le reproduit, sous la veille du droit ;
un écart chez eux se déclare. »

**Fait, le 23 octobre 2026 : le calcul rejoué ; le dépôt a raison, et
modele-as a deux erreurs, que modele-social partage.**

- *Ce qui a tourné.* Le paquet npm `modele-as` 0.1.0 (16 juillet 2026, MIT),
  installé à part dans le bloc-notes de la session avec publicodes 1.10.4,
  sans ses scripts, et interrogé hors navigateur : pour la rémunération brute
  annuelle d'un dirigeant assimilé salarié, au 1er juillet de 2024, 2025 et
  2026, ses trimestres validés et ses points Agirc-Arrco. La grille compte
  171 rémunérations, de 0 à 500 000 €, serrées autour de chaque seuil d'un à
  quatre trimestres (à 7, 6, 3, 1 et 0,5 € près), du plafond et de huit
  plafonds. Le dépôt, qui saisit ce dirigeant en salarié du privé (fiche
  `un_statut_par_annee`), les calcule par `trimestres_valides` (`macro.py`)
  et par `points_de_l_annee` (`droit/releve.py`), le moteur entier, en
  salarié cadre. Pour rejouer : `npm install --ignore-scripts modele-as@0.1.0
  publicodes@1`, puis `new Engine(regles).setSituation({date: '01/07/2024',
  'assimilé salarié . rémunération . brute': '6990 €/an'})` et ses deux
  règles, `protection sociale . retraite . trimestres` et `… . AGIRC ARRCO .
  points acquis`.
- *Ce qui concorde.* Ses paramètres sont ceux du dépôt : le SMIC du 1er
  janvier (11,65, 11,88 et 12,02 €) et celui de juin 2026 (12,31 €) ; le
  plafond (46 368, 47 100 et 48 060 €) ; la valeur d'achat du point (19,6321
  € en 2024, 20,1877 € en 2025 et en 2026) et sa valeur de service (1,4386 €
  depuis novembre 2024, inchangée en novembre 2025) ; les taux de vieillesse
  (6,90 + 8,55 % plafonnés ; 0,40 + 2,02 %, puis 2,11 % en 2026,
  déplafonnés) et ceux de l'Agirc-Arrco (7,87 et 21,59 %). Hors des deux
  erreurs, ses trimestres et ses points sont ceux du dépôt.
- *Ses deux erreurs.* Il arrondit à l'euro le revenu MENSUEL cotisé
  (`arrondi: oui`) avant de le comparer au seuil : à moins de 6 € d'un seuil,
  il valide un trimestre de trop ou de moins, 27 rémunérations de la grille
  sur 171. Pour 6 990 € en 2024, exactement 600 heures de SMIC, la
  rémunération que se fixe le dirigeant qui veut ses quatre trimestres, il
  n'en valide que trois : 582,50 € par mois, devenus 582 €. R. 351-9 en
  vigueur (LEGIARTI000053335598, lu dans l'index LEGI) compte « le salaire
  annuel ». Et il compte les points de la tranche 1 sur la cotisation
  divisée par 1,27, 6,197 % de l'assiette au lieu de 6,20 % : 97,53 et
  345,52 points pour les deux exemples du livret n° 3 de l'Agirc-Arrco, qui
  en écrit 97,58 et 345,59 ; c'est l'erreur que le dépôt avait chez lui
  jusqu'au 5 octobre. Les deux sont au registre, sur la ligne `modele_as`.
- *La famille.* `modele-social` 11.1.0, rejoué pour le salarié sur sept des
  mêmes cas, rend les mêmes trimestres et les mêmes points : mêmes règles,
  mêmes erreurs, déclarées une fois, sur la ligne de modele-as, et rappelées
  dans la note de la sienne. À la tête de mon-entreprise (`01861d0`, 16
  octobre), les deux règles n'ont changé que de nom
  (`protection-sociale/retraite-base.publicodes:41-72`,
  `retraite-complémentaire.publicodes:31-32`) ; rien de ses règles de
  retraite n'a bougé depuis `05cb5be`, le commit lu le 4 octobre.
- *Ce que les tests tiennent* (`tests/test_referents.py`) : onze
  rémunérations et ce que modele-as en rend — les seuils, les deux exemples
  du livret, le plafond, huit plafonds. Les trimestres du dépôt sont les
  siens, sauf aux quatre rémunérations où il arrondit, où ce sont ceux de R.
  351-9, posés à la main ; les points du dépôt sont les siens, la tranche 1
  comptée à 6,20 %. Et la version que sa ligne doit nommer, vue rouge avant
  le registre. Le tableau de bord le compte désormais confronté : 25
  modèles, et 3 à confronter en premier.

**Ce qui reste.** Le premier modèle qui reste à confronter, dans l'ordre du
registre, est Catala, au droit de sa date ; puis le simulateur de SUD
éducation et Nos Retraites. Une piste, non suivie : modele-ti arrondit aussi
son revenu cotisé (`retraite-base.publicodes:74-80`, au commit `01861d0`),
dans une unité que cette session n'a pas vérifiée ; au mois, les trimestres
des indépendants auraient la même erreur près des seuils. Elle se vérifie en
le rejouant, quand sa ligne se relira. Les autres restes du bloc « Reprise »
ne bougent pas. Au propriétaire, rien à trancher ; aux pages, rien : le site
ne lit pas le registre.

*Fichiers.* Le registre (lignes `modele_as` et `modele_social`),
`tests/test_referents.py`, `docs/etat.md`, la feuille de route, cette note et
l'entrée du journal de veille. Ni fiche, ni règle, ni page. Les scripts qui
ont fait tourner modele-as sont restés hors du dépôt, qui n'a pas npm pour
dépendance.
