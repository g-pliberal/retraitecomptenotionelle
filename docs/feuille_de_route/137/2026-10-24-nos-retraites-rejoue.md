# Nos Retraites, rejoué au droit de sa date

**La demande**, le 24 octobre 2026 : la troisième vague du lot que le
propriétaire a demandé ce jour-là, une session par tâche qui se mène sans
lui. Pour l'action 137, « le dernier modèle qui reste à confronter dans
l'ordre du registre : Nos Retraites, au droit d'avant 2023. Comme pour
modele-as, Catala et le simulateur de SUD éducation : rejouer son calcul au
droit de sa date, confronter chaque écart au dépôt, et dire de qui est
l'erreur. »

**Fait, le 24 octobre 2026 : le calcul rejoué ; sur tous ses écarts, le
dépôt a raison, et le simulateur a sept erreurs de plus que les trois du
registre. Les décrets lus pour trancher sa carrière longue montrent deux
erreurs du moteur, que la grille ne voit pas toutes, et qui vont à l'étape
138.21.**

- *Ce qui a tourné.* simulateur_cas_types au commit `5e4abf1`, encore sa
  tête, cloné à part : il n'a pas de licence, et se lit, se cite et
  s'exécute hors du dépôt. Son `utils/calculationUtils.js`, sous Node, dans
  un contexte `vm`, sa ligne d'import remplacée par sa table ; son dépôt de
  données, de juin 2022, est celui d'une version antérieure, qu'il ne lit
  plus. Sa date : le 22 janvier 2023. Son état « now » est le droit de ce
  jour, les lois de 2010 et de 2014, que le dépôt garde au droit
  contrefactuel `au_31_aout_2023` ; son état « mac », le projet du 10
  janvier, ne se compare qu'à lui-même. La grille : toute sa table, nés de
  1950 à 2010, entrés de 16 à 40 ans, avec ou sans deux ans et demi sans
  validation, sans enfant, mère du privé d'un ou de trois enfants, mère
  fonctionnaire de deux — 6 832 carrières, et 112 pour les nés de 1951 au
  second semestre —, chacune à ses dix âges : 69 440 départs. Le moteur a
  liquidé les mêmes carrières, d'un assuré né le 31 mars, ou le 30
  septembre : l'âge légal y tombe en fin de trimestre civil, où le décompte
  de la caisse, en trimestres civils (circulaire Cnav 2018-04), égale le
  sien, en années ; né dans les deux premiers mois d'un trimestre, la caisse
  compte un trimestre de surcote de moins que lui. Puis, pour les 1 952
  carrières entrées avant
  vingt ans, le premier mois que le moteur ouvre, essayé de mois en mois,
  contre l'âge que dit son résumé, « peut partir dès ». Les fichiers de
  rejeu sont restés hors du dépôt.
- *Ce qui concorde.* Sa table de l'état « now » est celle du dépôt,
  génération par génération, sauf 1951. Sur les 43 644 départs que les deux
  ouvrent, 41 627 ont la même décote et la même surcote ; 25 504 sont fermés
  des deux côtés. Son résumé redonne le premier mois du moteur pour 1 206
  des 1 952 carrières entrées avant vingt ans. La bonification des mères
  fonctionnaires pour enfants nés avant 2004, « sans condition » au
  registre depuis le 4 octobre : le dépôt présume lui aussi l'interruption
  remplie par la mère, et le déclare (fiche `enfants_fonction_publique`) ;
  les deux comptent les mêmes trimestres, et l'écart, récrit, ne lui
  reproche que de taire la présomption.
- *Ses erreurs nouvelles.* Il sert à toute la génération 1951 l'âge des nés
  du second semestre, 60 ans et 4 mois, et le taux plein à 65 ans et 4
  mois, quand D. 161-2-1-9 garde le premier semestre à « soixante ans » :
  373 départs. Sa décote compte 1,25 % par trimestre à toutes les
  générations ; le II de R. 351-27 en demande 1,625 % en 1950, 1,5 % en 1951
  et 1,375 % en 1952 : 588 départs. Il compte en fractions de trimestre la
  durée jusqu'à un âge du taux plein qui n'est pas entier, que le I du même
  article arrondit « au chiffre immédiatement supérieur » : 452 départs, de
  1951 à 1954. Il ouvre la carrière longue à l'âge légal moins deux ans à
  tout début avant vingt ans, dès 58 ans en 1950, quand les rédactions de
  2003 et de 2010 de D. 351-1-1 ne l'ouvraient avant soixante ans qu'aux
  débuts avant seize ou dix-sept ans : 56 départs, et 92 résumés qui
  avancent la date jusqu'à la génération 1954. À sa fonctionnaire, il sert
  la décote du régime général, sans le coefficient ni l'âge d'annulation que
  l'article 66, III, de la loi n° 2003-775 fait monter jusqu'en 2019 : 518
  départs, des générations 1950 à 1957 ; et une surcote jusqu'à 67 ans,
  quand la limite d'âge la radie à 65 ans si elle est née avant juillet
  1951, ou à celle de sa génération : 178 départs. Enfin, une année de
  naissance hors de sa table, que son formulaire accepte de 1900 à 2022,
  arrête le calcul : « TypeError: Cannot read properties of undefined
  (reading 'DTP_mac') ». Les sept sont au registre ; ses deux états
  périmés y sont récrits en retard.
