# Relecture des corrections de R-I (file I-bis)

File R-I-bis, vague 5, le 3 novembre 2026 : relecture indépendante des commits
3ddae71, bd1c251, c752a8a et e17c8f7 (session `session_01FVFLAmMhzcNBvyaZB3VGY7`,
note `2026-11-03-etape-14-corrections-de-la-relecture-r-i.md`), qui répondent à
la relecture R-I (`2026-11-03-relecture-surcote-du-salariat.md`), sur `main` à
e17c8f7. Rien n'est repris de la session ni de mémoire. Ouverts ici : le jaune
pensions annexé au PLF 2027, le PDF lui-même (branche `jaune-2027`, `34465.pdf`,
11 964 640 octets, SHA-256 `73dd4a66…2dbaf5`, recalculée, celle de
`data/sources.yaml`), p. 182, 210 et 211 ; le fichier certifié de l'EIR
`data/reference/macro/departs_generations.csv` ; le témoin des tables H et B de
l'EACR, `tests/temoins/drees_eacr_tables_2026.json`, et l'en-tête de son
récupérateur, `scripts/fetch/drees_eacr_tables.py` ; le code,
`scripts/mesurer_surcote.py`, `scripts/grille_large.py`, `scripts/controle_eacr.py` ;
la note de la file I (`2026-11-03-etape-14-surcote-du-salariat-selon-la-generation.md`).
Non ouverts : les classeurs d'origine de la DREES ; la sortie de la mesure
complète, qui n'est pas au dépôt ; l'arbre 8c93f72 où elle a tourné, qui n'est
pas publié (introuvable après `git fetch --deepen=500`). Seule cette note est
écrite : ni code, ni donnée, ni test, ni bloc « Reprise ».

**Verdict. Conforme sur l'essentiel.** Le script mesure ce que la note dit ; ses
deux tests sont posés à la main et mordent sur six mutations sur neuf ; tous les
chiffres des sources se refont, au témoin, au fichier certifié et au PDF ; les
calculs des départs après 67 ans se refont au centième ; l'explication des 0,58
point est une identité de ce que le script mesure ; les trois déclarations de
bd1c251 disent juste. Les chiffres simulés de la note retrouvent au centième
ceux du pilote indépendant de R-I sur chaque ligne que tous deux ont mesurée.
**Écarts**, tous faibles ou négligeables : la borne de 6,56 points et la
critique de R-I tiennent à une hypothèse que la note ne déclare que dans son
calcul (point 2) ; trois mutations échappent aux tests (point 1) ; les stocks
restent comptés au drapeau, que la note juge le mauvais compte pour la table H
(point 3) ; la sortie de la mesure complète n'est pas gardée (point 5) ; trois
négligeables.

## 1. Le script et ses deux tests

**Ce qu'il mesure — conforme.**

- *Au drapeau* (`surcotee`) : vrai si la variante est une jumelle qui surcote
  (`v.surcote`) et si `_attente_du_depart(génération)` n'est pas nul. Cette
  méthode (`grille_large.py`, l. 1553 à 1571) rend `None` sans attente, ou pour
  une règle `taux_plein` dont la génération atteint son âge légal avant
  `ANNEE_DE_LA_SURCOTE = 2004` (l. 1185). La génération est celle de la cohorte,
  la génération simulée. C'est ce que la note dit.
- *À la condition* : `condition_au_depart` (l. 5776 à 5805) classe d'abord la
  carrière longue, puis la décote ; « surcote » si le départ passe l'âge légal de
  plus de `TOLERANCE_DE_PLACE` (0,125 an) et l'âge du taux plein de plus de
  1e-6 ; sinon « taux plein par l'âge » ou « taux plein autre ». La part se prend
  parmi les couples dont la condition se lit, et les autres sont comptés à part
  (`inconnues`). C'est ce que la note dit.
- *Champ et année* : le régime général est le groupe `regime_general`, comme
  dans `controle_eacr.py`. Les fonctionnaires civils sont les affiliations de
  `CAISSES_DU_JAUNE` : l'État (`fonctionnaire_etat`, `_actif`, `_super_actif`)
  et la CNRACL. L'année est `ANNEE_EACR = 2024` (`src/retraite_notionnelle/controle_eacr.py`, l. 44). La
  pesée par année de naissance (`part_de(code, année − âge)`) est celle de
  `cohortes_de_la_population`. Les deux grilles sont vérifiées identiques (cas
  types et poids) ; la grille est simulée une fois, et pesée deux fois. C'est ce que la note
  dit.
- *Les sources* : la table H et la table B lues au témoin. La table B compte
  « 68 ans et plus » comme les âges supérieurs à 67, plus la clé `>70`. Les âges
  de la caisse 0015 somment 648 346, sa ligne « Ensemble ».

