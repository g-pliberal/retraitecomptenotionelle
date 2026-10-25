/**
 * Les indicateurs de cycle de vie : ce qu'une carrière verse, ce qu'elle reçoit.
 *
 * Le taux de remplacement compare une pension à un salaire, le jour du départ. Il
 * ne dit ni pendant combien de temps la pension sera servie, ni ce qu'elle a
 * coûté : un départ tardif le relève alors qu'il raccourcit la retraite, et un
 * système qui prélève davantage pour servir autant n'y paraît pas. Les autres
 * modèles le complètent par quatre indicateurs que le dépôt n'avait pas (action
 * 138, étape 9 ; registre des modèles, chantier « 138.9 ») :
 *
 * - la DURÉE DE RETRAITE, en années, en part de la vie et rapportée à la
 *   carrière — le premier indicateur d'équité que suit le COR (décret
 *   n° 2014-654 du 20 juin 2014) ;
 * - le TAUX DE RÉCUPÉRATION, somme des pensions sur somme des cotisations,
 *   chacune rapportée au salaire moyen par tête de son année (TRAJECTOiRE,
 *   `txRecuperation`), avec ses deux voisins de la même unité : le taux
 *   d'annuité, pensions sur revenus d'activité, et le taux de remplacement sur
 *   le cycle de vie, pension moyenne d'une année de retraite sur revenu moyen
 *   d'une année de carrière ;
 * - le RENDEMENT INTERNE, le taux qui égalise la valeur actuelle des cotisations
 *   et celle des pensions (le COR, « calculs SG-COR ») : réel quand les flux sont
 *   déflatés des prix, relatif quand ils sont rapportés au salaire moyen, comme
 *   le COR l'actualise depuis son rapport de juin 2026 ;
 * - le PATRIMOINE RETRAITE, valeur au départ des pensions espérées, actualisées
 *   à 1,5 % réel, en années de dernier revenu (l'OCDE, *Pensions at a Glance*),
 *   avec deux voisins que calcule PROST, de la Banque mondiale : la valeur
 *   actuelle nette, patrimoine moins cotisations capitalisées au même taux, et
 *   le taux de remplacement au décès, ce que la pension de la dernière année
 *   vaut contre le dernier revenu mené jusque-là par le salaire moyen.
 *
 * S'y ajoutent l'âge d'équilibre du diviseur et l'âge de part de vie constante
 * (« L'ÂGE D'ÉQUILIBRE », plus bas).
 *
 * DEUX FLUX PAR SYSTÈME (`Flux`). Chaque carrière est vue, sous chacun des six
 * systèmes, comme deux chroniques en euros courants, année civile par année
 * civile : ce qu'elle verse, ce qu'elle reçoit.
 *
 * CE QUI EST VERSÉ, C'EST CE QUE LA PAIE SUPPORTE pour la retraite, et non ce qui
 * est porté au compte : la cotisation salariale et la patronale, aux taux du
 * droit en vigueur de chaque régime, de l'État la part de sa contribution que la
 * Cour des comptes rattache à la retraite de l'agent, et les contributions
 * d'équilibre de l'Agirc-Arrco — l'ASF, l'AGFF, la CET de l'Agirc, la CEG et la
 * CET —, que le compte ne porte pas, mais que la paie supporte pour la retraite
 * complémentaire (`cotisationsVersees`, `contributions-equilibre.js`). Les
 * scénarios 2 à 5 ne diffèrent entre eux que par ce qui est porté au compte, non
 * par ce que la paie supporte : l'employeur verse toujours sa part, elle finance
 * toujours le système, elle n'ouvre plus de droit à celui qui la voit passer.
 * Ils versent donc tous ce que prélève le compte du scénario 4, et jusqu'à la
 * bascule les contributions d'équilibre (`cotisationsReformees`) : ce que verse
 * le scénario 1 jusqu'à elle, puis le taux du régime fusionné, qu'ils prélèvent
 * pour tous et qui remplace la complémentaire et ses contributions. Le 6 verse
 * ce que verse le scénario 1 jusqu'à la bascule, puis son taux unique et les
 * deux parts de son pilier capitalisé, puisque la rente qu'il sert entre dans ce
 * qu'il reçoit (`cotisationsLiberales`). Ce que les régimes provisionnés — le
 * RAFP — encaissent et servent est hors des deux flux, comme il est hors de la
 * comparaison des six systèmes.
 *
 * CE QUI EST REÇU, C'EST CE QUI EST SERVI, année après année (`niveauxActuels`,
 * `niveauxNotionnels`). Le scénario 1 suit le droit : chaque régime revalorisé
 * par ses textes jusqu'à l'année courante (`faireVivre`, `revalorisation.js`),
 * puis par la convention de projection de la page Coût — les prix, et pour
 * l'Agirc-Arrco la valeur de service que le COR projette (`coefficientActuel`),
 * sous le simulateur de la page Coût seulement (`parametres.conventions_cor`) :
 * le simulateur individuel, que les confrontations au COR emploient, n'a pas la
 * convention, et mène l'Agirc-Arrco sur les prix. Les systèmes notionnels
 * suivent la règle de leur compte, et celle du stock à la bascule
 * (`RevalorisationServie`, `revalorisation.js`), sur toute la retraite et non
 * jusqu'à l'année courante seulement. Le niveau d'une année est celui du
 * 31 décembre, revalorisations de l'année comprises : une revalorisation
 * d'octobre (le régime général de 2014 à 2018) ou de novembre (l'Agirc-Arrco) y
 * compte pour l'année entière. N'y entrent ni l'ASPA ni la garantie vieillesse,
 * que l'impôt finance et qui ne sont pas la contrepartie d'une cotisation, ni la
 * réversion, qui est un droit d'un autre.
 *
 * LA FIN DE LA RETRAITE est une convention (`Convention`), et les références
 * n'ont pas la même :
 *
 * - la SURVIE DE GÉNÉRATION du dépôt, la table du diviseur, par sexe ou des deux
 *   sexes réunis : chaque année de pension compte pour la probabilité d'y être
 *   en vie, sachant qu'on l'était au départ. C'est l'espérance que l'OCDE
 *   calcule, sur la mortalité de cohorte de l'ONU, et le défaut ;
 * - un ÂGE DE DÉCÈS FIXE : 60 ans plus l'espérance de vie à 60 ans de la
 *   génération pour le COR (`ageDeDecesCor`), le même arrondi à l'année et
 *   augmenté de six mois pour TRAJECTOiRE.
 *
 * Les cotisations, elles, ne sont pas pondérées par la survie : comme chez le
 * COR et l'OCDE, la carrière est celle de qui atteint le départ.
 *
 * EN NET, chaque année au taux de son année. La pension perd les prélèvements de
 * l'année où elle est servie, au taux plein de CSG (`prelevementsParAnnee`) :
 * rien avant le 1er juillet 1980, puis la cotisation maladie, la CSG, la CRDS,
 * la CASA, que l'IPP retrace (`prelevements-historiques.js`), dont la dernière
 * marche tient au-delà. Ce qui la rapporte à un revenu d'activité le rapporte au
 * revenu net de la même année (`revenusNets`) : la fiche de paie du droit en
 * vigueur, ramenée aux prélèvements de son année, et celle de la proposition
 * pour le scénario 6 après la bascule, comme le site. Le patrimoine reste en
 * années de dernier revenu brut ; l'OCDE exprime son patrimoine net en années de
 * salaire net (14,3 pour 11,5 brut au salaire moyen).
 *
 * APRÈS IMPÔT (action 138, étape 5 ; `conventionApresImpot`), la pension et les
 * revenus perdent en plus l'impôt sur le revenu de chaque année
 * (`impot-revenu.js`) : celui du foyer d'une personne seule, sans enfant à
 * charge, comme l'OCDE calcule ses taux nets (`foyerDeLAnnee`), au barème de
 * l'année, projeté au-delà de la dernière loi de finances lue sur les prix ou,
 * comme l'OCDE, sur le salaire moyen. Le foyer déclare son net imposable : le
 * revenu d'activité moins ses cotisations et la CSG déductible de son année
 * (`revenusImposables`) — pour un indépendant, son bénéfice, au réel et adhérent
 * d'un organisme de gestion agréé (`beneficesParAnnee`), qui paie jusqu'aux
 * revenus de 1969 la taxe complémentaire et déduit de son revenu global celle
 * de l'année précédente —, la pension moins la CSG déductible et la cotisation
 * maladie de l'année où elle est servie (`partsImposablesParAnnee`), et,
 * jusqu'aux revenus de 2012, moins sa majoration pour enfants, qu'aucune de ses
 * parts n'atteint (`partsExonerees`). L'année du départ, il déclare les deux, et
 * leur impôt se partage au prorata (`impotsParAnnee`). Le taux de remplacement
 * après impôt au départ (`remplacementApresImpot`) est le taux net de l'OCDE.
 * Les cotisations restent brutes : l'impôt ne les atteint pas.
 *
 * À CHAQUE ÂGE DE DÉPART (`balayageDUneCarriere`). Calculés au seul âge où un
 * cas type part, les indicateurs ne disent pas ce qu'un départ plus tôt ou plus
 * tard change. TRAJECTOiRE les calcule de trimestre en trimestre, de l'âge
 * d'ouverture, carrière longue comprise, à l'âge d'annulation de la décote, sous
 * plusieurs productivités, en net, avec la pension nette rapportée à l'ASPA et
 * le taux de remplacement net en euros courants, constants et en salaire moyen ;
 * le dépôt fait de même (`Depart`), et le mène sur les cas types sous les trois
 * productivités du COR (`scripts/cycle_de_vie.py --ages`).
 *
 * PAR ÉTAGE, ET AUTOUR DU DÉPART (`pensionParEtage`, `revenusAutourDuDepart`).
 * Typfallsmodellen, le modèle des cas types de Pensionsmyndigheten, rend la
 * pension du départ étage par étage, chacun en part du salaire de fin de
 * carrière, avec la pension après impôt en part du salaire après impôt (son
 * tableau 1), puis le revenu de chaque année, de dix ans avant le départ à la
 * fin de la retraite, avant et après impôt (son tableau 2). Le dépôt range au
 * scénario 1 chaque régime à son étage du catalogue — la base, la
 * complémentaire, l'intégré —, sert à un système notionnel son compte, et au
 * scénario 6 son pilier ; le revenu va de dix ans avant le départ à dix ans
 * après, en euros de l'année du départ.
 *
 * L'ÂGE D'ÉQUILIBRE (`ageDEquilibre`). Les indicateurs disent ce qu'une
 * génération reçoit à l'âge où elle part ; deux modèles disent en plus à quel
 * âge elle devrait partir pour retrouver une génération de référence. L'ETK, le
 * Centre finlandais des pensions, publie pour chaque génération son âge cible
 * (« tavoite-eläkeikä ») : le premier mois où la majoration pour report, 0,4 %
 * par mois depuis l'âge minimal, compense au moins le coefficient d'espérance
 * de vie, qui rapporte la valeur en capital d'une pension en 2009 à celle de
 * l'année (`ageCible`) ; 66 ans et 3 mois pour la génération 1962. Transposé au
 * compte, le coefficient est le rapport du diviseur de la référence à celui de
 * la génération au même âge, et la majoration pour report, ce dont le diviseur
 * baisse quand l'âge monte : l'âge d'équilibre est celui où le diviseur de la
 * génération rejoint celui de la référence, et où, à cotisations égales, elle
 * en retrouve la pension. La référence est celle du compte
 * (`referenceDuCompte`) : la conversion des droits acquis prend le diviseur de
 * l'âge de référence au 1er janvier de l'année de la bascule, 65 ans en 2026, la
 * génération 1961. Le taux de préfinancement étant nul par défaut, le diviseur
 * est l'espérance de vie résiduelle, et l'âge d'équilibre tient constante la
 * DURÉE de la retraite. Le simulateur du COR, réécrit par B. Scherrer et
 * M. Baudin, tient constante sa PART dans la vie, (60 + e60 − âge) / (60 + e60) ;
 * `ageDePartDeVieConstante` le fait sous les deux conventions de
 * `Indicateurs.part_de_vie`, pour la même référence. Par cas type
 * (`scripts/cycle_de_vie.py --equilibre`), le diviseur suit la population de la
 * carrière, la même des deux côtés de l'égalité, et la part de vie aussi, avec
 * le sexe du cas type.
 *
 * CE QUE LE MODULE NE FAIT PAS. La pension nette l'est au taux plein de CSG,
 * sans le taux réduit ni le médian que le revenu fiscal d'un foyer ouvrirait ;
 * la maladie des pensions des régimes de base autres que le régime général, que
 * l'IPP n'écrit pas, n'y est pas ; l'indépendant garde l'invalidité-décès de
 * l'année courante (`revenusNets`). Après impôt, le foyer n'est jamais un couple ni
 * un parent ; le bénéfice d'un indépendant est celui d'un adhérent d'un
 * organisme de gestion agréé, au réel, sans la majoration de qui n'y adhère
 * pas ; l'année où il est aussi salarié, il se partage le revenu imposable au
 * prorata des revenus bruts ; l'artisan de la sécurité sociale est l'artisan
 * fiscal de la taxe complémentaire ; une année d'avant 1960, sans barème lu, ne
 * paie pas d'impôt ; la limite de l'exonération de la majoration pour enfants,
 * que la doctrine lue en 1999 et en 2012 donne, vaut aussi pour les années
 * d'avant, et la seconde, la pension majorée bornée au revenu d'activité qui
 * l'a liquidée, n'est tenue que dans la fonction publique, où l'article L. 18 la
 * fait ; la prime pour l'emploi d'une année incomplète se calcule comme celle
 * d'une année entière (`HORS_CHAMP`, `impot-revenu.js`).
 *
 * LE SEUL EXEMPLAIRE DU CYCLE DE VIE (action 161). Le module fut d'abord le
 * jumeau JavaScript de `cycle_de_vie.py`, porté par morceaux : les deux flux de
 * chaque système — ce que la paie supporte pour la retraite, contributions
 * d'équilibre de l'Agirc-Arrco comprises (`contributions-equilibre.js`), et ce
 * qui est servi, année après année —, puis, le 14 octobre 2026, les revenus
 * nets de chaque année, que l'histoire des prélèvements donne
 * (`prelevements-historiques.js`) : donc la convention de l'OCDE, la convention
 * nette et celle du COR, la pension nette chaque année au taux de son année ;
 * le 16 octobre, l'impôt sur le revenu de chaque année (`impot-revenu.js`,
 * étape 5), donc la convention après impôt et le taux de remplacement après
 * impôt au départ, et les âges de départ d'une carrière (`agesBalayes`,
 * `depart`, `balayageDUneCarriere`), qu'une fonction bâtit à chaque âge ; le
 * 18 octobre, la pension du départ par étage et le revenu autour du départ
 * (`pensionParEtage`, `revenusAutourDuDepart`), les tableaux 1 et 2 de
 * Typfallsmodellen. Le site affiche ces indicateurs par lui, l'impôt compris
 * (dépliant « Partir plus tôt ou plus tard », action 138, étape 10). Depuis le
 * pont (action 161, étape 5), les cas types du COR, que le Python bâtit
 * (`castypes.py`, que le coût lit), passent par lui : `scripts/cycle_de_vie.mjs`
 * en calcule les indicateurs, les âges de départ et les âges d'équilibre pour
 * `scripts/cycle_de_vie.py`, et les noms du Python qui ne servaient qu'aux cas
 * types — leurs âges de départ, leur balayage, leurs âges d'équilibre, les
 * productivités du COR — sont partis. Depuis le 19 octobre 2026, la
 * confrontation aux publications du COR, de TRAJECTOiRE, de l'OCDE et de l'ETK
 * (`tests/test_cycle_de_vie_references.py`) passe aussi par lui, les comptes
 * régime par régime compris, sur le paquet des données du jour. Le Python, que
 * plus rien ne lisait hors des tests, est parti à son tour : le module est
 * désormais le seul exemplaire du cycle de vie, et `tests/js/cycle-de-vie.test.js`
 * le teste.
 */

