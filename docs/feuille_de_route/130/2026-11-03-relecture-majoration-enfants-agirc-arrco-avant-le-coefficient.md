# Relecture de la majoration pour enfants de l'Agirc-Arrco avant le coefficient (file M3)

File R-M3, le 3 novembre 2026 : relecture indépendante des commits 488c30a et 2d15a5b
(session M3, note `2026-11-03-majoration-enfants-agirc-arrco-avant-le-coefficient.md`),
entrés sur `main` avec le paquet refait par cd8db07. Chaque texte a été téléchargé et lu
ici, page utile par page utile, sans rien reprendre de la session ni de mémoire. Rien n'a
été modifié : ni règle, ni donnée, ni test, ni fiche ; le paquet refait pour l'essai l'a été
hors commit, puis remis en l'état.

**Verdict : conforme.** Les citations sont exactes mot pour mot, aux puces près ; les neuf
cas et le plafond se refont au centime, sur des valeurs de point et des coefficients que
les textes donnent ; les deux moteurs les rendent ; ce que les textes ne tranchent pas est
déclaré. **Écarts**, tous faibles : la note dit que le modèle « ne sert pas » le
pourcentage de service de l'accord Agirc de 1994, quand son barème de 8 à 24 % l'incorpore
déjà, d'après le COR (point 8) — une lecture qui, suivie, le ferait compter deux fois ; le
guide n° 9 dit autre chose pour la réversion, que la note ne relève pas (point 4) ; la
circulaire 2025-15-DT n'a pas d'adresse dans la fiche (point 1). Deux vérifications
restent impossibles d'ici : l'avenant n° 16 du 22 novembre 2023, et le site réglementaire de
la caisse (point 10).

## 1. Les sources, et leurs empreintes

Téléchargées le 3 novembre 2026 ; chaque empreinte sha256 est celle que la fiche porte,
sauf les trois dernières, que la fiche ne cite pas.

| Texte | Adresse | sha256 |
|---|---|---|
| Circulaire Agirc-Arrco 2020-02-DRJ du 20 janvier 2020, 88 pages | `agirc-arrco.fr/wp-content/uploads/2021/10/2020-02-DRJ_Regime_Agirc-Arrco_Reglementation_applicable_aux_individus.pdf` | 52477988…06ae, identique |
| Guide des salariés n° 9, « Majorations pour enfants », 20 pages | `carcept-prev.fr/sites/carcept/files/media/documents/2018/05/Majorations-pour-enfants.pdf` | 9dfcdaf5…43b2, identique |
| Recueil « Accords nationaux des partenaires sociaux », 205 pages | `agirc-arrco.fr/storage/2021/11/liste_accords_paritaires_Agirc_Arrco.pdf` | 0186b6b1…04c1, identique |
| Accord du 8 décembre 1961, mis à jour au 1er janvier 2018 | `agirc-arrco.fr/storage/2021/11/Accord_8dec1961-1.pdf` | 5af24910…9e03, identique |
| Convention du 14 mars 1947, mise à jour au 1er janvier 2018 | `agirc-arrco.fr/storage/2021/11/CCN_14mars1947-1.pdf` | 38966c27…ce78, identique |
| ANI du 17 novembre 2017, « applicable au 1er janvier 2019 » | `agirc-arrco.fr/storage/2024/09/201809dc_ANI_du_17_novembre_2017.pdf` | b8af8df7…fccb, identique |
| Circulaire Agirc-Arrco 2025-15-DT, « Paramètres du régime 2025-2026 » | `agirc-arrco.fr/storage/CirculaireAgircArrco2025-15dt.pdf` | 2e34ce29…b288, identique |
| Circulaire Agirc-Arrco 2023-03-DRJ et avenant n° 15 du 16 mars 2023 | `agirc-arrco.fr/storage/2024/09/2023-03-DRJ_Actualisation_texte_de_base.pdf` | 2c5ea4de…2b01, identique |
| Compilation des valeurs de point, novembre 2026 | `agirc-arrco.fr/storage/2024/10/Compilation_valeurs_de_point_novembre_2026.pdf` | 868a8a65…c4a |
| COR, séance du 25 mai 2011, document n° 7 (DSS), 13 pages | `cor-retraites.fr/sites/default/files/2019-06/doc-1530.pdf` | 952c1af1…9a00 |
| IFRAP, « Majoration de retraite pour enfants, focus sur une inéquité public / privé » | `ifrap.org/retraite/majoration-de-retraite-pour-enfants-focus-sur-une-inequite-public-prive` | page HTML |

