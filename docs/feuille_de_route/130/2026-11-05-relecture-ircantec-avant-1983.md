# Relecture de l'Ircantec d'avant 1983 (file R-M3d)

File R-M3d, le 5 novembre 2026 : relecture indépendante des commits e27cdce (la table par
année d'âge jusqu'au 31 août 1983), 6b05a20 (la durée n'exonère qu'au 1er avril 1983) et
cd8e64b (le paquet), de la session M3, note `2026-11-05-ircantec-avant-1983.md` et son
journal de veille. Chaque texte a été rouvert ici, sans rien reprendre de la session ni de
mémoire : l'index de la DILA, LEGI et JORF récupérés dans la session (LEGI à jour de
l'incrément du 2 novembre 2026, 20261102-213929 ; JORF du 3 novembre, 20261103-002311),
interrogé par `scripts/fetch/dila_cherche.py`. Les deux moteurs ont été lancés sur les cas
de M3 et sur sept cas neufs, par `tests/js/comparer-liquidation.mjs` et son jumeau Python.
Rien n'a été modifié : ni règle, ni donnée, ni test, ni fiche.

**Verdict.** Ce que M3 a écrit est **conforme** : les citations sont exactes mot pour mot,
la table est celle des quatre rédactions de 1971 à 1978, les huit valeurs de ses tests se
refont à la main, et les deux moteurs les rendent, ainsi que sept cas neufs ; la date qui
décide est la date d'effet ; seuls l'Ircantec, l'IPACTE et l'IGRANTE ont bougé. **Écarts** :
deux moyens, sur ce que M3 affirme hors de ce qu'il a corrigé — « avant le 1er avril 1983,
la durée n'exonère pas » est plus large que le texte, qui exonère dès le 1er juillet 1982
l'agent de soixante-trois ans qui a cent cinquante trimestres (6° a) ; point 6), et, dès le
30 septembre 1978, la femme pensionnée au régime général au titre de la loi du 12 juillet
1977, celle des trente-sept ans et demi (5° ; point 7) ; le moteur abat les deux, ce que la
fiche déclarait déjà, mais la correction leur retire, sans le dire, l'exonération que les
points de l'IPACTE et de l'IGRANTE recevaient par accident ; deux faibles — l'arrêté du
27 janvier 1983, qui a écrit ces exonérations dans l'article 16, cité nulle part (point 8),
et une citation de l'analyse du Journal officiel prêtée à la rédaction de LEGI (point 1).

## 1. Les sources, à la bonne version — conforme, un écart faible

- **Les rédactions de 1971 à 1978** (LEGIARTI000006381606, du 9 février 1971 au 3 janvier
  1976 ; …607, au 26 juillet 1977 ; …608, au 30 septembre 1978 ; …609, au 31 août 1983) :
  toutes les quatre portent, mot pour mot, « AGES COEFFICIENTS AGES COEFFICIENTS 55 ans 0,43
  60 ans 0,78 56 ans 0,50 61 ans 0,83 57 ans 0,57 62 ans 0,88 58 ans 0,64 63 ans 0,92 59 ans
  0,71 64 ans 0,96 », la liste `coefficients_par_annee_d_age` des sept versions de la fiche
  qui la lisent. Les bornes des versions suivent celles de LEGI. Les citations de la fiche
  (le 1er alinéa de 1971, le « normalement » de 1976, les 3° à 5°) sont exactes.
