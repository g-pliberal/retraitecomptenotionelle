# Étape 5, première partie : l'impôt sur le revenu d'un foyer, de son barème à son montant, chaque année

**Reprise, au 10 octobre 2026.** Fait : l'impôt sur le revenu d'un foyer —
personne seule ou couple, enfants ou non, salaires et pensions imposables —,
des revenus de 1960 à ceux de 2025 puis sur un barème projeté, et son revenu
fiscal de référence (`impot_revenu.py`), à l'euro des tableaux de la brochure
pratique, de 77 exemples de l'administration, un par année au moins de 1998
à 2025, et d'OpenFisca exécuté à part. Branché nulle part. Reste, dans cet
ordre : l'impôt dans les indicateurs de cycle de vie (la session suivante),
avec la CSG déductible de chaque année (la session de la CSG) ; l'effet
retour de la page Coût ; les règles d'avant 1981 sans texte lu. Détail :
« Ce qui reste ».

**La demande.** Le propriétaire, le 10 octobre 2026 : l'impôt sur le revenu
d'un foyer, de son barème à son montant, chaque année ; les barèmes de l'IPP
depuis 1960 au moins, complétés pour 2024 et 2025 par les lois de finances
pour 2025 et 2026, projetés au-delà sur les prix par défaut, sur le salaire
moyen en variante ; un module à lui, qui rende l'impôt et le revenu fiscal de
référence ; des tests à l'euro, sur les exemples de la brochure pratique et du
BOFiP, en francs et en euros, avant et après 2006, puis sur les référents
exécutés à part. Ne le brancher nulle part. Au registre, dire point par point
ce que le module reprend.

**Ce que disent les sources.**

- *L'IPP* : quinze paramètres de l'impôt sur le revenu, en CSV, chacun daté du
  1er janvier de l'année des REVENUS, chaque ligne une photographie. Ils
  commencent en 1945 en anciens francs, sautent de 1954 à 1959, et reprennent
  en 1960 en nouveaux francs : le dépôt commence en 1960. Ils ne portent pas
  le barème de 2024 ni rien de 2025.
- *L'index LEGI* : les rédactions des articles 83, 157 bis, 158, 193, 194,
  195, 197, 200 sexies et 1657 du code, de 1950 à 2026. Celles que les lois
  de finances pour 2025 et 2026 ont écrites donnent les revenus de 2024 et de
  2025 ; les plus anciennes, ce que l'IPP ne dit pas — les arrondis de chaque
  époque, le seuil de mise en recouvrement depuis 1977 —, ou dit mal.
- *Le BOFiP*, qui garde chaque version d'un document depuis 2012 : un exemple
  de décote par année de 2011 à 2019, réduction sous condition de revenus
  comprise de 2016 à 2019, et un de plafonnement du quotient familial par
  année de 2011 à 2025 ; la prime pour l'emploi de 2010 et 2011, les
  abattements de 10 % de 2011. Ses archives, cherchées par formulaire : le
  Bulletin officiel des impôts depuis 1999 et la documentation de base de
  1999 et 2000, rien d'avant. L'instruction qui commente chaque loi de
  finances y chiffre une réduction complémentaire et une décote par année,
  des revenus de 1998 à 2010 ; d'autres, la prime pour l'emploi, le crédit
  d'impôt exceptionnel de 2008 ; la documentation de base, les abattements
  de 10 % et de 20 % de 1998, les barèmes et les seuils de 1993 à 1999. Leurs
  tableaux et leurs calculs sont souvent des images, lues une à une. Aucun
  exemple chiffré de l'abattement des personnes âgées, à aucune époque.
- *La brochure pratique* de 2024 et de 2025 : un barème « par lecture
  directe », l'impôt de chaque revenu imposable et de chaque nombre de parts,
  plafonnement et décote compris, pour quatre situations ; quelque 4 600
  cases.
- *OpenFisca-France*, qui calcule l'impôt de chaque année depuis 2002 :
  installé à part, sous AGPL, ses sorties seules entrent.

**Ce qui est fait.**

