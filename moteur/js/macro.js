/**
 * Séries macroéconomiques : prix, salaires, productivité, plafond.
 *
 * Portage de ``src/retraite_notionnelle/donnees/macro.py``. Au-delà de la
 * dernière année observée, les séries sont prolongées par le scénario de
 * projection choisi et non par la dernière valeur connue ; les années projetées
 * portent la fiabilité la plus basse, ce qui se propage jusqu'au résultat.
 */

import { Fiabilite, SerieAnnuelle } from "./serie.js";

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

export class DonneesMacro {
  constructor(paquet, scenarioProjection = null, trajectoireEmploi = null) {
    this.paquet = paquet;
    this.scenarioProjection = scenarioProjection;
    this.trajectoireEmploi = trajectoireEmploi;

    const hypotheses = paquet.hypotheses;
    const nom = scenarioProjection || hypotheses.scenario_par_defaut;
    const scenarios = hypotheses.scenarios || {};
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
        courant = valeur * (1 + croissance) ** ((13 - mois) / 12);
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
   * Trimestres qu'un revenu d'activité valide dans l'année.
   *
   * Quatre au plus, et zéro si le revenu n'atteint pas le seuil du premier :
   * 200 heures de SMIC depuis 1972, 150 depuis 2014 ; de 1946 à 1971, le
   * salaire que R. 351-9 fixe, 18 F puis le trimestre de l'allocation aux
   * vieux travailleurs salariés. Avant 1946, la règle se lit sur la retenue et
   * non sur le salaire, et une année travaillée vaut quatre trimestres.
   */
  trimestresValides(revenu, annee) {
    if (revenu <= 0) {
      return 0;
    }
    let seuil;
    if (annee < this.heures_par_trimestre.premiereAnnee) {
      // Le seuil d'avant 1972 : le modèle validait quatre trimestres à toute
      // année travaillée, R. 351-9 en fixe un depuis 1946 (action 138, étape 6).
      const anciens = this.salaire_validant_avant_1972;
      if (annee < anciens.premiereAnnee) {
        return 4;
      }
      seuil = anciens.valeur(annee);
    } else {
      seuil = this.heures_par_trimestre.valeur(annee) * this.smic_horaire.valeur(annee);
    }
    if (seuil <= 0) {
      return 4;
    }
    // Un revenu qui tombe pile sur le seuil le valide : 450 SMIC horaires font
    // trois seuils, mais 450 × 11,88 / (150 × 11,88) vaut 2,999… en virgule
    // flottante, et l'arrondi rendait deux trimestres en 2025.
    return Math.max(0, Math.min(4, Math.floor(revenu / seuil + 1e-9)));
  }

  /**
   * Plafond annuel de la Sécurité sociale, en euros courants.
   *
   * Au-delà de la dernière valeur publiée, le plafond suit la croissance du
   * salaire moyen, conformément à l'article L. 241-3 du code de la sécurité
   * sociale.
   */
  _plafond(serie, hypotheses) {
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
    return new SerieAnnuelle(annees, valeurs, fiabilites, "pass", "escalier");
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
  /**
   * Le traitement indiciaire des fonctionnaires rapporté au salaire moyen, 1
   * l'année de base : la convention du COR (`traitement_indiciaire` de
   * `macro/hypotheses_projection.yaml`), et avant elle le décrochage déjà fait
   * (`passe`), le premier reconduit. Voir donnees/macro.py.
   */
  traitementIndiciaireRelatif(annee) {
    if (this._traitementRelatif === undefined) {
      this._traitementRelatif = this._calculerTraitementRelatif();
    }
    const { base, relatif } = this._traitementRelatif;
    if (relatif.size === 0 || annee === base) {
      return 1.0;
    }
    if (annee < base) {
      const passe = [...relatif.keys()].filter((a) => a < base);
      if (passe.length === 0) {
        return 1.0;
      }
      if (relatif.has(annee)) {
        return relatif.get(annee);
      }
      return annee < Math.min(...passe) ? relatif.get(Math.min(...passe)) : 1.0;
    }
    return relatif.get(Math.min(annee, Math.max(...relatif.keys())));
  }

  /**
   * Les années qu'un fonctionnaire de l'État né en `generation` passe sous un
   * autre statut avant d'entrer dans le régime (`entree_fonction_publique` de
   * `macro/hypotheses_projection.yaml`, action 147, étape 11) : en ligne
   * droite entre les points du fichier, la valeur du bord au-delà, zéro sans
   * fichier. Voir donnees/macro.py.
   */
  delaiEntreeFonctionPublique(generation) {
    const points = (this.paquet.hypotheses.entree_fonction_publique ?? [])
      .map((point) => [Number(point.generation), Number(point.annees)])
      .sort((a, b) => a[0] - b[0]);
    if (points.length === 0) return 0.0;
    if (generation <= points[0][0]) return points[0][1];
    for (let rang = 1; rang < points.length; rang += 1) {
      const [debut, avant] = points[rang - 1];
      const [fin, apres] = points[rang];
      if (generation <= fin) {
        return avant + (apres - avant) * (generation - debut) / (fin - debut);
      }
    }
    return points[points.length - 1][1];
  }

  _calculerTraitementRelatif() {
    const regle = this.paquet.hypotheses.traitement_indiciaire;
    if (!regle) {
      return { base: 0, relatif: new Map() };
    }
    const base = Number(regle.annee_base);
    const { nominal, reel, raccord } = regle;
    const fin = Number(raccord.jusqu_a);
    const relatif = new Map([[base, 1.0]]);
    let indice = 1.0;
    for (let annee = base + 1; annee <= fin; annee += 1) {
      const salaire = 1.0 + this.salaire_moyen.valeur(annee);
      const prix = 1.0 + this.inflation.valeur(annee);
      const borneReelle = (1.0 + Number(reel.taux)) * prix;
      let traitement;
      if (Number(nominal.depuis) <= annee && annee <= Number(nominal.jusqu_a)) {
        traitement = 1.0 + Number(nominal.taux);
      } else if (Number(reel.depuis) <= annee && annee <= Number(reel.jusqu_a)) {
        traitement = borneReelle;
      } else if (Number(raccord.depuis) <= annee) {
        const duree = fin - Number(raccord.depuis) + 1;
        const part = (annee - Number(raccord.depuis) + 1) / duree;
        traitement = borneReelle + (salaire - borneReelle) * part;
      } else {
        traitement = salaire;
      }
      indice *= traitement / salaire;
      relatif.set(annee, indice);
    }
    const passe = regle.passe;
    if (passe) {
      passe.annees.forEach((annee, rang) => {
        if (Number(annee) < base) {
          relatif.set(Number(annee),
            Number(passe.traitement[rang]) / Number(passe.revenu_moyen[rang]));
        }
      });
    }
    return { base, relatif };
  }

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
