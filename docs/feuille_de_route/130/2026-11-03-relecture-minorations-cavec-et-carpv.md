# Relecture des minorations de la CAVEC et de la CARPV

File R-E, le 3 novembre 2026 : relecture indépendante du commit 9020e7b (session E, note
`2026-11-03-carte-des-fiches-minorations-cavec-et-carpv-lues-au-droit.md`, fiches
`cavec_minoration_age_seul` et `carpv_minoration_age_seul`, tests de
`tests/test_sections_liberales.py` et `tests/test_carte.py`). Chaque texte a été rouvert
ici, dans les index JORF (à jour au 3 novembre 2026, 00:23) et LEGI (au 2 novembre,
21:39) récupérés par `dila_index.py --recuperer`, sans rien reprendre de la session ni de
mémoire. Rien n'a été modifié : ni règle, ni donnée, ni fiche, ni test.

**Verdict : conforme pour les citations, les dates, les âges, le taux et les calculs ; trois
écarts moyens, sept faibles.** Toutes les citations sont exactes mot pour mot, et les dates
d'effet justes. **Moyens** : la réversion des deux caisses n'est pas « servie coefficient
compris » par le moteur, elle n'est pas servie du tout (point 6) ; l'arrêté de la CARPV du
2 novembre 2015, classé sans effet, récrit l'alinéa de l'inapte (point 3) ; le bloc
« Reprise » a perdu la décision de la proposition que le README laisse au propriétaire, et
la note des décisions ne la porte pas (point 9). **Faibles** : un au point 2, un au point 4,
trois au point 5, la portée de l'inapte au point 6, un au point 7.

## 1. Les citations de la CAVEC

| Ce que la fiche cite | Texte rouvert | Verdict |
|---|---|---|
| Statuts de 2008, article 3.13 | JORFARTI000018197778, publié le 1er mars 2008 | mot pour mot |
| Article 3.15 (« premier jour du trimestre civil suivant la demande ») | même annexe | exact |
| Article 3.17 (« sans application du coefficient de réduction prévu à l'article 3.13 ») | même annexe | exact |
| Arrêté du 22 février 2008, article 1er (approuve les articles 3.1 à 3.20, sans date) | JORFARTI000018197775 ; l'article 2 n'est que l'exécution | exact |
| Statuts de 2018, partie 2, article 12 | JORFARTI000037363871, publié le 4 septembre 2018 | mot pour mot |
| Article 16 (50 % avant le 1er janvier 2009, 60 % après, sans le coefficient) | même annexe | exact |
| Arrêté du 19 juin 2019, annexe, II, 7° | JORFARTI000038689131 ; le 7° est bien au II (« La partie 2 est ainsi modifiée ») | mot pour mot |
| Règlement de 2026, article 1.1.3 | JORFARTI000054435943 et LEGIARTI000054437585, en vigueur au LEGI « 2026-07-18 → » | mot pour mot |
| Règlement de 2026, article 1.2.2 | même annexe | exact |
| Décret n° 2026-418, article 8, 7° (a) et article 30 | JORFARTI000054153497, JORFARTI000054153813 | exact |
| Arrêté du 13 mai 1994 : « sera publié intégralement au Bulletin officiel » | JORFARTI000001391556 | exact |
| CAVEC, « le livre des 70 ans », 1983 | PDF téléchargé ici, 80 564 762 octets, sha256 f37b161d…d030 | exact, à l'ellipse près |

Les huit arrêtés dits sans effet (2010, deux en 2012, 2013, 2014, 2 juillet 2024, 4 juillet
2025, 16 décembre 2025) ont été rouverts, cherchés à « 3.13 », « article 12 »,
« abattement », « inaptitude », « coefficient de réduction », « 60 ans », « 65 ans » :
aucun ne touche la règle. Le II de 2024 modifie bien les articles 3, 5, 10, 14, 15 et 17 ;
le 6° de 2025 ne change que la forme de la demande. La liste est complète : l'index ne porte,
de 2008 à 2025, que ces onze arrêtés de statuts de la section, cherchés sous quatre graphies
du titre, puis celui du 10 juillet 2026.

## 2. Les citations de la CARPV

| Ce que la fiche cite | Texte rouvert | Verdict |
|---|---|---|
| Arrêté du 11 janvier 2011, article 21, sixième alinéa | JORFARTI000023448554, publié le 19 janvier 2011 | mot pour mot |
| Arrêté du 16 avril 2014 : l'article 21 devenu 13 | JORFARTI000028939421 | exact, preuve indirecte (faible) |
| Statuts de 2021, articles 33, 34, 35 et 41 | JORFARTI000044220745, publié le 19 octobre 2021 | mot pour mot |
| Arrêté du 18 octobre 2021, article 2 (« entrent en vigueur le 1er janvier 2022 ») | JORFARTI000044220741 | mot pour mot |
| Règlement de 2026, articles 2 et 9 | JORFARTI000054436031 ; au LEGI, LEGIARTI000054437680, en vigueur le 18 juillet 2026 | mot pour mot |
| Décret n° 2026-418, article 6, 4° | JORFARTI000054153484 | exact |

**Faible.** Le fragment que la fiche cite pour la renumérotation (« les mots : « article 21 »
sont remplacés par les mots : « article 13 » ») est le i) du II, qui corrige un renvoi de
l'article 14 ; la renumérotation elle-même est au a) du II : « les articles 9, 11, 12, 13,
20, 21, 22 […] deviennent respectivement les articles 8, 9, 10, 11, 12, 13, 14 ». Le
renvoi le confirme, mais c'est le a) qui le dit.