**Les valeurs du premier test, refaites à la main — conformes.** L'État en 2024 :
3 + 1 + 2 + 6 + 2 + 5 = 19 retraités, au drapeau 1 (jumelle de 1955) + 2 (de 1960)
= 3, celle de 1940 exclue (1940 + 60 < 2004). Ses 13 liquidants : 2 au drapeau, 2
des 8 dont la condition se lit, 5 inconnus. Le régime général : 7 + 3 + 5 = 15
liquidants ; 3 au drapeau ; 7 à la condition, une carrière qui n'est pas jumelle ;
5 décotés (l'indice 3 de `proratisations`, la décote) ; 7 + 3 + 5 + 10 = 25
retraités, dont 3 au drapeau. Les hommes de 2020 : 10, dont 3 au drapeau ; 6 de
70 à 74 ans, dont 3 ; 1 fonctionnaire sur 3 surcotés. Les femmes : 5 sur 10, et
aucune de 70 à 74 ans. Le second test pose à la main les sources, refaites au
témoin et au fichier : 122 368 / 648 346, 1 658 347 / 14 744 736,
370 626 / 1 641 380, 20 350 + 6 969 + 4 832 + 15 581 = 47 732, et 14,3 / 99,1
(1,4 + 20,3 + 10,6 + 3,2 + 7,0 + 7,9 + 14,3 + 9,9 + 24,5 = 99,1). Les autres
valeurs du second test (zéro au drapeau, deux pesées égales) se déduisent de la
grille de la page, qui n'a pas de jumelle.

**Les tests mordent-ils ?** Une mutation à la fois dans le script, puis
`git checkout -- scripts/mesurer_surcote.py` :

| mutation | résultat |
|---|---|
| le drapeau sans la règle de 2004 (`return bool(v.surcote)`) | 1 échec |
| « 68 ans et plus » lu `>= 67` | 1 échec |
| la condition comptée « tout sauf décote » | 1 échec |
| la décote lue à l'indice du minimum | 1 échec |
| la tranche 70-75 au lieu de 70-74 | 1 échec |
| le stock de la Cnav lu au flux | 1 échec |
| la table H de l'État lue en 2024 pour chaque année | **2 réussis** |
| la décote de la Cnav lue au taux plein | **2 réussis** |
| les pesées « version » et « éteinte » permutées | **2 réussis** |

*Écart faible* : trois colonnes de la note ne sont tenues par aucun test. Ce sont
la colonne source des liquidants de l'État année par année, celle de la décote
de la Cnav, et l'étiquette des deux pesées : sur la grille de la page, la
constante ne change rien, et une permutation ne s'y voit pas. Ces chiffres se
refont pourtant ici. Au témoin : 19 278 / 52 693 = 36,59 % en 2020,
20 992 / 54 735 = 38,35, 20 893 / 54 666 = 38,22, 20 824 / 51 981 = 40,06,
17 547 / 45 078 = 38,93 %, moyenne 38,43 ; 86 776 / 648 346 = 13,38 %. Au code,
`construire(…, True)` donne bien « version ». La note ne prétend pas que les
tests tiennent ces chiffres.

## 2. Les départs après 67 ans

**Les sources — conformes.**

- *Table H*, caisse 0015, flux de 2024 : 439 202 + 86 776 + 122 368 = 648 346,
  exactement. R = 18,874 %.
- *Table B*, caisse 0015 : a = 47 732 / 648 346 = 7,362 %. À 67 ans, 60 530, soit
  9,34 %.
- *EIR* : à `departs_generations.csv`, l. 1044 à 1072, les nés en 1953 partis à
  « 67 ans et plus » sont 6,0 milliers sur 757,0 (l. 1071 et 1143), soit 0,8 % ;
  s = 34,6 % avec une surcote (29,1 des femmes, 40,6 des hommes). L'en-tête du
  fichier dit cette génération vue en 2020, à 67 ans : ses « 67 ans et plus »
  sont donc des départs à 67 ans.

**Les calculs, refaits — conformes au centième.** Avec m = 10,911 % :

- R − m = 7,963 ;
- a × (s − m) = 1,744, soit 21,9 % de l'écart ; reste 6,219 ;
- a × (1 − m) = 6,559 ; reste 1,404 ;
- au drapeau (m = 11,49 %) : 1,701 sur 7,384 ;
- a × s = 2,547 ;
- vu de la Cnav : (122 368 − 0,346 × 47 732) / 600 614 = 17,624 %, 20,374 et
  12,427 % aux bornes ; 17,62 − 10,91 = 6,71.

m lui-même vient de la mesure complète, non refaite (point 5).

**L'argument des « départs qu'ils remplacent » — tient sous une hypothèse ;
écart faible.** La formule exacte est un mélange : si une part a des liquidants
part après 67 ans au taux s, à la place de départs qui surcotaient au taux r, la
part des surcotés gagne a × (s − r). La note prend r = m, « sans rien changer au
taux m de ses départs de 67 ans et moins ». L'hypothèse est écrite dans son
calcul, mais aucune source ne la fonde : rien ne dit quels départs du modèle les
départs tardifs remplaceraient. Les 2,55 points de R-I (a × s) ne sont pas un
oubli. Ce sont le même mélange, dans le cas r = 0 : les départs tardifs
remplaceraient des départs sans surcote. La note les dit pourtant « la part des
liquidants de la Cnav qui auraient 68 ans et plus et surcoteraient, non ce
qu'ils retranchent de l'écart ». Il en suit trois choses :

- au taux de l'EIR, le gain va de 1,74 (r = m) à 2,55 points (r = 0), le tiers
  de l'écart au plus ;
- la borne « tous surcotent, 6,56 au plus » n'est une borne que pour r = m ; pour
  r = 0, elle vaut a × 100 = 7,36 points, et il reste 0,60 point, non 1,40 ;
- la phrase au propriétaire (« 6,6 points au plus si tous ces départs
  surcotaient ; le reste, 6,2 points ») se dirait juste ainsi : « 1,7 à 2,5
  points au seul taux de l'enquête, selon les départs qu'ils remplacent ; 7,4 au
  plus si tous surcotaient ; le reste, 5,4 à 6,2 points ».

La conclusion, *l'absence de départ après 67 ans n'explique pas l'essentiel de
l'écart au taux de l'enquête*, tient pour tout r. *Poids : faible.*

## 3. 10,91 % ou 11,49 %

**L'explication par les jumelles — établie par ce que le script mesure.**
`croisement` range chaque liquidant du régime général de 2024 dont la condition
se lit, deux fois : drapeau ou non, puis selon la classe de sa condition. La
différence des deux parts est donc une identité : drapeau − condition =
(drapeau sans surcote) − (surcote sans drapeau). La note l'écrit ainsi :
0,50 + 0,08 − 0,00 = 0,58. Les deux dénominateurs sont les mêmes si toutes les
conditions se lisent (« 17 090 couples […], tous lus »). Le mécanisme se lit au
code. La jumelle du salariat part à `max(âge du pilote, âge légal + attente)`
(l. 1551). Ses attentes, recalculées ici (`attentes_des_surcotes`), valent
1,21, 3,11 et 5,42 ans pour les femmes, 1,23, 3,15 et 5,45 pour les hommes, bien
au-delà de la tolérance de 0,125 an. Une jumelle classée « taux plein » part donc
à son taux plein, qui vient après son attente : c'est ce que la note dit. Les
valeurs mêmes, 10,91, 0,50 et 0,08, sortent de la mesure complète, non refaite
ici (point 5).

**Lequel compare juste avec les 18,87 % de la Cnav — la condition, 10,91 %,
conforme.** Au témoin, la table H partage les liquidants en trois, sans reste
(taux plein, décote, surcote ; 648 346 exactement en 2024 à la Cnav). Le
récupérateur le dit : « les retraités partis au taux
plein, avec une décote, avec une surcote […] Les trois conditions partitionnent
les retraités : la surcote n'est pas comptée dans le taux plein ». Une jumelle
partie à son taux plein, sans surcote, y est au taux plein. Seule la condition la
compte ainsi. Cette définition est celle du témoin et du récupérateur : le
classeur de la DREES n'a pas été rouvert. *Négligeable, non mesuré* : la
condition compte « surcote » tout départ passé d'un rien le taux plein, sans
vérifier qu'il gagne un trimestre de surcote.

**Ce que la note n'en tire pas — écart faible.** Par le même argument, les stocks
devraient se compter à la condition. Or le script ne les compte qu'au drapeau,
faute de conditions pour eux : les retraités du régime général de 2024 (7,81 %,
contre 11,25 % à la table H), ceux de l'État (23,52 %, contre 22,58 %) et le
stock de 2020. Pour le régime général, où aucune carrière ne surcote hors des
jumelles parmi les liquidants de 2024, le drapeau est probablement un plafond, et
l'écart à la Cnav serait un peu plus large. Une piste aussi, non éprouvée : la
note de la file I écrit compter au drapeau « le stock de 2020 par tranche d'âge
et les retraités du régime général de 2024 […] ; le reste, à la condition »
(l. 124 à 128). À la lettre, elle comptait donc à la condition les retraités de
l'État de 2024, quand le script les compte au drapeau. Cela pourrait expliquer
23,4 contre 23,52 ; la note d'I-bis tient la cause pour non établie, à juste
titre. *Poids : faible.*

## 4. Les trois déclarations de bd1c251

- *4.1, la rupture de 2012 du tableau 103 — conforme.* Relu au PDF, p. 182, le
  tableau 103 donne 28 % en 2011, 36 % en 2012 et 31 % en 2013. La note 154 est
  citée mot pour mot, « avait progressée » compris. La suite du sédentaire de
  l'État a été recalculée ici par `surcotes_des_fonctionnaires_selon_la_generation` :
  38,78 (1951), 44,67 (1952, à 60,75 ans), 42,94 (1953), 42,14 (1954),
  38,78 (1955), 42,94 (1956), 44,32 % (1957). Ce sont les valeurs du commentaire
  et de la note, à partir d'une part de 2025 de 48,479 %.
  *Négligeable* : la note écrit « les nés en 1952 et 1953 portent le relèvement
  de 2012 ». Seuls les nés en 1952 le portent (2012,75, entre 2012 et 2013). Les
  nés en 1953 atteignent leur âge légal en 2014,17, entre 2014 et 2015, tous deux
  à 31 %, et la p. 182 ne dit perturbée que 2012.
- *4.2, la cible et le juge — conforme.* La cible est au tableau `residence`,
  colonne `france` (l. 1530 et 1542, 14,2 et 14,4 % ; l. 756 et 768, 11,2 et
  12,2 %). Ses conditions somment 99,2 % (femmes) et 99,3 % (hommes) en 1953 : les
  inconnues sont bien au dénominateur. Le juge, `confronter_departs`, lit le
  tableau `condition` parmi les conditions connues : 14,2 / 99,2 = 14,315 ;
  14,5 / 99,0 = 14,646 ; 11,2 / 99,6 = 11,245 ; 12,2 / 99,2 = 12,298. L'écart va
  de 0,04 à 0,25 point.
- *4.5, l'État contre le jaune, deux champs — conforme.* Relu au PDF, le
  tableau B-3 est à la p. 210 pour ses effectifs (« Pensions civiles » :
  ancienneté 41 812, motifs familiaux 2 545, invalidité 2 747) et à la p. 211
  pour « Part des pensions avec surcote » (42,7 %, 16,5 %, 11,9 %). La table H
  (caisse 0012, « Cube SRE 2024 ») a été refaite au point 1. La moyenne du modèle
  de 2020 à 2024, d'après la note, est de (37,24 + 42,40 + 41,85 + 31,94 +
  50,64) / 5 = 40,81 % : 2,4 points de plus que la table H, et 11,7 en 2024.
  L'en-tête du script le déclare, et `sources()` met bien la table H de l'État,
  année par année, en regard.