import { contributionsDUneCarriere, partSalarialeAnnualisee } from "./contributions-equilibre.js";
import { AGE_TERMINAL } from "./mortalite.js";
import {
  chargerPrelevementsHistoriques, familleDeLaFiche, FAMILLES_INDEPENDANTES,
} from "./prelevements-historiques.js";
import {
  ficheDepuisBrut, indemnitesDesLignes, profilDeLaFiche, remunerationDeLaCarriere,
} from "./remuneration.js";
import {
  chargerBaremesImpotRevenu, croissanceMacro, Declarant, Foyer, impotAuxParametres, INDEXATIONS,
  taxeComplementaireDesRevenus,
} from "./impot-revenu.js";
import { agesDeLEstimation } from "./pilote.js";
import { faireVivre, RevalorisationServie } from "./revalorisation.js";
import { exp, log, pow } from "./libm.js";

/**
 * Les six systèmes, dans l'ordre de la comparaison : les attributs de
 * `Comparaison` (`simulateur.js`).
 */
export const SCENARIOS = Object.freeze([
  "actuel",
  "notionnel_retroactif",
  "notionnel_prospectif",
  "notionnel_retroactif_employeur",
  "notionnel_prospectif_employeur",
  "notionnel_liberal",
]);

/**
 * Le taux réel auquel l'OCDE actualise le patrimoine retraite (*Pensions at a
 * Glance 2025*, p. 160-161 ; registre, `modeles_ocde`).
 */
export const TAUX_ACTUALISATION_OCDE = 0.015;

/**
 * Les bornes de la recherche d'un rendement interne : de −50 % à +100 % par an.
 * Un rendement hors de ces bornes n'a pas de sens pour une carrière, et la
 * dichotomie n'en cherche pas.
 */
export const BORNES_RENDEMENT = Object.freeze([-0.5, 1.0]);

/**
 * Comment une retraite finit, et comment on la compte.
 *
 * Le défaut est la convention de l'OCDE : la survie de génération du sexe de la
 * carrière, le patrimoine actualisé à 1,5 % réel, la pension brute. Celle du COR
 * se bâtit carrière par carrière (`conventionCor`).
 *
 * Le constructeur prend ses champs en un objet d'options :
 *
 * - `age_deces` : l'âge du décès, quand la convention le fixe ; `null` pour la
 *   survie de génération du dépôt ;
 * - `unisexe` : la table des deux sexes réunis, comme les cas types du COR, qui
 *   n'en ont pas ; celle du sexe de la carrière sinon ;
 * - `taux_actualisation` : le taux réel du patrimoine retraite ;
 * - `prelevement` : ce que les prélèvements retirent à la pension, en part du
 *   brut, pour des indicateurs nets (`tauxDePrelevement`). Les cotisations ne
 *   changent pas ;
 * - `prelevements` : le même, année par année, en une `Map` de l'année à sa
 *   part, que l'histoire des prélèvements donne (`prelevementsParAnnee`) : une
 *   année qu'elle ne porte pas prend `prelevement` ;
 * - `impot` : l'impôt sur le revenu (`conventionApresImpot`) : `null`, la
 *   pension et les revenus avant lui ; sinon, comment son barème se projette
 *   au-delà de la dernière loi de finances lue, sur les `prix` ou sur le
 *   `salaire_moyen` (`INDEXATIONS`, `impot-revenu.js`). Il se calcule sur le net
 *   imposable : la convention porte alors les prélèvements.
 */
export class Convention {
  constructor({
    age_deces = null, unisexe = false, taux_actualisation = TAUX_ACTUALISATION_OCDE,
    prelevement = 0.0, prelevements = null, impot = null,
  } = {}) {
    this.age_deces = age_deces;
    this.unisexe = unisexe;
    this.taux_actualisation = taux_actualisation;
    this.prelevement = prelevement;
    this.prelevements = prelevements;
    this.impot = impot;
    if (impot !== null) {
      if (!INDEXATIONS.includes(impot)) {
        throw new Error(`indexation du barème inconnue : '${impot}' (${INDEXATIONS.join(", ")})`);
      }
      if (!this.nette) {
        throw new Error("l'impôt se calcule sur le net imposable : une convention après "
          + "impôt porte les prélèvements");
      }
    }
    Object.freeze(this);
  }

  /** La même convention, après l'impôt d'`impot`. */
  avecLImpot(impot) {
    return new Convention({
      age_deces: this.age_deces, unisexe: this.unisexe,
      taux_actualisation: this.taux_actualisation, prelevement: this.prelevement,
      prelevements: this.prelevements, impot,
    });
  }

  /** La pension est-elle nette des prélèvements ? */
  get nette() {
    return this.prelevement > 0.0
      || (this.prelevements !== null && this.prelevements.size > 0);
  }

  /** La part de la pension de l'année `annee` que les prélèvements laissent. */
  retenu(annee) {
    if (this.prelevements !== null && this.prelevements.has(annee)) {
      return 1.0 - this.prelevements.get(annee);
    }
    return 1.0 - this.prelevement;
  }
}

/**
 * L'impôt sur le revenu d'une année du cycle de vie, et ce qu'en supportent
 * le salaire et la pension (`impotsParAnnee`). Ses champs :
 *
 * - `annee` ;
 * - `salaire` et `pension` : ce que le foyer déclare, en euros courants : le
 *   salaire imposable de l'année (`revenusImposables`), et la part imposable de
 *   ce que la pension sert dans l'année (`partsImposablesParAnnee`) ;
 * - `foyer` : l'impôt du foyer, étape par étape, tel que `impotAuxParametres`
 *   le rend (`impot-revenu.js`) ;
 * - `sur_la_pension` : la part de l'impôt que supporte la pension : au prorata
 *   des revenus après leurs abattements (`partDeLaPension`) ;
 * - `benefice` : le bénéfice imposable de l'année, en euros courants, que le
 *   foyer déclare en plus de son salaire (`beneficesParAnnee`).
 */
export class ImpotDeLAnnee {
  constructor({ annee, salaire, pension, foyer, sur_la_pension, benefice = 0.0 }) {
    Object.assign(this, { annee, salaire, pension, foyer, sur_la_pension, benefice });
    Object.freeze(this);
  }

  /** Ce que le foyer paie ; négatif, ce qui lui est restitué. */
  get impot() {
    return this.foyer.impot;
  }

  /** Ce que supporte le revenu d'activité, salaire ou bénéfice. */
  get sur_le_salaire() {
    return this.foyer.impot - this.sur_la_pension;
  }
}

/**
 * Ce qu'une carrière verse et reçoit sous un système, en euros courants de
 * chaque année. Ses champs, que le constructeur prend en un objet, les
 * chroniques en `Map` de l'année à son montant :
 *
 * - `scenario` ;
 * - `cotisations` : ce qui est versé chaque année pour la retraite, salariale
 *   et patronale (`cotisationsVersees`) ;
 * - `revenus` : les revenus d'activité des années cotisées ;
 * - `niveaux` : le niveau ANNUEL de la pension au 31 décembre de chaque année à
 *   partir de celle du départ : ce qu'elle sert sur une année entière ;
 * - `debut` : le premier mois servi, en date décimale : l'année du départ et
 *   ses mois écoulés, `(mois − 1) / 12` ;
 * - `age` : l'âge à ce premier mois ;
 * - `sexe` ;
 * - `dernier_revenu` : le dernier revenu d'activité annualisé, en euros de
 *   l'année du départ : le dénominateur du taux de remplacement, et celui du
 *   patrimoine ;
 * - `revenus_nets` et `dernier_revenu_net` : les mêmes revenus et le même
 *   dernier revenu, nets (`revenusNets`), que les indicateurs nets opposent à la
 *   pension nette ; `null` quand le flux ne les porte pas, ou qu'un statut de la
 *   carrière n'a pas de fiche de paie ;
 * - `indexation_impot` et `impots` : sous un impôt (`fluxDesSystemes(…,
 *   { impot })`), l'indexation de son barème, et l'impôt sur le revenu de
 *   chaque année (`impotsParAnnee`), un `ImpotDeLAnnee` par année ;
 * - `exoneree` : sous un impôt aussi, la part du niveau de chaque année que
 *   l'impôt exonère, la majoration pour enfants jusqu'aux revenus de 2012
 *   (`partsExonerees`) ; aucune les autres années ;
 * - `revenus_apres_impot` et `dernier_revenu_apres_impot` : les revenus nets
 *   que l'impôt laisse, et le dernier revenu net d'une année entière d'impôt
 *   (`dernierRevenuApresImpot`) ; `null` quand un statut n'a pas de fiche de
 *   paie.
 */
export class Flux {
  constructor({
    scenario, cotisations, revenus, niveaux, debut, age, sexe, dernier_revenu,
    revenus_nets = null, dernier_revenu_net = null, indexation_impot = null, impots = null,
    exoneree = new Map(), revenus_apres_impot = null, dernier_revenu_apres_impot = null,
  }) {
    Object.assign(this, {
      scenario, cotisations, revenus, niveaux, debut, age, sexe, dernier_revenu,
      revenus_nets, dernier_revenu_net, indexation_impot, impots, exoneree,
      revenus_apres_impot, dernier_revenu_apres_impot,
    });
  }

  /** Le même flux, ses champs de `champs` remplacés. */
  remplace(champs) {
    return new Flux({ ...this, ...champs });
  }

  /** L'origine des âges, en date décimale. */
  get naissance() {
    return this.debut - this.age;
  }

  /**
   * La part de l'année `annee` où la pension est servie : du premier mois au
   * 31 décembre l'année du départ, l'année entière ensuite.
   */
  servi(annee) {
    return Math.min(Math.max(annee + 1 - this.debut, 0.0), 1.0);
  }

  /**
   * La part de la pension brute de l'année `annee` que l'impôt lui retire :
   * ce qu'elle en supporte (`ImpotDeLAnnee.sur_la_pension`) sur ce qu'elle sert
   * dans l'année ; zéro sans impôt.
   */
  impotDeLaPension(annee) {
    const impot = this.impots === null ? undefined : this.impots.get(annee);
    const servie = (this.niveaux.get(annee) ?? 0.0) * this.servi(annee);
    if (impot === undefined || servie <= 0.0) return 0.0;
    return impot.sur_la_pension / servie;
  }

  get annee_liquidation() {
    return Math.floor(this.debut + 1e-9);
  }

  /**
   * Les années de carrière : celles qui portent un revenu d'activité, comme
   * TRAJECTOiRE les compte (`dureeCarriere`).
   */
  get duree_carriere() {
    let n = 0;
    for (const revenu of this.revenus.values()) if (revenu > 0) n += 1;
    return n;
  }
}

/**
 * Les indicateurs de cycle de vie d'une carrière, sous un système. Ses champs,
 * que le constructeur reçoit en un objet :
 *
 * - `scenario` ;
 * - `duree_retraite` : les années de retraite, espérées sous la survie de
 *   génération, fixées sous un âge de décès, à compter du premier mois servi ;
 * - `part_de_vie` : la même, rapportée à la vie entière : durée / (âge au
 *   départ + durée) ;
 * - `duree_carriere` ;
 * - `taux_recuperation` : pensions sur cotisations, chacune rapportée au
 *   salaire moyen de son année ; `null` sans cotisation ;
 * - `taux_annuite` : pensions sur revenus d'activité, même unité ; nettes sur
 *   nets sous une convention nette ;
 * - `taux_remplacement_cycle` : pension moyenne d'une année de retraite sur
 *   revenu moyen d'une année de carrière, même unité et même règle ;
 * - `rendement_reel` et `rendement_smpt` : le rendement interne des flux
 *   déflatés des prix, et celui des flux rapportés au salaire moyen ; `null`
 *   quand aucun taux ne les égalise ;
 * - `patrimoine` : la valeur au départ des pensions espérées, actualisées au
 *   taux réel de la convention, en années de dernier revenu ;
 * - `valeur_nette` : le patrimoine moins la valeur au départ des cotisations,
 *   capitalisées au même taux : la valeur actuelle nette d'être couvert (PROST,
 *   de la Banque mondiale), en années de dernier revenu ;
 * - `remplacement_au_deces` : la pension de la dernière année de la retraite —
 *   espérée, ou fixée par l'âge de décès —, rapportée au dernier revenu mené
 *   jusqu'à elle par le salaire moyen : ce qu'une pension perd sur les salaires
 *   en une retraite (PROST, « replacement rate at death ») ; nette sur net sous
 *   une convention nette.
 */
export class Indicateurs {
  constructor(champs) {
    Object.assign(this, champs);
  }

  /** La durée de retraite rapportée à la durée de carrière. */
  get duree_relative() {
    return this.duree_carriere <= 0 ? null : this.duree_retraite / this.duree_carriere;
  }

  dictionnaire() {
    return {
      duree_retraite: this.duree_retraite,
      part_de_vie: this.part_de_vie,
      duree_carriere: this.duree_carriere,
      duree_relative: this.duree_relative,
      taux_recuperation: this.taux_recuperation,
      taux_annuite: this.taux_annuite,
      taux_remplacement_cycle: this.taux_remplacement_cycle,
      rendement_reel: this.rendement_reel,
      rendement_smpt: this.rendement_smpt,
      patrimoine: this.patrimoine,
      valeur_nette: this.valeur_nette,
      remplacement_au_deces: this.remplacement_au_deces,
    };
  }
}

// -- les flux ----------------------------------------------------------------

/**
 * Des montants datés, sommés par année, dans l'ordre où ils viennent : une
 * année peut porter plusieurs lignes, un statut quitté et un autre pris.
 */
function parAnnee(couples) {
  const sommes = new Map();
  for (const [annee, montant] of couples) {
    if (montant) sommes.set(annee, (sommes.get(annee) ?? 0.0) + montant);
  }
  return sommes;
}

function trieesParAnnee(map) {
  return [...map.entries()].sort(([a], [b]) => a - b);
}

/**
 * Ce que le droit en vigueur prélève sur `carriere` pour sa retraite, année
 * par année et sans bascule : la cotisation salariale et la patronale, de
 * l'État la part que `parametres.contribution_etat` lui rattache, et les
 * contributions d'équilibre de l'Agirc-Arrco.
 *
 * Le compte des scénarios 4 et 5, bâti sans le régime fusionné de la bascule :
 * il porte, chaque année, les taux du droit en vigueur de chaque régime, part
 * patronale comprise. Pour l'État, qui ne cotise pas mais équilibre, le défaut
 * est la part de son taux que la Cour des comptes rattache à la retraite de
 * l'agent lui-même — 44,1 % du traitement d'un civil en 2025 sur 78,28 % versés
 * (`ContributionEtat.RETRAITE_SEULE`, `config.js`) : le reste paie
 * l'invalidité, les majorations pour enfants, les départs anticipés et la
 * démographie du régime, ce que le COR retire aussi de son rendement interne en
 * n'y comptant que les cotisations, « sans les autres ressources telles que les
 * impôts et taxes affectés et les transferts ». Le COR et TRAJECTOiRE ne
 * comptent, pour l'État, que la retenue de l'agent ; la recette de la page Coût,
 * le taux entier (`TAUX_REELS`, `cout.py`). Ce que les régimes provisionnés
 * encaissent n'y est pas.
 *
 * Le compte ne porte pas les contributions d'équilibre de l'Agirc-Arrco, qui
 * n'achètent aucun point et ne sont pas des cotisations (décision du 2 octobre
 * 2026) ; la paie du salarié du privé les supporte pour la retraite
 * complémentaire, et TRAJECTOiRE comme le COR les comptent : elles s'ajoutent
 * ici à ce que le compte prélève (`contributionsDUneCarriere`,
 * `contributions-equilibre.js`).
 */
export function cotisationsVersees(simulateur, carriere) {
  const compte = simulateur.constructeurEmployeur.construire(
    carriere, carriere.anneeLiquidation, carriere.premiereAnnee);
  return parAnnee([
    ...compte.cotisations.map((ligne) => [ligne.annee, ligne.cotisation]),
    ...trieesParAnnee(contributionsDUneCarriere(simulateur, carriere)),
  ]);
}

