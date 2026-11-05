# Retouches de la relecture R-N : la CRPNPAC avant cinquante ans, et six écarts faibles (Retouches 3)

Le 5 novembre 2026, action 130. La relecture R-N (`2026-11-05-relecture-de-n-crpnpac.md`) du travail
de la file N (1464c06, `2026-11-05-crpnpac-et-regime-general.md`) a trouvé un écart moyen et six
écarts faibles. Cette note les reprend un à un, dans les fiches et ici ; ni règle, ni donnée, ni
valeur du modèle ne change. Chaque texte a été rouvert dans l'index LEGI du dépôt, récupéré dans la
session (`dila_index.py legi --recuperer`, à jour du 2 novembre 2026, incrément 20261102-213929),
par `dila_cherche.py` (`--num`, `--texte`) ; rien n'est repris de la relecture ni de la mémoire.
Les moteurs ont été rejoués par `servi_et_refait` (`tests/outils_pont.py` : le portage sert, le
moteur Python refait) sur trois cas, ci-dessous. Les fiches touchées : `crpn_pension_des_navigants`
(approximations, lectures) et `liquidation_regime_par_regime` (texte de la CRPNPAC, `textes`,
`a_relire`, lectures).

## A1. L'âge de la CRPNPAC avant 2012 — écart moyen, déclaré

**Ce que R-N dit** : de 1984 à 2011, la CRPNPAC s'ouvrait par anticipation dès quarante-cinq ans
(R. 426-15-1), et le modèle refuse ces départs ; la note de N, qui ne cite que R. 426-11-1 de 1995
à 2011 et déclare l'article d'avant 1995 « non relu », est incomplète.

**Ce que j'ai lu** (code de l'aviation civile, index LEGI) :

- R. 426-15-1, du 1er juillet 1984 au 1er juillet 1995 (LEGIARTI000006845221) : « L'entrée en
  jouissance de la pension prévue à l'article R. 426-11 ne peut être antérieure à la date à laquelle
  l'intéressé a atteint l'âge de cinquante ans. Toutefois, l'entrée en jouissance prend effet
  immédiatement lorsque la cessation d'activité est postérieure à l'âge de quarante-cinq ans
  accomplis, pour l'affilié qui compte vingt-cinq annuités valables pour la retraite et qui demande
  la liquidation anticipée de sa pension, sous réserve des réductions prévues à l'article
  R. 425-18. » (le texte écrit « R. 425-18 ») ; l'article continue par l'inaptitude définitive, à la
  date de laquelle l'entrée en jouissance prend effet.
- R. 426-18, de la même rédaction (LEGIARTI000006845236) : « Dans le cas de jouissance anticipée de
  la pension mentionnée au deuxième alinéa de l'article R. 426-15-1, la pension annuelle […] est
  affectée des coefficients de minoration suivants », « 45 ans / 0,65 46 ans / 0,73 47 ans / 0,81
  48 ans / 0,88 49 ans / 0,95 » : c'est donc bien lui que vise « R. 425-18 ».
- R. 426-15-1, du 1er juillet 1995 au 1er janvier 2012 (LEGIARTI000006845222) : « Le droit à pension
  peut être ouvert par anticipation : a) Pour les pensions à taux plein, postérieurement au
  quarante-cinquième anniversaire, avec application des coefficients de minoration prévus à
  l'article R. 426-18 ; b) Pour les pensions proportionnelles, à l'exception de celles visées à
  l'article R. 426-11-3, postérieurement au cinquantième anniversaire, si l'intéressé ne justifie
  pas du nombre de jours validés nécessaires à l'ouverture du droit à pension proportionnelle
  conformément aux dispositions du deuxième alinéa de l'article R. 426-11-2, avec application des
  coefficients actuariels d'anticipation prévus à l'article R. 426-18-1. » ; R. 426-18 de 1995
  (LEGIARTI000006845237) reprend les coefficients, « avant l'âge de cinquante ans […] de la pension
  mentionnée au a de l'article R. 426-15-1 ».
- R. 426-11-1, de 1995 à 2011 (LEGIARTI000006845207) : « Le droit à pension à taux plein d'un
  affilié est ouvert aux conditions suivantes : Avoir atteint l'âge de cinquante ans ; Avoir validé
  un nombre d'annuités au moins égal à : 25, lorsque N est supérieur ou égal à 7 ; (32 - N),
  lorsque N est supérieur à 2 et inférieur à 7 ; 30, lorsque N est inférieur ou égal à 2. » C'est
  le droit « à taux plein », non l'âge où la caisse s'ouvre : la phrase de N (et de la fiche) sur
  1995 à 2011 est incomplète, et l'âge d'avant 1995 se lit à R. 426-15-1, désormais relu. R-N ne
  citait la rédaction de 1984 que jusqu'à « vingt-cinq annuités » sans le dire : elle est citée ici
  en entier.

