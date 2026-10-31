/**
 * Séries macroéconomiques : prix, salaires, productivité, plafond.
 *
 * Portage de ``src/retraite_notionnelle/donnees/macro.py``. Au-delà de la
 * dernière année observée, les séries sont prolongées par le scénario de
 * projection choisi et non par la dernière valeur connue ; les années projetées
 * portent la fiabilité la plus basse, ce qui se propage jusqu'au résultat.
 */

import { Fiabilite, SerieAnnuelle } from "./serie.js";
import { pow } from "./libm.js";

/**
 * Première année où les salaires portés au compte sont revalorisés sur les
 * PRIX et non plus sur les salaires. Avant elle, les arrêtés annuels de
 * revalorisation suivaient l'évolution des salaires ; à partir de 1987 ils
 * suivent celle des prix, ce que la loi du 22 juillet 1993 a ensuite inscrit
 * dans le code en retenant l'indice hors tabac.
 */
export const ANNEE_REVALORISATION_SUR_LES_PRIX = 1987;

/** L'assurance vieillesse des parents au foyer naît le 1er juillet 1972. */
export const ANNEE_CREATION_AVPF = 1972;

/** Heures de SMIC de l'assiette MENSUELLE de l'AVPF (R. 381-3). */
export const HEURES_AVPF_PAR_MOIS = 169;

/**
 * Une année de SMIC à temps complet sur 35 heures, 35 heures pendant 52
 * semaines : ce qui prolonge `smic_annuel.csv` au-delà de la dernière année
 * publiée. Voir le Python.
 */
export const HEURES_ANNUELLES_SMIC = 35 * 52;

/**
 * Les départements d'outre-mer, chacun avec la colonne de son seuil au barème
 * de la Cnav : la Guadeloupe, la Guyane et la Martinique en partagent une, La
 * Réunion a la sienne. Voir le Python.
 */
export const DEPARTEMENTS_D_OUTRE_MER = Object.freeze({
  guadeloupe: "antilles_guyane", guyane: "antilles_guyane",
  martinique: "antilles_guyane", reunion: "reunion",
});

/**
 * Le régime de retraite des salariés de Mayotte, dont la caisse valide les
 * trimestres au salaire minimum en vigueur à Mayotte (décret n° 2003-589,
 * art. 8). Voir le Python.
 */
export const REGIME_DE_MAYOTTE = "cssm_mayotte";

/**
 * Avant 1946, la retenue (R. 351-9, rédactions de 1985 à 2025) : les périodes
 * d'assurance comptent du 1er juillet 1930, six mois cette année-là ; de 1936 à
 * 1945, un trimestre par retenue de 15 anciens francs, 0,15 F, en euros. Voir
 * le Python.
 */
export const DEBUT_DES_ASSURANCES_SOCIALES = 1930;
export const MOIS_ASSURES_EN_1930 = 6;
export const RETENUE_D_UN_TRIMESTRE = 0.15 / 6.55957;

/**
 * Les trimestres qu'un revenu valide au seuil d'un trimestre, quatre au plus.
 * Un revenu qui tombe pile sur le seuil le valide : 450 SMIC horaires font
 * trois seuils, mais 450 × 11,88 / (150 × 11,88) vaut 2,999… en virgule
 * flottante, et l'arrondi rendait deux trimestres en 2025.
 */
function trimestresAuSeuil(revenu, seuil) {
  if (seuil <= 0) {
    return 4;
  }
  return Math.max(0, Math.min(4, Math.floor(revenu / seuil + 1e-9)));
}

