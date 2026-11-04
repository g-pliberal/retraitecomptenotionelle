# Le taux plein à 65 ans des parents de trois enfants nés de juillet 1951 à 1955, à la CAVIMAC et aux points d'avant 1973

File M4 de la sixième vague, sur la décision 14 du propriétaire : servir à la CAVIMAC
et aux points d'avant 1973 des artisans et des commerçants l'âge de soixante-cinq ans
que la fiche `taux_plein_a_soixante_cinq_ans` leur laissait « à faire », et verser les
deux écarts faibles de la relecture R-M4-bis
(`2026-11-03-relecture-corrections-r-m4-fonctionnaires.md`). Chaque texte a été ouvert
dans la session : l'index LEGI mis à jour (incrément du 3 novembre 2026,
LEGI_20261103-214151) et l'index JORF à jour au 3 novembre ; les pages de la CAVIMAC,
la circulaire Cnav n° 2014-64 et le barème du minimum de la Cnav téléchargés le jour.

**Ce qui est fait.**

- *La règle, dans les deux moteurs* : la version de 2011 de la fiche porte les régimes
  `cavimac`, `cancava_avant_1973` et `organic_avant_1973` ; l'âge que lit tout le moteur
  (`ageTauxPlein`, `age_taux_plein`) y est soixante-cinq ans pour qui remplit les
  conditions. Aux cultes, les deux fractions le lisent par le taux plein : celle
  d'après 1997 au taux de 50 %, celle d'avant 1998 sans décote et avec les majorations
  du V et du V bis ; avant soixante-cinq ans, toutes deux décotées jusqu'au
  soixante-cinquième anniversaire. Aux points d'avant 1973, la minoration se compte
  jusqu'à lui.
- *Un défaut trouvé en lisant les cultes* : les deux années qui précèdent la naissance
  comptaient tout l'emploi ; le décret n° 2011-620 n'y retient que « les trimestres
  validés en contrepartie de cotisations à la charge de l'assuré » ou de maladie,
  maternité, chômage, formation. L'activité cultuelle d'avant 1979, que la CAVIMAC prend
  en compte sans cotisation (D. 721-11 du code de 1985), n'en est plus
  (`remplitPourLEnfant` et `_remplit_pour_l_enfant`, par `ligneCotisee` et
  `ligne_cotisee`, le prédicat des trimestres cotisés que lisent déjà la carrière longue
  et le minimum majoré). Même classe ailleurs : le prédicat ne tient pour validées sans
  cotisation que les périodes dont tous les régimes sont des « services passés »
  (`data/reference/legislation/affiliations.yaml`) — les cultes d'avant 1979, ministres
  et membres des congrégations ; les périodes calédoniennes et de Saint-Pierre n'ont que
  leur complémentaire en services passés. Il écarte aussi l'emploi sans revenu ou sans
  cotisation versée (`cotise`).
- *La fiche* : les textes lus, chacun par son identifiant et mot pour mot, dans la
  version de 2011 ; son droit, ce qu'elle lit et écrit, son code, son effet ; les deux
  approximations de la CAVIMAC et des points d'avant 1973, qui chiffraient un écart,
  remplacées par ce que les textes ne tranchent pas (ci-dessous) et par la lecture à
  l'année des points d'avant 1973 en 2012 ; trois lectures de plus (les deux documents de
  la CAVIMAC, le barème de la Cnav, avec leur empreinte) ; le « à relire » de la file du
  régime général ne garde que les non-salariés agricoles, les libéraux et les avocats.
