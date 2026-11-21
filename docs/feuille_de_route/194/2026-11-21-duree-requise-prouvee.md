# Action 194 : la durée requise, huit parties prouvées

Le 21 novembre 2026. Session sur Opus 5.5, comme Gilles l'a choisi pour ces
briefs ; un point tranché par une session Fable 5.2. Posée sur la mise en
versions de la fiche (action 191, étape 3, deuxième session), non publiée à
son début : à publier après elle.

## Ce qui est fait

**Huit grilles indépendantes**, `data/reference/preuves/grille_duree_requise_*.yaml`,
une par version de la fiche `duree_requise_par_generation` :
`cent_cinquante` (7 cas), `escalier_de_1993` (23),
`decembre_1942_au_1er_janvier_2003` (6), `cent_soixante` (13), `loi_de_2003`
(28), `loi_de_2014` (21), `loi_de_2023` (25), `suspension_de_2025` (18). Les
huit parties sont au cliquet ; la carte en compte quinze prouvées.

**Une grandeur de plus**, `duree_requise_a_l_effet` (`tests/test_oracle.py`) :
la durée que `ouvrir.dureeRequise` oppose à une pension du régime général
prenant effet au mois de la liquidation, que l'assuré puisse ou non partir ce
jour-là. Aucun ajout au pont : la fonction y était.

**Une correction au texte.** R. 351-45, II (décret n° 93-1022, rédaction du 28
août 1993) n'a pas de date d'application différée : l'escalier vaut dès ce jour,
et non au 1er janvier 1994. Né le 1er janvier 1934, pension du 1er octobre
1993 : 151 trimestres au texte, 150 avant. La période 1983-1993 du régime
général lit désormais la fiche au lieu de ses 150 trimestres écrits en dur.
Aucune pension ne bouge (937 témoins de simulation, 86 rendus de page) : nul ne
pouvait partir avant soixante ans.

## Comment la grille s'est faite

Une session sans le code (`/mnt/project-files/justesse/2026-11-21-duree-requise-prouvee/aveugle/`)
a reçu la consigne, 114 couples naissance, date d'effet, et les index LEGI et
JORF du 16 novembre 2026 ; elle a trouvé seule ses textes (R. 351-27, R. 351-45,
L. 161-17-3, loi n° 2003-775, article 5, les décrets 2010-1734 à 2013-1155,
l'article 70 du décret n° 45-179) et proposé 30 cas. Un guetteur n'a noté
aucune lecture des deux copies du dépôt. Accord sur 133 des 144 cas.

## Les onze écarts

- Né le 1er janvier 1934, effet au 1er octobre 1993 : le moteur, corrigé.
- Nés en 1949 et 1950, effet de 2003 à 2008 (quatre cas) : elle lit 161 ou 162
  par le V de l'article 5 de la loi de 2003 (la durée en vigueur aux soixante
  ans). Retenu 160 : R. 351-45, I, « quelle que soit la date de naissance »,
  la circulaire Cnav 2008/41 (§ 211, « à compter du 1er janvier 2009 »), et
  l'avis de Fable 5.2. Sans effet sur le taux d'une carrière longue (168).
- Nés en 1953, effet de janvier à juin 2011 (quatre cas) : 165 au décret,
  164 pour la caisse (circulaire 2011/25, selon la date de la demande) ; la
  grille retient la caisse et chiffre le texte.
- Nés à compter de 1958, effet avant le 22 janvier 2014 (trois cas) : aucun
  texte ne fixe leur durée ; elle retient la dernière fixée (166), le moteur
  celle de la loi de 2014 (167). Hors grille, question à Gilles.

## Coût

Cinq commits par-dessus l'étape 3b, 18 fichiers ; une session aveugle de neuf
minutes, une consultation Fable de vingt secondes ; trois heures en tout.