export class DonneesMacro {
  constructor(paquet, scenarioProjection = null, trajectoireEmploi = null) {
    this.paquet = paquet;
    this.scenarioProjection = scenarioProjection;
    this.trajectoireEmploi = trajectoireEmploi;

    const hypotheses = paquet.hypotheses;
    const nom = scenarioProjection || hypotheses.scenario_par_defaut;
    // Une variante du COR, ou l'un des jeux de référence d'une autre
    // institution, qui se nomment de même. Voir le Python.
    const scenarios = { ...(hypotheses.jeux_de_reference || {}),
                        ...(hypotheses.scenarios || {}) };
    if (!(nom in scenarios)) {
      throw new Error(
        `scénario de projection inconnu : ${nom}. Disponibles : `
        + Object.keys(scenarios).sort().join(", "),
      );
    }
    this.projection = {
      ...scenarios[nom],
      code: nom,
      fin: Number(hypotheses.annee_fin_projection ?? 2100),
    };

    // La trajectoire d'emploi retenue, telle que le fichier la décrit.
    const nomTrajectoire = trajectoireEmploi
      || hypotheses.trajectoire_emploi_par_defaut || "constant";
    const trajectoires = hypotheses.trajectoires_emploi || {};
    if (!(nomTrajectoire in trajectoires)) {
      throw new Error(
        `trajectoire d'emploi inconnue : ${nomTrajectoire}. Disponibles : `
        + Object.keys(trajectoires).sort().join(", "),
      );
    }
    this.trajectoire = { ...(trajectoires[nomTrajectoire] || {}), code: nomTrajectoire };

    const serie = (cle) => SerieAnnuelle.depuisPaquet(cle, paquet.series[cle]);
    const prolonger = (s, cle) => s.prolongee(Number(this.projection[cle]), this.projection.fin);

    /** Ce que le fichier d'hypothèses annonce, à confronter à l'observé. */
    this.anneeDerniereObservationDeclaree =
      Number(hypotheses.annee_derniere_observation);
    /**
     * Croissance annuelle de l'EMPLOI, sur les seules années projetées : nulle
     * partout sous `constant`, lue dans le fichier de la trajectoire sinon, et
     * nulle au-delà de sa dernière année — 2070 pour le COR.
     */
    this.emploi = this._emploi(serie);

    this.inflation = prolonger(serie("inflation"), "inflation");
    this.salaire_moyen = prolonger(serie("salaire_moyen"), "salaire_moyen_nominal");
    /**
     * Le salaire moyen par tête EN NIVEAU, des années que les comptes
     * nationaux publient : d'où se cumulent les croissances
     * (`ancrageSalaireMoyen`, dans carriere.js).
     */
    this.salaire_moyen_niveau = serie("salaire_moyen_niveau");
    this._smicAnnuelPublie = serie("smic_annuel");
    this.masse_salariale = this._prolongeAvecEmploi(
      serie("masse_salariale"), "masse_salariale_nominale");
    this.pib_nominal = this._prolongeAvecEmploi(serie("pib_nominal"), "pib_nominal");
    this.productivite = prolonger(serie("productivite"), "productivite_reelle");
    this.plafond_securite_sociale = this._plafond(serie("pass"), hypotheses);
    this.smic_horaire = this._prolongeParSalaire(serie("smic_horaire"), "smic_horaire",
                                                 paquet.smic_horaire_releve ?? null);
    /** La dernière année du barème du SMIC, et son dernier relèvement. */
    this._smicPublie = [serie("smic_horaire").derniereAnnee, paquet.smic_horaire_releve ?? null];
    this.heures_par_trimestre = serie("heures_par_trimestre");
    /**
     * Le salaire qui valide un trimestre de 1946 à 1971, en euros (R. 351-9) :
     * 18 F jusqu'en 1948, puis le trimestre de l'allocation aux vieux
     * travailleurs salariés au 1er janvier.
     */
    this.salaire_validant_avant_1972 = serie("salaire_validant_avant_1972");
    /**
     * Le même seuil outre-mer, de 1948 à 1995, par colonne du barème de la Cnav
     * (R. 753-21, puis le SMIC du département) ; un paquet qui ne les porte pas
     * encore laisse l'outre-mer au seuil de la métropole.
     */
    this.salaire_validant_outre_mer = Object.fromEntries(
      [...new Set(Object.values(DEPARTEMENTS_D_OUTRE_MER))]
        .filter((colonne) => `salaire_validant_outre_mer_${colonne}` in paquet.series)
        .map((colonne) => [colonne, serie(`salaire_validant_outre_mer_${colonne}`)]));
    /**
     * Avant 1946, la retenue des assurances sociales : leur plafond
     * d'assujettissement de 1930 à 1946, la part de l'assuré dans la double
     * contribution de 1936 à 1945, et les statuts que le routage leur porte. Un
     * paquet qui ne les porte pas encore laisse quatre trimestres à toute année
     * travaillée avant 1946. Voir le Python.
     */
    this.plafond_assujettissement_avant_1947 =
      "plafond_assujettissement_avant_1947" in paquet.series
        ? serie("plafond_assujettissement_avant_1947") : null;
    this.taux_retenue_avant_1946 = "taux_retenue_avant_1946" in paquet.series
      ? serie("taux_retenue_avant_1946") : null;
    this.statutsAssuresSociaux = new Set(Object.entries(paquet.affiliations ?? {})
      .filter(([, profil]) => (profil.periodes ?? [])
        .some((periode) => (periode.regimes ?? []).includes("assurances_sociales")))
      .map(([code]) => code));
    /**
     * Mayotte : le salaire minimum en vigueur à Mayotte au 1er janvier, depuis
     * 2002, prolongé comme le SMIC ; ses heures qui valident un trimestre, 200
     * puis 150 depuis 2017 ; les statuts que le routage porte au régime des
     * salariés de Mayotte. Un paquet qui ne les porte pas encore laisse
     * Mayotte au seuil de la métropole. Voir le Python.
     */
    this.smig_mayotte = "smig_mayotte" in paquet.series
      ? this._prolongeParSalaire(serie("smig_mayotte"), "smig_mayotte") : null;
    this.heures_par_trimestre_mayotte = "heures_par_trimestre_mayotte" in paquet.series
      ? serie("heures_par_trimestre_mayotte") : null;
    /**
     * Le plafond annuel des cotisations de la caisse de Mayotte, depuis 2005,
     * prolongé comme celui de la Sécurité sociale (`plafondDeCotisations`).
     */
    this.plafond_mayotte = "plafond_mayotte" in paquet.series
      ? this._plafond(serie("plafond_mayotte"), hypotheses, "plafond_mayotte") : null;
    this.statutsDeMayotte = new Set(Object.entries(paquet.affiliations ?? {})
      .filter(([, profil]) => (profil.periodes ?? [])
        .some((periode) => (periode.regimes ?? []).includes(REGIME_DE_MAYOTTE)))
      .map(([code]) => code));
    /**
     * L'assiette forfaitaire MENSUELLE de l'AVPF à chaque date du barème de la
     * Cnav, `[[AAAA-MM-JJ, euros], …]`, du 1er juillet 1972 au dernier publié.
     */
    this.assietteAvpf = paquet.assiette_avpf ?? [];
    this._revenusAvpf = new Map();

    this._coefficientsPrix = new Map();
    this._coefficientsSalaires = new Map();
    /**
     * Colonnes de revalorisation publiées par la Cnav, triées par année de date
     * d'effet : `{ annee, mois, coefficients }`, où `coefficients`
     * associe une année de perception à son coefficient.
     */
    const colonnes = (cle) => (paquet[cle] || []).map(
      ([annee, mois, premiere, valeurs]) => ({
        annee,
        mois,
        coefficients: new Map(valeurs.map((v, rang) => [premiere + rang, v])),
        derniere: premiere + valeurs.length - 1,
      }),
    );
    this.revalorisationPorteeAuCompte = colonnes("revalorisation_salaires");
    /**
     * Les colonnes d'AVANT octobre 2017, de l'arrêté du 14 mai 1946 à celle
     * d'octobre 2015 : servies seulement à la date où elles sont en vigueur,
     * jamais par rapport de deux de leurs valeurs. Voir le Python.
     */
    this.revalorisationPorteeAuCompteAnciennes = colonnes("revalorisation_salaires_anciennes");
    /** Toutes les colonnes, anciennes et récentes, triées par date d'effet. */
    this._colonnesEnVigueur = [
      ...this.revalorisationPorteeAuCompteAnciennes, ...this.revalorisationPorteeAuCompte,
    ].sort((a, b) => a.annee - b.annee || a.mois - b.mois);
    /** Dernière année de liquidation que les circulaires publiées couvrent. */
    this.derniereLiquidationRevalorisee = this.revalorisationPorteeAuCompte.length
      ? this.revalorisationPorteeAuCompte[
        this.revalorisationPorteeAuCompte.length - 1].annee
      : null;

    /**
     * Dernière année dont l'indexation ne doit rien à une hypothèse.
     *
     * Déduite des séries elles-mêmes — la dernière année que les trois
     * assiettes portent au-dessus de `estimee` — et non lue dans le fichier
     * d'hypothèses, qui la DÉCLARE de son côté. Les deux doivent coïncider, et
     * un test le vérifie.
     */
    this.derniereAnneeObservee = Math.min(
      ...[this.inflation, this.salaire_moyen, this.masse_salariale].map(
        (serie) => Math.max(
          ...serie.annees.filter(
            (_, rang) => serie.fiabilites[rang] > Fiabilite.ESTIMEE,
          ),
        ),
      ),
    );

  }

