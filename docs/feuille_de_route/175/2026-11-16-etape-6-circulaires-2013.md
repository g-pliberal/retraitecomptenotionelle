# Étape 6, circulaires de 2013 : les 44 références sans thème de la vingtième et dernière période, relues par l'API

**Reprise, au 16 novembre 2026.** Trois natures de l'étape sont rangées. La
quatrième, les circulaires, lettres et instructions sans thème, l'est maintenant
entière, de 1936 à 2026 : cette note range la dernière année, 2013. Restent trois
natures, une session chacune, dans cet ordre : les 96 autres textes sans thème, les
74 références que la base nomme sans les servir, les 107 accords. Méthode : celle de
la note de 2010, chaque texte lu en entier, chaque citation vérifiée par script, le
code et les fiches relus avant de dire un écart neuf. Les écarts candidats de toutes
les circulaires sont récapitulés et classés par poids dans la note du même jour
`2026-11-16-etape-6-circulaires-recapitulatif-des-ecarts.md` : c'est par elle qu'une
session du modèle choisit quoi corriger.

**Le 16 novembre 2026, ce qui est fait.**

- *La période* : les références du registre sans thème et à lire dont le titre commence
  par « Circulaire », « Lettre », « Instruction », « Note d'information » ou « Diffusion
  d'instructions », datées par le registre de 2013 : 44, comme la note de 2012 les
  comptait. Toutes sont de 2013 (le registre date du 23 janvier un courrier de la
  n° 2013/42, qui est du 23 septembre).
- *La lecture* : les 44, relues par l'API le 16 novembre 2026 vers 14 h UTC
  (`/reference/referencesByFileLeafRef/`), toutes servies au premier appel : 10 en page,
  par le HTML du champ `contenu`, 34 en PDF lus au site (`/Pdf/textes/<nom>`) par leur
  texte (`pdftotext -layout`). Deux PDF sont des scans, lus à l'image, sans citation
  vérifiable : les lettres ministérielles du 9 juillet et du 14 novembre 2013. Deux
  textes longs ont été lus par leur plan et une recherche de ce qui touche la retraite,
  non ligne à ligne : la circulaire DGEFP n° 2013/07 du 15 mai 2013 sur le contrat de
  génération (84 pages, une aide à l'employeur, sans règle de pension) et le guide du
  secret professionnel joint à la n° 2013/32 (31 pages, la liste des tiers à qui la
  caisse peut répondre). 9 circulaires de la Cnav et 20 de leurs pièces, dont les 10
  modèles de courrier et la contrainte de la n° 2013/42 ; une lettre de la Cnav et une
  pièce d'une autre ; 4 circulaires et 7 lettres ministérielles ; 2 circulaires du RSI.
- *Qui a lu* : la session elle-même, sans agent. Les 28 citations relevées ont été
  retrouvées mot pour mot, par script, dans le texte servi (blancs normalisés), chaque
  raison hors modèle dans le registre, chaque renvoi dans le dépôt
  (`tests/test_cnav_legislation.py`, 42 tests, verts). La session a relu le code et les
  fiches qui décident des écarts (plus bas).
- *Les sorts* : 44 références rangées, 20 `limite`, 24 `hors_modele` ; le registre seul
  a changé (`data/reference/legislation/cnav/references.csv`, 44 lignes, les colonnes
  `sort` et `renvoi` seules, écrites et vérifiées par script). Aucune raison neuve.

**Par ce qu'elles disent.**

- *En `limite`* : les rentes ouvrières et paysannes majorées de 1,75 % (n° 2013/11) ; le
  schéma des rachats des périodes hors de France (n° 2013/16, annexe) et le barème des
  versements pour la retraite de 2013 (n° 2013/8, annexe) ; l'accord sur l'Espace
  économique européen et ses annexes (n° 2013/17, annexes 1 et 3) ; les plafonds de
  réversion au 1er janvier 2013 (n° 2013/7) ; les plafonds opposables aux veuves de guerre
  au 1er avril (n° 2013/30) ; les exemples du service civique (n° 2013/41, annexe) ; la
  liste des régimes étrangers équivalents pour réduire les années du salaire annuel moyen,
  la Croatie comprise (n° 2013/56, annexe) ; le calcul d'un rachat de pension par un
  régime spécial (lettre Cnav du 27 août, annexe 2) ; la qualité d'assuré social des
  périodes assimilées (lettre Cnav du 5 décembre) ; l'affiliation des élus locaux au
  régime général (circulaire interministérielle n° 2013/193) ; l'adhésion de la Croatie
  (circulaire DSS/DACI n° 2013/373) ; la CASA (lettre ministérielle du 20 février,
  circulaire RSI n° 2013/014) ; les taux de l'auto-entrepreneur en 2013 (circulaire RSI
  n° 2013/019) ; la retraite anticipée pour pénibilité des élèves de l'enseignement
  technique et des contractuels de l'État (lettre ministérielle du 2 avril) ; les
  avantages viagers dans les ressources de la réversion (lettre ministérielle du 7 mars) ;
  les indemnités d'élu hors du cumul emploi-retraite plafonné (lettre ministérielle du
  26 novembre) ; la rémunération de fin de formation, qui n'est pas une période assimilée
  (lettre ministérielle du 21 mai).
