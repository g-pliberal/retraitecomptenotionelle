# Étape 17, neuvième partie : les taux pleins de L. 351-8

**Le 8 octobre 2026, la demande.** La deuxième du reste de l'étape : L. 351-8
donne le taux plein sans la durée requise à des catégories que le dépôt ne
portait pas — l'ancien déporté ou interné (3°), la mère de famille ouvrière
(4°), l'ancien combattant ou prisonnier de guerre (5°) —, ni avant 1983 le
travailleur manuel ; OpenFisca-France-Pension les porte en entrée (registre,
chantier 138.17), et la fiche `decote_avant_1983` les disait « des faits que le
modèle ne porte pas ».

**Ce que dit le droit, lu le jour même** (journal de veille du 8 octobre ;
fiches `taux_plein_*`).

- *L'ancien déporté ou interné* : le décret n° 65-315 lui étend le taux de
  soixante-cinq ans que l'inapte avait dès soixante ans, pour les pensions
  prenant effet depuis le 1er mai 1965 (circulaire ministérielle n° 47 SS) ;
  depuis 1983, le taux plein dès l'âge légal, sans condition de durée (L. 351-8,
  3° ; circulaire Cnav n° 2024-29).
- *La mère de famille ouvrière et le travailleur manuel* : la loi n° 75-1279, «
  dont la date d'effet est fixée au 1er juillet 1976 » (circulaire n° 21 SS),
  leur donne le taux de soixante-cinq ans dès soixante ans — à la mère de trois
  enfants de trente ans d'assurance, majoration de durée comprise, ouvrière
  cinq des quinze dernières années ; au travailleur manuel de quarante-trois
  ans d'assurance jusqu'en juin 1977, puis quarante-deux, puis quarante et un
  en mars 1978, qui a travaillé cinq ans en continu, en semi-continu, à la
  chaîne, au four ou aux intempéries. Depuis 1983, la mère a le taux plein
  (R. 351-23) ; le travailleur manuel n'a plus de catégorie, cent cinquante
  trimestres suffisant.
- *L'ancien combattant ou prisonnier* : depuis 1974, le taux plein de
  soixante-quatre à soixante ans selon les mois de captivité et de services de
  guerre, soixante-trois ans au moins cette année-là (décret n° 74-54, puis
  D. 351-2) ; D. 351-2 n'ayant pas changé avec la loi de 2010, « il était
  ajouté à chaque âge […] deux années de plus » ; depuis le 8 juillet 2024, de
  soixante-six ans à l'âge légal (circulaire Cnav n° 2024-29).
- *Les complémentaires* : l'Ircantec exempte de coefficient les trois
  catégories (arrêté du 30 décembre 1970, article 16, 2° à 4°), l'Agirc-Arrco
  quiconque a le taux plein au régime général.

**Ce qui est fait.**

- *Les fiches*, quatre, lues par les deux moteurs à la date d'effet :
  `taux_plein_anciens_deportes_internes`,
  `taux_plein_meres_de_famille_ouvrieres`, `taux_plein_travailleurs_manuels`,
  `taux_plein_anciens_combattants_prisonniers`, au régime général et chez les
  salariés agricoles, aux artisans et commerçants pour les déportés et les
  combattants.
- *Le modèle* (`droit/categories.py`, son jumeau `categories.js`) : la
  catégorie qui donne le taux plein, que la liquidation lit comme celui de
  l'inapte — la décote nulle, le minimum contributif ouvert, les complémentaires
  sans coefficient depuis 1983. La durée des mères et des travailleurs manuels
  compte les assurances sociales d'avant 1945, que la circulaire n° 21 SS
  totalise, comme le taux des femmes d'avant 1983.
- *La saisie* : trois faits, dans le dépliant de l'invalidité, que son titre
  dit désormais « Invalidité, inaptitude et taux plein » — la carte de déporté
  ou interné, les mois de captivité ou de services de guerre, le travail manuel
  ouvrier ou pénible des quinze dernières années —, deux titres et une
  exposition de la chronologie (la sorte `titre` est nouvelle) ; le budget de
  mots du formulaire vierge monte de deux, à 182.
- *Les tests* : `test_taux_plein_par_categorie.py`, vingt-six cas, dont les
  paliers de 1974, les deux ans de la caisse et le tableau de 2024, la saisie
  et les deux moteurs ; quatre témoins neufs de simulation.

**Les mesures.** Aucune carrière de la grille ni aucun témoin ne déclare ces
faits : aucune pension ne bouge, hors les quatre témoins neufs. L'ancien
déporté parti à soixante ans en 2010 avec trente ans d'assurance passe de 33,75
à 50 %, sa pension de base et son Arrco de 48 et 28 % ; l'ancien combattant de
trente mois parti à soixante-deux ans en 2002, de 43,75 à 50 % ; l'ouvrière mère
de trois enfants partie à l'âge légal en 2022, de 40,625 à 50 % ; le travailleur
manuel de 1978, de 25 à 50 %, son Arrco restant abattu par l'âge, comme avant
l'accord de 1983.

**Ce qui reste.**

1. *L'allocation de solidarité aux personnes âgées* dès l'âge de la catégorie,
   que R. 815-1 ouvre « aux 2° à 5° de l'article L. 351-8 » : le modèle ne la sert
   ainsi qu'à l'inapte.
2. *Les évadés et rapatriés pour maladie*, à l'âge du dernier palier quelle que
   soit leur captivité ; les titulaires de la carte de patriote résistant.
3. *Les autres régimes* : les dates où les salariés agricoles, les artisans et
   les commerçants ont reçu chaque règle, que le modèle leur prête aux dates du
   régime général.
4. *Les textes* : les lois n° 73-1051 et n° 75-1279, les décrets n° 65-315 et
   n° 76-404, dont l'index ne garde que les notices.
5. *De l'étape 17, ensuite* : les majorations pour enfants à charge et pour
   conjoint à charge.