  _emploi(serie) {
    const debut = this.anneeDerniereObservationDeclaree + 1;
    const fin = this.projection.fin;
    const annees = [];
    const valeurs = [];
    const fiabilites = [];
    for (let annee = debut; annee <= fin; annee += 1) {
      annees.push(annee);
      valeurs.push(0.0);
      fiabilites.push(Fiabilite.ESTIMEE);
    }
    const fichier = this.trajectoire.fichier;
    if (fichier) {
      const lue = serie(fichier.replace(/\.csv$/, ""));
      lue.annees.forEach((annee, rang) => {
        if (annee >= debut && annee <= fin) {
          valeurs[annee - debut] = lue.valeurs[rang];
          fiabilites[annee - debut] = Math.min(lue.fiabilites[rang], Fiabilite.ESTIMEE);
        }
      });
    }
    return new SerieAnnuelle(annees, valeurs, fiabilites, "croissance_emploi", "escalier");
  }

  /**
   * Prolonge une assiette : le taux du scénario COMPOSÉ avec l'emploi,
   * `(1 + taux) × (1 + emploi de l'année) − 1`, année par année. Le taux du
   * fichier d'hypothèses est celui du salaire moyen, à emploi constant ; c'est
   * ici que l'emploi entre, et nulle part ailleurs.
   */
  _prolongeAvecEmploi(serie, cle) {
    const annees = serie.annees.slice();
    const valeurs = serie.valeurs.slice();
    const fiabilites = serie.fiabilites.slice();
    const base = Number(this.projection[cle]);
    const premiereProjetee = this.anneeDerniereObservationDeclaree + 1;
    for (let annee = serie.derniereAnnee + 1; annee <= this.projection.fin; annee += 1) {
      const emploi = annee >= premiereProjetee ? this.emploi.valeur(annee) : 0.0;
      annees.push(annee);
      valeurs.push((1 + base) * (1 + emploi) - 1);
      fiabilites.push(Fiabilite.ESTIMEE);
    }
    return new SerieAnnuelle(annees, valeurs, fiabilites, serie.nom, serie.interpolation);
  }

