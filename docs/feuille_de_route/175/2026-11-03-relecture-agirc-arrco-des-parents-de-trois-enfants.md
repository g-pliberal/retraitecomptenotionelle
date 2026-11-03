# Relecture de l'Agirc-Arrco des parents de trois enfants (file M3)

File R-M3b, le 3 novembre 2026 : relecture indépendante du commit 16663e5 (session M3,
note `2026-11-03-agirc-arrco-des-parents-de-trois-enfants.md`), qui sert sans coefficient
d'anticipation, dans les deux moteurs, l'Agirc et l'Arrco, puis l'Agirc-Arrco, du parent de
trois enfants né de juillet 1951 à 1955 au taux plein du régime général à soixante-cinq ans.
Rien n'a été repris de la session ni de mémoire : les huit documents de l'Agirc-Arrco, du
COR et du guide n° 9 téléchargés le jour, leur empreinte recalculée ; l'index LEGI de la
DILA récupéré dans la session (à jour au 2 novembre 2026) ; chaque fragment cité entre « »
cherché par un script dans le texte de sa source, apostrophes et espaces ramenés à une
forme, et ceux que l'extraction disjoint (un renvoi de note, une césure) lus sur la page ;
chaque valeur attendue refaite à la main ; les tests lancés sur le dernier `main`
(e17c8f7). Rien n'a été modifié : ni règle, ni donnée, ni test, ni fiche.

**Verdict : la règle est conforme ; un écart moyen, six faibles.** Chaque condition et
chaque borne de date sont dans les textes ; chaque citation est exacte, mot pour mot ;
chaque valeur des tests se refait au centime ; les deux moteurs la rendent, tests verts,
sous `PRESOMPTIONS_DECALEES=1` aussi ; le paquet se refait à l'octet. L'écart moyen : la
majoration pour enfants reversée depuis 2019, que M3 dit « ni court ni tranché(e) », la
circulaire 2020-02-DRJ, qu'il cite ailleurs, la tranche (point 6). Les six faibles, sans
effet sur un calcul de la règle, au point 8.

## 1. Les textes, à la version en vigueur