- *Hors modèle* : la fraude et ses pénalités (10, les modèles de courrier de la
  n° 2013/42) ; les monnaies (4, les taux de change des quatre trimestres) ; une règle
  générale de l'administration (4 : le secret professionnel, la n° 2013/32, sa liste des
  caisses et son guide ; le répertoire national commun de la protection sociale, DSS
  n° 2013/363) ; une chacune, une règle de procédure (la contrainte de la n° 2013/42), les
  institutions de la coordination européenne (les décisions de la commission
  administrative, n° 2013/17, annexe 2), le mode de paiement (les majeurs protégés,
  n° 2013/20), le droit du travail (le contrat de génération), l'allocation de chômage
  (l'allocation transitoire de solidarité, lettre ministérielle du 9 juillet), le
  financement (la compensation par l'État des trimestres des sportifs de haut niveau,
  lettre ministérielle du 14 novembre).

**Les montants relus, conformes.** Le SMIC de 9,43 € au 1er janvier 2013
(`data/reference/macro/smic_horaire.csv`, ligne 85), d'où les plafonds de la réversion :
« 9,43 euros x 2 080 = 19.614,40 euros. » (n° 2013/7), que `reversion.yaml` calcule ; le
plafond de 37 032 € (`plafond_securite_sociale.csv`, ligne 140), dont la moitié fait le
seuil d'affiliation des élus, « supérieur à 1 543 € par mois ou 18 516 € par an »
(n° 2013/193), le `seuil_pass` de 0,5 de `legislation/affiliations.yaml` (ligne 179) ; la
CASA « au taux de 0,3 % » sur les avantages « servis à compter du 1er avril 2013 », pour
qui est « assujettis à la CSG au taux de 6,6 % » (lettre du 20 février), comme
`legislation/prelevements_historiques.yaml` (ligne 170) et les taux de
`prelevements_remuneration.yaml` (lignes 1009 à 1013) ; le trimestre du service civique à
la moitié du plafond trimestriel, « Assiette permettant de valider 1 trimestre : 4 327,5
euros » en 2010 (`service_civique.yaml`, ligne 100). Les élus locaux hors du cumul
plafonné : le modèle sert déjà entière la pension d'un élu qui exerce
(`src/retraite_notionnelle/droit/cumul.py`, ligne 96), comme la lettre du 26 novembre le
demande pour 2013 : « le mandat d'élu local ne peut être considéré, au sens du cumul
entre emploi et retraite, comme une activité salariée. » Sans série au dépôt : les taux
de change, la majoration des rentes ouvrières et paysannes, les barèmes des versements et
des rachats, les plafonds des veuves de guerre ; les taux de l'auto-entrepreneur de 2013,
que le modèle n'emploie pas avant 2018 (il valide sur le revenu abattu,
`legislation/micro_social.yaml`, en-tête).

**Aucun écart neuf.** Un candidat d'avant est confirmé, un point reste à trancher.