- **La rédaction du 31 août 1983** (LEGIARTI000006381610, jusqu'au 2 octobre 1990) : l'escalier
  (« majoré de 0,017 5 par trimestre écoulé », « soit 0,78, est majoré de 0,012 5 »,
  « soit 0,88, est majoré de 0,01 »), le 6° c) (« A compter du 1er avril 1983, aux agents ou
  anciens agents justifiant d'une durée d'assurance susceptible de les faire bénéficier […]
  d'une pension au taux plein ») et le II (« A compter du 1er avril 1983 […] en assimilant à
  l'âge de soixante-cinq ans l'âge auquel l'intéressé aurait effectivement compté
  trentre-sept années et demie d'assurance ») sont cités exactement, la coquille
  « trentre-sept » comprise, qui est dans LEGI.
- **L'analyse de l'arrêté du 26 juillet 1983** (JORFTEXT000000837384, publié le 31 août
  1983) : « COEFFICIENTS DE REDUCTION VARIANT SELON L'AGE DE LIQUIDATION ET FIXES DESORMAIS
  PAR TRIMESTRE » ; exact. **Écart faible** : la note de M3 écrit que « la cinquième
  [rédaction] fixe les coefficients « désormais par trimestre » » ; les mots sont de
  l'analyse du Journal officiel, non de l'article, qui dit « par trimestre écoulé ». Le
  journal de veille, lui, les attribue bien (« (son analyse) »). Sans effet sur le modèle.
- **Les arrêtés de l'IPACTE et de l'IGRANTE** (12 décembre 1951, 17 février 1960) : absents
  de LEGI, comme M3 l'écrit. Le JORF de l'index n'en a que des titres sans texte : les
  instructions du 10 et du 15 novembre 1960 (JORFTEXT000000519147, …519148) et les statuts
  de l'IGRANTE approuvés le 31 août 1961 (JORFTEXT000000803388) ; aucune occurrence
  d'« anticipation », de « coefficient » ni d'âge. La version `ipacte_et_igrante` reste
  présumée, et la fiche le dit (`statut: supposee`, fiabilité faible) ; ces trois numéros
  du Journal officiel sont les pistes, sur papier, pour la lever.

## 2. Les valeurs, refaites à la main — conforme

L'agent des tests de M3 est né le 15 janvier 1922, ses âges comptés de février ; la date
d'effet est le premier du mois. Chaque ligne est refaite de l'article 16 de sa date, puis
lue dans les deux moteurs (« portage = jumeau » : la même valeur pour l'Ircantec, l'IPACTE
et l'IGRANTE, aux deux moteurs).

| Cas | Date d'effet | Calcul à la main | Attendu | Portage = jumeau |
|---|---|---|---|---|
| M3 : 60 ans 9 mois, 1922 | 1982-11-01 | table, ligne de 60 ans | 0,78 | 0,78 |
| M3 : 63 ans 11 mois, 1919 | 1983-01-01 | ligne de 63 ans (l'escalier : 0,88 + 7 × 0,01 = 0,95) | 0,92 | 0,92 |
| M3 : 61 ans 3 mois, 145 trimestres | 1983-05-01 | II : 65 − 5/4 = 63,75, ligne de 63 ans, 0,92 > 0,83 (61 ans) | 0,92 | 0,92 |
| M3 : 60 ans 9 mois, 1923 | 1983-11-01 | escalier : 0,78 + 3 × 0,0125 | 0,8175 | 0,8175 |
| M3 : dès 18 ans, 60 ans 9 mois | 1982-11-01 | aucune exonération avant le 6° c) | 0,78 | 0,78 |
| M3 : dès 18 ans, 61 ans 1 mois | 1983-03-01 | ligne de 61 ans | 0,83 | 0,83 |
| M3 : dès 18 ans, 61 ans 2 mois | 1983-04-01 | 6° c) | aucun | aucun |
| M3 : 1905, 62 ans, IPACTE et IGRANTE | 1967-02-01 | table présumée, ligne de 62 ans | 0,88 | 0,88 |
| Neuf : 1923, dès 25 ans, 60 ans 4 mois, 141 trimestres | 1983-06-01 | II : 65 − 9/4 = 62,75, ligne de 62 ans, 0,88 > 0,78 | 0,88 | 0,88 |
| Neuf : 1923, 60 ans 6 mois | 1983-08-01 | dernier mois de la table | 0,78 | 0,78 |
| Neuf : 1923, 60 ans 7 mois | 1983-09-01 | premier mois de l'escalier : 0,78 + 2 × 0,0125 | 0,805 | 0,805 |
| Neuf : 1915, 60 ans 6 mois | 1975-08-01 | ligne de 60 ans | 0,78 | 0,78 |
| Neuf : 1915, dès 18 ans, 64 ans 11 mois | 1980-01-01 | ligne de 64 ans, aucune durée | 0,96 | 0,96 |
| Neuf : 1923, dès 18 ans, 60 ans 6 mois | 1983-08-01 | 6° c) | aucun | aucun |
| Neuf : 1923, dès 33 ans, 60 ans 6 mois | 1983-08-01 | moins de 130 trimestres, pas de II | 0,78 | 0,78 |