La première page de la circulaire n'a pas de texte lisible (police non extraite) : son
numéro, « CIRCULAIRE 2020-02-DRJ », et sa date, « Le 20/01/2020 », ont été lus sur l'image
de la page. **Écart faible** : la fiche cite la circulaire 2025-15-DT sans adresse ; la
voici.

## 2. Les citations, mot pour mot

- **Guide n° 9**, « Les modalités d'attribution et de calcul », « 2. Retraite minorée » :
  « Lorsque la retraite est minorée : • le régime Arrco ne tient pas compte du coefficient
  de minoration pour le calcul des majorations pour enfants ; • le régime Agirc en tient
  compte. » La note et la fiche le citent sans les puces : **conforme**. De même le titre
  « 3. Plafonnement des majorations pour enfants nés ou élevés », le plafond « Au 1er
  novembre 2016 [...] 1 031,15 € pour le régime Arrco et à 1 028,12 € pour le régime Agirc »,
  et la formule « Nombre de points de retraite (de la période) × valeur du point × Taux de
  majoration ». Les deux exemples (p. 14 à 19) partent au taux plein : **conforme**.
- **Circulaire 2020-02-DRJ** : « Cette circulaire précise, sous forme de fiches
  indépendantes, la réglementation Agirc-Arrco applicable aux individus à compter du 1er
  janvier 2019. » Fiche 4, II.2.1 : « La majoration est calculée sur les droits de base du
  participant sans tenir compte des coefficients d'anticipation éventuellement appliqués et
  varie en fonction de la période d'attribution des points de retraite complémentaire » ;
  II.2.2 : « La majoration pour enfants nés ou élevés est plafonnée au montant du cumul des
  plafonds en vigueur à l'Agirc et à l'Arrco applicables à l'entrée en vigueur de l'ANI »,
  « Le montant du plafonnement applicable à un allocataire est celui en vigueur à la date
  d'effet de sa retraite » ; II.2.3 : « Les majorations sont calculées sur les droits du
  participant, sans tenir compte des coefficients d'anticipation éventuellement
  appliqués. » **Conforme.**
- **Les accords** : accord Arrco du 25 avril 1996, article 10, « les points de retraite
  effectivement inscrits au compte de l'intéressé », article 11, « une majoration de leur
  allocation égale à 5 % » ; accord du 18 mars 2011, article 7, « majoration de leur
  allocation égale à 10% » ; annexe A de 1961, article 17, 2, et annexe I de 1947, article 6
  bis, 2, « égale à 10 % de l'allocation correspondant à cette partie de carrière » ; les
  articles 18 et 6, « les points de retraite inscrits au compte de l'intéressé sont affectés
  du coefficient 0,43 » ; ANI, article 94, « une majoration de son allocation », article 84,
  2, « le coefficient d'anticipation viager est appliqué aux points de retraite inscrits au
  compte de l'intéressé ». **Conforme** : aucun ne dit l'ordre de la majoration et du
  coefficient.
- **Le coefficient divisé** : l'ANI, article 85, 3 (carrières courtes), nomme aussi
  « coefficient d'anticipation » celui des trimestres manquants ; le modèle divise
  l'abattement de `liquider` (l'âge, les trimestres manquants, la tranche C d'avant 2016),
  et non un coefficient de solidarité, qu'il ne modélise pas (`config.py`, limite
  déclarée). **Conforme.**

## 3. Le guide de mars 2017, pour les départs de 2012 à 2016