**Le modèle, rejoué** (`servi_et_refait`, requête de N, statut `personnel_navigant`, entré à vingt
ans, deux salaires moyens) : né le 10 février 1957, parti à 48 ans (mars 2005) : refusé,
`liquidation_ouverte` faux, motif `non_ouverte`, aucun départ ; né le 10 février 1940, parti à
47 ans (mars 1987) : de même ; né en 1957, parti à 50 ans : servi, la CRPNPAC en mars 2007 et le
reste en mars 2019. Les deux moteurs concordent. La cause est lisible : `age_ouverture: 50` à
toutes les périodes de `data/reference/regimes/crpnpac.yaml`.

**Une précision qui manquait à R-N** : « les textes lui ouvraient la CRPNPAC » n'est sûr que pour
1984 à 1995 (vingt-cinq annuités). De 1995 à 2011 l'anticipation du a) vise « les pensions à taux
plein » et dépend de N, la valeur du fonds, que le modèle ne porte pas : le cas de 1957 (28 années
de services à 48 ans) n'est ouvert qu'à N d'au moins 4 (32 − N ≤ 28). Le texte de 1995 ne dit pas en
toutes lettres que ces pensions sont celles de R. 426-11-1 : c'est la lecture qui s'impose, et la
fiche le dit comme telle.

**Fait** : l'approximation est déclarée dans `crpn_pension_des_navigants` (versions
`vingt_cinq_annuites` et `valeur_n_du_fonds`), avec les deux rédactions de R. 426-15-1, celles de
R. 426-18 et celle de R. 426-11-1 citées mot pour mot, et ses deux cas ; la fiche
`liquidation_regime_par_regime` renvoie à elle, et son `a_relire` ne dit plus « l'article d'avant
1995 non relu ». Le modèle n'est pas corrigé : la question va au propriétaire (le refus de ces
départs, ou la CRPNPAC servie dès 45 ans sous les coefficients de R. 426-18, selon N).

## A2. Six écarts faibles

1. **R. 426-16-1.** Texte rouvert (LEGIARTI000036880164, du 7 mai 2018 au 1er novembre 2023) : « Pour
   la période de jouissance comprise entre l'âge auquel l'affilié aura atteint le nombre d'annuités
   nécessaires pour l'ouverture du droit à pension, et ce au plus tôt à l'âge mentionné au 1° du A du
   II de l'article R. 426-11, et l'âge mentionné à l'article L. 161-17-2 du code de la sécurité
   sociale, la pension mensuelle est assortie d'une majoration ». La fiche écrivait « l'âge [...]
   d'ouverture » : le « d' » n'est pas dans le texte, qui dit « pour l'ouverture ». Corrigé dans la
   fiche, avec la période de la rédaction, du 7 mai 2018 au 1er novembre 2023 (non « depuis »). Le
   docstring de `tests/test_ouverture_des_navigants.py` porte la même coquille : corrigé aussi (un
   commentaire, aucun test ne bouge).
2. **R. 6527-21.** Texte rouvert (LEGIARTI000048325100, depuis le 1er novembre 2023) : « Une pension
   de retraite est servie à l'affilié qui demande la liquidation de ses droits à pension, dans les
   conditions prévues par les articles R. 6527-22, R. 6527-27, R. 6527-49 et R. 6527-50 dès lors
   qu'il réunit cumulativement à la date d'effet de la pension les conditions suivantes : 1° Avoir
   atteint l'âge de cinquante ans ; 2° Justifier de vingt annuités acquises au titre des services
   valables pour la retraite tels qu'ils sont définis à l'article R. 6527-28. Cette condition n'est
   pas requise lorsque l'assuré a atteint l'âge prévu par l'article R. 6527-23. » Mêmes conditions, 1°
   et 2°, que R. 426-11, I (2012 et 2021) ; non la même phrase (« dans les conditions précisées aux
   articles suivants », « à l'article R. 426-13 », « à l'article R. 426-12 », « prévu à »). La fiche
   le dit désormais.
