"""L'impôt sur le revenu d'un foyer, de son barème à son montant, chaque année.

Le dépôt ne calculait aucun impôt sur le revenu : le site affiche un net
« avant impôt sur le revenu », les indicateurs de cycle de vie s'arrêtent aux
prélèvements sociaux, la page Coût n'a pas d'effet retour par l'impôt (action
138, étape 5). Ce module calcule l'impôt d'un FOYER pour les revenus d'une
année, de 1960 à la dernière loi de finances lue, et au-delà sur un barème
projeté (:mod:`~retraite_notionnelle.donnees.impot_revenu`). Il n'est branché
nulle part : les indicateurs, le site et la page Coût le prendront plus tard.

LE FOYER. Une personne seule — célibataire, divorcée ou veuve — ou un couple
marié ou pacsé, imposé en commun ; des enfants à charge ou non ; des salaires
et des pensions imposables, c'est-à-dire déjà nets de la CSG déductible de
leur année, que calculera la session de la CSG : ce module part du net
imposable. Chaque déclarant dit son âge au 31 décembre de l'année des revenus,
pour l'abattement des personnes âgées, et s'il est invalide.

CE QU'IL REND. L'impôt, et chacune des étapes qui y mènent, et le revenu
fiscal de référence (CGI, art. 1417, IV), qui servira à la CSG des pensions :
pour un foyer qui n'a que des salaires et des pensions, c'est le revenu net
imposable, abattement des personnes âgées déduit.

LES ÉTAPES, dans l'ordre de l'article 193 du code et de ses rédactions
successives :

1. les revenus nets : les salaires, moins 10 % de frais professionnels (CGI,
   art. 83, 3°), bornés par personne ; les pensions, moins 10 % (art. 158, 5,
   a), au moins un minimum par pensionné, au plus un maximum par foyer ;
   jusqu'aux revenus de 2005, 80 % seulement de leur somme, l'abattement de
   20 % s'appréciant pour chaque membre du foyer jusqu'à sa limite (DB 5 F
   3122) ;
2. le revenu net global, puis l'abattement des personnes de plus de 65 ans ou
   invalides (art. 157 bis), le revenu net imposable, arrondi ;
3. le nombre de parts (art. 194 et 195) : un, deux pour un couple ou un veuf
   ayant un enfant à charge, une demi-part par enfant, une part entière par
   enfant à partir du troisième (selon les années :
   ``parts_par_rang_d_enfant``), une demi-part au parent qui vit seul avec ses
   enfants (case T), une demi-part par déclarant invalide ;
4. l'impôt brut du barème, par part, multiplié par les parts ; depuis 1981, le
   plafonnement des effets du quotient familial, et les réductions
   complémentaires de l'invalide (depuis 1998) et du veuf (depuis 2012) ;
5. la décote, dont la règle a changé six fois (:func:`decote`) ; la réduction
   sous condition de revenus de 2016 à 2019 ; les majorations et minorations
   exceptionnelles des années 1960 à 1992 ; la réduction exceptionnelle des
   revenus de 2013 ;
6. le seuil de mise en recouvrement, et la prime pour l'emploi de 2000 à 2015,
   un crédit d'impôt restitué au-delà de l'impôt.

LES MONNAIES ET LES ARRONDIS. L'impôt d'une année en francs se calcule en
francs : ``unite="euro"`` (le défaut) prend et rend des euros, convertis au
taux légal ; ``unite="monnaie"`` prend et rend la monnaie de l'année. Les
arrondis suivent le code : le revenu imposable à la dizaine de francs
inférieure jusqu'aux revenus de 1997 (art. 193), au franc, puis à l'euro, le
plus proche ensuite, ainsi que chaque élément qui y concourt ; l'impôt au
franc le plus proche depuis 1979, à la dizaine de centimes avant (art. 1657,
1), puis à l'euro le plus proche.

CE QU'IL NE FAIT PAS, et que :data:`HORS_CHAMP` énumère : les revenus autres
que les salaires et les pensions, les charges déductibles, les réductions et
crédits d'impôt autres que la prime pour l'emploi et la réduction de 2013,
les demi-parts des anciens combattants et de qui vit seul après avoir élevé
un enfant (case L), les enfants en résidence alternée ou majeurs rattachés,
les départements d'outre-mer, la contribution exceptionnelle sur les hauts
revenus, le travail à temps partiel de la prime pour l'emploi (le foyer
travaille à temps plein, toute l'année).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .donnees.chargement import Fiabilite
from .donnees.impot_revenu import FRANC, BaremesImpotRevenu, ParametresImpot
from .somme import somme_ordonnee

#: Ce que le module ne calcule pas : voir l'en-tête.
HORS_CHAMP = (
    "revenus autres que les salaires et les pensions",
    "charges déductibles et pensions alimentaires",
    "réductions et crédits d'impôt autres que la prime pour l'emploi et la réduction de 2013",
    "demi-parts des anciens combattants et de qui vit seul après avoir élevé un enfant (case L)",
    "enfants en résidence alternée ou majeurs rattachés",
    "abattement des départements d'outre-mer",
    "contribution exceptionnelle sur les hauts revenus",
    "temps partiel et activité sur une partie de l'année, pour la prime pour l'emploi",
)

#: L'âge, atteint au 31 décembre de l'année des revenus, qui ouvre
#: l'abattement des personnes âgées : « âgé de plus de soixante-cinq ans au
#: 31 décembre de l'année d'imposition » (art. 157 bis), que l'administration
#: entend comme né avant le 1er janvier de l'année des revenus moins 64
#: (brochure pratique 2025 : « né avant le 1.1.1960 » pour les revenus 2024).
AGE_ABATTEMENT = 65

#: « Jusqu'à l'imposition des revenus 1978, cette part supplémentaire n'est
#: appliquée qu'aux enfants majeurs invalides à charge » (IPP, note de la
#: table du quotient familial) : le mineur invalide l'a depuis 1979.
PREMIERE_ANNEE_ENFANT_INVALIDE = 1979

#: La première année de revenus dont le barème plafonne l'avantage du
#: quotient familial : la loi de finances pour 1982 (art. 197, VII,
#: LEGIARTI000006308325, « Ce plafond était de 7.500 F pour l'imposition des
#: revenus de 1981 »).
PREMIERE_ANNEE_PLAFONNEMENT = 1981


@dataclass(frozen=True)
class Declarant:
    """Un déclarant du foyer, ses revenus imposables de l'année et sa situation."""

    #: Salaires imposables : le brut moins les cotisations et la CSG
    #: déductible de l'année.
    salaires: float = 0.0
    #: Pensions et retraites imposables, nettes de la CSG déductible.
    pensions: float = 0.0
    #: Âge atteint au 31 décembre de l'année des revenus.
    age: int | None = None
    invalide: bool = False


