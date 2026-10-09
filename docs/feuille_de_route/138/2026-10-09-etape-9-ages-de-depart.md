# Étape 9, troisième partie : les indicateurs à chaque âge de départ, nets, sous les trois productivités du COR

**La demande.** Le propriétaire fait passer, le 9 octobre 2026, avant les
prélèvements de l'IPP, le troisième point de « Ce qui reste » de la note du
7 octobre : les indicateurs de cycle de vie à chaque âge de départ, de l'âge
d'ouverture à l'annulation de la décote, en net, sous plusieurs hypothèses de
productivité, avec la pension rapportée à l'ASPA — le point de TRAJECTOiRE du
chantier 138.9, `a_reprendre` au registre.

**Ce que dit TRAJECTOiRE, lu le jour même** (commit `0963b57`, lu sans être
copié : EUPL).

- `inst/scripts/casTypesCOR.R` balaie chaque cas type de l'âge de la carrière
  longue, ou de l'âge d'ouverture s'il est plus tôt, à l'âge d'annulation de
  la décote, par pas de 0,25 an, sous quatre croissances du salaire moyen :
  0,4, 0,7, 1 et 1,3 %. Le COR a retiré la dernière en juin 2025.
- Son rapport (`inst/templates/rapport_casTypesCOR.Rmd`) divise la pension
  nette mensuelle en euros courants, fois douze, par l'ASPA de la date de
  liquidation, « revalorisée par les prix » ; il rapporte la pension nette à
  la dernière rémunération nette d'une année pleine, en euros courants,
  constants ou en salaire moyen, « afin d'éviter des années incomplètes en
  fin de carrière ».
- `R/fonctionsCalculsPensions.R` (l. 4785-4786) : `txRemplacementNet`, la
  pension nette de la liquidation, RAFP comprise, sur la rémunération nette de
  l'année d'avant, en euros constants ; `txRemplacementNetSmpt`, la même en
  salaire moyen. `R/fonctionsCalculsDivers.R` : la rémunération nette perd la
  CSG-CRDS de l'année sur 98,25 % du brut, la cotisation maladie et, hors
  fonction publique, l'assurance chômage, puis les cotisations salariales de
  retraite ; les primes d'un fonctionnaire, la CSG-CRDS et la RAFP, sans la
  retenue ; la pension, le taux de la catégorie de CSG du cas à son année, et
  la maladie de 1 % de l'Agirc-Arrco quelle que soit la catégorie.

**Ce qui est fait.**

