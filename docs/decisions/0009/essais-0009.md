# Essais de la note 0009 : compte rendu

*16 novembre 2026. Essais sur le papier, en lecture seule : rien n'a changé
dans le dépôt (lu à `origin/main`, 394907a). Après l'essai sur l'âge du taux
plein (`essai-0009-age-du-taux-plein.md`, même dossier), le propriétaire a
demandé d'en faire d'autres. Les trois fiches ont été choisies parce qu'elles
risquaient le plus de casser le format.*

## Le bilan, après quatre fiches

Aucune des quatre ne casse le format tel que le premier essai l'avait
corrigé : une version porte ce que dit son texte. Mais trois règles de la
note changent encore, une quatrième se précise, et le code paiera plus que la
note ne le disait.

- **Ce qui tient, mieux prouvé qu'avant.** Les deux axes : la carrière longue
  écrit en 2023 un renvoi à l'âge légal qui ne se résout qu'avec l'âge légal
  en versions (essai 4). Les couches à la place des copies : les deux copies
  d'avant réforme de l'âge légal sont les tables de deux versions closes
  (essai 2). Les bornes lues dans les textes, et non dans les dates de LEGI,
  pour les trois fiches. Une version par réforme, et non par rédaction : la
  carrière longue a six rédactions dans LEGI et cinq versions.
- **Ce qui change.** Une version peut renvoyer à une autre version de sa
  propre fiche : la loi de 2025 le fait pour l'âge légal, et c'est la
  solution que la note avait écartée (essai 2). La version se choisit à la
  date que nomme le texte, pas toujours à la date d'effet : chaque trimestre
  de surcote prend la version de sa date (essai 3). Un renvoi dit à quelle
  date il lit la fiche visée (essais 3 et 4). La ligne entre table datée et
  version passe entre une valeur et une règle, pas au nombre de dates
  (essai 3).