@dataclass(frozen=True)
class Foyer:
    """Un foyer fiscal : un déclarant, ou deux imposés en commun."""

    declarants: tuple[Declarant, ...]
    #: Enfants à charge, mineurs, à charge exclusive ou principale.
    enfants: int = 0
    #: Ceux d'entre eux qui sont titulaires de la carte d'invalidité : une
    #: demi-part de plus chacun (art. 195, 2), depuis les revenus de 1979 pour
    #: un enfant mineur (IPP, note de la table du quotient familial).
    enfants_invalides: int = 0
    #: Une personne seule veuve : le veuf qui a un enfant à charge garde la
    #: part du conjoint (art. 194, I).
    veuf: bool = False
    #: Une personne seule qui vit seule avec ses enfants : la demi-part du
    #: parent isolé (art. 194, II, case T).
    vit_seul: bool = True

    def __post_init__(self):
        if len(self.declarants) not in (1, 2):
            raise ValueError("un foyer a un déclarant, ou deux s'il est un couple")
        if self.veuf and len(self.declarants) == 2:
            raise ValueError("un couple n'est pas veuf")
        if self.enfants < 0 or not 0 <= self.enfants_invalides <= self.enfants:
            raise ValueError("un nombre d'enfants négatif, ou plus d'enfants invalides que d'enfants")

    @property
    def couple(self) -> bool:
        return len(self.declarants) == 2

    @property
    def parts_de_base(self) -> float:
        """Les parts que le plafonnement ne touche pas : une, deux pour un couple."""
        return 2.0 if self.couple else 1.0


@dataclass(frozen=True)
class ImpotDuFoyer:
    """L'impôt d'un foyer pour les revenus d'une année, étape par étape, dans
    l'unité demandée."""

    annee: int
    #: La monnaie du calcul : celle de l'année.
    monnaie: str
    #: L'unité des montants ci-dessous : ``euro`` ou ``monnaie``.
    unite: str
    parts: float
    #: Par déclarant, les salaires et les pensions après leurs abattements de
    #: 10 %, et l'abattement de 20 % qu'ils ont reçu.
    salaires_nets: tuple[float, ...]
    pensions_nettes: tuple[float, ...]
    abattement_vingt_pour_cent: float
    revenu_net_global: float
    abattement_age_invalidite: float
    revenu_net_imposable: float
    revenu_fiscal_de_reference: float
    #: L'impôt du barème avec toutes les parts, puis avec les seules parts de
    #: base, et l'impôt brut retenu : après plafonnement et réductions
    #: complémentaires.
    impot_sans_plafonnement: float
    impot_brut: float
    plafonnement: float
    reduction_complementaire: float
    decote: float
    reduction_sous_condition_de_revenus: float
    minoration_exceptionnelle: float
    majoration_exceptionnelle: float
    reduction_exceptionnelle: float
    #: La cotisation : l'impôt avant les crédits d'impôt.
    impot_avant_credits: float
    prime_pour_l_emploi: float
    #: La cotisation atteint-elle le seuil de mise en recouvrement ?
    mis_en_recouvrement: bool
    #: Ce que le foyer paie ; négatif, ce qui lui est restitué.
    impot: float
    fiabilite: Fiabilite = Fiabilite.HAUTE
    #: Ce que le calcul a laissé de côté ou approché, pour ce foyer et cette année.
    remarques: tuple[str, ...] = field(default_factory=tuple)