- *Le test* `tests/test_taux_plein_a_soixante_cinq_ans.py`, vu rouge pour la raison
  attendue, puis vert : la fiche datée et ses six régimes ; l'âge aux cultes et aux
  points d'avant 1973 (`ALIGNES`) ; la pension des cultes de bout en bout
  (`CULTES_DE_BOUT_EN_BOUT`, par `scenario_actuel.calculer`) ; les années d'avant 1979 ;
  la ministre du culte de la saisie (`NON_TRANCHE_CULTES`, `servi_et_refait`) ; les points
  d'avant 1973 de bout en bout (`AVANT_1973`, vu rouge sur la fiche de main : 0,9375 au
  lieu d'aucun coefficient). `ECARTS_DECLARES` et son test, qui affirmaient les deux
  écarts de la CAVIMAC, sont partis avec eux ; `ENCORE_A_L_AGE_DE_LA_GENERATION` ne garde
  que l'Arrco et le RCI.
- *Les deux écarts faibles de R-M4-bis* : la fiche et le test disent, pour la naissance
  d'avril 1978, quatorze semaines, le congé de la salariée (L. 122-26,
  LEGIARTI000006646773), seize dès le 1er octobre 1978 ; la fiche cite le renvoi à la
  sécurité sociale de la CNRACL (loi n° 84-53, article 57, 5° ; loi n° 86-33, article 41,
  5°) et des ouvriers de l'État (décret n° 72-154, article 4), et les vingt-six semaines
  de L. 331-4 dès sa rédaction de 1985.
- Le paquet `moteur/donnees.json` refait : une ligne, les régimes de la version.

**Les textes lus, et ce qu'ils décident** (citations entières dans la fiche).

| Texte | Version lue | Ce qu'il décide |
|---|---|---|
| L. 382-27 CSS | LEGIARTI000019959668 (19 décembre 2008-1er septembre 2023), LEGIARTI000047453094, LEGIARTI000048697351 | la pension des cultes « dans les conditions définies aux articles [...] L. 351-8 à L. 351-13 » ; celle des périodes d'avant 1998 aux règles du 31 décembre 1997 « sous réserve d'adaptation par décret » |
| Loi n° 2010-1330, article 20, IV | LEGIARTI000023023835 | « applicable dans tous les régimes obligatoires de retraite auxquels s'appliquent les dispositions de l'article L. 351-8 » : les cultes en sont |
| Décret n° 2006-1325, article 2 | LEGIARTI000023397816 (pensions dès le 1er juillet 2011, seule depuis) | I : l'âge de D. 721-6 est celui de L. 161-17-2 pour qui a la durée ; II : sinon, « également » dès cet âge, avec « le coefficient de minoration fixé au 2° du I et au II de l'article R. 351-27 » ; III : le maximum au prorata de la durée de R. 351-6 ; V : à qui remplit « les conditions prévues à l'article D. 721-6 », « 100 % de l'écart pour les assurés nés après 1942 », « au prorata du nombre de trimestres cotisés [...] entre le 1er janvier 1979 et le 31 décembre 1997 » ; V bis : l'écart au minimum non majoré, au prorata des trimestres d'avant 1979 |
| D. 721-6, code de 1985 | LEGIARTI000006738898 (21 décembre 1985-26 février 2004) | « fixé à soixante-cinq ans » |
| D. 721-11, code de 1985 | LEGIARTI000006739120 (13 novembre 1988-21 juin 1998) | les périodes d'activité cultuelle d'avant 1979 « sont prises en compte pour l'ouverture du droit et le calcul de la pension », sans cotisation pour elles |
| L. 382-25, I | LEGIARTI000006742803 (20 décembre 2005-14 juin 2018) | « 1° Des cotisations à la charge des assurés » : les trimestres cultuels de 1979 et après sont cotisés à la charge de l'assuré |
| R. 351-27 | LEGIARTI000024113020 (3 juin 2011-1er septembre 2023) | « pour l'application du deuxième alinéa de l'article L. 351-1 et de l'article L. 351-8 » : la minoration jusqu'au « soixante-cinquième anniversaire » de qui remplit « le III ou IV de l'article 20 » ; « 1,25 % pour l'assuré né après 1952 » |
| R. 351-6 ; décret n° 2010-1734, article 9 | LEGIARTI000006749349 ; LEGIARTI000023383430 | la durée maximale, celle de L. 351-1 ; « 165 trimestres pour les assurés nés en 1953 et 1954 » |
| Décret n° 73-937, article 3 | LEGIARTI000006765819 (19 février 2004-7 octobre 2012), LEGIARTI000026474703 (7 octobre 2012-1er septembre 2023), LEGIARTI000047634732 (depuis) | jusqu'en 2012, la minoration jusqu'au « soixante-cinquième anniversaire » de tous ; depuis, jusqu'à lui pour qui remplit « les conditions prévues [...] aux III ou IV de l'article 20 », sinon jusqu'à l'âge du 1° de L. 351-8 |
| Décret n° 2011-620 | JORFTEXT000024110091, articles 1er à 11 | l'article 2 vaut « pour l'application du IV » ; aucun article ne touche aux cultes, et la notice ne les nomme pas parmi les « publics concernés » |
| R. 382-57, R. 382-89, R. 382-90, R. 382-121, D. 382-30 à D. 382-33, L. 382-15, L. 382-26 | identifiants dans la fiche | aucun ne renvoie à R. 351-27 ni ne règle l'âge du taux plein ; R. 382-121 suppose R. 351-29 applicable aux cultes, comme L. 382-27 rend applicables L. 351-1 et L. 351-8 |
| Barème de la Cnav « Montant minimum de la retraite personnelle » | lu par son API le 3 novembre 2026 | « 01/10/2017 7 615,94 € 634,66 € 8 322,13 € 693,51 € Circulaire Cnav 2017/32 du 26/09/2017 » |
| CAVIMAC, « Demander ma retraite de base » ; triptyque « retraite » de 2024 | sha256 a5f43cfa… ; sha256 868aa09c… | la décote comptée jusqu'à « l'âge du taux plein » ; le minimum majoré « si vous totalisez au moins 120 trimestres cotisés tous régimes » ; « varie de 65 à 67 ans » ; rien des parents de trois enfants |
| Circulaire Cnav n° 2014-64 | sha256 f6717a0f…, celle de la fiche | ne nomme pas les cultes |