Le guide porte « Édition mars 2017 » (dernière page) ; la copie de Carcept Prev a été créée
le 16 mai 2017 et modifiée le 11 mai 2018 (métadonnées du PDF). Aucune autre édition n'a été
trouvée. Une source secondaire, datée, dit la même règle : l'IFRAP, « Publié le 11 juillet
2013 », « Mis à jour le 05 février 2015 » : « Les majorations pour enfants Arrco sont
calculées sur les droits du salarié sans tenir compte des éventuels coefficients de
minoration. Les majorations pour enfants Agirc sont calculées sur les droits du cadre en
tenant compte des éventuels coefficients de minoration. » Elle conforte la lecture pour
2013, sans être un texte de la caisse. La fiche déclare la lecture à relire : **conforme**.

## 4. L'Agirc de 2012 à 2018 : « en tient compte »

Le « en tient compte » repose sur le seul guide n° 9 (droits directs), conforté par l'IFRAP
de 2013 ; aucun accord ni aucune annexe ne le dit (point 2). **Conforme**, et déclaré.
**Écart faible** : la partie « Réversion » du même guide (« 2. Les modalités de calcul »,
p. 12) dit, sans distinguer les régimes : « Lorsque la retraite a été minorée, il n'est pas
tenu compte du coefficient de minoration pour le calcul de la majoration pour enfants. »
La note ne le relève pas ; il ne touche pas les droits directs que l'étape change, mais il
dit, pour la réversion de 2012 à 2018, le contraire de ce que le guide dit de l'Agirc pour
le retraité. À inscrire aux lectures de la fiche, et à confronter au calcul de la réversion
(`reversion.py`, qui ne dit la majoration de l'Agirc-Arrco que depuis 2019).

## 5. Le plafond, après le coefficient

Depuis 2019, II.2.1 calcule la majoration sans le coefficient et II.2.2 « plafonne » la
majoration ainsi calculée : aucun coefficient ne la frappe, et le plafond, celui de la date
d'effet, la borne. Le texte ne dit pas « après » en toutes lettres ; c'est la seule lecture
que ses deux paragraphes permettent. À l'Arrco de 2012 à 2018, le guide dit de même (2.
puis 3.). À l'Agirc de 2012 à 2018, rien ne tranche, et la fiche le déclare. **Conforme.**
Le plafond de 2026 : « Le montant du plafond des majorations pour enfants nés ou élevés
reste fixé à 2 367,48 € », et « La valeur de service du point est inchangée au 1er
novembre 2025 ; elle reste fixée à 1,4386€ » (circulaire 2025-15-DT) : **conforme**.

## 6. Les neuf cas, refaits à la main

Les valeurs de point, lues à la compilation de la caisse : 1,1884 € (Arrco, 2010) ;
1,2513 € et 0,4352 € (2017, que le guide donne aussi) ; 1,2841 € (« A compter du 1er
novembre 2021 ») ; 1,4386 € (2025 et 2026) ; 1,4587 € (« A compter du 1er novembre 2026 »).
Les coefficients, lus aux tables : « moins 5 ans 0,78 » et « moins 3 ans 0,88 » (annexe A
de 1961, article 18 ; ANI, article 84, 2) ; à 62 ans en 2010, « le coefficient applicable
à 60 ans soit 0,78 est majoré de 0,0125 par trimestre », jusqu'au « coefficient applicable
à 62 ans soit 0,88 » (accord du 25 avril 1996, article 10).

