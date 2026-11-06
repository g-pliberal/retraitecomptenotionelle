# Étape 4, thème « Carrière : majorations de durée d'assurance » : les exposés et leurs références

**Reprise, au 6 novembre 2026.** Cinq thèmes de l'étape sont rangés : « Retraite
personnelle de base », « Carrière : cotisations-salaires », « Carrière : versements
volontaires », « Carrière : périodes assimilées », puis « Carrière : majorations de durée
d'assurance » (cette note). Suivant : les quatre autres thèmes de « Carrière » (17 exposés),
sous la convention de la note du premier thème. La base se relit par `cnav_legislation.py`
hors de 5 h–6 h UTC. Restent à lire avec leur thème : les listes d'accords, de l'Union et de
l'Espace économique européens. Aux sessions du modèle : les deux candidats de cette note, les
trois et les deux des précédentes ; l'activité accessoire d'avant 2015 est portée (H6), ses
deux candidats dans sa note, relue (R-H6), ses six écarts déclarés (H6-bis, sa note) ;
suivante de la file H : H7, l'AVPF du père.

**Le 6 novembre 2026, ce qui est fait.**

- *La relecture de la base.* Relue de 0 h 13 à 0 h 21 UTC par
  `python scripts/fetch/cnav_legislation.py` (import de la nuit du 5 novembre à 5 h 00),
  sortie sur le code 0, sans refus ; elle n'a rien changé au registre.
- *La lecture* : les 13 exposés du thème, à la version que le registre date et que la base
  sert ce jour (du 24 octobre 2025 au 2 octobre 2026) — enfant (bénéficiaires, conditions,
  compétence), enfant handicapé (bénéficiaires, compétence, décompte, enfant à charge),
  adulte handicapé, congé parental, âge, compte professionnel de prévention, sapeur-pompier
  volontaire, élu local —, chacun confronté à ce que le modèle en fait : la fiche
  `majoration_duree_assurance_enfants`, que lisent `majoration_pour_enfants`
  (`droit/compter.py`, ligne 1340) et `majorationPourEnfants`
  (`moteur/js/droit/compter.js`, ligne 1317), par `par_enfant`
  (`scenarios/actuel.py`, ligne 1411) et `parEnfant` (`moteur/js/regimes.js`, ligne 1419) ;
  les fiches `priorite_majorations_enfants`, `majoration_duree_apres_65_ans`,
  `majoration_duree_sapeurs_pompiers_volontaires`, `majoration_duree_elus_locaux`,
  `inaptitude_invalidite_penibilite_amiante`. Les textes, à l'index LEGI à jour au
  5 novembre 2026 : L. 351-4 (rédaction du 31 décembre 2025, LEGIARTI000053280393, et son
  histoire), L. 351-4-1 (LEGIARTI000017845585), L. 351-4-2 (LEGIARTI000028497884),
  L. 351-5 (LEGIARTI000021537902), R. 351-3 (LEGIARTI000053389999), R. 4163-11 du code du
  travail (LEGIARTI000047962401). Le cas du candidat 1 a été calculé par le jumeau Python.
- *Le rapprochement de l'index* (LEGI à jour au 5 novembre 2026, JORF au 6). Les exposés
  lient 60 fois Légifrance, sous 42 identifiants ; ceux de l'adulte handicapé et du compte
  professionnel de prévention n'en lient aucun. 35 identifiants se trouvent à l'index, et
  chacun concorde avec son ancre par le numéro de l'article ou du texte ; « décret 2014/1702
  du 30/12/20104 », ancre fautive, mène bien au décret n° 2014-1702 du 30 décembre 2014.
  Des 7 absents, un se trouve par le numéro : « Loi 2005/102 du 11/02/2005 art.68 »
  (LEGITEXT000006051257, absent) est l'article 68 de la loi (LEGIARTI000006682303), qui « A
  modifié […] art. L351-4-1 ». Restent absents les articles 355, 373-3, 375-3 et 377-1 du
  code civil et L. 1225-48 du code du travail, hors du champ social de l'index, et l'article
  12 de la loi n° 94-629, que l'index ne porte ni par l'identifiant ni par le numéro. Hors
  de Légifrance, un lien fautif : dans l'exposé du compte professionnel de prévention,
  chaque « § » de la circulaire Cnav 2025/19 mène au PDF de la circulaire 2024/30.
- *Les sorts*, sous la convention de la note du premier thème : 13 exposés `limite` ;
  5 fenêtres — « Concubinage » et « Kafala » `hors_modele`, définitions du lexique, trois
  autres déjà rangées ; 2 listes — celle des régimes de base obligatoires, déjà rangée, dont
  le renvoi s'étend, et celle des pays de l'Espace économique européen, laissée `a_lire`
  avec son thème ; 56 références — 39 `limite`, 15 déjà rangées dont les renvois
  s'étendent, 2 qui les portaient déjà ; le barème de la majoration pour âge, déjà
  `recoupe` ; 3 avis de mise à jour `hors_modele` : la répartition des trimestres d'un
  enfant né depuis 2010 (2014), le compte professionnel de prévention (2024), le justificatif
  du sapeur-pompier d'avant 2002 (2026). L'exposé de la réversion qu'un exposé lie reste à
  son thème.
