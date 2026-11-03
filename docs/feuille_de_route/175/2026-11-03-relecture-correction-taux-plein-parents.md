# Relecture de la fiche corrigée du taux plein des parents de trois enfants (file M4-bis)

File R-M4-bis, le 3 novembre 2026 : relecture indépendante du commit e5e8d34 (session
M4-bis, note `2026-11-03-correction-taux-plein-parents-de-trois-enfants.md`), qui corrige
la fiche `taux_plein_a_soixante_cinq_ans`, son test et la limite d'après la relecture R-M4
(`2026-11-03-relecture-taux-plein-parents-de-trois-enfants.md`). Rien n'a été repris de la
session ni de mémoire : l'index de la DILA récupéré dans la session (LEGI à jour au
2 novembre 2026, aucun incrément depuis ; JORF au 3 novembre) ; les deux recueils de
l'Agirc-Arrco, la circulaire Cnav n° 2014-64 et la circulaire Agirc-Arrco du 20 janvier
2020 téléchargés le jour, leur empreinte recalculée. Chaque fragment cité entre « » a été
cherché par un script dans le texte de sa source. Rien n'a été modifié : ni règle, ni
donnée, ni test, ni fiche.

**Verdict : conforme.** Chaque écart de R-M4 est corrigé ou déclaré ; chaque citation est
exacte, mot pour mot, dans la rédaction en vigueur à la date qui compte ; chaque chiffre
de la fiche, du test et de la note se refait à la main ; aucun calcul n'a changé ; les
tests sont verts, sous `PRESOMPTIONS_DECALEES=1` aussi ; le point que les textes ne
tranchent pas est déclaré comme tel, et la circulaire de l'Agirc-Arrco lue ici ne le
tranche pas davantage. Trois remarques faibles, sans effet sur un calcul ni sur un
chiffre (point 6).

## 1. Les écarts de R-M4, un à un

| Écart de R-M4 | Ce qu'en fait e5e8d34 | Constat |
|---|---|---|
| 5, grave : la fiche disait que l'Agirc-Arrco « garde l'âge de sa génération », le test l'affirmait | la phrase est retirée (aucune occurrence dans la fiche) ; `test_les_regimes_alignes_suivent` ne porte plus que les salariés agricoles et le RSI ; l'Arrco et l'Agirc-Arrco passent dans `ECARTS_DECLARES` (0,95, 0,93, 0,92) et `ENCORE_A_L_AGE_DE_LA_GENERATION`, comme écarts ; une approximation les déclare, textes, citations et effet chiffré ; `test_la_fiche_declare_chaque_ecart` interdit la phrase | **corrigé** dans la fiche et le test, **déclaré** en attendant le calcul |
| 6, moyen : fonctionnaires, CAVIMAC, points d'avant 1973 ni servis ni déclarés | une approximation pour chacun, et une pour le RCI, que R-M4 n'avait pas vu ; la limite les nomme | **déclaré** |
| 7, mineur : « article 87, VIII, C » | « article 87, II, 19°, que le VIII, A, applique à ces pensions » | **corrigé** (point 2) |
| 7, mineur : les avocats depuis 2019 | R. 723-38 jusqu'au 8 juillet 2019, puis R. 653-2 | **corrigé** |
| 7, mineur : la citation coupée du point 2.3.2.1 | poursuivie jusqu'à « au moins égale à 66 % » | **corrigé** |

## 2. Les textes, à la version en vigueur

