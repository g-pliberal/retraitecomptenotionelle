# Relecture des corrections de la relecture R-M3d (file R-M3-bis)

File R-M3-bis, le 5 novembre 2026 : relecture indépendante du commit cc627e8 de la session
M3-bis (paquet repris par d8124ff), de sa note `2026-11-05-corrections-de-la-relecture-r-m3d.md`
et de son journal de veille `2026-11-05-action-130-corrections-r-m3d.yaml`, contre la relecture
qu'il corrige (`2026-11-05-relecture-ircantec-avant-1983.md`, points 1, 6, 7 et 8). Chaque
texte a été rouvert ici, sans rien reprendre de la session ni de mémoire : l'index de la DILA,
LEGI et JORF récupérés dans la session (LEGI à jour de l'incrément du 2 novembre 2026,
20261102-213929 ; JORF du 3 novembre, 20261103-002311), interrogé par
`scripts/fetch/dila_cherche.py`. Les citations de la fiche ont été confrontées à leur source
par programme, morceau par morceau. Les deux moteurs ont été lancés sur les quatorze cas et
sur onze cas neufs, par `tests/js/comparer-liquidation.mjs` et son jumeau Python, aussi sous
`PRESOMPTIONS_DECALEES=1`. Rien n'a été modifié : ni règle, ni donnée, ni test, ni fiche.

**Verdict.** Ce que M3-bis a écrit est **conforme** pour l'essentiel : les citations sont
exactes mot pour mot, les quatorze valeurs se refont à la main, les deux moteurs les rendent,
les trois dates de bascule sont les bonnes, et rien d'autre que l'Ircantec, l'IPACTE et
l'IGRANTE ne bouge. Restent un écart **moyen** et trois **faibles**. Le moyen porte sur la
question posée : **le 6° a) après le 1er avril 1983**. Aucun texte normatif lu ne lui donne
de terme : la lettre de l'article en vigueur jusqu'en 2003 le sert. Le modèle ne le sert pas,
sur la foi du seul rapport au Président de la République, et sa fiche dit « le texte ne
tranche pas » (point 6). Les trois faibles : un texte normatif manqué, l'article 13 du
décret n° 82-628, que la note et le journal disent absent de l'index (point 5) ; une
citation du rapport dont les deux morceaux sont intervertis (point 1) ; une note des fiches
de l'IPACTE et de l'IGRANTE qui oublie le 6° b) (point 7).

## 1. Les sources, à la bonne version — conforme, un écart faible

- **L'article 16 de l'arrêté du 30 décembre 1970.** LEGIARTI000006381609, du 30 septembre
  1978 au 31 août 1983 : la table « 60 ans 0,78 56 ans 0,50 61 ans 0,83 57 ans 0,57 62 ans
  0,88 58 ans 0,64 63 ans 0,92 59 ans 0,71 64 ans 0,96 », et le « 5° Aux femmes qui
  bénéficient d'une pension de vieillesse du régime général de sécurité sociale attribuée
  dans les conditions fixées par la loi n° 77-774 du 12 juillet 1977 », mot pour mot ; le
  licenciement y est bien le 6°. LEGIARTI000006381610, du 31 août 1983 au 2 octobre 1990 : le
  6° a) et b) cités par la fiche, mot pour mot, et le 5° de 1978 n'y est plus (le 4° y devient
  « Aux mères de famille […] dans les conditions prévues par l'article L. 332 »).
  LEGIARTI000006381611, du 2 octobre 1990 au 1er janvier 2004 : le même 6° a) et b), mot pour
  mot. LEGIARTI000006381612, du 1er janvier 2004 : plus de « 1er juillet 1982 », plus
  d'« ordonnance du 26 mars 1982 » ; le 6° a) y est l'article L. 351-1-1. La note dit vrai.