  /**
   * Prolonge une série de niveau par la croissance du salaire moyen.
   *
   * C'est l'indexation légale du SMIC, à laquelle s'ajoutent des coups de
   * pouce que le modèle ne prétend pas anticiper.
   */
  _prolongeParSalaire(serie, nom, releve = null) {
    const annees = serie.annees.slice();
    const valeurs = serie.valeurs.slice();
    const fiabilites = serie.fiabilites.slice();
    let courant = serie.valeur(serie.derniereAnnee);
    const croissance = Number(this.projection.salaire_moyen_nominal);
    for (let annee = serie.derniereAnnee + 1; annee <= this.projection.fin; annee += 1) {
      if (releve !== null && annee === serie.derniereAnnee + 1) {
        // Un SMIC ne baisse pas : janvier suivant part du dernier relèvement
        // en vigueur, porté au même rythme sur les mois qui restent.
        const [mois, valeur] = releve;
        courant = valeur * pow(1 + croissance, (13 - mois) / 12);
      } else {
        courant *= 1 + croissance;
      }
      annees.push(annee);
      valeurs.push(courant);
      fiabilites.push(Fiabilite.ESTIMEE);
    }
    return new SerieAnnuelle(annees, valeurs, fiabilites, nom, "escalier");
  }

  /**
   * Le salaire de l'année, sur ses mois travaillés, ne dépasse pas le plafond
   * d'assujettissement aux assurances sociales, ou l'année n'en a plus. Un
   * micro-euro de marge : un salaire pile sur le plafond reste assujetti.
   */
  _assujetti(revenu, annee, fraction) {
    const plafond = this.plafond_assujettissement_avant_1947;
    if (plafond === null || annee < plafond.premiereAnnee || annee > plafond.derniereAnnee) {
      return true;
    }
    return revenu <= plafond.valeur(annee) * fraction + 1e-6;
  }

  /**
   * Le salaire de l'année est porté au compte de l'assuré social : ni avant le
   * 1er juillet 1930, ni au-delà du plafond d'assujettissement jusqu'en 1946.
   * Voir le Python.
   */
  salaireAuCompte(revenu, annee, fraction = 1) {
    return annee >= DEBUT_DES_ASSURANCES_SOCIALES && this._assujetti(revenu, annee, fraction);
  }

  /**
   * Les trimestres d'un assuré social avant 1946, que R. 351-9 lit sur la
   * retenue : rien avant le 1er juillet 1930 ; de 1930 à 1935, un par trimestre
   * civil travaillé, deux en 1930 ; de 1936 à 1945, autant que la retenue de
   * l'année paie de fois 15 anciens francs. Voir le Python.
   */
  _trimestresDeLaRetenue(revenu, annee, fraction) {
    if (annee < DEBUT_DES_ASSURANCES_SOCIALES) {
      return 0;
    }
    const taux = this.taux_retenue_avant_1946;
    if (annee < taux.premiereAnnee) {
      if (annee === DEBUT_DES_ASSURANCES_SOCIALES) {
        return Math.floor(Math.min(MOIS_ASSURES_EN_1930, Math.round(12 * fraction)) / 3);
      }
      return 4;
    }
    return trimestresAuSeuil(taux.valeur(annee) * revenu, RETENUE_D_UN_TRIMESTRE);
  }

