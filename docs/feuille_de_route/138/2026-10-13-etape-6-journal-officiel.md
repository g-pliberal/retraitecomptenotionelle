# Étape 6, deuxième partie : les montants de l'AVTS et du minimum vieillesse, relus au Journal officiel décret par décret

**La demande.** Le propriétaire, le 13 octobre 2026 : « la certification au
Journal officiel, décret par décret, des montants de l'AVTS et du minimum
vieillesse que lit `cnav_avts.py` » — le premier point de « Ce qui reste » de la
première partie. D'autres sessions tournant en parallèle, ne toucher ni à
`castypes.py`, `cas_types_csp.yaml` et `grille_large.py` (action 152), ni à
`cout.py` (action 147), ni aux pages du site.

**Ce que portent les index du dépôt, lus le jour même** (journal de veille du
13 octobre). Six cent treize titres, notices et articles des textes « fixant
le montant de divers avantages de vieillesse et d'invalidité », « de l'allocation
supplémentaire du Fonds national de solidarité » ou « portant revalorisation » de
l'un et de l'autre, de 1941 à 2007, dans les index JORF et LEGI ; les majorations
exceptionnelles, versées une fois aux allocataires, et l'outre-mer en sont
écartés.

- *Avant 1970*, le titre seul, ou une notice sans montant — « MODIFICATION DU
  TAUX PREVU A L'ART. 13 DE L'ORDONNANCE 45170 » — : la loi du 14 mars 1941, les
  lois de 1946 à 1956, les décrets de 1962 à 1969. Rien ne s'y certifie.
- *De 1970 à 1989, la notice*, en capitales : elle redit le plus souvent l'AVTS et
  sa date — « (2 250 FRS PAR AN A COMPTER DU 01-07-1973) », « FIXANT A 8500FRS PAR
  AN A COMPTER DU 01-01-1981 » —, le plafond une fois (n° 70-879). Les décrets de
  l'allocation supplémentaire n'y sont presque pas : leur titre ne nomme ni la
  vieillesse ni la retraite, et le filtre thématique de l'index (`THEMATIQUE`
  dans `dila_index.py`) les a laissés au dump. Le dump de juillet 2025, lu le
  même jour (1,7 Go, 6,9 millions de documents), les porte de 1968 à 1981, et
  leur titre en redit le montant — « FIXANT LE MONTANT DE L'ALLOCATION
  SUPPLEMENTAIRE DU FONDS NATIONAL DE SOLIDARITE: 5250FRS A COMPTER DU
  01-07-1977 » —, quatorze montants, qui redonnent ceux de la caisse ;
  jamais le plafond, que la caisse leur rapporte. Aucune ligne de plus ne s'y
  certifie : le certificateur reste sur l'index.
- *De 1981 à 2003, le texte*, article par article : dans LEGI depuis les décrets
  n° 81-1166 et 81-1167, dans le JORF depuis 1990. L'AVTS — « Sont portés à
  13 470 F par an à compter du 1er janvier 1987 et à 13 600 F par an à compter
  du 1er juillet 1987 : - le montant de l'allocation aux vieux travailleurs
  salariés » —, l'allocation supplémentaire, les « montants limites annuels »
  d'une personne seule et de deux époux.
- *De 2004 à 2006*, un arrêté « relatif à la revalorisation des pensions de
  vieillesse », qui ne fixe qu'un coefficient : 1,017, 1,02, 1,018. Appliquer un
  coefficient est un calcul, et un calcul ne se certifie pas.

**Ce qui est fait.**

- *Le certificateur* (`scripts/fetch/jorf_avts.py`, après `cnav_avts.py`) lit
  tous ces textes, non les seuls que la caisse cite, et range chaque montant dans
  sa série par ce que la proposition nomme : le plafond par le libellé qui suit
  son montant (« pour une personne seule », « pour deux époux », « par
  ménage »), l'allocation supplémentaire par le sien (« Pour les couples
  mariés »), l'AVTS par l'article qui la nomme, ou par la notice d'un décret « de
  divers avantages de vieillesse », dont l'article 1er l'applique d'abord à
  l'AVTS. Un montant prend la date d'effet qui le suit, sauf celle qui l'annonce
  (« AU 01-01-1987: 18120FRS »), sinon la seule de son article ou de son décret,
  ce que la sortie dit. Ne sont pas lus le montant servi « à titre
  provisionnel » ni le « minimum vieillesse » des notices.