- **L'ordonnance n° 82-270, article 9** (LEGIARTI000006275868, en vigueur du 1er juillet 1982,
  sans terme dans LEGI) : la citation de la fiche est le texte entier, exact, en un seul
  paragraphe de trois phrases.
- **Le rapport au Président de la République** (LEGIARTI000006759661, du 1er avril 1983) : les
  deux passages cités sont exacts. **Écart faible** : la fiche (version
  `ordonnance_du_26_mars_1982`) les joint par « […] » dans l'ordre inverse du texte. Le passage
  des « 150 trimestres obtenue en totalisant les périodes cotisées et assimilées dans un ou
  plusieurs régimes de base quels qu'ils soient » vient, dans le rapport, avant celui qui
  dit qu'« elle entrera en vigueur, selon des modalités spécifiques, dès le 1er juillet
  1982 ». Aucun mot n'est faux ; l'ordre l'est. La note, qui les cite séparément, est juste.
- **Le décret n° 45-0179, article 70-2** : LEGIARTI000006760658, du 16 mars 1978 au 23 juillet
  1982, porte le c) cité, mot pour mot. LEGIARTI000006760659, du 23 juillet 1982 au
  21 décembre 1985, n'a plus de c), ni le mot « femmes ».
- **Le décret n° 78-319, article 1er** (LEGIARTI000006762125) : « femmes assurées qui
  réunissent trente-sept ans et demi d'assurance dans l'ex-régime local […] et dans le régime
  général ou dans ces régimes et celui des salariés agricoles », soixante-trois ans en 1978,
  soixante ensuite : la même règle, comme le dit la note.
- **Les analyses du Journal officiel.** Celle de la loi n° 77-774 (JORFTEXT000000522844) donne
  le titre cité. Celle de l'arrêté du 27 janvier 1983 (JORFTEXT000000654120, du 5 février
  1983) : la citation est exacte, et le « […] » n'omet que la phrase sur les ordonnances
  appliquées et le nom du régime. Celle de l'arrêté du 26 juillet 1983 (JORFTEXT000000837384)
  porte « FIXES DESORMAIS PAR TRIMESTRE », et la rédaction de LEGI (…610) n'a pas le mot
  « désormais », mais « majoré de 0,017 5 par trimestre écoulé ». L'écart 4 de R-M3d est donc
  bien réglé.