# -- les arrondis ------------------------------------------------------------


def _au_plus_proche(valeur: float, pas: float = 1.0) -> float:
    """L'arrondi du code : la fraction égale à la moitié comptée pour un."""
    return math.floor(round(valeur / pas, 6) + 0.5) * pas


def _arrondir_element(annee: int, valeur: float) -> float:
    """Un abattement ou un revenu net : au franc, puis à l'euro le plus proche,
    depuis les revenus de 1998 (art. 193, LEGIARTI000006308269) ; au centime
    avant (art. 1657, 1 : « bases arrondies au centime de franc inférieur »)."""
    if annee >= 1998:
        return _au_plus_proche(valeur)
    return math.floor(round(valeur * 100, 6)) / 100


def _arrondir_revenu_imposable(annee: int, valeur: float) -> float:
    """Le revenu imposable : à la dizaine de francs inférieure jusqu'aux
    revenus de 1997 (art. 193, et sa rédaction de 1950 au millier d'anciens
    francs), au plus proche ensuite."""
    if annee >= 1998:
        return _au_plus_proche(valeur)
    return math.floor(round(valeur / 10, 6)) * 10.0


def _arrondir_impot(annee: int, valeur: float) -> float:
    """Une cotisation, une décote, une réduction : au franc ou à l'euro le plus
    proche depuis les revenus de 1979 (art. 1657, 1, LEGIARTI000006312651) ; à
    la dizaine de centimes avant (sa rédaction de 1950, en anciens francs)."""
    if annee >= 1979:
        return _au_plus_proche(valeur)
    return _au_plus_proche(valeur, 0.1)


# -- les étapes ----------------------------------------------------------------


def impot_du_bareme(parametres: ParametresImpot, revenu: float, parts: float) -> float:
    """L'impôt du barème : celui d'une part, multiplié par les parts, arrondi."""
    quotient = revenu / parts
    impot_par_part = 0.0
    seuils, taux = parametres.seuils, parametres.taux
    for rang, seuil in enumerate(seuils):
        haut = seuils[rang + 1] if rang + 1 < len(seuils) else math.inf
        if quotient > seuil:
            impot_par_part += (min(quotient, haut) - seuil) * taux[rang]
    return _arrondir_impot(parametres.annee, impot_par_part * parts)


def nombre_de_parts(foyer: Foyer, parametres: ParametresImpot) -> float:
    """Le quotient familial du foyer (art. 194 et 195)."""
    qf = parametres["quotient_familial"]
    parts = foyer.parts_de_base
    if foyer.veuf and foyer.enfants:
        parts += qf.get("veuf_avec_enfant", 0.0)
    parts += somme_ordonnee(parametres.parts_d_enfant(rang)
                            for rang in range(1, foyer.enfants + 1))
    if _parent_isole(foyer):
        parts += qf.get("parent_isole", 0.0)
    parts += qf.get("invalide", 0.0) * _invalidites(foyer, parametres.annee)
    return parts


def _invalidites(foyer: Foyer, annee: int) -> int:
    """Les demi-parts d'invalidité : une par déclarant invalide, une par enfant
    invalide depuis les revenus de 1979."""
    enfants = foyer.enfants_invalides if annee >= PREMIERE_ANNEE_ENFANT_INVALIDE else 0
    return _nombre(d.invalide for d in foyer.declarants) + enfants


def _nombre(drapeaux) -> int:
    """Combien de vrais."""
    return len([d for d in drapeaux if d])


def _parent_isole(foyer: Foyer) -> bool:
    return not foyer.couple and not foyer.veuf and foyer.enfants > 0 and foyer.vit_seul