/**
 * Ce que versent les scénarios 2 à 5 : ce que prélève le compte du scénario 4,
 * part patronale comprise — les taux du droit en vigueur jusqu'à la bascule,
 * ceux de `cotisationsVersees`, puis le taux du régime fusionné, celui du
 * statut pivot, que la réforme prélève pour tous. Un agent de l'État n'y verse
 * plus, après la bascule, que ce taux-là : la contribution d'équilibre de l'État
 * ne finance plus ses droits. Les contributions d'équilibre de l'Agirc-Arrco
 * s'y ajoutent jusqu'à la bascule, où la paie les supportait ; après elle, le
 * régime fusionné remplace la complémentaire, et son taux les omet, comme celui
 * du scénario 6.
 */
export function cotisationsReformees(simulateur, comparaison) {
  const compte = comparaison.notionnel_retroactif_employeur.compte;
  const bascule = simulateur.parametres.annee_bascule;
  const equilibre = contributionsDUneCarriere(simulateur, comparaison.carriere);
  return parAnnee([
    ...compte.cotisations.map((ligne) => [ligne.annee, ligne.cotisation]),
    ...trieesParAnnee(equilibre).filter(([annee]) => annee < bascule),
  ]);
}

/**
 * Ce que le scénario 6 fait verser : le droit en vigueur avant la bascule, son
 * compte ensuite — le taux unique, sur la carrière que l'âge légal de 65 ans a
 * peut-être prolongée —, et les deux parts de son pilier, dont il sert la rente.
 */
export function cotisationsLiberales(simulateur, versees, liberal) {
  const bascule = simulateur.parametres.annee_bascule;
  const couples = [...versees.entries()].filter(([annee]) => annee < bascule);
  for (const ligne of liberal.compte.cotisations) {
    if (ligne.annee >= bascule) couples.push([ligne.annee, ligne.cotisation]);
  }
  const pilier = liberal.capitalisation;
  if (pilier !== null && pilier !== undefined && pilier.actif) {
    for (const annee of pilier.annees) couples.push([annee.annee, annee.versement_brut]);
  }
  return parAnnee(couples);
}

/** Les revenus d'activité des années cotisées, en euros courants. */
export function revenusDActivite(carriere) {
  return parAnnee(carriere.lignes.filter((ligne) => ligne.cotise)
    .map((ligne) => [ligne.annee, ligne.revenu]));
}

/**
 * Les postes de la fiche de paie que les contributions d'équilibre de l'année
 * remplacent : la CEG et la CET, que la fiche prélève aux taux de l'année
 * courante.
 */
export const POSTES_EQUILIBRE = Object.freeze(["equilibre_general", "equilibre_technique"]);

/**
 * Les postes de la fiche d'un indépendant que l'histoire refait à l'année : la
 * maladie et l'indemnité journalière, les allocations familiales, la CSG et la
 * CRDS. Les autres — la retraite, l'invalidité-décès — entrent, avant 2025,
 * dans l'assiette de sa CSG.
 */
export const POSTES_REFAITS_INDEPENDANT = Object.freeze([
  "maladie_maternite", "indemnites_journalieres", "famille", "csg_crds",
]);

function historiqueDe(simulateur) {
  const historique = chargerPrelevementsHistoriques(simulateur.paquet);
  if (historique === null) {
    throw new Error("le paquet ne porte pas l'histoire des prélèvements "
      + "(`prelevements_historiques`) : les revenus nets ne se calculent pas");
  }
  return historique;
}

/**
 * Le net du revenu annualisé d'une ligne cotisée, primes et indemnité
 * compensatrice de la CSG comprises, aux prélèvements de son année
 * (`revenusNets`), et, avec `imposable`, ce que ces prélèvements en retirent
 * sans que le revenu imposable le déduise (`revenusImposables`), zéro sans lui ;
 * `null` sans fiche de paie. Une famille que l'histoire ne connaît pas garde les
 * prélèvements de l'année courante.
 */
function netAnnualise(simulateur, carriere, ligne, indemnite = 0.0, imposable = false) {
  const { macro, catalogue, affiliations } = simulateur;
  // Les régimes de la date d'entrée dans le statut : l'agent de la SNCF entré
  // avant 2020 paie le sien après la fermeture.
  const entree = affiliations.dateEntree(carriere, ligne.affiliation, ligne.annee);
  const fiche = ficheDepuisBrut(simulateur.baremePrelevements, macro, catalogue, affiliations,
    ligne.affiliation, ligne.annee, ligne.revenuAnnualise, ligne.part_primes, indemnite,
    entree);
  if (fiche === null) return null;
  const annualise = fiche.brut;
  const profil = profilDeLaFiche(affiliations, catalogue, ligne.affiliation, ligne.annee,
    entree);
  const regimes = profil === "independant"
    ? affiliations.regimes(ligne.affiliation, ligne.annee, entree)
    : [];
  const famille = familleDeLaFiche(profil, regimes);
  const historique = historiqueDe(simulateur);
  const plafond = macro.plafond_securite_sociale.valeur(ligne.annee);
  const courante = simulateur.baremePrelevements.annee;
  if (famille === null) {
    return [fiche.net, imposable
      ? historique.nonDeductiblesAnnuel(null, courante, annualise, plafond) : 0.0];
  }
  let retraite;
  if (FAMILLES_INDEPENDANTES.includes(famille)) {
    retraite = 0.0;
    for (const l of fiche.lignes) {
      if (!POSTES_REFAITS_INDEPENDANT.includes(l.code)) retraite += l.salarie;
    }
  } else {
    retraite = fiche.retraiteSalarie;
  }
  const horsRetraite = historique.horsRetraiteAnnuel(famille, courante, annualise, plafond, retraite)
    - historique.horsRetraiteAnnuel(famille, ligne.annee, annualise, plafond, retraite);
  let equilibre = 0.0;
  for (const l of fiche.lignes) if (POSTES_EQUILIBRE.includes(l.code)) equilibre += l.salarie;
  if (equilibre > 0.0) equilibre -= partSalarialeAnnualisee(simulateur, carriere, ligne);
  const nonDeductibles = imposable
    ? historique.nonDeductiblesAnnuel(famille, ligne.annee, annualise, plafond, retraite) : 0.0;
  return [fiche.net + horsRetraite + equilibre, nonDeductibles];
}

/**
 * Chaque ligne cotisée, dans l'ordre : son année, son net et, avec
 * `imposable`, sa part non déductible, ce que sa paie retire sans que le revenu
 * imposable le déduise (`netAnnualise`), ramenés aux mois travaillés ; `null`
 * quand un statut de la carrière n'a pas de fiche de paie.
 */
function paies(simulateur, carriere, imposable) {
  const resultat = [];
  const indemnites = indemnitesDesLignes(carriere, simulateur.macro, simulateur.catalogue,
    simulateur.affiliations);
  for (const [rang, ligne] of carriere.lignes.entries()) {
    if (!ligne.cotise) continue;
    const paie = netAnnualise(simulateur, carriere, ligne, indemnites[rang], imposable);
    if (paie === null) return null;
    const [net, nonDeductible] = paie;
    resultat.push([ligne.annee, net * ligne.fraction_annee, nonDeductible * ligne.fraction_annee]);
  }
  return resultat;
}

/**
 * Les nets des années de la bascule au départ, lus sur la fiche de paie de la
 * proposition (`revenusNets`).
 */
function avecLaProposition(simulateur, carriere, nets) {
  const remuneration = remunerationDeLaCarriere(carriere, simulateur.macro,
    simulateur.catalogue, simulateur.affiliations, simulateur.parametres,
    simulateur.baremePrelevements, simulateur.paquet);
  const bruts = revenusDActivite(carriere);
  for (const annee of remuneration === null ? [] : remuneration.annees) {
    const fiche = annee.proposition;
    if (fiche.brut > 0.0 && bruts.has(annee.annee)) {
      // Le même brut que la fiche du droit en vigueur : le revenu de l'année et
      // l'indemnité compensatrice qu'elle lui ajoute, au prorata des mois payés.
      const revenu = annee.droitEnVigueur.brut - annee.indemniteCsg;
      const paye = revenu > 0.0 ? annee.indemniteCsg * bruts.get(annee.annee) / revenu : 0.0;
      nets.set(annee.annee, (bruts.get(annee.annee) + paye) * fiche.net / fiche.brut);
    }
  }
  return nets;
}

/**
 * Ce que la paie laisse de chaque revenu d'activité, année par année, aux
 * prélèvements de son année : la fiche de paie du droit en vigueur
 * (`ficheDepuisBrut`, `remuneration.js`), qui retient les cotisations retraite
 * de l'année et les autres prélèvements de l'année courante, ramenée à ceux de
 * l'année par l'histoire que l'IPP retrace (`PrelevementsHistoriques.horsRetraite`,
 * `prelevements-historiques.js`) — la CSG et la CRDS depuis 1991 et 1996, la
 * maladie, le veuvage, l'assurance chômage du salarié du privé, la maladie et la
 * contribution de solidarité de l'agent public — et par les contributions
 * d'équilibre de l'Agirc-Arrco de l'année, l'ASF, l'AGFF ou la CEG, au lieu de
 * celles de l'année courante. L'indépendant a les siens : la maladie des
 * artisans et commerçants ou celle des professions libérales, les allocations
 * familiales, la CSG et la CRDS sur son revenu augmenté, jusqu'en 2024, de ses
 * cotisations ; son invalidité-décès reste celle de l'année courante. La fiche
 * se lit sur le revenu annualisé, sous le plafond de l'année entière, puis se
 * ramène aux mois travaillés.
 *
 * Les primes d'un fonctionnaire perdent les prélèvements hors retraite, sans la
 * retenue pour pension, que la loi n'assied que sur le traitement
 * (`blocDroitEnVigueur`, `remuneration.js`), et la RAFP, que la fiche prélève
 * depuis le 10 octobre 2026 comme TRAJECTOiRE : elle sort du net, quand sa
 * cotisation et sa rente restent hors des deux flux, servies à part. Depuis
 * 2018, le net d'un agent public compte son indemnité compensatrice de la hausse
 * de la CSG, que la fiche ajoute au revenu de la ligne (`indemnitesDesLignes`,
 * `remuneration.js`).
 *
 * Avec `proposition`, les années de la bascule au départ se lisent sur la fiche
 * de paie de la proposition (`remunerationDeLaCarriere`, `remuneration.js`), qui
 * laisse un net plus fort du même brut : son rapport du net au brut, appliqué au
 * revenu de l'année, comme le site le fait pour le taux de remplacement net du
 * scénario 6 (`Montants`, `contexte.js`). Les scénarios 2 à 5 gardent la fiche
 * du droit en vigueur, comme le site. `null` quand un statut de la carrière n'a
 * pas de fiche de paie — l'exploitant agricole —, dont le net ne se calcule pas.
 */
export function revenusNets(simulateur, carriere, proposition = false) {
  const lues = paies(simulateur, carriere, false);
  if (lues === null) return null;
  const nets = parAnnee(lues.map(([annee, net]) => [annee, net]));
  return proposition ? avecLaProposition(simulateur, carriere, nets) : nets;
}

/**
 * Les revenus d'activité nets imposables, année par année : ce que la paie en
 * laisse (`revenusNets`), plus ce qu'elle en retire sans que le revenu imposable
 * le déduise — la CSG au-delà de sa part déductible, la CRDS —, aux taux de son
 * année (`PrelevementsHistoriques.nonDeductibles`, `prelevements-historiques.js`).
 * Autrement dit, le brut moins les cotisations de l'année et la CSG déductible
 * (CGI, art. 83 et 154 quinquies) : le salaire imposable qu'attend
 * `impot-revenu.js`, avant l'abattement de 10 %. Pour un indépendant, c'est son
 * bénéfice imposable, qui n'a pas cet abattement, et que le module de l'impôt
 * reçoit tel quel, sans le calculer (`HORS_CHAMP`, `impot-revenu.js`).
 *
 * Avec `proposition`, le net du scénario 6 après la bascule garde la part non
 * déductible du droit en vigueur : la CSG que la proposition rend
 * (`pointsCsgRendus`, `restitution.js`) baisse la part déductible, comme chaque
 * hausse et chaque baisse de la CSG l'a fait depuis 1997 — une convention, que
 * le README ne tranche pas. `null` comme `revenusNets`.
 */
export function revenusImposables(simulateur, carriere, proposition = false) {
  const revenus = netsEtImposables(simulateur, carriere, proposition);
  return revenus === null ? null : revenus[1];
}

/** `revenusNets` et `revenusImposables`, d'une seule fiche de paie par ligne. */
function netsEtImposables(simulateur, carriere, proposition) {
  const lues = paies(simulateur, carriere, true);
  if (lues === null) return null;
  let nets = parAnnee(lues.map(([annee, net]) => [annee, net]));
  if (proposition) nets = avecLaProposition(simulateur, carriere, nets);
  const retires = parAnnee(lues.map(([annee, , part]) => [annee, part]));
  return [nets,
    new Map([...nets].map(([annee, net]) => [annee, net + (retires.get(annee) ?? 0.0)]))];
}

/**
 * Le dernier revenu annualisé, net : le rapport du net au brut de la dernière
 * année cotisée, celle que le simulateur annualise.
 */
function dernierRevenuNet(dernierRevenu, revenus, nets) {
  if (nets === null || revenus.size === 0) return null;
  const annee = Math.max(...revenus.keys());
  return dernierRevenu * (nets.get(annee) ?? 0.0) / revenus.get(annee);
}

function debutDe(carriere) {
  return carriere.anneeLiquidation + carriere.fractionAnneeLiquidation;
}

/**
 * La dernière année qu'une pension peut atteindre : l'âge terminal de la table
 * de mortalité.
 */
function derniereAnneeDe(carriere) {
  return Math.floor(debutDe(carriere) - carriere.age_liquidation + AGE_TERMINAL) + 1;
}

function horsRepartition(simulateur, regime) {
  return Boolean(simulateur.parametres.isoler_capitalisation
    && simulateur.catalogue.obtenir(regime).hors_repartition);
}

/**
 * La répartition d'une pension menée à une échéance, majoration pour enfants
 * comprise : ce que `faireVivre` rend, sans le RAFP.
 */
function servie(vivante) {
  let total = 0.0;
  for (const r of vivante.regimes) if (!r.hors_repartition) total += r.aujourd_hui;
  return total + vivante.majoration_enfants * vivante.coefficient_majoration;
}

/** La répartition du scénario 1 au départ, sans l'ASPA. */
function auDepart(simulateur, resultat) {
  let regimes = 0.0;
  for (const p of resultat.pensions_par_regime) {
    if (!horsRepartition(simulateur, p.regime)) regimes += p.montant;
  }
  let majoration = 0.0;
  for (const a of resultat.avantages_appliques) {
    if (a.code === "majoration_enfants") majoration += a.montant;
  }
  return regimes + majoration;
}

/**
 * La part de la pension du scénario 1 que sert, au bout de ses fusions, un
 * régime à valeur de service convenue (comme `parts_convenues`, dans `cout.py`),
 * rapportée à la répartition sans l'ASPA, comme les niveaux qu'elle mène ; une
 * `Map` du régime convenu à sa part.
 */
function partsConvenues(simulateur, resultat, revalorisation) {
  const total = auDepart(simulateur, resultat);
  const parts = new Map();
  if (total <= 0.0) return parts;
  for (const pension of resultat.pensions_par_regime) {
    const convenu = revalorisation.regimeConvenu(pension.regime);
    if (convenu !== null && pension.montant > 0.0) {
      parts.set(convenu, (parts.get(convenu) ?? 0.0) + pension.montant / total);
    }
  }
  return parts;
}

/**
 * Ce que `coefficient_actuel` fait pour la page Coût (`cout.py`) : les prix, et
 * la valeur de service convenue.
 */
function coefficientActuel(parts, revalorisation, anneeLiquidation, annee) {
  let coefficient = 1.0;
  if (annee <= anneeLiquidation) return coefficient;
  for (const [regime, part] of parts) {
    coefficient += part * (revalorisation.coefficientPoints(regime, anneeLiquidation, annee) - 1.0);
  }
  return coefficient;
}