- *Hors du thème, ce que la relecture du 5 novembre a ajouté.* La circulaire ministérielle
  n° DSS/3C/2026/140 du 3 novembre 2026 (« numéro interne : 2026/140 »), lue au PDF de la
  base : elle exempte la pension de la Caisse de retraite complémentaire du personnel
  navigant de l'aéronautique civile de L. 161-22 « jusqu'à la liquidation de leur pension de
  retraite de base », et tout à fait si la pension de base est une pension militaire de
  L. 6 du code des pensions civiles et militaires liquidée avant elle ; `limite`, renvoyée
  aux fiches `cumul_emploi_retraite_et_retraite_progressive`, qui sert entières les
  complémentaires des navigants, et `crpn_pension_des_navigants`. L'avis 357, « Recouvrement
  de créance » (3 novembre 2026), le droit de rectification avant le recouvrement d'un indu,
  vingt jours, d'après la circulaire Cnav 2026/34 : `hors_modele`, comme les autres avis ;
  la circulaire 2026/34, non lue, reste `a_lire`.
- *La limite* « majorations de durée d'assurance » (`docs/limites/3-systeme-actuel.md`),
  neuve : ce que le modèle sert — la majoration pour enfants à la mère, la majoration pour
  âge —, les deux conditions de la première qu'il ne lit pas, et ce qu'il ne sert pas —
  l'adoption, le congé parental, l'enfant handicapé, l'adulte handicapé, le compte
  professionnel de prévention ; les sapeurs-pompiers et les élus, déjà déclarés.

**Ce que la lecture a trouvé, sans écart.** La majoration pour âge (2,5 % par trimestre
depuis l'âge du taux plein, arrondie au trimestre supérieur, bornée à la durée maximale,
répartie entre régimes alignés par R. 173-4-2, devenu R. 173-3-3 le 1er janvier 2026 avec
les non-salariés agricoles) est celle de sa fiche, qui déclare l'arrondi au plus proche
entre régimes. Les règles de compétence de l'exposé « Compétence » (régime spécial d'abord
s'il peut pensionner, puis régime général parmi les alignés, l'exception de la CRPCEN) sont
celles de `priorite_majorations_enfants`, qui déclare ce qu'elle n'en porte pas ; la
priorité des régimes locaux de Saint-Pierre-et-Miquelon et de Mayotte, que l'exposé dit
aussi, ira aux thèmes de l'outre-mer et de Mayotte. Les majorations des sapeurs-pompiers volontaires et
des élus locaux sont déclarées (`ecarts-au-droit-positif.md`) ; l'exposé de l'élu local
(version du 23 janvier 2026) attend encore « la publication des instructions
réglementaires », quand la fiche a lu le décret n° 2026-948. La circulaire Cnav 2026/31 du
30 septembre 2026, que lie l'exposé du sapeur-pompier, « annule et remplace la circulaire
n° 2026/22 du 23 juillet 2026 à compter du 1er janvier 2027 » et étend la majoration à
Mayotte pour les retraites prenant effet à compter de cette date (ordonnance n° 2026-647,
article 3) ; ses règles de décompte, de compétence et de prise en compte sont celles que la
fiche cite de la 2026/22 : la fiche la citera le jour où elle sera modélisée. L. 351-4-2
s'applique « aux périodes de prise en charge intervenues à compter du 1er février 2014 »,
quand l'exposé décompte « à partir du 01/01/2015 », d'après la circulaire Cnav 2015/56, non
lue ici : à lire quand la majoration sera modélisée. Aucun exposé du thème ne publie
d'exemple chiffré.

**Un point non tranché, sans candidat.** L. 351-4, VIII : « Lorsque le délai mentionné au
II n'est pas écoulé à la date d'effet de la demande de retraite de l'un des parents, ce
délai est réduit à deux mois » ; VI : « L'assuré ne peut bénéficier, au titre de la
majoration prévue au II, d'un nombre de trimestres supérieur au nombre d'années durant
lesquelles il a résidé avec l'enfant ». L'exposé « Majoration de durée d'assurance pour
enfant » : « Le point de départ de la retraite doit se situer après la période de 4 ans
d'éducation » ; « Bénéficiaires des majorations » : « Les trimestres de majoration ne peuvent
pas être attribués au parent dont la retraite prend effet avant cette période d'option ».
Le modèle sert entiers les quatre trimestres d'éducation d'un enfant de moins de quatre ans
à la date d'effet, ce que sa fiche déclare en approximation sur la lecture du VI (autant de
trimestres que d'années de résidence) ; la caisse n'en sert aucun. Pour un enfant de deux
ans à la date d'effet : 4 au modèle, 2 par la lecture de la fiche, 0 par celle de la caisse.
Les deux lectures surestiment dans le même sens ; seule une naissance déclarée moins de
quatre ans avant la pension de la mère y entre.