## 3. L'arrêté de la CARPV du 2 novembre 2015, classé sans effet — moyen

JORFARTI000031549970, publié le 1er décembre 2015, annexe, I, 3° : « Au quatrième alinéa
de l'article 13, les mots : « titulaires de la rente d'invalidité à 100 % » sont remplacés
par les mots : « reconnus inaptes au taux fonctionnel ou professionnel de 100 % », et après
les mots : « peuvent demander à bénéficier de la retraite », est inséré le mot :
« complémentaire » ».

C'est l'alinéa de l'inapte que la fiche cite dans sa rédaction de 2011 : le sixième alinéa
de l'article 21, devenu l'article 13 en 2014, et son quatrième alinéa quand le même arrêté
de 2014 en supprime les quatrième et cinquième (h du II). La fiche le range pourtant parmi
ses `textes_sans_effet`, au motif : « la cotisation du titre II (articles 4, 12 et 13) et
la date d'effet de la réversion (article 21) ; rien de l'âge ni de la minoration ». Et son
écart de l'inapte dit « de 2011 à 2021, au moins l'invalide inapte titulaire de la rente
d'invalidité à 100 % », ce qui n'est vrai que jusqu'au 1er décembre 2015 : du 2 décembre 2015
au 31 décembre 2021, l'alinéa sert sans minoration l'invalide « reconnu inapte au taux
fonctionnel ou professionnel de 100 % ». Aucun chiffre du modèle n'en dépend, puisqu'il ne
sert l'inapte sans minoration à aucune date ; mais la fiche dit faux un texte et la
condition de six ans de l'écart qu'elle déclare.