- **Ce que l'index n'a pas.** Les articles L. 351-16 et L. 351-17 du code du travail : absents,
  sous ce code comme sous tout autre. Le texte de l'arrêté du 27 janvier 1983 et son
  rectificatif du 12 mars 1983 : absents, le JORF de 1983 n'ayant sur l'Ircantec que des
  analyses. La loi n° 77-774 : son titre et son article 2 sont dans LEGI
  (LEGITEXT000006068610, LEGIARTI000006273117, l'Alsace-Moselle), mais pas le texte de son
  article 1er, que LEGI réduit à « a modifié les dispositions suivantes »
  (LEGIARTI000006758755). La fiche, qui écrit « le texte de son article 1er, qui modifie
  L. 332, n'est pas dans l'index », est exacte. Le décret n° 82-628 : voir le point 5.

## 2. Les valeurs, refaites à la main — conforme

Les âges se comptent du mois qui suit la naissance, au 15 janvier : soixante-trois ans et
quatre mois pour un homme de 1919, c'est juin 1982. Les durées sont comptées ici en années
pleines, une borne basse ou haute qui suffit à trancher. Entre crochets, ce que le modèle
compte.

| Cas | Date d'effet | Refait ici | Attendu |
|---|---|---|---|
| Homme de 1919, 63 ans 4 mois | 1982-06-01 | avant le 1er juillet 1982 ; table, 63 ans | 0,92 |
| Homme de 1919, 63 ans 5 mois | 1982-07-01 | 1938 à 1981 : 44 × 4 = 176 ≥ 150 [182] ; dernière ligne contractuel | aucun |
| Homme de 1919, 63 ans 6 mois | 1982-08-01 | de même | aucun |
| Homme de 1919, 64 ans 1 mois | 1983-03-01 | de même, avant le 1er avril 1983 ; la table eût donné 0,96 | aucun |
| Homme de 1919, agent dès 30 ans | 1982-08-01 | au plus 4 (1949) + 32 × 4 (1950 à 1981) + 4 (1982) = 136 < 150 [134] | 0,92 |
| Homme de 1920, 62 ans 6 mois | 1982-08-01 | 62 < 63 ; table, 62 ans | 0,88 |
| Homme de 1919, au privé depuis 1975 | 1982-08-01 | ancien agent, pas demandeur d'emploi : ni 6° a), ni 6° b) | 0,92 |
| Femme de 1920, 60 ans | 1980-02-01 | effet après 1978 : 60 ans ; 1939 à 1944, 6 × 4, puis 1945 à 1979, 35 × 4 : 164 ≥ 150 [168] | aucun |
| Homme de 1920, 60 ans | 1980-02-01 | le 5° nomme les femmes ; table, 60 ans | 0,78 |
| Femme de 1920, au travail à 25 ans | 1980-02-01 | au plus 4 + 34 × 4 + 4 = 144 < 150 [140] | 0,78 |
| Femme de 1915, 63 ans 8 mois | 1978-10-01 | effet en 1978 : 63 ans ; 1934 à 1944, 11 × 4, puis 1945 à 1977, 33 × 4 : 176 [183] | aucun |
| Femme de 1915, 63 ans 7 mois | 1978-09-01 | avant le 30 septembre 1978 ; table, 63 ans | 0,92 |
| Femme de 1918, 60 ans 8 mois | 1978-10-01 | effet en 1978 : 63 ans exigés, 60 < 63 ; table, 60 ans | 0,78 |
| Femme de 1922, 61 ans 1 mois | 1983-03-01 | 60 ans ; 1941 à 1944, 4 × 4, puis 1945 à 1982, 38 × 4 : 168 [172] | aucun |

Les quatorze valeurs de la note et du test sont celles-ci. Les paramètres de la fiche aussi :
trente-sept ans et demi font 150 trimestres, et `ages: [[1978, 63], [1979, 60]]` est le c) de
l'article 70-2. `{age: 63, trimestres: 150}` est l'article 9, deuxième phrase.

**Les trois bornes.** Le 30 septembre 1978 est la date d'entrée en vigueur de …609, et la
version `femmes_de_la_loi_de_1977` s'ouvre ce jour. Le 1er juillet 1982 est le « A compter
du 1er juillet 1982 » du 6° a), et la version `ordonnance_du_26_mars_1982` s'ouvre ce jour.
Le 31 mars 1983 est la veille du « A compter du 1er avril 1983 » du 6° c), et cette version
se ferme le 1er avril. Onze cas neufs, posés à la main, les encadrent :

| Cas | Date d'effet | Attendu | Servi |
|---|---|---|---|
| Femme de 1918, 60 ans 10 mois (1978 : 63 ans exigés) | 1978-12-01 | 0,78 | 0,78 |
| Femme de 1918, 60 ans 11 mois (après 1978 : 60 ans) | 1979-01-01 | aucun | aucun |
| Femme de 1922, 61 ans 2 mois (6° c), 168 trimestres) | 1983-04-01 | aucun | aucun |
| Femme de 1922, 61 ans 6 mois (6° c), le 5° encore écrit dans …609) | 1983-08-01 | aucun | aucun |
| Agent de 1919, 64 ans 2 mois (6° c)) | 1983-04-01 | aucun | aucun |
| Agent de 1920, 63 ans (6° a)) | 1983-02-01 | aucun | aucun |
| Femme fonctionnaire de 1938 à 1955, puis contractuelle : régime général < 150, tous régimes ≥ 150 | 1980-02-01 | 0,78 | 0,78 |
| Femme revenue au privé en 1975 (le 5° ne demande pas d'être agent) | 1980-02-01 | aucun | aucun |
| Femme au travail à 25 ans, deux enfants (la majoration de durée, déclarée) | 1980-02-01 | aucun, tel que déclaré | aucun |
| Agent de 1936, 63 ans, un trimestre de moins que sa génération (régime général à 48,75 %) | 1999-02-01 | voir le point 6 | 0,99 |
| Agent de 1938, 64 ans, trois trimestres de moins que sa génération (46,25 %) | 2002-02-01 | voir le point 6 | 0,97 |

Les cas d'avril à août 1983 vérifient ce que la note affirme : « Après le 1er avril 1983, le
6° c) la contient ». La femme de 1977 et l'agent de soixante-trois ans y sont servis sans
coefficient par le 6° c), y compris pendant les cinq mois où …609, qui porte encore le 5°,
est la rédaction en vigueur.