**Deux candidats, aux sessions du modèle** (rien n'a été corrigé) :

1. *La durée d'assurance de deux ans des parents.* L. 351-4, VII, rédaction du 31 décembre
   2025 (LEGIARTI000053280393), mot pour mot celle du 28 décembre 2009 (loi n° 2009-1646,
   LEGIARTI000021537916) : « Lors de la
   liquidation de la pension de retraite, la majoration prévue au II ne peut être attribuée
   à l'un ou l'autre des parents lorsque chacun d'eux ne justifie pas d'une durée
   d'assurance minimale de deux ans auprès d'un régime de retraite légalement obligatoire
   d'un Etat membre de la Communauté européenne ou partie à l'accord sur l'Espace
   économique européen ou de la Confédération suisse. Ces dispositions ne sont pas
   applicables au parent qui a élevé seul l'enfant […] ». L'exposé (version du 15 décembre
   2025) : « La condition de durée d'assurance doit être remplie par les 2 parents au point
   de départ de la retraite du bénéficiaire de la majoration. Chaque parent doit justifier
   d'au moins 8 trimestres » ; « Tous les trimestres du régime général sont retenus sauf la
   majoration d'assurance pour éducation et la majoration d'assurance pour les assurés qui
   ont dépassé l'âge d'obtention du taux plein ». Le modèle ne lit aucune durée :
   `par_enfant` ne regarde que la naissance, la date d'effet, le sexe et le nombre
   d'enfants. Calculé par le jumeau (`chronologie.du_releve`, `releve.construire`) : la
   salariée née en janvier 1965, qui n'a travaillé qu'en 1987, pour 2 500 €, et un enfant né
   en mars 1990, partie à soixante-sept ans — le modèle lui valide 3 trimestres en 1987 et
   8 de majoration (version `mda_2010_nes_avant`), 11 au régime général. Par la lecture de
   la caisse : 3 + 4 (maternité) = 7 trimestres, moins que 8 : la majoration d'éducation
   n'est pas due ; 3 + 4 = 7 au régime général, 4 de moins. Ce que le texte ne tranche
   pas : « chacun d'eux ne justifie pas » se lit « chacun des deux doit justifier », la
   lecture de la caisse, ou « aucun des deux ne justifie », qui laisse la majoration à la
   mère de 7 trimestres si le père en a 8 — ce que la saisie ne dit pas. Le modèle peut
   porter la première sur la durée de la mère, qu'il connaît, et doit déclarer celle du
   père, qu'il ne connaît pas ; la limite le déclare dès ce jour.
2. *Le seuil du cumul emploi-retraite de 2027 est publié* (hors du thème, trouvé en lisant
   la circulaire 2026/140, qui cite le décret n° 2026-1016). Décret n° 2026-1017 du
   2 novembre 2026, JO du 3 novembre, article 3 (JORFARTI000055047362), qui écrit
   D. 161-2-8 : « Le seuil mentionné au 2° du A du III de l'article L. 161-22 s'apprécie
   sur une année civile. Pour l'année 2027, son montant est fixé à sept mille euros. » ;
   son article 6 : « Les dispositions du présent décret s'appliquent aux pensions prenant
   effet à compter du 1er janvier 2027 ». L. 161-22, III, A, 2°, rédaction du 31 décembre
   2025 (LEGIARTI000053279730) : « la pension servie est réduite à due concurrence de la
   moitié du dépassement de ce seuil ». La fiche `cumul_emploi_retraite_et_retraite_progressive`
   porte `seuil: non_publie` (ligne 292) et l'approximation « le seuil du 2° de L. 161-22
   pour les premières pensions de 2027, qu'un décret fixe, n'a pas paru » ; les deux moteurs
   rendent alors une réduction nulle (`droit/cumul.py`, ligne 1175 ;
   `moteur/js/droit/cumul.js`, ligne 918). Calculé à la main : l'assuré qui entre en
   jouissance de sa première pension en janvier 2027, à l'âge légal, et gagne 17 000 € en
   2027 — la loi réduit ses pensions de (17 000 − 7 000) / 2 = 5 000 € sur l'année, le
   modèle de 0. Le reste de l'article 3, qui remplace les articles D. 161-2-5 à
   D. 161-2-23, n'a pas été lu ici, ni donc ce qu'il dit de la répartition de la réduction
   entre régimes. À reprendre avec l'action 159, étape 9, que la fiche nomme.

**Pour le thème suivant**, les quatre autres thèmes de « Carrière » : le candidat 1 de la
note des périodes assimilées (le congé de maternité) et le candidat 1 de celle-ci touchent
tous deux les trimestres de la mère. Aucun fichier d'une autre file n'a été changé.