def _revenus_nets(foyer: Foyer, parametres: ParametresImpot, salaires: tuple[float, ...],
                  pensions: tuple[float, ...]) -> tuple[tuple[float, ...], tuple[float, ...], float]:
    """Les salaires et pensions de chaque déclarant après leurs abattements de
    10 %, puis l'abattement de 20 % du foyer (jusqu'aux revenus de 2005)."""
    annee = parametres.annee
    d = parametres["deductions"]
    salaires_nets = []
    for salaire in salaires:
        deduction = d.get("frais_professionnels_taux", 0.0) * salaire
        if "frais_professionnels_minimum" in d:
            deduction = max(deduction, d["frais_professionnels_minimum"])
        if "frais_professionnels_maximum" in d:
            deduction = min(deduction, d["frais_professionnels_maximum"])
        deduction = _arrondir_element(annee, min(deduction, salaire))
        salaires_nets.append(salaire - deduction)
    abattements = []
    for pension in pensions:
        abattement = d.get("pensions_taux", 0.0) * pension
        if "pensions_minimum" in d:
            abattement = max(abattement, d["pensions_minimum"])
        abattements.append(min(abattement, pension))
    total = somme_ordonnee(abattements)
    if "pensions_maximum" in d and total > d["pensions_maximum"]:
        # Le maximum vaut pour le foyer : chaque pensionné en garde sa part.
        abattements = [a * d["pensions_maximum"] / total for a in abattements]
    abattements = [_arrondir_element(annee, a) for a in abattements]
    pensions_nettes = [p - a for p, a in zip(pensions, abattements)]
    vingt = 0.0
    if d.get("vingt_pour_cent_taux"):
        for salaire, pension in zip(salaires_nets, pensions_nettes):
            base = salaire + pension
            limite = d.get("vingt_pour_cent_plafond")
            assiette = base if limite is None else min(base, limite)
            abattement = d["vingt_pour_cent_taux"] * assiette
            if limite is not None and annee in (1973, 1974):
                # « Pour les revenus 1973 et 1974, les salariés avaient
                # également droit à un abattement de 10 % au-delà du plafond »
                # (IPP, note de la table des déductions).
                abattement += 0.10 * max(base - limite, 0.0)
            vingt += _arrondir_element(annee, abattement)
    return tuple(salaires_nets), tuple(pensions_nettes), vingt


def _abattement_age_invalidite(foyer: Foyer, parametres: ParametresImpot,
                               revenu_net_global: float) -> float:
    """L'abattement de l'article 157 bis, par déclarant de plus de 65 ans ou
    invalide, plein ou réduit selon le revenu net global du foyer."""
    a = parametres["abattement_age_invalidite"]
    if not a:
        return 0.0
    ayants_droit = _nombre((d.age is not None and d.age >= AGE_ABATTEMENT) or d.invalide
                            for d in foyer.declarants)
    if revenu_net_global <= a["seuil_plein"]:
        montant = a["abattement_plein"]
    elif revenu_net_global <= a["seuil_reduit"]:
        montant = a["abattement_reduit"]
    else:
        montant = 0.0
    return float(montant * ayants_droit)


def _plafonnement(foyer: Foyer, parametres: ParametresImpot, revenu: float, parts: float,
                  impot_plein: float) -> tuple[float, float, float]:
    """L'impôt après plafonnement des effets du quotient familial (art. 197,
    I, 2) : rend l'impôt retenu, le supplément que le plafonnement ajoute, et
    la réduction complémentaire qui en retranche une part."""
    plafonds = parametres["plafonds_quotient_familial"]
    if parametres.annee < PREMIERE_ANNEE_PLAFONNEMENT or "general" not in plafonds:
        return impot_plein, 0.0, 0.0
    base = foyer.parts_de_base
    if parts <= base:
        return impot_plein, 0.0, 0.0
    demi_parts = round((parts - base) * 2)
    general = plafonds["general"]
    if _parent_isole(foyer):
        # La part du premier enfant du parent isolé : sa demi-part et celle de
        # la case T, plafonnées ensemble (art. 197, I, 2, deuxième phrase).
        premier = plafonds.get("parent_isole_premier_enfant", 2 * general)
        avantage = premier + general * (demi_parts - 2)
    else:
        avantage = general * demi_parts
    impot_de_base = impot_du_bareme(parametres, revenu, base)
    plafonne = impot_de_base - avantage
    if plafonne <= impot_plein:
        return impot_plein, 0.0, 0.0
    supplement = plafonne - impot_plein
    # Les réductions complémentaires, quand le plafonnement s'applique : par
    # demi-part d'invalidité, et pour la part du veuf qui a un enfant à charge.
    complement = (plafonds.get("reduction_complementaire_invalide", 0.0)
                  * _invalidites(foyer, parametres.annee))
    if foyer.veuf and foyer.enfants:
        complement += plafonds.get("reduction_complementaire_veuf", 0.0)
    reduction = min(complement, supplement)
    return plafonne - reduction, supplement, reduction