| Texte | Ouvert | Constat |
|---|---|---|
| Accord du 18 mars 2011, article 1er, recueil « Accords nationaux des partenaires sociaux » | PDF téléchargé le 3 novembre 2026, sha256 0186b6b165ad2a5f5f561deb969c6a35c661dc2e1fedbfcdcaa24801f51104c1, identique ; pages imprimées 147 et 148 (135 et 136 du fichier) | les trois fragments cités, mot pour mot, la coupure « [...] » ne retranchant que le cas des assurances sociales agricoles ; le champ, « prenant effet à compter du 1er juillet 2011 et jusqu'au 31 décembre 2018 au plus tard » : **conforme** |
| Accord du 17 novembre 2017, « Applicable au 1er janvier 2019 », articles 84 et 98 | PDF, sha256 b8af8df7372e4f897c1ca0c4fd9bf4baaa5b706ec4737b8e51b593c5a2a4fccb, identique ; pages imprimées 51-52 et 57-59 (53-54 et 59-61 du fichier) | 84, 1 et 3, mot pour mot ; « cet âge » (84, 2) ; la table : « moins 1 an 1 trimestre » 0,95, « moins 1 an 3 trimestres » 0,93, « moins 2 ans » 0,92, lus sur la page (l'extraction disjoint les cellules) ; 98 : « Les participants, nés à partir du 1er janvier 1957 » (l'exposant de « 1er » disjoint) : **conforme** |
| Loi n° 2010-1330, article 20, IV | LEGIARTI000023023835, seule rédaction, du 11 novembre 2010 au 28 février 2025 | « Par dérogation [...] fixé à soixante-cinq ans » et « est applicable dans tous les régimes obligatoires de retraite auxquels s'appliquent les dispositions de l'article L. 351-8 » : **conforme** |
| Loi n° 2010-1330, article 28 | LEGIARTI000023023851 (1er juillet-23 décembre 2011), LEGIARTI000025014566 (depuis) ; le mot à mot (`--diff`) ne change que le renvoi d'application, le I (soixante-sept ans dès 1956, puis dès 1955) et le II | III cité en entier, mot pour mot, identique dans les deux rédactions ; I, « nés à compter du 1er janvier 1955, la limite d'âge est fixée à soixante-sept ans » dans la rédaction de 2020 : **conforme** |
| R. 26 ter du code des pensions | LEGIARTI000024111781, seule rédaction, depuis le 3 juin 2011 ; inséré par le décret n° 2011-620, article 3 (JORFARTI000024110126, « il est inséré un article R. 26 ter ») | les quatre fragments, mot pour mot ; huit trimestres avant, huit d'activité préalable : **conforme** |
| Décret n° 2003-1306, article 65-3 ; décret n° 2004-1056, article 50-3 ; décret n° 2011-620, article 10 | LEGIARTI000024113270, LEGIARTI000024113274 ; JORFARTI000024110234 | la même règle, aux mêmes générations ; le renvoi à R. 26 ter, mot pour mot, ajouté par l'article 10 : **conforme** |
| L. 13, L. 14, L. 24 du code des pensions | LEGIARTI000028498258 (2014-2023), LEGIARTI000037200740 (15 juillet 2018-1er septembre 2023), LEGIARTI000028498845 (2014-2023) | 75 % au plus ; « un coefficient de minoration de 1,25 % par trimestre s'applique au montant de la pension », « Le nombre de trimestres correspondant est arrondi à l'entier supérieur », le plus petit des deux nombres ; L. 24, I, 1°, l'âge de L. 161-17-2 : **conforme** |
| Loi n° 2003-775, article 66, III | LEGIARTI000006758610, seule rédaction | la colonne « Année au cours de laquelle sont réunies les conditions mentionnées au I et au II de l'article L. 24 », et la ligne de 2017 : « 1,25 % », « Limite d'âge moins 3 trimestres » : **conforme** |
| L. 161-17-2 | LEGIARTI000025014605 (23 décembre 2011-1er septembre 2023) | soixante-deux ans dès 1955 ; quatre mois par génération en 1951, cinq de 1952 à 1954 : 61 ans et 2 mois en 1953, 61 ans et 7 mois en 1954 ; avec cinq ans, les âges de génération de la note : **conforme** |
| L. 382-27 | LEGIARTI000019959668 (19 décembre 2008-1er septembre 2023) | « reçoivent une pension de vieillesse dans les conditions définies aux articles L. 351-1 à L. 351-1-3 » et « L. 351-8 à L. 351-13 » : **conforme** |
| Décret n° 2006-1325, article 2 | LEGIARTI000023397816, pensions dès le 1er juillet 2011 | II, « peut également être allouée à partir de l'âge mentionné au I » et « le coefficient de minoration fixé au 2° du I et au II de l'article R. 351-27 » : **conforme** |
| R. 351-27 | LEGIARTI000024113020 (3 juin 2011-1er septembre 2023) | I, 2°, « leur soixante-cinquième anniversaire, s'ils remplissent les conditions prévues au 1° bis ou 1° ter de l'article L. 351-8 ou au III ou IV de l'article 20 » : **conforme** |
| Décret n° 73-937, article 3 | LEGIARTI000006765819 (19 février 2004-7 octobre 2012), LEGIARTI000026474703 (7 octobre 2012-1er septembre 2023) | avant 2012, le « soixante-cinquième anniversaire » de tous ; depuis, le II cité mot pour mot, « 1,25 % pour l'assuré né après 1952 » : **conforme** |
| Règlement du RCI, arrêté du 9 février 2012, article 12 | LEGIARTI000054891893 (1er janvier 2013-26 juin 2024) ; LEGIARTI000054896398 (26 juin 2024-1er janvier 2027) | « sans aucun abattement : a) A partir de l'âge fixé à l'article L. 161-17-2 [...] et à partir de la première liquidation à taux plein de la retraite de base servie par le régime social des indépendants », mot pour mot : **conforme** |
| R. 723-38, R. 653-2 ; décret n° 2011-620, article 4, 14° et 16° | LEGIARTI000024113046 (3 juin 2011-8 juillet 2019), LEGIARTI000038787833 (le seul jour du 8 juillet 2019), LEGIARTI000038770285 (8 juillet 2019-1er septembre 2023) ; JORFARTI000024110134 | la citation de R. 653-2, mot pour mot ; les 14° et 16° ajoutent la règle à R. 643-7 et R. 723-38 : **conforme** |
| Loi n° 2025-199, article 87 | JORFARTI000051269910 | le VIII n'a que A et B ; le 19° du II complète L. 351-8 « par un 6° » ; le A : « les 3° à 6°, 10°, 12°, 14°, 18°, 19° et 23° du II [...] s'appliquent aux pensions prenant effet à compter du 1er janvier 2026 » : **conforme** |
| Circulaire Cnav n° 2014-64, point 2.3.2.1 | PDF, sha256 f6717a0f61473e4ea56976868f97b2dbb8068ba22d57befbaf2c0e120cdcaccb, identique | « [...] accidents du travail/maladies professionnelles pour incapacité temporaire ou permanente au moins égale à 66 % », sous le titre 2.3.2.1 : **conforme** |

