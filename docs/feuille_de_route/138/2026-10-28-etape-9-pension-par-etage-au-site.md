# Étape 9, suite de la quatorzième partie : la pension par étage et le revenu autour du départ, sur la page des résultats

**La demande.** Le point « Pour les pages » de la note du 18 octobre
(`2026-10-18-etape-9-pension-par-etage.md`) : la page des résultats montre,
pour la carrière saisie, la pension du départ par étage en part du dernier
revenu, à côté du taux de remplacement, et le revenu des dix années de part et
d'autre du départ, avant ou après impôt (`pensionParEtage`,
`revenusAutourDuDepart`, du portage). Ni la révision de 2026 du COR, ni
l'impôt dans les cartes de résultats, qui restent au propriétaire. Session de
la vague du 28 octobre, la seule sur les pages.

**Ce qui est fait.**

- *Au site* (`pages.js`, `avantEtApresLeDepart`) : le dépliant « Votre revenu,
  avant et après le départ », sous « Pour aller plus loin », avant « Partir
  plus tôt ou plus tard ». Son premier tableau donne, sous les quatre
  systèmes, chaque étage de la pension du premier mois servi en part du
  dernier revenu — la base, la complémentaire, le régime intégré,
  l'additionnelle, le compte notionnel, le pilier capitalisé —, puis leur
  somme, le taux de remplacement brut que donne la carte de chaque système,
  le taux net et le taux après impôt de l'OCDE ; les parts, arrondies au
  dixième de point, font leur total (`arrondisQuiSadditionnent`). Le second
  donne, au système 1, chaque année de dix ans avant celle du départ à dix ans
  après : le revenu d'activité et la pension bruts, leur net avant impôt,
  l'impôt et ce qu'il laisse, par an, en euros de la page ; l'année du départ
  se dit en toutes lettres, « 2044 (départ) ». Le net et l'impôt suivent la
  convention de « Partir plus tôt ou plus tard » : une personne seule, le
  barème suivant les prix. Rien pour une saisie par la pension, dont la
  carrière est reconstituée. Les cartes ne changent pas.
- *Le budget de Simuler tout déplié* (`BUDGETS_DEPLIES`, action 173) passe de
  6 850 à 7 310 mots : la simulation témoin en faisait 6 835, le dépliant en
  ajoute 462, dont 426 dans ses deux tableaux. Le chapeau ne redit pas que la
  somme des étages est le taux de remplacement : la rangée le dit. Un
  graphique n'en aurait pas épargné : le tableau de ses points compte aussi.
- *Deux écarts, que la page dit.* Comme tout le cycle de vie, la pension par
  étage ne compte ni le minimum vieillesse ni la garantie vieillesse, que
  l'impôt finance ; la carte du système 4 compte la garantie. À 1 100 € bruts
  par mois (né en 1985, entré en 2010), elle y donne 70,9 % de taux de
  remplacement, quand ses étages font 47,9 % : une phrase le dit sous le
  tableau, au taux de la carte, dès que les deux diffèrent au dixième. Sans
  fiche de paie, l'exploitant agricole n'a dans le modèle ni revenu net ni
  revenu imposable : un tiret pour le net, l'impôt et l'après-impôt, plutôt
  qu'un impôt nul sur ses années de travail.
- *Les tests* (`tests/test_web.py`, « la pension par étage, et le revenu
  autour du départ ») : le premier tableau contre `pensionParEtage`, les
  étages du système 1 posés à la main sur les pensions de ses régimes, son
  taux brut contre celui des cartes ; le second contre
  `revenusAutourDuDepart`, de 2034 à 2054 pour le né le 15 janvier 1980 parti
  en février 2044, son année du départ au douzième du dernier revenu
  annualisé ; l'exploitant ; la garantie vieillesse. Chacun vu rouge avant
  son code.

**Ce que montrent les mesures.** Le né le 15 janvier 1980, parti en février
2044 : au système 1, 38,8 % de base et 13,5 de complémentaire, 52,3 % en tout,
59,9 % net, 65,1 % après impôt ; 15,8, 39,0 et 42,9 % bruts aux systèmes 2 à
4. Après impôt, en euros de 2026, 37 730 € en 2043, sa dernière année pleine,
25 940 € l'année du départ, puis 24 925 € par an. Des 82 rendus de page des
témoins, les 52 qui gagnent le dépliant ne changent que de lui ; les six pages
de résultats qui ne l'ont pas sont des saisies par la pension. Les neuf pages
toutes faites ne bougent pas : aucune ne porte de résultats. Dans Chromium,
rien ne déborde, de 320 à 1 440 points (`test_ecrans.py`) ; sur un téléphone,
les deux tableaux se replient en cartes, et les vingt et une années font
environ sept écrans.

**Vu en passant, hors des pages.** À `HEAD` (92288d6), sans ce changement,
les confrontations des deux moteurs échouent : le portage contre les témoins
de simulation (`test_le_portage_javascript_retrouve_les_chiffres_du_modele`),
`test_pont.py`, `test_coupures_au_mois.py`, la surcote parentale,
`test_cycle_de_vie_script.py` ; `construire_donnees.py --verifier` dit
`data/derive/equilibre.json` périmé. Ni les témoins de simulation refaits ni
les chiffres ancrés que `verifier_prose.py --corriger` récrivait du même coup
(la concordance du portage y tombait à 99,9 %) n'ont donc été commités. La
course de GitHub, qui refait les fichiers fabriqués, dira ce qu'il en reste.
Au site, dans « Partir plus tôt ou plus tard », l'âge et l'année de chaque
rangée se lisent collés, « 63 ans et 9 moisen 2032 » : leur `span.aide` n'a de
style que dans « Comme votre estimation officielle ».

**Ce qui reste** de l'étape, dans l'ordre :

1. *La révision de 2026*, à la réponse du COR (note du 18 octobre, « la
   révision de 2026 »), inchangée ; la question au secrétariat général reste
   au propriétaire.
2. Inchangés : la rémunération moyenne par tête du COR, à la session des
   données ; le rendement de −2,9 % du cadre né en 1975 sous le scénario 2.
3. *À la session des pages, si elle le juge utile* : dessiner le second
   tableau, comme Typfallsmodellen ses deux figures, pour un téléphone ; et
   l'âge collé à son année dans « Partir plus tôt ou plus tard ».