/**
 * Le niveau annuel de la pension du scénario 1, de l'année du départ à
 * `derniere`, en euros courants.
 *
 * Ce que le droit a servi jusqu'à l'année courante, régime par régime
 * (`faireVivre`) ; au-delà, ou pour un départ à venir, la convention de
 * projection de la page Coût : les prix, et la valeur de service que le COR
 * projette pour l'Agirc-Arrco (`coefficientActuel`) — quand le simulateur porte
 * ses conventions (`parametres.conventions_cor`) ; sinon, les prix pour tous.
 * Pour le cas type n° 2 du COR, ces conventions, cette valeur de service et le
 * taux moyen des entreprises, abaissent le rendement de 0,02 à 0,05 point
 * (note du 10 octobre 2026).
 */
export function niveauxActuels(simulateur, comparaison, revalorisation, derniere) {
  const carriere = comparaison.carriere;
  const resultat = comparaison.actuel;
  const macro = simulateur.macro;
  const liquidation = carriere.anneeLiquidation;
  const courante = simulateur.parametres.annee_courante;
  const niveaux = new Map();
  let ancre;
  if (liquidation <= courante) {
    for (let annee = liquidation; annee <= courante; annee += 1) {
      niveaux.set(annee, servie(faireVivre(simulateur, carriere, resultat, annee)));
    }
    ancre = courante;
  } else {
    niveaux.set(liquidation, auDepart(simulateur, resultat));
    ancre = liquidation;
  }
  const depart = niveaux.get(ancre);
  const parts = partsConvenues(simulateur, resultat, revalorisation);
  for (let annee = ancre + 1; annee <= derniere; annee += 1) {
    niveaux.set(annee, depart * macro.coefficientPrix(ancre, annee)
      * coefficientActuel(parts, revalorisation, ancre, annee));
  }
  return niveaux;
}

/**
 * La pension de répartition qu'un système notionnel sert au départ, sans la
 * garantie vieillesse du scénario 6, que l'impôt finance.
 */
function pensionContributive(calcul, resultat) {
  const garantie = resultat.garantie_vieillesse;
  if (calcul.garantie && garantie !== null && garantie !== undefined) {
    return garantie.pension_contributive;
  }
  return resultat.pension_annuelle;
}

/**
 * Le niveau annuel de la pension d'un système notionnel, en euros courants : sa
 * règle d'indexation depuis le départ, et celle du stock à la bascule
 * (`RevalorisationServie.coefficientStock`, `revalorisation.js`).
 *
 * Une réforme prospective ne touche pas qui est parti avant elle : il garde la
 * pension du scénario 1, revalorisée par le droit jusqu'à la bascule, puis
 * selon `revalorisation_stock`. Le scénario 6 sert sa part contributive — la
 * garantie vieillesse, que l'impôt finance, n'y est pas — et la rente de son
 * pilier, nominale et constante.
 */
export function niveauxNotionnels(simulateur, comparaison, scenario, revalorisation,
  actuels, derniere) {
  const parametres = simulateur.parametres;
  const calcul = simulateur.calculs[scenario];
  const macro = simulateur.macro;
  const resultat = comparaison[scenario];
  const liquidation = comparaison.carriereDe(scenario).anneeLiquidation;
  const bascule = parametres.annee_bascule;
  if (calcul.prospectif && liquidation <= bascule) {
    const niveaux = new Map([...actuels].filter(([annee]) => annee <= bascule));
    const base = actuels.get(bascule);
    const reindexe = parametres.revalorisation_stock === "reindexe";
    for (let annee = bascule + 1; annee <= derniere; annee += 1) {
      const reel = reindexe ? revalorisation.coefficient(bascule, annee) : 1.0;
      niveaux.set(annee, base * macro.coefficientPrix(bascule, annee) * reel);
    }
    return niveaux;
  }
  const pension = pensionContributive(calcul, resultat);
  const rente = resultat.rente_capitalisation_obligatoire ?? 0.0;
  const niveaux = new Map();
  for (let annee = liquidation; annee <= derniere; annee += 1) {
    niveaux.set(annee, pension * macro.coefficientPrix(liquidation, annee)
      * revalorisation.coefficientStock(liquidation, annee, calcul.prospectif) + rente);
  }
  return niveaux;
}

/**
 * Les deux flux d'une carrière sous chacun des six systèmes, un `Flux` par
 * scénario ; avec `nets`, leurs revenus nets aussi (`revenusNets`), qu'une
 * fiche de paie par année coûte, sur la fiche du droit en vigueur, ou sur celle
 * de la proposition pour le scénario 6 ; avec `impot`, l'indexation du barème de
 * l'impôt sur le revenu (`Convention.impot`), l'impôt de chaque année aussi, et
 * les revenus nets qu'il laisse (`avecLImpot`).
 */
export function fluxDesSystemes(simulateur, comparaison, { nets = false, impot = null } = {}) {
  const carriere = comparaison.carriere;
  let derniere = -Infinity;
  for (const scenario of SCENARIOS) {
    derniere = Math.max(derniere, derniereAnneeDe(comparaison.carriereDe(scenario)));
  }
  // La règle des pensions notionnelles servies, jusqu'à `derniere` : celle du
  // simulateur s'arrête à l'année courante, la page Coût bâtit la sienne
  // jusqu'à son horizon, et une retraite va plus loin.
  const revalorisation = new RevalorisationServie(
    simulateur, simulateur.parametres.annee_debut_repartition, derniere);
  const versees = cotisationsVersees(simulateur, carriere);
  const actuels = niveauxActuels(simulateur, comparaison, revalorisation, derniere);
  const parts = impot === null ? null : partsImposablesParAnnee(simulateur, comparaison);
  const exonerees = impot === null ? {} : partsExonerees(simulateur, comparaison);
  // Les revenus de chaque carrière, leur net et, sous l'impôt, leur net
  // imposable : sur la fiche du droit en vigueur, ou sur celle de la
  // proposition pour le scénario 6 ; une fiche de paie par année, une fois par
  // carrière et par fiche. Ce qui fait les revenus d'un système, c'est sa
  // carrière, et la fiche de paie de la proposition, que lit le scénario 6 ;
  // `revenusDe` en rend les revenus d'activité, leur net avec `nets` ou
  // `impot`, et leur net imposable avec `impot` ; `null` pour ce qui n'est pas
  // demandé, ou qu'un statut sans fiche de paie ne permet pas.
  const revenus = new Map();
  const revenusDe = (scenario) => {
    const duScenario = comparaison.carriereDe(scenario);
    const proposition = scenario in simulateur.calculs
      ? Boolean(simulateur.calculs[scenario].garantie) : false;
    if (!revenus.has(duScenario)) revenus.set(duScenario, new Map());
    const parFiche = revenus.get(duScenario);
    if (!parFiche.has(proposition)) {
      const bruts = revenusDActivite(duScenario);
      let lus;
      if (impot === null) {
        lus = [bruts, nets ? revenusNets(simulateur, duScenario, proposition) : null, null];
      } else {
        const deux = netsEtImposables(simulateur, duScenario, proposition);
        lus = deux === null ? [bruts, null, null] : [bruts, ...deux];
      }
      parFiche.set(proposition, lus);
    }
    return parFiche.get(proposition);
  };

  const flux = (scenario, cotisations, niveaux) => {
    const duScenario = comparaison.carriereDe(scenario);
    const [bruts, netsDuScenario, imposables] = revenusDe(scenario);
    const dernier = duScenario !== carriere
      ? comparaison.dernier_revenu_annualise_liberal
      : comparaison.dernier_revenu_annualise;
    const avantImpot = new Flux({
      scenario,
      cotisations,
      revenus: bruts,
      niveaux,
      debut: debutDe(duScenario),
      age: duScenario.age_liquidation,
      sexe: duScenario.sexe,
      dernier_revenu: dernier,
      revenus_nets: netsDuScenario,
      dernier_revenu_net: dernierRevenuNet(dernier, bruts, netsDuScenario),
      exoneree: exonerees[scenario] ?? new Map(),
    });
    if (impot === null) return avantImpot;
    return avecLImpot(simulateur, avantImpot, duScenario, parts, imposables, impot, derniere);
  };

  const systemes = { actuel: flux("actuel", versees, actuels) };
  const reformees = cotisationsReformees(simulateur, comparaison);
  for (const scenario of SCENARIOS.slice(1)) {
    const cotisations = simulateur.calculs[scenario].garantie
      ? cotisationsLiberales(simulateur, versees, comparaison[scenario])
      : reformees;
    systemes[scenario] = flux(scenario, cotisations, niveauxNotionnels(
      simulateur, comparaison, scenario, revalorisation, actuels, derniere));
  }
  return systemes;
}

// -- la fin de la retraite ---------------------------------------------------

/**
 * ∫ S(x) dx de `debut` à `fin` années après le départ, la force de mortalité
 * constante entre deux anniversaires du départ — l'hypothèse de
 * `DonneesMortalite.survieAnnuelle` (`mortalite.js`), qui rend S exponentielle
 * par morceaux.
 */
export function integraleSurvie(courbe, debut, fin) {
  let total = 0.0;
  let x = debut;
  while (x < fin - 1e-12) {
    const rang = Math.floor(x + 1e-12);
    const borne = Math.min(fin, rang + 1);
    if (rang + 1 >= courbe.length) break;
    const haut = courbe[rang];
    const bas = courbe[rang + 1];
    if (haut <= 0.0) break;
    const u0 = x - rang;
    const u1 = borne - rang;
    if (bas <= 0.0) {
      // La dernière cellule s'éteint : la survie y décroît linéairement.
      total += haut * ((u1 - u0) - (u1 * u1 - u0 * u0) / 2.0);
    } else if (Math.abs(bas - haut) <= 1e-15 * haut) {
      total += haut * (u1 - u0);
    } else {
      const logarithme = log(bas / haut);
      total += haut * (exp(logarithme * u1) - exp(logarithme * u0)) / logarithme;
    }
    x = borne;
  }
  return total;
}

function trieesNiveaux(flux) {
  return trieesParAnnee(flux.niveaux);
}

/**
 * Chaque année servie : [année, pension espérée en euros courants, instant
 * moyen en date décimale, années de vie espérées dans l'année].
 *
 * Sous un âge de décès fixe, la pension court du premier mois servi au décès.
 * Sous la survie de génération, chaque morceau d'année compte pour l'espérance
 * de le vivre, sachant qu'on était en vie au départ. Après impôt, chaque année
 * perd ce que l'impôt d'une année vécue en entier retire à sa pension
 * (`Flux.impotDeLaPension`).
 */
export function pensionsEsperees(flux, simulateur, convention) {
  verifierLImpot(flux, convention);
  const esperees = [];
  if (convention.age_deces !== null) {
    const deces = flux.naissance + convention.age_deces;
    for (const [annee, niveau] of trieesNiveaux(flux)) {
      const debut = Math.max(annee, flux.debut);
      const fin = Math.min(annee + 1, deces);
      if (fin > debut) {
        esperees.push([annee, niveau * (fin - debut) * retenu(flux, convention, annee),
          (debut + fin) / 2.0, fin - debut]);
      }
    }
    return esperees;
  }
  const courbe = simulateur.mortalite.courbe(flux.age, flux.debut,
    convention.unisexe ? null : flux.sexe);
  for (const [annee, niveau] of trieesNiveaux(flux)) {
    const debut = Math.max(annee, flux.debut);
    const fin = annee + 1;
    if (fin <= debut) continue;
    const vie = integraleSurvie(courbe, debut - flux.debut, fin - flux.debut);
    if (vie > 0.0) {
      esperees.push([annee, niveau * vie * retenu(flux, convention, annee),
        (debut + fin) / 2.0, vie]);
    }
  }
  return esperees;
}

/**
 * La part de la pension brute de l'année `annee` qui reste : ce que les
 * prélèvements de la convention laissent, moins, après impôt, ce que
 * l'impôt prend.
 */
function retenu(flux, convention, annee) {
  if (convention.impot === null) return convention.retenu(annee);
  return convention.retenu(annee) - flux.impotDeLaPension(annee);
}

/** Une convention après impôt demande un flux qui porte l'impôt de son indexation. */
function verifierLImpot(flux, convention) {
  if (convention.impot !== null && flux.indexation_impot !== convention.impot) {
    throw new Error(`la convention est après impôt ('${convention.impot}') : il faut les flux `
      + `de fluxDesSystemes(…, {impot: '${convention.impot}'})`);
  }
}

/**
 * L'âge de décès des cas types du COR : « 60 + l'espérance de vie à 60 ans de
 * la génération » (annexe méthodologique en ligne du rapport de juin 2026,
 * § 2.3 b), les deux sexes réunis — ses cas types n'en ont pas. Celle du
 * dépôt, en table de génération : la moyenne des deux espérances, puisque la
 * table unisexe moyenne les deux survies.
 */
export function ageDeDecesCor(mortalite, generation) {
  return 60.0 + mortalite.esperanceResiduelle(60.0, generation + 60.0, null);
}

/**
 * Ce que les prélèvements de l'année courante retirent à la pension du
 * scénario 1 de `resultat`, en part du brut : la CSG au taux plein, la CRDS et
 * la CASA sur toute la pension, la cotisation maladie sur sa part
 * complémentaire, et celle de la SNCF et des mines sur la leur, sous le plafond
 * de la SNCF (`partsAssujetties`). Les autres systèmes gardent le taux de la
 * même personne, comme le simulateur le fait (`Montants`, `contexte.js`).
 */
export function tauxDePrelevement(simulateur, resultat, anneeLiquidation = null) {
  const prelevements = simulateur.baremePrelevements.pensions;
  const total = auDepart(simulateur, resultat);
  if (total <= 0.0) return prelevements.tauxTotal;
  let complementaire = 0.0;
  for (const p of resultat.pensions_par_regime) {
    if (prelevements.regimes_maladie.has(p.regime)) complementaire += p.montant;
  }
  // La SNCF et les mines, sur leur part, sous le plafond de la SNCF.
  const parts = prelevements.regimes_speciaux.length > 0
    ? partsAssujetties(simulateur, resultat, anneeLiquidation) : new Map();
  let speciaux = 0.0;
  for (const special of prelevements.regimes_speciaux) {
    speciaux += special.taux * (parts.get(special.serie) ?? 0.0);
  }
  return prelevements.tauxTotal + prelevements.maladie_complementaire * complementaire / total
    + speciaux;
}

/**
 * Les conventions du rendement interne des cas types du COR : les deux sexes
 * réunis, le décès à 60 ans plus l'espérance de vie à 60 ans de la génération,
 * la pension nette — « les cas types de cadre et de non-cadre sont soumis au
 * taux plein de la CSG » (rapport annuel de juin 2026, figure 3.A, note), ce
 * que `tauxDePrelevement` retient pour tous, chaque année au taux de son année
 * (`prelevementsParAnnee`).
 */
export function conventionCor(simulateur, comparaison) {
  return new Convention({
    age_deces: ageDeDecesCor(simulateur.mortalite, comparaison.carriere.annee_naissance),
    unisexe: true,
    prelevement: tauxDePrelevement(simulateur, comparaison.actuel,
      comparaison.carriere.anneeLiquidation),
    prelevements: prelevementsParAnnee(simulateur, comparaison),
  });
}

/**
 * La convention nette, celle du balayage : celle de l'OCDE, la convention du
 * dépôt — la survie de génération du sexe de la carrière, le patrimoine à
 * 1,5 % réel —, ou, avec `cor`, celle du COR (`conventionCor`) ; la pension
 * nette des prélèvements de l'année courante au taux plein dans les deux cas
 * (`tauxDePrelevement`), chaque année au taux de son année
 * (`prelevementsParAnnee`).
 */
export function conventionNette(simulateur, comparaison, cor = false) {
  if (cor) return conventionCor(simulateur, comparaison);
  return new Convention({
    prelevement: tauxDePrelevement(simulateur, comparaison.actuel,
      comparaison.carriere.anneeLiquidation),
    prelevements: prelevementsParAnnee(simulateur, comparaison),
  });
}

