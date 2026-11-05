# Étape 6, articles de code : les 642 références sans thème, rapprochées de l'index LEGI

**Le 5 novembre 2026, ce qui est fait.**

- *La lecture* : les 642 références sans thème dont le titre commence par « Code », toutes
  `a_lire`, relues par l'API le 5 novembre 2026 vers 18 h 50 UTC, toutes servies, de
  nature « article de codes » : 501 du code de la sécurité sociale, 62 du code de
  procédure civile, 47 du code civil, 14 du code général des impôts, 7 du code des
  pensions militaires d'invalidité et des victimes de guerre, 4 du code des pensions
  civiles et militaires de retraite, 2 du code de procédure pénale, 2 du code du service
  national, et un du code de l'action sociale et des familles, du code de la famille et
  de l'aide sociale, du code pénal. La page d'un article ne sert que son lien vers
  Légifrance ; neuf pages, des plages (« L351-1 à L351-5 »), ne lient que les articles
  qu'elles couvrent. L'index LEGI, récupéré de la release `index-dila`, est à jour au
  4 novembre 2026 (incrément `LEGI_20261104-214059`).
- *Le rapprochement* : 516 par leur identifiant — l'article que l'index porte sous
  l'identifiant `LEGIARTI` du lien est du même code et du même numéro que le titre — ;
  15 par leur numéro : les neuf plages, L. 488 du code des pensions militaires, dont le
  lien est faux (ci-dessous), les articles 382, sans lien, 383 et 524 du code de
  procédure civile, dont l'index porte la version en vigueur sans porter l'identifiant de
  la base, l'article
  1496 du code général des impôts et l'article 146 du code de la famille et de l'aide
  sociale, dont la version visée manque (ci-dessous) ; 111 ne se rapprochent pas.
- *La version visée* : un lien vise `dateTexte=vig`, la version en vigueur au jour où on
  l'ouvre, ou une date. Des 516, le lien porte la version en vigueur au jour visé pour 183
  (103 « en vigueur », 80 datés, dont les articles « ancien », liés à la veille du jour
  où leur version a pris fin) ; une version antérieure d'un article toujours en vigueur le 5 novembre 2026 pour
  260 ; un article qu'aucune version ne tient au jour visé pour 73. Ce sont, avec l'année
  de leur abrogation : au code de la sécurité sociale, D. 115-1 (2015), D. 161-2-4 (2017),
  D. 161-2-16-1 (2023), D. 161-2-22 (2023), D. 161-5-1 (2011), D. 171-11-1 (2015),
  D. 241-6 (2019), D. 351-1 (2020), D. 351-1-7 (2012), D. 351-15 (2023), D. 634-15
  (2017), D. 634-19 (2014), D. 815-4 (2023), D. 815-19-1 (2020), L. 131-4 (2018),
  L. 143-1 (2011), L. 143-3 (2011), L. 161-1-6 (2010), L. 161-25-3 (2016), L. 241-11
  (2014), L. 242-12 (2018), L. 311-8 (1998), L. 311-9 (2011), L. 313-3 (2016), L. 351-9
  (2016), L. 351-15 (2010), L. 351-16 (2014), L. 381-4 (2016), L. 381-26 (2016), L. 622-5
  (2011), L. 634-2-2 (2014), L. 634-3-1 (2017), L. 634-3-2 (2014), L. 634-3-3 (2011),
  L. 634-6 (2014), L. 643-6 (2014), L. 723-1 (2015), L. 814-2 (2006), L. 815-28 (2020),
  R. 115-6 (2016), R. 143-6 (2019), R. 144-10 (2016), R. 173-4-2 (2017), R. 173-4-3
  (2019), R. 173-11 (2011), R. 313-12 (2016), R. 351-2 (2011), R. 351-8 (2026),
  R. 351-26 (2012), R. 351-29-1 (2026), R. 351-31 à R. 351-33 (2011), R. 351-37-4 (2011),
  R. 351-40 (2017), R. 351-41 (2014), R. 351-42 (2022), R. 351-43 (2017), R. 351-44
  (2014), R. 381-104 (2025), R. 381-110 (2025), R. 381-111 (2011), R. 381-113 (2011),
  R. 721-50 (2006), R. 742-33 (2011), R. 815-76 (2007), R. 815-78 (2021) ; L. 815-30,
  lié au 19 décembre 2005, dont l'unique version court du 1er janvier 2006 au
  20 décembre 2005 ; au code des pensions militaires, L. 461, L. 481, L. 489, L. 490 et
  L. 492 (2017). La base les lie « en vigueur » : son lien mène à un article abrogé.