| Texte | Ouvert | Constat |
|---|---|---|
| Loi n° 2010-1330, article 20, IV | LEGIARTI000023023835, du 11 novembre 2010 au 28 février 2025, seule rédaction dans l'index ; son nota : l'article 118, II, « Les dispositions de l'article 20 sont applicables aux pensions prenant effet à compter du 1er juillet 2011 » | la phrase citée, mot pour mot ; les trois conditions (« au moins trois enfants », l'interruption ou la réduction « suivant la naissance ou l'adoption d'au moins un de ces enfants », les trimestres validés avant) : **conforme**. La rédaction prend fin le 28 février 2025 : sans effet, le dernier de ces parents ayant 67 ans, l'âge de sa génération, en 2022 |
| Accord du 18 mars 2011, articles 1er et 3, recueil « Accords nationaux des partenaires sociaux », https://www.agirc-arrco.fr/storage/2021/11/liste_accords_paritaires_Agirc_Arrco.pdf | sha256 0186b6b165ad2a5f5f561deb969c6a35c661dc2e1fedbfcdcaa24801f51104c1, identique | les huit fragments, mot pour mot (« loi n° 2010-1330 », que l'extraction soude, lu sur la page) ; l'article 1er est aux pages imprimées 147 et 148, l'article 3 à la page 149, non 148 (point 8, e) : **conforme** |
| Accord du 30 octobre 2015, article 12 et sa note 7, même recueil | même empreinte | « assurés nés entre le 1er juillet 1951 et le 31 décembre 1955 parents d'au moins trois enfants », mot pour mot ; le recueil ne nomme ces parents qu'ici et à l'article 1er de 2011 (« 3 enfants », « 1951 » cherchés dans tout le texte) : **conforme** |
| Convention du 14 mars 1947, annexe I, article 6, et annexe V, « Textes mis à jour au 1er janvier 2018 », https://www.agirc-arrco.fr/storage/2021/11/CCN_14mars1947-1.pdf | sha256 38966c272726dd11abbcc5ffa18ffb67d2731caa86ca4ce3aa94d0169568ce78, identique | article 2 ter, le préambule, la note (1), mot pour mot ; la table de l'article 6, § 1er : « moins 1 an 1 trimestre » 0,95, « moins 1 an » 0,96, « moins 2 ans 1 trimestre » 0,91, lus sur la page ; « Mise à jour au 1 janvier 2018 » n'y est pas, « Textes mis à jour au 1er janvier 2018 » si : **conforme** |
| Accord du 8 décembre 1961, annexe A, article 18, et annexe E, même mise à jour, https://www.agirc-arrco.fr/storage/2021/11/Accord_8dec1961-1.pdf | sha256 5af24910e87017e7f50ce4db12f5329edf3bb286e1c69749de19a559419d9e03, identique | article 2 ter, mot pour mot celui de l'annexe V ; article 6 ; la note (1), « pour toute liquidation prenant effet à compter du 1er juillet 2011 » : **conforme** |
| Accord du 17 novembre 2017, « applicable au 1er janvier 2019 », articles 84, 98, 102 et 109, https://www.agirc-arrco.fr/storage/2024/09/201809dc_ANI_du_17_novembre_2017.pdf | sha256 b8af8df7372e4f897c1ca0c4fd9bf4baaa5b706ec4737b8e51b593c5a2a4fccb, identique | 84, 3 ; 98, le dernier tiret (son renvoi « 1 », que l'extraction insère, lu sur la page) et sa note 1 ; 109, ses trois phrases citées : mot pour mot ; la table de 84, 2 : 0,95, 0,93, 0,92, 0,91, 0,96 aux lignes que M3 nomme : **conforme**. L'article 102 ne dit pas que la tranche C garde son coefficient (point 8, a) |
| Circulaire Agirc-Arrco 2020-02-DRJ du 20 janvier 2020, https://www.agirc-arrco.fr/wp-content/uploads/2021/10/2020-02-DRJ_Regime_Agirc-Arrco_Reglementation_applicable_aux_individus.pdf | sha256 524779881a0e4e377382f4b3d8ab9cf0ebd4aa21fe2eca841dd523491f4806ae, identique | fiche 3, I.1.1 et I.1.2.2 ; fiche 4, III.3.2.1, « à 65 ans » l'aidant de l'enfant handicapé et l'aidant familial ; elle ne nomme pas ces parents : **conforme**. Sa fiche 6, I.1.2.2, tranche la majoration reversée (point 6) |
| Guide des salariés n° 9, « Majorations pour enfants », édition de mars 2017, https://www.carcept-prev.fr/sites/carcept/files/media/documents/2018/05/Majorations-pour-enfants.pdf | sha256 9dfcdaf5c2d655737ce3509a28fbebe7143322006f62a3abfe23f361972743b2, identique | « Lorsque la retraite a été minorée, il n'est pas tenu compte du coefficient de minoration pour le calcul de la majoration pour enfants » (page marquée « P. 12 ⁄ 13 », la 13e du fichier) ; « le régime Agirc en tient compte » (« 2. Retraite minorée ») : **conforme** |
| COR, séance du 25 mai 2011, document n° 7, https://www.cor-retraites.fr/sites/default/files/2019-06/doc-1530.pdf | sha256 952c1af12ace77881e18b58599bd900044fbfc0880950c0964f8308197029a00, identique | « application d'un pourcentage de service de 80% (01/03/94) à la majoration suivante : 10% pour 3 enfants », « 30% pour 7 enfants et + », lus sur la page (trois colonnes) : **conforme** |
| Accord Agirc du 9 février 1994, article 2, même recueil | même empreinte | la citation de la fiche, mot pour mot ; elle est à la page imprimée 16, non 15 (point 8, e) : **conforme** au texte |
| Circulaire Agirc-Arrco 2025-15-DT, https://www.agirc-arrco.fr/storage/CirculaireAgircArrco2025-15dt.pdf | sha256 2e34ce291edcfa5e9d21bf0b80e7c30d8889f7342ee8b5dae4463801ad04b288, identique | « Le montant du plafond des majorations pour enfants nés ou élevés reste fixé à 2 367,48 € », mot pour mot : **conforme** |