/**
 * Les parts de la pension du scénario 1 au départ qui ont payé une cotisation
 * maladie, par cotisation, en une `Map` de la série à sa part : celle des
 * complémentaires (`regimes_maladie`), toujours ; jusqu'en 1997, celle du
 * régime général et des salariés agricoles, de la fonction publique, des
 * retraités indépendants et des exploitants sur leur pension de base, des
 * régimes spéciaux, dont la SNCF et les mines prélèvent encore
 * (`regimes_des_pensions` de l'histoire). Celle de la SNCF depuis 2010 ne prend
 * que la part de sa pension sous son plafond (`maladie_regimes_speciaux`) : la
 * pension du départ en `anneeLiquidation`, menée par les prix en euros de
 * l'année du plafond, que les deux suivent ensuite au même pas. Sans l'année,
 * toute la pension, comme sous la convention de la première tranche.
 *
 * Une cotisation qu'un âge borne (`avant_l_age` de l'histoire) ne prélève qu'un
 * pensionné plus jeune : sous `avantLAge`, un âge que le pensionné n'a pas,
 * chacune de celles qu'un âge plus haut ou égal borne prend la part de ses
 * régimes aux autres ; sans lui, aucune.
 */
export function partsAssujetties(simulateur, resultat, anneeLiquidation = null, avantLAge = null) {
  const total = auDepart(simulateur, resultat);
  if (total <= 0.0) return new Map([["maladie_complementaires", 1.0]]);
  const prelevements = simulateur.baremePrelevements.pensions;
  const historique = historiqueDe(simulateur);
  const groupes = new Map(historique.regimes_des_pensions);
  groupes.set("maladie_complementaires", prelevements.regimes_maladie);
  const bornees = new Set([...historique.avant_l_age]
    .filter(([, age]) => avantLAge !== null && avantLAge <= age).map(([serie]) => serie));
  const prises = new Set([...bornees].flatMap((serie) => [...groupes.get(serie)]));
  const parts = new Map();
  for (const [serie, regimes] of groupes) {
    const bornee = bornees.has(serie);
    if (!bornee && historique.avant_l_age.has(serie)) continue;
    let montant = 0.0;
    for (const p of resultat.pensions_par_regime) {
      if (regimes.has(p.regime) && (bornee || !prises.has(p.regime))) montant += p.montant;
    }
    parts.set(serie, montant / total);
  }
  // La SNCF depuis 2010 : sa part sous son plafond, la pension du départ menée
  // par les prix en euros de l'année du plafond.
  for (const special of prelevements.regimes_speciaux) {
    const part = parts.get(special.serie) ?? 0.0;
    if (special.plafond_annuel !== null && anneeLiquidation !== null && part > 0.0) {
      const montant = part * total * simulateur.macro.coefficientPrix(
        anneeLiquidation, special.annee);
      parts.set(special.serie, part * Math.min(1.0, special.plafond_annuel / montant));
    }
  }
  return parts;
}

/**
 * Du premier départ des systèmes de `comparaison` à la dernière année qu'une de
 * leurs pensions peut atteindre.
 */
function anneesDesPensions(comparaison) {
  const carrieres = SCENARIOS.map((scenario) => comparaison.carriereDe(scenario));
  const premiere = Math.min(...carrieres.map((c) => c.anneeLiquidation));
  const derniere = Math.max(...carrieres.map(derniereAnneeDe));
  return Array.from({ length: derniere - premiere + 1 }, (_, rang) => premiere + rang);
}

/**
 * Les parts assujetties de la pension de `comparaison` (`partsAssujetties`),
 * et, pour chaque âge qui borne une cotisation, du plus jeune au plus vieux, le
 * premier jour du premier mois au premier jour duquel l'assuré l'a, et les
 * parts des mois qui le précèdent : ce que `tauxPensionAnnuel` de l'histoire
 * prend en `avant`. Les deux se rendent en `{ parts, avant }`.
 */
function partsSelonLAge(simulateur, comparaison) {
  const { carriere, actuel } = comparaison;
  const ages = [...new Set(historiqueDe(simulateur).avant_l_age.values())].sort((a, b) => a - b);
  const avant = ages.map((age) => {
    const mois = carriere.dateDeLAge(age);
    const jour = `${String(mois.annee).padStart(4, "0")}-${String(mois.mois).padStart(2, "0")}-01`;
    return [jour, partsAssujetties(simulateur, actuel, carriere.anneeLiquidation, age)];
  });
  return { parts: partsAssujetties(simulateur, actuel, carriere.anneeLiquidation), avant };
}

/**
 * Ce que les prélèvements de chaque année retirent aux pensions de
 * `comparaison`, du premier départ de ses systèmes à la dernière année qu'une
 * pension peut atteindre, au taux plein de CSG : l'histoire que l'IPP retrace
 * (`prelevements-historiques.js`), dont la dernière marche tient au-delà. La
 * cotisation maladie des pensions du régime général et des salariés agricoles
 * naît le 1er juillet 1980 et s'éteint en 1998, sur leur part de la pension ;
 * celle des complémentaires vaut toujours, sur la leur ; celle de la fonction
 * publique, de 1976 à 1997, celle des retraités indépendants, de 1970 à 1997,
 * celle des exploitants, de 1990 à 1997, et celle des régimes spéciaux, de
 * 1980, 1988 ou 1991 à 1997 — à la SNCF et aux mines, jusqu'aujourd'hui —, sur
 * la leur (`partsAssujetties`) ; celle des chemins de fer secondaires, de 1954
 * à 1997, jusqu'aux 60 ans du pensionné, à la place de celle des régimes
 * spéciaux (`partsSelonLAge`). Les autres systèmes gardent les parts du
 * scénario 1, comme ils gardent son taux de l'année courante.
 */
export function prelevementsParAnnee(simulateur, comparaison) {
  const historique = historiqueDe(simulateur);
  const { parts, avant } = partsSelonLAge(simulateur, comparaison);
  return new Map(anneesDesPensions(comparaison)
    .map((annee) => [annee, historique.tauxPensionAnnuel(annee, parts, avant)]));
}

/**
 * La part des pensions de `comparaison` que le revenu imposable de chaque année
 * retient, au taux plein de CSG, les années de `prelevementsParAnnee` : la
 * pension moins la CSG déductible de l'année — rien avant 1997, 1 point en
 * 1997, 3,8 points de 1998 à 2004, 4,2 de 2005 à 2017, 5,9 depuis 2018 (CGI,
 * art. 154 quinquies) — et ses cotisations maladie de l'année, sur leurs parts
 * (`partsSelonLAge`), des cotisations de sécurité sociale (CGI, art. 83). La
 * CRDS, la CASA et le reste de la CSG restent imposables. Appliquée à la
 * pension brute, c'est la pension imposable qu'attend `impot-revenu.js`, avant
 * l'abattement de 10 %.
 */
export function partsImposablesParAnnee(simulateur, comparaison) {
  const historique = historiqueDe(simulateur);
  const { parts, avant } = partsSelonLAge(simulateur, comparaison);
  return new Map(anneesDesPensions(comparaison)
    .map((annee) => [annee, 1.0 - historique.tauxDeductiblePensionAnnuel(annee, parts, avant)]));
}

/**
 * La première année de revenus dont l'impôt prend « les majorations de retraite
 * ou de pension pour charges de famille » : la loi de finances pour 2014 abroge
 * le 2° ter de l'article 81 du code général des impôts, qui les exonérait
 * depuis 1950 (art. 5), et s'applique « à l'impôt sur le revenu dû au titre de
 * 2013 et des années suivantes » (art. 1er, II, 1°) ; « les majorations [...]
 * perçues à compter du 1er janvier 2013 sont imposables »
 * (BOI-RSA-PENS-20-10-20140305, § 1).
 */
export const PREMIERE_ANNEE_MAJORATION_IMPOSABLE = 2013;
/**
 * Jusque-là, « le montant exonéré des majorations pour enfant à charge,
 * augmenté, le cas échéant, des majorations pour avoir eu ou élevé au moins
 * trois enfants, ne peut excéder, pour un même bénéficiaire, 10 % du montant de
 * la pension pour les trois premiers enfants et 5 % par enfant au-delà du
 * troisième » (DB 5 F 1222, n° 4, du 10 février 1999 ;
 * BOI-RSA-PENS-20-10-20120912, § 30) : le surplus s'impose.
 */
export const TAUX_EXONERE_TROIS_ENFANTS = 0.10;
export const TAUX_EXONERE_PAR_ENFANT_AU_DELA = 0.05;

/**
 * La part de `majoration`, la majoration pour enfants que sert l'année `annee`
 * une pension de `pension` sans elle, que l'impôt de l'année exonère : toute,
 * jusqu'aux revenus de 2012, sous la limite de la doctrine
 * (`TAUX_EXONERE_TROIS_ENFANTS`) ; rien ensuite
 * (`PREMIERE_ANNEE_MAJORATION_IMPOSABLE`). Toutes les majorations des régimes
 * de base et complémentaires obligatoires y entrent, celles des enfants à
 * charge comme celles des parents de trois enfants (DB 5 F 1222, n° 3).
 */
export function majorationExoneree(annee, majoration, pension, enfants) {
  if (annee >= PREMIERE_ANNEE_MAJORATION_IMPOSABLE || majoration <= 0.0) return 0.0;
  const taux = TAUX_EXONERE_TROIS_ENFANTS
    + TAUX_EXONERE_PAR_ENFANT_AU_DELA * Math.max(enfants - 3, 0);
  return Math.min(majoration, taux * pension);
}

/**
 * Pour chaque système, la part du niveau de sa pension que l'impôt de chaque
 * année exonère (`majorationExoneree`), aux années servies d'avant
 * `PREMIERE_ANNEE_MAJORATION_IMPOSABLE`, en un objet du scénario à une `Map` de
 * l'année à sa part. Seul le scénario 1 sert une majoration pour enfants, que
 * `faireVivre` mène chaque année. Un système prospectif garde sa pension à qui
 * est parti avant la bascule, et sa part avec elle, celle de la bascule
 * ensuite, la pension s'y revalorisant d'un bloc (`niveauxNotionnels`) ; un
 * système rétroactif n'a rien à exonérer. Ce qu'une majoration exonérée laisse
 * de CSG ne se déduit pas (BOI-RSA-BASE-30-30-20120912, § 90) : la part
 * imposable de l'année ne porte que sur le reste.
 */
export function partsExonerees(simulateur, comparaison) {
  const carriere = comparaison.carriere;
  const resultat = comparaison.actuel;
  const actuelle = new Map();
  if (resultat.avantages_appliques.some((a) => a.code === "majoration_enfants")) {
    const derniere = Math.min(PREMIERE_ANNEE_MAJORATION_IMPOSABLE - 1,
      simulateur.parametres.annee_courante);
    for (let annee = carriere.anneeLiquidation; annee <= derniere; annee += 1) {
      const vivante = faireVivre(simulateur, carriere, resultat, annee);
      const majoration = vivante.majoration_enfants * vivante.coefficient_majoration;
      const niveau = servie(vivante);
      const exoneree = majorationExoneree(annee, majoration, niveau - majoration,
        carriere.nombre_enfants);
      if (exoneree > 0.0) actuelle.set(annee, exoneree / niveau);
    }
  }
  const bascule = simulateur.parametres.annee_bascule;
  const parts = { actuel: actuelle };
  for (const scenario of SCENARIOS.slice(1)) {
    parts[scenario] = new Map();
    if (!(simulateur.calculs[scenario].prospectif
      && comparaison.carriereDe(scenario).anneeLiquidation <= bascule)) continue;
    for (const [annee, part] of actuelle) {
      if (annee <= bascule) parts[scenario].set(annee, part);
    }
    if (actuelle.has(bascule)) {
      for (let annee = bascule + 1; annee < PREMIERE_ANNEE_MAJORATION_IMPOSABLE; annee += 1) {
        parts[scenario].set(annee, actuelle.get(bascule));
      }
    }
  }
  return parts;
}

// -- l'impôt sur le revenu ---------------------------------------------------

const chroniques = new WeakMap();

/**
 * Les paramètres de l'impôt de chaque année de revenus, du premier barème lu
 * à `derniere`, projetés au-delà de la dernière loi de finances lue sur
 * `indexation` par le scénario de projection du simulateur
 * (`BaremesImpotRevenu.chronique`, `impot-revenu.js`) : une `Map`.
 */
function baremesDeLImpot(simulateur, indexation, derniere) {
  if (!chroniques.has(simulateur)) chroniques.set(simulateur, new Map());
  const memoire = chroniques.get(simulateur);
  const cle = `${indexation}:${derniere}`;
  if (!memoire.has(cle)) {
    const baremes = chargerBaremesImpotRevenu(simulateur.paquet);
    if (baremes === null) {
      throw new Error("le paquet ne porte pas les barèmes de l'impôt sur le revenu "
        + "(`impot_revenu`) : l'impôt ne se calcule pas");
    }
    memoire.set(cle, baremes.chronique(derniere, indexation,
      croissanceMacro(simulateur.macro, indexation)));
  }
  return memoire.get(cle);
}

/**
 * Le foyer fiscal de `carriere` l'année `annee` : une personne seule, sans
 * enfant à charge, comme l'OCDE calcule ses taux nets, qui a au 31 décembre
 * l'âge de sa génération — à 65 ans, il ouvre l'abattement des personnes âgées
 * (CGI, art. 157 bis) — et déclare `salaire`, `benefice` et `pension`,
 * imposables. Le bénéfice, de `categorie`, est celui d'un adhérent d'un
 * organisme de gestion agréé, au réel : de 1976 à 2005 il a l'abattement des
 * adhérents, de 2006 à 2022 il échappe à la majoration (CGI, art. 158, 4 bis,
 * 4 ter et 7 ; `beneficeRetenu`, `impot-revenu.js`) ; celui d'un `artisan`, ses
 * règles de la taxe complémentaire, que le foyer déduit de son revenu global
 * l'année où il la paie (`taxeComplementairePayee`).
 */
export function foyerDeLAnnee(carriere, annee, salaire = 0.0, pension = 0.0, benefice = 0.0,
  categorie = "bic", artisan = false, taxeComplementairePayee = 0.0) {
  return new Foyer({
    declarants: [new Declarant({
      salaires: salaire, pensions: pension, benefices: benefice, categorie, artisan,
      age: annee - carriere.annee_naissance,
    })],
    taxe_complementaire_de_l_annee_precedente: taxeComplementairePayee,
  });
}

/**
 * Les familles d'indépendant dont le bénéfice est non commercial ; les autres —
 * l'artisan, le commerçant — ont des bénéfices industriels et commerciaux.
 */
export const FAMILLES_BNC = Object.freeze(["liberal", "avocat"]);

/**
 * Les années où `carriere` a un revenu d'indépendant, en une `Map` de l'année à
 * [part, catégorie, artisan] : la part de son revenu imposable qui est un
 * bénéfice — celle des revenus bruts des lignes d'indépendant dans ceux des
 * lignes cotisées de l'année, un l'année où il n'est qu'indépendant —, la
 * catégorie de ce bénéfice, non commercial pour le libéral et l'avocat,
 * industriel et commercial sinon, et s'il est celui d'un artisan, que la taxe
 * complémentaire distingue (CGI, art. 1649 quater A) : l'affilié des régimes
 * des artisans, que le modèle tient pour l'artisan fiscal ; catégorie et
 * artisan de la ligne au plus fort revenu quand il en a plusieurs.
 */
export function beneficesParAnnee(simulateur, carriere) {
  const revenus = new Map();
  const independants = new Map();
  for (const ligne of carriere.lignes) {
    if (!ligne.cotise) continue;
    revenus.set(ligne.annee, (revenus.get(ligne.annee) ?? 0.0) + ligne.revenu);
    const entree = simulateur.affiliations.dateEntree(carriere, ligne.affiliation, ligne.annee);
    const profil = profilDeLaFiche(simulateur.affiliations, simulateur.catalogue,
      ligne.affiliation, ligne.annee, entree);
    if (profil !== "independant") continue;
    const regimes = simulateur.affiliations.regimes(ligne.affiliation, ligne.annee, entree);
    const famille = familleDeLaFiche(profil, regimes);
    if (!independants.has(ligne.annee)) independants.set(ligne.annee, []);
    independants.get(ligne.annee).push(
      [ligne.revenu, FAMILLES_BNC.includes(famille) ? "bnc" : "bic", famille === "artisan"]);
  }
  const benefices = new Map();
  for (const [annee, lignes] of independants) {
    let total = 0.0;
    for (const [revenu] of lignes) total += revenu;
    const part = revenus.get(annee) > 0.0 ? total / revenus.get(annee) : 1.0;
    let plusFort = lignes[0];
    for (const l of lignes) if (l[0] > plusFort[0]) plusFort = l;
    benefices.set(annee, [Math.min(part, 1.0), plusFort[1], plusFort[2]]);
  }
  return benefices;
}

