# Relecture du taux propre de l'indépendant de Mayotte (file D) : le taux juste, le plafond faux

File R-D, vague 7, le 5 novembre 2026, sur Opus : relecture indépendante des commits
bbb85b0, 9b62adc et d8124ff (file D, action 177), de leur note
`2026-11-05-taux-des-independants-de-mayotte.md` et de leur fiche
`cotisation_vieillesse_independants_mayotte`. Lecture seule : aucune règle, aucune donnée,
aucun test n'est touché. Chaque texte a été rouvert dans l'index LEGI de la DILA récupéré
dans la session (`dila_index.py legi --recuperer`, puis `--mettre-a-jour` : à jour au
4 novembre 2026). Chaque valeur a été refaite à la main, puis demandée aux deux moteurs.

**Verdict : le taux est conforme, l'assiette ne l'est pas. Un écart grave, un moyen,
trois faibles.** Les citations sont exactes. Les seize valeurs, leurs dates d'effet et leur
certification sont justes, et les deux moteurs les rendent au centime. Les cinq témoins
bougent pour cette seule raison. Mais l'article 4-2 borne l'assiette au plafond de la
caisse de Mayotte, et les deux moteurs la bornent au plafond de la Sécurité sociale. Quatre
des cinq témoins gagnent plus que le plafond de la caisse. Sur 2019 à 2026, le compte du
témoin né en 1965 reçoit 29 035 € de cotisations au lieu de 19 353 €, soit 50 % de trop.
De 2012 à 2018, la présomption est déclarée, mais elle n'est pas la plus prudente.

## 1. Les textes, rouverts : conformes

- **Décret n° 2011-2085, article 4-2**, deux rédactions dans l'index :
  LEGIARTI000038680068 (du 25 juin 2019 au 1er janvier 2026) et LEGIARTI000053297541
  (depuis le 1er janvier 2026). La note et la fiche citent exactement la première. On y
  lit la note d'application (« dues au titre des périodes courant à compter du 1er janvier
  2019 »), l'assiette (« dans la limite du plafond prévu au I de l'article 28-1 de
  l'ordonnance du 20 décembre 1996 susvisée ») et le tableau, de « 2019 5,85 % » à
  « 2036 17,75 % ». Le mot « totalité » n'est pas au I : il n'apparaît qu'au II, celui de
  l'assurance maladie. `dila_cherche.py --diff` entre les deux rédactions : la seconde ôte
  la note d'application et ajoute « L'assiette minimale s'applique aux travailleurs
  indépendants dont la durée d'affiliation est au moins égale à quatre-vingt-dix jours au
  cours de l'année considérée. » Le reste est inchangé, comme la note le dit.
- **Ordonnance n° 96-1122, article 28-2**, LEGIARTI000025018560 (du 1er janvier 2012 au
  1er décembre 2024) et LEGIARTI000046455192 (depuis le 1er décembre 2024) : la citation
  du I, 1°, est exacte. La seconde rédaction n'ajoute que la note d'entrée en vigueur et
  un III (les personnes détenues).
- **Décret n° 2011-2085, article 4**, trois rédactions : LEGIARTI000025097520 (du
  1er janvier au 21 octobre 2012), LEGIARTI000026514552 (du 21 octobre 2012 au
  1er janvier 2026) et LEGIARTI000053469930 (depuis le 1er janvier 2026). Aucune ne nomme
  les travailleurs indépendants. Toutes fixent « le taux des cotisations mentionnées aux
  articles 28-2 », par une part salariale et une part patronale. La citation de la fiche
  (« 2012 4,00 % 9,90 % ») est exacte dans la deuxième rédaction ; la première dit autre
  chose pour 2012 (§ 6, a).

## 2. Les seize valeurs et leurs dates : conformes

À la main, d'après le tableau du I : 2019 0,058500 ; 2020 0,065500 ; 2021 0,072500 ;
2022 0,079500 ; 2023 0,086500 ; 2024 0,093500 ; 2025 0,100500 ; 2026 0,107500. C'est
0,70 point de plus chaque année. Pour chacune des huit années, la mesure
`taux_deplafonne_non_salarie` vaut 0 : le I et l'article 28-2 bornent tous deux la
cotisation au plafond. Ces seize valeurs sont celles de `taux_cotisation_annuels.csv`.

Les dates d'effet :

