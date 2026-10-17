# Étape 18, septième partie : la Lodeom, outre-mer, à la place de la réduction générale

**La demande.** La session n° 3 de la vague du 17 octobre 2026, où le
propriétaire demandait « toutes les tâches qui n'ont pas besoin de mes
décisions » : l'action 138, le premier point de la note
`…-plafond-rci-taux-propres-assiette-abattue.md`, la Lodeom. Coupé au registre
le 14 octobre, du rang « léger ou nul », le point a été rouvert par la vague,
comme les dispenses l'avaient été le 16. Les classes d'avant 1973 restent à une
autre session. `pages.js`, la saisie et `textes.py --inscrire` n'ont pas été
touchés.

**Ce que faisait le dépôt.** La fiche de paie donnait la réduction générale
dégressive unique à tout salarié du privé, Antilles, Guyane et Réunion compris
(registre, `modele_social`, chantier 138.18).

**Ce que disent les textes**, lus le jour même dans les index LEGI et JORF, mis
à jour au 17 octobre (détail au journal de veille du jour).

- *L. 752-3-2* (LEGIARTI000053280451, du 1er janvier au 30 juin 2026 ; loi
  n° 2025-1403, article 40) : en Guadeloupe, en Guyane, en Martinique et à La
  Réunion, l'employeur de moins de onze salariés ou d'un secteur que le II
  énumère est exonéré des cotisations du I de L. 241-13 « dans sa rédaction
  antérieure » à la loi de financement pour 2025. Trois barèmes (III) :
  compétitivité, totale sous 1,3 SMIC, nulle à 2,2 ; compétitivité renforcée,
  2 et 2,7 ; innovation et croissance, 1,7, aux cotisations de 1,7 SMIC jusqu'à
  2,5, nulle à 3,5. T est borné à la somme des taux du périmètre « pour une
  rémunération égale au » SMIC (IV) ; rien ne se cumule (VI). Les rédactions du
  1er juillet 2026 et de 2028, qui ouvre Mayotte, gardent les seuils.
- *D. 752-7* (LEGIARTI000052196887) : les trois formules dégressives ; T, la
  somme des taux du périmètre ; le SMIC de D. 241-7. Aucun arrondi n'y est écrit.
- *L. 241-13, I, d'avant 2025* (LEGIARTI000042912368) : le périmètre, celui des
  composantes de la réduction générale du dépôt.
- *La loi n° 2025-1403, article 40, V et VI*, et *le décret n° 2025-1446,
  article 3* : l'employeur d'une réduction spécifique non cumulable avec la
  réduction générale garde la maladie à 7 % et la famille à 3,45 % jusqu'à 2,5
  et 3,5 fois le SMIC du 31 décembre 2023, 11,52 € de l'heure (arrêté du
  26 avril 2023) : 52 416 € et 73 382,40 € par an.