/**
 * Les revenus imposables de chaque année, partagés entre le salaire et le
 * bénéfice (`beneficesParAnnee`) : les salaires, et les bénéfices avec leur
 * catégorie et s'ils sont d'un artisan, en une paire de `Map`.
 */
function partageDesImposables(simulateur, carriere, imposables) {
  const parts = beneficesParAnnee(simulateur, carriere);
  const salaires = new Map();
  const benefices = new Map();
  for (const [annee, montant] of imposables) {
    const [part, categorie, artisan] = parts.get(annee) ?? [0.0, "bic", false];
    if (part < 1.0) salaires.set(annee, montant * (1.0 - part));
    if (part > 0.0) benefices.set(annee, [montant * part, categorie, artisan]);
  }
  return [salaires, benefices];
}

/**
 * La part de l'impôt d'un foyer que supporte sa pension : au prorata des
 * revenus après leurs abattements de 10 %, le bénéfice tel que l'impôt le
 * retient, un déficit ne comptant pour rien.
 */
function partDeLaPension(impot) {
  let activite = 0.0;
  for (const s of impot.salaires_nets) activite += s;
  for (const b of impot.benefices_retenus) activite += b;
  activite = Math.max(activite, 0.0);
  let pensions = 0.0;
  for (const p of impot.pensions_nettes) pensions += p;
  if (activite + pensions <= 0.0) return 0.0;
  return pensions / (activite + pensions);
}

/**
 * L'impôt sur le revenu de chaque année d'un flux, de la première de la
 * carrière à la dernière que la pension peut atteindre, en une `Map` de l'année
 * à son `ImpotDeLAnnee` : celui du foyer de l'année (`foyerDeLAnnee`), qui
 * déclare son salaire imposable — `salaires`, ceux de `revenusImposables` que
 * le module prend — et la part imposable de l'année (`parts`,
 * `partsImposablesParAnnee`) de ce que la pension sert dans l'année
 * (`Flux.servi`), hors ce que l'impôt en exonère (`Flux.exoneree`), au barème
 * de l'année, projeté au-delà de la dernière loi de finances lue sur
 * `indexation`, jusqu'à `derniere` au moins. `benefices` donne, pour une année
 * d'indépendant, son bénéfice imposable, sa catégorie et s'il est d'un artisan
 * (`partageDesImposables`) ; la taxe complémentaire des bénéfices de l'année
 * précédente, celle des revenus de 1959 comprise, se déduit du revenu global de
 * l'année où le foyer la paie.
 *
 * Chaque année de retraite se compte vécue en entier : l'impôt plus faible de
 * l'année que le décès interrompt n'est pas calculé. L'année du départ, le
 * foyer déclare son dernier salaire et sa première pension, et leur impôt se
 * partage au prorata des deux revenus après leurs abattements de 10 %
 * (`ImpotDeLAnnee.sur_la_pension`) — la taxe complémentaire, qui ne frappe que
 * le bénéfice, n'en est pas. Une année d'avant le premier barème lu, 1960, n'a
 * pas d'impôt.
 */
export function impotsParAnnee(simulateur, flux, carriere, parts, salaires,
  indexation = "prix", derniere = null, benefices = new Map()) {
  const pensions = new Map();
  for (const [annee, niveau] of flux.niveaux) {
    const servieDansLAnnee = niveau * flux.servi(annee);
    if (servieDansLAnnee > 0.0) {
      pensions.set(annee, servieDansLAnnee * (1.0 - (flux.exoneree.get(annee) ?? 0.0))
        * parts.get(annee));
    }
  }
  const annees = [...new Set([...salaires.keys(), ...benefices.keys(), ...pensions.keys()])]
    .sort((a, b) => a - b);
  const impots = new Map();
  if (annees.length === 0) return impots;
  const baremes = baremesDeLImpot(simulateur, indexation,
    Math.max(annees[annees.length - 1], derniere ?? 0));
  const taxes = chargerBaremesImpotRevenu(simulateur.paquet);
  for (const annee of annees) {
    const parametres = baremes.get(annee);
    if (parametres === undefined) continue;
    const salaire = salaires.get(annee) ?? 0.0;
    const pension = pensions.get(annee) ?? 0.0;
    const [benefice, categorie, artisan] = benefices.get(annee) ?? [0.0, "bic", false];
    const [precedent, categoriePrecedente, artisanPrecedent] = benefices.get(annee - 1)
      ?? [0.0, "bic", false];
    const payee = precedent > 0.0 ? taxeComplementaireDesRevenus(
      foyerDeLAnnee(carriere, annee - 1, 0.0, 0.0, precedent, categoriePrecedente,
        artisanPrecedent), annee - 1, taxes) : 0.0;
    const foyer = impotAuxParametres(foyerDeLAnnee(carriere, annee, salaire, pension, benefice,
      categorie, artisan, payee), parametres);
    impots.set(annee, new ImpotDeLAnnee({
      annee, salaire, pension, foyer,
      sur_la_pension: (foyer.impot - foyer.taxe_complementaire) * partDeLaPension(foyer),
      benefice,
    }));
  }
  return impots;
}

/**
 * `flux` sous l'impôt sur le revenu : l'impôt de chaque année
 * (`impotsParAnnee`), les revenus nets qu'il laisse et le dernier revenu net
 * d'une année entière d'impôt (`dernierRevenuApresImpot`).
 *
 * `imposables` sont les revenus imposables de `carriere` (`revenusImposables`),
 * `null` pour un statut sans fiche de paie — l'exploitant agricole —, dont la
 * pension s'impose alors seule. Ceux d'un indépendant sont son bénéfice
 * (`partageDesImposables`).
 */
export function avecLImpot(simulateur, flux, carriere, parts, imposables,
  indexation = "prix", derniere = null) {
  const [salaires, benefices] = imposables === null ? [new Map(), new Map()]
    : partageDesImposables(simulateur, carriere, imposables);
  const impots = impotsParAnnee(simulateur, flux, carriere, parts, salaires, indexation,
    derniere, benefices);
  let apres = null;
  let dernier = null;
  if (flux.revenus_nets !== null && imposables !== null) {
    apres = new Map([...flux.revenus_nets].map(([annee, net]) => [annee,
      net - (impots.has(annee) ? impots.get(annee).sur_le_salaire : 0.0)]));
    dernier = dernierRevenuApresImpot(simulateur, flux, imposables, indexation, derniere,
      benefices);
  }
  return flux.remplace({
    indexation_impot: indexation, impots, revenus_apres_impot: apres,
    dernier_revenu_apres_impot: dernier,
  });
}

/**
 * Le dernier revenu annualisé (`Flux.dernier_revenu`), net de ses prélèvements
 * (`Flux.dernier_revenu_net`) et de l'impôt d'une année entière de ce revenu,
 * déclaré seul, au barème de l'année du départ — celle de ses euros — et sans
 * l'abattement des personnes âgées, comme le revenu d'un actif. Son imposable
 * est le dernier revenu fois le rapport de l'imposable au brut de la dernière
 * année cotisée, partagé comme elle entre le salaire et le bénéfice
 * (`benefices`, `partageDesImposables`). C'est le dernier salaire net que
 * l'OCDE oppose à la pension après impôt (`remplacementApresImpot`) ; `null`
 * sans dernier revenu net.
 */
export function dernierRevenuApresImpot(simulateur, flux, imposables, indexation = "prix",
  derniere = null, benefices = new Map()) {
  if (flux.dernier_revenu_net === null || flux.revenus.size === 0) return null;
  const annee = Math.max(...flux.revenus.keys());
  const imposable = flux.dernier_revenu * (imposables.get(annee) ?? 0.0)
    / flux.revenus.get(annee);
  const depart = flux.annee_liquidation;
  const parametres = baremesDeLImpot(simulateur, indexation,
    Math.max(depart, derniere ?? 0)).get(depart);
  if (parametres === undefined) return flux.dernier_revenu_net;
  const [benefice, categorie, artisan] = benefices.get(annee) ?? [0.0, "bic", false];
  const part = benefice && imposables.get(annee) ? benefice / imposables.get(annee) : 0.0;
  const declarant = new Declarant({
    salaires: imposable * (1.0 - part), benefices: imposable * part, categorie, artisan,
  });
  const impot = impotAuxParametres(new Foyer({ declarants: [declarant] }), parametres);
  return flux.dernier_revenu_net - impot.impot;
}

/**
 * La convention nette (`conventionNette`), après impôt sur le revenu : la
 * pension et les revenus de chaque année perdent l'impôt du foyer de l'année
 * (`impotsParAnnee`), son barème projeté au-delà de la dernière loi de finances
 * lue sur `indexation` — les prix, comme les lois de finances le relèvent, ou
 * le salaire moyen, comme l'OCDE.
 */
export function conventionApresImpot(simulateur, comparaison, cor = false, indexation = "prix") {
  return conventionNette(simulateur, comparaison, cor).avecLImpot(indexation);
}

/**
 * La pension brute du premier mois servi, annualisée, en euros de l'année du
 * départ du système : celle dont partent les niveaux de `niveauxActuels` et de
 * `niveauxNotionnels`, sans l'ASPA ni la garantie vieillesse, rente du pilier
 * comprise. Une réforme prospective sert à qui part avant elle la pension du
 * scénario 1.
 */
export function pensionAuDepart(simulateur, comparaison, scenario) {
  if (scenario === "actuel") return auDepart(simulateur, comparaison.actuel);
  const calcul = simulateur.calculs[scenario];
  const liquidation = comparaison.carriereDe(scenario).anneeLiquidation;
  if (calcul.prospectif && liquidation <= simulateur.parametres.annee_bascule) {
    return auDepart(simulateur, comparaison.actuel);
  }
  const resultat = comparaison[scenario];
  return pensionContributive(calcul, resultat) + (resultat.rente_capitalisation_obligatoire ?? 0.0);
}

/**
 * Le taux de remplacement après impôt au départ du système `scenario` : la
 * pension du premier mois servi, annualisée (`pensionAuDepart`), nette des
 * prélèvements de son année et de l'impôt d'une année entière de cette
 * pension, déclarée seule au barème de l'année du départ, sur le dernier revenu
 * annualisé, net des siens et de l'impôt d'une année entière de ce revenu
 * (`dernierRevenuApresImpot`) : le taux net de l'OCDE (« net replacement
 * rate », *Pensions at a Glance*). `systemes`, les flux de `fluxDesSystemes`
 * sous l'impôt d'`indexation`, s'ils sont déjà calculés ; `null` sans dernier
 * revenu après impôt.
 */
export function remplacementApresImpot(simulateur, comparaison, scenario = "actuel",
  indexation = "prix", systemes = null) {
  const lesSystemes = systemes
    ?? fluxDesSystemes(simulateur, comparaison, { impot: indexation });
  const flux = lesSystemes[scenario];
  const convention = conventionNette(simulateur, comparaison);
  verifierLImpot(flux, convention.avecLImpot(indexation));
  return remplacementApresImpotDe(simulateur, comparaison, scenario, flux, convention,
    partsImposablesParAnnee(simulateur, comparaison));
}

/**
 * `remplacementApresImpot`, de la convention nette et des parts imposables de
 * la comparaison.
 */
function remplacementApresImpotDe(simulateur, comparaison, scenario, flux, convention, parts) {
  const dernier = flux.dernier_revenu_apres_impot;
  if (dernier === null || dernier <= 0.0) return null;
  return pensionApresImpotDe(simulateur, comparaison, scenario, flux, convention, parts) / dernier;
}

/**
 * La pension du premier mois servi, annualisée (`pensionAuDepart`), nette des
 * prélèvements de son année et de l'impôt d'une année entière de cette pension,
 * déclarée seule au barème de l'année du départ.
 */
function pensionApresImpotDe(simulateur, comparaison, scenario, flux, convention, parts) {
  const annee = flux.annee_liquidation;
  const brute = pensionAuDepart(simulateur, comparaison, scenario);
  const parametres = baremesDeLImpot(simulateur, flux.indexation_impot,
    Math.max(...flux.niveaux.keys())).get(annee);
  const imposable = brute * (1.0 - (flux.exoneree.get(annee) ?? 0.0)) * parts.get(annee);
  const impot = parametres === undefined ? 0.0 : impotAuxParametres(
    foyerDeLAnnee(comparaison.carriereDe(scenario), annee, 0.0, imposable),
    parametres).impot;
  return brute * convention.retenu(annee) - impot;
}

// -- les indicateurs ---------------------------------------------------------

/**
 * Les prix et le salaire moyen par tête de chaque année, en indices (un la
 * première année) : ce par quoi un montant courant se déflate ; une paire de
 * `Map`.
 */
function indices(macro, premiere, derniere) {
  const prix = new Map([[premiere, 1.0]]);
  const salaires = new Map([[premiere, 1.0]]);
  for (let annee = premiere + 1; annee <= derniere; annee += 1) {
    prix.set(annee, prix.get(annee - 1) * (1.0 + macro.inflation.valeur(annee)));
    salaires.set(annee, salaires.get(annee - 1) * (1.0 + macro.salaire_moyen.valeur(annee)));
  }
  return [prix, salaires];
}

/**
 * Le taux `r` qui annule Σ montant × (1 + r)^-(t − t₀), par dichotomie ;
 * `null` quand aucun taux des bornes ne l'annule.
 *
 * Les cotisations, négatives, précèdent les pensions : la somme décroît avec le
 * taux, de positive aux taux bas, où les pensions lointaines pèsent le plus, à
 * négative aux taux hauts. Une seule racine, donc, et la dichotomie la trouve
 * sans dérivée, comme celle du pilier (`tauxInterne`, `capitalisation.js`).
 */
export function rendementInterne(flux) {
  if (flux.length === 0) return null;
  let origine = Infinity;
  for (const [instant] of flux) origine = Math.min(origine, instant);
  const valeur = (taux) => {
    let somme = 0.0;
    for (const [instant, montant] of flux) somme += montant * pow(1.0 + taux, -(instant - origine));
    return somme;
  };
  let [bas, haut] = BORNES_RENDEMENT;
  if (valeur(bas) <= 0.0 || valeur(haut) >= 0.0) return null;
  for (let i = 0; i < 200; i += 1) {
    const milieu = 0.5 * (bas + haut);
    if (valeur(milieu) > 0.0) bas = milieu;
    else haut = milieu;
    if (haut - bas < 1e-12) break;
  }
  return 0.5 * (bas + haut);
}

/**
 * Le milieu de la part cotisée d'une année : l'année entière, sauf celle du
 * départ, cotisée jusqu'au premier mois servi.
 */
function instantCotisation(flux, annee) {
  if (annee === flux.annee_liquidation) return annee + Math.max(flux.debut - annee, 0.0) / 2.0;
  return annee + 0.5;
}

/**
 * Les indicateurs de cycle de vie d'un système, sous `convention`.
 *
 * Sous une convention nette, la pension est nette, et ce qui la rapporte à un
 * revenu d'activité — le taux d'annuité, le remplacement sur le cycle de vie et
 * au décès — la rapporte au revenu net (`Flux.revenus_nets`), ou ne se calcule
 * pas sans lui. Après impôt, la pension et les revenus sont nets de l'impôt de
 * chaque année (`Flux.revenus_apres_impot`). Le patrimoine reste en années de
 * dernier revenu brut ; l'OCDE exprime le sien, net, en années de dernier
 * salaire net. Les cotisations sont ce que la paie supporte, brutes par nature,
 * et l'impôt ne les atteint pas : la part patronale n'est pas un revenu du
 * salarié, et la sienne se déduit de son revenu imposable (CGI, art. 83).
 */