- *La liste de contrôle des textes* (`data/reference/textes/perimetre.yaml`) tient 345 des
  642 : 319 dans ses chapitres — 315 du code de la sécurité sociale, les 4 du code des
  pensions civiles et militaires —, 22 hors de ses chapitres dont une fiche cite une
  rédaction (`redactions.csv`), et 4 plages (L. 351-1 à L. 351-5, D. 351-1 à D. 351-14,
  R. 815-18 à R. 815-20, R. 815-25 à R. 815-33). Ils prennent `limite`, avec ce fichier
  pour renvoi, comme les décrets de codification de la note du 3 novembre : chaque
  rédaction y a le statut que sa fiche lui donne.
- *Hors de la liste, 71 `limite`*, que prennent les fiches et les limites qui citent
  l'article ou disent ce que le modèle n'en sert pas, la citation relue pour s'assurer
  qu'elle vise le même article : le cumul emploi-retraite (D. 161-2-6 à D. 161-2-22 et
  leurs plages, 14), l'allocation aux vieux travailleurs salariés et le minimum vieillesse
  (L. 811, L. 812, D. 811, D. 813, R. 816-2 : 14 ; L. 816-1, D. 816-3, R. 816-3 à
  `residence_et_minimum_vieillesse`), l'assurance volontaire et ses rachats (L. 742-4,
  R. 742-2 à R. 742-39 : 17, à la limite « rachats et versements » de
  `docs/limites/3-systeme-actuel.md`, qui nomme depuis l'étape 4 l'assistance à un
  invalide, l'indemnité de soins aux tuberculeux et l'assurance volontaire vieillesse),
  la pension d'invalidité de veuve ou de veuf et la pension de vieillesse de veuve ou de
  veuf qui la remplace (L. 342-1 à L. 342-6, D. 342-2, D. 342-3, R. 342-6 : 8, à
  `reversion`, qui dit ne pas porter cette pension), la cotisation du régime local
  d'Alsace-Moselle sur les pensions (L. 242-13, D. 242-21, D. 242-21-2, à
  `csg_des_pensions_selon_le_revenu`), la période de rééducation professionnelle
  (L. 432-11, à `taux_plein_a_soixante_cinq_ans`, que la saisie ne porte pas), la carte
  d'invalidité (L. 241-3 du code de l'action sociale et des familles, à
  `inaptitude_au_travail` et `retraite_anticipee_handicap`), le volontariat civil (L. 122-15
  du code du service national), et L. 136-1, L. 241-3, L. 242-1, D. 242-4, L. 512-3,
  R. 711-24, L. 751-1, L. 821-1, L. 842-1 aux fiches qui les citent. L. 842-1 est lié
  dans sa version de 2000 (l'allocation de garde d'enfant à domicile) ; la version en
  vigueur, depuis 2016 (`LEGIARTI000031087527`), est celle que cite
  `assiette_minimale_independants`.