| Cas | Droits (points × valeur) | Avant | Après | Note |
|---|---|---|---|---|
| Arrco 2017, 5 %, 0,78 | 2 050,96 € | 79,99 € | 102,55 € | conforme |
| Cadre 2017, Arrco, 5 %, 0,78 | 2 329,42 € | 90,85 € | 116,47 € | conforme |
| Cadre 2017, Agirc, 8 %, 0,78 gardé | 4 751,10 € | 296,47 € | 296,47 € | conforme |
| 2022, Arrco, 10 %, 0,78 | 1 173,08 € | 91,50 € | 117,31 € | conforme |
| 2022, Agirc-Arrco, 10 %, 0,78 | 531,22 € | 41,44 € | 53,12 € | conforme |
| 2027, Arrco, 10 %, taux plein | 1 332,58 € | 133,26 € | 133,26 € | conforme |
| 2027, Agirc-Arrco, 10 %, taux plein | 1 557,25 € | 155,72 € | 155,72 € | 155,73 € à la note, sur les points non arrondis, qu'elle signale |
| 2010, Arrco, 5 %, 0,88 gardé | 1 343,03 € | 59,09 € | 59,09 € | conforme |
| Plafond 2026, 0,88 | 25 442,00 € | 2 238,90 € | 2 367,48 € | conforme : 2 238,90 < 2 367,48 < 2 544,20 |

Le test calcule l'attendu sur les points et la valeur que la pension affiche : il éprouve
la règle (le rapport au coefficient), non les montants ; seul le plafond y est écrit en
dur, et il est juste.

## 7. Les deux moteurs, et les témoins

- `test_majoration_enfants_agirc_arrco_avant_coefficient.py`, `test_agirc_arrco_au_droit.py`
  et `test_oracle_points_enfants_arrco.py` : 41 passés ; sous `PRESOMPTIONS_DECALEES=1`, 40
  passés, la confrontation à OpenFisca sautée, comme le veut `conftest.py` (« le portage lit
  ses présomptions dans le paquet, que la mesure ne décale pas »).
- `python -m pytest -m rapide` : 4 266 passés, 56 sautés. `-m site` : 36 passés.
- Le portage (`completer.js`) et son jumeau (`completer.py`) font le même geste, ligne pour
  ligne : la majoration de chaque régime nommé se pose sur `montant / coefficient`.
- Les témoins, de l'avant à l'après 488c30a : trois sur 930 bougent, et seulement eux.
  `enfants_pere` : 30 139,94 → 30 233,67 €, +93,73 € (+0,31 %), majoration 2 675,46 →
  2 769,20 € (+3,50 %) ; sa complémentaire porte 0,88, et 687,35 € de majoration avec le
  coefficient donnent 687,35 × (1/0,88 − 1) = 93,73 €. `enfants_carriere_incomplete` :
  +93,73 € (+0,27 %), majoration +3,08 %. `departs_prive_puis_categorie_active_trois_enfants` :
  +10,77 € (+0,04 %), majoration +0,45 % ; son Arrco, liquidée le 1er novembre 2027,
  porte 0,90 : 96,9 € × (1/0,90 − 1) = 10,77 €. **Conforme.**

## 8. L'accord Agirc du 9 février 1994

Recueil de la caisse, p. 15, article 2 : « Les majorations pour charges de famille visées
à l'article 6 bis de l'annexe 1 à la convention collective nationale du 14 mars 1947 sont
affectées, à compter du 1er janvier 1995, d'un pourcentage de service égal à : - 96 % à
compter du 1er janvier 1995 - 85 % à compter du 1er janvier 1996 - 80 % à compter du 1er
janvier 1997 ». La citation de M3 est exacte.

- **À quels points** : à l'Agirc seule, aux majorations de l'article 6 bis, quels que
  soient les points ; **à quelles dates** : aux majorations servies à compter de 1995, sans
  que le texte distingue les allocations déjà liquidées.