def decote(foyer: Foyer, parametres: ParametresImpot, impot: float, parts: float) -> float:
    """La décote, selon la règle de l'année.

    - 1961 à 1972, la franchise et la décote de l'IPP : l'impôt qui n'excède
      pas la franchise (``seuil_celibataire``) est effacé, celui qui reste sous
      la limite (``seuil_couple``) réduit de sorte que l'impôt soit continu
      aux deux seuils ; un foyer d'au plus ``nombre_de_parts_limite`` parts a
      les siens. L'IPP ne cite aucun texte : une lecture de ses colonnes.
    - 1973 à 1980 : aucune.
    - 1981 à 1985 : la différence entre un seuil et l'impôt, pour une part ou
      une part et demie seulement (art. 197, VI, LEGIARTI000006308325).
    - 1986 à 1999 : la différence entre le seuil et l'impôt, pour tous (DB 5 B
      321, 2000).
    - depuis 2000 : la différence entre le seuil et une fraction de l'impôt —
      la moitié jusqu'en 2013, la totalité en 2014, les trois quarts de 2015 à
      2019, 45,25 % depuis ; un seuil propre aux couples depuis 2014."""
    d = parametres["decote"]
    annee = parametres.annee
    if not d or impot <= 0:
        return 0.0
    if annee <= 1972:
        franchise, limite = d["seuil_celibataire"], d["seuil_couple"]
        if "nombre_de_parts_limite" in d and parts <= d["nombre_de_parts_limite"]:
            franchise = d["seuil_1_faible_nombre_de_parts"]
            limite = d["seuil_2_faible_nombre_de_parts"]
        if impot <= franchise:
            return impot
        if impot >= limite:
            return 0.0
        apres = (impot - franchise) * limite / (limite - franchise)
        return _arrondir_impot(annee, impot - apres)
    if annee <= 1985:
        seuil = {1.0: d.get("seuil_une_part"), 1.5: d.get("seuil_une_part_et_demie")}.get(parts)
        taux = 1.0
    else:
        seuil = d["seuil_couple"] if foyer.couple and "seuil_couple" in d else d["seuil_celibataire"]
        taux = d.get("taux", 1.0 if annee <= 1999 else 0.5)
    if not seuil:
        return 0.0
    return min(impot, max(_arrondir_impot(annee, seuil - taux * impot), 0.0))


def _reduction_sous_condition(foyer: Foyer, parametres: ParametresImpot, impot: float,
                              rfr: float, parts: float) -> float:
    """La réduction de 20 % des revenus de 2016 à 2019 (art. 197, I, 4, b),
    dégressive entre ses deux seuils de revenu fiscal de référence."""
    r = parametres["reduction_sous_condition_de_revenus"]
    if not r or impot <= 0:
        return 0.0
    multiple = 2.0 if foyer.couple else 1.0
    demi_parts = (parts - foyer.parts_de_base) * 2
    bas = r["seuil_bas"] * multiple + r["majoration_par_demi_part"] * demi_parts
    haut = r["seuil_haut"] * multiple + r["majoration_par_demi_part"] * demi_parts
    if rfr <= bas:
        taux = r["taux"]
    elif rfr < haut:
        taux = r["taux"] * (haut - rfr) / (haut - bas)
    else:
        return 0.0
    return _arrondir_impot(parametres.annee, taux * impot)


def _minoration(parametres: ParametresImpot, impot: float, revenu: float, parts: float) -> float:
    """Les minorations exceptionnelles, selon les notes de l'IPP : de 1966 à
    1972, par paliers de revenu ou d'impôt ; de 1984 à 1992, un taux par
    tranche d'impôt, raccordé entre elles par « la différence entre une somme
    et 14 % de l'impôt » (17 % en 1985)."""
    m = parametres["minorations_exceptionnelles"]
    annee = parametres.annee
    if not m or impot <= 0:
        return 0.0
    if annee <= 1972:
        base = revenu if annee <= 1967 else impot
        s2, s3, s4 = m["seuil_impot_2"], m["seuil_impot_3"], m["seuil_impot_4"]
        haut, bas = m["taux_1"], m.get("taux_5", 0.0)
        if base <= s2:
            taux = haut
        elif base <= s3:
            taux = haut + (bas - haut) * (base - s2) / (s3 - s2)
        elif base <= s4:
            taux = bas
        else:
            taux = 0.0
        return _arrondir_impot(annee, taux * impot)
    s = [m.get(f"seuil_impot_{rang}") for rang in range(1, 6)]
    if impot <= s[1]:
        montant = m["taux_1"] * impot
    elif s[2] is not None and impot <= s[2]:
        montant = m["formule_seuil_2"] - m["taux_formule"] * impot
    elif s[3] is not None and impot <= s[3]:
        montant = m["taux_3"] * impot
    elif s[4] is not None and impot <= s[4]:
        montant = m["formule_seuil_4"] - m["taux_formule"] * impot
    elif s[4] is not None and revenu / parts <= m.get("revenu_par_part_maximum", math.inf):
        montant = m["taux_5"] * impot
    else:
        montant = 0.0
    return _arrondir_impot(annee, max(montant, 0.0))