  /**
   * Trimestres qu'un revenu d'activité valide dans l'année.
   *
   * Quatre au plus, et zéro si le revenu n'atteint pas le seuil du premier :
   * 200 heures de SMIC depuis 1972, 150 depuis 2014 ; de 1946 à 1971, le
   * salaire que R. 351-9 fixe, 18 F puis le trimestre de l'allocation aux
   * vieux travailleurs salariés. Avant 1946, la règle se lit sur la retenue et
   * non sur le salaire, et une année travaillée vaut quatre trimestres.
   *
   * `outreMer`, le département où l'assuré a travaillé dans l'année (une clef
   * de `DEPARTEMENTS_D_OUTRE_MER`), lui donne son seuil : aucun trimestre avant
   * 1948, puis `salaire_validant_outre_mer` jusqu'en 1995 ; depuis 1996, le
   * SMIC y est celui de la métropole.
   *
   * Avant 1946, la règle se lit sur la retenue des assurances sociales
   * (`_trimestresDeLaRetenue`), et jusqu'en 1946 le salarié payé au-delà de
   * leur plafond d'assujettissement n'en subissait aucune. `fraction`, la part
   * de l'année que la carrière couvre, proratise ce plafond et dit les mois
   * assurés de 1930 ; `assureSocial`, que le statut de l'année relevait des
   * assurances sociales : les autres gardent avant 1946 quatre trimestres par
   * année travaillée.
   *
   * `mayotte`, que le statut de l'année relevait du régime des salariés de
   * Mayotte (`statutsDeMayotte`), lui donne le seuil de sa caisse depuis 2002,
   * la première année du Smig mahorais.
   */
  trimestresValides(revenu, annee, outreMer = "", fraction = 1, assureSocial = true,
                    mayotte = false) {
    if (revenu <= 0) {
      return 0;
    }
    if (this._auSmigMahorais(annee, mayotte)) {
      // Mayotte : le salaire minimum en vigueur à Mayotte, fois 200 heures
      // jusqu'en 2016 et 150 depuis (décret n° 2003-589, art. 8 ; action 177,
      // étape 3).
      return trimestresAuSeuil(revenu, this.seuilDUnTrimestre(annee, "", true));
    }
    const serie = outreMer ? this._salaireValidantDuDepartement(outreMer) : undefined;
    if (serie !== undefined && annee <= serie.derniereAnnee) {
      // L'outre-mer : R. 753-21 et R. 351-9 donnent aux années travaillées
      // outre-mer leur seuil, plus bas de 1949 à 1951 et de 1972 à 1995, et rien
      // n'y comptait avant 1948 (action 138, étape 6).
      return trimestresAuSeuil(revenu, this.seuilDUnTrimestre(annee, outreMer));
    }
    if (annee < this.heures_par_trimestre.premiereAnnee) {
      // Le seuil d'avant 1972 : le modèle validait quatre trimestres à toute
      // année travaillée, R. 351-9 en fixe un depuis 1946 (action 138, étape 6).
      // Avant 1946, la retenue des assurances sociales les fait, et le cadre
      // payé au-delà de leur plafond d'assujettissement n'en subissait aucune.
      if (assureSocial && !this._assujetti(revenu, annee, fraction)) {
        return 0;
      }
      if (annee < this.salaire_validant_avant_1972.premiereAnnee) {
        return assureSocial && this.taux_retenue_avant_1946 !== null
          ? this._trimestresDeLaRetenue(revenu, annee, fraction) : 4;
      }
    }
    return trimestresAuSeuil(revenu, this.seuilDUnTrimestre(annee));
  }

  /**
   * Le revenu d'activité qui valide un trimestre dans l'année, en euros
   * courants : 200 heures de SMIC depuis 1972, 150 depuis 2014 ; de 1946 à
   * 1971, le salaire que R. 351-9 fixe. `outreMer` lui donne celui du
   * département, infini avant 1948 ; `null` avant 1946, où la retenue des
   * assurances sociales les fait. C'est le seuil qu'un relevé de carrière se
   * lit contre (action 138, étape 10). `mayotte` lui donne celui de la caisse
   * de Mayotte depuis 2002 : 200 heures du Smig mahorais du 1er janvier
   * jusqu'en 2016, 150 depuis. Voir `seuil_d_un_trimestre` du Python.
   */
  seuilDUnTrimestre(annee, outreMer = "", mayotte = false) {
    if (this._auSmigMahorais(annee, mayotte)) {
      return this.heures_par_trimestre_mayotte.valeur(annee) * this.smig_mayotte.valeur(annee);
    }
    const serie = outreMer ? this._salaireValidantDuDepartement(outreMer) : undefined;
    if (serie !== undefined && annee < serie.premiereAnnee) {
      return Infinity;
    }
    if (serie !== undefined && annee <= serie.derniereAnnee) {
      return serie.valeur(annee);
    }
    if (annee >= this.heures_par_trimestre.premiereAnnee) {
      return this.heures_par_trimestre.valeur(annee) * this.smic_horaire.valeur(annee);
    }
    const anciens = this.salaire_validant_avant_1972;
    return annee >= anciens.premiereAnnee ? anciens.valeur(annee) : null;
  }

  /**
   * L'année d'un salarié de Mayotte se valide au Smig mahorais : depuis la
   * première année de sa série, quand le paquet la porte.
   */
  _auSmigMahorais(annee, mayotte) {
    return mayotte && this.smig_mayotte !== null && this.heures_par_trimestre_mayotte !== null
      && annee >= this.smig_mayotte.premiereAnnee;
  }

  /** La série de `salaire_validant_outre_mer` du département `outreMer`. */
  _salaireValidantDuDepartement(outreMer) {
    if (!Object.hasOwn(DEPARTEMENTS_D_OUTRE_MER, outreMer)) {
      throw new Error(`département d'outre-mer inconnu : ${outreMer}`);
    }
    return this.salaire_validant_outre_mer[DEPARTEMENTS_D_OUTRE_MER[outreMer]];
  }

