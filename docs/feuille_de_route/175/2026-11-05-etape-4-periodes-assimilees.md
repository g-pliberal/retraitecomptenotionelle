# Étape 4, thème « Carrière : périodes assimilées » : les exposés et leurs références

**Reprise, au 5 novembre 2026.** Quatre thèmes de l'étape sont rangés : « Retraite
personnelle de base », « Carrière : cotisations-salaires », « Carrière : versements
volontaires », puis « Carrière : périodes assimilées » — ses 25 exposés, et les 9 fenêtres,
58 listes de guerre, 243 références et 6 avis qu'ils lient (cette note). Suivant, dans l'ordre de
l'étape : « Carrière : majorations de durée d'assurance » (13 exposés), sous la convention
de la note du premier thème. La base se relit par `cnav_legislation.py` sans mise en garde,
hors de 5 h–6 h UTC. Restent à lire avec leur thème : les listes d'accords, de l'Union et
de l'Espace économique européens. Aux sessions du modèle : les trois candidats de cette
note, les deux de la précédente, l'activité accessoire d'avant 2015, l'AVPF du père.

**Le 5 novembre 2026, ce qui est fait.**

- *La relecture de la base.* Relue de 20 h 48 à 20 h 57 UTC par
  `python scripts/fetch/cnav_legislation.py` (import de la nuit à 5 h 00), sortie sur le
  code 0, sans refus ; elle n'a rien changé au registre.
- *La lecture* : les 25 exposés du thème, à la version que le registre date (du 24 octobre
  2025 au 14 octobre 2026, celle que la base sert ce jour) — chômage (validation, décompte,
  compétence), situations validées comme le chômage, qualité d'assuré social, maladie,
  longue maladie, maternité, invalidité, accident du travail, service national, périodes
  de guerre, évènements d'Afrique du Nord, invasion du Koweït, rapatriés, indemnité de soins
  aux tuberculeux, allocation de préparation à la retraite, activité partielle, aide aux
  créateurs d'entreprise, crise sanitaire, sportifs de haut niveau, stages de la formation
  professionnelle continue, volontariat international et de service civil, congé
  supplémentaire de naissance —, chacun confronté à ce que le modèle en fait : la table
  `legislation/periodes_non_travaillees.csv`, `carriere.py`, `droit/compter.py` et les
  fiches `chomage_non_indemnise`, `sportifs_haut_niveau`, `stages_formation_professionnelle`,
  `conge_supplementaire_naissance`, `volontariat_civil_et_international`, `service_civique`.
  Les cas des candidats 1 et 3 ont été calculés par le jumeau Python
  (`Carriere.depuis_parcours`) ; le candidat 2 se lit dans un test du dépôt.