def _paliers_de_1968(impot: float, pas: float, taux_haut: float) -> float:
    """1968 : +2 % de 6 000 à 7 000 F d'impôt, +4 % de 7 000 à 8 000 F…
    jusqu'à +14 % de 12 000 à 14 000 F, 15 % au-delà ; 1969, la moitié, à
    partir de 7 000 F (IPP, notes des majorations)."""
    if impot > 14000:
        return taux_haut
    palier = math.floor((min(impot, 13999.99) - 6000) / 1000) + 1
    return pas * min(palier, 7)


def _majoration(parametres: ParametresImpot, impot: float, revenu: float) -> float:
    """Les majorations exceptionnelles, selon les notes de l'IPP : le « décime »
    et le « demi-décime » de 1960 à 1965 au-delà d'un revenu ; de 1967 à 1971,
    un taux par tranche d'impôt, appliqué à tout l'impôt ; de 1980 à 1984, un
    taux sur la fraction de l'impôt qui excède un seuil (sur tout l'impôt, par
    tranche, en 1983)."""
    m = parametres["majorations_exceptionnelles"]
    annee = parametres.annee
    if not m or impot <= 0:
        return 0.0
    if "seuil_revenu" in m:
        taux = m["taux_1"] if revenu > m["seuil_revenu"] else 0.0
        return _arrondir_impot(annee, taux * impot)
    if annee == 1968:
        taux = _paliers_de_1968(impot, 0.02, m["taux_3"]) if impot > m["seuil_1"] else 0.0
        return _arrondir_impot(annee, taux * impot)
    if annee == 1969:
        if impot <= m["seuil_1"]:
            return 0.0
        taux = _paliers_de_1968(impot, 0.02, 2 * m["taux_3"]) / 2 if impot <= 14000 else m["taux_3"]
        return _arrondir_impot(annee, taux * impot)
    if annee <= 1971 or annee == 1983:
        taux = 0.0
        for rang in (1, 2, 3):
            if f"seuil_{rang}" in m and impot > m[f"seuil_{rang}"]:
                taux = m[f"taux_{rang}"]
        return _arrondir_impot(annee, taux * impot)
    if annee == 1981 and impot <= 25000:
        # « Pour les revenus 1981, seuls les contribuables dont l'impôt est
        # supérieur à 25 000 FRF sont concernés » (IPP).
        return 0.0
    return _arrondir_impot(annee, m["taux_1"] * max(impot - m["seuil_1"], 0.0))


def _reduction_exceptionnelle(foyer: Foyer, parametres: ParametresImpot, impot: float,
                              rfr: float, parts: float) -> float:
    """La réduction exceptionnelle des revenus de 2013 (loi n° 2014-891, art. 1) :
    350 € pour une personne seule, 700 € pour un couple, sous un seuil de
    revenu fiscal de référence majoré par demi-part, dégressive au-delà."""
    r = parametres["reduction_exceptionnelle"]
    if not r or impot <= 0:
        return 0.0
    multiple = 2.0 if foyer.couple else 1.0
    seuil = r["seuil"] * multiple + r["majoration_par_demi_part"] * (parts - foyer.parts_de_base) * 2
    montant = r["montant"] * multiple
    if rfr <= seuil:
        reduction = montant
    else:
        reduction = max(seuil + montant - rfr, 0.0)
    return _arrondir_impot(parametres.annee, min(reduction, impot))


