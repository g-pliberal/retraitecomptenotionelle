# Relecture de E12 : la réserve de 2006, et la Cipav de `surcote_par_age_seul` en versions (R-E13)

File E, relecture R-E13, le 6 novembre 2026 (action 130, vague 11, sur Opus), du commit
45453aa (E12, session `session_01FVFLAkniccVXUs9FLf5CKu`) et de sa note
`130/2026-11-06-e12-surcote-par-age-seul.md`. Rien n'est modifié : ni règle, ni donnée,
ni test.

**Verdict.** Conforme pour l'essentiel : chaque citation, chaque date et chaque montant
de E12 se retrouvent, au centime, à la source et dans les deux moteurs. Quatre écarts,
tous mineurs (aucun montant servi ni déclaré ne bouge), et un candidat hors de la tâche.

**Méthode.** Index de la DILA récupérés puis mis à jour : JORF au 6 novembre 2026
(JORF_20261106-002608), LEGI au 5 novembre (LEGI_20261105-214938). Les moteurs : un script
hors du dépôt, qui pose les cas par `servi_et_refait` (`tests/outils_pont.py` : le
portage, refait par le moteur Python) et un espion sur
`retraite_notionnelle.droit.acquerir.acquerir`, qui relève les cotisations revalorisées
de `cipav_complementaire` année par année. Réglages de E11 et E12 : `profil` plat,
`euros` 2026, `enfants` 0, `sexe` F, `salaire` 2, `debut` 22, `statut`
`profession_liberale`, `liquidation` 66, `liquidation_mois` 9 ; le tout refait sous
`PRESOMPTIONS_DECALEES=1`, aux mêmes valeurs, au dernier chiffre.

## 1. La réserve de l'arrêté du 3 octobre 2006

**La citation : conforme.** JORFARTI000002050100 (Journal officiel du 13 octobre 2006),
relu en entier : « sont approuvées les modifications apportées aux statuts […] (art. 2.7
et 2.21 de la seconde partie « règlement intérieur », troisième partie « Régime de
retraite complémentaire », ainsi que les dispositions transitoires). L'arrêté du 21 mars
1979 portant approbation des statuts de la section professionnelle des architectes,
agréés en architecture, ingénieurs, techniciens, experts et conseils et relatif au régime
d'assurance vieillesse complémentaire est abrogé à compter du 1er janvier 2007, à
l'exception de l'article 16 et de l'article 17, alinéa 2, qui seront abrogés le
1er janvier 2008. Nota. - L'arrêté, accompagné de son annexe, sera publié intégralement
au Bulletin officiel d'octobre 2006 ». Le texte nomme les articles de « l'arrêté du
21 mars 1979 portant approbation des statuts » ; E12 écrit « des statuts de 1979 » :
lecture appuyée, les arrêtés suivants modifiant l'« art. 17 » des statuts (ci-dessous).

**L'arrêté de 1979 et les dispositions transitoires, hors de l'index : conforme.**
« 21 mars 1979 » : 106 documents ; « architectes » et « statuts » en 1979 : aucun ;
« transitoires » avec « architectes » ou « cipav », de 2006 à 2009 : l'arrêté de 2006,
et un plan comptable des offices de l'habitat du 24 décembre 2008, étranger à la Cipav.

**Écart 1 (mineur) : les arrêtés qui modifient l'article 17 de 1979, non cités.** Trois
arrêtés de l'index, que ni E11, ni R-E12, ni E12 ne nomment (aucune occurrence au dépôt),
modifient les statuts du complémentaire de 1979, article 17 compris : du 5 mai 1981
(JORFTEXT000000871027, JO du 19 mai 1981) : « modifications apportées aux statuts […]
relatifs au régime d'assurance vieillesse complémentaire (art. 8, 11 et 17) » ; du
17 juin 1985 (JORFTEXT000000840042, JO du 21 juin 1985) : « modifications apportées aux
art. 4, 9, 12, 13, 17, 17-bis et 21 des statuts » ; du 29 juillet 2003
(JORFARTI000001531753, JO du 9 août 2003) : « modifications apportées aux statuts du
régime complémentaire d'assurance vieillesse (art. 9, 11, 13, 15, 17 et 17 bis) », avec
« Nota. - L'arrêté du 29 juillet 2003 sera publié intégralement au Bulletin officiel
n° 2003-35 ». S'y ajoute celui du 4 mai 1982 (JORFTEXT000000677739), « une modification
apportée aux statuts […] relatifs au régime d'assurance vieillesse complémentaire »,
« intégralement publié au Bulletin officiel », article non dit. L'article 17 en vigueur
en 2007 est donc celui de 1979 modifié au moins trois fois ; les arrêtés de 1981 et de
1985 n'ont que leur titre à l'index (au fac-similé du Journal officiel ou au Bulletin
officiel : `138/2026-11-05-la-file-des-fac-similes.md`). La lecture B de 2007 et la
question 22 doivent les nommer. Le verdict « 2007 non tranché » n'en bouge pas.

