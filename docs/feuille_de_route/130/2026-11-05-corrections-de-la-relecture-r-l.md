# Les corrections de la relecture R-L : la CARPV d'avant 2022, le coefficient des biologistes

File L-bis, vague 7, le 5 novembre 2026 : les écarts de la relecture R-L
(`2026-11-04-relecture-ouverture-de-la-base-des-liberaux.md`), qui a relu le travail L
(`2026-11-04-ouverture-de-la-base-des-liberaux.md`). Chaque texte a été ouvert ici, dans
l'index de la DILA récupéré dans la session (LEGI à jour au 2 novembre 2026, JORF au
3 novembre). Le bloc « Reprise » de l'action 130 n'est pas touché (file E seule).

## 1. L'écart moyen : la CARPV d'avant le 1er janvier 2022, présumée

**Ce qui est lu.** Les statuts de 2021 entrent en vigueur le 1er janvier 2022 : « Les
modifications des statuts prévues par le présent arrêté entrent en vigueur le 1er janvier
2022 » (arrêté du 18 octobre 2021, article 2, JORFARTI000044220741). Avant, le Journal
officiel ne publie que des modifications :

- l'arrêté du 11 janvier 2011 (JORFARTI000023448554), lu en entier : de l'article 21 du
  titre II, il ne récrit que le sixième alinéa, celui de l'inapte (« peuvent demander à
  bénéficier de la retraite à 60 ans sans minoration ») ; l'article 23 demande d'avoir
  « liquidé ses pensions de vieillesse personnelles auprès de la totalité des régimes
  légaux ou rendus légalement obligatoires, de base et complémentaires », mais au seul
  vétérinaire qui veut que « le bénéfice de la retraite complémentaire [soit] entièrement
  cumulée avec une activité professionnelle » ;
- les arrêtés du 16 avril 2014 (JORFARTI000028939421), du 18 février 2015
  (JORFARTI000030285511) et du 2 novembre 2015 (JORFARTI000031549970) : aucune occurrence
  de « liquid » en 2014 et en novembre 2015, de « soixant » ni de « 60 ans » dans les
  trois ; « base » n'y vient que pour les bases d'appel des cotisations ; en 2014,
  l'article 13 perd ses « quatrième et cinquième alinéas », que nul texte publié ne donne.

Les statuts eux-mêmes ne sont au Journal officiel que par leurs avis : l'arrêté du
5 juillet 1999 approuve les modifications des « art. 3 à 40 du titre II » du régime
complémentaire (JORFARTI000001562289), et « sera publié intégralement au Bulletin
officiel no 99/33 du ministère de l'emploi et de la solidarité » (JORFARTI000001368893) ;
celui du 28 août 2006, des « art. 21, 23 et 24 du titre II », au Bulletin officiel du
ministère de la santé (JORFARTI000001494755). Ni l'un ni l'autre n'est dans l'index ; une
recherche sur le web n'en a rien trouvé, et le site de la CARPV ne sert pas ses statuts
d'avant 2022.

**Verdict : les textes lus ne tranchent pas.** Rien ne dit que la complémentaire attende la
base, rien ne dit le contraire. Aucune règle ne change : la présomption est déclarée,
avec son effet (les trois cas du test qui la datent avant 2022, le vétérinaire né le
10 février 1955, le 10 février 1961 et le 10 octobre 1961), dans les approximations de
`liquidation_regime_par_regime`, dont la version dit désormais la date d'effet des
statuts de 2021 ; dans celles de `carpv_minoration_age_seul` ; dans la limite des écarts
au droit positif (`docs/limites/ecarts-au-droit-positif.md`, les départs échelonnés) ;
et au commentaire de `SANS_LEUR_BASE` (`departs.py`). Les statuts de 1999 à 2021 restent
à lire au Bulletin officiel ou auprès de la caisse (`a_relire` de la fiche).

## 2. Le cliquet des textes