- *Comment la caisse l'applique.* Le BOSS et les pages de l'Urssaf refusent la
  connexion de la session. Lus à leur place : la fiche Sage de janvier 2026 sur
  le barème de compétitivité renforcée, qui cite le BOSS (§ 1380 : T vaut
  0,3241 dans une entreprise de cinquante salariés et plus, 0,3201 en deçà ; le
  coefficient s'arrondit à quatre décimales, plafonné à T) ; le simulateur de
  l'Urssaf (mon-entreprise, `lodeom.publicodes`, branche master), qui compose T
  de même, arrondit de même et écarte la réduction générale dès que la Lodeom
  s'applique. Aucun exemple chiffré de 2026 n'a été lu à la source.

**Ce qui est fait.**

- *Les données* : le bloc `lodeom` de `prelevements_remuneration.yaml`, au seul
  profil `salarie_prive` : T et ses composantes — celles de la réduction
  générale, la maladie et la famille à leurs taux réduits —, les trois barèmes,
  les deux taux réduits et le SMIC de référence.
- *Le modèle* : `BaremeLodeom` et `Lodeom` ; `ConstructeurFiche(profil, lodeom)`
  met l'exonération à la place de la réduction générale, qui ne la relaie pas
  au-delà de son seuil de sortie, et rend les taux réduits ; T se refait des
  fiches de régime, comme le coefficient de la réduction générale ;
  `FicheDePaie.lodeom` dit le barème appliqué. La ligne du relevé
  (`LigneRelevee.lodeom`), la chronologie et l'année de carrière
  (`AnneeCarriere.lodeom`) le portent, la prolongation du relevé et celle de la
  carrière le gardent, et `remuneration_de_la_carriere` prend celui de chaque
  année. Les jumeaux JavaScript suivent ; le paquet porte le bloc pour le seul
  profil qui l'a, et garde sa version.
- *Le registre* : le point de `modele_social` passe de `coupe` à `repris`. Les
  limites de la fiche de paie (5 ter) disent ce qui est servi et ce qui reste.
- *Les tests* : `tests/test_lodeom.py`, dix-huit cas posés à la main depuis les
  textes, dont le jumeau, fiche par fiche et carrière par carrière.

**Ce que montrent les mesures** (fiche de 2026, salarié non cadre d'une
entreprise de cinquante salariés et plus, coût du travail par mois, chaque
barème contre la réduction générale).

- Au SMIC, rien : les deux allègements effacent tout le périmètre.
- À 1,2 SMIC, 331 € de moins sous chaque barème ; à 1,5 SMIC, 445 € sous la
  compétitivité, 734 € sous les deux autres ; à 2 SMIC, 259, 1 270 et 1 093 € ;
  à 3 SMIC, 98, 98 et 601 €.
- À 2,5 SMIC sous la compétitivité, 40 € de plus : la Lodeom s'est éteinte à
  2,2 SMIC, la réduction générale ne la relaie pas, et la maladie a quitté son
  taux réduit à 52 416 €.
- Le net du droit en vigueur ne bouge pas. Sous l'incidence intégrale, le gain
  net de la proposition en 2026 descend de 109 à 69 € par mois à 26 000 € de
  brut annuel, sous chaque barème, de 158 à 143 € (compétitivité) ou 90 €
  (renforcée) à 34 000 €, de 217 à 214 ou 137 € à 44 000 € : la proposition
  baisse des taux que la Lodeom effaçait déjà, et le pilier capitalisé, hors du
  périmètre, se paie en entier.

**Pour les pages**, que la session du site tient. Un champ, offert au seul
salarié du privé : « Votre employeur, en Guadeloupe, en Guyane, en Martinique
ou à La Réunion, applique la Lodeom : non / barème de compétitivité / de
compétitivité renforcée / d'innovation et de croissance », porté par la
période d'emploi (`lodeom` de la chronologie) ou la ligne du relevé
(`LigneRelevee.lodeom`). `FicheDePaie.lodeom` dit le barème, si la page veut
nommer la ligne « exonération Lodeom » plutôt que « réduction générale ».

**Ce qui reste**, de ce point. Au BOSS et sur la page de l'Urssaf, quand la
session pourra les lire : l'arrondi du coefficient, et surtout si l'employeur
de la Lodeom reprend la réduction générale au-delà du seuil de sortie, jusqu'à
3 SMIC — le simulateur de l'Urssaf dit non, le VI ne le dit pas mot pour mot ;
elle vaudrait 2,68 % du brut à 2,5 SMIC. Un exemple chiffré de 2026. Restent
dehors Saint-Barthélemy et Saint-Martin (L. 752-3-3), Mayotte dès le
1er juillet 2026 (action 121), l'employeur de moins de cinquante salariés (T à
0,3201), que l'employeur type du dépôt écarte, et les barèmes d'avant 2026, que
la fiche, millésime 2026, ne lit pas. De l'étape, une session : au fac-similé,
les classes d'avant 1973.