- *La qualité d'assuré social des périodes assimilées* (note de 2012) : la lettre Cnav du
  5 décembre 2013 annule et remplace celle du 26 septembre 2012 dans les mêmes mots, « La
  condition d'assujettissement préalable est remplie dès lors qu'un versement de
  cotisations, si minime soit-il, est intervenu avant la période à valider », et garde la
  qualité à qui s'affilie comme non-salarié après le début du chômage indemnisé : « si la
  personne a été affiliée à un régime de non salarié postérieurement au début de la
  période d’indemnisation de chômage, elle conserve sa qualité d’assuré social au régime
  général ». Dans l'exemple contraire, « Le régime général n’est pas compétent pour
  valider la période de chômage du 20 mars 2005 au 30 juin 2009. » Elle est à son tour
  annulée par la circulaire Cnav n° 2015-34. Le modèle n'exige toujours rien.
- *Les avantages viagers dans les ressources de la réversion, sur douze mois* (point non
  tranché). La lettre ministérielle du 7 mars 2013 étend à la réversion la règle de
  l'ASPA, malgré le renvoi limité de R. 353-1 : « Le montant annuel des avantages viagers
  doit en conséquence être apprécié d'après la valeur en vigueur à la date d'entrée en
  jouissance de la pension de réversion. » Le modèle prend une seule valeur annuelle des
  retraites du survivant, sans revalorisation dans la période : il suit la lettre pour une
  retraite servie toute l'année. Pour une retraite commencée dans les douze mois, il la
  compte depuis sa date d'effet (`moteur/js/droit/reversion.js`, ligne 985), comme la
  circulaire Cnav n° 2010/58 le dit des « sommes réellement perçues » à la révision
  (`reversion.yaml`, ligne 1830) ; la lettre, qui parle de la valeur, non de la durée, ne
  tranche pas si elle compte alors entière. À relire avec R. 815-29 au texte.

**Écarts relevés, déjà déclarés.** La retraite anticipée pour pénibilité, que le modèle
ne sert pas (`inaptitude_invalidite_penibilite_amiante.yaml`) ; l'élu qui cesse son
activité pour son mandat, affilié quel que soit le montant de ses indemnités
(`docs/limites/3-systeme-actuel.md`, « élus locaux ») ; les rachats et les versements
(même fichier, « rachats et versements ») ; le rachat de la pension par un régime spécial
(même fichier, « Rachat de retraite »). La rémunération de fin de formation : la lettre
du 21 mai dit que ses périodes « ne sont pas assimilées à des périodes d'assurance
vieillesse dans le cadre de cet article », l'assuré se constituant des droits « en
contrepartie des cotisations calculées sur une base forfaitaire » ; la saisie, qui dit le
chômage indemnisé sans en dire l'allocation, n'a pas de quoi la distinguer
(`docs/limites/3-systeme-actuel.md`, « périodes assimilées »).

**Points non tranchés.**

- *Les sorts retenus*, quand l'autre se défendrait. En `limite` : la liste des régimes
  étrangers équivalents (n° 2013/56), que le modèle lit sans distinguer les régimes ; les
  taux de l'auto-entrepreneur, qu'il n'emploie pas en 2013. En `hors_modele` : les
  décisions de la commission administrative (n° 2013/17, annexe 2), quand ses deux autres
  annexes sont en `limite`.

**Ce que la base sert de travers.**

- Des mentions d'annulation : la n° 2013/20 (par la 2021/10), la n° 2013/32 (2022/15), la
  lettre du 5 décembre (circulaire 2015/34).
- Des erreurs : la n° 2013/20 dit annuler la circulaire n° 91/73 « du 23/10/1973 » en
  tête et « du 29 octobre 1973 » dans son texte ; l'exemple 1 de la n° 2013/41 prend une
  indemnité de « 484 euros » en 2011 et en reporte « 486 x 6 = 2 916 euros » ; le registre
  date du 23 janvier un courrier du 23 septembre ; la lettre ministérielle du 20 février
  est servie amputée de sa deuxième partie (« […] » dans le PDF même).

**Ce que la lecture n'a pas fait.** Aucune règle, aucune fiche, aucune série, aucune valeur
du modèle n'a changé, et le moteur n'a pas été touché. R. 815-29 n'a pas été relu au
Journal officiel ; les moteurs n'ont tourné sur aucun cas.