- 2019 vaut pour toute l'année, bien que la rédaction n'entre en vigueur que le 25 juin :
  c'est sa note d'application qui le dit.
- 2020 à 2025 sont lues dans la même rédaction.
- 2026 est lue dans la rédaction du 1er janvier 2026, à la même valeur.

Le tableau fixe un taux « pour chaque année civile », et la fiche borne ses versions par
`revenu.annee` : c'est conforme.

**La certification.** Relancé, `scripts/fetch/dila_legi_taux_mayotte.py` imprime ces huit
lignes : `LEGIARTI000038680068` pour 2019 à 2025, `LEGIARTI000053297541` pour 2026.
Ensuite, `scripts/verifier_donnees.py`, sans `--appliquer`, rend : « OK
taux_cotisation_mayotte : 16 valeurs confrontables […] — 16 identiques, 0 corrigées,
0 ajoutées ». Le récupérateur certifie bien ce qu'il annonce : il ne lit que le tableau du
I, et il s'arrête sur un I sans tableau ou qui parle de la totalité du revenu. Le
déplafonné à 0 n'est pas un nombre lu dans le texte : le récupérateur le déduit de
l'assiette « dans la limite du plafond », et sa documentation le dit.

## 3. Les deux moteurs : conformes au taux

`python -m pytest tests/test_mayotte.py` : 11 réussis. Avec `PRESOMPTIONS_DECALEES=1` :
6 réussis et 5 passés. Les 5 tests passés confrontent le Python au portage ; la conftest
les écarte sous cette variable (« le portage lit ses présomptions dans le paquet »).

Le compte de l'année (`cotisation_annuelle`), à la main puis dans les deux moteurs, avec
un résultat identique au centime en Python et en JavaScript dans les 18 cas :

| Statut, revenu, année | Attendu | Python et JavaScript |
|---|---|---|
| indépendant, 10 000 €, 2019 | 10 000 × 5,85 % = 585,00 € | 585,00 € |
| indépendant, 10 000 €, 2024 | 10 000 × 9,35 % = 935,00 € | 935,00 € |
| indépendant, 10 000 €, 2026 | 10 000 × 10,75 % = 1 075,00 € | 1 075,00 € |
| indépendant, 10 000 €, 2018 | série alignée, 15,45 % + 2,30 % = 1 775,00 € | 1 775,00 € |
| indépendant, 10 000 €, 2012 | série alignée, 14,95 % + 1,70 % = 1 665,00 € | 1 665,00 € |
| salarié, 10 000 €, 2019 | inchangé, 1 775,00 € | 1 775,00 € |

Les valeurs que pose la note sont justes : 450 × 7,57 = 3 406,50 €, et 1 545 + 230 =
1 775 €.

## 4. L'assiette au-dessus du plafond de la caisse : écart GRAVE