export function indicateurs(flux, simulateur, convention = new Convention()) {
  const esperees = pensionsEsperees(flux, simulateur, convention);
  let duree = 0.0;
  for (const [, , , vie] of esperees) duree += vie;
  const annees = [...esperees.map(([annee]) => annee), ...flux.cotisations.keys(),
    ...flux.revenus.keys()];
  const [prix, salaires] = indices(simulateur.macro, Math.min(...annees), Math.max(...annees));
  let revenus;
  let dernier;
  if (convention.impot !== null) {
    revenus = flux.revenus_apres_impot;
    dernier = flux.dernier_revenu_apres_impot;
  } else if (convention.nette) {
    revenus = flux.revenus_nets;
    dernier = flux.dernier_revenu_net;
  } else {
    revenus = flux.revenus;
    dernier = flux.dernier_revenu;
  }

  let pensionsSmpt = 0.0;
  for (const [annee, montant] of esperees) pensionsSmpt += montant / salaires.get(annee);
  let cotisationsSmpt = 0.0;
  for (const [annee, montant] of flux.cotisations) cotisationsSmpt += montant / salaires.get(annee);
  let revenusSmpt = null;
  if (revenus !== null) {
    revenusSmpt = 0.0;
    for (const [annee, montant] of revenus) revenusSmpt += montant / salaires.get(annee);
  }
  const carriere = flux.duree_carriere;

  const chronique = (indice) => [
    ...[...flux.cotisations].map(([annee, montant]) => [
      instantCotisation(flux, annee), -montant / indice.get(annee)]),
    ...esperees.map(([annee, montant, instant]) => [instant, montant / indice.get(annee)]),
  ];

  let patrimoine = null;
  let valeurNette = null;
  let remplacementAuDeces = null;
  if (flux.dernier_revenu > 0.0) {
    const liquidation = flux.annee_liquidation;
    const actualisation = 1.0 + convention.taux_actualisation;
    // Un montant courant, en euros du départ, actualisé au départ — capitalisé
    // jusqu'à lui s'il le précède.
    const aLaDate = (annee, montant, instant) => montant * prix.get(liquidation) / prix.get(annee)
      * pow(actualisation, -(instant - flux.debut));
    patrimoine = 0.0;
    for (const [annee, montant, instant] of esperees) patrimoine += aLaDate(annee, montant, instant);
    let capitalisees = 0.0;
    for (const [annee, montant] of flux.cotisations) {
      capitalisees += aLaDate(annee, montant, instantCotisation(flux, annee));
    }
    valeurNette = patrimoine - capitalisees;
    patrimoine /= flux.dernier_revenu;
    valeurNette /= flux.dernier_revenu;
    const derniereServie = Math.floor(flux.debut + duree - 1e-9);
    if (duree > 0.0 && flux.niveaux.has(derniereServie) && dernier) {
      remplacementAuDeces = flux.niveaux.get(derniereServie)
        * retenu(flux, convention, derniereServie)
        / (dernier * salaires.get(derniereServie) / salaires.get(liquidation));
    }
  }

  const avecCotisations = flux.cotisations.size > 0;
  return new Indicateurs({
    scenario: flux.scenario,
    duree_retraite: duree,
    part_de_vie: flux.age + duree > 0 ? duree / (flux.age + duree) : 0.0,
    duree_carriere: carriere,
    taux_recuperation: cotisationsSmpt > 0 ? pensionsSmpt / cotisationsSmpt : null,
    taux_annuite: revenusSmpt ? pensionsSmpt / revenusSmpt : null,
    taux_remplacement_cycle: duree > 0 && carriere > 0 && revenusSmpt
      ? (pensionsSmpt / duree) / (revenusSmpt / carriere) : null,
    rendement_reel: avecCotisations ? rendementInterne(chronique(prix)) : null,
    rendement_smpt: avecCotisations ? rendementInterne(chronique(salaires)) : null,
    patrimoine,
    valeur_nette: valeurNette,
    remplacement_au_deces: remplacementAuDeces,
  });
}

/** Les indicateurs d'une carrière sous chacun des six systèmes. */
export function indicateursDesSystemes(simulateur, comparaison, convention = new Convention()) {
  const systemes = fluxDesSystemes(simulateur, comparaison,
    { nets: convention.nette, impot: convention.impot });
  return Object.fromEntries(Object.entries(systemes)
    .map(([scenario, flux]) => [scenario, indicateurs(flux, simulateur, convention)]));
}

// -- les âges de départ ------------------------------------------------------

/**
 * Le pas du balayage des âges de départ, en années : le trimestre, que la
 * décote et la surcote comptent, et que TRAJECTOiRE balaie (`casTypesCOR.R`, au
 * commit `0963b57`).
 */
export const PAS_DES_AGES = 0.25;

/**
 * Le minimum vieillesse d'une personne seule l'année `annee`, en euros par an :
 * l'ASPA depuis 2007, menée sur les prix au-delà de son barème ; avant, ses
 * deux étages, l'AVTS et l'allocation supplémentaire (action 138, étape 6).
 * `null` avant la loi du 14 mars 1941.
 */
export function minimumVieillesse(simulateur, annee) {
  const bareme = simulateur.scenarioActuel.minimumVieillesse;
  if (annee <= bareme.constructor.DERNIERE_ANNEE_A_DEUX_ETAGES) {
    const etages = bareme.deuxEtages(annee);
    return etages === null ? null : etages.avts + etages.supplementaire;
  }
  const plafond = bareme.plafond(annee);
  return plafond === null ? null : plafond[0];
}

/**
 * La dernière année civile travaillée en entier avant celle du départ :
 * TRAJECTOiRE y lit le dernier revenu de son taux de remplacement net, pour
 * éviter les années incomplètes de la fin de carrière. `null` sans année
 * pleine.
 */
export function derniereAnneePleine(carriere) {
  const couverture = new Map();
  for (const ligne of carriere.lignes) {
    if (ligne.cotise && ligne.annee < carriere.anneeLiquidation) {
      couverture.set(ligne.annee, (couverture.get(ligne.annee) ?? 0.0) + ligne.fraction_annee);
    }
  }
  const pleines = [...couverture].filter(([, part]) => part >= 1.0 - 1e-9)
    .map(([annee]) => annee);
  return pleines.length ? Math.max(...pleines) : null;
}

/**
 * La pension nette du départ sur le revenu net de la dernière année pleine,
 * chacun ramené à une même unité : TRAJECTOiRE publie les trois
 * (`txRemplacementNetEuroCourant`, `…EuroConstant`, `…Smpt`). Elles ne
 * diffèrent que de ce que les prix et le salaire moyen ont fait entre l'année
 * du revenu et celle du départ. Ses champs :
 *
 * - `courants` : chacun en euros de son année ;
 * - `constants` : chacun en euros constants ;
 * - `salaire_moyen` : chacun en salaire moyen par tête de son année : le taux
 *   de remplacement du simulateur, en net.
 */
export class RemplacementNet {
  constructor({ courants, constants, salaire_moyen }) {
    Object.assign(this, { courants, constants, salaire_moyen });
  }
}

/**
 * Le taux de remplacement net au départ de `carriere`, en trois unités ;
 * `null` sans année pleine ou sans revenu net.
 */
export function remplacementNet(simulateur, carriere, nets, pensionNette) {
  const annee = derniereAnneePleine(carriere);
  if (annee === null || !nets || nets.size === 0 || (nets.get(annee) ?? 0.0) <= 0.0) {
    return null;
  }
  const courants = pensionNette / nets.get(annee);
  const liquidation = carriere.anneeLiquidation;
  const { macro } = simulateur;
  return new RemplacementNet({
    courants,
    constants: courants / macro.coefficientPrix(annee, liquidation),
    salaire_moyen: courants / macro.coefficientSalaireMoyen(annee, liquidation),
  });
}

/**
 * Un âge du balayage, et ce qu'y donne chacun des six systèmes, en net. Ses
 * champs, ceux d'après `annee` chacun un objet par système :
 *
 * - `age` ;
 * - `annee` : l'année du départ du scénario 1 ; celui du scénario 6 est plus
 *   tard quand son âge légal le reporte (`Comparaison.carriereDe`) ;
 * - `indicateurs` : les indicateurs de chaque système, sous la convention
 *   nette, ou après impôt ;
 * - `pensions_nettes` : la pension nette du premier mois servi, annualisée, en
 *   euros de l'année du départ de chaque système ;
 * - `pensions_aspa` : la même, rapportée au minimum vieillesse d'une personne
 *   seule de cette année (`minimumVieillesse`) ; `null` sans barème ;
 * - `remplacements` : le taux de remplacement net au départ ; `null` sans
 *   revenu net ;
 * - `remplacements_apres_impot` : après impôt, le taux de remplacement après
 *   impôt au départ (`remplacementApresImpot`) ; `null` avant impôt ;
 * - `pensions_apres_impot` : après impôt, son numérateur : la pension nette du
 *   premier mois servi, annualisée, moins l'impôt d'une année entière d'elle
 *   seule, en euros de l'année du départ de chaque système ; `null` avant
 *   impôt.
 */
export class Depart {
  constructor({
    age, annee, indicateurs: lesIndicateurs, pensions_nettes, pensions_aspa, remplacements,
    remplacements_apres_impot = null, pensions_apres_impot = null,
  }) {
    Object.assign(this, {
      age, annee, indicateurs: lesIndicateurs, pensions_nettes, pensions_aspa, remplacements,
      remplacements_apres_impot, pensions_apres_impot,
    });
  }
}

/**
 * Ce que donne, en net, le départ de `comparaison` sous les six systèmes
 * (`conventionNette`) ; avec `impot`, l'indexation du barème de l'impôt sur le
 * revenu, les indicateurs après impôt (`conventionApresImpot`), la pension et
 * le taux de remplacement après impôt.
 */
export function depart(simulateur, comparaison, cor = false, age = null, impot = null) {
  const convention = impot === null ? conventionNette(simulateur, comparaison, cor)
    : conventionApresImpot(simulateur, comparaison, cor, impot);
  const systemes = fluxDesSystemes(simulateur, comparaison, { nets: true, impot });
  let apres = null;
  let pensionsApres = null;
  if (impot !== null) {
    const parts = partsImposablesParAnnee(simulateur, comparaison);
    apres = Object.fromEntries(Object.entries(systemes).map(([scenario, flux]) => [scenario,
      remplacementApresImpotDe(simulateur, comparaison, scenario, flux, convention, parts)]));
    pensionsApres = Object.fromEntries(Object.entries(systemes).map(([scenario, flux]) => [
      scenario, pensionApresImpotDe(simulateur, comparaison, scenario, flux, convention, parts)]));
  }
  const pensions = {};
  const aspa = {};
  const remplacements = {};
  for (const [scenario, flux] of Object.entries(systemes)) {
    const carriere = comparaison.carriereDe(scenario);
    const nette = pensionAuDepart(simulateur, comparaison, scenario)
      * convention.retenu(carriere.anneeLiquidation);
    const minimum = minimumVieillesse(simulateur, carriere.anneeLiquidation);
    pensions[scenario] = nette;
    aspa[scenario] = minimum ? nette / minimum : null;
    remplacements[scenario] = remplacementNet(simulateur, carriere, flux.revenus_nets, nette);
  }
  return new Depart({
    age: age === null ? comparaison.carriere.age_liquidation : age,
    annee: comparaison.carriere.anneeLiquidation,
    indicateurs: Object.fromEntries(Object.entries(systemes)
      .map(([scenario, flux]) => [scenario, indicateurs(flux, simulateur, convention)])),
    pensions_nettes: pensions,
    pensions_aspa: aspa,
    remplacements,
    remplacements_apres_impot: apres,
    pensions_apres_impot: pensionsApres,
  });
}

/**
 * Les âges de départ de la carrière que `batir(age)` rend liquidée à `age`, de
 * `pas` en `pas` : de l'âge d'ouverture, carrière longue comprise, à l'âge
 * d'annulation de la décote, les âges « au plus tôt » et « au taux plein
 * automatique » de `agesDeLEstimation` (`pilote.js`), partis de `ageDemande`,
 * chacun un point fixe sur la carrière que l'âge déplace. Le dernier est
 * toujours l'âge d'annulation, même s'il n'est pas à un pas du précédent. Vide
 * quand le droit n'oppose aucun âge à la carrière.
 */
export function agesBalayes(simulateur, batir, ageDemande, pas = PAS_DES_AGES) {
  const ages = agesDeLEstimation(simulateur.scenarioActuel, batir, ageDemande);
  if (ages === null) return [];
  const debut = Number(ages.legal);
  const fin = Number(ages.automatique);
  const nombre = Math.floor((fin - debut) / pas + 1e-9);
  const balayes = [];
  for (let rang = 0; rang <= nombre; rang += 1) {
    balayes.push(Number((debut + rang * pas).toFixed(9)));
  }
  if (fin - balayes[balayes.length - 1] > 1e-9) balayes.push(fin);
  return balayes;
}

/**
 * Les indicateurs nets de la carrière que `batir(age)` rend liquidée à `age`, à
 * chacun de ses âges de départ (`agesBalayes`, partis de `ageDemande`) ; avec
 * `impot`, après impôt (`depart`).
 */
export function balayageDUneCarriere(simulateur, batir, ageDemande, cor = false,
  pas = PAS_DES_AGES, impot = null) {
  return agesBalayes(simulateur, batir, ageDemande, pas)
    .map((age) => depart(simulateur, simulateur.simuler(batir(age)), cor, age, impot));
}

// -- la pension par étage, et le revenu autour du départ ----------------------

/**
 * L'étage d'un système notionnel : son compte, où la bascule a versé les droits
 * de tous les régimes de répartition.
 */
export const ETAGE_NOTIONNEL = "notionnel";
/** Celui du pilier capitalisé du scénario 6. */
export const ETAGE_CAPITALISE = "capitalise";

/**
 * Les années que `revenusAutourDuDepart` montre de part et d'autre de celle du
 * départ : Typfallsmodellen commence son tableau 2 dix ans avant
 * (« Int(par − 10) »).
 */
export const ANNEES_AUTOUR_DU_DEPART = 10;

function rapport(montant, revenu) {
  if (montant === null || revenu === null || revenu <= 0.0) return null;
  return montant / revenu;
}

/**
 * La pension du départ, étage par étage, et ce qu'elle remplace du dernier
 * revenu : le tableau 1 de Typfallsmodellen (`pensionParEtage`).
 *
 * Les montants sont annuels, dans une même unité : les euros de l'année du
 * départ pour un système du dépôt. Sans fiche de paie, le dernier revenu net
 * est `null` ; avant impôt, les deux champs après impôt. Ses champs :
 *
 * - `etages` : le brut de chaque étage, dans l'ordre où les régimes le servent,
 *   en un objet de l'étage à son montant ;
 * - `dernier_revenu` : le dernier revenu d'activité annualisé
 *   (`Flux.dernier_revenu`) ;
 * - `nette` et `dernier_revenu_net` : la pension nette des prélèvements de
 *   l'année du départ, et le dernier revenu net (`Flux.dernier_revenu_net`) ;
 * - `apres_impot` et `dernier_revenu_apres_impot` : la pension nette aussi de
 *   l'impôt d'une année entière d'elle seule, et le dernier revenu après impôt
 *   (`Flux.dernier_revenu_apres_impot`).
 */
export class PensionParEtage {
  constructor({
    etages, dernier_revenu, nette = null, dernier_revenu_net = null, apres_impot = null,
    dernier_revenu_apres_impot = null,
  }) {
    Object.assign(this, {
      etages, dernier_revenu, nette, dernier_revenu_net, apres_impot,
      dernier_revenu_apres_impot,
    });
    Object.freeze(this);
  }

  get brute() {
    let total = 0.0;
    for (const montant of Object.values(this.etages)) total += montant;
    return total;
  }

  /** Chaque étage en part du dernier revenu ; vide sans dernier revenu. */
  get parts() {
    if (this.dernier_revenu <= 0.0) return {};
    return Object.fromEntries(Object.entries(this.etages)
      .map(([etage, montant]) => [etage, montant / this.dernier_revenu]));
  }

  get remplacement_brut() {
    return rapport(this.brute, this.dernier_revenu);
  }

  get remplacement_net() {
    return rapport(this.nette, this.dernier_revenu_net);
  }

  /** Le taux net de l'OCDE (`remplacementApresImpot`). */
  get remplacement_apres_impot() {
    return rapport(this.apres_impot, this.dernier_revenu_apres_impot);
  }