La note L dit que « le cliquet des textes descend à 9 344 ». Le commit 9772e14 change
`redactions_sans_statut` de 9 340 à 9 334 (`git show 9772e14 --
data/reference/textes/perimetre.yaml`) : il descend à 9 334. La note L, un récit, n'est
pas récrite ; un renvoi daté s'ajoute à son bout.

## 3. Le coefficient des biologistes, jusqu'à l'âge de L. 351-8, 1°

**Le texte.** « La prestation supplémentaire de vieillesse est alors réduite par
application d'un coefficient d'anticipation qui est fonction du nombre de trimestres
manquants, à la date d'effet des droits, pour atteindre l'âge fixé à l'article L. 351-8
(1°) du code de la sécurité sociale. Ce coefficient est égal à 1,25% par trimestre
manquant dans la limite de vingt trimestres » (statuts de la CAVP, prestations des
biologistes, article 14, arrêté du 23 juin 2011, JORFARTI000024270214, en vigueur le
30 juin 2011) ; « La prestation complémentaire de vieillesse est réduite par application
d'un coefficient de minoration qui est fonction du nombre de trimestres manquants, à la
date d'effet des droits, pour atteindre l'âge fixé au 1° de l'article L. 351-8 [...] Ce
coefficient est égal à 1,25 % par trimestre manquant dans la limite de vingt trimestres »
(règlement de 2026, III, article 1er, JORFARTI000054436087).

L. 351-8, 1° : « Les assurés qui atteignent l'âge prévu à l'article L. 161-17-2 augmenté de
cinq années » (LEGIARTI000023030950, « applicables aux pensions prenant effet à compter du
1er juillet 2011 » ; LEGIARTI000028498855, pensions du 1er février 2014 au 31 août 2023) ;
« l'âge prévu au premier alinéa de l'article L. 161-17-2 augmenté de trois années »
depuis (LEGIARTI000047452736, LEGIARTI000051289852). L'âge de L. 161-17-2 : « 1° Soixante
ans pour les assurés nés avant le 1er juillet 1951 ; 2° Soixante ans et quatre mois pour
les assurés nés entre le 1er juillet 1951 et le 31 décembre 1951 inclus ; 3° Soixante ans
et neuf mois pour les assurés nés en 1952 ; 4° Soixante et un ans et deux mois pour les
assurés nés en 1953 ; 5° Soixante et un ans et sept mois pour les assurés nés en 1954 ;
6° Soixante deux ans pour les assurés nés à compter du 1er janvier 1955 » (D. 161-2-1-9,
LEGIARTI000025089933, du 31 décembre 2011 au 1er septembre 2023 ; L. 161-17-2,
LEGIARTI000025014605). L'âge de L. 351-8, 1°, est donc : 65 ans avant juillet 1951,
65 ans 4 mois, 65 ans 9 mois (1952), 66 ans 2 mois (1953), 66 ans 7 mois (1954), 67 ans
depuis 1955 ; la table `age_annulation_decote.csv` du dépôt porte ces valeurs (65,00,
65,33, 65,75, 66,17, 66,58, 67,00). Le modèle comptait jusqu'à 67 ans à toute génération.

**Les valeurs, à la main.** Le biologiste né le 10 février part au 1er mars ; les
trimestres manquants se comptent au trimestre supérieur, comme le modèle les compte
ailleurs (le texte ne dit pas l'arrondi : déclaré) :

| Né le | Parti à | Pension | Âge de L. 351-8, 1° | Manquants | Coefficient | Avant |
|---|---|---|---|---|---|---|
| 10/02/1950 | 62 ans | 1/03/2012 | 60 + 5 = 65 ans | 3 ans = 12 | 1 − 12 × 1,25 % = 0,85 | 0,7625 |
| 10/02/1952 | 63 ans | 1/03/2015 | 60 a 9 m + 5 = 65 a 9 m | 2 a 9 m = 11 | 1 − 11 × 1,25 % = 0,8625 | 0,80 |
| 10/02/1953 | 63 ans | 1/03/2016 | 61 a 2 m + 5 = 66 a 2 m | 3 a 2 m = 12,67 → 13 | 1 − 13 × 1,25 % = 0,8375 | 0,80 |

Les trois cas sont choisis pour que l'arrondi ne dépende pas de l'âge compté à
l'anniversaire ou au premier du mois. « Avant » est ce que les deux moteurs servaient :
0,7625 pour le premier, soit 19 trimestres et non 20 : le modèle y prend le plus
favorable de l'âge et de la durée, et la durée qui manque lui en oppose 19 (voir le
point 5).