**« 2007 non tranché » : à bon droit.** Les articles 16 et 17, alinéa 2, restent en
vigueur toute l'année 2007, et les dispositions transitoires sont approuvées avec la
troisième partie ; ni les uns ni les autres ne sont lus : aucune des deux lectures n'est
intenable. Cas de E12 refait : née le 10 mars 1940, liquidation à 66 ans et 9 mois,
pension au 1er janvier 2007 (65 ans le 10 mars 2005 : une année entière). Servi dans les
deux moteurs : 6 947,955483 € (« cotisations revalorisées 112,064 € × rendement 6.20% »,
sans coefficient). Relevés : de 1979 à 2006, 112 063,7981 € ; 1979, 1 410,1318 € ; de
1980 à 2006, 110 653,6663 € ; de 1979 à 1991, 43 931,5488 €. À la main :
112 063,7981 × 0,06 = 6 723,8279 ; × 0,002 = 224,1276 ; 6 947,9555 €. Lecture A,
0,05 × 0,062 = 0,0031 : 112 063,7981 × 0,003 = 336,1914 ; × 0,0001 = 11,2064 ;
347,3978, **347,40 €** ; 110 653,6663 × 0,003 = 331,9610 ; × 0,0001 = 11,0654 ;
343,0264, **343,03 €** ; 43 931,5488 × 0,003 = 131,7946 ; × 0,0001 = 4,3932 ; 136,1878,
**136,19 €** (de 1962, affiliation à 22 ans, à 1991). Lecture B : 0 € si les textes de
1979 ne majorent rien. Conforme au centime.

**Écart 2 (mineur) : une lecture de l'affiliation non écrite.** Les trois décomptes « de
la première année du régime » comptent les années de cotisation depuis 1979 ; compter de
même les « trente années d'affiliation à la C•I•P•A•V » depuis 1979 ne les atteint qu'au
1er janvier 2009 (1979 à 2008). Au cas de 2007, 28 années : la lecture A rend alors 0 €,
non 347,40 ou 343,03 € ; et pour une pension de 2008, 29 années : rien n'est dû, le
modèle sert juste. Lecture faible — l'affiliation est à la caisse, dès 1962 ou 1967 aux
cas posés, et le régime de 1979 « se substitue » à ceux de 1956 (candidat, plus bas) —,
mais non intenable tant que l'article 3.6 n'est pas lu. Effets : en 2007, l'ensemble des
valeurs ne change pas (0 €, ou de 136,19 à 347,40 €) ; de 2008 à 2012, l'erreur tient
sous toutes les lectures de l'affiliation de 2009 à 2012 (33 années au cas de 2012), et
dépend de cette lecture pour une pension de 2008.

**De 2008 à 2012, erreur déclarée sous une réserve : conforme.** Le modèle : périodes de
1979 à 1999 et de 2000 à 2012 de `cipav_complementaire`, `surcote_par_trimestre: null`,
« AUCUNE SURCOTE LUE AVANT 2013 » : une borne de période, sans texte. Cas refait : née le
10 mars 1945, pension au 1er janvier 2012 (65 ans le 10 mars 2010 : une année entière).
Servi dans les deux moteurs : 9 791,174793 € (« 157,922 € × rendement 6.20% », sans
coefficient). Relevés : de 1979 à 2011, 157 922,1741 € ; 1979, 1 533,6360 € ; de 1979 à
2008, 135 298,4577 € ; de 1980 à 2009, 141 074,4652 € ; de 1979 à 2009,
142 608,1012 € ; de 1979 à 1996, 69 492,8927 €. À la main : 157 922,1741 × 0,06 =
9 475,3304 ; × 0,002 = 315,8443 ; 9 791,1748 €. Depuis l'affiliation, de 1967 à 1996 :
69 492,8927 × 0,003 = 208,4787 ; × 0,0001 = 6,9493 ; 215,4280, **215,43 €** ;
135 298,4577 : 405,8954 + 13,5298 = 419,4252, **419,43 €** ; 141 074,4652 : 423,2234 +
14,1074 = 437,3308, **437,33 €** ; 142 608,1012 : 427,8243 + 14,2608 = 442,0851,
**442,09 €**. E12 a raison contre R-E12 (1.3) : le décompte depuis l'affiliation réduit
l'écart de 2008 à 2012, où le modèle ne majore rien ; il le grossit de 2013 à 2022.
La lecture contraire (rien de majoré de 2008 à 2012) n'a d'appui que dans des
dispositions transitoires non lues, et la seule date de transition que le Journal
officiel montre est le 1er janvier 2008 : déclarer l'erreur, sous la réserve, se défend.
Mais « au moins 215,43 € » ne vaut que hors de cette réserve, que E12 dit pouvoir
« borner les points majorés » : c'est ainsi qu'il faut le lire.