  dictionnaire() {
    return {
      etages: { ...this.etages }, parts: this.parts, brute: this.brute,
      dernier_revenu: this.dernier_revenu, nette: this.nette,
      dernier_revenu_net: this.dernier_revenu_net, apres_impot: this.apres_impot,
      dernier_revenu_apres_impot: this.dernier_revenu_apres_impot,
      remplacement_brut: this.remplacement_brut,
      remplacement_net: this.remplacement_net,
      remplacement_apres_impot: this.remplacement_apres_impot,
    };
  }
}

/**
 * La pension brute du premier mois servi, annualisée (`pensionAuDepart`), étage
 * par étage, en euros de l'année du départ du système. Au scénario 1, chaque
 * régime sert l'étage que le catalogue lui donne — la base, la complémentaire,
 * l'intégré —, sa part de la majoration pour enfants comprise ; un système
 * notionnel sert son compte, et le scénario 6 son pilier capitalisé. Une
 * réforme prospective sert à qui part avant elle les étages du scénario 1.
 */
export function etagesAuDepart(simulateur, comparaison, scenario) {
  if (scenario !== "actuel") {
    const calcul = simulateur.calculs[scenario];
    const liquidation = comparaison.carriereDe(scenario).anneeLiquidation;
    if (!(calcul.prospectif && liquidation <= simulateur.parametres.annee_bascule)) {
      const resultat = comparaison[scenario];
      const etages = { [ETAGE_NOTIONNEL]: pensionContributive(calcul, resultat) };
      const rente = resultat.rente_capitalisation_obligatoire ?? 0.0;
      if (rente) etages[ETAGE_CAPITALISE] = rente;
      return etages;
    }
  }
  const resultat = comparaison.actuel;
  const etages = {};
  const porter = (regime, montant) => {
    if (!montant) return;
    const { etage } = simulateur.catalogue.obtenir(regime);
    etages[etage] = (etages[etage] ?? 0.0) + montant;
  };
  // Ce que `auDepart` additionne : les régimes de répartition, et toute la
  // majoration pour enfants.
  for (const pension of resultat.pensions_par_regime) {
    if (!horsRepartition(simulateur, pension.regime)) porter(pension.regime, pension.montant);
  }
  for (const avantage of resultat.avantages_appliques) {
    if (avantage.code === "majoration_enfants") {
      for (const [regime, part] of avantage.par_regime ?? []) porter(regime, part);
    }
  }
  return etages;
}

/**
 * La pension du départ du système `scenario`, étage par étage
 * (`etagesAuDepart`), en part du dernier revenu annualisé : le tableau 1 de
 * Typfallsmodellen, de Pensionsmyndigheten (registre, `typfallsmodellen`,
 * chantier « 138.9 »), qui rend chaque étage brut en part du salaire de fin de
 * carrière, et la pension après impôt en part du salaire après impôt. Le brut
 * en est le taux de remplacement du simulateur ; la pension nette des
 * prélèvements de l'année du départ, au taux plein (`conventionNette`), se
 * rapporte au dernier revenu net ; sous l'impôt, la pension après l'impôt d'une
 * année entière d'elle seule, au dernier revenu après impôt : le taux net de
 * l'OCDE (`remplacementApresImpot`).
 *
 * `systemes`, les flux de `fluxDesSystemes`, nets ou sous un impôt, s'ils sont
 * déjà calculés ; sans eux, les flux nets, avant impôt.
 *
 * Comme les autres indicateurs du module, la pension n'a ni l'ASPA ni la
 * garantie vieillesse, que l'impôt finance, quand Typfallsmodellen compte sa
 * garantie (« garantipension ») ; le dernier revenu est celui de la dernière
 * année cotisée, annualisé, quand Typfallsmodellen moyenne les cinq dernières,
 * en prix constants.
 */
export function pensionParEtage(simulateur, comparaison, scenario = "actuel", systemes = null) {
  const lesSystemes = systemes ?? fluxDesSystemes(simulateur, comparaison, { nets: true });
  const flux = lesSystemes[scenario];
  const convention = conventionNette(simulateur, comparaison);
  const etages = etagesAuDepart(simulateur, comparaison, scenario);
  const brute = new PensionParEtage({ etages, dernier_revenu: flux.dernier_revenu }).brute;
  const apres = flux.impots === null ? null : pensionApresImpotDe(
    simulateur, comparaison, scenario, flux, convention,
    partsImposablesParAnnee(simulateur, comparaison));
  return new PensionParEtage({
    etages, dernier_revenu: flux.dernier_revenu,
    nette: brute * convention.retenu(flux.annee_liquidation),
    dernier_revenu_net: flux.dernier_revenu_net, apres_impot: apres,
    dernier_revenu_apres_impot: flux.dernier_revenu_apres_impot,
  });
}

/**
 * Une année autour du départ, en euros de l'année du départ : ce que la
 * carrière gagne, ce que la pension sert, et ce que les prélèvements et l'impôt
 * en laissent (`revenusAutourDuDepart`). Ses champs :
 *
 * - `annee` ;
 * - `revenu` : le revenu d'activité brut de l'année ;
 * - `pension` : la pension brute qu'elle sert, de ses mois servis ;
 * - `net` : les deux, nets de leurs prélèvements ; `null` sans fiche de paie ;
 * - `impot` : l'impôt sur le revenu du foyer de l'année ; `null` avant impôt.
 */
export class AnneeAutourDuDepart {
  constructor({ annee, revenu, pension, net, impot }) {
    Object.assign(this, { annee, revenu, pension, net, impot });
    Object.freeze(this);
  }

  get brut() {
    return this.revenu + this.pension;
  }

  get apres_impot() {
    if (this.net === null || this.impot === null) return null;
    return this.net - this.impot;
  }

  dictionnaire() {
    return {
      annee: this.annee, revenu: this.revenu, pension: this.pension, brut: this.brut,
      net: this.net, impot: this.impot, apres_impot: this.apres_impot,
    };
  }
}

/**
 * Le revenu de chaque année, de `annees` avant celle du départ du système
 * `scenario` à `annees` après, en euros de l'année du départ, les prix
 * déflatant chaque année : le tableau 2 de Typfallsmodellen, que ses deux
 * figures dessinent, et qui commence dix ans avant le départ. Le revenu
 * d'activité, la pension des mois servis (`Flux.servi`), leur net, la pension
 * nette des prélèvements de son année au taux plein (`conventionNette`), et,
 * sous l'impôt, l'impôt du foyer de l'année (`impotsParAnnee`). `systemes`
 * comme pour `pensionParEtage`.
 */
export function revenusAutourDuDepart(simulateur, comparaison, scenario = "actuel",
  systemes = null, annees = ANNEES_AUTOUR_DU_DEPART) {
  const lesSystemes = systemes ?? fluxDesSystemes(simulateur, comparaison, { nets: true });
  const flux = lesSystemes[scenario];
  const convention = conventionNette(simulateur, comparaison);
  const depart = flux.annee_liquidation;
  const lignes = [];
  for (let annee = depart - annees; annee <= depart + annees; annee += 1) {
    const euros = simulateur.macro.coefficientPrix(annee, depart);
    const pension = (flux.niveaux.get(annee) ?? 0.0) * flux.servi(annee);
    const net = flux.revenus_nets === null ? null
      : ((flux.revenus_nets.get(annee) ?? 0.0) + pension * convention.retenu(annee)) * euros;
    let impot = null;
    if (flux.impots !== null) {
      impot = flux.impots.has(annee) ? flux.impots.get(annee).impot * euros : 0.0;
    }
    lignes.push(new AnneeAutourDuDepart({
      annee, revenu: (flux.revenus.get(annee) ?? 0.0) * euros, pension: pension * euros,
      net, impot,
    }));
  }
  return lignes;
}

// -- l'âge d'équilibre -------------------------------------------------------

/**
 * La référence du compte, la génération à laquelle il rapporte les autres :
 * celle qui a l'âge de référence au 1er janvier de l'année de la bascule. La
 * conversion des droits acquis prend le diviseur de cet âge à cette date
 * (`ScenarioNotionnel._droitsAcquis`, `scenario-notionnel.js`), 65 ans en 2026,
 * la génération 1961. Elle se rend en un objet :
 *
 * - `naissance` : sa naissance, en date décimale : l'année de la bascule moins
 *   l'âge de référence, un 1er janvier pour un âge en années entières ;
 * - `age` et `annee` : l'âge de référence, et l'année de la bascule, où elle
 *   l'atteint.
 */
export function referenceDuCompte(simulateur) {
  const annee = simulateur.parametres.annee_bascule;
  const age = simulateur.ageReference.age(annee);
  return { naissance: annee - age, age, annee };
}

/**
 * L'arrondi au pair, celui de `int(round(x))` en Python, que le cycle de vie a
 * d'abord suivi.
 */
function arrondi(x) {
  const r = Math.round(x);
  return Math.abs(x - Math.trunc(x)) === 0.5 && r % 2 !== 0 ? r - 1 : r;
}

/**
 * Le diviseur du compte de qui est né à la date `naissance` — un 1er janvier
 * pour une génération — et part à `age`, en mois entiers : celui de
 * `Convertisseur.coefficient` (`conversion.js`), le mois du départ. `sexe` ne
 * compte que sous une table par sexe.
 */
export function diviseurA(simulateur, naissance, age, sexe = null, population = null) {
  const mois = arrondi((naissance + age) * 12.0);
  const annee = Math.floor(mois / 12);
  return simulateur.convertisseur.coefficient(age, annee, sexe, mois - 12 * annee + 1,
    population).diviseur;
}

/** Le report le plus long que `ageCible` cherche, en mois. */
export const REPORT_MAXIMAL = 600;

/**
 * Le critère de l'âge cible de l'ETK (« tavoite-eläkeikä », TyEL 75 c §) : le
 * premier mois entier où la majoration pour report, comptée depuis
 * `ageMinimal`, compense au moins ce que le coefficient retire à la pension —
 * où `coefficient × majoration(mois)` atteint un. La majoration croît avec le
 * report : en Finlande, `1 + 0,004 × mois`. `moisMinimum` borne la recherche
 * en deçà de l'âge minimal : zéro en Finlande, où l'on ne part pas avant lui ;
 * moins sous le compte, où une génération plus ancienne que la référence
 * retrouve son diviseur plus tôt.
 */
export function ageCible(coefficient, majoration, ageMinimal, moisMinimum = 0) {
  const compense = (mois) => coefficient * majoration(mois) >= 1.0;
  let mois = 0;
  if (compense(mois)) {
    while (mois > moisMinimum && compense(mois - 1)) mois -= 1;
  } else {
    while (!compense(mois)) {
      mois += 1;
      if (mois > REPORT_MAXIMAL) {
        throw new Error(`aucun report de ${REPORT_MAXIMAL} mois au plus ne `
          + `compense le coefficient ${coefficient}`);
      }
    }
  }
  return ageMinimal + mois / 12.0;
}

/** L'âge le plus bas où l'on cherche un âge d'équilibre, en années. */
export const AGE_EQUILIBRE_MINIMAL = 40.0;

/**
 * L'âge d'équilibre du diviseur de la génération `generation`, née un
 * 1er janvier, sous la mortalité de `population` : la même des deux côtés de
 * l'égalité, pour que l'âge ne mesure que la longévité des générations. C'est
 * `ageCible`, le coefficient et la majoration lus sur le diviseur, le report
 * compté depuis l'âge de référence ; puis l'âge exact, entre le mois trouvé et
 * le précédent, où les deux diviseurs sont égaux.
 *
 * L'âge auquel la génération retrouve le diviseur de la référence se rend en
 * un objet :
 *
 * - `generation` ;
 * - `age` : l'âge où son diviseur égale celui de la référence, interpolé entre
 *   les deux mois qui l'encadrent ;
 * - `au_mois` : le premier mois entier où il ne le dépasse plus, où la pension,
 *   à capital égal, est au moins celle de la référence : l'âge cible de l'ETK,
 *   compté comme le sien ;
 * - `diviseur_reference` et `diviseur_a_l_age_de_reference` : le diviseur de
 *   la référence, et celui de la génération à l'âge de référence ;
 * - `coefficient` : ce que la longévité de la génération retire à sa pension à
 *   l'âge de référence, à capital égal : le rapport des deux diviseurs, comme
 *   le coefficient de l'ETK est le rapport de deux valeurs en capital.
 */
export function ageDEquilibre(simulateur, generation, sexe = null, population = null) {
  const reference = referenceDuCompte(simulateur);
  const cible = diviseurA(simulateur, reference.naissance, reference.age, sexe, population);
  const diviseur = (mois) => diviseurA(simulateur, generation, reference.age + mois / 12.0,
    sexe, population);
  const aLaReference = diviseur(0);
  const minimum = arrondi((AGE_EQUILIBRE_MINIMAL - reference.age) * 12.0);
  const auMois = ageCible(cible / aLaReference, (mois) => aLaReference / diviseur(mois),
    reference.age, minimum);
  const mois = arrondi((auMois - reference.age) * 12.0);
  if (mois <= minimum) {
    throw new Error(`génération ${generation} : pas d'âge d'équilibre `
      + `au-dessus de ${AGE_EQUILIBRE_MINIMAL} ans`);
  }
  const avant = diviseur(mois - 1);
  const apres = diviseur(mois);
  return {
    generation,
    age: auMois - (cible - apres) / (avant - apres) / 12.0,
    au_mois: auMois,
    diviseur_reference: cible,
    diviseur_a_l_age_de_reference: aLaReference,
    coefficient: cible / aLaReference,
  };
}

/**
 * Les années de retraite qu'espère qui part à `age` à la date `debut`, sous la
 * survie de génération du sexe `sexe`, les deux réunis pour `null`, et de
 * `population`, la population générale pour `null` : la durée de
 * `pensionsEsperees`, d'un seul tenant.
 */
export function dureeEsperee(simulateur, age, debut, sexe = null, population = null) {
  const courbe = simulateur.mortalite.courbe(age, debut, sexe, true, population);
  return integraleSurvie(courbe, 0.0, courbe.length - 1);
}

/**
 * La part de la vie passée en retraite de qui part à `age` à la date `debut` :
 * la durée espérée sur l'âge plus elle, celle de `Indicateurs.part_de_vie` pour
 * la population générale ; sous la convention du COR, (D − âge) / D, D l'âge de
 * décès de sa génération (`ageDeDecesCor`), les deux sexes réunis, la
 * population générale.
 */
export function partDeVie(simulateur, age, debut, sexe = null, cor = false, population = null) {
  if (cor) {
    const deces = ageDeDecesCor(simulateur.mortalite, Math.floor(debut - age + 1e-9));
    return (deces - age) / deces;
  }
  const duree = dureeEsperee(simulateur, age, debut, sexe, population);
  return duree / (age + duree);
}

/**
 * L'âge auquel qui est né à la date `naissance` passe en retraite la même part
 * de sa vie que la référence (`referenceDuCompte`) partie à l'âge de référence,
 * de même sexe et de même population (`partDeVie`). Sous la convention du COR,
 * la part ne dépend que de l'âge et de l'âge de décès D : l'âge est celui de
 * référence fois le rapport des deux D. Sous celle du dépôt, il se cherche par
 * dichotomie, la part baissant quand l'âge monte.
 */
export function ageDePartDeVieConstante(simulateur, naissance, sexe = null, cor = false,
  population = null) {
  const reference = referenceDuCompte(simulateur);
  if (cor) {
    const mortalite = simulateur.mortalite;
    return reference.age * (ageDeDecesCor(mortalite, Math.floor(naissance + 1e-9))
      / ageDeDecesCor(mortalite, Math.floor(reference.naissance + 1e-9)));
  }
  const cible = partDeVie(simulateur, reference.age, reference.annee, sexe, false, population);
  let bas = AGE_EQUILIBRE_MINIMAL;
  let haut = AGE_EQUILIBRE_MINIMAL + 50.0;
  while (haut - bas > 1e-9) {
    const milieu = 0.5 * (bas + haut);
    if (partDeVie(simulateur, milieu, naissance + milieu, sexe, false, population) > cible) {
      bas = milieu;
    } else {
      haut = milieu;
    }
  }
  return 0.5 * (bas + haut);
}