Les trimestres que le II lit, ceux que le moteur compte, se recomptent : 145 au 1er mai
1983 pour l'agent entré à vingt-cinq ans en février 1947 (4 en 1947, 140 de 1948 à 1982, le
premier trimestre de 1983, échu avant la date d'effet), 141 au 1er juin 1983 pour celui de 1923 entré en février 1948 ; la durée
requise lue est 150. Le plafond de l'écart déclaré, « jusqu'à 3,75 points », se refait :
de un à vingt trimestres manquants, la table à l'âge assimilé et l'escalier diffèrent au
plus de 0,0375, à treize et à dix-sept (0,8675 contre 0,83 ; 0,8175 contre 0,78). Les
« dix-sept écarts déclarés » qui s'en vont du test se comptent : sept versions × deux
paramètres, plus trois versions de la durée.

## 3. Les deux moteurs — conforme

`python -m pytest tests/test_ircantec.py` : 19 réussis ; sous `PRESOMPTIONS_DECALEES=1` :
19 réussis, les deux tests neufs compris, que la garde de `conftest.py` ne saute pas (ils
appellent node par `_deux_moteurs`, qu'elle ne voit pas) et ne dépendent d'aucune
présomption : la date de naissance y est entière. Les quinze cas du point 2 et les quatre
des points 6 et 7 : portage et jumeau rendent la même valeur, aux trois régimes. Le code
(`liquider.py`, `bareme_ircantec`, `coefficient_par_annee_d_age` ; `liquider.js`,
`baremeIrcantec`, `coefficientParAnneeDAge`) est le même aux deux moteurs, ligne pour
ligne.

## 4. Ce que le texte ne tranche pas — conforme

Le renvoi du II au « paragraphe Ier » d'avril à août 1983 est déclaré en approximation de
la version `structure_financiere_1983`, avec sa population (130 à 149 trimestres) et son
plafond, refait au point 2. La table de l'IPACTE et de l'IGRANTE d'avant 1971 est présumée
et déclarée (point 1). La lecture à l'âge révolu (« 60 ans » pour qui a soixante ans et neuf
mois) n'est pas déclarée en approximation : c'est le sens courant d'un âge en années, et la
fiche l'écrit dans le droit de la version ; rien ne la contredit dans les textes lus.

## 5. La date qui décide — conforme

`bareme_ircantec` lit la fiche à `date_d_effet(carriere)` (`droit/commun.py`, l. 42 ;
`commun.js`, l. 38), le premier jour du mois de la liquidation, et la fiche déclare
`dates_qui_decident: [liquidation.date_effet]`. Les bornes s'éprouvent au mois près : mars
1983 abat, avril exonère ; août 1983 lit la table, septembre l'escalier (point 2). Les
points de l'IPACTE et de l'IGRANTE se liquident sous la version de la date d'effet de la
pension, non sous celle de leur acquisition.

## 6. Écart moyen : le 6° a), soixante-trois ans et cent cinquante trimestres dès le 1er juillet 1982

