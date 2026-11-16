# Étape 6, circulaires de 2015 et 2014 : la lecture à rebours range les 50 références sans thème des deux années

**Reprise, au 16 novembre 2026.** Une seconde lecture des circulaires sans thème
avance à rebours, de 2026 vers le passé, pendant que la première avance depuis
2008. Ce bloc est le sien ; celui de la lecture chronologique reste sous sa note.
2026 à 2014 sont faites : 158 références. Deux écarts neufs en tout, aucun en
2015 ni en 2014 : la revalorisation de 10 % des salaires de Mayotte, et l'âge de
la retraite des exploitants agricoles de 1986 à 1989 (note de 2016). Vient
ensuite 2013 : 44 circulaires. La lecture chronologique en est à 2011 et 2012 :
les deux lectures se rejoignent là, et la dernière s'arrête où l'autre a fini.
Méthode : celle de la note de 2017. Détail ici.

**Le 16 novembre 2026, ce qui est fait.**

- *La période* : les références du registre sans thème et à lire dont le titre commence
  par « Circulaire », « Lettre », « Instruction », « Note d'information » ou « Diffusion
  d'instructions », datées par le registre de 2015 (24) et de 2014 (26) : 50.
- *La lecture* : les 50, relues par l'API le 16 novembre 2026
  (`/reference/referencesByFileLeafRef/`), toutes servies ; les PDF lus au site
  (`/Pdf/<nom>`) par leur texte (`pdftotext`), les pages `.aspx` par le HTML du champ
  `contenu` de leur fiche ; la lettre ministérielle n° 2015/1490 du 17 mars 2015, une
  image sans texte, lue page à page en image. Toutes lues en entier par la session
  elle-même, sans agent. Les citations de cette note ont été retrouvées mot pour mot,
  par script, dans le texte servi (blancs normalisés) ; la lettre n° 2015/1490 n'est
  pas citée.
- *Les sorts* : 50 références rangées, 33 `limite`, 17 `hors_modele` ; le registre seul
  a changé (`data/reference/legislation/cnav/references.csv`, 50 lignes, les colonnes
  `sort` et `renvoi` seules, chaque renvoi trouvé dans le dépôt par script). Aucune
  raison neuve : la fiscalisation de la majoration pour enfants (n° 2014/015) prend
  celle de l'impôt sur le revenu.

**Par ce qu'elles disent.**

- *Les montants des années* : le plafond de 2014 et de 2015, la pension maximale et la
  réversion qui s'en déduisent (n° 2014/024, 2014/63) ; l'allocation de solidarité aux
  personnes âgées au 1er octobre 2014 (n° 2014/53, et la circulaire RSI n° 2015/001,
  qui rappelle la condition de résidence) ; les ressources qu'elle exclut (n° 2014/02,
  annexe 1) et l'abattement sur les revenus d'activité (n° 2015/23) ; le salaire
  forfaitaire de l'assurance vieillesse des parents au foyer, « Le salaire forfaitaire
  mensuel applicable en 2014 au titre de l’AVPF est fixé à 1 594 euros » (n° 2014/027) ;
  les seuils de la CSG pour 2016 (n° 2015/46) ; la revalorisation du 1er octobre 2015,
  « revalorisées du coefficient de 1,001 » (circulaire ministérielle n° 2015/299), et
  le report de la date de revalorisation au 1er octobre (circulaire RSI n° 2014/008).
- *Les durées et les âges* : la durée requise des assurés nés à partir de 1958, de 167 à
  172 trimestres, et les âges de la retraite anticipée pour carrière longue, de
  cinquante-sept ans et quatre mois à cinquante-huit ans, ou soixante ans
  (n° 2014/20 et ses annexes 1 et 2) ; la retraite anticipée des assurés handicapés au
  taux de 50 %, avec la reconnaissance de la qualité de travailleur handicapé gardée
  pour les périodes antérieures à 2016 (n° 2015/31, remplacée par la n° 2015/58).
- *Le chômage non indemnisé* (n° 2015/38) : la circulaire d'application que la fiche
  `chomage_non_indemnise.yaml` demande, dans sa note à relire, de chercher. Son exemple
  écrête à six les trimestres de la première période, qui « se situe sur deux années
  civiles », en les comptant « de manière chronologique » : quatre trimestres
  potentiels en 2012, deux en 2013. La fiche borne à six trimestres et lit à l'année civile, approximation qu'elle
  déclare : la circulaire répond à la question posée, sans écart neuf.
- *Les rachats et l'assurance volontaire* : le versement pour les trimestres de stage
  (n° 2015/25), la gratification des stagiaires et son exonération (lettre circulaire
  Acoss n° 2015/042), l'assurance volontaire des anciens conjoints collaborateurs
  (circulaire RSI n° 2015/015), rangés sous les limites, qui les mettent hors du
  modèle.