- *Le balayage* (`cycle_de_vie.py`). `ages_de_depart` : les âges « au plus
  tôt » et « au taux plein automatique » de `pilote.ages_de_l_estimation`,
  chacun un point fixe, de trimestre en trimestre, le dernier toujours l'âge
  d'annulation. `balayage` : un `Depart` par âge, les indicateurs nets des six
  systèmes, la pension nette du premier mois servi (`pension_au_depart`),
  rapportée au minimum vieillesse d'une personne seule de l'année du départ
  (`minimum_vieillesse` : l'ASPA, ses deux étages avant 2007), et le taux de
  remplacement net en euros courants, constants et en salaire moyen
  (`RemplacementNet`), sur la dernière année travaillée en entier
  (`derniere_annee_pleine`). `CasType.carriere_a` bâtit la carrière d'un cas
  type à un âge donné ; `hypotheses_de_productivite` énumère les trois
  scénarios du COR. Le scénario 6, que son âge légal reporte à 65 ans, se
  rapporte à l'ASPA et au revenu de son propre départ.
- *Nets sur nets.* Le revenu d'activité net est ce que laisse la fiche de paie
  du droit en vigueur (`revenus_nets`, `remuneration.fiche_depuis_brut`), aux
  taux hors retraite de l'année courante. Sous une convention nette, le taux
  d'annuité, le remplacement sur le cycle de vie et au décès rapportent
  désormais la pension nette au revenu net ; ils la rapportaient au brut, ce
  que `--cor` imprimait. Le patrimoine reste en années de dernier revenu
  brut, comme l'OCDE exprime le sien.
- *Les primes d'un fonctionnaire.* La fiche de paie a pour assiette le
  traitement (`docs/limites/5-ante-bis-fiche-de-paie.md`, 5 ter) : elle se lit
  sur lui, et les primes perdent les mêmes prélèvements hors retraite, sans
  la retenue. La RAFP reste hors du net, comme elle est hors des flux.
- *Le script* : `python scripts/cycle_de_vie.py --ages salaire_moyen
  --generations 1970,2000`, avec `--productivites`, `--scenarios`, `--cor`,
  `--json`.
- *Les tests* : dix cas de plus dans `tests/test_cycle_de_vie.py` (rapide),
  un dans `tests/test_cycle_de_vie_references.py`.
- *Le registre* : le point de TRAJECTOiRE, repris.

**Ce que montre la confrontation à TRAJECTOiRE.** Sur les soixante-quinze
carrières de son témoin, au premier âge du taux plein et sous un salaire
moyen à +1 %, sa pension, RAFP comprise, nette au barème de sa catégorie de
CSG, rapportée au revenu net que le dépôt tire de la même carrière, retrouve
son `txRemplacementNet` à 1,1 % près sur les 46 cas où les deux modèles
prélèvent la même chose, et son `txRemplacementNetSmpt` à 1,4 % près. Les
autres écarts sont déclarés avec leur cause :

- *avant 2018* (14 cas, 0,963 à 0,988 fois le sien) : la CSG des pensions au
  taux plein de 6,6 %, et sur le salaire du privé la cotisation maladie de
  0,75 % et celle de chômage de 2,4 %, que la hausse de la CSG de 1,7 point a
  remplacées ; le dépôt prélève les taux de 2026 ;
- *la prime spéciale de sujétion de l'aide-soignante (cas 9) et l'indemnité de
  sujétions spéciales du policier (cas 8)*, sur lesquelles TRAJECTOiRE assied
  une retenue (`primes_dans_la_base`), que le dépôt ne porte pas
  (`data/sources_a_explorer.yaml`, page de la CNRACL ; étape 17) : 0,945 à
  0,997, l'écart croissant avec la part des primes ;
- *le cas 3*, au chômage avant son départ : TRAJECTOiRE lit l'année d'avant
  le départ, chômée ; le dépôt, la dernière année travaillée en entier.

Deux choses trouvées en chemin. Appliquée au revenu entier, la fiche de paie
prélevait la retenue sur les primes : le public passait de 1 à 5 % au-dessus
de TRAJECTOiRE. Et TRAJECTOiRE compte la RAFP dans la pension de son taux ; le
dépôt l'en laisse dehors, comme il la laisse hors des flux : le remplacement
net d'un fonctionnaire en est plus bas chez lui, de 0,4 à 3,4 % selon les
années de cotisation à la RAFP depuis 2005.

**Ce que dit le balayage** (conventions du dépôt, nettes ; scénario 1, sauf
dit autrement ; productivité de 0,7 %, puis 0,4 et 1,0 %).

- *Le salarié au salaire moyen né en 1970*, de 64 à 67 ans : sa pension nette
  passe de 2,23 à 2,55 fois l'ASPA, son remplacement net en salaire moyen de
  68,6 à 76,9 %, son rendement interne réel de 0,96 à 0,77 % et son taux de
  récupération de 1,11 à 1,04. Partir plus tard sert une pension plus forte
  sur une retraite plus courte, et rend moins de ce qui a été versé.
- *Né en 2000*, à 64 ans : 2,61 fois l'ASPA, 2,46 sous la productivité basse,
  2,78 sous la haute ; un taux de récupération de 1,12, 1,24 et 1,02. Plus les
  salaires dépassent les prix, plus la pension monte sur l'ASPA, qui suit les
  prix, et moins rend une pension que les prix revalorisent. Sous la
  proposition (scénario 6), le rendement réel est de −0,11 %, −0,32 et +0,10 % :
  son compte suit les salaires.
- *Le cadre né en 2000* rend 0,05 % réel à 64 ans, pour un remplacement net de
  36,9 % ; *le fonctionnaire sédentaire*, −0,39 %, la contribution de l'État
  comptée, et un remplacement net de 63,8 % sous les trois productivités : sa
  pension et son dernier revenu suivent le même point d'indice.
- *Une marche à chaque 1er janvier.* La durée de carrière compte, comme
  TRAJECTOiRE, toute année rémunérée pour une année : un départ qui déborde
  sur janvier en ajoute une, et la durée relative, comme le remplacement sur
  le cycle de vie, marchent au premier trimestre de chaque année.

**Ce qui reste** de l'étape, dans l'ordre :

1. *Les prélèvements sur les pensions et sur les salaires depuis 1980*, que
   l'IPP publie (registre, chantier 138.9) : ils refermeront l'écart « avant
   2018 » de la confrontation, et le rendement net du COR des générations
   parties avant 2018.
2. *L'écart au COR du rendement des générations 1963 à 1970*, commun au régime
   général et à l'Agirc-Arrco (note du 9 octobre sur les contributions).
3. *L'âge d'équilibre* : l'ETK, le simulateur de pilotage.
4. *Le portage et l'affichage*, avec l'étape 10 : le jumeau JavaScript du
   balayage, et le revenu net du scénario 6 sur la fiche de paie de la
   proposition, comme le site le fait déjà (`contexte.Montants`).
5. *La génération 1941*, aux données.
6. *Hors de l'étape*, à la session des données : la prime spéciale de
   sujétion des aides-soignants et l'indemnité de sujétions spéciales des
   policiers dans l'assiette de la retenue.