- *Hors du modèle, 111*, sous 25 raisons, dont 17 que les notes précédentes ont écrites :
  la procédure, le recours et la prescription (23, dont les articles 2230, 2232, 2254 et
  2277 ancien du code civil et 382, 383 et 524 du code de procédure civile, lus à
  l'index), l'impôt sur le revenu (9), la fraude aux prestations et ses pénalités (9),
  l'assurance maladie (9), les pupilles de la nation et la mention « Mort pour la
  France » (7), la procédure pénale (6, dont la plage L. 377-1 à L. 377-5), le financement
  (6), les exonérations de cotisations patronales, l'organisation des caisses, les
  accidents du travail, les prestations familiales (5 chacune), les règles générales de
  l'administration (4), et treize raisons d'un ou deux articles.
- *115 restent à lire*, nommés ci-dessous.

**Les liens faux de la base.**

- `LO_CMIL_L488.aspx` (« Article L 488 ») lie `LEGIARTI000006794869`, qui est L. 481 du
  code des pensions militaires (1951-2017), le lien de `LO_CMIL_L481.aspx`. L. 488 est à
  l'index sous `LEGIARTI000006794876` (1955-2010) et `LEGIARTI000021649264` (2010-2017).
- `LO_CSS_D161-2-11.aspx` porte deux liens « Voir article » : `LEGIARTI000006735317`,
  D. 161-2-11, et `LEGIARTI000006735316`, qui est D. 161-2-10.
- `LO_CSS_D173-24.aspx` et `LO_CSS_D173-25.aspx` disent l'article « Rétabli par décret
  2010/778 » (et « 2010-778 ») « du 31/12/2010 » ; leur lien, `LEGITEXT000023388478`,
  est à l'index le décret n° 2010-1778 du 31 décembre 2010 : le libellé est faux, le lien
  juste.
- `LO_NCPC_383.aspx` lie le texte `LEGITEXT000006071570`, quand les 59 autres articles du
  code de procédure civile qui ont un lien lient `LEGITEXT000006070716` ; l'index ne porte
  ni l'un ni l'autre : ce que vise ce lien n'est pas tranché ici.

Ne sont pas faux : `LO_CSS_L130-1.aspx`, qui lie L. 133-10 (« abrogé. Voir
Article L133-10 », le même arrondi des cotisations depuis 2015) ; les six pages R. 356-2
à R. 356-9, qui lient aussi les décrets qui les modifient ou les abrogent : le décret
n° 2001-1077, article 1, et le décret n° 2004-857, article 8, dont l'index porte les
articles liés ; R. 356-2, le décret n° 88-679 aussi, sans identifiant d'article.

**Les 115 à lire, et ce qui manque.**

- *L'article n'est pas dans l'index* (111). L'index ne garde que les textes du champ
  social ; ni l'identifiant que la base lie, ni aucune version du même numéro n'y est, et
  Légifrance refuse le conteneur (403). Code civil (43) : 47, 112, 118, 128, 184, 191,
  201, 205, 206, 207, 214, 276, 342, 1153, 1289, 1291, 1351, 1376, 1382, 2219, 2220
  ancien, 2222, 2224, 2228, 2231, 2233, 2234, 2237, 2240, 2241, 2242, 2244, 2244 ancien,
  2247, 2248, 2248 ancien, 2249, 2251 ancien, 2258, 2262 ancien, 2270-1 ancien, 2428,
  2434. Code de procédure civile (59) : 12, 23-1, 125, 446-1, 446-2, 446-3, 451, 453,
  462, 463, 509-1, 509-2, 509-3, 509-5, 554, 643, 653 à 664, 674 à 682, 695, 700, 771,
  776, 849-1, 910, 932, 1055, 1055-3, 1056, 1056-1, 1059, 1060, 1082, 1140, 1149-1, 1152,
  1157, 1196, 1294, 1303-1, 1303-4 — 658 sans aucun lien. Code général des impôts (4) :
  4 B, 775, 1516, et l'article 5 de l'annexe IV, dont le lien vise une section
  (`LEGISCTA000006179466`, au 31 décembre 2000). Code de procédure pénale : 421, 593.
  Code pénal : 226-13. Code du service national : L. 122-9. Code de la sécurité sociale :
  L. 337 ancien, d'avant la numérotation de 1985, que la base lie au fac-similé du
  Journal officiel du 4 janvier 1975, pages 198 et 199.
- *La version visée manque à l'index* (2). L'article 1496 du code général des impôts
  (lien `LEGIARTI000006311725`, « en vigueur ») : l'index n'en porte que la version de
  1950 à 1979, la taxe sur les chiens. L'article 146 du code de la famille et de l'aide
  sociale, lié au 22 décembre 2000 (`LEGIARTI000006681337`) et, en vigueur, dans le code
  de l'action sociale et des familles (`LEGIARTI000006796594`) : l'index porte ses
  versions de 1961 au 1er janvier 2000, les recours de l'aide sociale, et ni l'un ni
  l'autre identifiant.
- *Deux silences, que ni fiche ni limite ne déclare* (2), lus à l'index, pour la session
  du modèle : R. 161-16 (`LEGIARTI000006747397`, en vigueur depuis le 20 juin 2006) : « les
  périodes de perception de l'allocation de préparation à la retraite mentionnée à
  l'article 125 de la loi de finances pour 1992 (n° 91-1322 du 30 décembre 1991) modifiée
  sont assimilées à des périodes d'assurance. Il est décompté autant de trimestres qu'au
  cours de l'année civile correspond de fois 90 jours de perception de ladite
  allocation » ; L. 311-8 (`LEGIARTI000006742444`, 1985-1998) : les assurés qui cessent de résider ou de
  travailler en France « conservent le bénéfice de la rente inscrite à leur compte
  individuel d'assurance vieillesse à la date du 1er janvier 1941 ».

**Ce que la lecture n'a pas fait.** Aucun candidat d'écart : des 297 articles hors de la
liste, la lecture de la version liée de ceux que l'index porte n'a relevé aucune règle
que le modèle contredise ; les
deux silences ci-dessus ne sont pas des contradictions. Le contenu des 345 articles de la
liste n'a pas été confronté ici aux règles : la liste de contrôle le fait rédaction par
rédaction, sous le cliquet de `perimetre.yaml`. Le registre seul a changé
(`data/reference/legislation/cnav/references.csv`, 527 lignes) ; aucune règle, aucune
fiche, aucun bloc « Reprise » d'une autre étape.