- `scripts/fetch/ipp_impot_revenu.py` lit l'IPP et écrit
  `data/reference/legislation/impot_revenu.yaml`, chaque montant dans sa
  monnaie, francs jusqu'en 2000 ; il y ajoute, chaque fois avec sa source
  (`origine`), les revenus de 2024 et de 2025 lus dans LEGI, et ce que l'IPP
  porte mal (ci-dessous), et deux mesures d'une seule année qu'il ne porte
  pas. Entrée au manifeste : `ipp_impot_revenu`.
- `donnees/impot_revenu.py` rend les paramètres d'une année de revenus, et les
  projette au-delà de 2025 : chaque montant relevé de l'inflation de l'année,
  ou de la croissance du salaire moyen, et arrondi à l'euro, les taux et le
  seuil de recouvrement inchangés ; une année projetée est `estimee`.
- `impot_revenu.py` calcule l'impôt d'un foyer dans l'ordre de l'article 193 :
  les abattements de 10 % et, jusqu'en 2005, de 20 % ; l'abattement des
  personnes âgées ou invalides ; les parts ; le barème, son plafonnement et
  les réductions complémentaires ; la décote, dont la règle a changé six
  fois ; la réduction sous condition de revenus ; les majorations et
  minorations exceptionnelles ; la réduction exceptionnelle de 2013 et les
  5 % de 2001 ; la prime pour l'emploi et le crédit d'impôt exceptionnel de
  2008, restitués en entier au foyer qui n'est pas imposable ; le seuil de
  recouvrement. Il rend chaque étape, et le revenu fiscal de référence. Une
  année en francs se calcule en francs.
- Les tests (`tests/test_impot_revenu.py`) : toutes les cases de la brochure
  qu'un foyer du module atteint, de 2023 et 2024
  (`tests/temoins/brochure_impot_revenu.json`, `dgfip_brochure_impot.py`) ;
  77 exemples chiffrés (`tests/temoins/exemples_impot_revenu.yaml`), de
  chaque année de 1998 à 2025, en francs jusqu'en 2000 ;
  OpenFisca sur quinze foyers de 2002 à 2025
  (`tests/temoins/impot_revenu_openfisca.json`, `openfisca_impot_revenu.py`) ;
  chaque année de 1960 à 2025 dans sa monnaie ; la projection ; les valeurs
  lues dans LEGI, relues dans l'index quand il est là.

**Ce que la confrontation a trouvé.**

- *Chez l'IPP*, tranché par le code : l'abattement des personnes âgées de
  2024 (2 796 €, non 2 795 €) ; la réduction complémentaire des invalides de
  1998 à 2000 (5 380, 5 410 et 4 260 F, non 4 336 F) ; le taux de la décote de
  2000, la moitié de l'impôt, qu'il ne donne pas ; la part du veuf ayant un
  enfant, qu'il ne fait naître qu'en 2008 ; la majoration de la prime pour
  l'emploi du premier enfant d'un parent isolé, double depuis 2001, qu'il ne
  porte qu'à partir de 2007 ; la part entière du troisième enfant, datée de
  1995 dans sa table et de 1980 dans ses notes ; trois années sans montant de
  l'abattement des personnes âgées (1982, 1983, 1989), que la règle
  d'indexation de l'article 157 bis comble, et qui retrouve 1984 ; la
  réduction complémentaire de 2009 (651 €, non 661 €) ; les taux de la prime
  pour l'emploi de 2005 (6 % et 15 %, non ceux de 2006). Tranché par la
  documentation de base, aucun index n'ayant la loi de finances de l'année :
  le barème de 1994 (48 570 F, non 48 750 F) ; l'abattement des personnes
  âgées de 1993 (jusqu'à 57 500 F de revenu, non 57 000 F). Et deux mesures
  d'une seule année que ses paramètres ne portent pas : les 5 % retranchés de
  l'impôt des revenus de 2001 (loi n° 2002-1050), le crédit d'impôt
  exceptionnel des revenus de 2008, les deux tiers de l'impôt sous 11 673 €
  par part, dégressif jusqu'à 12 475 € (loi n° 2009-431). Au registre :
  `baremes_ipp`, écarts IR1 à IR9.
- *Chez OpenFisca*, tranché par le code : 1,5 part au veuf ayant un enfant
  avant 2008 (article 194 : 2,5) ; l'abattement de 20 % des pensions appliqué
  avant leur plafond, jusqu'en 2005 (article 158, 5, a : après) ; les taux
  de la prime pour l'emploi de 2005, ceux de l'IPP ; au foyer dont la
  cotisation n'atteint pas le seuil de recouvrement, la seule part des
  crédits qui dépasse l'impôt, et non la prime entière (BOI 5 B-12-01,
  n° 53), lu dans son code et non dans le témoin, qui ne compare pas ce que
  le foyer paie. Et trois
  conventions qui ne sont pas des désaccords : il arrondit les corrections sur
  l'impôt non arrondi, quand le BOFiP arrondit chaque élément (un euro, au
  plus) ; sa décote n'est pas bornée par l'impôt ; il retire de la prime pour
  l'emploi le RSA activité, de 2010 à 2015, que le module ne calcule pas.