**Ce que les textes ne tranchent pas**, déclaré à la fiche : l'activité cultuelle est-elle
l'« activité professionnelle » du 2° et du 3° du IV ? Le code ne la nomme
qu'« activités mentionnées à l'article L. 382-15 » ; ni le décret n° 2011-620, ni la
circulaire Cnav, ni la CAVIMAC n'en disent rien. Le modèle la compte comme l'emploi,
celle d'avant 1979 comprise pour l'activité d'avant la naissance (non pour les deux
années d'avant, que le décret veut cotisées). Le cas de bout en bout est choisi pour ne
pas en dépendre : l'activité d'avant la naissance y est un salariat.

**Les calculs posés à la main**, pour chaque valeur que le test attend.

- *De bout en bout* : née le 15 mars 1953, salariée de 1971 à 1975 (20 trimestres),
  sans activité de 1976 à 1979, ministre du culte de 1980 à 1987 (32) et de 2005 à 2017
  (52) ; enfants d'avril 1976, juin 1978 et juin 1980 ; partie à 65 ans, effet le 1er
  avril 2018. L'enfant de 1976 : avant, 1974 + 1975 = 8 cotisés ; fenêtre 1976-1978, 0 ;
  activité 1971-1975, 20 ≥ 8. Soixante-cinq ans le 15 mars 2018 : 0 trimestre de
  décote, **taux 50 %** au régime général et à la CAVIMAC. Avant 1998 : 32 trimestres,
  tous cotisés de 1979 à 1997 ; 104 cotisés tous régimes, moins de 120, le minimum non
  majoré (la caisse) ; maximum × 32/165 + 100 % × (7 615,94 − maximum) × 32/165 =
  7 615,94 × 32 / 165 = 243 710,08 / 165 = **1 477,03 €**, sans décote. *Le témoin*,
  deux enfants : jusqu'à 66 ans et 2 mois, le 15 mai 2019, 13 mois et 14 jours, 4,5
  trimestres, **5** au supérieur, moins que ceux qui manquent à la durée de 165 ; 50 % ×
  (1 − 5 × 1,25 %) = **46,875 %** ; avant 1998, le modèle sert 4 635,65 × 32 / 165 ×
  0,9375 = 842,85 €, sa lecture déclarée par la fiche `cultes_fractions_de_pension`
  (ci-dessous).