## 3. Les deux moteurs — conforme

`tests/test_ircantec.py` : 21 réussis. Sous `PRESOMPTIONS_DECALEES=1`, encore 21 réussis.
Les deux tests neufs n'y sont pas sautés : leur source n'écrit pas « node », que cherche la
garde de `conftest.py`. Le jumeau y tourne décalé, le portage non, et les deux rendent les
quatorze valeurs. Les onze cas neufs donnent la même valeur au portage et au jumeau, aux
trois régimes, et de même au jumeau décalé. Le code des deux moteurs est le même, ligne à
ligne : `exonereParLAgeEtLaDuree` et `exonere_par_l_age_et_la_duree`, `agentALaLiquidation`
et `agent_a_la_liquidation`.

## 4. Rien d'autre n'a bougé — conforme

Le nouveau chemin ne s'ouvre que si `bareme_ircantec` rend une version. Il n'en rend que pour
une période à `abattement_points: ircantec`, ce que seules l'Ircantec, l'IPACTE et l'IGRANTE
portent : `coefficient_anticipation_ircantec` n'est nommé que par leurs trois fiches. Les
deux paramètres ne sont non nuls que dans les versions `femmes_de_la_loi_de_1977` et
`ordonnance_du_26_mars_1982`, du 30 septembre 1978 au 1er avril 1983. `durees`, passé de
plus à `abattement_points`, n'est lu que là. Les fiches de l'IPACTE et de l'IGRANTE ne
changent que d'une note. Les témoins refaits par d8124ff (`pages.json`, `simulations.json`)
n'ont aucune ligne qui nomme l'Ircantec, l'IPACTE ou l'IGRANTE. Le renvoi daté ajouté au bout
de la note de M3 ajoute une ligne et n'en récrit aucune.

## 5. Écart faible : l'article 13 du décret n° 82-628, présent dans LEGI, non cité

La note (« le décret n° 82-628 du 21 juillet 1982, qui l'a récrit, n'a pas son texte dans
l'index »), la fiche (« ni celui du décret n° 82-628 ») et le journal (« les articles du
décret n° 82-628 […], sans texte dans l'index ») n'ont cherché que dans JORF. LEGI a ses
articles 8, 9 et 13 à 16 (LEGITEXT000006063841). Le texte qui récrit l'article 70-2 n'y est,
lui, que par son résultat, …659. Trois de ces articles touchent la correction.

- **L'article 13** (LEGIARTI000006763435, en vigueur du 23 juillet 1982, sans terme) : « La
  durée d'assurance dont doivent justifier les personnels visés à l'article 9, deuxième
  alinéa, de l'ordonnance du 26 mars 1982 susvisée pour bénéficier, dès le 1er juillet 1982,
  du taux plein peut avoir été accomplie dans le régime général ou dans ce régime et un ou
  plusieurs autres régimes de base obligatoires. » C'est la source normative de la durée
  tous régimes du 6° a), que la fiche ne tient que du rapport. Il confirme aussi que le
  « deuxième alinéa » de l'article 9 est sa deuxième phrase.