- *Chez nous*, et corrigé : la majoration de la prime pour l'emploi du
  parent isolé, qui suivait l'IPP (trouvé par OpenFisca) ; le montant minimal
  de la prime, lu comme un seuil à toute époque quand le code en fait un
  plancher jusqu'en 2004 (« ne peut être inférieur à 160 F », puis 25 €) ;
  la restitution partielle au foyer non imposable, comme OpenFisca (trouvées
  par les exemples du BOI et l'article 200 sexies).
- *Les exemples de l'administration* que le module ne reproduit pas, gardés
  en écart connu parce qu'une loi postérieure a changé leur résultat : la
  décote de 2013, que la réduction exceptionnelle votée en août 2014 efface ;
  celle de 2001, avant les 5 % d'août 2002 ; le plafonnement de 1999, au
  barème initial que la loi du 13 juillet 2000 a baissé ; trois primes pour
  l'emploi de 2000, avant leur doublement de décembre 2001. La décote de 2008
  se rejoue sur l'impôt publié, l'énoncé du BOI reprenant le revenu de
  l'année précédente.

**Le registre.** Les cinq points du chantier 138.5 qui calculent l'impôt
disent, chacun, ce que le module reprend. Saphir passe à `repris` : il ne
reprochait au dépôt que de n'en calculer aucun. OpenFisca-France, Ines, EUROMOD
et ir-catala restent `a_reprendre` : le premier pour la pension nette et la
page Coût, le deuxième et le troisième pour la CSG déductible et le net du
site, le dernier pour les demi-parts des anciens combattants et des veuves de
guerre, que le module ne calcule pas.

**Ce que le module ne fait pas** (`HORS_CHAMP`, et ses remarques). Les revenus
autres que les salaires et les pensions, les charges déductibles, les
réductions et crédits d'impôt hors la prime pour l'emploi, les réductions de
2001 et de 2013 et le crédit de 2008 ; le seuil sous lequel une restitution
n'est pas faite (50 F, puis 8 €) ; la case L, les anciens combattants, les
enfants en résidence alternée
ou majeurs rattachés ; les départements d'outre-mer ; la contribution sur les
hauts revenus ; le temps partiel de la prime pour l'emploi, et le RSA
activité qui la diminue de 2009 à 2015. Et, sans texte lu, sur les colonnes
et les notes de l'IPP seules : la franchise et la décote de 1961 à 1972, les
majorations et minorations exceptionnelles, l'arrondi d'avant 1980, le seuil
de recouvrement de 1978 et de 1985 à 1990, reconstitué par la règle de
l'article 1657.

**Ce qui reste**, dans cet ordre :

1. L'impôt dans les indicateurs de cycle de vie (`cycle_de_vie.py`) : le
   salaire et la pension nets de l'impôt de chaque année. La session suivante,
   après celle de la CSG, qui fait le net imposable : la CSG déductible de
   chaque année, que le module attend dans les salaires et les pensions
   imposables qu'on lui donne.
2. L'effet retour de la page Coût (étape 5, seconde partie) : l'ASPA que
   déclenchent les petites pensions des scénarios 2 à 5, la CSG et l'impôt
   qu'elles ne paient plus, avec ce module pour l'impôt des cas types.
3. Les règles d'avant 1981 sans texte lu : les lois de finances de chaque
   année, que l'index du JORF n'a qu'en titre, et les exemples en francs
   d'avant 1994, s'il en existe d'officiels.
