# Le simulateur de SUD éducation, rejoué au droit de sa date

**La demande**, le 24 octobre 2026 : la deuxième vague du lot que le
propriétaire a demandé ce jour-là, une session par tâche qui se mène sans
lui. Pour l'action 137, « le modèle suivant dans l'ordre du registre : le
simulateur de SUD éducation. Comme pour Catala et modele-as : rejouer son
calcul au droit de sa date, confronter chaque écart au dépôt, et dire de qui
est l'erreur. »

**Fait, le 24 octobre 2026 : le calcul rejoué ; le dépôt a raison partout,
et le simulateur a deux erreurs de plus que les cinq du registre, dont l'une,
sa décote, se dédouble.**

- *Ce qui a tourné.* simulateur-retraites au commit `eec62c9`, encore sa
  tête, cloné à part : son `static/js/retraites.js`, exécuté sous Node dans
  un contexte `vm` dont le faux `document` rend la saisie et garde ce que
  `calcul()` écrit, sur tout son menu — huit corps, nés de 1958 à 1998,
  entrés de 20 à 28 ans, partis de 62 à 67 ans : 17 712 carrières, sans
  direction d'école ni primes. Sa date : ses constantes sont du 13 octobre
  2019 (`7626b4d`), son calcul du 24 décembre (`4ffa115`) ; son minimum
  contributif est le majoré de 2019, 8 347,09 € par an, et son point celui
  de février 2017, au millième, 4,686 € par mois. Ses pensions partent de
  2020 : le droit de sa date est celui des lois de 2010 et de 2014, que le
  dépôt garde au droit contrefactuel `au_31_aout_2023`. Le moteur y a liquidé
  ses 11 070 carrières de titulaire sur son traitement et ses services — le
  relevé d'années pleines d'un assuré né un 1er janvier, de l'anniversaire
  du début à celui du départ —, la pension prise avant le minimum garanti
  (`total_contributif`). Les fichiers de rejeu sont restés hors du dépôt.
- *Ce qui concorde.* Le dépôt a raison partout : sur les 11 070 carrières,
  ses durées, ses services, ses décotes, ses surcotes et ses proratas sont
  ceux que L. 161-17-3 (version de 2014), L. 13 et L. 14 du code des
  pensions (versions de 2014 et de 2018, en vigueur jusqu'au 31 août 2023),
  lus dans l'index LEGI, donnent à la main, la décote s'annulant à la limite
  d'âge, soixante-sept ans, dès la génération 1958. Le simulateur lui rend
  sa pension, au centime qu'il tronque, sur 3 665 d'entre elles : partout où
  ni la décote ni la durée ne l'égarent. Ses durées de 1960 à 1998 sont
  celles de la loi de 2014 ; son point et son minimum contributif, ceux du
  dépôt pour 2019. Ce minimum contributif, que son code sert aux
  fonctionnaires, n'atteint aucun titulaire de son menu. Aux départs de 2023
  et de 2024, le relevé du dépôt porte le traitement de la dernière année au
  point du 1er janvier du départ (+ 3,5 % et + 1,5 %) : ses montants n'y
  sont pas comparés, ses durées, décotes et proratas si.
- *Ses erreurs nouvelles.* Sa table des durées commence en 1960 : il demande
  172 trimestres aux nés de 1958 et de 1959, que son menu propose, quand
  L. 161-17-3 leur en demande 167 — 540 carrières, de 28,8 % de moins à
  4,9 % de plus que le droit. L'écart du registre sur sa décote et son
  prorata se dédouble. Sa décote ne compte que les trimestres qui manquent à
  la durée, sans ceux qui séparent l'âge de la limite d'âge ni la borne de
  vingt (L. 14, I) : 4 560 carrières payées de 1,3 à 26,7 % de moins,
  jusqu'à 620 € par mois, dont tout départ à 67 ans sans la durée, que le
  texte ne décote pas. Au-delà de la durée, son prorata dépasse un et sa
  décote devient une surcote à tout âge (L. 13, I, et L. 14, III) : 2 305
  carrières payées de 0,6 à 13,7 % de plus. Et sa moyenne des contractuels
  n'est pas même la sienne : chaque année passée au sommet de la grille y
  compte pour un mois de traitement, non douze ; la boucle omet le dernier
  échelon d'une carrière qui s'y achève, et somme jusqu'à vingt-sept ans
  qu'elle divise par vingt-cinq. Aucune de ses 4 428 carrières de
  contractuel enseignant n'a sa moyenne, prise de 0,71 à 1,05 fois, et ses
  2 214 carrières d'AESH tombent toutes au minimum contributif. La direction
  d'une école de quatre classes lève bien « ReferenceError:
  anneesDirection24 is not defined ». L'écart de ses durées et de son point,
  lu contre le droit d'aujourd'hui, est récrit en retard : au droit de 2019,
  ils sont justes.
- *Ce que les tests tiennent* (`tests/test_referents.py`) : sa durée de
  chaque génération de son menu, contre celle du dépôt au droit au 31 août
  2023, sauf 1958 et 1959, à 167 trimestres ; treize carrières de titulaire,
  ce qu'il en rend et ce que le dépôt en liquide — sa pension au centime sur
  six, et sur sept le droit de 2019 posé à la main, durée, décote et
  surcote ; son point et son minimum contributif, contre les séries du dépôt
  pour 2019. Et la version que sa ligne doit nommer, vue rouge avant le
  registre. Le tableau de bord le compte confronté : 27 modèles, et 1 à
  confronter en premier.

**Ce qui reste.** Le dernier modèle à confronter en premier, dans l'ordre du
registre : Nos Retraites, au droit d'avant 2023, seul comparable. Ses
contractuels, une hypothèse sans source, ne se sont pas rejoués contre le
régime général et l'Ircantec du dépôt : la comparaison tiendrait à la façon
de ramener ses euros constants de 2019 aux salaires de chaque année. Une
piste, non suivie, pour une session du modèle : le traitement d'un
fonctionnaire parti un 1er janvier est celui de sa dernière année, que le
moteur multiplie par le rapport des points aux deux 1er janvier
(`salaire_de_reference`, `droit/liquider.py`) ; si la ligne de cette année
porte le traitement payé, « en euros courants de cette année-là », un
relèvement du point en juillet y compte une fois et demie — 1,75 % de trop
pour un départ au 1er janvier 2023. Le rejeu ne le met pas en défaut, son
traitement étant au point du 1er janvier ; il se vérifie contre la façon
dont le site saisit cette ligne. Les autres restes du bloc « Reprise » ne
bougent pas. Au propriétaire, rien à trancher ; s'il le veut, les erreurs du
simulateur se signalent à SUD éducation, ce qu'une session ne fait pas. Aux
pages, rien : le site ne lit pas le registre.

*Fichiers.* Le registre (ligne `simulateur_sud_education`), le registre des
sources (`sud_education_simulateur`), `tests/test_referents.py`,
`docs/etat.md`, la feuille de route, cette note et l'entrée du journal de
veille. Ni fiche, ni règle, ni page. Le simulateur et les fichiers de rejeu
sont restés hors du dépôt, qui n'a pas le simulateur pour dépendance.