**Le test d'abord.** `test_le_biologiste_est_minore_jusqu_a_l_age_de_l_351_8`
(`tests/test_ouverture_des_liberaux.py`), par `servi_et_refait` : vu rouge (0,7625, 0,80,
0,80), vert après. **La correction**, en données : `age_taux_plein_par_generation:
age_annulation_decote` aux périodes de 2009 et d'après de
`asv_directeurs_laboratoire.yaml`, celles où L avait déjà mis l'âge d'ouverture à la
génération, et `asv_directeurs_laboratoire` à la liste des régimes de la fiche
`age_annulation_decote` ; aucun code, l'interrupteur existant dans les deux moteurs.
**Ce qui est présumé** : de 2009 au 29 juin 2011, la règle de 2011 (les statuts d'avant
ne sont pas lus) ; avant 2009, les 67 ans du guide de la CNAVPL de 2025, inchangés.

## 4. La déclaration du coefficient des biologistes

L'approximation de `asv_autres_professions_de_sante` ne nommait que « soixante-cinq ans aux
générations nées avant le 1er juillet 1951 » : elle dit désormais chaque génération, de
65 ans à 67 ans, avec ses textes, l'effet mesuré, et ce que le texte ne tranche pas.
R-L notait aussi que le règlement de la CARPV de 2026 n'est pas « mot pour mot »
l'article 34 de 2021 : relu, son article 2 dit « les adhérents remplissant les conditions
de l'article 1 er », où 2021 dit « de l'article 33 » ; la fiche cite la phrase de 2021,
attribuée à 2021.

## 5. Ce que le texte ne tranche pas, et les restes

- **La durée qui efface la minoration des biologistes.** Les deux textes comptent les
  trimestres « pour atteindre l'âge » ; le modèle prend le plus favorable de l'âge et de la
  durée (`decote_annulee_par_la_duree`, vrai par défaut) : un biologiste au taux plein de
  durée n'est pas minoré, quand le texte le minore. Déclaré dans la fiche ; à une file du
  modèle (la CARPV a sa fiche `carpv_minoration_age_seul` pour le même interrupteur).
- **Les 65 ans du parent de trois enfants** des générations de juillet 1951 à 1955
  (loi n° 2010-1330, article 20, IV : « l'âge mentionné au 1° dudit article est fixé à
  soixante-cinq ans ») : le modèle ne les donne pas au biologiste ; que la CAVP les
  applique, le texte ne le dit pas.
- **La CARPV de 1999 à 2021**, au Bulletin officiel ; **la CAVP d'avant 2011**.
- **La CRPNPAC** (écart 4 de R-L) : hors de cette zone, à la file E et à sa fiche.

## 6. Les deux moteurs, les tests

`tests/test_ouverture_des_liberaux.py` : 36 verts. `python -m pytest -m rapide` : 4 423
verts ; sous `PRESOMPTIONS_DECALEES=1` : 4 224 verts. Les fichiers qui lisent les fichiers
touchés (`test_departs`, `test_sections_liberales`, `test_pcv_sante`, `test_moteur`,
`test_donnees`, `test_carte`, `test_regle_de_chacun`, `test_conservation` et six autres) :
550 verts. Le paquet refait (`python scripts/construire_donnees.py`) ; le cliquet des
textes reste à 9 334 ; `verifier_prose.py --corriger` : « la prose déclarée dit le vrai ».