- **Le texte.** L'article 16 (LEGIARTI000006381610) n'applique pas le coefficient : « 6° a)
  A compter du 1er juillet 1982 aux agents visés aux articles L. 351-16 et L. 351-17 du code
  du travail remplissant les conditions fixées par l'article 9, alinéa 2, de l'ordonnance du
  26 mars 1982 » ; l'article 9 de l'ordonnance n° 82-270 (LEGIARTI000006275868) : « les
  personnels visés aux articles L. 351-16 et L. 351-17 du code du travail, âgés d'au moins
  soixante-trois ans et justifiant d'une durée d'assurance de 150 trimestres, bénéficient,
  dès le 1er juillet 1982, du taux plein ». Les analyses du Journal officiel disent qui :
  « AU BENEFICE DES ASSURES AYANT 63 ANS ET 150 TRIMESTRES D'ASSURANCE […] (A COMPTER DU
  01-07-1982) » (arrêté du 27 janvier 1983, JORFTEXT000000654120) ; « A COMPTER DU
  01-07-1982: AUX AGENTS NON TITULAIRES AYANT AU MOINS 63 ANS » (arrêté du 26 juillet 1983).
  Les articles L. 351-16 et L. 351-17 du code du travail de 1982 ne sont pas dans l'index :
  que ces « personnels » soient les agents non titulaires repose sur cette seconde analyse.
- **Ce que rendent les moteurs**, à un agent né en 1919, au travail dès dix-huit ans :
  0,92 en août 1982 (63 ans 6 mois, 182 trimestres), 0,92 en janvier 1983 (63 ans 11 mois,
  184), 0,96 en mars 1983 (64 ans 1 mois, 184), aux trois régimes, portage et jumeau ; le
  texte n'en sert aucun.
- **Ce que la correction a changé.** Avant elle, la période de l'Ircantec ouverte le
  1er janvier 1983 et celle de l'IPACTE et de l'IGRANTE, qui portent la durée, exonéraient
  ces agents de janvier à mars 1983 (l'Ircantec) et dès 1951 (l'IPACTE et l'IGRANTE) : à tort
  pour la plupart, à raison pour eux. M3 a retiré l'exonération à tous, sans nommer ceux-là.
  Sa note (« n'exonère à la durée (6° c) […] qu'« A compter du 1er avril 1983 » ») est exacte
  du 6° c) ; mais la docstring de son test, « Avant le 1er avril 1983, la durée d'assurance
  n'exonère pas », et la note des fiches de l'IPACTE et de l'IGRANTE (« L'abattement
  d'anticipation ne s'applique « à l'âge seul » que jusqu'au 1er avril 1983 ») disent plus
  que le texte. Ses tests ne sont pas faux : leur agent a soixante et un ans.
- **Pourquoi moyen.** La fiche déclarait déjà l'écart (approximation des versions
  `arrete_de_1970` à `retraite_anticipee_2004` : « ni les bénéficiaires des mesures de 1982 :
  il les abat », « jusqu'à 22 points de coefficient de moins ; non mesuré, des populations
  rares ») ; mais ces agents sont le cœur de l'Ircantec à soixante-trois et soixante-quatre
  ans, « rares » n'est pas mesuré, et la condition est lisible dans le texte — soixante-trois
  ans, cent cinquante trimestres, du 1er juillet 1982 au 31 mars 1983 —, donc servable. Au
  plus 8 points (0,92), sur neuf mois de liquidations.

## 7. Écart moyen : le 5° de 1978, la femme de la loi du 12 juillet 1977

- **Le texte.** La rédaction du 30 septembre 1978 (LEGIARTI000006381609) n'applique pas le
  coefficient « 5° Aux femmes qui bénéficient d'une pension de vieillesse du régime général
  de sécurité sociale attribuée dans les conditions fixées par la loi n° 77-774 du 12 juillet
  1977 » ; cette loi tend « à accorder aux femmes assurées au régime général de la sécurité
  sociale atteignant l'âge de soixante ans la pension de vieillesse au taux normalement
  applicable à soixante-cinq ans », pour les femmes « qui réunissent trente-sept ans et demi
  d'assurance » (décret n° 78-319 du 8 mars 1978, titre et article 1er,
  LEGIARTI000006762125, son application en Alsace-Moselle). Une exonération à la durée,
  donc, de 1978 au 31 mars 1983.
- **Ce que M3 écrit** : « Les quatre premières [rédactions] donnent la même table, et aucune
  durée n'y exonère » ; inexact pour la quatrième.