- *Le rapprochement de l'index* (LEGI à jour au 2 novembre 2026, JORF au 3). Les exposés
  lient 101 fois Légifrance, sous 59 identifiants. 93 liens se trouvent à l'index par leur
  identifiant : 87 concordent avec leur ancre par le numéro de l'article ou du texte ; 5,
  relus un à un, aussi — « Décret du 29/12/1945 art. 74 § 3 » mène au décret n° 45-0179 du
  29 décembre 1945, « loi 2025/1403 » à son article 23, qui modifie L. 131-6-4, « Art
  D131-6-3 Css » à D. 131-6-3 (LEGIARTI000041968018) derrière l'identifiant du code,
  « décret 2021/570 » à son article 3, « arrêté du 31 mai 2021 » à l'arrêté de ce jour qui
  fixe la liste des stages ; et un est faux : « Décret 2001/496 du 11/06/2001 » (exposé
  « Autres périodes validées comme le chômage ») mène à LEGITEXT000005631050, le décret
  n° 2001-500 du même jour, qui règle le montant et le financement du congé-solidarité. Le
  décret n° 2001-496 est à l'index (JORFTEXT000000223764, LEGITEXT000005631046), et c'est
  lui qui fonde la validation, son article 1er, I : « Il est ajouté au 4o de l'article
  R. 351-12 du code de la sécurité sociale, après le g, un h ainsi rédigé : « h) Des
  périodes pendant lesquelles l'assuré a bénéficié de l'allocation de congé-solidarité dans
  les conditions prévues par l'article 15 de la loi no 2000-1207 du 13 décembre 2000. » ».
  L'ancre est juste, le lien de la base faux. Des 8 absents par l'identifiant, aucun ne se
  trouve par le numéro : le décret n° 2021-626, la loi n° 2000-1207 (l'index n'en porte que
  les décrets d'application), la loi n° 2022-172, la loi n° 55-141, le décret n° 56-930, les
  secteurs « S1 » et « S1 bis » (LEGIARTI000042922598 et LEGIARTI000042922595), que l'index
  ne connaît ni par l'identifiant ni par un titre ; L. 221-2 du code du sport est hors du
  champ social de l'index. Hors de Légifrance : l'instruction ministérielle du 28 septembre
  2021, au site du Bulletin officiel de la sécurité sociale ; et, dans l'exposé des stages,
  « Circulaire Cnav 2024/18 du 11/04/2024 § 3 » mène à un dossier du site SharePoint de la
  caisse (`/:f:/r/sites/N_GDLC_Campus_Ref/RefReg/textes?…`), lien mort que `liens` ne
  route pas et que `liens_de_l_import` ne voit pas (un dossier, non une page) ; la même
  circulaire est liée ailleurs dans l'exposé par son PDF. Les 160 références du registre que
  lient les exposés sont des circulaires (110), des lettres (44), deux diffusions
  d'instructions ministérielles, deux articles du règlement (CE) n° 883/2004, le
  décret-loi du 28 octobre 1935 et la loi du 5 avril 1928 : ces trois derniers textes ne
  sont pas à l'index sous ces titres ; les circulaires et les lettres n'y ont pas été
  cherchées une à une.
- *Les sorts*, sous la convention de la note du premier thème : 25 exposés `limite` ;
  9 fenêtres — 6 `limite`, 2 déjà rangées dont les renvois s'étendent, la définition
  « Assédic » `hors_modele` ; 58 listes de guerre — la liste des situations validables
  (« Périodes assimilées - Guerre, opérations militaires, service national ») et les 56
  tableaux qu'elle ouvre, chacun « situation, justificatifs, référence », `limite`, et celle
  des dates des conflits, déjà rangée, dont le renvoi s'étend ; restent `a_lire` les listes
  des pays de l'Union et de l'Espace économique européens ; 243 références que lient les
  exposés, les fenêtres et les listes de guerre — 176 `limite`, 46 déjà rangées dont les
  renvois s'étendent, 20 qui les portaient déjà, une `hors_modele` laissée telle quelle ;
  6 avis de mise à jour `hors_modele` : les congés de maternité et d'adoption (2014), le
  régime compétent du chômage (2015), ses règles de validation (2020), l'évolution des
  conditions de validation (2022), les sportifs de haut niveau (2023), l'Acre (2026).
- *La limite* « périodes assimilées » (`docs/limites/3-systeme-actuel.md`), neuve : ce que
  le modèle valide, à l'année, de ce que la saisie déclare sans emploi ; ce que la caisse
  compte au jour ; ce qu'il ne sert pas — l'activité partielle, l'allocation de préparation
  à la retraite, les périodes de guerre, la détention liée à l'Afrique du Nord, les otages du
  Koweït, les rapatriés, l'indemnité de soins aux tuberculeux et ses trente-six trimestres,
  les situations validées comme le chômage, la validation gratuite de 2020 et 2021 ; et la
  compétence entre régimes, que l'année d'interruption ne suit pas.

**Ce que la lecture a trouvé, sans écart.** Une année entière de chômage, de maladie,
d'accident du travail, d'invalidité ou de service national vaut quatre trimestres au modèle
comme à la caisse. Les stages (cinquante jours par trimestre depuis 2015, et les stages
d'insertion de 1977 à 1992 pour les pensions depuis le 1er septembre 2023) et le congé
supplémentaire de naissance (cinquante-huit jours) sont ceux de leurs fiches ; les
volontariats sont déclarés. Les fenêtres publient trois exemples du chômage : le premier
chômage non indemnisé de juin 2011 à novembre 2012, six trimestres, est celui du modèle ;
le chômage indemnisé de novembre 2010 à février 2011, zéro trimestre, et le chômage non
indemnisé d'un an de juin 2009 à mai 2010, sept trimestres (« Au total, il a été possible
de valider 7 trimestres sur la période d'1 an de chômage non indemnisé avant 2011 »), ne se
rejouent pas tant que le modèle lit l'année civile, approximation que la fiche
`chomage_non_indemnise` déclare : ils seront les cas de son test quand il lira le mois.

**Trois candidats, aux sessions du modèle** (rien n'a été corrigé) :

1. *Le congé de maternité.* L'exposé « Maternité » (version du 27 février 2026), sous
   « Du 01/07/1948 au 31/12/2013 » : « Le trimestre qui comprend la date de l'accouchement
   est assimilé à un trimestre d'assurance » ; sous « A partir de 2014 » : « Chaque période
   de 90 jours permet de valider le trimestre civil qui comprend le 90e jour
   d'indemnisation ». R. 351-12, 2°, rédaction du 15 février 2004 (LEGIARTI000006750030) :
   « le trimestre civil au cours duquel est survenu l'accouchement » ; rédaction du
   1er novembre 2026 (LEGIARTI000054425288) : « Le trimestre civil au cours duquel l'assuré
   a bénéficié du quatre-vingt-dixième jour d'indemnisation […]. Si la durée
   d'indemnisation a été inférieure à quatre-vingt-dix jours, le trimestre civil au cours
   duquel l'assuré a bénéficié du dernier jour d'indemnisation est décompté comme période
   d'assurance ; b) Un trimestre est également décompté pour chaque nouvelle période
   d'indemnisation de quatre-vingt-dix jours ». Le modèle donne quatre
   trimestres à l'année que la saisie déclare en « congé de maternité »
   (`legislation/periodes_non_travaillees.csv`, ligne 143, `maternite,4` ; `carriere.py`,
   lignes 763 et 803 ; `moteur/js/carriere.js`, ligne 763). Calculé : la salariée née en
   mars 1965, en congé de maternité toute l'année 1992 (`interruptions={1992: "maternite"}`)
   — le modèle valide 4 trimestres en 1992 ; la caisse, 1, celui de l'accouchement. Ce que
   la source ne tranche pas : ce que la caisse fait du reste de l'année, qui relève d'un
   autre motif (congé parental, inactivité) ; la majoration de durée pour enfant est à part.
2. *Le plafond des sportifs de haut niveau.* Décret n° 2023-799, article 7, II
   (JORFARTI000047984368) : « Les dispositions du 9° de l'article R. 351-12 du code de la
   sécurité sociale, dans sa rédaction issue du présent décret, s'appliquent aux périodes
   d'inscription en tant que sportif de haut niveau sur la liste mentionnée au premier
   alinéa de l'article L. 221-2 du code du sport postérieures au 1er janvier 2023. » ;
   R. 351-12, 9°, e, rédaction du 13 mai 2021 (LEGIARTI000043495410) : « est limité à 16 » ;
   l'exposé (version du 24 octobre 2025) : « limité à 16 trimestres sur l'ensemble de la
   carrière jusqu'au 31/12/2022. A compter du 01/01/2023, le nombre de trimestres assimilés
   validables sur l'ensemble de la carrière est de 32 trimestres ». La fiche
   `sportifs_haut_niveau` borne la version `trente_deux_trimestres` (ligne 91) par la date
   d'effet de la pension (ligne 107, `liquidation.date_effet: [2023-09-01, null]`), et
   `compter.version_ouverte` (`droit/compter.py`, lignes 806 à 829) la donne à toute période
   depuis 2012 d'une pension d'après le 1er septembre 2023 ; `trimestres_des_periodes`
   (lignes 997 à 1011) plafonne à 32. Le test
   `test_le_sportif_compte_ses_periodes_de_quatre_vingt_dix_jours`
   (`tests/test_periodes_assimilees.py`, lignes 206 à 216) l'assure : le sportif né en
   janvier 1995, inscrit de juin 2013 à janvier 2025, compte 32 trimestres à partir de 2015.
   Le décret ne lui en donne que 16 pour ses périodes de 2015 à 2022, et quatre au plus pour
   chacune des années 2023 et 2024 (« limitée au nombre de trimestres nécessaire pour
   obtenir 4 trimestres tous régimes confondus », dit l'exposé) : 24 au plus. À l'inverse,
   la pension prise de janvier à août 2023 garde au modèle le plafond de 16 pour ses
   périodes de 2023. La fiche demandait déjà la circulaire qui le dirait ; Cnav 2023/20,
   que l'exposé cite, n'a pas été lue.
3. *Le chômage non indemnisé qui suit le chômage indemnisé.* L'exposé « Périodes de chômage
   et assimilées » (version du 31 octobre 2025) distingue « Le chômeur n'a jamais été
   indemnisé » — première période, un an avant 2011, dix-huit mois et six trimestres depuis
   — de « Le chômeur a cessé d'être indemnisé » : « La période de chômage non indemnisé qui
   suit, sans interruption, une période de chômage indemnisé, est validée dans la limite
   d'1 an […]. Elle est validée dans la limite de 5 ans si l'assuré : a au moins 55 ans à
   la date de cessation de l'indemnisation ; totalise au moins 20 ans de cotisations tous
   régimes de base confondus […] ; ne relève pas à nouveau d'un régime de base
   obligatoire d'assurance vieillesse ». Le modèle tient pour première période la première série d'années de
   chômage non indemnisé, même quand elle suit un chômage indemnisé (`carriere.py`,
   ligne 574, `serie_premiere = not premiere_vue or not suit_indemnise` ;
   `moteur/js/carriere.js`, ligne 547), et ne lui ouvre jamais les cinq ans. Calculé : le
   salarié du seul régime général né en janvier 1942, 136 trimestres cotisés, indemnisé en
   1996 et 1997, non indemnisé de 1998 à sa pension du 1er janvier 2002 — le modèle valide
   4 trimestres, la caisse les quatre années, 16 ; le salarié né en 1975, indemnisé en 2014,
   non indemnisé de 2015 à 2017 — le modèle en valide 6 (4 et 2), la caisse un an, 4. Ce que
   la source ne tranche pas : R. 351-12, 4°, d, à la lettre (LEGIARTI000054425288 : « la
   première période de chômage non indemnisé, qu'elle soit continue ou non, est prise en
   compte dans la limite d'un an et demi […] ; chaque période ultérieure de chômage non
   indemnisé est prise en compte à condition qu'elle succède sans solution de continuité à
   une période de chômage indemnisé ») porte la lecture du modèle, que sa fiche déclare
   (« une première période qui suit un chômage indemnisé garde la limite de la première
   période ») ; celle de la caisse s'appuie sur des circulaires non lues ici (Cnav 2020/25,
   § 2.3 ; 2010/54 ; instructions ministérielles 2007/11). La même correction aura à dire,
   d'après l'exposé, que les vingt ans de cotisations se comptaient au seul régime général
   pour une pension d'avant le 14 juin 2002, et sans les périodes des règlements européens
   avant le 1er août 2007, quand le modèle les compte sur toutes ses lignes cotisées
   (`carriere.py`, lignes 562 et 563).

**Pour le thème suivant**, « Carrière : majorations de durée d'assurance » : le candidat 1
touche les trimestres de la naissance, que la majoration pour enfant ne remplace pas. Aucun
fichier d'une autre file n'a été changé.