  /**
   * Plafond annuel de la Sécurité sociale, en euros courants.
   *
   * Au-delà de la dernière valeur publiée, le plafond suit la croissance du
   * salaire moyen, conformément à l'article L. 241-3 du code de la sécurité
   * sociale.
   */
  _plafond(serie, hypotheses, nom = "pass") {
    if (hypotheses.plafond_suit_salaire_moyen === false) {
      return serie;
    }
    const annees = serie.annees.slice();
    const valeurs = serie.valeurs.slice();
    const fiabilites = serie.fiabilites.slice();
    let courant = serie.valeur(serie.derniereAnnee);
    const croissance = Number(this.projection.salaire_moyen_nominal);
    for (let annee = serie.derniereAnnee + 1; annee <= this.projection.fin; annee += 1) {
      courant *= 1 + croissance;
      annees.push(annee);
      valeurs.push(courant);
      fiabilites.push(Fiabilite.ESTIMEE);
    }
    return new SerieAnnuelle(annees, valeurs, fiabilites, nom, "escalier");
  }

  /**
   * Le plafond annuel des cotisations de l'année : celui de la Sécurité
   * sociale, ou, au régime des salariés de Mayotte (`mayotte`), celui de sa
   * caisse depuis 2005. Voir `plafond_de_cotisations` du Python.
   */
  plafondDeCotisations(annee, mayotte = false) {
    if (mayotte && this.plafond_mayotte !== null && annee >= this.plafond_mayotte.premiereAnnee) {
      return this.plafond_mayotte.valeur(annee);
    }
    return this.plafond_securite_sociale.valeur(annee);
  }

  // -- grandeurs dérivées ----------------------------------------------------

  /** Productivité réelle ramenée en nominal : (1+ρ)(1+π) - 1. */
  productiviteNominale(annee) {
    return (1 + this.productivite.valeur(annee)) * (1 + this.inflation.valeur(annee)) - 1;
  }

  /**
   * Coefficient de passage d'euros de ``depart`` en euros de ``arrivee``.
   *
   * Sert à exprimer tous les résultats dans une unité comparable — sans quoi
   * confronter une pension liquidée en 1975 à une pension de 2026 n'a aucun
   * sens.
   */
  coefficientPrix(depart, arrivee) {
    if (arrivee === depart) {
      return 1.0;
    }
    if (arrivee > depart) {
      const cle = `${depart}|${arrivee}`;
      const memorise = this._coefficientsPrix.get(cle);
      if (memorise !== undefined) {
        return memorise;
      }
      let coefficient = 1.0;
      for (let annee = depart + 1; annee <= arrivee; annee += 1) {
        coefficient *= 1 + this.inflation.valeur(annee);
      }
      this._coefficientsPrix.set(cle, coefficient);
      return coefficient;
    }
    return 1.0 / this.coefficientPrix(arrivee, depart);
  }

  /**
   * Coefficient de passage par le salaire moyen par tête, d'une année à
   * l'autre : le produit de ses croissances nominales. Prolonge un barème que
   * son texte indexe sur les salaires : la valeur d'achat du point
   * Agirc-Arrco, au-delà du dernier barème publié. Voir donnees/macro.py.
   */

  coefficientSalaireMoyen(depart, arrivee) {
    if (arrivee === depart) {
      return 1.0;
    }
    if (arrivee > depart) {
      let coefficient = 1.0;
      for (let annee = depart + 1; annee <= arrivee; annee += 1) {
        coefficient *= 1 + this.salaire_moyen.valeur(annee);
      }
      return coefficient;
    }
    return 1.0 / this.coefficientSalaireMoyen(arrivee, depart);
  }

  /**
   * Coefficient de passage par le SMIC, d'une année à l'autre.
   *
   * Plusieurs montants du droit positif ne suivent ni les prix ni les salaires
   * mais le SALAIRE MINIMUM DE CROISSANCE : le plafond d'écrêtement du minimum
   * contributif depuis février 2014, les deux montants du minimum lui-même
   * depuis la réforme du 14 avril 2023.
   */
  coefficientSmic(depart, arrivee) {
    const valeurDepart = this.smic_horaire.valeur(depart);
    return valeurDepart > 0 ? this.smic_horaire.valeur(arrivee) / valeurDepart : 1.0;
  }

  /**
   * Le salaire minimum brut d'une année ENTIÈRE à temps complet, en euros de
   * cette année : publié par l'INSEE de 1951 à la dernière année complète ;
   * au-delà, 1 820 heures du barème horaire, celui de janvier puis, l'année du
   * dernier relèvement connu, celui-ci à compter de son mois ; avant 1951, le
   * rapport de 1951 au salaire moyen. Voir le Python.
   */
  smicAnnuel(annee) {
    const publie = this._smicAnnuelPublie;
    if (annee < publie.premiereAnnee) {
      const premiere = publie.premiereAnnee;
      return publie.valeur(premiere) * this.coefficientSalaireMoyen(premiere, annee);
    }
    if (annee <= publie.derniereAnnee) {
      return publie.valeur(annee);
    }
    const janvier = this.smic_horaire.valeur(annee);
    const [derniere, releve] = this._smicPublie;
    let horaireMoyen = janvier;
    if (annee === derniere && releve !== null) {
      const [mois, valeur] = releve;
      horaireMoyen = (janvier * (mois - 1) + valeur * (13 - mois)) / 12;
    }
    return HEURES_ANNUELLES_SMIC * horaireMoyen;
  }