Les autres arrêtés relus de la CARPV n'ont pas d'effet : 18 février 2015 (majorations de
retard), 23 janvier 2017 (titre III), 10 février 2017 (gouvernance, titre Ier ; ni dans
les lectures de la fiche ni dans sa liste, sans conséquence), 3 août 2017 (invalidité-décès),
16 décembre 2025 (article 50, points gratuits de l'invalide).

## 4. Les dates d'effet — conforme

Publications lues à l'index : 1er mars 2008, 4 septembre 2018, 27 juin 2019, 19 octobre
2021, 17 juillet 2026. Aucun de ces arrêtés ne fixe de date, sauf celui de 2021
(1er janvier 2022) ; les versions commencent le lendemain de la publication (2 mars 2008,
5 septembre 2018, 28 juin 2019, 18 juillet 2026), ce que l'index LEGI confirme pour les
deux règlements de 2026, qu'il dit en vigueur le 18 juillet. L'article 1er du code civil,
qui pose la règle, n'est pas dans l'index thématique (cherché à « lendemain de leur
publication » et au titre « code civil ») : la note le déclare justement. Les deux arrêtés
du 21 septembre 2026 qui modifient ceux du 10 juillet visent la CARMF, la CAVP et la
CARCDSF, pas ces deux caisses. Le décret n° 2026-239 (statuts types, en vigueur le
1er juillet 2026) ne porte aucune règle de liquidation : il ne tranche pas la question du
1er au 17 juillet 2026, que la fiche déclare ouverte.

**Faible.** La CAVEC date, en 2018 (article 16) et en 2026 (article 1.2.2), « avant le
1er janvier 2009 » les points que l'article 3.17 de 2008 dit acquis « avant la mise en
œuvre des présents statuts ». La caisse a donc mis en œuvre ses statuts de 2008 au
1er janvier 2009, au moins pour la réversion, quand la fiche les fait entrer en vigueur le
2 mars 2008. Aucun chiffre ne bouge, la règle d'avant étant supposée la même ; la fiche ne
le relève pas.

## 5. La règle supposée avant 2008 et avant 2022 — déclarée, trois faiblesses

Les deux versions sont `supposee`, avec leur hypothèse, leur fiabilité et une
approximation « effet : non mesuré » : c'est déclaré. Trois points s'en écartent, tous
faibles.

- **CAVEC, « l'arrêté du 23 mai 1953 ».** La fiche dit les statuts d'avant 2008 approuvés
  par cet arrêté. Le seul arrêté du 23 mai 1953 de l'index (JORFTEXT000000472264) porte
  « FIXATION DES COTISATIONS DE L'ASSURANCE VIEILLESSE COMPLEMENTAIRE POUR L'ANNEE 1953,
  DES EXPERTS COMPTABLES ET DES COMPTABLES AGREES » ; rien de l'index ne dit qu'il approuve
  des statuts. L'affirmation n'a pas de source.
- **CAVEC, l'âge d'ouverture.** La fiabilité ne vise que le taux (« faible ») et l'âge du
  taux plein (« moyenne ») ; l'ouverture à 60 ans avant 2008 n'a pas davantage de source :
  le livre de la caisse dit seulement qu'en 1983 l'« âge de départ en retraite […] reste et
  restera fixé à 65 ans », ce qui peut viser l'âge du taux plein comme l'âge de départ.
- **CARPV, avant 2011.** La version supposée part de la création du régime (1950), mais
  l'alinéa de 2011, seul lu, ne prouve rien avant 2011 : la fiabilité « moyenne pour la
  minoration elle-même et l'âge de 60 ans » ne vaut que depuis. L'index montre l'article 21
  du titre II modifié par les arrêtés du 9 mars 1960, du 16 septembre 1968, du
  30 décembre 1970 et du 8 juillet 1977 (titres seuls), que la fiche ne nomme pas ; et
  l'arrêté de 2014 en supprime deux alinéas dont on ne sait rien, ce qui ne permet pas de le
  dire « sans effet » : son effet est inconnu.

## 6. Les trois écarts du modèle, refaits dans les deux moteurs

Les essais passent par `servi_et_refait` (`tests/outils_pont.py`), qui fait calculer chaque
cas au portage JavaScript puis au moteur Python, et lève à la moindre différence : aucune
n'est apparue. Carrière : né le 10 février 1964, début en janvier 1990.

**L'inapte minoré — réel, dans les deux moteurs, portée à préciser (faible).**
`age_d_inaptitude` rend `None` à tout régime que la fiche `inaptitude_au_travail` ne nomme
pas (`src/retraite_notionnelle/droit/invalidite.py:136`, `moteur/js/droit/invalidite.js:91`),
et elle ne nomme que `regime_general, msa_salaries, cancava, organic, rsi,
assurances_sociales`. Essai, `inaptitude: oui` : coefficient 0,7500 à 60 ans (mars 2024)
et 0,8500 à 62 ans (mars 2026), à la CAVEC comme à la CARPV, les mêmes que sans
inaptitude. À la main : 65 − 60 = 20 trimestres × 1,25 % = 25 % ; 65 − 62 = 12 × 1,25 % =
15 %. Les deux effets annoncés sont justes. Leur portée l'est moins à la CAVEC de 2008 au
27 juin 2019 : l'inapte n'y était servi sans abattement que « lorsque la retraite du régime
de base de la CNAVPL est liquidée au titre de l'inaptitude », et cette retraite ne se liquide
qu'« à partir de l'âge prévu au premier alinéa de l'article L. 351-1 » (L. 643-3, I,
LEGIARTI000028498667, en vigueur du 22 janvier 2014 au 1er septembre 2023), soit 62 ans
pour les générations de 1955 et après : pour elles, la perte de l'inapte, dans ces années,
se mesure à l'âge légal (15 % à 62 ans), non à 60 ans. À la CARPV, la condition change le
2 décembre 2015 (point 3).