## 5. Reproduire

- *Le mode court, lancé* sur `main` à e17c8f7 :
  `python scripts/mesurer_surcote.py --grille reference --processus 1 --json …`.
  1,7 s, la mémoire des calculs chaude du test ; 18 cas types, 498 couples ;
  24 échecs (16 liquidations antérieures à la répartition, 8 carrières sans
  régime actif) ; 18 conditions sur 18 lues. Les deux pesées sont égales, et le
  drapeau nul. Les colonnes des sources sont celles de la note : 18,87, 11,25,
  13,38, 7,36, 22,58, 36,59 à 38,93, 25,97, 10,56, 7,29, 63,60. Les deux tests
  de la mesure : 2 réussis, en 27 s.
- *La mesure complète n'a pas été refaite* : la note l'estime à près de trois
  heures sur quatre cœurs sans mémoire des calculs. Ses chiffres, dans la note, recoupent pourtant au
  centième le pilote de R-I (sur 9689bd99), sur chaque ligne que tous deux ont
  mesurée : les douze lignes de départs que R-I a refaites ; l'État en 2024,
  retraités et liquidants ; le régime général au drapeau ; ses retraités ; les
  62 ans ; l'âge moyen ; les stocks de 2020 et leurs fonctionnaires.
- *Écart faible* : la sortie de la mesure complète, son fichier `--json`, n'est
  pas au dépôt, et l'arbre où elle a tourné, 8c93f72, n'est pas publié (il se
  rebâtit de 490cb7a et du script). Les chiffres qui ne sont qu'à elle (l'État de
  2020 à 2023 et de 2025, la CNRACL, la décote, le croisement, les femmes de 1950
  à l'âge légal, les pensions et l'écart de Kolmogorov) n'ont donc pour preuve
  écrite que leur transcription dans la note. *Négligeable* : le taux de 6,58 %
  des liquidants du régime général à 67 ans est dit « mesuré ci-dessus », mais
  aucun tableau ne le montre, et le script n'imprime que les 68 ans et plus.

## Les tests

Sur `main` à e17c8f7 : les deux tests de la mesure (`-k la_mesure_de_la_surcote`),
2 réussis ; les neuf mutations du point 1, chacune annulée, l'arbre propre
ensuite (`git status`) ; `python -m pytest -m rapide`, 4 269 réussis, 56 sautés,
en 2 min 1 s.