Le script a trouvé 29 fragments dans leur texte, chacun dans la source que l'approximation
cite ; les 3 autres (l'exposant de « 1er janvier 1957 », deux cellules de la table de
l'article 84) ont été lus sur la page.

## 3. Les chiffres, refaits à la main

| Cas | Calcul | Fiche, test, note |
|---|---|---|
| Arrco, 2018 | née le 15 mars 1953 : 66 ans et 2 mois au 15 mai 2019 ; du 1er avril 2018, 13 mois et 14 jours, 4,49 trimestres, 5 au trimestre supérieur : « moins 1 an 1 trimestre », 0,95 ; le droit, 1 | 0,95, 5 % ✓ |
| Agirc-Arrco, 2019 | née le 15 septembre 1954 : 66 ans et 7 mois au 15 avril 2021 ; du 1er octobre 2019, 18 mois et 14 jours, 6,15, 7 : « moins 1 an 3 trimestres », 0,93 | 0,93, 7 % ✓ |
| Agirc-Arrco, 2020 | née le 15 mars 1955 : 67 ans au 15 mars 2022 ; du 1er avril 2020, 23 mois et 14 jours, 7,82, 8 : « moins 2 ans », 0,92 | 0,92, 8 % ✓ |
| Fonctionnaire née le 15 mars 1955 | 62 ans en 2017, ligne de 2017 : limite d'âge 67 ans moins 3 trimestres, 66 ans et 3 mois ; de 65 ans, 15 mois, 5 trimestres (de la date d'effet, 14 mois et demi, 5 à l'entier supérieur) ; 75 % × (1 − 5 × 1,25 %) = 70,3125 % ; le droit, si l'interruption est un congé ou une disponibilité de R. 13 : 75 % | 70,3125 %, 6,25 % de la pension ✓ |
| CAVIMAC, née le 15 mars 1953 | 5 trimestres ; 50 % × 0,9375 = 46,875 % ; 16 643,72 × 50 % × 73/165 = 3 681,79 € et 16 643,72 × 46,875 % × 73/165 = 3 451,68 € ; 4 635,65 × 11/165 = 309,04 € et × 0,9375 = 289,73 € ; écart total 6,25 % | ✓ |
| Points d'avant 1973 | 5 trimestres à 1,25 % (né après 1952) : 0,9375 ; le droit, compté du 65e anniversaire, 0 trimestre : 1 | 6,25 % de cette part ✓ |
| RCI | le modèle 0,95 ; le droit, article 12, a), 1 | 5 % ✓ |