def prime_pour_l_emploi(foyer: Foyer, parametres: ParametresImpot,
                        salaires: tuple[float, ...], rfr: float, parts: float) -> float:
    """La prime pour l'emploi (art. 200 sexies), de 2000 à 2015, pour un foyer
    qui travaille à temps plein toute l'année : par personne active, une part
    croissante de son revenu d'activité, puis décroissante ; les majorations
    du couple dont un seul travaille et des personnes à charge."""
    p = parametres["prime_pour_l_emploi"]
    if not p:
        return 0.0
    base = p["rfr_couple"] if foyer.couple else p["rfr_personne_seule"]
    if rfr > base + p["rfr_par_demi_part"] * (parts - foyer.parts_de_base) * 2:
        return 0.0
    actifs = [s for s in salaires if s >= p["revenu_minimum"]]
    mono_emploi = foyer.couple and len(actifs) == 1
    prime = 0.0
    forfait_famille = False
    for salaire in actifs:
        if salaire <= p["revenu_taux_plein"]:
            prime_individuelle = p["taux_entree"] * salaire
        elif salaire < p["revenu_maximum"]:
            prime_individuelle = p["taux_sortie"] * (p["revenu_maximum"] - salaire)
        else:
            prime_individuelle = 0.0
        if mono_emploi:
            if salaire <= p["revenu_maximum"]:
                prime_individuelle += p["majoration_mono_emploi"]
            elif salaire <= p["revenu_taux_plein_mono_emploi"]:
                prime_individuelle = p["majoration_mono_emploi"]
                forfait_famille = True
            elif salaire < p["revenu_maximum_mono_emploi"]:
                prime_individuelle = p["taux_sortie_mono_emploi"] * (
                    p["revenu_maximum_mono_emploi"] - salaire)
                forfait_famille = True
            else:
                prime_individuelle = 0.0
        prime += prime_individuelle
    if not actifs:
        return 0.0
    total_actif = somme_ordonnee(actifs)
    if _parent_isole(foyer) and p["revenu_maximum"] < total_actif < p["revenu_maximum_mono_emploi"]:
        forfait_famille = True
    if foyer.enfants and (prime > 0 or forfait_famille):
        premier = (p["majoration_parent_isole"] if _parent_isole(foyer)
                   else p["majoration_par_personne_a_charge"])
        if forfait_famille:
            prime += premier
        else:
            prime += premier + p["majoration_par_personne_a_charge"] * (foyer.enfants - 1)
    if parametres.annee == 2000:
        # Le complément de la loi n° 2001-458 : la prime des revenus de 2000
        # versée deux fois (IPP, note de la prime pour l'emploi).
        prime *= 2
    prime = _arrondir_impot(parametres.annee, prime)
    return prime if prime >= p["montant_minimum"] else 0.0


def _remarques(foyer: Foyer, parametres: ParametresImpot, la_decote: float,
               minoration: float, majoration: float, ppe: float) -> tuple[str, ...]:
    """Ce que le calcul de ce foyer doit à une règle qu'aucun texte lu ne
    porte, ou à une hypothèse."""
    annee = parametres.annee
    remarques = []
    if parametres.projete:
        remarques.append(f"barème projeté ({parametres.indexation}) au-delà des revenus de "
                         f"{parametres.derniere_annee_lue}")
    if la_decote and annee <= 1972:
        remarques.append("franchise et décote des années 1960 : une lecture des colonnes de "
                         "l'IPP, sans texte lu")
    if minoration or majoration:
        remarques.append("minoration ou majoration exceptionnelle : la règle des notes de "
                         "l'IPP, sans texte lu")
    if ppe:
        remarques.append("prime pour l'emploi d'un travail à temps plein toute l'année")
    if annee < PREMIERE_ANNEE_PLAFONNEMENT and any(d.invalide for d in foyer.declarants):
        remarques.append("invalide : les régimes des couples d'avant 1981 ne sont pas repris")
    return tuple(remarques)


# -- le calcul ----------------------------------------------------------------


def _conversion(parametres: ParametresImpot, unite: str) -> float:
    """Ce par quoi multiplier un montant de l'unité demandée pour l'avoir dans
    la monnaie de l'année."""
    if unite not in ("euro", "monnaie"):
        raise ValueError(f"unité inconnue : {unite!r}")
    return FRANC if (unite == "euro" and parametres.monnaie == "FRF") else 1.0


def impot_du_foyer(foyer: Foyer, annee: int, baremes: BaremesImpotRevenu, *,
                   unite: str = "euro", indexation: str = "prix",
                   croissance=None) -> ImpotDuFoyer:
    """L'impôt du ``foyer`` sur ses revenus d'``annee``.

    ``unite="euro"`` : les revenus du foyer et l'impôt rendu sont en euros,
    convertis au taux légal pour une année en francs ; ``unite="monnaie"`` :
    dans la monnaie de l'année. Au-delà de la dernière loi de finances lue,
    ``indexation`` et ``croissance`` projettent le barème
    (:meth:`~retraite_notionnelle.donnees.impot_revenu.BaremesImpotRevenu.parametres`)."""
    parametres = baremes.parametres(annee, indexation, croissance)
    vers = _conversion(parametres, unite)
    salaires = tuple(_au_plus_proche(d.salaires * vers) for d in foyer.declarants)
    pensions = tuple(_au_plus_proche(d.pensions * vers) for d in foyer.declarants)
    salaires_nets, pensions_nettes, vingt = _revenus_nets(foyer, parametres, salaires, pensions)
    revenu_net_global = max(somme_ordonnee(salaires_nets) + somme_ordonnee(pensions_nettes)
                            - vingt, 0.0)
    revenu_net_global = _arrondir_element(annee, revenu_net_global)
    abattement = min(_abattement_age_invalidite(foyer, parametres, revenu_net_global),
                     revenu_net_global)
    revenu = _arrondir_revenu_imposable(annee, revenu_net_global - abattement)
    assiette = {"salaires_nets": salaires_nets, "pensions_nettes": pensions_nettes,
                "abattement_vingt_pour_cent": vingt, "revenu_net_global": revenu_net_global,
                "abattement_age_invalidite": abattement}
    return _liquider(foyer, parametres, revenu, salaires, assiette, unite, vers)


