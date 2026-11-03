# Relecture des corrections de R-K (file K-bis)

File R-K-bis, le 3 novembre 2026 : relecture indépendante des commits ddb8824 (fiches,
limite et paquet) et a7f4519 (note, journal de veille et bloc « Reprise ») de la session
K-bis, note `2026-11-03-corrections-de-la-relecture-r-k.md`, qui répondent à la relecture
R-K (`2026-11-03-relecture-majoration-de-1986-a-2025.md`). Chaque source a été rouverte ici,
sans rien reprendre de K-bis ni de mémoire, dans les index LEGI (à jour au 2 novembre 2026)
et JORF (au 3 novembre 2026) de la DILA, récupérés, par `scripts/fetch/dila_cherche.py`
(`--texte`, `--num`, `--diff`, `--motif`). Rien n'a été modifié : ni règle, ni donnée, ni
test, ni fiche.

**Verdict.** **Conforme**, avec **deux écarts faibles** de rédaction, sans effet sur aucune
valeur. Aucun calcul n'a changé : ddb8824 et a7f4519 ne touchent ni le code, ni un test, ni
un témoin ; le paquet de ddb8824 ne diffère du précédent que par deux notes ; refait ici sur
le dernier `main`, il ne change rien. Chaque citation qu'ajoutent les deux commits est
exacte, mot pour mot : 26 fragments sur 26, vérifiés par un script contre les textes de
l'index (les 7 autres citent l'ancienne rédaction de la fiche, non une source). Le décret
n° 99-875 porte bien ce numéro et dit bien la date de 1952 ; deux textes que K-bis ne cite
pas le confirment. Les effets de 0,63 € et de l'arrondi, refaits à la main sur les
cotisations captées au moteur, sont exacts. Les deux écarts : la phrase « l'exercice 1952
n'a qu'une demi-année » est une inférence que l'article 45 du décret n° 52-1166 ne dit pas,
et que son article 15 contredit à la lettre (point 3) ; la ligne `manque` (« n'est pas
lu ») reste inexacte, ce que K-bis déclare (point 1).

## 1. R. 732-69, R. 732-70 et R. 732-66 : conforme, un reste déclaré

- R. 732-69, rédaction du 22 avril 2005 au 28 octobre 2017 (LEGIARTI000006597478), lue
  ici : les citations de la fiche du régime, de la fiche des règles et de la note sont
  exactes, y compris la coquille du texte (« De 1 180 F (179,80 €) », après « (179,89 €) »
  à la ligne d'avant). Les quatre décrets qu'il nomme pour les « années antérieures à
  1981 » sont bien les n° 65-346, 67-570, 74-443 et 75-97 : le n° 68-571 n'y est pas.
  `--diff` : la rédaction de 2017 (LEGIARTI000035918355) ne change que « du I de
  l'article 18 » ; celle de 2026 (LEGIARTI000053337682) récrit l'article.
- R. 732-70, rédaction de 2005 (LEGIARTI000006597479) : « A compter du 1er janvier 1990 »,
  exact.
- R. 732-66, rédaction du 8 septembre 2007 au 28 octobre 2017 (LEGIARTI000006597475) : « le
  rapport de trente-sept et demi sur » la durée, exact. Le moteur l'applique comme la fiche
  le dit : `coefficient_duree = 37.5 / (requis / 4.0)` (`liquider.py`, l. 861 ; même calcul
  à la majoration, l. 947-950, et dans `liquider.js`, l. 426-430), pour les seules périodes
  au barème `msa_proportionnelle`, les six du paquet, toutes depuis 1990 ; la valeur de
  service divisée par 172/150, la même cotisation vaut bien 172/150 fois les points.
- La phrase corrigée de la période de 1974 à 1985 et la limite
  (`docs/limites/4-regimes-incomplets.md`) disent ce que disent R. 732-69 et R. 732-70.
- Reste, déclaré par K-bis et laissé : la ligne `manque` de `msa_non_salaries.yaml`
  (ligne 26, « Le barème en points d'avant 1990 n'est pas lu »), reprise mot pour mot par
  `inventaire.yaml` (l. 3145), `docs/regimes.md` (l. 199) et `docs/etat.md` (l. 127).
  Inexacte à la lettre depuis que R. 732-69 est lu : **écart faible**, déjà inscrit au
  `reste` du journal de K-bis.

## 2. Le décret n° 68-571 ôté du barème : conforme

R. 732-69 ne le nomme pas (point 1). Sa notice au JORF (JORFTEXT000000330850) : « Décret
n°68-571 du 26 juin 1968 RELATIF A LA RETRAITE COMPLEMENTAIRE DE L'ASSURANCE VIEILLESSE DES
PERSONNES NON SALARIEES DES PROFESSIONS AGRICOLES », « VALIDATION D'ANNUITES
SUPPLEMENTAIRES ». L'article 2 du décret n° 86-1084 (LEGIARTI000006769405), lu ici, dit ce
qu'il fait : « sont exclues les années pour lesquelles des points supplémentaires ont été
accordés en application du décret susvisé du 26 juin 1968 » : des points de plus pour des
années validées, non un barème. Le retrait est justifié par le texte ; la fiche garde, à
juste titre, ces années parmi ce que le modèle ne connaît pas.

## 3. Le 1er juillet 1952 et le décret n° 52-1166 : conforme, un écart faible

- **Le décret n° 99-875.** Le numéro est juste, et la surprise s'explique : c'est un texte
  du 13 octobre 1999, « portant application de l'article 30 de la loi n° 99-574 du 9
  juillet 1999 d'orientation agricole » (attribution gratuite de points de retraite
  proportionnelle), dont l'article 2, dans sa seule rédaction du 23 février 2001 au 2 mars
  2002 (LEGIARTI000006779656), lue ici, borne les années revalorisables : « sans que les
  années retenues puissent être antérieures à la date de création du régime d'assurance
  vieillesse des professions non salariées agricoles, à savoir le 1er juillet 1952 pour la
  métropole ou le 1er janvier 1964 pour les départements d'outre-mer ». La citation de
  K-bis est exacte, et ses dates aussi ; les deux rédactions d'avant (LEGIARTI000006779654
  et LEGIARTI000006779655) disaient « les années comprises entre le 1er juillet 1952 et le
  31 décembre 1998 ». Source indirecte, mais explicite, et confirmée par deux textes plus
  proches, lus ici, que K-bis ne cite pas : le décret n° 55-753, article 18 (du 3 juin 1955
  au 22 avril 2005, LEGIARTI000006763581) : « Les années d'activité postérieures au 1er
  juillet 1952 ne sont prises en considération que si elles ont donné lieu au payement des
  cotisations prévues à l'article 19 de la loi du 10 juillet 1952 modifiée » ; la loi
  n° 60-768, article 5 (LEGIARTI000006758011) : les périodes « antérieures au 1er janvier
  1949 ou, dans les professions agricoles, au 1er juillet 1952 ». La loi n° 52-799 n'est,
  au JORF, que par sa notice (JORFTEXT000000512405), et LEGI n'en a pas le texte : vérifié.
  La borne de D. 732-77 n'exclut donc rien de ce que le modèle compte : conforme.