Le site réglementaire de la caisse (reglementation.agirc-arrco.fr) refuse toujours la
connexion d'ici, son certificat ne se vérifiant pas : ce que M3 en dit est exact.

## 2. Chaque condition, chaque borne

- *La génération, les enfants, l'interruption* : le IV, « nés entre le 1er juillet 1951 et
  le 31 décembre 1955 inclus », « au moins trois enfants », l'interruption ou la réduction
  après une naissance ; le moteur les lit par `categories.age_du_parent_de_trois_enfants`
  (la fiche `taux_plein_a_soixante_cinq_ans`, que R-M4 et R-M4-bis ont relue), et n'exonère
  que si cet âge est atteint à la liquidation. **Conforme.**
- *Le taux plein du régime général à soixante-cinq ans* : l'accord de 2011, article 1er,
  « en application des III et IV de l'article 20 » ; les annexes V et E, article 2 ter, « à
  l'âge de 65 ans » ; l'accord de 2017, article 84, 3, « à l'âge auquel il a obtenu la
  pension d'assurance vieillesse du régime général [...] à taux plein », et l'article 98,
  note 1, qui nomme ces parents. Le moteur : `age_liquidation >= 65` (les deux jumeaux,
  lignes identiques). **Conforme.**
- *Les bornes de date* : de 2011 à 2018, « pour toute liquidation [...] prenant effet à
  compter du 1er juillet 2011 et jusqu'au 31 décembre 2018 au plus tard » (accord de 2011,
  article 1er) ; depuis le 1er janvier 2019, l'accord de 2017. Le motif est dans les quatre
  versions de la fiche `coefficients_anticipation_agirc_arrco` qui couvrent le 1er juillet
  2011 à aujourd'hui (`accord_du_18_mars_2011`, `accord_du_30_octobre_2015`,
  `regime_unifie`, `avenant_15`). Le premier de ces parents a soixante-cinq ans en juillet
  2016 : la version de 2011 à 2015 ne peut pas jouer, sans dommage. **Conforme.**
- *La tranche C d'avant 2016 garde son coefficient* : de 2011 à 2015, l'accord de 2011 n'exonère
  que « sur les tranches A et B des rémunérations » ; de 2016 à 2018, la convention de 1947,
  annexe I, article 6, § 3 a), le dit en toutes lettres : « Ce coefficient correspond à
  l'application des coefficients d'anticipation visés au § 1er du présent article sur les
  droits du participant constitués sur la tranche C jusqu'au 31 décembre 2015 et des
  dispositions de l'annexe V [...] pour les droits constitués sur la même tranche depuis le
  1er janvier 2016 », avec le préambule de l'annexe V ; depuis 2019, l'article 102 ne le dit
  pas, il le suppose (le report « sans abattement » de ces points), et c'est la circulaire
  2020-02-DRJ qui le dit, fiche 4, III.1 : sont liquidés « avec application d'un coefficient
  d'anticipation en fonction de l'âge [...] y compris les droits constitués sur la tranche C
  des salaires avant 2016 au titre de l'ancien régime Agirc liquidés avant l'âge de 67 ans ».
  **Conforme quant à la règle** ; la référence de M3 pour 2019 est à reprendre (point 8, a).