- *Ce qui n'est l'erreur de personne.* 144 départs de mères parties depuis
  septembre 2026, que le moteur ouvre et non lui, et 426 carrières de mères
  au résumé : le contrefactuel ne change que l'âge légal, la durée requise
  et les portes de la carrière longue, et garde la majoration pour enfants
  réputée cotisée de D. 351-1-2-1, de 2026. Au droit de janvier 2023, le
  simulateur a raison, et le dépôt le déclare (`DROITS_CONTREFACTUELS`,
  `scenarios/actuel.py`) ; un test le tient.
- *Les erreurs du dépôt.* Pour trancher sa carrière longue, les trois
  rédactions de D. 351-1-1 d'avant 2023, relues dans l'index LEGI. Celle du
  2 juillet 2012 ne donne la porte des débuts avant dix-sept ans, à 59 ans
  et 8 mois, qu'aux nés de 1952 et de 1953, et ses portes des débuts avant
  seize ans génération par génération ; le moteur, qui retient pour chaque
  porte la ligne de la plus haute génération qui ne dépasse pas celle de
  l'assuré, les étend à toutes les suivantes. Le né de 1955 et après entré
  à seize ans, sa durée cotisée atteinte, y part à 59 ans et 8 mois — au
  droit en vigueur, de novembre
  2012 à août 2023, vu pour 1955, 1958, 1960 et 1962 ; au droit au 31 août
  2023, à toute date —, quand le texte ne lui ouvre que 60 ans : ce que dit
  le résumé du simulateur pour 224 carrières de la grille, de 1955 à 2010
  (pour 1954, les deux ont tort, 59 ans et 7 mois chez lui, 59 ans et 8 au
  moteur). Et les rédactions de 2003 et de 2010 n'ouvraient la carrière
  longue qu'avec une durée d'assurance égale à la durée requise « majorée
  de huit trimestres », que le moteur ne vérifie pas : le né du 31 mars
  1950 entré à seize ans, deux ans et demi sans validation, part à 59 ans,
  en 2009, avec 162 trimestres. La
  grille ne voit la première qu'au résumé, au mois près, et la seconde
  nulle part, le simulateur la commettant aussi. Elles ne sont pas
  corrigées ici : la table est certifiée contre le texte
  (`scripts/verifier_donnees.py`), et la corriger touche la donnée, sa
  certification, les deux moteurs et les témoins, une étape du modèle. Elle
  est ouverte à l'action 138, l'étape 21, comme TRAJECTOiRE avait ouvert la
  vingtième ; le registre en porte le point, que le simulateur fait mieux
  (`fait_mieux`, 138.21).
- *Ce que les tests tiennent* (`tests/test_referents.py`) : sa table de
  l'état « now », génération par génération, contre les tables du moteur
  posées comme son droit contrefactuel, et 1951 à part ; dix-neuf départs,
  ce qu'il en rend et ce que le moteur en liquide — le même sur dix, et sur
  neuf le droit de sa date posé à la main, texte cité ; la mère de 1970, que
  le contrefactuel ouvre par D. 351-1-2-1, et pas sans enfant. Et la
  version que sa ligne doit nommer, vue rouge avant le registre. Le tableau
  de bord le compte confronté, 28 modèles, et ne compte plus de modèle à
  confronter en premier : sa phrase, qui en comptait zéro devant une liste
  vide, dit qu'il n'en reste aucun (`scripts/tableau_de_bord.py`, le test vu
  rouge d'abord).

**Ce qui reste.** Les treize « jamais confrontés » le sont tous. L'étape
138.21, pour une session du modèle : les portes de la carrière longue
bornées aux générations que chaque rédaction nomme, et la durée majorée de
huit trimestres avant novembre 2012. Le premier reste de l'action 137 :
l'Agirc-Arrco d'EDIFIS ; puis l'ASPA de Saphir et EUROMOD de 2015 à 2025.
Au propriétaire, rien à trancher ; s'il le veut, les erreurs du simulateur
se signalent au collectif Nos Retraites, ce qu'une session ne fait pas. Aux
pages, rien : le site ne lit pas le registre.

*Fichiers.* Le registre (ligne `nosretraites_cas_types`), le registre des
sources (`nosretraites_simulateur_cas_types`), `tests/test_referents.py`,
`scripts/tableau_de_bord.py`, `docs/etat.md`, la feuille de route (le bloc
« Reprise » de l'action 137, l'étape 21 de l'action 138), cette note et
l'entrée du journal de veille. Ni fiche, ni règle, ni page. Le simulateur et
les fichiers de rejeu sont restés hors du dépôt, qui n'a pas le droit de le
copier.