def impot_d_un_revenu_imposable(foyer: Foyer, annee: int, revenu_net_imposable: float,
                                baremes: BaremesImpotRevenu, *, unite: str = "euro",
                                indexation: str = "prix", croissance=None) -> ImpotDuFoyer:
    """L'impôt d'un foyer dont on connaît le revenu net imposable, comme dans
    les exemples de l'administration : les revenus de ses déclarants sont
    ignorés, et la prime pour l'emploi n'est pas calculée."""
    parametres = baremes.parametres(annee, indexation, croissance)
    vers = _conversion(parametres, unite)
    revenu = _arrondir_revenu_imposable(annee, revenu_net_imposable * vers)
    assiette = {"salaires_nets": (), "pensions_nettes": (), "abattement_vingt_pour_cent": 0.0,
                "revenu_net_global": revenu, "abattement_age_invalidite": 0.0}
    return _liquider(foyer, parametres, revenu, (), assiette, unite, vers)


def _liquider(foyer: Foyer, parametres: ParametresImpot, revenu: float,
              salaires: tuple[float, ...], assiette: dict, unite: str,
              vers: float) -> ImpotDuFoyer:
    """Du revenu net imposable à l'impôt : les parts, le barème et son
    plafonnement, la décote et les autres corrections, la prime pour l'emploi,
    le seuil de mise en recouvrement. Les montants sont dans la monnaie de
    l'année ; ``vers`` y convertit l'unité demandée."""
    annee = parametres.annee
    rfr = revenu
    parts = nombre_de_parts(foyer, parametres)
    impot_plein = impot_du_bareme(parametres, revenu, parts)
    impot_brut, supplement, reduction_complementaire = _plafonnement(
        foyer, parametres, revenu, parts, impot_plein)
    la_decote = decote(foyer, parametres, impot_brut, parts)
    impot = impot_brut - la_decote
    reduction_scr = _reduction_sous_condition(foyer, parametres, impot, rfr, parts)
    impot -= reduction_scr
    minoration = _minoration(parametres, impot, revenu, parts)
    impot -= minoration
    majoration = _majoration(parametres, impot, revenu)
    impot += majoration
    reduction_exc = _reduction_exceptionnelle(foyer, parametres, impot, rfr, parts)
    impot = max(impot - reduction_exc, 0.0)

    ppe = prime_pour_l_emploi(foyer, parametres, salaires, rfr, parts) if salaires else 0.0
    recouvrement = parametres["recouvrement"]
    mis_en_recouvrement = impot > 0 and impot >= recouvrement.get("seuil", 0.0)
    net = impot - ppe
    if net >= 0 and (not mis_en_recouvrement
                     or net < recouvrement.get("seuil_apres_credits", 0.0)):
        net = 0.0
    retour = 1.0 / vers
    return ImpotDuFoyer(
        annee=annee, monnaie=parametres.monnaie, unite=unite, parts=parts,
        salaires_nets=tuple(s * retour for s in assiette["salaires_nets"]),
        pensions_nettes=tuple(p * retour for p in assiette["pensions_nettes"]),
        abattement_vingt_pour_cent=assiette["abattement_vingt_pour_cent"] * retour,
        revenu_net_global=assiette["revenu_net_global"] * retour,
        abattement_age_invalidite=assiette["abattement_age_invalidite"] * retour,
        revenu_net_imposable=revenu * retour,
        revenu_fiscal_de_reference=rfr * retour,
        impot_sans_plafonnement=impot_plein * retour,
        impot_brut=impot_brut * retour,
        plafonnement=supplement * retour,
        reduction_complementaire=reduction_complementaire * retour,
        decote=la_decote * retour,
        reduction_sous_condition_de_revenus=reduction_scr * retour,
        minoration_exceptionnelle=minoration * retour,
        majoration_exceptionnelle=majoration * retour,
        reduction_exceptionnelle=reduction_exc * retour,
        impot_avant_credits=impot * retour,
        prime_pour_l_emploi=ppe * retour,
        mis_en_recouvrement=mis_en_recouvrement,
        impot=net * retour,
        fiabilite=parametres.fiabilite,
        remarques=_remarques(foyer, parametres, la_decote, minoration, majoration, ppe),
    )