**L'erreur de 2013 à 2022 : conforme.** Née le 10 mars 1949, pension au 1er janvier 2016 :
12 625,514345 € servis, « × coefficient de majoration 1.0500 ». Relevés : de 1979 à
2015, 193 940,3125 € ; 1979, 1 558,2124 € ; de 1979 à 2008, 137 466,6071 € ; de 1980 à
2009, 143 335,1748 € ; de 1979 à 2009, 144 893,3872 € ; de 1979 à 2000,
89 447,7163 €. À la main : 193 940,3125 × 0,062 = 12 024,2994 ; × 1,05 = 12 625,5143 ;
majoration 581,8209 + 19,3940 = 601,2150 ; 144 893,3872 × 0,0031 = 449,1695, écart
152,0455, **152,05 €** ; 426,1465, 175,07 € ; 444,3390, 156,88 € ; depuis l'affiliation
(1971 à 2000), 89 447,7163 × 0,0031 = 277,2879, écart 323,93 € : l'écart grossit.
« Au moins 152,05 € » : conforme.

## 2. Le test du décret garde sa table : conforme

Mutations essayées, sans rien commiter, le fichier rétabli après chacune
(`-k decret_2026_418`, trois tests) : la ligne de l'article 10 ôtée de la table
(`ARTICLES_DU_DECRET_2026_418`, `tests/test_sections_liberales.py`) : les deux tests
neufs rouges ; son identifiant faussé, dans l'ordre (…523 en …522) : l'ancien test et
celui de l'index rouges ; son texte faussé (« 60-664 » en « 60-665 ») : l'ancien rouge ;
un texte donné à l'article 29 : l'ancien et le structurel rouges ; les identifiants de
« 18, fin » et de 19 permutés : les trois rouges ; dans la fiche
`decret_2026_418_liberaux`, l'identifiant de l'article 10 changé : l'ancien rouge.
Rétablis : trois verts ; l'index à jour du 6 novembre, ses 32 documents « Article
DECRET » du décret sont ceux de la table. Remarque : `tests.yml` ne récupère pas
l'index ; sur GitHub, le test de l'index est sauté, comme E12 le dit : la fidélité des
identifiants au Journal officiel ne s'y vérifie que par l'ancien test (chaque identifiant
dans une lecture de la fiche). Les 14 lignes changées de `decret_2026_418_liberaux`
(`sources.a_relire`) ne citent que l'arrêté de 2006, au mot près ; « approuve la
troisième partie des statuts » résume « approuvées les modifications apportées aux
statuts (… troisième partie …) » : conforme.

## 3. La fiche, écrite en versions pour la Cipav

**Citations et dates : conformes.** Décret n° 79-262, article 5, LEGIARTI000006767479
(« 1979-01-01 → 2004-01-01 ») et LEGIARTI000006767480 (« 2004-01-01 → 2026-07-01 »), au
mot près. Arrêté du 16 décembre 2021 (JO du 24 décembre 2021), 19°, et article 2
(« entrent en vigueur le 1er janvier 2022 ») ; arrêté du 20 mars 2023 (JO du 24 mars
2023), 17°, a) et b), et article 2 (« applicable aux cotisations et aux prestations dues
au titre des périodes courant à compter du 1er janvier 2023 ») ; décret n° 2026-418,
article 20 (JORFARTI000054153655, JO du 31 mai 2026), et 79-262, articles 5-2, II
(LEGIARTI000054168515) et 5-1, 1°, a (LEGIARTI000054168518), en vigueur le 1er juillet
2026 : au mot près. Bornes : 1er janvier 2007 et 2008 (arrêté de 2006), 2022 (article 2
de 2021), 2023 (article 2 de 2023), 1er juillet 2026 (article 30 du décret, dit par
LEGI) : conformes. Le PDF des statuts au 1er janvier 2023 n'est pas relu ici.

