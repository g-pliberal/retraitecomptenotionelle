# Étape 5, treizième partie : l'impôt au site — la pension après impôt des quatre systèmes, dans le dépliant « Partir plus tôt ou plus tard »

**La demande.** Le point « l'impôt au site, à la session des pages » du bloc
« Reprise » de l'étape (session d'orchestration du 18 octobre, lot 5) : l'impôt
que les deux moteurs calculent, dit là où les pages montrent déjà les revenus
nets et les indicateurs de cycle de vie. Un choix de présentation que les
notes, le README ou les pages n'éclairent pas ne se prend pas : la part sans
choix se fait, la question va au propriétaire. Ni l'effet retour dans le
solde, ni les décisions sur le bénéfice (au propriétaire), ni les règles
d'avant 1969. Session du 18 octobre, la seule sur les pages.

**Ce que le site disait déjà.** Le dépliant « Partir plus tôt ou plus tard »
de l'étape 10 (16 octobre) calcule chaque âge de départ après impôt
(`balayageDeLEstimation`, `contexte.js`), sous la convention de l'OCDE : une
personne seule, le barème suivant les prix. Il montrait le taux de
remplacement après impôt du seul système 1, et le patrimoine et le rendement
des quatre systèmes, nets de l'impôt, quand sa bulle ne disait l'impôt que des
colonnes « après impôt ».

**Ce qui est fait.**

- *Au modèle*, dans les deux moteurs : `Depart.pensions_apres_impot`
  (`cycle_de_vie.py`, puis son jumeau de `cycle-de-vie.js`), le numérateur du
  taux de remplacement après impôt, que `_pension_apres_impot` calculait sans
  le rendre : la pension nette du premier mois servi, annualisée, moins
  l'impôt d'une année entière d'elle seule, déclarée par une personne seule
  de son âge au barème de l'année du départ, en euros de cette année. Sans
  calcul de plus : il vient des flux que le départ tire déjà. Le test
  (`test_le_depart_rend_la_pension_apres_impot_de_chaque_systeme`) la pose
  comme la nette moins l'impôt du module, et comme le taux après impôt fois le
  dernier revenu après impôt ; la confrontation des balayages
  (`test_cycle_de_vie_portage.py`) la compare d'un moteur à l'autre.
- *Au site* (`pages.js`, `partirPlusTotOuPlusTard`) : sous la pension nette du
  premier mois, la même après impôt, des quatre systèmes à chaque âge, en
  euros de la page. La bulle dit l'impôt : celui d'une personne seule, sans
  enfant à charge, qui ne déclare que ses revenus d'activité et ses pensions,
  au barème de chaque année, suivant les prix au-delà de la dernière loi de
  finances ; la pension du premier mois y paie l'impôt d'une année entière
  d'elle seule ; le patrimoine et le rendement en sont nets. Le test
  (`test_plusieurs_ages_de_depart_cote_a_cote`) lit le tableau ligne à ligne
  contre le Python.

**Ce que montrent les mesures.** Le salarié non cadre né en 1975, entré à 22
ans, parti à 64 ans en 2039 : par mois, en euros de 2026, 2 577 € nets au
système 1, 2 427 € après impôt ; 794 € au système 2, sous le seuil de
l'impôt, autant après ; 1 973 et 1 912 € au système 3 ; 2 158 et 2 089 € au
système 4. Les 38 rendus de page qui ont le dépliant gagnent le tableau et la
bulle, sans autre changement ; aucun témoin de simulation ne bouge.

**Le registre.** Inchangé : les points de 138.5 (OpenFisca-France, Ines,
EUROMOD, l'OCDE) restent `a_reprendre` pour « le net du site », celui des
cartes de résultats, que la question ci-dessous suspend.

**Au propriétaire : l'impôt dans les cartes de résultats.** Les cartes de la
page des résultats donnent la pension nette avant impôt, comme « Mon
estimation retraite », et leur CSG suit le foyer que la saisie déclare : une
part, ou deux avec un conjoint, ses ressources comprises, le revenu fiscal
dit ou présumé (étape 2, `Montants.du_foyer`). Le dépliant suit l'OCDE, une
personne seule. Les deux ne coïncident que pour qui ne déclare ni conjoint ni
revenu fiscal. Y dire l'impôt demande trois choix, que ni le README, ni les
notes, ni les pages ne tranchent :

1. *Le foyer* : celui que la saisie déclare — le couple imposé à deux parts
   sur ses deux pensions, l'impôt partagé au prorata des pensions, comme le
   modèle partage celui d'une année entre salaire et pension ; le revenu
   fiscal dit, qui compte des revenus que la saisie ne détaille pas — ou une
   personne seule, comme le dépliant et la note du 13 octobre (« le taux après
   impôt d'une personne seule », à côté du taux de remplacement net) ?
2. *La place* : un troisième chiffre dans chaque carte, la pension après
   impôt ; le taux après impôt dans la glose, à côté du taux de remplacement ;
   ou rien, les cartes restant au format de l'estimation officielle, et
   l'impôt au dépliant seul ? Le tableau « Comme votre estimation
   officielle » garderait son net avant impôt, qui est celui de l'estimation.
3. *Les cas à part* : sous des montants bruts, le mode par défaut, un chiffre
   après impôt, ou rien ? Et hors de France, où l'impôt d'un non-résident
   n'est pas celui que le module calcule : un tiret ?

**Ce qui reste** de l'étape, dans l'ordre :

1. *Au propriétaire* : l'impôt dans les cartes (ci-dessus) ; l'effet retour
   dans le solde ; les trois décisions sur le bénéfice.
2. *Selon ses réponses, à la session des pages* : l'impôt dans les cartes ;
   l'affichage de l'effet retour, une ligne « gain public » de la page Coût
   s'il reste hors du solde.
3. *Les revenus de 1960 à 1968*, puis l'exonération de l'article 5, 2°, et
   le seuil de recouvrement d'avant 1977 : les points 4 à 6 de « Ce qui
   reste » de `2026-10-18-etape-5-lois-de-finances-de-1970-a-1973.md`.