- **Ce que l'article 6 bis en a fait** : le COR, document n° 7 du 25 mai 2011 (DSS,
  « Document de travail, n'engage pas le Conseil »), décrit l'article 6 bis d'avant 2012 :
  « majoration du total des points en fonction du nombre d'enfants nés ou élevés et
  application d'un pourcentage de service de 80% (01/03/94) à la majoration suivante : 10%
  pour 3 enfants, 15% pour 4 enfants, 20% pour 5 enfants, 25% pour 6 enfants, 30% pour 7
  enfants et + ». Or 80 % de 10 à 30 % font 8 à 24 % : le barème que l'article 6 bis écrit
  depuis 2012 pour les « périodes antérieures au 1er janvier 2012 », que l'ANI (article 94,
  3) et la circulaire 2020-02-DRJ (fiche 4, II.2.1, 3) reprennent, et que le guide n° 9
  applique sans autre réduction (« 25 000 × 0,4352 × 0,08 », soit 1 305,60 € avec
  « 10 000 × 0,4352 × 0,10 »). C'est une déduction, sur une source secondaire : la rédaction
  de l'article 6 bis de 1994 à 2011 reste à lire. Le COR date le pourcentage du 1er mars
  1994, l'accord des 1er janvier 1995 à 1997 : l'accord fait foi.
- **Ce que le modèle en fait** : il sert 8 à 24 % à toute date d'effet, donc le pourcentage
  de 80 % en fait depuis 1997, si le COR dit vrai ; il ne sert ni les 10 à 30 % d'avant
  1995, ni les 96 % de 1995, ni les 85 % de 1996 (pour trois enfants : 8 % au lieu de 10 %,
  9,6 % et 8,5 %), ce que la version `reglements_d_avant_le_regime_unique`, `supposee`, couvre
  (« dont la rédaction d'alors n'est pas lue »). Depuis 2012, les textes de la caisse
  appliquent 8 % sans le pourcentage : le modèle a raison de ne pas l'y ajouter.
- **Écart faible** : la note et la fiche disent « le modèle ne le sert pas » ; c'est inexact
  si le COR dit vrai, et une session qui le suivrait compterait les 80 % deux fois. À
  récrire dans la ligne `a_relire` de la fiche, avec la référence du COR.

## 9. L'écart d'OpenFisca, au départ de 2014

Pour ce départ à l'Arrco, le guide n° 9 (règle sans date, édition de mars 2017) et l'IFRAP
de 2013 disent la majoration calculée sans le coefficient ; OpenFisca la minore. L'écart
est d'OpenFisca d'après les textes lus, sous la même réserve que le point 3 : aucun texte
de la caisse daté de 2014. **Conforme**, et déclaré au test et à la fiche.

## 10. Ce qui n'a pas pu être vérifié

- **L'avenant n° 16 du 22 novembre 2023** à l'ANI : non vérifié, faute de texte.
  L'avenant n° 15, rouvert ici (circulaire 2023-03-DRJ, point 1), « modifie » l'article 79
  et le point « 3. Carrières courtes » de l'article 85, et rien d'autre : l'article 94 en
  sort inchangé, comme le dit M3. L'avenant n° 16, nommé par une page
  secondaire avec la circulaire 2024-04-DRJ, n'a pas été trouvé à la caisse, et l'index
  JORF n'est pas dans ce conteneur. S'il touche l'article 94, la fiche le dira.
- **Le site réglementaire de la caisse** (`reglementation.agirc-arrco.fr`) ne répond pas
  d'ici non plus ; aucune mise à jour de la circulaire 2020-02-DRJ n'a été trouvée par
  recherche.

## 11. Le paquet

Sur le dernier `main` (5b33e12), `python scripts/construire_donnees.py` ne change rien :
`git status` ne montre que les deux fichiers de cette relecture. Le paquet
(`moteur/donnees.json`, lu par une requête ciblée) porte, sous
`fiches_datees/majoration_enfants_agirc_arrco`, les neuf versions de la fiche et leur
`sans_anticipation` : aucun régime pour les trois versions d'avant 2012 ; `arrco`, ses deux
tranches 2 et `arrco_cultes` pour les trois de 2012 à 2018 ; les sept régimes de la
complémentaire pour les trois depuis 2019. **Conforme.**

## Ce qui attend

Rien de bloquant. À la prochaine session de la fiche : récrire la ligne du pourcentage de
1994 (point 8), inscrire la réversion du guide (point 4) et l'adresse de la circulaire
2025-15-DT (point 1) ; chercher l'avenant n° 16 et la rédaction de l'article 6 bis de
1994 à 2011.