- **L'article 14** (LEGIARTI000006763436) : « Les dispositions du troisième alinéa de
  l'article 9 […] s'appliquent aux assurés qui sont en situation de chômage constaté à la
  date d'entrée en jouissance de leur pension et qui étaient inscrits comme demandeur
  d'emploi à la date du 1er février 1982 ». C'est le 6° b), non servi, déclaré ; la condition
  de chômage à la date d'effet est à ajouter à sa déclaration.
- **L'article 15** (LEGIARTI000006763437) nomme les « allocations aux travailleurs privés
  d'emploi visées aux articles […] L. 351-16 et L. 351-17 du code du travail ». Ces deux
  articles, absents de l'index, indemnisent donc la perte d'emploi. Les « personnels » qu'ils
  visent pourraient comprendre l'agent qui a perdu son emploi et qu'ils indemnisent. Le
  modèle, qui demande une dernière ligne d'emploi à l'Ircantec, abat cet agent. À verser à
  la déclaration « qui est agent ».

Sans effet sur les valeurs : le modèle compte déjà la durée tous régimes. Faible, parce que
la règle servie est la bonne. Mais une règle tenue d'un rapport, quand un décret la dit, se
justifie moins bien par écrit.

## 6. Écart moyen : le 6° a) après le 1er avril 1983

**La question** : le modèle ne sert le 6° a) que jusqu'au 31 mars 1983. Est-ce la lecture
la plus prudente, ou le texte en vigueur après 1983 tranche-t-il ?

- **Ce que disent les textes en vigueur.** L'article 16 garde le 6° a) mot pour mot du
  31 août 1983 au 1er janvier 2004 (…610, …611). Il a une date de début, « A compter du
  1er juillet 1982 », et pas de fin. Il renvoie aux « conditions fixées par l'article 9,
  alinéa 2 » : soixante-trois ans, 150 trimestres, tous régimes (décret n° 82-628,
  article 13). L'article 9 de l'ordonnance (LEGIARTI000006275868) et l'article 13 du décret
  (LEGIARTI000006763435) sont
  sans terme dans LEGI. Les deux analyses du Journal officiel, du 27 janvier et du 26 juillet
  1983, n'en donnent pas non plus : « (A COMPTER DU 01-07-1982) », « A COMPTER DU
  01-07-1982: AUX AGENTS NON TITULAIRES AYANT AU MOINS 63 ANS ». Le texte oppose même les
  deux alinéas. Le troisième, celui des demandeurs d'emploi (6° b), est borné : « à
  compter du 1er juillet 1982 et jusqu'au 1er avril 1983 ». Le deuxième ne l'est pas.
- **Ce qui le borne.** Rien de normatif. Le rapport au Président de la République dit que
  l'ordonnance « entrera en vigueur, selon des modalités spécifiques, dès le 1er juillet
  1982 » pour ces agents. Le « Toutefois » de l'article 9 déroge à la date d'entrée en
  vigueur, le 1er avril 1983. Ces deux éléments en font une anticipation, sans objet après
  cette date tant que la durée requise est de 150 trimestres. Que la rédaction de 2004 l'ôte
  le dit caduc, sans dire depuis quand.
- **Ce qui reste à lire.** Deux pièces trancheraient, et l'index n'a ni l'une ni l'autre.
  D'abord, les articles L. 351-16 et L. 351-17 du code du travail après sa refonte de 1984 :
  s'ils ne visaient plus ces agents, le 6° a) perdait son objet. Ensuite, la pratique de
  l'Ircantec de 1994 à 2003.
- **Ce que rend le modèle.** Un agent né en 1936, encore agent, a 63 ans en février 1999,
  un trimestre de moins que la durée de sa génération (le régime général du modèle lui sert
  48,75 %) : 0,99 aux trois régimes. Un agent né en 1938, à 64 ans en
  février 2002, à qui en manquent trois (46,25 %) : 0,97. La lettre ne leur met pas de
  coefficient. L'écart mesuré, 1 et 3 points, est sous la borne de « huit points » que la
  fiche déclare.