- **Ce que le code paiera.** Si l'âge dépend de la date d'effet, le moteur
  doit chercher la première date de départ au lieu de la déduire de l'âge
  (essai 2). Des chiffres de la loi vivent en constantes dans le code
  (essai 3). Une version qui change la forme des conditions demande sa
  branche (essai 4, comme l'essai 1).
- **La preuve reste inégale.** Les exemples officiels couvrent surtout les
  dernières versions de chaque fiche, sauf pour la surcote. La certification, qui lit les valeurs
  dans les textes, prouve les valeurs, pas leur application.

Ce n'est pas une preuve pour les 267 fiches : quatre fiches, choisies pour
leur difficulté, et lues sur le papier. Les régimes en points, la réversion
et les régimes spéciaux n'ont pas été essayés.

| Fiche | Pourquoi elle pouvait casser le format | Ce qu'elle a montré |
|---|---|---|
| L'âge du taux plein (essai 1) | Défini par un renvoi | Une version porte ce que dit son texte ; les renvois des régimes sont souvent leur droit |
| L'âge légal (essai 2) | Une table écrite par deux textes ; deux copies d'avant réforme | La loi de 2025 renvoie à sa propre rédaction antérieure |
| La surcote (essai 3) | Le taux suit la date de chaque trimestre | Une pension mêle trois versions |
| La carrière longue (essai 4) | Une grille de conditions ; un renvoi à l'âge légal avec un calcul | Les deux axes existent déjà dans le moteur, et ce renvoi les exige |

## Essai 2 : l'âge légal

### La fiche aujourd'hui

- `age_legal_par_generation`, conforme, sans versions. Elle lit
  `legislation/age_ouverture_requis.csv` : 79 segments certifiés, coupés au
  mois (1er juillet 1951, 1er septembre 1961, 1er avril 1965). Le récupérateur
  les tire de L. 161-17-2 et D. 161-2-1-9 en appliquant leurs rédactions
  « dans l'ordre de leur DATE D'EFFET, chaque version écrasant, MOIS PAR MOIS,
  ce que la précédente disait des générations qu'elle nomme ».
- Deux copies servent aux droits contrefactuels du site :
  `age_ouverture_avant_reforme_2023.csv` (62 ans dès 1955) et
  `age_ouverture_avant_suspension.csv` (63 ans pour 1964, 64 ans dès 1968),
  que `TableRecouverte` pose sur la table.
- 49 régimes y renvoient, sur 562 périodes, chacune avec une valeur de
  repli : l'âge « cible » de chaque réforme, que l'en-tête de la table dit
  faux (« 64 ans opposés à des liquidations de 2023 »).
- Code : `ageOuvertureCommun` (`moteur/js/droit/ouvrir.js`) lit l'âge à la
  génération, sans date ; `ouvertureSous` (`moteur/js/droit/departs.js`) en
  tire le premier mois de départ.
- Cinq exemples officiels, tous postérieurs à la suspension : trois de la
  circulaire Cnav 2026-07, deux fiches de service-public.fr sur la surcote.

### Les versions, au format du dépôt (brouillon)

```yaml
lit:
- la génération de l'assuré, au mois de naissance
dates_qui_decident:
- liquidation.date_effet
versions:
- id: age_determine_fixe_par_decret
  textes: [LEGIARTI000006742620, LEGIARTI000006742621, LEGIARTI000006742622 (L. 351-1),
    LEGIARTI000006749340 (R. 351-2)]
  bornes: {liquidation.date_effet: [1985-12-21, 2011-07-01]}   # avant : l'ancien code, hors de l'index
  contenu: {parametres: {age: 60}, droit: « un âge déterminé », que le décret fixe à soixante ans}
  # formule à relire sur le texte, comme L. 351-8 et R. 351-27 dans l'essai 1
  exemples: aucun dans le dépôt
- id: loi_de_2010
  textes: [LEGIARTI000023030935 (L. 161-17-2), LEGIARTI000023388636 (D. 161-2-1-9)]
  nee_de: loi n° 2010-1330, article 18 ; article 118, II
  bornes: {liquidation.date_effet: [2011-07-01, 2011-12-23]}
  contenu: la table du décret, quatre mois par génération ; 62 ans dès 1956, dans la loi
  exemples: aucun dans le dépôt
- id: loi_de_2011
  textes: [LEGIARTI000025014605 (L. 161-17-2), LEGIARTI000025089933 (D. 161-2-1-9)]
  nee_de: loi n° 2011-1906, article 88
  bornes: {liquidation.date_effet: [2011-12-23, 2023-09-01]}
  # relu le 16 novembre : pas de disposition d'application dans LEGI, et aucune fenêtre ;
  # les nés de 1952 à 1955 ne pouvaient pas partir avant septembre 2012 sous la loi de 2010,
  # et aucune pension ne prend effet entre la loi (23 décembre) et le décret (31 décembre)
  contenu: la table du décret, cinq mois par génération ; 62 ans dès 1955
  exemples: aucun dans le dépôt
- id: loi_de_2023
  textes: [LEGIARTI000047452768, LEGIARTI000051289659 (L. 161-17-2),
    LEGIARTI000047634502 (D. 161-2-1-9)]
  nee_de: loi n° 2023-270, article 10
  bornes: {liquidation.date_effet: [2023-09-01, 2026-09-01]}
  contenu: la table du décret, du 1° au 14° ; 64 ans dès 1968, dans la loi
  exemples: aucun dans le dépôt
- id: suspension_de_2025
  textes: [LEGIARTI000053280889 (L. 161-17-2, version du 31 décembre 2025)]
  nee_de: loi n° 2025-1403, article 105
  bornes: {liquidation.date_effet: [2026-09-01, null]}
  contenu:
    table: les nés à compter du 1er septembre 1961, de 62 ans et 3 mois à 64 ans dès 1969
    renvoi: >-
      « Pour les assurés nés avant le 1er septembre 1961, il est celui applicable
      en application du présent article dans sa rédaction antérieure » : la
      version loi_de_2023, qui renvoie elle-même au décret
  exemples: [cnav_2026_07_age_legal_1964, cnav_2026_07_age_legal_1965_premier_trimestre,
    cnav_2026_07_age_legal_1965_apres_avril, sp_f19643_surcote,
    sp_f16494_surcote_fonction_publique]
```

### Ce que l'essai montre

**1. La loi de 2025 ne porte que ce qu'elle change.** Elle écrit l'âge des
nés à compter du 1er septembre 1961, et renvoie les autres à sa rédaction
antérieure (citée par le récupérateur du dépôt, qui l'a lue dans LEGI). C'est
la solution que la note 0009 avait écartée, « une version qui ne porte que ce
qu'elle change », parce que lire une version demanderait de recomposer la
table. Le texte l'impose pourtant : la version de 2025 porte une table pour
une partie des générations et un renvoi à la version de 2023 pour le reste,
qui elle-même renvoie au décret. Le récupérateur le fait déjà, mois par mois.
Le format doit donc permettre un renvoi d'une version à une autre version de
sa propre fiche, borné aux générations que le texte lui laisse.

**2. Le décret en vigueur contredit la loi.** D. 161-2-1-9 n'a pas été
réécrit en 2025 : il dit encore 63 ans pour 1964, quand la loi dit 62 ans et
9 mois pour les pensions de septembre 2026. La loi l'emporte. Une version ne
peut donc pas citer « les textes en vigueur » en bloc : elle cite, pour
chaque partie de sa table, celui qui décide. La note le disait (« chaque
ligne cite son texte ») ; c'est ici nécessaire.

**3. Les deux copies sont deux versions.** `age_ouverture_avant_reforme_2023.csv`
est la table de la version de 2011, `age_ouverture_avant_suspension.csv`
celle de la version de 2023. Les deux lois sont closes (62 ans dès 1955,
64 ans dès 1968) : une couche qui garde l'une prolonge sa version telle
quelle, sans rien supposer. `TableRecouverte` et les deux classes par loi
disparaissent. La note le disait ; c'est vrai ici.

**4. Aucun résultat ne devrait bouger, mais grâce à l'écriture des lois, pas
au format.** La table par génération donne le bon âge parce que chaque loi a
visé des générations qui ne pouvaient pas encore partir : un assuré né en
1964 n'atteint 62 ans et 9 mois qu'en octobre 2026, après la date d'effet de
la suspension, comme le dit l'en-tête de la table. Mais le moteur déduit le
premier départ possible de l'âge (`ouvertureSous`), puis la date d'effet de
ce départ. Avec des versions, l'âge dépend de la date d'effet : il faut
chercher la première date dont la version ouvre le droit. Si une loi
relevait l'âge d'une génération qui pouvait déjà partir, la table et la
recherche donneraient deux dates différentes. Les lois de 2010, 2023 et 2025
ne l'ont pas fait ; celle de 2011 se vérifiera avec sa borne. Un test devrait
le garder pour chaque réforme.

**5. Les renvois des régimes : même constat que l'essai 1, avec une
nuance.** 22 régimes ont des périodes sans renvoi avant de renvoyer, et
certains y portent un âge à eux : 55 ans à la Banque de France et à la CRPCEN
jusqu'en 2007, 65 ans à la MSA des non-salariés jusqu'en 1985, à la CNBF
jusqu'en 2003. Mais toutes les dates de bascule ne sont pas du droit : le
régime général ne renvoie qu'à partir de 1994, la fonction publique de l'État
à partir de 2004, et leur âge, 60 ans, n'a pas changé ces années-là. Ce sont
des coupures de leurs fichiers. L'essai 1 disait que ces dates appartiennent
au droit de chaque régime : il faut les relire une à une.

**6. La preuve.** Les cinq exemples valent pour la version de 2025. Les
quatre premières n'en ont aucun dans le dépôt, mais leurs valeurs sont
certifiées : lues dans les textes par le récupérateur. Ce sont deux preuves
différentes. La certification prouve la valeur ; l'exemple prouve
l'application, la date d'effet et la coupure au mois.

## Essai 3 : la surcote du régime général

### La fiche aujourd'hui

- `surcote_regime_general`, conforme, sans versions. Le taux vient de
  `legislation/surcote_baremes.csv`, un barème daté au trimestre : 0,75 % de
  2004 à 2006 ; en 2007 et 2008, 0,75 % pour les quatre premiers trimestres,
  1 % ensuite, 1,25 % après 65 ans ; 1,25 % depuis 2009. En 2007 et 2008,
  « le RANG se compte depuis le premier trimestre de surcote, ceux de 2004 à
  2006 compris ». Le barème a dû prendre trois colonnes de règle
  (`rang_minimum`, `apres_65_ans`, `trimestres_maximum`).
- La période qui ouvre la surcote commence au plus tard de trois dates : le
  trimestre qui suit l'âge légal, le mois qui suit la durée requise, le
  1er janvier 2004 (circulaire Cnav 2018-04). Deux renvois, à l'âge légal et
  à la durée requise.
- Code : `coefficientSurcoteDatee` (`moteur/js/droit/liquider.js`) prend
  chaque trimestre au taux de sa date. Deux chiffres de la loi y sont des
  constantes : `SURCOTE_DEPUIS` (le 1er janvier 2004) et `SURCOTE_AGE_MAJORE`
  (65 ans).
- Quatre exemples officiels : la fiche F19643 de service-public.fr, et trois
  cas de la circulaire Cnav 2018-04, à un, deux et trois taux.
- D. 351-1-4 a cinq rédactions dans LEGI : 19 février 2004, 17 décembre
  2006, 1er avril 2009, 1er juillet 2011, 1er janvier 2026.

### Les versions, au format du dépôt (brouillon)

```yaml
lit:
- chaque trimestre civil cotisé après l'âge légal et au-delà de la durée requise, à sa date
- l'âge légal et la durée requise de l'assuré, lus à la date d'effet de sa pension
dates_qui_decident:
- periode.debut            # le taux : la date du trimestre
- liquidation.date_effet   # les deux renvois
versions:
- id: decret_de_2003
  textes: [LEGIARTI000006742670 (L. 351-1-2), LEGIARTI000006736524 (D. 351-1-4)]
  nee_de: loi n° 2003-775 ; décret n° 2003-1306
  bornes: {periode.debut: [2004-01-01, 2007-01-01]}
  contenu: {parametres: {taux: 0.0075}}
  exemples: [cnav_2018_04_surcote_trois_taux]
- id: decret_de_2006
  textes: [LEGIARTI000006736525 (D. 351-1-4)]
  nee_de: décret n° 2006-1611
  bornes: {periode.debut: [2007-01-01, 2009-01-01]}
  contenu:
    parametres: {taux_des_quatre_premiers: 0.0075, taux_ensuite: 0.01, taux_apres_65_ans: 0.0125}
    droit: le rang se compte depuis le premier trimestre de surcote, ceux de 2004 à 2006 compris
  exemples: [cnav_2018_04_surcote_deux_taux, cnav_2018_04_surcote_trois_taux]
- id: loi_de_2008
  textes: [LEGIARTI000020090083 (D. 351-1-4)]
  nee_de: loi n° 2008-1330 ; décret n° 2008-1509
  bornes: {periode.debut: [2009-01-01, null]}   # relu le 16 novembre : voir plus bas
  contenu: {parametres: {taux: 0.0125}}
  exemples: [cnav_2018_04_surcote_un_taux, cnav_2018_04_surcote_deux_taux,
    cnav_2018_04_surcote_trois_taux, sp_f19643_surcote]
```

### Ce que l'essai montre

**1. La version ne se choisit pas à la date d'effet.** Chaque trimestre prend
la version de sa date, et une pension en mêle plusieurs : l'exemple « trois
taux » de la Cnav, un assuré né en 1944, en mêle trois. Le contrat C.2 le
permet déjà : 18 fiches bornent leurs versions par `periode.debut`. Ce qui
tombe, c'est la phrase de l'essai 1, « la version se choisit à la date
d'effet » : elle se choisit à la date que nomme le texte.

**2. Une même fiche a deux dates qui décident, pour deux parties.** Le taux
suit la date du trimestre ; la période de référence renvoie à l'âge légal et
à la durée requise, lus à la date d'effet, comme le reste de la pension (le
moteur les lit à la génération). Un renvoi doit donc dire à quelle date il
lit la fiche visée. L'essai 1 l'écrivait pour un renvoi ; c'est une règle.

**3. Une version dépend de ce qui s'est passé sous la précédente.** En 2007
et 2008, le taux d'un trimestre dépend de son rang, compté depuis le premier
trimestre de surcote, ceux de 2004 à 2006 compris. Dans la fonction
publique, l'ancien barème plafonne à vingt trimestres. Ce n'est pas un trou
du format : le rang est un fait de la carrière, que le code compte ; la
version dit comment s'en servir.

**4. La ligne entre table datée et version, que la note traçait au nombre de
dates, est à revoir.** La surcote ne dépend que d'une date, celle du
trimestre ; selon la note, elle irait en table datée (C.3), « même quand un
texte en change la forme ». C'est ce que fait le dépôt, au prix de trois
colonnes de règle que seul le code explique. La ligne plus juste : une valeur
que seule une date change va en table datée ; une règle dont la forme change
va en versions, quelle que soit la date qui les choisit.

**5. Les dates de LEGI ne sont pas les bornes, ici non plus.** La rédaction
qui porte 1,25 % entre dans LEGI le 1er avril 2009, pour les trimestres
accomplis depuis le 1er janvier 2009 ; celle de 2006, le 17 décembre 2006,
pour les trimestres de 2007.

**6. Le code et la preuve.** Les deux constantes passent dans les versions.
La fonction applique déjà le taux trimestre par trimestre : l'étape de code
serait courte, et aucun résultat ne devrait bouger. La preuve est la
meilleure des quatre fiches : chaque version a son exemple officiel, et deux
exemples traversent ses bornes.

**Relu le 16 novembre, avec les cinq rédactions de D. 351-1-4.** Les points 1,
5 et 6 se corrigent.

- Chaque rédaction vaut pour les pensions qui prennent effet après elle :
  celles de 2011 et de 2026 le disent (« applicables aux pensions prenant
  effet à compter du 1er juillet 2011 », décret n° 2010-1734 ; à compter du
  1er janvier 2026, décret n° 2025-1410). Dans chacune, le taux suit la date
  du trimestre. La date d'effet choisit donc la version, la date du trimestre
  la ligne ; les trois versions ci-dessus sont les lignes que porte chaque
  rédaction depuis 2009.
- Elles ne disent juste que si aucune rédaction ne change le droit des
  trimestres d'avant elle. Celle de 2004 donne 0,75 % à tout trimestre.
  Celle de 2006 (décret n° 2006-1611 du 15 décembre 2006, au Journal officiel
  du 17, et non du 19 comme l'écrit le dépôt) donne ses taux « pour chaque
  trimestre accompli à compter du 1er janvier 2004 » : un cinquième trimestre
  de 2005 y prend 1 %, un trimestre de 2005 après soixante-cinq ans 1,25 %.
  Le barème du dépôt leur garde 0,75 %, sur la circulaire Cnav 2018-04 et sur
  une disposition d'application du décret qu'il cite sans identifiant
  (`reformes.yaml`). La page du décret ne
  s'ouvre pas sur Légifrance, et aucun des quatre exemples n'a de cinquième
  trimestre avant 2007 : l'exemple « trois taux » commence sa surcote en
  juillet 2006. Le point 6 surestimait donc la preuve.
- La rédaction de 2011 remplace le soixantième anniversaire par l'âge légal,
  sans changer aucune pension ; celle de 2026 la reprend phrase pour phrase.
- LEGI attribue la création de l'article au décret n° 2004-156 du 16 février
  2004, que ni le barème ni la version `decret_de_2003` ne citent.

## Essai 4 : la carrière longue

### La fiche aujourd'hui

- `carriere_longue`, conforme, sans versions dans la fiche. Mais
  `legislation/carriere_longue.csv` est déjà rangé comme la note le voulait :
  chaque ligne est une « porte » (borne d'entrée, trimestres de début, âge de
  départ, trimestres exigés en plus), avec sa date d'effet et les générations
  que sa rédaction nomme. Cinq dates d'effet (janvier 2004, juillet 2011,
  novembre 2012, septembre 2023, septembre 2026) et 80 portes, certifiées
  dans les rédactions de D. 351-1-1. Le moteur (`CarriereLongue._portes`)
  retient celles du texte en vigueur à la date d'effet.
- Le droit contrefactuel garde une version par `avant(...)` : c'est déjà une
  couche. La rédaction de 2012 couvre toutes les générations, sans rien à
  supposer.
- Les conditions changent de forme d'une version à l'autre : cinq
  trimestres avant la fin de l'année de la borne, quatre au né du dernier
  trimestre, dans la seule année de son anniversaire pour les pensions
  d'avant novembre 2012 ; huit trimestres d'assurance au-delà de la durée
  requise jusqu'en octobre 2012 ; trimestres réputés cotisés ; périodes
  assimilées au début d'activité.
- Onze exemples officiels, publiés en 2026 par la Cnav et l'Union Retraite,
  tous pour les générations 1964 à 1971.

### Ce que l'essai montre

**1. Les deux axes existent déjà dans le moteur, et marchent.** Un tableau
par version, indexé par génération, choisi à la date d'effet : la forme de la
note tourne ici depuis l'action 27. Passer en versions de fiche serait
découper le fichier par date d'effet, chaque bloc citant sa rédaction. LEGI
compte six rédactions de D. 351-1-1 et la fiche cinq versions : celle du
1er janvier 2026 « réécrit le I sans changer une valeur » et n'ouvre pas de
date d'effet. C'est le cas que la note écartait, « une version par rédaction
d'article de LEGI ».

**2. Un renvoi exige l'âge légal en versions.** La rédaction de 2023 écrit la
porte des vingt ans de la génération 1964 comme « l'âge prévu à l'article
L. 161-17-2 minoré de deux ans et six mois ». Le récupérateur la résout
contre l'âge légal de 2023, 63 ans, soit 60 ans et 6 mois, et stocke le
nombre. Lue contre la table d'aujourd'hui, qui donne 62 ans et 9 mois à cette
génération (l'âge de la suspension), elle donnerait 60 ans et 3 mois : trois
mois trop tôt pour les pensions de septembre 2023 à août 2026. C'est le
contre-exemple qui manquait aux deux axes : sans l'âge légal en versions, un
renvoi daté ne se résout pas. Le dépôt l'évite en recopiant le nombre ; une
version qui porte ce que dit son texte porterait le renvoi, et le moteur le
résoudrait à la date d'effet.

```yaml
- id: loi_de_2023
  textes: [LEGIARTI000047634571 (D. 351-1-1)]
  bornes: {liquidation.date_effet: [2023-09-01, 2026-09-01]}
  contenu:
    portes:
    - {borne: 20, generation: 1964, age: « l'âge prévu à l'article L. 161-17-2 minoré de deux ans et six mois »}
      # lu dans la version loi_de_2023 de l'âge légal : 63 ans, soit 60 ans et 6 mois
```

**3. Le coût est dans le code.** Chaque version change la forme des
conditions, pas seulement des nombres. Relier le code aux versions demandera
une branche par version, comme l'essai 1 l'avait vu pour l'âge du taux
plein ; le moteur en a déjà une pour les pensions d'avant novembre 2012.

**4. La preuve est concentrée sur les dernières versions.** Les onze
exemples visent les générations 1964 à 1971 ; aucun ne vaut pour les
versions de 2004, 2011 et 2012, dont les portes sont pourtant certifiées.
Aucun résultat ne devrait bouger.

## Ce que les essais changent à la note 0009

Phrase par phrase. La note a été réécrite selon cette liste le 16 novembre
(`docs/decisions/0009-le-droit-date-dans-les-versions-de-fiche.md`), pour être
adoptée ; le brouillon qu'elle remplace est gardé à côté
(`0009-brouillon-du-15-novembre.md`).

- « Chaque version porte sa table entière » devient : une version porte ce
  que dit son texte, une table, une valeur, un renvoi à une autre fiche ou à
  une autre version de la sienne (essais 1 et 2).
- « Une version qui ne porte que ce qu'elle change » sort des solutions
  écartées : elle revient quand le texte l'écrit (essai 2).
- « La version se choisit à la date d'effet » devient : à la date que nomme
  le texte, le plus souvent la date d'effet (essai 3).
- Un renvoi nomme la fiche visée et la date à laquelle il la lit (essais 1,
  3 et 4).
- La ligne entre table datée et version : une valeur que seule une date
  change va en table datée ; une règle dont la forme change va en versions
  (essai 3).
- Les renvois des régimes restent, mais leurs dates de départ se relisent
  une à une : certaines sont du droit, d'autres des coupures de fichier
  (essai 2, qui nuance l'essai 1).
- Les preuves : la certification prouve la valeur, l'exemple l'application.
  Une version reprise devrait avoir les deux, ou dire ce qui a été cherché.
- Le moteur cherche la première date de départ quand l'âge dépend de la date
  d'effet, et un test vérifie, réforme par réforme, qu'aucune fenêtre ne
  s'ouvre (essai 2).

## Ce qui reste ouvert

Examiné le 16 novembre ; le détail est dans la note 0009, « Ce qui reste
ouvert ».

- **Le trou d'avant 1985 est celui de l'ancien code, pas celui des fiches.**
  L'index n'a aucun article du code de la sécurité sociale avant le
  21 décembre 1985, mais 171 des 271 versions qui couvrent des pensions
  d'avant cette date sont `lue`, dans les textes qui ont écrit la règle ;
  100 sont `supposée`, dont 73 sans texte. Un chantier de données, pas de
  format.
- Les bornes de la loi de 2011 : lues, sans fenêtre (essai 2, version
  `loi_de_2011`).
- Les rédactions de D. 351-1-4 de 2011 et de 2026 : sans effet sur les
  pensions ; la relecture a trouvé l'écart des trimestres de 2004 à 2006
  (essai 3, « Relu le 16 novembre »), à trancher avant de migrer la surcote.
- Les fiches non essayées : les régimes en points (valeur du point, en
  tables datées), la réversion (la date du décès décide), les régimes
  spéciaux et leurs tables propres.

## L'étape de code, si elle est décidée

L'âge légal d'abord, puisque les trois autres fiches le lisent. Une session
neuve, sur Fable 5.2, comme une étape de l'action 191 : écrire d'abord les
tests (les cinq versions, à quelques générations et dates tirées des textes
et des exemples, et la recherche de la première date de départ, qui doit
rendre la même date que la table pour chaque réforme) ; faire lire les
versions au moteur, renvoi de 2025 compris ; retirer les deux copies et
`TableRecouverte` ; témoins identiques ; une étape, poussée sur `main` selon
les règles du dépôt. Viendraient ensuite l'âge du taux plein (essai 1), la
carrière longue, dont le renvoi de 2023 remplacerait le nombre recopié, et la
surcote, en versions choisies à la date d'effet, chaque trimestre au taux de
sa date, une fois lue la disposition d'application du décret n° 2006-1611.