- *L'Arrco des cultes n'est pas exonéré* : l'accord de 2011 et l'article 84, 3 ne nomment
  que la pension « du régime général ou du régime des assurances sociales agricoles » ; le
  ministre du culte a la sienne de la CAVIMAC ; aucun des textes lus ne parle des cultes à
  ce sujet (« culte » cherché dans l'accord de 2017, la circulaire et l'accord de 1961).
  Le choix repose sur cette lecture, et il est déclaré comme non tranché (fiche
  `taux_plein_a_soixante_cinq_ans`, son approximation de l'Agirc-Arrco). **Conforme,
  déclaré** ; une remarque au point 8, f.

## 3. Les valeurs attendues, refaites à la main

Les valeurs de service lues dans `data/reference/regimes/valeurs_service_datees.csv` :
Arrco 1,2513 € du 1er novembre 2016 au 31 octobre 2018 ; Agirc 0,4352 € à la même date ;
Agirc-Arrco 1,2588 € au 1er janvier 2019, 1,2714 € au 1er novembre 2019. Les âges de la
génération, ceux que la caisse a servis (lecture divergente déclarée à la fiche des
coefficients) : 66 ans et 2 mois pour 1953, 66 ans et 7 mois pour 1954, 67 ans pour 1955.
Les points sont ceux que la formule affiche, comme chez M3.

| Cas | Refait | Constat |
|---|---|---|
| Arrco, née le 15 mars 1953, effet 1er avril 2018 | jusqu'au 15 mai 2019 : 13 mois 14 jours, 4,49 trimestres, 5, 0,95 ; 2 791,14 × 1,2513 = 3 492,55 €, × 0,95 = 3 317,93 € (3 317,92 au moteur, points non arrondis) ; 1/0,95 − 1 = 5,26 % | **conforme** |
| Agirc-Arrco, née le 15 septembre 1954, effet 1er octobre 2019 | jusqu'au 15 avril 2021 : 18 mois 14 jours, 6,16 trimestres (6,15 chez M3, selon le compte des jours ; 7 dans les deux cas), 0,93 ; 2 842,73 × 1,2588 = 3 578,43 € ; 96,95 × 1,2588 = 122,04 € ; 7,53 % | **conforme** |
| Agirc-Arrco, née le 15 mars 1955, effet 1er avril 2020 | jusqu'au 15 mars 2022 : 23 mois 14 jours, 7,82, 8, 0,92 ; 2 528,23 × 1,2714 = 3 214,39 € ; 159,78 × 1,2714 = 203,14 € ; 8,70 % | **conforme** |
| Cadre à huit fois le salaire moyen, effet 1er avril 2018 | 1 − 0,05 × 54 284,66 / 129 874,12 = 0,979101 ; 129 874,12 × 0,4352 = 56 521,22 €, × 0,95 = 53 695,16 €, × 0,979101 = 55 339,98 € ; +1 644,82 €, +3,06 % ; 41,8 % des points de la tranche C d'avant 2016 ; Arrco 3 110,48 × 1,2513 = 3 892,14 € | **conforme** |
| Deux enfants, effet 1er avril 2018 | ni le IV (trois enfants), ni l'exonération : 0,95 | **conforme** |
| À 64 ans, effet 1er avril 2017 | jusqu'au 15 mai 2019 : 25 mois 14 jours, 8,49, 9, « moins 2 ans 1 trimestre », 0,91 ; compté de 65 ans (15 mars 2018) : 11 mois 14 jours, 3,82, 4, « moins 1 an », 0,96 ; 2 660,55 × 1,2513 = 3 329,15 €, × 0,91 = 3 029,52 €, × 0,96 = 3 195,98 € | **conforme** |

L'effet que M3 en tire en euros ne l'est pas tout à fait : « 174,63 € à 257,15 € par an »
ne compte, pour les cas de 2019 et de 2020, que la ligne de l'Arrco ; la complémentaire non
cadre gagne 259,04 € (250,49 + 8,55) en 2019 et 273,40 € (257,15 + 16,25) en 2020
(point 8, c).

## 4. Les deux moteurs

Sur e17c8f7, le dernier `main` : les trois fichiers de tests de M3,
`test_taux_plein_a_soixante_cinq_ans.py`, `test_exonerations_agirc_arrco.py`,
`test_agirc_arrco_au_droit.py`, 45 passés, et 44 passés et 1 sauté sous
`PRESOMPTIONS_DECALEES=1` (le portage lit ses présomptions dans le paquet) ;
`python -m pytest -m rapide` : 4 317 passés, 8 sautés ; sous `PRESOMPTIONS_DECALEES=1` :
4 119 passés, 206 sautés ; `-m site` : 36 passés ; les confrontations légères (oracle,
Destinie, estimation officielle, vérification) : 423 passés, 1 sauté ;
`tests/test_pont.py -k refait` : 2 passés. Les cas de M3 passent par `servi_et_refait`,
qui fait calculer le portage et refaire chaque cas au jumeau Python ; le code ajouté,
`parentAuTauxPleinDuRegimeGeneral` et `parent_au_taux_plein_du_regime_general`, est le
même, ligne pour ligne. Les trois cas sans abattement étaient, avant 16663e5, des écarts
déclarés que le test affirmait à 0,95, 0,93 et 0,92 : le test nouveau dit donc bien ce
qui a changé. **Conforme.**

## 5. Les témoins

Aucun des 930 témoins de simulation ne bouge : c'est exact, mais pas pour la raison que
M3 donne (« Aucun témoin n'est parent de trois enfants né de 1951 à 1955 avec une
naissance déclarée »). Un relevé ciblé de `tests/temoins/simulations.json` (la requête de
chaque témoin, puis les seules pensions de l'Agirc-Arrco de ceux qu'elle retient) en
trouve cinq, nés en 1954 ou 1955, de trois ou huit enfants aux naissances déclarées :
`parents_trois_enfants_ancien_calcul_decote`, `plafond_l18_huit_enfants`,
`plafond_l18_huit_enfants_cnracl`, `plafond_l18_huit_enfants_surcote`,
`plafond_l18_surcote_2021`. Tous sont fonctionnaires, sans aucune pension de l'Agirc-Arrco
(361 témoins en ont une) ; trois partent avant soixante-cinq ans, deux à soixante-sept.
Aucun ne peut bouger (point 8, b). Les six lignes de `tests/temoins/pages.json` que le
commit change (441 779 → 441 807 valeurs, durées d'échelon 8 626 → 8 639 et 14 506 →
14 521) tiennent au paquet d'un travail antérieur, comme M3 le dit : 28 = 13 + 15.

## 6. Ce que les textes ne tranchent pas, et l'écart moyen

- *L'âge d'où se compte le coefficient avant soixante-cinq ans* : avant 2019, l'âge figé au
  18 mars 2011 et l'« à l'âge de 65 ans » de l'article 2 ter ; depuis 2019, l'article 84, 1
  et 2, renvoie au 1° de L. 351-8, que le IV fixe pour eux à soixante-cinq ans, quand la
  circulaire 2020-02-DRJ dit « 67 ans [...] pour les participants nés à compter du 1er
  janvier 1955 » sans nommer la dérogation. Je n'ai trouvé, dans les textes ouverts, rien
  qui le tranche. Déclaré à la fiche `taux_plein_a_soixante_cinq_ans`, chiffré (0,91 ou
  0,96), fixé par `test_avant_soixante_cinq_ans_l_age_de_la_generation_reste`.
  **Conforme, déclaré.** La lecture littérale de l'article 84 penche pour soixante-cinq ans
  depuis 2019 ; M3 le dit.
- *La tranche C d'avant 2016 au-delà de soixante-cinq ans* : depuis 2019, le report « sans
  abattement, à l'âge mentionné au 1° de l'article L. 351-8 » (article 102) les servirait
  sans coefficient dès soixante-cinq ans si cet âge est celui du IV ; déclaré de même.
  **Conforme, déclaré.**
- *L'Arrco des cultes* : déclaré (point 2). **Conforme.**
- **Écart moyen : la majoration reversée depuis 2019.** M3 écrit à la fiche
  `majoration_enfants_agirc_arrco` que l'article 109 « ne dit pas si la majoration
  reversée se calcule sans le coefficient » et que « aucun texte lu ne la tranche pour ce
  défunt », d'où un effet au conditionnel (« si la caisse reverse cette majoration sans le
  coefficient »). La circulaire 2020-02-DRJ, celle que M3 a téléchargée et cite, la
  tranche, fiche 6, « Droits de réversion », I.1.2.2, « Majorations pour enfants », 1., à
  la page 6 de la fiche (79e du fichier) : « Les majorations pour enfants nés ou élevés
  applicables aux droits du participant décédé sont réversibles au taux de 100 %. » ; « Les
  majorations sont calculées sur les droits de base du participant décédé, sans tenir
  compte d'un éventuel coefficient d'anticipation dont les droits directs ont pu être
  affectés. » Le texte ne distingue pas la date de liquidation du défunt. Le modèle, qui
  reverse la majoration servie au défunt, coefficient compris pour une pension de l'Agirc
  de 2012 à 2018, s'écarte donc de la règle écrite de la caisse, pour un décès depuis 2019.
  L'écart reste déclaré, et son effet ne porte que sur la majoration reversée (5 % de
  celle-ci à 0,95, 22 % à 0,78, selon la fiche) ; mais la fiche dit faux l'état des
  sources. À reprendre : la citation à la fiche, l'écart dit
  comme tel, et la correction, le test d'abord (cas posé à la main depuis ce texte). Ce
  n'est pas une règle du parent de trois enfants, et R-M3 l'avait signalé pour le guide
  n° 9 : il n'y a pas d'urgence de calcul.