- **Le verdict.** La lecture de M3-bis est défendable, et elle est déclarée, avec son effet.
  Mais elle n'est pas la plus prudente au regard de la règle du scénario 1, le droit en
  vigueur à la date d'effet. La lettre de l'article en vigueur, et l'opposition des deux
  alinéas de l'article 9, servent le 6° a) jusqu'au 31 décembre 2003. La lecture du modèle
  ne s'appuie que sur un rapport, qui n'est pas normatif. La déclaration, « le texte ne
  tranche pas », dit moins que les textes. Elle devrait dire que la lettre sert le 6° a), que
  le modèle ne le sert pas sur la foi du rapport, et quelles pièces trancheraient. Il faut
  alors soit servir la lettre jusqu'au 31 décembre 2003, soit garder la lecture du rapport
  et récrire la déclaration en ces termes. C'est un choix de lecture, à faire par qui tient
  le scénario 1. Moyen, comme R-M3d l'a jugé du 6° a) d'avant 1983 : la condition est
  lisible dans le texte en vigueur, donc servable. L'effet est petit et la population étroite :
  des agents des générations 1934 à 1940, encore en fonction à soixante-trois ou soixante-quatre
  ans, entre 150 trimestres et la durée de leur génération.

## 7. Écart faible : la note des fiches de l'IPACTE et de l'IGRANTE

Les deux fiches de régime disent désormais que l'article 16 « n'exonère avant cette date, à
l'âge et à la durée, que la femme de la loi du 12 juillet 1977, dès le 30 septembre 1978
(5°), et l'agent de soixante-trois ans et de cent cinquante trimestres, dès le 1er juillet
1982 (6° a) ». Le « que » exclut à tort le 6° b). Lui aussi exonère à l'âge et à la durée
avant le 1er avril 1983 : soixante ans et quarante trimestres, l'ancien agent demandeur
d'emploi au 1er février 1982 (article 9, troisième phrase). Le modèle ne le sert pas, ce que
la fiche des coefficients déclare. Sans effet sur les valeurs.

## 8. Ce que le texte ne tranche pas — conforme, sauf le point 6

Les autres déclarations de M3-bis sont dans la fiche, avec leur effet :
- le 6° b), non servi ;
- la qualité d'agent lue à la dernière ligne ;
- la femme de 1977 de juillet 1982 à mars 1983, sans l'article 70-2, c), dans LEGI ;
- la durée « dans le régime général » comptée avec les assurances sociales d'avant 1945
  et la majoration pour enfants ;
- la pension du régime général tenue pour acquise.

Les cas neufs du point 2 montrent que le modèle fait ce qu'elles disent. La femme dont la
durée tous régimes atteint 150 trimestres, mais pas celle du régime général, garde son
coefficient. La femme revenue au privé n'en a pas, puisque le 5° ne demande pas d'être
agent. Avec la majoration pour enfants, le modèle exonère, comme déclaré.

## Hors du périmètre, à transmettre

Ce que M3-bis transmet au régime général : ni le taux plein de l'article 9 à l'agent de
soixante-trois ans, ni celui de la loi de 1977. L'article 13 du décret n° 82-628 en dit la
durée, tous régimes, et sert là aussi.

Sources : LEGI LEGIARTI000006381609, 610, 611, 612 ; LEGIARTI000006275868 ;
LEGIARTI000006759661 ; LEGIARTI000006760658, 659 ; LEGIARTI000006762125 ;
LEGIARTI000006763432, 433, 435 à 438 et LEGITEXT000006063841 (décret n° 82-628) ;
LEGITEXT000006068610, LEGIARTI000006273117, LEGIARTI000006758755 (loi n° 77-774). JORF
JORFTEXT000000522844, 654120, 837384, 699275.