## 4. Aucun calcul changé

- Le commit touche six fichiers : la fiche, le test, la limite, sa note, son entrée de
  journal et le cliquet des textes (9 355 à 9 350). Rien sous `src/`, `moteur/` ni
  `tests/temoins/` ; `moteur/donnees.json` est identique à l'octet avant et après lui.
- Dans la fiche, il ne change que des champs que nul calcul ne lit
  (`CHAMPS_DOCUMENTAIRES`, `src/retraite_notionnelle/memoire.py:216`) et une citation
  d'une lecture ; ce que lit le moteur, `existe`, `regimes` et `parents_de_trois_enfants`
  (`src/retraite_notionnelle/droit/categories.py:232-235`), n'a pas bougé.
- Ce que sert le portage, sur le paquet de main refait par GitHub (7c45287), à l'artisane
  et à la commerçante de `REQUETE` parties à 65 ans : régime général « taux 50.000% » ;
  « coefficient d'anticipation 0.9375 » aux points d'avant 1973 ; « 0.9500 » au RCI, au
  RCO des artisans et au NRIC — ce que la fiche et la note disent.

## 5. Les tests

- `tests/test_taux_plein_a_soixante_cinq_ans.py` et `tests/test_regle_de_chacun.py` :
  15 passés ; sous `PRESOMPTIONS_DECALEES=1`, 15 passés.
- `python -m pytest -m rapide`, sur main à 7c45287 et le paquet que GitHub y a refait :
  4 242 passés, 6 ignorés, aucun échec — les échecs que R-M4 (24) et M4-bis (28) attribuaient
  au paquet périmé ont disparu avec lui.
- `PRESOMPTIONS_DECALEES=1 python -m pytest -m rapide` : 4 044 passés, 204 ignorés, aucun
  échec.

## 6. Ce que le texte ne tranche pas, et trois remarques faibles

