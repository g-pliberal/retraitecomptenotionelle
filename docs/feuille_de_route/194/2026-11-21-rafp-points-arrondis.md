# Action 194 : les points du RAFP, arrondis chaque année au point supérieur

Écart trouvé en confrontant le moteur à la calculette de points de l'ERAFP,
le 21 novembre 2026 (trois saisies, sur la règle des cinq cents saisies par
mois) ; corrigé sans accord préalable (règle 1 du projet, du 20 novembre
2026), relu sous Opus, à relire sous Fable.

## Le texte, relu dans l'index LEGI du 16 novembre 2026

Décret n° 2004-569, article 5 (LEGIARTI000006453303, en vigueur depuis le
19 juin 2004, sans autre version) : le nombre de points de l'année « est égal
au rapport entre les cotisations versées […] et la valeur d'acquisition du
point ». Il ne dit pas d'arrondi.

## Ce que la caisse fait

Sa calculette de points arrondit le total de l'année au point supérieur :
14,99 € par mois de part agent en 2005, 359,76 points, rendus 360 ; 15 € en
2015, 314,36, rendus 315 ; 15 € en 2026, 246,64, rendus 247. Le scénario 1
étant le droit tel que la caisse l'applique, le moteur arrondit comme elle.

## La correction

`arrondirLesPointsDeLAnnee` (`moteur/js/droit/acquerir.js`) regroupe les
crédits RAFP d'une même année et en arrondit le total au point supérieur, un
total entier ne montant pas. Le relevé des points lui-même, `droits.points`,
porte les points arrondis : la pension, le relevé et la conversion inverse
lisent les mêmes (relecture Opus). Pas de jumeau Python.

## Les tests

- `tests/js/rafp-arrondi-des-points.test.js` : les trois cas de la
  calculette ; l'arrondi du total de l'année ; un total entier et les autres
  régimes inchangés ; le relevé des points d'un fonctionnaire, entier chaque
  année. Vus rouges, puis verts.
- `erafp_calculette_points_2026`, exemple officiel : 36 000 € en 2026 dont
  10 % de primes, 247 points (246,64 avant la correction). L'oracle passe
  désormais `part_primes` au relevé.

## Ce qui reste

Les témoins de simulation bougent (68 écarts sur 937 cas avant le
complément, environ +0,1 % sur le RAFP de dix cas de fonctionnaire) : ils se
refont au tour de ce patch sur `main`, par `construire_temoins.py`, avec le
témoin du droit.