## 7. Le paquet

Sur 16663e5, puis sur e17c8f7, le dernier `main` : `python scripts/construire_donnees.py`
ne change rien (`git status` vide) ; aucune copie à remettre. **Conforme.**

## 8. Les écarts, par gravité

**Moyen**

- La majoration reversée depuis 2019 : la circulaire 2020-02-DRJ, fiche 6, I.1.2.2, 1.,
  tranche ce que la fiche `majoration_enfants_agirc_arrco` dit non tranché (point 6).

**Faibles**, sans effet sur un calcul de la règle :

- *a) La tranche C depuis 2019* : « 102 : la tranche C d'avant 2016 garde son coefficient »
  (note de M3, section 1) ; l'article 102 ne l'écrit pas. Les textes qui l'écrivent : la
  convention de 1947, annexe I, article 6, § 3 a), pour 2016 à 2018 ; la circulaire
  2020-02-DRJ, fiche 4, III.1, depuis 2019 (point 2). La même attribution est dans la fiche
  `taux_plein_a_soixante_cinq_ans` (« annexe V, préambule ; accord de 2017, article 102 »).
- *b) La raison donnée pour les témoins* : cinq témoins sont des parents de trois enfants
  nés en 1954 ou 1955 aux naissances déclarées ; aucun n'a de pension de l'Agirc-Arrco
  (point 5). La conclusion tient, la phrase de la section 6 de M3 est fausse.