- *Ce qu'il certifie.* Un montant daté du barème de la caisse l'est quand un
  texte le redit à la même date, dans la même série : 185 des 340 que le barème
  date jusqu'en 2006. Une année l'est quand toute sa ligne l'est, la ligne
  n'ayant qu'un niveau : de 1982 à 2003, vingt-deux années, les cinq colonnes de
  `minimum_vieillesse_avant_2007.csv` au niveau `certifiee`, par six contrôles
  de `verifier_donnees.py` (`*_journal_officiel`), la Cnav gardant les autres au
  niveau `haute`. Le seuil d'un trimestre de 1946 à 1948 (les 18 F de R. 351-9)
  et de 1971 (le quart des 1 750 F du décret n° 70-879) passe aussi au niveau
  `certifiee`. Aucune valeur ne change : les deux sources s'accordent au centime.
- *Le ménage.* La colonne `supplementaire_menage` est celle des « couples
  mariés » depuis 1992 (n° 92-50) ; en 1982, deux fois celle de l'allocataire
  marié, que l'article fixe (« lorsque le bénéficiaire est marié, ce montant est
  fixé à 12700 F », n° 82-560) ; de 1983 à 1991, deux fois le montant unique que
  l'article fixe sans nommer ni le mariage ni le couple. Le certificateur ne
  double un montant que dans ce cas, et le dit (`derivation`).
- *Quatre tests* (`tests/test_verification.py`) : l'AVTS dans l'article, la
  notice et le titre ; le libellé et la date du plafond et de l'allocation
  supplémentaire ; le ménage ; la ligne entière et le seuil. Les fiches
  `minimum_vieillesse` et `trimestres_avant_1972`, `data/sources.yaml` (le jeu
  `jorf_avts`), les en-têtes des deux tables et le tableau de
  `docs/limites/1-certification.md` le disent.

**Ce que la vérification a trouvé.**

- *Trois notices fausses*, que l'article contredit ou que la caisse dément : celle
  du n° 74-1126 date du 1er avril 1975 les 3 250 F du 1er janvier ; celle du
  n° 82-1142 écrit 10 300 F, l'article 11 300 F ; celle du n° 87-78, 32 400 F pour
  le plafond d'une personne seule, l'article 32 490 F. Celle du n° 79-1057 date
  du 1er septembre 1979 les 7 400 F que la caisse date du 1er décembre : seul le
  fac-similé tranchera ; le 31 décembre 1979, les deux s'accordent.
- *Un décret cité pour un autre* : la caisse rapporte au n° 82-1143 l'allocation
  supplémentaire de juillet 1983, que fixe le n° 83-552 (15 810 F).
- *L'allocataire marié de 1983 à 1991.* La notice du n° 87-78 écrit 14 865 F « POUR
  UNE PERSONNE MARIEE », que l'article ne fixe pas : la moitié du plafond du couple
  diminué de deux AVTS, ce que le plafond laisse à chacun. Celles des n° 90-266 et
  90-1242 chiffrent de même l'allocation d'un couple marié, 32 700 F et 33 690 F,
  sous le nom de « minimum global ». Le modèle le calcule de lui-même, en bornant
  les deux étages au plafond du couple (`avant_l_aspa`, L. 815-8) ; la colonne
  garde le montant que le texte fixe, avant le plafond.
- *LEGI* a lu « 17.48O F » pour 17 480 F (n° 85-785), et colle en tête des
  articles d'après 1993 une note de la loi n° 93-936 qui nomme l'allocation
  supplémentaire ; le certificateur corrige l'un et ôte l'autre.

**Pour les pages, rien à écrire.** La page Données lit le journal de
certification que le paquet porte : les six contrôles nouveaux y paraîtront
quand GitHub l'aura refait.

**Ce qui reste.**

1. *Le fac-similé du Journal officiel*, que seul le poste du propriétaire ouvre
   (étape 17) : les lois et les décrets d'avant 1970, dont dépend le seuil d'un
   trimestre de 1949 à 1970 ; le plafond de 1956 à 1981, qu'aucune notice ne
   redit hors celle du n° 70-879, et sans lequel aucune ligne de ces années ne
   se certifie ; la date du décret n° 79-1057.
2. *Un filtre thématique élargi* à « allocation supplémentaire » et « Fonds
   national de solidarité », que seul le workflow `index-dila.yml` peut
   republier : il épargnerait à la prochaine lecture le dump, sans rien
   certifier de plus aujourd'hui.
3. Les points 2 à 5 de la première partie : la pension minimum d'avant le
   1er avril 1983 ; l'AVTS dans R. 732-70 ; l'outre-mer ; avant 1946, la
   retenue.