**La liste des arrêtés de 2007 à 2025 : conforme.** Recherche sans borne de réponses
(« statuts » et « cipav », « interprofessionnelle de prévoyance », « section
professionnelle des architectes » ou « profession libérale non rattachée », arrêtés,
2006 à 2026) : ceux que la fiche nomme, et celui du 8 décembre 2006, qui ne touche que
l'invalidité-décès. « 3.15 » et « statuts », de 2006 à 2026 : les deux seuls arrêtés qui
nomment un article 3.15 hors de 2021 et 2023, du 26 novembre 2010 et du 9 février 2012,
sont ceux de la section des experts-comptables (CAVEC).

**Écart 3 (mineur) : la version de 2022 ne cite pas sa source de l'âge.** `cipav_2022`
porte `surcote_age_debut` « l'âge du taux plein du 1° de L. 351-8, que l'article 3.13,
1°, nomme » ; ce texte est le 18° du même arrêté de 2021 (« L'article 3.13 est remplacé
par les dispositions suivantes : […] « 1° A taux plein : « - à partir de l'âge du taux
plein prévu au 1° de l'article L. 351-8 du code de la sécurité sociale » »), que la
version ne cite pas (elle cite le 19° et l'article 2) ; la version de 2023 le prend au
PDF de la caisse. Même document (JORFARTI000044554134) : à citer.

**Ce que la fiche dit servir est servi.** Essayés dans les deux moteurs, sous les deux
jeux : pensions de 2007 et de 2012, sans coefficient (« rien jusqu'en 2012 ») ; de 2016,
1,05 (« tous les points dès 2013 ») ; née le 10 mars 1954, liquidation à 68 ans, pension
au 1er avril 2022 : 18 094,447 €, « coefficient de majoration 1.0500 » ; née le 10 mars
1958, à 68 ans et 9 mois, pension au 1er janvier 2027 : 23 790,0215 €, 1,05. Comptées
de 65 ans, ces deux pensions auraient trois années entières, 1,15 ; de l'âge du taux
plein du dépôt (66 ans et 7 mois pour 1954, 67 ans pour 1958,
`age_annulation_decote.csv`, non relu ici), une : le moteur compte bien de l'âge du taux
plein, comme les versions de 2022 et d'après. Approximations : conformes à ce qui est
servi. `perimetre.yaml` : le cliquet à 9305, le compte réel de `textes.sans_statut()`
9305, l'égalité exigée par `noyau/textes.py` : conforme.

## 4. Le bloc « Reprise » et « Ce qui reste »

Recomptés par `carte.manques()` : 73 fiches à manques, 412 manques ;
`surcote_par_age_seul` n'en a plus, et n'est pas dans `LUES_AU_DROIT` : conforme, comme
les six régimes qui restent (CARMF et ASV, CARPIMKO, CAVEC, CAVP, CPRN) et les montants
de la Cipav. Les trois pistes sont dites ouvertes : « non vérifiées » dans la note
(« Ce qui reste ») et le bloc, « à vérifier » au journal. **Écart 4 (mineur)** : le bloc écrit « la CARMF au premier
trimestre 2017 », la note et le journal « la CARMF et l'ASV » : l'ASV y manque.

## Candidat, hors de la tâche

Le décret n° 79-262 (JORFTEXT000000702512) : « Ce régime se substitue à celui des
ingénieurs, techniciens, experts et conseils (décret n° 56-572 du 8 juin 1956 modifié),
d'une part, et à celui des architectes (décret n° 56-1341 du 29 décembre 1956 modifié),
d'autre part, qui sont abrogés. » `cipav_complementaire` ouvre en 1979 et écrit du décret
« qui institue le complémentaire » ; aucun fichier du dépôt ne nomme ces deux décrets.
À instruire : ce que sont devenus les droits acquis dans ces régimes de 1956 à 1978, et
si les « trente années » d'affiliation et de cotisation les comptent.

## Tests

`tests/test_sections_liberales.py`, `tests/test_carte.py`, `tests/test_textes.py`,
`tests/test_regle_de_chacun.py` (le premier, seul à nommer la fiche) : 100 verts ;
sous `PRESOMPTIONS_DECALEES=1`, 99 verts et un sauté, comme E12 le dit. La suite rapide :
voir le message du commit.

## Ce qui repart à E13

Les quatre écarts : nommer les arrêtés du 5 mai 1981, du 4 mai 1982, du 17 juin 1985 et
du 29 juillet 2003 dans la lecture B de 2007 et la question 22 ; écrire la lecture de
l'affiliation comptée depuis 1979 (0 € en 2007 sous la lecture A, 2008 dépendant de
cette lecture) ; citer le 18° de 2021 dans `cipav_2022` ; l'ASV dans la piste de 2017.