- *c) L'effet en euros* : la borne haute, 257,15 €, n'est que la ligne de l'Arrco du cas de
  2020 ; sa complémentaire gagne 273,40 € (point 3).
- *d) L'arrondi de l'effet* : « 5 à 8 % » (fiche des coefficients, son `effet`) et « de 5 %
  à 8 % de plus » (fiche `taux_plein_a_soixante_cinq_ans`) pour 5,26 % à 8,70 % : 8,70 %
  s'arrondit à 9 %.
- *e) Deux pages* : l'article 3 de l'accord de 2011 est à la page imprimée 149 du recueil,
  non 148 (note de M3, section 1) ; l'article 2 de l'accord Agirc de 1994 à la page 16, non
  15 (note de M3, section 5, et fiche `majoration_enfants_agirc_arrco`, `a_relire`). Les
  numéros sont au pied de page ; vérifiés page par page.
- *f) L'Arrco des cultes* : les autres motifs de la fiche des coefficients (`regimes: null`)
  exonèrent l'Arrco des cultes sur la catégorie du régime général ; le motif nouveau
  l'exclut. Les deux se défendent ; la déclaration gagnerait à dire cette asymétrie.

Sources ouvertes : listées au point 1 ; et `data/reference/regimes/valeurs_service_datees.csv`,
`tests/temoins/simulations.json` (requêtes et pensions, par un relevé ciblé),
`tests/temoins/exemples_officiels.yaml` (`agirc_arrco_tranche_c_63_ans_11_mois`), le code
des deux jumeaux.
