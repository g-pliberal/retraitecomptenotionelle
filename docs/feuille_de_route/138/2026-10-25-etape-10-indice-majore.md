# Étape 10, quatrième partie : l'indice majoré, multiplié par la valeur du point

**La demande.** Le reste 3 de la note du 16 octobre
(`2026-10-16-etape-10-ages-de-depart-au-site.md`, « Ce qui reste »), le
premier point de son bloc : l'indice majoré. Le registre le tient du
simulateur de SUD éducation (`simulateur_sud_education`, chantier 138.10) :
« Il saisit l'enseignant par son corps et son échelon. Le dépôt n'a aucun
champ d'indice ; […] ce qui se reprend est un champ « indice majoré »,
multiplié par la valeur du point. » Ni le solveur inverse, ni les grilles,
qui sont l'action 158. Session du 25 octobre, la seule sur les pages.

**La forme du champ.** Le registre la dit, et les conventions du site font le
reste : elle ne revenait pas au propriétaire. Celle du micro-entrepreneur
(étape 12) : un menu, « Fonctionnaire, vous saisissez », qui ne paraît
qu'avec une période du statut, change la lecture du revenu de ses lignes,
sans un champ de plus par ligne. Celle des euros saisis, qui sont ceux
d'aujourd'hui : l'indice se multiplie par la valeur du point de l'année du
modèle, puis le modèle suit le traitement le long du salaire moyen, comme
tout revenu. Celle de la part de primes, que la fiche de paie partage : le
traitement n'est que la part `1 − primes` de la rémunération, qui vaut donc
l'indice fois le point, divisé par un moins la part.

**La veille.** Aucune règle du scénario 1 ne change, et le journal de veille
n'a pas d'entrée. La valeur du point est celle que le paquet garde pour le
minimum garanti, `point_indice_fonction_publique.csv`, lue au LEGI (décret
n° 85-1148 du 24 octobre 1985, article 3) : 5 907,34 € par an pour cent
points, en vigueur au 1er janvier 2026.

**Ce qui est fait.**

- La saisie (`saisie.js`) : le champ `indice`, vide ou `majore` (`INDICES`) ;
  `STATUTS_A_L_INDICE`, les douze statuts dont le régime de base est, l'année
  du modèle, celui de l'État ou la CNRACL — les fonctionnaires titulaires,
  civils et militaires, des trois versants ; ni l'ouvrier de l'État, ni le
  fonctionnaire de Nouvelle-Calédonie, ni l'agent non titulaire.
  `enIndice(statut)` ; `niveauDe`, qui fait d'un indice la rémunération de son
  traitement, en toute unité et en tout mode ; le zéro refusé à la lecture
  (`verifierRevenu`), les bornes du revenu au calcul, redites en indices
  (`verifierNiveau`) ; l'activité après le départ, dont le revenu hérité du
  dernier métier reste un indice ; l'adresse (`indice=majore`).
- L'échelle (`Echelle`) : `point` et `annee`, `traitement`, `remuneration`,
  `indice`, l'inverse, et `indicesDansLesBornes`, les indices entiers extrêmes
  que le modèle accepte. Le contexte lui donne le point en vigueur au
  1er janvier de l'année du modèle, lu dans la série du minimum garanti
  (`valeurDuPoint`, `contexte.js`). Pas de jumeau Python : la saisie n'en a
  plus (action 161).
- La page : le menu (`indiceFormulaire`) et sa bulle, qui cite le décret ; le
  champ « Indice majoré » (`champIndice`), dont l'aide chiffre le traitement,
  puis la rémunération primes comprises ; les bascules d'unité et des
  montants passent l'indice tel quel, comme un chiffre d'affaires ;
  l'avertissement des statuts sans conversion ne le compte pas ; le revenu
  que la pension suppose dit son indice (« Soit l'indice majoré 632, au point
  de 2026, avec 20 % de primes »), que le lien de reprise écrit.
- Les tests : quinze, dans `tests/test_web_saisie.py`, à la suite de ceux du
  micro-entrepreneur — les traitements posés à la main (l'indice 500 vaut
  2 461,39 € bruts par mois, 3 076,74 € avec 20 % de primes ; l'indice 600,
  2 953,67 €), la liste des statuts recoupée aux affiliations, les bornes du
  refus acceptées et leurs voisines refusées. Les témoins : deux simulations
  (`fonctionnaire_indice_majore`, `…_et_primes`) et deux rendus
  (`simuler_indice_majore`, au formulaire figé entier, et `…_par_pension`).
  Au registre, le point de `simulateur_sud_education` passe à `repris`.

**Ce que montrent les mesures.** L'indice 500 vaut 0,69 fois le salaire moyen
de 2026, quand le même nombre lu en euros en valait 0,14. Le modèle accepte
les indices de 73 à 7 218 sans primes, de 58 à 5 774 avec 20 % : les bornes
du revenu, non celles du barème. Aucun des 907 témoins de simulation ne
bouge ; deux rendus de page sur 79 gagnent le menu, ceux dont une période est
de fonctionnaire (`simuler_demande_de_pension`,
`simuler_radiation_invalidite`), sans autre changement. Au navigateur, le
pilote de `tests/test_ecrans.py`, joué une fois sur les deux pages de
l'indice, ne trouve aux cinq largeurs ni débordement, ni grand vide, ni
erreur ; ses routes n'en ont pas gagné.

**Ce qui reste.**

1. Le relevé. Ses lignes portent un revenu en euros de l'année, et celui d'un
   fonctionnaire n'en porte pas (`docs/limites/5-hors-du-modele.md`, « reste
   à saisir ») : y lire un indice au point de chaque année est le choix de
   l'étape 4 de l'action 158 — le pré-remplissage écrit le traitement divisé
   par un moins la part de primes, ou la saisie apprend à recevoir le
   traitement seul —, à faire avec elle.
2. Le barème : les bornes du champ sont celles du revenu ; le minimum de
   traitement (l'indice majoré 366 payé à tout indice brut jusqu'à 367 depuis
   2024, note de l'étape 1 de l'action 158) et le haut de l'échelle viendront
   avec les grilles.
3. Les restes de la note du 16 octobre : le solveur inverse ; puis, s'il le
   faut, le dépliant des âges de départ. Puis le retrait du jumeau
   `cycle_de_vie.py` (action 161).