- **Ce que rendent les moteurs**, à une femme née en 1920, au travail dès dix-huit ans,
  partie à soixante ans en février 1980 avec 168 trimestres : 0,78 aux trois régimes,
  portage et jumeau ; avant la correction, les points de l'IPACTE et de l'IGRANTE n'avaient
  aucun coefficient. Le régime général du modèle lui sert 25 % (« taux 25.000 % ×
  140/150 ») : il ne sert pas non plus la loi de 1977, et l'exonération de l'Ircantec, qui
  suit la pension du régime général, ne peut s'y brancher qu'après lui.
- **Pourquoi moyen** : même raison qu'au point 6, l'écart était déclaré (« ni la femme de
  trente-sept ans et demi d'assurance de la loi de 1977 […] il les abat ») ; mais la note
  affirme le contraire du texte, et la population — les femmes de trente-sept ans et demi
  parties à soixante ans de 1979 à 1983 — n'est pas rare.

## 8. Écart faible : l'arrêté du 27 janvier 1983, cité nulle part

L'arrêté du 27 janvier 1983 (JORFTEXT000000654120, JO du 5 février 1983, « RECT. JO DU
12-03-1983 ») porte « MODIFICATION DE L'ART. 16 (AL. 2) DE L'ARRETE DU 30-12-1970 » : les
exonérations des 63 ans et 150 trimestres et des demandeurs d'emploi « (A COMPTER DU
01-07-1982) », du taux plein du régime général « (A COMPTER DU 01-04-1983) », et de la
cessation anticipée d'activité. LEGI n'a pas de rédaction de l'article à cette date
(…609 court jusqu'au 31 août 1983), et la fiche attribue le 6° au seul arrêté du 26 juillet
1983 (versions `ordonnance_du_26_mars_1982` et `structure_financiere_1983`, « en_vigueur:
1983-08-31 »). Sans effet sur les valeurs : le 1er avril 1983 reste la date du 6° c), et le
II, que l'analyse de janvier ne mentionne pas, reste du 31 août. Mais la source qui a publié
le 6° c), et ses dates, est à citer ; son texte intégral, et le rectificatif du 12 mars, sont
à lire au Journal officiel : l'index n'en a que l'analyse.

## 9. Rien d'autre n'a bougé — conforme

`git diff 9fcd8a1 cd8e64b` : treize fichiers, tous de l'Ircantec, de l'IPACTE et de
l'IGRANTE, ou fabriqués. Dans le paquet, `regimes` ne change que les notes de la première
période de `ipacte`, `ircantec` et `igrante`, et `fiches_datees` gagne
`coefficient_anticipation_ircantec` ; le reste est `agregats` et `bilan_equilibre`, que
GitHub refait : le cumul du coût passé du droit actuel ne bouge pas ; ceux des scénarios
notionnels de 634,8 à 1 370,1 (l'unité du paquet ; environ 0,02 %), celui de la
garantie des libéraux de −3,0 ; au README, « d'une unité » comme M3 l'écrit :
`verifier_prose.py` y lit encore 2 762 au scénario 2 et 6 385 aux scénarios 4 et 6, quand
la mesure en donne 2 763 et 6 386, chiffres ancrés que GitHub récrit. Aucun témoin n'est touché. Le nouveau chemin du moteur ne
s'ouvre qu'à `abattement_points: ircantec` ; ailleurs, `bareme_ircantec` rend `None` et le
calcul est celui d'avant. Après le 31 août 1983, la version porte la durée et pas de table :
rien ne change (l'escalier de septembre 1983, point 2).

## Hors du périmètre, à transmettre

Le régime général du modèle, aux mêmes dates : l'article 9 de l'ordonnance n° 82-270 sert
« dès le 1er juillet 1982 » le taux plein aux « personnels visés aux articles L. 351-16 et
L. 351-17 du code du travail » de soixante-trois ans et cent cinquante trimestres, quand le
modèle sert 42,5 % à l'agent du point 6 en août 1982 ; et la loi du 12 juillet 1977, dont
la femme du point 7 n'a pas le taux. Ni l'un ni l'autre n'est l'objet de M3 ; les deux sont
à lire par la zone du régime général, les articles L. 351-16 et L. 351-17 de 1982 et le
calendrier de la loi de 1977 d'abord.
