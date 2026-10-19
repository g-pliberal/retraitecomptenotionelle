# Étape 9, suite de la huitième partie : la cotisation des chemins de fer secondaires avant 60 ans

**La demande.** Vague B du 19 octobre 2026, session 5 de la première salve,
lancée par la session de suivi « Tâches restantes » : le point « les chemins
de fer secondaires avant 60 ans » du bloc « Reprise » de la huitième partie,
que la note « décrets sans marche » décrivait (`2026-10-19-etape-9-decrets-sans-marche.md`,
« Ce qui reste », 2) : une série de plus, sur l'âge du pensionné. Règle du
scénario 1 ; ni les pages, ni la saisie.

**Ce que disent les textes, lus le jour même dans les index JORF et LEGI, mis
à jour le 18 octobre.**

- *L'article 6, § 3, du décret n° 50-1448*, rédaction par rédaction dans
  LEGI : aucune cotisation en 1950 ; de 1952 à 1954, une cotisation « égale à
  celle imposée aux retraités de l'Etat », à tout âge (décret n° 51-1411) ;
  depuis le 28 janvier 1954 (décret n° 54-102), les agents retraités sur une
  pension fondée sur la durée des services et les veuves « supportent,
  jusqu'à leur soixantième anniversaire, une cotisation de 2,5 p. 100 assise
  sur le montant de leur pension », dans la limite du plafond
  (LEGIARTI000006772950). L'index du JORF écrit le numéro « 501448 », sans
  tiret : une recherche de « 50-1448 » ne ramène que les décrets de 1996 et
  1997.
- *Le décret n° 87-463* : « à titre exceptionnel », 2,9 % « pour la période
  du 1er juillet 1987 au 30 juin 1988 » ; le décret n° 88-787 récrit le
  paragraphe : 2,9 % « à compter du 1er juillet 1988 ».
- *Le décret n° 96-471, art. 5* : 3,05 % « pour les pensions dues à compter
  du 1er juin 1996 », 3,80 % au 1er janvier 1997 ; le décret n° 96-1151
  (art. 16) remplace les 3,80 % par 2,80 %, pour les pensions versées à
  compter du 1er janvier 1997 (notice) ; le décret n° 97-1249 abroge le
  paragraphe (art. 16, 3°) au 1er janvier 1998 (art. 17).
- *Passé 60 ans*, la cotisation des régimes spéciaux placés sous le régime
  général : la notice du décret n° 96-680 dit qu'elle s'applique aux
  retraités des chemins de fer secondaires « s'ils sont âgés de plus de
  60 ans ». Avant, elle ne s'y ajoute pas : « les pensionnés des régimes
  spéciaux déjà assujettis à une cotisation pour la couverture des risques
  précités continuent d'être régis par les dispositions qui les concernent »
  (décret n° 80-598, art. 1er, puis R. 711-8). Avant le 31 juillet 1980, un
  pensionné de plus de 60 ans ne paie rien.

**Ce qui est fait.**

- *La série* `maladie_chemins_fer_secondaires_avant_60_ans`, six marches lues
  aux textes et ancrées au Journal officiel (`maladie_des_pensions.py`), sur
  le régime `chemins_fer_secondaires`, et `avant_l_age`, l'âge qui la borne,
  60 ans, que le script écrit dans la donnée : avant lui, elle prend la part
  de ses régimes aux autres séries ; à cet âge, elle la leur rend. Le décret
  n° 87-463 quitte les décrets en suspens de la garde.
- *Le modèle* : `_parts_assujetties` rend les parts d'un pensionné plus jeune
  qu'un âge ; `_parts_selon_l_age` date la coupure au premier mois au premier
  jour duquel l'assuré a 60 ans (`date_de_l_age`), et les moyennes annuelles
  de l'histoire prennent, mois par mois, les parts d'avant ou d'après
  (`avant`). La pension nette et le net imposable de chaque année suivent.
  Le jumeau JavaScript de même ; le paquet porte `avant_l_age`, et sa version
  passe à 29 : un site en cache lirait la série sans sa borne.
- *Deux conventions*, dites dans le module : le taux sous le plafond est
  celui de toute la pension (convention de la première tranche) ; un âge se
  compte au premier jour du mois, le mois de l'anniversaire, s'il ne tombe
  pas un 1er, payant encore le taux d'avant.
- *Les tests* : la série et sa borne ; un agent né en 1910, parti à 55 ans en
  1965, qui paie 2,5 % de sa part jusqu'en janvier 1970, puis rien ; un agent
  né en 1930, parti en 1985, qui paie 2,9 % en 1989 et 1,9 % dès février
  1990, compté une fois avant comme après, son net imposable avec
  (`tests/test_prelevements_historiques.py`) ; ce second agent dans la
  confrontation du portage (`tests/test_cycle_de_vie_portage.py`). Verts le
  19 octobre : `-m rapide`, les deux fichiers, `-m site`, les confrontations
  légères et les lecteurs de l'histoire.

**Ce que montrent les mesures** (Python, scénario 1, convention du dépôt,
salaire moyen, entrée à 20 ans, départ à 55 ans, avant et après) :

- *Né en 1910, parti en 1965* : prélevé de 1965 à 1969, 2,116 % de sa pension
  au lieu de rien (sa part du régime, 84,6 %, à 2,5 %), 0,176 % en 1970 ;
  rendement réel net de 12,875 à 12,832 %, taux de remplacement sur le cycle
  de 0,6839 à 0,6808.
- *Né en 1925, parti en 1980* : 1,726 % de 1981 à 1984 au lieu de 1,349 % ;
  rendement de 5,7875 à 5,7843 %, remplacement de 0,4395 à 0,4392.
- *Né en 1930, parti en 1985* : 1,907 % en 1988 et 1989 au lieu de 1,717 %,
  1,733 % en 1990 ; rendement de 3,9993 à 3,9987 %, remplacement de 0,3695 à
  0,3694.

**Ce qui reste** :

1. *Au fac-similé, depuis un poste* : la cotisation de 1952 à 1954, au taux
   des retraités de l'État, que le dépôt ne lit pas avant 1976.
2. *Inchangés* : le plafond de 2027 ; la date d'entrée dans la saisie en net,
   à une session des pages ; la limite 5 ante ter (2), en fin d'étape ; la
   date d'effet des marches de l'IPP ; au propriétaire, la CAMIEG,
   l'écrêtement du minimum de la SNCF, l'ASPA de l'article 23, des décrets au
   fac-similé.

**Pour la session des pages** : rien à faire ; la version du paquet monte à
29 (`VERSION`, `VERSION_PAQUET`), qu'une autre montée le même jour devra
suivre.