- **Le décret n° 52-1166**, lu ici. Article 45 (LEGIARTI000019272803, du 19 octobre 1952,
  sans fin) : « Pour l'exercice 1952, les cotisations professionnelles visées aux articles
  20 et 21 de la loi du 10 juillet 1952 sont égales à la moitié des cotisations
  annuelles. » Article 15 (LEGIARTI000019272718) : « La double cotisation professionnelle
  prévue à l'article 19 de la loi du 10 juillet 1952 est due pour chaque exercice
  commençant au 1er janvier et finissant au 31 décembre. » Les deux citations sont
  exactes.
- **Écart faible, de rédaction.** La fiche des règles (« Mais l'exercice 1952 n'a qu'une
  demi-année : » suivi de l'article 45) et la note de K-bis (« L'exercice 1952 n'a qu'une
  demi-année ») attribuent à l'article 45 ce qu'il ne dit pas : il divise par deux les
  cotisations des articles 20 et 21, et l'article 15 fait commencer chaque exercice au 1er
  janvier. Que 1952 ne couvre que six mois se tire du 1er juillet 1952, non de l'article
  45 ; et que la moitié vaille aussi pour la « double cotisation » de l'article 19, celle
  dont le décret n° 55-753 fait dépendre la prise en compte des années, aucun texte lu ne
  le dit. La limite, qui écrit « dont le régime ne couvre que la seconde moitié et ne
  prélève que la moitié de la cotisation annuelle », est plus juste. Sans effet sur aucune
  valeur : la convention et son effet au plus restent ceux que K-bis déclare.
- Ce que le texte ne tranche pas est déclaré : les points de 1952 et le compte de P, dans
  `a_relire` de `retraite_proportionnelle_msa`, comme convention ; la cotisation de 1952,
  prélevée entière dans toute la pension proportionnelle, au bloc « Reprise » comme étape à
  venir. Conforme.

## 4. L'effet de 0,63 € : refait à la main, exact

Les cotisations que le moteur Python passe à
`majoration_des_points_de_1952_a_1972_d_avant_2026` pour le témoin
`statut_exploitant_agricole_1925`, captées ici par un script de brouillon qui simule sa
requête (`tests/outils_pont.py`, `Saisies`) : 21 années de chef, de 1952 à 1972 ; valeur de
service 2,473 812 € ; rendement 0,06 ; cotisation de 1952 revalorisée 417,269 6 € ; somme
15 584,822 7 €. Le moteur rend 46,754 47 €, 5 %, P = 17,999 78 ; le témoin du portage,
« 46.75 € (5.00% pour une moyenne de 18.00 points par an, décret n° 86-1084, article 2) ».