*Le point ouvert est déclaré.* La fiche dit, dans l'approximation de l'Agirc-Arrco et dans
`a_relire`, que les textes lus ne tranchent pas de quel âge l'Agirc-Arrco compte, depuis
2019, le coefficient de ces parents partis avant soixante-cinq ans sans le taux plein du
régime de base : « cet âge » de l'article 84, 2, est celui du 1° de L. 351-8, que le IV de
l'article 20 fixe pour eux à soixante-cinq ans. **Conforme.** La circulaire Agirc-Arrco
2020-02-DRJ du 20 janvier 2020, « Réglementation applicable aux individus »
(https://www.agirc-arrco.fr/wp-content/uploads/2021/10/2020-02-DRJ_Regime_Agirc-Arrco_Reglementation_applicable_aux_individus.pdf,
téléchargée le 3 novembre 2026, sha256
524779881a0e4e377382f4b3d8ab9cf0ebd4aa21fe2eca841dd523491f4806ae), ne le tranche pas
davantage. Sa fiche 3, I.1.1 : « le participant peut bénéficier de sa pension au titre du
régime Agirc-Arrco, sans abattement, dès lors qu'il a atteint l'âge de 67 ans, âge visé au
1° de l'article L. 351-8 du code de la sécurité sociale pour les participants nés à compter
du 1er janvier 1955 » ; I.1.2.1 : « au plus tôt 10 ans avant l'âge visé au 1° de l'article
L. 351-8 du code de la sécurité sociale, soit au plus tôt à 57 ans (pour les participants
nés à compter du 1er janvier 1955) ». Elle ne nomme ni la dérogation du IV de l'article 20,
ni ces parents ; sa règle générale, sans réserve, s'accorde avec ce que sert le modèle,
sans rien dire de leur cas. Sa fiche 3, I.1.2.2, confirme en revanche l'article 84, 3 : le
taux plein du régime de base « peut notamment avoir pour origine » la durée, les « 1° bis
à 5° de l'article L. 351-8 » ou les carrières longues — une liste ouverte.

*Remarques, sans effet sur un calcul ni un chiffre :*

- *L'article 98 nomme ces parents.* Son dernier tiret exclut des coefficients de
  solidarité « les participants visés au III et IV de l'article 20 de la loi n° 2010-1330
  du 9 novembre 2010 ainsi qu'au 1° bis de l'article L. 351-8 du code de la sécurité
  sociale qui bénéficient du taux plein dans le régime de base dès 65 ans », et sa note 1
  précise : « d'assurés nés entre le 1er juillet 1951 et le 31 décembre 1955 parents d'au
  moins trois enfants » (page imprimée 59). Nés avant 1957, ils n'y sont de toute façon pas soumis :
  la fiche dit vrai, mais pourrait citer ce texte, qui montre que l'accord de 2017 les
  tient pour au taux plein dès soixante-cinq ans.
- *Les tranches A et B.* L'accord de 2011 ne les sert « sans abattement » que « sur les
  tranches A et B des rémunérations » ; la fiche le cite, mais son effet, son `a_relire` et
  la limite disent « sans coefficient » sans réserve. Le moteur garde déjà, pour tout taux
  plein, le coefficient de l'âge aux points de l'Agirc de la tranche C d'avant 2016
  (`src/retraite_notionnelle/droit/liquider.py:987-996`) : le calcul à venir devra le
  garder pour ces parents. Les cas chiffrés n'ont pas de tranche C.
- *La rédaction de référence de l'accord de 2011.* Son article 1er s'applique « sur la
  base de la rédaction en vigueur, à la date du présent accord, de l'ensemble des
  dispositions législatives susvisées » : la fiche ne le cite pas. Au 18 mars 2011,
  L. 351-8 était encore dans sa rédaction de 2003 (LEGIARTI000006742633, jusqu'au 1er
  juillet 2011), sans 1° bis ni 1° ter ; la clause vise donc les dispositions telles que la
  loi n° 2010-1330 les écrit, dont le IV de l'article 20, publié depuis le 11 novembre
  2010. Elle ne change pas la conclusion : l'article nomme lui-même ces parents.

## Ce qui reste, pour le propriétaire

Rien à corriger dans le travail de M4-bis. À la session qui servira les complémentaires à
ces parents : garder le coefficient de la tranche C d'avant 2016 ; citer l'article 98 et sa
note ; pour le point ouvert, la circulaire 2020-02-DRJ ne suffit pas — la question se pose
à l'Agirc-Arrco, ou dans une circulaire que cette relecture n'a pas trouvée.