- *Les étrangers et l'outre-mer* : Saint-Pierre-et-Miquelon (n° 2015/35), les accords
  avec le Brésil (n° 2015/36) et l'Uruguay (n° 2015/54), dont les dates d'effet, 1er
  septembre et 1er juillet 2014, sont celles d'`accords_internationaux.yaml`.
- *Trois circulaires du RSI et les élus locaux* : l'assiette minimale de 2015,
  « 7,70% du plafond de la sécurité sociale au lieu de 5,25% auparavant » (n° 2015/006),
  que `assiette_minimale_independants.csv` porte ; les taux et seuils des
  micro-entrepreneurs de 2014 et 2015 (n° 2014/003, 2015/007) ; l'affiliation des élus
  locaux (n° 2014/032 et ses annexes), dont « une indemnité de fonction inférieure ou
  égale à 18 774 euros » est exonérée, et le cumul de leurs indemnités avec la retraite
  (n° 2014/021, remplacée par la n° 2014/040).
- *Deux lettres ministérielles* : le volontariat international (lettre du 10 décembre
  2015), dont la caisse prend en compte les périodes des volontaires « qui n'auront
  jamais relevé au cours de leur carrière d'un régime obligatoire de retraite
  français », et la majoration de durée d'assurance de l'aidant familial (lettre
  n° 2015/1490, un trimestre par trente mois, huit au plus, depuis 2015), rangées sous
  les limites, qui les citent déjà parmi ce que le modèle ne sert pas ; la fin des
  périodes assimilées signalées par la Caisse des Français de l'étranger (lettre du
  12 décembre 2014) : « aucun signalement de la CFE ne sera donc pris en compte
  au-delà du 31/12/2013 », rangée sous la fiche de la caisse, hors champ.
- *Hors modèle* : les taux de change (n° 2015/1, 19, 33, 47 ; 2014/1, 36, 43, 48) ; les
  conventions franco-yougoslave et franco-canadienne (annexes des n° 2014/010 et
  2014/025, n° 2014/52) ; la garantie de paiement à la date d'effet (n° 2015/43 et
  2015/51) ; la prescription (n° 2014/023, annexe 2) ; le recouvrement des cotisations
  du RSI (n° 2014/006, 2015/008) ; l'impôt sur la majoration pour enfants
  (n° 2014/015).

**Les montants relus.** Conformes : les durées de 167 à 172 trimestres
(`duree_assurance_requise.csv`, `duree_requise_avant_reforme_2023.csv`) et les âges de
la carrière longue (`carriere_longue.csv`) ; les plafonds de 37 548 et 38 040 euros
(`macro/plafond_securite_sociale.csv`) ; l'allocation de solidarité, 9 600 et
14 904 euros au 1er octobre 2014 ; les seuils de la CSG pour 2016, 10 676 et
13 956 euros (`csg_pensions_seuils.csv`) ; le coefficient de 1,001 au 1er octobre 2015,
sans revalorisation en 2014 (`revalorisation_pensions.csv`) ; l'assiette minimale de
7,70 % en 2015, dont le plancher de trois cents heures de SMIC ne mord pas. Un arrondi :
la série de l'assurance vieillesse des parents au foyer porte 1 593,67 euros pour 2014
(169 heures à 9,43 euros, le barème de la Cnav), que la circulaire arrondit à 1 594 ;
deux sources de la caisse, pas un écart.

**Aucun écart neuf.**

**Ce que la base sert de travers.**

- Des textes annulés servis comme vivants : la n° 2015/23 (par la n° 2015/59), 2015/25
  (2016/23), 2015/31 (2015/58), 2015/35 (2016/7), 2015/36 (2015/45), 2015/43 (2015/51,
  elle-même remplacée par la n° 2017/3), 2015/46 (2015/63), 2015/54 (2017/21), 2014/021
  (2014/040), 2014/027 (2015/28), 2014/53 (2014/58), 2014/024 (2016/14), 2014/63
  (2015/12), 2014/010 (2014/025).
- L'annexe de la n° 2014/010 est datée, en tête, du 12 octobre 2014 pour le 12 février ;
  le titre de la circulaire RSI n° 2014/003 porte « 20./03/2014 ».
- La lettre ministérielle n° 2015/1490 n'est servie qu'en image, sans texte.

**Ce que la lecture n'a pas fait.** Aucune règle, aucune fiche, aucune série, aucune valeur
du modèle n'a changé, et le moteur n'a pas été touché. Les lois et décrets que ces
circulaires appliquent n'ont pas été relus au Journal officiel ; les moteurs n'ont tourné
sur aucun cas.