À la main : 15 584,822 7 × 0,06 = 935,089 4 € ; P = 935,089 4 / 2,473 812 / 21 = 18,00 ;
compris entre 15 et 19,51, T = 5 % ; majoration 0,05 × 935,089 4 = 46,754 5 €. À la moitié de
1952 : 15 584,822 7 − 208,634 8 = 15 376,187 9 € ; × 0,06 = 922,571 3 € ; P = 17,76 sur 21
années, 18,19 sur 20,5, 5 % dans les deux cas ; majoration 46,128 6 €. Écart :
46,754 5 − 46,128 6 = 0,625 9 €, soit 0,63 € par an : exact. La moitié de la cotisation de
1952 dans le reste de la pension : 417,269 6 × 0,06 / 2 = 12,52 € : exact. Les deux autres
témoins que la majoration touche commencent en 1956 (né en 1935, 17 années) et en 1966 (né
en 1945, 7 années), captés de même : le témoin de 1925 est bien le seul qui ait 1952.

## 5. L'arrondi : refait à la main, exact

- R. 732-67 (LEGIARTI000053328816, depuis le 1er janvier 2026) : « Sauf si le résultat est
  déjà entier, les nombres de points annuels ainsi obtenus sont arrondis aux entiers
  supérieurs », exact ; ni D. 732-77 (LEGIARTI000006597491) ni l'article 2 du décret
  n° 86-1084, relus ici, n'écrivent d'arrondi : la convention est déclarée.
- T au centième : |ΔT| ≤ 0,005 point, soit 0,005 % de la pension des années de la période ;
  au point entier, 0,5 % : exact. Témoin né en 1945 (2009), capté : somme 9 233,215 8 €,
  × 0,06 = 553,993 €, P = 22,955 6, T = 3,19 × 22,955 6 − 57,23 = 15,998 5 % ; à 16 % :
  0,001 5 % × 553,993 = 0,008 5 €, « 0,01 € » dans la fiche, « 0,008 € » dans la note :
  exact. Témoins de 1989 et 1999 (P = 18,00 et 18,84) : 5 %, rien ne bouge.
- Un point au plus pour le total, soit une valeur de service : 2,473 812, 2,982 180 et
  3,447 601 €, celles que le moteur passe pour les trois témoins (rapport de durée de 1,
  tous nés avant 1949) : exact. Un point au plus par année arrondie : 21, 17 et 7 années :
  exact.

## 6. L'identifiant du décret n° 86-1084 : conforme

LEGITEXT000006065220 est bien le « Décret n°86-1084 du 7 octobre 1986 relatif à
l'harmonisation des pensions de retraite des personnes non-salariées de l'agriculture
[...] » ; JORFTEXT000000870113, sa publication du 8 octobre 1986. Ses visas citent, mot pour
mot, « le décret n° 68-571 du 26 juin 1968 modifié relatif à la retraite complémentaire de
l'assurance vieillesse des personnes non-salariées des professions agricoles » et « le
décret n° 81-790 du 18 août 1981 portant relèvement exceptionnel des retraites
proportionnelles des personnes non-salariées de l'agriculture ». Le n° 81-790 : au JORF,
la seule notice JORFTEXT000000335107 (« Texte totalement abrogé ») et les textes qui le
visent ; dans LEGI, aucun texte à lui. Le décret n° 2005-368, article 3
(LEGIARTI000006240372), abroge bien « 65° Le décret n° 81-790 » et « 78° Le décret
n° 86-1084 ». Le décret n° 80-808 (LEGITEXT000006063328) vise bien le n° 65-346 dans les
termes cités. Les n° 65-346 et 75-97 ne sont, au JORF, que cités par R. 732-69 (décret
n° 2005-368) et par le décret n° 2025-1409 ; les autres réponses de l'index à ces
numéros n'en contiennent aucune occurrence. Les notices des n° 67-570
(JORFTEXT000000514415) et 74-443 (JORFTEXT000000328985) : conformes.

## 7. Les tests et le paquet

- Aucun code, aucun test, aucun témoin : `git show --stat` de ddb8824 ne touche que deux
  fiches, la limite, quatre chiffres ancrés du poids du paquet, dans trois documents
  (5 872 → 5 873 Ko), et
  `moteur/donnees.json` ; a7f4519, la note, le journal et la feuille de route. Le paquet de
  ddb8824 comparé au précédent, champ par champ : deux différences, les notes des périodes
  1 et 2 du régime `msa_non_salaries`.
- `python scripts/construire_donnees.py` sur le dernier `main` (3351fbd) : `git status`
  vide, le paquet ne change pas.
- `python -m pytest -m rapide` : 4 269 réussis, 6 sautés ; sous `PRESOMPTIONS_DECALEES=1` :
  4 071 réussis, 204 sautés (davantage que chez K-bis : `main` a avancé depuis).
  `tests/test_simulateur.py -k "majoration or agricole"` : 19 réussis ; sous les
  présomptions décalées, 14 réussis, 5 sautés. `tests/test_pont.py -k refait`, où le moteur
  Python refait chaque témoin du portage : 2 réussis. Le moteur Python rend, pour les trois
  témoins, les valeurs du portage (points 4 et 5).