**La réversion de la CAVEC sans le coefficient, et celle de la CARPV sans lui quand
l'assuré meurt avant 65 ans — la règle est bien lue, l'écart du modèle est autre — moyen.**
Les textes disent ce que la fiche cite (points 1 et 2). Mais la fiche (« Le moteur applique
le taux de réversion à la retraite servie, coefficient compris (`droit/reversion.py`, sa
notice) ») et la note décrivent un comportement que le moteur n'a pas pour ces régimes.
Aucune fiche de réversion (`reversion*.yaml`) ne nomme `cavec_complementaire`,
`carpv_complementaire` ni `cnavpl` ; `fiche_du_regime` rend alors `None`, et la ligne vaut
zéro, motif `non_portee` (`src/retraite_notionnelle/droit/reversion.py:1813-1817`,
`moteur/js/droit/reversion.js:1676-1682`). Essai : vétérinaire parti en mars 2026 à 62 ans,
conjoint né en 1962, marié en 1988, décès en juin 2027 : ligne `carpv_complementaire`, base
14 513,36 €, taux 0, montant 0, motif `non_portee` ; de même à la CAVEC, avec décès en 2027,
en 2032 ou supposé juste après le départ, et pour la CNAVPL. La notice citée
(`reversion.py:133-136`) ne parle que de l'Agirc-Arrco, de l'Ircantec et de la RCI.
L'écart réel est donc la réversion entière, non 15 % : le conjoint d'un expert-comptable ou
d'un vétérinaire ne reçoit rien de ces caisses dans le modèle, et la ligne le dit. Aucun
chiffre servi n'est faux par l'erreur de la fiche, mais une pièce écrite pour justifier le
système décrit mal le modèle et sous-estime le manque.

**Hors du lot, observé en passant, non instruit.** La même classe touche la base : L. 643-4,
2°, a) (LEGIARTI000047453026, en vigueur le 1er septembre 2023) liquide « sans coefficient de
réduction » la pension de l'assuré « reconnu inapte au travail dans les conditions prévues
à l'article L. 643-5 », à l'âge du IV de L. 643-3 ; l'essai (départ en mars 2028, 64 ans,
`inaptitude: oui`) rend un coefficient de 0,8500 à la CNAVPL, comme sans inaptitude. Et le
modèle ouvre la CNAVPL à 60 ans à la génération 1964 (âge d'ouverture opposable 60,
coefficient 0,7500), quand sa fiche de régime la dit ouverte à l'âge légal de la génération
et que L. 643-3, I, l'ouvre « à partir de l'âge prévu au premier alinéa de l'article
L. 351-1 ». À instruire par une file du modèle.

## 7. Les tests — verts, une faiblesse

