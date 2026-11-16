"""Le départ anticipé pour carrière longue — article L. 351-1-1 : les règles
du moteur Python qui lisent la table du dispositif.

Méthodes de la table (``donnees/tables_du_droit.CarriereLongue``) jusqu'au
16 novembre 2026 : la table, chargeur des portes et des périodes réputées
cotisées, reste sous ``donnees/`` ; ses règles en sont détachées, telles
quelles, et partiront avec le moteur Python (action 161, étape 3 de
l'inventaire du retrait des règles). Le portage les tient dans
``moteur/js/regimes.js`` (``CarriereLongue``).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..calendrier import DateMois, date_d_effet
from ..donnees.chargement import Fiabilite
from ..noyau import versions
from ..somme import somme_ordonnee

if TYPE_CHECKING:
    from ..carriere import Carriere
    from ..donnees.tables_du_droit import CarriereLongue

#: Premier mois du dernier trimestre civil : qui est né à compter de lui
#: doit un trimestre de moins à la condition d'entrée précoce.
MOIS_DERNIER_TRIMESTRE = 10

#: Ces quatre trimestres se comptent « à la fin de l'année » de
#: l'anniversaire pour les pensions prenant effet à compter du 1er novembre
#: 2012 (décret n° 2012-847, article 14 ; circulaire Cnav n° 2012-60,
#: points 211 et 5). Avant, ils devaient l'être « au titre de l'année au
#: cours de laquelle est survenu » cet anniversaire, dans cette seule année
#: (D. 351-1-3, 2°, LEGIARTI000006736523 et LEGIARTI000023397562 ; D. 16-3
#: du code des pensions, LEGIARTI000023383594 ; circulaire Cnav n° 2003-46,
#: point 113).
QUATRE_TRIMESTRES_A_LA_FIN_DE_L_ANNEE_DEPUIS = DateMois(2012, 11)

#: Les trimestres validés à son régime qui tiennent le non-salarié
#: agricole pour entré avant la borne, « à la fin de l'année » de
#: l'anniversaire et quel que soit son mois de naissance : III de l'article
#: 28 ter du décret n° 55-753 (LEGIARTI000006763597, 2004), puis D. 732-40
#: du code rural, de LEGIARTI000006597425 (2005) à LEGIARTI000053365409
#: (2026).
TRIMESTRES_DE_DEBUT_AGRICOLES = 4

#: Depuis les pensions prenant effet au 1er septembre 2026, les majorations
#: de durée d'assurance pour enfants — maternité, adoption, éducation, congé
#: parental — et les bonifications de la fonction publique sont réputées
#: cotisées pour la carrière longue, dans la limite de DEUX trimestres sur
#: l'ensemble de la carrière : 3° de l'article L. 351-1-1 (article 104 de
#: la loi n° 2025-1403 du 30 décembre 2025), article D. 351-1-2-1 créé par
#: le décret n° 2026-700 du 29 juillet 2026 ; circulaire Cnav 2026-29 du
#: 4 septembre 2026, point 1.2.3.8 et annexe 4. La majoration pour enfant
#: handicapé, que le modèle ne sert pas, en est exclue.
ENFANTS_REPUTES_COTISES_DEPUIS = DateMois(2026, 9)
ENFANTS_REPUTES_COTISES_MAXIMUM = 2

#: LES FONCTIONNAIRES N'ONT LA CARRIÈRE LONGUE QUE DEPUIS 2005, ET CHAQUE
#: PORTE À SA DATE : « 1° A compter du 1er janvier 2008, à cinquante-six
#: ans [...] ; 2° A compter du 1er juillet 2006, à cinquante-huit ans [...] ;
#: 3° A compter du 1er janvier 2005, à cinquante-neuf ans » — L. 25 bis du
#: code des pensions (LEGIARTI000006362733) pour l'État, article 57 de la
#: loi n° 2004-1370 (LEGIARTI000006759076) pour la CNRACL, jusqu'au 30 juin
#: 2011 : l'article 43 de la loi n° 2010-1330, qui récrit l'un et abroge
#: l'autre, « entre en vigueur le 1er juillet 2011 et est applicable aux
#: demandes de pension déposées à compter de cette date » (article 118,
#: III), et D. 16-1, que la base date du 1er janvier 2011, n'en est que
#: l'application ; la table le lit à la date d'effet, faute de celle de la
#: demande. Le régime général les ouvrait toutes trois dès 2004 ; le
#: modèle les ouvrait de même aux fonctionnaires (action 153, étape 2).
#: L. 25 bis vaut aussi pour les ouvriers de l'État : « Les dispositions de
#: l'article L. 25 bis [...] sont applicables aux ouvriers relevant du
#: régime des pensions des ouvriers des établissements industriels de
#: l'Etat » (loi n° 2004-1484, article 119, II), puis l'article 22 ter du
#: décret n° 2004-1056 ; le modèle leur ouvrait les portes du régime général.
REGIMES_FONCTION_PUBLIQUE = frozenset({"fonction_publique_etat", "cnracl", "fspoeie"})
PORTES_FONCTION_PUBLIQUE_DEPUIS = {
    59.0: DateMois(2005, 1), 58.0: DateMois(2006, 7), 56.0: DateMois(2008, 1),
}
#: Et la durée y était fixe : 168 trimestres d'assurance, et 168, 164 ou
#: 160 trimestres cotisés selon la porte, soit cent soixante plus le
#: supplément de la table, jusqu'à la rédaction du 19 décembre 2008
#: (LEGIARTI000019959540), qui la rapporte à « la durée [...] applicable
#: l'année où l'assuré atteint l'âge » de soixante ans. Le modèle lui
#: opposait celle de l'année d'ouverture du droit, de 152 à 158 trimestres
#: avant 2008.
DUREE_FIXE_FONCTION_PUBLIQUE = 160
DUREE_FIXE_FONCTION_PUBLIQUE_AVANT = DateMois(2009, 1)


def portes_opposables(table: CarriereLongue, carriere: Carriere,
                      fonction_publique: bool = False
                      ) -> list[tuple[int, int, float, int, Fiabilite, int | None]] | None:
    """Les portes opposables à cette carrière : celles du texte en vigueur
    à sa date d'effet, et pour chaque porte — borne d'entrée ET supplément
    de trimestres —, parmi les lignes qui couvrent sa génération, celle de
    la plus haute génération : l'adaptation du II l'emporte sur la règle
    générale du I.

    Une ligne ne couvre que les générations que le texte lui nomme, de
    ``generation`` à ``generation_fin`` exclue. Le moteur retenait la
    ligne de la plus haute génération qui ne dépassait pas celle de
    l'assuré, et l'étendait ainsi à toutes les suivantes : sous le décret
    du 2 juillet 2012, la porte des débuts avant dix-sept ans, à
    cinquante-neuf ans et huit mois, que le texte ne donne qu'aux nés de
    1953, s'ouvrait aux nés de 1955, de 1960 ou de 1962, qui n'avaient
    que soixante ans (action 138, étape 21).

    Une borne d'entrée peut ouvrir DEUX portes : avant 2023, qui avait
    débuté avant seize ans partait à cinquante-six ans avec huit
    trimestres cotisés de plus que la durée requise, ou à cinquante-huit
    avec quatre. Retenir une ligne par borne d'entrée en perdait une, au
    hasard de l'ordre du fichier ; c'est le couple (borne, supplément)
    qui identifie une porte.
    """
    if not table._dates:
        return None
    effet = table._annee_decimale(carriere.date_liquidation)
    if effet < table._dates[0]:
        return None
    applicable = table._dates[0]
    for candidate in table._dates:
        if candidate > effet + 1e-9:
            break
        applicable = candidate
    generation = carriere.generation
    retenues: dict[tuple[int, int],
                   tuple[float, tuple[int, int, float, int, Fiabilite, int | None]]] = {}
    for (gen, fin, age_max, trimestres_debut, age_depart, supplement, assurance,
         fiabilite) in table._table[applicable]:
        if gen > generation + 1e-9 or generation > fin - 1e-9:
            continue
        actuelle = retenues.get((age_max, supplement))
        if actuelle is None or gen > actuelle[0]:
            retenues[(age_max, supplement)] = (
                gen, (age_max, trimestres_debut, age_depart, supplement, fiabilite,
                      assurance)
            )
    portes = [porte for _, porte in sorted(retenues.values())]
    if fonction_publique:
        liquidation = carriere.date_liquidation.rang
        portes = [porte for porte in portes
                  if (depuis := PORTES_FONCTION_PUBLIQUE_DEPUIS.get(porte[2]))
                  is None or liquidation >= depuis.rang]
    return portes

def de_la_fonction_publique(codes) -> bool:
    """Les régimes qui opposent la durée sont-ils tous ceux des
    fonctionnaires (:data:`PORTES_FONCTION_PUBLIQUE_DEPUIS`) ?"""
    codes = set(codes)
    return bool(codes) and codes <= REGIMES_FONCTION_PUBLIQUE

def _requis(carriere: Carriere, requis: int, fonction_publique: bool) -> int:
    """La durée que la porte majore : la durée fixe des fonctionnaires
    avant 2009 (:data:`DUREE_FIXE_FONCTION_PUBLIQUE`), ``requis`` sinon."""
    if (fonction_publique and carriere.date_liquidation.rang
            < DUREE_FIXE_FONCTION_PUBLIQUE_AVANT.rang):
        return DUREE_FIXE_FONCTION_PUBLIQUE
    return requis

def _entree_precoce(carriere: Carriere, annee_liquidation: int,
                    age_max: int, trimestres_debut: int,
                    etrangers: dict[int, int] | None = None,
                    agricoles: dict[int, int] | None = None) -> bool:
    """La condition d'entrée précoce est-elle remplie pour cette porte ?

    Elle se lit sur la DURÉE D'ASSURANCE validée avant la fin de l'année
    civile des seize, dix-huit, vingt ou vingt et un ans : « une durée
    d'assurance d'au moins cinq trimestres » (D. 351-1-3, toutes ses
    rédactions depuis 2003), et non la durée cotisée que D. 351-1-1 exige
    ensuite. La Cnav y compte « les périodes de cotisations à l'assurance
    vieillesse obligatoire ou volontaire […] ainsi que les périodes
    assimilées à des périodes d'assurance » (circulaires n° 2003-46,
    point 113, et n° 2026-29, point 1.1.4) : le service national, le
    chômage, la maladie comptent ici, réputés cotisés ou non. Le modèle
    n'y comptait que les trimestres cotisés jusqu'au 20 octobre 2026, et
    fermait la porte à qui avait fait son service à dix-neuf ans.
    L'article en demande cinq, **ou quatre à qui est né au cours du
    dernier trimestre de l'année civile** : né en novembre, on n'a pu
    travailler que deux mois de l'année de ses seize ans, et le texte en
    tient compte. Le modèle retenait cinq pour tout le monde tant qu'il ne
    connaissait que l'année de naissance ; il lit le mois depuis. Ces
    quatre-là, le décret n° 2012-847 les compte à la fin de l'année de
    l'anniversaire ; avant novembre 2012, ils devaient tenir dans cette
    année même (:data:`QUATRE_TRIMESTRES_A_LA_FIN_DE_L_ANNEE_DEPUIS`), et
    le modèle ouvrait la porte à qui les avait répartis sur deux années.

    ``etrangers`` sont les trimestres qu'un accord fait compter hors de
    France, année par année : ils comptent ici comme en France (fiche
    ``totalisation_des_periodes_etrangeres``).

    **Le non-salarié agricole l'est aussi avec quatre trimestres validés à
    son régime** à la fin de la même année, quel que soit son mois de
    naissance : sont considérés comme ayant débuté avant la borne « les
    assurés justifiant soit des conditions définies à l'article D. 351-1-3
    du code de la sécurité sociale, soit ayant validé au titre de
    l'assurance vieillesse des personnes non salariées des professions
    agricoles quatre trimestres à la fin de l'année au cours de laquelle
    est survenu » l'anniversaire (:data:`TRIMESTRES_DE_DEBUT_AGRICOLES`),
    « par dérogation à l'article D. 351-1-3 » dans la rédaction de 2026 ;
    la MSA : « au moins quatre trimestres si vous étiez non-salarié
    agricole » (guide réf. 11342, janvier 2020). Son régime valide l'année
    entière à qui est présent au 1er janvier, et rien à qui entre après :
    cinq trimestres lui demanderaient une année de plus. Le modèle lui en
    demandait cinq jusqu'au 15 novembre 2026. ``agricoles`` sont ces
    trimestres, année par année ; sans eux, la voie n'est pas lue.
    """
    par_annee: dict[int, int] = {}
    for ligne in carriere.lignes:
        # Cotisée ou assimilée, toute ligne qui valide des trimestres :
        # l'année sans activité n'en valide aucun.
        if (ligne.trimestres_valides > 0
                and ligne.annee <= carriere.annee_naissance + age_max
                and ligne.annee < annee_liquidation):
            par_annee[ligne.annee] = (par_annee.get(ligne.annee, 0)
                                      + ligne.trimestres_valides)
    for annee, trimestres in (etrangers or {}).items():
        if annee <= carriere.annee_naissance + age_max and annee < annee_liquidation:
            par_annee[annee] = par_annee.get(annee, 0) + trimestres
    acquis = somme_ordonnee(min(4, trimestres) for trimestres in par_annee.values())
    if acquis >= trimestres_debut:
        return True
    au_regime_agricole = somme_ordonnee(
        min(4, trimestres) for annee, trimestres in (agricoles or {}).items()
        if annee <= carriere.annee_naissance + age_max and annee < annee_liquidation)
    if au_regime_agricole >= TRIMESTRES_DE_DEBUT_AGRICOLES:
        return True
    if carriere.mois_naissance < MOIS_DERNIER_TRIMESTRE:
        return False
    if (carriere.date_liquidation.rang
            < QUATRE_TRIMESTRES_A_LA_FIN_DE_L_ANNEE_DEPUIS.rang):
        # Avant novembre 2012, dans l'année de l'anniversaire seule.
        acquis = min(4, par_annee.get(carriere.annee_naissance + age_max, 0))
    return acquis >= trimestres_debut - 1

def cotises_reputes(table: CarriereLongue, carriere: Carriere, trimestres_cotises: int,
                    trimestres_enfants: int) -> int:
    """La durée cotisée que le dispositif oppose, périodes réputées comprises.

    Les trimestres réellement cotisés, plus deux listes fermées que le droit
    RÉPUTE cotisées. L'article D. 351-1-2 porte la première — service
    national, incapacité temporaire, chômage indemnisé, maternité,
    invalidité, assurance vieillesse des parents au foyer —, chacune sous sa
    propre limite, comptée sur toute la carrière, et selon sa rédaction à la
    date d'effet ; c'est :func:`_reputes_assimiles` qui la tient. Et
    l'article D. 351-1-2-1 porte la seconde, pour les pensions prenant effet
    depuis le 1er septembre 2026 : jusqu'à deux trimestres de la majoration
    pour enfants.

    Le modèle ne comptait que les trimestres réellement cotisés, ce qui
    rendait la condition plus dure qu'elle ne l'est et déclarait non
    ouvertes des carrières hachées que le droit ouvre.
    """
    cotises = trimestres_cotises + _reputes_assimiles(table, carriere)
    if trimestres_enfants <= 0 or carriere.age_liquidation is None:
        return cotises
    if carriere.date_liquidation.rang < ENFANTS_REPUTES_COTISES_DEPUIS.rang:
        return cotises
    return cotises + min(
        ENFANTS_REPUTES_COTISES_MAXIMUM, trimestres_enfants
    )

def _reputes_assimiles(table: CarriereLongue, carriere: Carriere) -> int:
    """Ce que les périodes assimilées ajoutent à la durée cotisée.

    La rédaction de l'article D. 351-1-2 en vigueur à la date d'effet dit
    quelles natures il répute cotisées, et sous quelles limites (fiche
    :attr:`~retraite_notionnelle.donnees.tables_du_droit.CarriereLongue.FICHE_DES_REPUTES`) : rien avant 2004 ; le service national et
    l'incapacité temporaire jusqu'en octobre 2012 ; le chômage depuis
    novembre 2012, l'invalidité depuis avril 2014, l'AVPF depuis septembre
    2023. Le modèle lisait la rédaction de 2026 à toute date, et comptait à
    un départ de 2009 un chômage que celle de 2003 ne réputait pas cotisé.

    Chaque limite vaut pour toute la carrière, et deux natures qui la
    partagent la partagent : maladie et accident du travail tiennent
    toujours ensemble, parce que l'article vise l'incapacité temporaire et
    non l'une ou l'autre, et la maternité les rejoignait jusqu'en mars
    2014. Une période dont la nature est dans plusieurs limites les
    consomme toutes ; une limite sans plafond — la maternité depuis avril
    2014 — n'en consomme aucun. Les limites se consomment dans l'ordre de
    la carrière, et le total n'en dépend pas : celles d'une rédaction sont
    emboîtées ou disjointes.

    Le plafond annuel de quatre trimestres que l'article pose par ailleurs
    est tenu d'avance : une année ne porte ici qu'un statut, et
    :meth:`~retraite_notionnelle.carriere.Carriere.trimestres_retenus` n'en rend jamais plus de quatre.
    """
    annee_liquidation = carriere.annee_liquidation
    version = (None if table._reputes is None else versions.applicable(
        table._reputes, {"liquidation.date_effet": date_d_effet(carriere)}))
    if version is None:
        return 0
    limites = version["parametres"]["limites"]
    restants = [limite["trimestres"] for limite in limites]
    reputes = 0
    for ligne in carriere.lignes:
        if ligne.cotise or not ligne.reputes_cotises_nature:
            continue
        if ligne.annee > annee_liquidation:
            continue
        siennes = [rang for rang, limite in enumerate(limites)
                   if ligne.reputes_cotises_nature in limite["natures"]]
        if not siennes:
            continue
        pris = min([carriere.trimestres_retenus(ligne)]
                   + [restants[rang] for rang in siennes if restants[rang] is not None])
        if pris <= 0:
            continue
        for rang in siennes:
            if restants[rang] is not None:
                restants[rang] -= pris
        reputes += pris
    return reputes

def age_de_depart(table: CarriereLongue, carriere: Carriere, annee_liquidation: int,
                  trimestres_cotises: int, requis: int,
                  etrangers: dict[int, int] | None = None,
                  fonction_publique: bool = False,
                  trimestres_assurance: int | None = None,
                  agricoles: dict[int, int] | None = None
                  ) -> tuple[float, Fiabilite] | None:
    """Âge le plus précoce ouvert par le dispositif, ou ``None``.

    La condition d'entrée précoce se lit sur la durée d'assurance validée
    avant la fin de l'année civile des seize, dix-huit, vingt ou vingt et un
    ans, périodes assimilées comprises (:func:`_entree_precoce`). La
    condition de durée, elle, porte sur les seuls trimestres cotisés et
    réputés tels — c'est ce qui distingue ce dispositif de la durée
    d'assurance qui commande la décote. ``trimestres_cotises`` est la durée que
    :func:`cotises_reputes` a déjà complétée, ``etrangers`` les trimestres
    cotisés hors de France, année par année, ``agricoles`` ceux que valide
    le régime des non-salariés agricoles (:func:`_entree_precoce`).

    **Et jusqu'en octobre 2012, la durée d'assurance aussi** : les
    rédactions de 2003 et de 2010 n'ouvrent le dispositif qu'aux assurés
    « qui justifient, dans le régime général et, le cas échéant, dans un
    ou plusieurs autres régimes obligatoires, d'une durée minimale
    d'assurance ou de périodes reconnues équivalentes au moins égale à la
    limite [...] majorée de huit trimestres » (LEGIARTI000006736521,
    LEGIARTI000023397567 ; L. 25 bis du code des pensions et D. 16-1 de
    même) ; la Cnav y compte « tous les trimestres retenus pour déterminer
    le taux de la pension » (circulaire n° 2003-46, point 111). Chaque
    ligne de la table en dit les huit trimestres. ``trimestres_assurance``
    est cette durée, tous régimes, enfants et périodes étrangères
    comprises ; sans elle, la condition n'est pas lue. Le moteur ne lisait
    que la durée cotisée, et ouvrait à cinquante-neuf ans, en 2009, la
    porte du né en 1950 qui n'avait pas ses 170 trimestres d'assurance
    (action 138, étape 21).
    """
    portes = portes_opposables(table, carriere, fonction_publique)
    if portes is None:
        return None
    requis = _requis(carriere, requis, fonction_publique)
    ouvertures = []
    for age_max, trimestres_debut, age_depart, supplement, fiabilite, assurance in portes:
        if not _entree_precoce(
                carriere, annee_liquidation, age_max, trimestres_debut, etrangers,
                agricoles):
            continue
        if trimestres_cotises < requis + supplement:
            continue
        if (assurance is not None and trimestres_assurance is not None
                and trimestres_assurance < requis + assurance):
            continue
        ouvertures.append((age_depart, fiabilite))
    return min(ouvertures) if ouvertures else None

def age_propose(table: CarriereLongue, carriere: Carriere, annee_liquidation: int,
                trimestres_cotises: int, requis: int,
                age_liquidation: float,
                etrangers: dict[int, int] | None = None,
                fonction_publique: bool = False,
                trimestres_assurance: int | None = None,
                agricoles: dict[int, int] | None = None) -> float | None:
    """Âge le plus précoce que le dispositif ouvrirait à qui continue de
    cotiser jusqu'à son départ, ou ``None``.

    :func:`age_de_depart` répond à une liquidation DATÉE : le droit
    ouvre-t-il ce départ-là ? Ici la question est celle qui date un cas
    type — à quel âge partir ? — et elle se pose avant que la carrière ne
    soit arrêtée. La condition d'entrée précoce se lit telle quelle, elle
    ne dépend que du début de la carrière. La condition de durée, elle, se
    projette : il manque ``requis + supplément − cotisés`` trimestres, et
    une année de cotisation en rend quatre, la soustraction étant signée.
    La durée d'assurance que les rédactions d'avant novembre 2012 exigent
    aussi se projette de même (:func:`age_de_depart`). Chaque porte ouvre
    donc au plus tardif de son âge et des âges où ses durées sont réunies,
    et la plus précoce l'emporte.
    """
    portes = portes_opposables(table, carriere, fonction_publique)
    if portes is None:
        return None
    requis = _requis(carriere, requis, fonction_publique)
    candidats = []
    for age_max, trimestres_debut, age_depart, supplement, _, assurance in portes:
        if not _entree_precoce(
                carriere, annee_liquidation, age_max, trimestres_debut, etrangers,
                agricoles):
            continue
        atteint = age_liquidation + (requis + supplement - trimestres_cotises) / 4.0
        if assurance is not None and trimestres_assurance is not None:
            atteint = max(atteint, age_liquidation
                          + (requis + assurance - trimestres_assurance) / 4.0)
        candidats.append(max(age_depart, atteint))
    return min(candidats) if candidats else None