  /**
   * Le SMIC horaire en vigueur le 1er juillet de cette année : le barème de
   * janvier, ou, la dernière année publiée, le relèvement d'avant juillet qui
   * l'a remplacé. Voir le Python.
   */
  smicHoraireAu1erJuillet(annee) {
    const [derniere, releve] = this._smicPublie;
    if (annee === derniere && releve !== null && releve[0] <= 7) {
      return releve[1];
    }
    return this.smic_horaire.valeur(annee);
  }

  /**
   * Le salaire qu'une année ENTIÈRE d'assurance vieillesse des parents au foyer
   * porte au compte : la somme des assiettes mensuelles de la Cnav sur ses douze
   * mois, rien avant juillet 1972 ; au-delà du barème, 169 heures par mois du
   * SMIC du 1er juillet précédent (R. 381-3). Voir le Python.
   */
  revenuAvpf(annee) {
    const connu = this._revenusAvpf.get(annee);
    if (connu !== undefined) {
      return connu;
    }
    const datees = this.assietteAvpf;
    let total;
    if (datees.length > 0 && annee <= Number(datees[datees.length - 1][0].slice(0, 4))) {
      total = 0.0;
      for (let mois = 1; mois <= 12; mois += 1) {
        const jour = `${String(annee).padStart(4, "0")}-${String(mois).padStart(2, "0")}-01`;
        let rang = 0;
        while (rang < datees.length && datees[rang][0] <= jour) {
          rang += 1;
        }
        if (rang > 0) {
          total += datees[rang - 1][1];
        }
      }
    } else if (annee < ANNEE_CREATION_AVPF) {
      total = 0.0;
    } else {
      total = 12 * HEURES_AVPF_PAR_MOIS * this.smicHoraireAu1erJuillet(annee - 1);
    }
    this._revenusAvpf.set(annee, total);
    return total;
  }

  /**
   * La colonne que la caisse oppose à une liquidation du premier jour de ce
   * mois : la plus récente dont la date d'effet ne lui est pas postérieure, qui
   * vaut jusqu'à la suivante. `null` avant la première, et après l'année de la
   * dernière. Voir le Python.
   */
  colonneDeRevalorisationEnVigueur(annee, mois = 1) {
    const colonnes = this._colonnesEnVigueur;
    let bas = 0;
    let haut = colonnes.length;
    while (bas < haut) {
      const milieu = (bas + haut) >> 1;
      const colonne = colonnes[milieu];
      if (colonne.annee < annee || (colonne.annee === annee && colonne.mois <= mois)) {
        bas = milieu + 1;
      } else {
        haut = milieu;
      }
    }
    const rang = bas - 1;
    if (rang < 0) {
      return null;
    }
    if (rang === colonnes.length - 1 && annee > colonnes[rang].annee) {
      return null;
    }
    return colonnes[rang];
  }

  /**
   * Revalorisation d'un salaire PORTÉ AU COMPTE, telle que l'arrêté la fixe.
   *
   * C'est la grandeur qui commande le salaire annuel moyen : la moyenne porte
   * sur les N MEILLEURES années, et « meilleures » se juge sur des salaires
   * revalorisés — changer les coefficients ne déplace donc pas seulement le
   * niveau de chaque année, cela change lesquelles sont retenues. Le modèle
   * l'approchait par « les salaires jusqu'en 1986, les prix depuis », ce qui
   * SUR-revalorisait les salaires anciens de 12 % sur quarante ans.
   *
   * D'abord la colonne EN VIGUEUR à la date de liquidation, que la caisse
   * oppose sans calcul — un salaire plus récent qu'elle n'a encore rien reçu ;
   * sinon le rapport de deux valeurs de la colonne récente la plus proche
   * (`coefficientRevalorisationParRapport`). Voir le Python.
   */
  coefficientRevalorisationPorteeAuCompte(depart, arrivee, moisArrivee = 1) {
    if (arrivee === depart) {
      return 1.0;
    }
    if (arrivee < depart) {
      return 1.0 / this.coefficientRevalorisationPorteeAuCompte(arrivee, depart);
    }
    const enVigueur = this.colonneDeRevalorisationEnVigueur(arrivee, moisArrivee);
    if (enVigueur !== null) {
      if (enVigueur.coefficients.has(depart)) {
        return enVigueur.coefficients.get(depart);
      }
      if (depart > enVigueur.derniere) {
        return 1.0;
      }
    }
    return this.coefficientRevalorisationParRapport(depart, arrivee, moisArrivee);
  }