- `python -m pytest tests/test_sections_liberales.py tests/test_carte.py` : 59 passés.
- `python -m pytest -m rapide` : 4 326 passés, 13 rouges, tous
  `tests/test_pages_en_dossier.py` (les pages toutes faites, périmées dès que `main` bouge).
- `PRESOMPTIONS_DECALEES=1 python -m pytest -m rapide` : 4 127 passés, 205 sautés, les
  mêmes 13 rouges.
- La carte : `carte.manques()` rend 85 fiches et 503 manques, ceux du bloc ; aucun aux deux
  fiches.

Les valeurs du premier test neuf (60, 65, 0,0125, la durée sans effet) sont celles des
textes rouverts ; pour les deux versions supposées, celles d'une hypothèse déclarée. Celles
de `test_la_cavec_minore_par_l_age_seul` se refont à la main : 62 ans et 9 mois, neuf
trimestres, 11,25 %, 0,8875 ; 60 ans, 0,75 ; 62 ans, 0,85 ; 65 ans, 1.

**Faible.** Le second test neuf compare deux champs que la même fiche écrit
(`bornes` et `en_vigueur` du texte `nee_de`) : il tient leur cohérence, non leur vérité.
Celle-ci se vérifie à la main au point 4.

## 8. Ce que le texte ne tranche pas — déclaré

Le trimestre entamé (les statuts disent « par trimestre manquant », sans arrondi ; le modèle
arrondit au supérieur, `trimestres_de_decote`, comme R. 351-27) et la règle du 1er au
17 juillet 2026 sont déclarés dans les deux fiches (`a_relire`, `conditions`). Les statuts
d'avant 2008 et d'avant 2021, au seul Bulletin officiel, aussi.

## 9. Le bloc « Reprise » de l'action 130 — un manque, moyen

Comparé à l'ancien (`git show 9020e7b -- docs/feuille_de_route.md`), le bloc récrit perd :
« Au propriétaire, README muet : sa septième étape, la décision de la proposition, la
retraite progressive, le cumul et la seconde pension, la grille des marins d'avant 2008 (au
seul JO imprimé), la garantie des cultes de 2002 au 30 juin 2005 ». Il renvoie en échange
aux « 17 décisions » et aux « neuf questions qui attendent sa réponse » de
`130/2026-11-03-decisions-du-proprietaire.md`.

- La grille des marins d'avant 2008 y est : question 3. La garantie des cultes de 2002 au
  30 juin 2005 aussi : question 7.
- La décision de la proposition n'y est pas, ni pour la septième étape du sixième domaine
  (comment le compte reçoit les périodes qu'un tiers paie), ni pour la retraite
  progressive, le cumul et la seconde pension : ni « README », ni « proposition », ni
  « progressive », ni « cumul » dans ses 26 278 octets. Elles restent écrites ailleurs : dans
  la note `130/2026-10-17-sixieme-domaine-etape-6.md` (« La décision de la proposition, à
  l'étape 7 ») et dans le corps de l'action 130 (`docs/feuille_de_route.md`, vers la ligne
  4757 : « la décision de la proposition reste à prendre, par le propriétaire : le README ne
  dit rien de la retraite progressive, du cumul emploi-retraite, de la seconde pension ni
  de la date de chaque pension »).

Rien n'est perdu du dépôt, mais deux décisions qui attendent le propriétaire sortent du seul
paragraphe que lit une session au démarrage, et la phrase qui les remplace laisse croire
que la note des décisions porte toutes ses questions. À rétablir par la file E, seule à
récrire ce bloc.

## Ce que la relecture laisse

À la file E ou à une file du modèle, sans rien en corriger ici : la fiche de la CARPV
(arrêté de 2015, point 3) ; la description de la réversion dans les deux fiches et la note
(point 6) ; les faiblesses des points 2, 4, 5 et 7 ; le bloc « Reprise » (point 9) ; et, hors
du lot, l'inapte de la CNAVPL et l'âge où le modèle ouvre sa base (point 6).