**Le texte.** L'article 4-2, I, assied la cotisation « dans la limite du plafond prévu au
I de l'article 28-1 ». L'article 28-1, I (LEGIARTI000031324363, du 16 octobre 2015 au
28 février 2025), dit : « Il est créé un plafond de cotisations de sécurité sociale à
Mayotte. […] Son montant, calculé selon des règles prévues par décret, est arrêté par le
ministre chargé de la sécurité sociale. » Le plafond du texte est donc celui de la caisse
de Mayotte, et non le plafond de la Sécurité sociale. La série du dépôt donne 23 208 € en
2020 et 31 728 € en 2024 (`legislation/mayotte_smig_et_plafond.csv`, fiabilité `haute` ;
la présente relecture ne l'a pas revérifiée à sa source).

**Les moteurs.** Les deux rendent la même chose, dans le compte comme dans la fiche de
paie (`bloc_droit_en_vigueur`, `ConstructeurFiche`) :

| Revenu, année | Attendu (plafond de la caisse) | Rendu (plafond de la Sécurité sociale) |
|---|---|---|
| 30 000 €, 2020 | 23 208 × 6,55 % = 1 520,12 € | 30 000 × 6,55 % = 1 965,00 € |
| 50 000 €, 2024 | 31 728 × 9,35 % = 2 966,57 € | 46 368 × 9,35 % = 4 335,41 € |

**L'effet sur les témoins.** Leurs carrières ont été relues par le portage
(`pont.carrieres_des_saisies`). Quatre des cinq témoins qui bougent gagnent plus que le
plafond de la caisse chaque année de 2012 à 2026 : `statut_independant_mayotte`,
`statut_independant_mayotte_1965`, `statut_independant_mayotte_ne_le_20_septembre_1968`,
et `statut_independant_mayotte_1955` de 2012 à 2018. Le témoin né en 1965, par exemple,
gagne 46 042 € en 2024, pour un plafond de la caisse de 31 728 €. De 2019 à 2026, son
compte reçoit 29 035 € ; le texte en donne 19 353 €, soit 50 % de moins. Sa pension
notionnelle reste donc surestimée après le commit, et la baisse de 21,38 % que la note
annonce est plus faible que celle que donnerait le droit.

**Pourquoi l'écart est grave.** Il n'est pas né du commit : avant lui, les taux du régime
général s'appliquaient déjà jusqu'au plafond de la Sécurité sociale. La ligne `manque` de
`cssm_mayotte.yaml` le dit en termes généraux : « Les cotisations restent assises sur le
plafond et aux taux du régime général ». Mais le commit a écrit une règle « sous le
plafond seulement » sans le plafond du texte, et rien ne le signale là où on le
chercherait :

- la fiche neuve, au statut `lue`, donne pour droit « sous le plafond » et ne déclare
  aucune approximation sur le plafond ;
- la note et la docstring du test nomment comme borne « le plafond de la caisse
  (23 208 € en 2020, 31 728 € en 2024) » ;
- les deux tests se placent à 10 000 €, sous les deux plafonds : ils ne peuvent pas voir
  lequel des deux borne l'assiette.

La fiche qui servirait de preuve dit l'assiette du texte, alors que les moteurs, et donc
les témoins publiés, en calculent une autre. L'écart ne touche aucune pension du
scénario 1. Il touche le compte notionnel et la fiche de paie du droit en vigueur.

**Ce qui reste, à la file du modèle.** Il faut borner la cotisation de `cssm_mayotte` au
plafond de la caisse, dans les deux moteurs, en commençant par un test au-dessus de ce
plafond. À défaut, la fiche doit déclarer l'écart. L'erreur est de classe : l'article 28-2
borne au même plafond les cotisations du salarié de Mayotte depuis 2012 (« dans la limite
du plafond prévu au deuxième alinéa du I de l'article 28-1 ») ; c'est à vérifier dans la
rédaction de 2012 de l'article 28-1.

## 5. De 2012 à 2018 : déclaré, mais pas la plus prudente des présomptions — écart MOYEN

**La déclaration est faite.** La version `avant_le_taux_propre` de la fiche est
`supposee`, à la fiabilité « faible ». Son approximation dit que « l'article 28-2 de
l'ordonnance n° 96-1122 n'appelle aucune cotisation sur la totalité du revenu ». Une
lecture reste à faire (`a_relire`) : une circulaire de la caisse ou un barème de la Cnav.

**Mais les textes lus tranchent une partie de la question.** La note dit que « le texte ne
le tranche pas ». C'est vrai du taux, pas de l'assiette :

- l'article 28-2 (LEGIARTI000025018560), en vigueur depuis le 1er janvier 2012, borne au
  plafond les cotisations « des travailleurs indépendants agricoles et non agricoles » ;
  le modèle leur garde pourtant une part sur la totalité, de 1,70 % en 2012 à 2,30 % en
  2018 ;
- l'article 4 fixe le taux de ces mêmes cotisations : une part salariale de 4,00 % à
  4,66 % et une part patronale de 9,90 %, soit au plus 13,90 % à 14,56 % si l'indépendant
  doit les deux.

Le modèle retient 14,95 % à 15,45 % jusqu'au plafond de la Sécurité sociale, plus 1,70 % à
2,30 % sur la totalité. À 10 000 €, cela fait 16,65 % en 2012 et 17,75 % en 2018. C'est
plus que chacune des lectures que le texte permet (la part salariale, la part patronale
ou leur somme), et sur une assiette plus large que la sienne. Le critère de la relecture
R-L-bis est de n'ajouter rien qu'aucun texte n'écrit
(`130/2026-11-05-relecture-corrections-r-l.md`). Selon ce critère, la présomption n'est
pas la plus prudente. La plus prudente qui reste compatible avec les textes serait : au
plus la somme des deux parts de l'article 4, sous le plafond de la caisse, et rien
au-dessus.

L'écart est moyen : il est déclaré, il ne touche pas le scénario 1, et il porte sur le
compte notionnel des années 2012 à 2018 des cinq témoins.

## 6. Les témoins : conformes ; aucun autre statut de Mayotte ne bouge

`python scripts/resumer_temoins.py --depuis bbb85b0^` : 18 témoins bougent sur 930.
Leurs pensions :

- scénarios 2 et 4 : 5 bougent, de −0,84 % (`statut_independant_mayotte_1955`) à
  −21,38 % (`statut_independant_mayotte_1965`) ;
- scénario 6 : le seul témoin de 1955, à −0,84 % ;
- scénarios 1, 3 et 5 : aucune.

C'est ce que dit la note. Les 13 autres témoins ne bougent pas dans bbb85b0. Ils bougent
dans d8124ff, qui refait le paquet sur le dernier `main`. Ce qui change chez eux :

- `age_ouverture_opposable`, au scénario actuel, est écrit sans arrondi (61,166667
  devient 61,166666666666664) ;
- pour `comedie_francaise_generation_1958_apres_soixante_ans`, changent aussi
  `liquidation_ouverte` et `motif_ouverture`.

Aucun de ces 13 témoins n'est de Mayotte, et aucun ne touche une cotisation. Les sept
témoins du salarié de Mayotte, et ceux de l'indépendant nés en 1925, 1935 et 1945, sont
identiques à l'octet.

**Une vérification à la main.** Le témoin `independante_mayotte_assiette_minimale` déclare
1 000 € par an. Ses `cotisations_versees` passent de 7 497,88 € à 6 809,48 €, soit
688,40 € de moins. À la main, de 2019 à 2025, la différence entre la série alignée et le
taux de l'article 4-2, appliquée à 1 000 €, donne : 119 + 112 + 105 + 98 + 91 + 85,20 +
78,20 = 688,40 €. Le compte au centime près confirme que le taux seul fait bouger le
témoin. Le compte cotise sur le revenu déclaré, et non sur l'assiette minimale ; c'est la
convention que déclare la fiche `assiette_minimale_independants`.

Pour les pages, `methode` compte une série de plus (227) et 16 valeurs de plus
(441 823), avec la ligne `taux_cotisation_mayotte` : ces changements viennent de ce
commit. Les autres rendus qui changent (`programme`, les courbes du coût) sont des
fichiers fabriqués, que GitHub refait ; je ne les ai pas examinés plus avant.

## 7. Trois écarts faibles

a) **La part salariale de 2012.** La première rédaction de l'article 4
   (LEGIARTI000025097520, du 1er janvier au 21 octobre 2012) donne pour 2012 « 4,11 %
   9,90 % ». C'est la rédaction du 21 octobre 2012 qui donne 4,00 %. Or la note et la fiche
   écrivent « 4,00 % en 2012 », et l'approximation « de 4,00 % à 4,66 % ». Du 1er juillet
   2012, date de l'affiliation, au 21 octobre, le texte en vigueur disait 4,11 %. Aucune
   valeur du modèle n'en dépend.
b) **Deux phrases restées en arrière.** La ligne `manque` de `cssm_mayotte.yaml` dit encore
   que les cotisations restent « aux taux du régime général », ce qui est faux pour
   l'indépendant depuis 2019. Le commentaire de `TAUX_ALIGNES` dans
   `scripts/verifier_donnees.py` dit que le dépôt « ne lit pas encore » l'article 4, alors
   que la fiche le cite comme lu le 5 novembre.
c) **Les tests ne voient pas le plafond.** Les tests du compte et de la fiche de paie se
   placent tous deux sous les deux plafonds : aucun ne voit l'écart du § 4. C'est par là
   que sa correction devrait commencer.

**Sources** : index LEGI de la DILA, à jour au 4 novembre 2026 :

- décret n° 2011-2085, art. 4-2 : LEGIARTI000038680068, LEGIARTI000053297541 ;
- décret n° 2011-2085, art. 4 : LEGIARTI000025097520, LEGIARTI000026514552,
  LEGIARTI000053469930 ;
- ordonnance n° 96-1122, art. 28-2 : LEGIARTI000025018560, LEGIARTI000046455192 ;
- ordonnance n° 96-1122, art. 28-1 : LEGIARTI000031324363.