  /**
   * La revalorisation par RAPPORT de deux valeurs d'une colonne récente : la
   * colonne de l'année d'arrivée en vigueur à son mois, sinon la PLUS PROCHE —
   * ce qui divise la dérive par dix —, hors de toute colonne l'ancienne
   * approximation, ancrée sur la borne connue quand il y en a une. C'est le
   * taux annuel du mode d'indexation `revalorisation_portee_au_compte`. Voir le
   * Python.
   */
  coefficientRevalorisationParRapport(depart, arrivee, moisArrivee = 1) {
    if (arrivee === depart) {
      return 1.0;
    }
    if (arrivee < depart) {
      return 1.0 / this.coefficientRevalorisationParRapport(arrivee, depart);
    }
    const colonnes = this.revalorisationPorteeAuCompte;
    if (colonnes.length === 0) {
      return this.coefficientRevalorisationSalaires(depart, arrivee);
    }

    // La colonne EN VIGUEUR à la date de liquidation : la plus récente dont la
    // date d'effet ne lui est pas postérieure, dans son année. C'est le mois
    // qui la désigne — un départ du 1er août 2022 relève de la circulaire du
    // 1er juillet, un départ du 1er mars de celle du 1er janvier, et les deux
    // diffèrent de 3,9 %.
    let enVigueur = null;
    for (const colonne of colonnes) {
      if (colonne.annee === arrivee && colonne.mois <= moisArrivee
          && colonne.coefficients.has(depart)) {
        enVigueur = colonne;
      }
    }
    if (enVigueur !== null) {
      return enVigueur.coefficients.get(depart);
    }

    // La colonne la plus proche qui porte les deux années. Une colonne dont la
    // date d'effet est POSTÉRIEURE à la liquidation ne peut pas servir pour
    // l'année de celle-ci : son millésime porte déjà une revalorisation que
    // l'assuré n'a pas connue.
    let meilleure = null;
    for (const colonne of colonnes) {
      if (!colonne.coefficients.has(depart) || !colonne.coefficients.has(arrivee)) {
        continue;
      }
      if (colonne.annee === arrivee && colonne.mois > moisArrivee) {
        continue;
      }
      const distance = Math.abs(colonne.annee - arrivee);
      if (meilleure === null || distance < meilleure.distance) {
        meilleure = { distance, colonne };
      }
    }
    if (meilleure !== null) {
      return meilleure.colonne.coefficients.get(depart)
        / meilleure.colonne.coefficients.get(arrivee);
    }

    // Au-delà de la dernière colonne, on ANCRE sur elle et on n'approche que le
    // bout du chemin. En deçà de la première année publiée, il n'y a rien sur
    // quoi ancrer.
    const derniere = colonnes[colonnes.length - 1];
    if (arrivee > derniere.annee && derniere.coefficients.has(depart)) {
      return derniere.coefficients.get(depart)
        * this.coefficientRevalorisationSalaires(derniere.annee, arrivee);
    }
    return this.coefficientRevalorisationSalaires(depart, arrivee);
  }

  /**
   * Revalorisation d'un salaire porté au compte, de ``depart`` à ``arrivee``.
   *
   * Ce n'est pas l'indice des prix. Les salaires inscrits au compte sont
   * revalorisés par un coefficient fixé chaque année par arrêté, et cet arrêté
   * a suivi les SALAIRES jusqu'en 1986 avant de suivre les prix. Sur les
   * Trente Glorieuses l'écart est massif : appliquer la règle des prix à ces
   * années-là ramenait au compte des salaires très en dessous de ce que le
   * droit y a réellement inscrit.
   *
   * **Cette règle n'est plus qu'un REPLI.** Les coefficients des arrêtés
   * eux-mêmes sont dans le paquet, et
   * `coefficientRevalorisationPorteeAuCompte` les sert là où ils existent.
   * Cette approximation ne vaut plus que hors de leur plage, et pour les
   * régimes qui ne portent aucun salaire à un compte.
   */
  coefficientRevalorisationSalaires(depart, arrivee) {
    if (arrivee === depart) {
      return 1.0;
    }
    if (arrivee < depart) {
      return 1.0 / this.coefficientRevalorisationSalaires(arrivee, depart);
    }
    const cle = `${depart}|${arrivee}`;
    const memorise = this._coefficientsSalaires.get(cle);
    if (memorise !== undefined) {
      return memorise;
    }
    let coefficient = 1.0;
    for (let annee = depart + 1; annee <= arrivee; annee += 1) {
      coefficient *= 1 + (annee >= ANNEE_REVALORISATION_SUR_LES_PRIX
        ? this.inflation.valeur(annee)
        : this.salaire_moyen.valeur(annee));
    }
    this._coefficientsSalaires.set(cle, coefficient);
    return coefficient;
  }

  /** Fiabilité du maillon le plus faible des séries macro sur la plage. */
  fiabiliteSur(debut, fin) {
    return Math.min(
      this.inflation.fiabiliteMinimaleSur(debut, fin),
      this.salaire_moyen.fiabiliteMinimaleSur(debut, fin),
      this.productivite.fiabiliteMinimaleSur(debut, fin),
    );
  }
}