- *Les années d'avant 1979* : ministre du culte de 1973 à 1979, puis de 2000 à 2017 ;
  enfants d'avril 1980, juin 1984, juin 1986. Pour 1980 : avant, 1978 (pris en compte
  sans cotisation) + 1979 (cotisé) = 0 + 4 = 4 < 8 ; pour 1984 et 1986, 0 : **66 ans et
  2 mois**, aux deux régimes. Avant la correction, le modèle comptait 8 et servait
  65 ans. *Le témoin*, au culte jusqu'en 1980, enfants d'avril 1981, juin 1984, juin
  1986 : avant, 1979 + 1980 = 8 cotisés ; fenêtre 1981-1983, 0 ; activité, 8 cotisés au
  moins : **65 ans**.
- *La ministre du culte de la saisie* (née le 15 mars 1953, au culte à 26 ans, le 15
  mars 1979, sans activité de 1982 à 1999, enfants d'avril 1982, juin 1984, juin 1986 ;
  effet le 1er avril 2018) : avant, 1980 + 1981 = 8 ; fenêtre 1982-1984, 0 ; activité
  1979-1981, 3 + 4 + 4 = 11, sous la lecture du modèle ; **taux 50 %** ; avant 1998, 11
  trimestres, 84 cotisés tous régimes (11 + 73) : 7 615,94 × 11 / 165 = 83 775,34 / 165 =
  **507,73 €** (le maximum 4 635,65 × 11 / 165 = 309,04 €, et (7 615,94 − 4 635,65) × 11
  / 165 = 198,69 €), sans décote.
- *Les points d'avant 1973* : l'assurée de `REQUETE`, artisane ou commerçante dès dix-huit
  ans (points de 1971 et 1972), effet le 1er avril 2018 : 0 trimestre jusqu'à son
  soixante-cinquième anniversaire, le plus petit des deux nombres : **aucun
  coefficient**. Le témoin, deux enfants : 5 trimestres jusqu'à 66 ans et 2 mois, moins
  que ceux qui manquent à la durée : 1 − 5 × 1,25 % = **0,9375**.

**Les vérifications.** `python -m pytest -m rapide`, la garde des présomptions,
`tests/test_regle_de_chacun.py`, les confrontations légères et les fichiers qui lisent
les fichiers touchés : voir le compte rendu du commit. `construire_temoins.py` : voir
plus bas.

**Ce qui reste**, et qui n'est pas de cette session.

- *La même classe, hors des parents* : la fraction d'avant 1998 des générations nées
  depuis 1951 qui partent à soixante-cinq ans sans la durée ni la dérogation. D. 721-6 du
  code de 1985 l'alloue à soixante-cinq ans, et le V la majore ; le modèle la décote
  jusqu'à l'âge de la génération et ne la majore pas, comme la caisse le décrit. C'est
  l'approximation déjà déclarée de la fiche `cultes_fractions_de_pension` (« le décret
  garde soixante-cinq ans (D. 721-6 de 1997) pour la fraction d'avant 1998 »), à mesurer
  et à trancher par la file des cultes.
- *Le minimum majoré du V* : le décret écrit « le minimum de pension majoré au titre des
  périodes ayant donné lieu à cotisations » ; le modèle ne le prend qu'à cent vingt
  trimestres cotisés, comme la caisse : l'approximation de la même fiche.
- *L'Arrco des cultes*, que les textes lus ne tranchent pas (fiche, « à relire ») ; le
  RCI et l'Ircantec, à la file des complémentaires ; les non-salariés agricoles, les
  libéraux et les avocats, à la file du régime général.
- Une réponse de la CAVIMAC sur l'activité cultuelle, et un exemple chiffré.