3. **Le décret n° 2011-1500, article 26.** Lu en entier (LEGIARTI000024779267, du 1er janvier 2012 au
   16 décembre 2021). Le I : « Par dérogation aux dispositions du I de l'article R. 426-11 […], la
   condition d'annuité prévue au 2° est fixée comme suit pour les pensions prenant effet entre le 1er
   janvier 2012 et le 31 décembre 2019 : 1° Du 1er janvier 2012 au 31 décembre 2012, à 16
   annuités ; 2° […] à 16,5 annuités ; 3° Du 1er janvier 2014 au 31 décembre 2014, à 17 annuités ; 4°
   […] à 17,5 ; 5° […] à 18 ; 6° […] à 18,5 ; 7° […] à 19 annuités ; 8° Du 1er janvier 2019 au 31
   décembre 2019, à 19,5 annuités. » Les chiffres de R-N (17 en 2014, 19,5 en 2019) sont exacts. Le II
   (l'âge et les annuités du taux plein, de « cinquante ans et 6 mois et 26 annuités » en 2012 à
   « cinquante-quatre ans et 6 mois et 30 annuités » en 2020) a aussi été lu, comme le IV. Le I et le
   II étaient déjà déclarés « non portés » par `crpnpac.yaml` (manque) et par `decote_crpn`. Le IV (la
   limite de la première tranche, de 3,55 plafonds en 2012 à 3,95 en 2020) n'y est pas nommé : je ne
   l'ai confronté ni à la fiche de régime ni au modèle, **à instruire**. Cas rejoué : né
   le 10 février 1964, entré à quarante ans, parti à 55 ans (15 annuités) : la CRPNPAC est servie le
   1er mars 2019 dans les deux moteurs, quand le texte demande 19,5 annuités à une pension de 2019 et
   n'exempte que l'affilié qui a l'âge de R. 426-12. Le défaut candidat de N tient. **Fait** :
   déclaré et cité dans `crpn_pension_des_navigants` (approximations) et dans le `a_relire` de
   `liquidation_regime_par_regime`.
4. **R. 426-15-4, la règle de date.** Lu (LEGIARTI000006845227, du 1er juillet 1995 au 1er novembre
   2023) : « Sauf disposition particulière contraire, l'entrée en jouissance d'une pension pour
   laquelle un droit est ouvert prend effet le premier jour du mois suivant la réception de la
   demande. » Cité dans la fiche, avec ses bornes. Avant 1995 et depuis le code des transports, la
   règle de date n'est pas lue ici.
5. **D. 351-1-1, ses rédactions depuis 2023.** Lues : LEGIARTI000047634571 (du 1er septembre 2023 au
   1er janvier 2026, « s'appliquent aux pensions prenant effet à compter du 1er septembre 2023 »),
   LEGIARTI000053356023 (du 1er janvier 2026 au 1er septembre 2026, décret n° 2025-1410) et
   LEGIARTI000054059621 (depuis le 1er septembre 2026, décret n° 2026-345, article 4). Le I, à
   l'identique dans les trois : « 1° A cinquante-huit ans pour les assurés qui ont débuté leur
   activité avant l'âge de seize ans ; 2° A soixante ans […] avant l'âge de dix-huit ans ; 3° A
   soixante-deux […] avant l'âge de vingt ans ; 4° A soixante-trois ans pour les assurés qui ont
   débuté leur activité avant l'âge de vingt-et-un ans ». La rédaction du 1er septembre 2026 régit la
   pension du 1er décembre 2026 du navigant de N ; celle de 2023, le cas d'une pension de mars 2024.
   Entré à vingt-deux ans, il n'a la carrière longue à aucune date : la conclusion de N tient. Le II
   de la rédaction du 1er septembre 2026 adapte le 3° du I pour les nés en 1964 (« soixante ans et six
   mois » au lieu de « soixante-deux ans », début avant vingt ans) : sans objet pour un début à
   vingt-deux ans. Citées dans la fiche (`textes` et lectures).
6. **« Aucun témoin ne bouge ».** R-N écrit qu'aucun témoin ne contient « personnel_navigant » ni
   « crpnpac » : **c'est inexact dans la lettre**. `tests/temoins/simulations.json` porte sept
   témoins `statut_personnel_navigant*` (nés en 1925, 1935, 1945, 1955, 1965, 1975 et le
   20 septembre 1968), tous du statut `personnel_navigant`, entrés à vingt et un ans, partis à
   64 ans. C'est vrai dans le fond : à 64 ans les deux âges, celui de la CRPNPAC et celui de
   L. 161-17-2, sont atteints ; ces témoins ne passent pas par le chemin que la correction de N
   change, la CRPNPAC servie avant le régime général. Ne bouge qu'un chemin que seul le test de N
   (`tests/test_ouverture_des_navigants.py`, par `servi_et_refait`) confronte entre les deux
   moteurs ; l'affirmation « aucun témoin ne bouge » ne prouve donc rien sur la règle. Je n'ai pas
   rejoué ces sept témoins.

## Ce que je laisse

- La phrase de R-N à reprendre par « une session qui y travaille » sur le renvoi de l'Agirc-Arrco à
  l'écart de la fiche `coefficients_anticipation_agirc_arrco` n'était pas au programme ; la fiche
  `liquidation_regime_par_regime` dit déjà l'anticipation des complémentaires des salariés.
- Les défauts candidats ne sont pas corrigés : le refus de la CRPNPAC avant 50 ans, les vingt annuités
  et leur barème de 2012 à 2019 vont au propriétaire.
- Le cliquet des textes baisse de 9 324 à 9 323 (`perimetre.yaml`) : L. 643-5
  (LEGIARTI000006743795), que nulle fiche ne citait, est rattachée par la fiche
  `liquidation_regime_par_regime` (point B2 de la note jumelle). R. 426-15-4 n'est pas au périmètre
  de la liste.
