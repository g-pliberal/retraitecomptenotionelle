"""Le routage des statuts vers leurs régimes, année par année : le chargeur
de ``data/reference/legislation/affiliations.yaml``.

Logé ici depuis ``carriere.py``, tel quel (action 161, étape 3 de
l'inventaire du retrait des règles) : la fabrique du paquet, celle des
témoins, le simulateur de données, la fiche de paie et les contributions
d'équilibre le lisent sans le moteur Python, qui le reprend. La date
d'entrée que le maintien d'une affiliation décide (:meth:`Affiliations.date_entree`)
vient avec lui : elle route comme :meth:`Affiliations.regimes`, et la fiche de
paie et les contributions d'équilibre la lisent.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ..calendrier import MOIS_PAR_AN, DateMois
from .chargement import charger_yaml

if TYPE_CHECKING:
    from ..types_du_pont.carriere import Carriere


def rang_borne(borne: int | str) -> int:
    """Une borne d'entrée du routage, en rang de mois.

    ``2020`` se lit janvier 2020 ; ``"2023-09"`` septembre 2023. Le YAML garde
    les deux écritures parce que la loi ferme un régime « aux agents recrutés à
    compter du 1er septembre 2023 », et non à compter d'une année.
    """
    if isinstance(borne, int):
        return DateMois(borne, 1).rang
    annee, mois = str(borne).split("-")
    return DateMois(int(annee), int(mois)).rang


#: Les familles de statuts, dans l'ordre où le menu du simulateur les range :
#: code du YAML -> libellé du groupe. Sept groupes de deux à seize statuts se
#: parcourent ; soixante-deux à la file ne se parcouraient pas. L'ordre va du
#: plus commun au plus rare, et « hors emploi » ferme la marche.
FAMILLES_STATUT: dict[str, str] = {
    "prive": "Salariés du privé",
    "public": "Fonction publique et militaires",
    "independant": "Indépendants et professions libérales",
    "agricole": "Agriculture",
    "special": "Régimes spéciaux",
    "outre_mer": "Outre-mer",
    "elus": "Élus et assemblées",
    "hors_emploi": "Hors emploi",
}


class Affiliations:
    """Correspondance statut -> régimes, année par année."""

    def __init__(self, racine: Path) -> None:
        contenu = charger_yaml(racine / "reference" / "legislation" / "affiliations.yaml")
        self._profils: dict[str, dict] = contenu.get("affiliations", {})
        if not self._profils:
            raise ValueError("aucun profil d'affiliation chargé")
        for code, profil in self._profils.items():
            if profil.get("famille") not in FAMILLES_STATUT:
                raise ValueError(
                    f"affiliations.yaml / {code} : famille manquante ou inconnue "
                    f"{profil.get('famille')!r} — attendue parmi "
                    f"{sorted(FAMILLES_STATUT)}"
                )
        #: Régimes du catalogue que le fichier déclare volontairement hors
        #: routage, avec leur raison. Le moteur ne s'en sert pas ; la cohérence
        #: entre catalogue et routage, si — cf. `tests/test_donnees.py`.
        self._hors_routage: dict[str, str] = contenu.get(
            "regimes_sans_affiliation", {}
        )
        #: :meth:`maintien`, statut par statut : chaque routage le demande.
        self._maintiens: dict[str, tuple[DateMois, int] | None] = {}

    def __contains__(self, code: str) -> bool:
        return code in self._profils

    @property
    def codes(self) -> tuple[str, ...]:
        return tuple(sorted(self._profils))

    def libelle(self, code: str) -> str:
        return self._profils[code].get("libelle", code)

    def famille(self, code: str) -> str:
        """Le groupe du menu où ce statut se range — une clé de FAMILLES_STATUT."""
        return self._profils[code]["famille"]

    def periodes(self, affiliation: str) -> tuple[dict, ...]:
        """Les tranches temporelles déclarées par ce statut, telles qu'écrites."""
        return tuple(self._profils[affiliation].get("periodes", []))

    def ouverture(self, affiliation: str) -> int:
        """Première année que le statut route — l'année où son régime naît."""
        return min(periode["debut"] for periode in self.periodes(affiliation))

    def fermeture_entrants(self, affiliation: str) -> DateMois | None:
        """Mois depuis lequel le statut est fermé aux nouveaux entrants.

        C'est la clause du grand-père lue depuis le routage lui-même : la plus
        ancienne borne ``entres_avant`` de ses périodes, POUR UN STATUT QUI
        DÉCLARE ``releve_par`` — celui dont le nom même cesse de convenir
        après la date : un jeune d'aujourd'hui ne peut pas se déclarer mineur,
        le régime des mines est fermé aux recrutés depuis septembre 2010, et
        c'est cette date que le formulaire lui oppose. ``None`` pour un statut
        ouvert, et aussi pour un statut dont les régimes changent pour les
        nouveaux entrants sans qu'il cesse d'exister — le libéral non
        réglementé est à la Cipav s'il y était avant 2019, au régime général
        et au RCI sinon, et reste un libéral non réglementé.
        """
        if self.releve_par(affiliation) is None:
            return None
        bornes = [periode["entres_avant"] for periode in self.periodes(affiliation)
                  if periode.get("entres_avant") is not None]
        if not bornes:
            return None
        return DateMois.depuis_rang(min(rang_borne(borne) for borne in bornes))

    def releve_par(self, affiliation: str) -> str | None:
        """Le statut de droit commun dont relève qui entre après la fermeture."""
        return self._profils[affiliation].get("releve_par")

    def maintien(self, affiliation: str) -> tuple[DateMois, int] | None:
        """La borne du grand-père que la loi ne tient qu'à une affiliation
        continue, et le nombre d'années que s'y maintient une affiliation
        suspendue ou rompue avant elle : la période qui porte ``entres_avant``
        et ``maintien``. ``None`` pour un statut qui garde ses anciens sans
        condition — la RATP garde « les anciens agents […] recrutés avant le
        1er septembre 2023 » (décret n° 2008-637, art. 1er, 1°)."""
        if affiliation not in self._maintiens:
            self._maintiens[affiliation] = next(
                ((DateMois.depuis_rang(rang_borne(periode["entres_avant"])),
                  int(periode["maintien"]))
                 for periode in self.periodes(affiliation)
                 if periode.get("maintien") is not None
                 and periode.get("entres_avant") is not None), None)
        return self._maintiens[affiliation]

    def date_entree(self, carriere: Carriere, affiliation: str,
                    annee: int) -> DateMois | None:
        """La date d'entrée qui décide des régimes de ce statut cette année-là.

        Celle de la carrière (:meth:`Carriere.date_entree`), sauf sous un régime
        fermé qui ne garde que ses anciens restés affiliés (:meth:`maintien`) :
        la CRPCEN et les IEG, depuis le 1er septembre 2023, ne servent la
        pension de vieillesse qu'aux recrutés d'avant « qui remplissent, à
        compter de cette date, les conditions d'affiliation » (loi du 12 juillet
        1937, art. 1er, § 2 ; loi n° 2004-803, art. 16, I ; rédactions de la loi
        n° 2023-1250, art. 15, V et VI). L'affiliation se maintient dix ans au
        plus après une suspension ou une rupture antérieure, « quelle qu'en soit
        la cause » ; un mois ou un an après une rupture postérieure, jusqu'à la
        reprise d'une activité affiliée ailleurs, et pendant les congés que les
        décrets n° 2025-761 et n° 2025-799 énumèrent. Un retour que rien ne
        maintient (:meth:`Carriere.retours`) est un recrutement d'après la
        borne : il date l'entrée de cette année et des suivantes.

        Le modèle ne connaît la carrière qu'à l'année : le départ se date de la
        fin de sa dernière année d'emploi, le retour de janvier. Une année
        civile entière sans emploi sous le statut, après une rupture
        postérieure, passe le mois comme l'an ; seules la maintiennent les
        années d'une interruption qui suspend le statut. Revenu avant la
        borne, l'assuré est recruté avant elle, et garde son régime.
        """
        entree = carriere.date_entree(affiliation)
        regle = self.maintien(affiliation)
        if entree is None or regle is None:
            return entree
        borne, annees = regle
        for retour in carriere.retours(affiliation):
            if retour.annee > annee:
                break
            if DateMois(retour.annee, 1).rang < borne.rang:
                continue
            if DateMois(retour.depart, MOIS_PAR_AN).rang < borne.rang:
                maintenu = retour.annee - retour.depart <= annees
            else:
                maintenu = retour.suspendu
            if not maintenu:
                entree = DateMois(retour.annee, 1)
        return entree

    @property
    def hors_routage(self) -> dict[str, str]:
        """Régimes qu'aucune affiliation ne route, et la raison déclarée."""
        return dict(self._hors_routage)

    def sans_employeur(self, affiliation: str) -> bool:
        """Ce statut cotise-t-il sans employeur ?

        Vrai pour les non-salariés : leur cotisation est intégralement
        personnelle. Le drapeau est porté par le STATUT et non par le régime,
        parce qu'un non-salarié relève souvent d'un régime partagé avec des
        salariés — un artisan cotise au régime général, dont la fiche porte la
        répartition d'un salarié. Le taux y est le bon ; la répartition, non.
        """
        return bool(self._profils.get(affiliation, {}).get("sans_employeur", False))

    def part_salariale_seule(self, affiliation: str) -> bool:
        """Ce statut ne paie-t-il que la part salariale, sans part patronale ?

        Vrai pour les trois statuts d'auteur : l'auteur paie la cotisation du
        salarié, à son taux, et personne ne paie celle de l'employeur — le
        diffuseur ne verse qu'une contribution de 1 %, toutes branches
        confondues. C'est l'inverse de ``sans_employeur``, où l'assuré paie
        les deux ; dans les deux cas, le compte ne porte aucune part patronale.
        """
        return bool(self._profils.get(affiliation, {}).get(
            "part_salariale_seule", False))

    def sans_prise_en_charge(self, affiliation: str, annee: int) -> bool:
        """Ce statut paie-t-il seul, cette année, les prestations
        complémentaires de vieillesse que les caisses d'assurance maladie
        financent pour les autres professionnels de santé conventionnés ?

        Vrai pour le médecin de secteur 2 depuis la convention de 1980, qui
        le crée : il verse le forfait et l'ajustement entiers, quand les
        caisses en paient les deux tiers en secteur 1 (L. 645-2, D. 645-3 ;
        guide de la CNAVPL, 2025, p. 85). Ses points sont les mêmes.
        """
        depuis = self.sans_prise_en_charge_depuis(affiliation)
        return depuis is not None and annee >= depuis

    def au_menu(self, affiliation: str) -> bool:
        """Le statut se choisit-il pour un métier ? Non quand il porte
        ``menu: false`` : l'assurance volontaire du salarié expatrié, que la
        saisie dit sur une période passée hors de France."""
        return bool(self._profils.get(affiliation, {}).get("menu", True))

    def assurance_volontaire(self, affiliation: str) -> dict | None:
        """Le barème de l'assurance volontaire que porte le statut — la part du
        plafond de chaque catégorie, l'âge où finit la 4e —, ou rien."""
        bareme = self._profils.get(affiliation, {}).get("assurance_volontaire")
        if bareme is None:
            return None
        return {"parts_du_plafond": {str(categorie): float(part) for categorie, part
                                     in bareme["parts_du_plafond"].items()},
                "age_de_la_4e_categorie": int(bareme["age_de_la_4e_categorie"])}

    def sans_prise_en_charge_depuis(self, affiliation: str) -> int | None:
        """L'année depuis laquelle :meth:`sans_prise_en_charge` vaut, ou rien."""
        depuis = self._profils.get(affiliation, {}).get("sans_prise_en_charge_depuis")
        return None if depuis is None else int(depuis)

    def categorie_active(self, affiliation: str) -> str | None:
        """Classement de l'emploi : ``active``, ``super_active`` ou rien.

        Le classement tient à l'EMPLOI, pas à la personne ni au régime : un
        aide-soignant et un rédacteur territorial cotisent à la même CNRACL, et
        l'un liquide cinq ans avant l'autre. Aucune donnée de carrière — revenu,
        régime, âge — ne permet de le deviner ; c'est donc le statut déclaré qui
        le porte, comme il porte déjà l'absence d'employeur.
        """
        classement = self._profils.get(affiliation, {}).get("categorie_active")
        if classement is None:
            return None
        if classement not in ("active", "super_active"):
            raise ValueError(
                f"{affiliation} : classement inconnu {classement!r} "
                "(attendu 'active' ou 'super_active')"
            )
        return classement

    def pension_militaire(self, affiliation: str) -> str | None:
        """Catégorie militaire : ``non_officier``, ``officier`` ou rien.

        Les militaires relèvent du même régime que les fonctionnaires civils de
        l'État — le code s'appelle « des pensions civiles ET MILITAIRES » — mais
        leur pension ne s'ouvre pas à un âge : elle s'ouvre à une durée de
        services, différente selon qu'ils sont officiers ou non.
        """
        categorie = self._profils.get(affiliation, {}).get("pension_militaire")
        if categorie is None:
            return None
        if categorie not in ("non_officier", "officier"):
            raise ValueError(
                f"{affiliation} : catégorie militaire inconnue {categorie!r} "
                "(attendu 'non_officier' ou 'officier')"
            )
        return categorie

    @property
    def classements_actifs(self) -> dict[str, str]:
        """Statuts classés en catégorie active, et leur classement."""
        return {code: self.categorie_active(code) for code in self.codes
                if self.categorie_active(code) is not None}

    @property
    def categories_militaires(self) -> dict[str, str]:
        """Statuts militaires, et leur catégorie."""
        return {code: self.pension_militaire(code) for code in self.codes
                if self.pension_militaire(code) is not None}

    def regimes(self, affiliation: str, annee: int,
                annee_entree: int | DateMois | None = None,
                revenu: float | None = None,
                plafond: float | None = None) -> tuple[str, ...]:
        """Régimes applicables à ce statut cette année-là.

        **La fermeture d'un régime ne vaut que pour les nouveaux entrants.**
        Le régime de la SNCF est fermé aux agents recrutés depuis le 1er janvier
        2020, celui de la RATP et celui des IEG depuis le 1er septembre 2023 :
        un agent recruté avant garde le sien jusqu'à sa retraite, et c'est la
        « clause du grand-père ». Le routage par la seule ANNÉE faisait basculer
        tout le monde à la date de fermeture, y compris l'agent entré vingt ans
        plus tôt : un cheminot né en 1975, entré en 1996, perdait vingt années
        de régime spécial et vingt points de taux de remplacement.

        Une période peut donc porter `entres_avant` ou `entres_depuis`, et
        ``annee_entree`` — l'entrée dans le statut, une année ou un mois
        (:class:`DateMois`) — dit laquelle s'applique. Les bornes s'écrivent
        au mois quand la loi le fait — « recrutés à compter du 1er septembre
        2023 » — et une année vaut son 1er janvier. Sans entrée, on suppose
        une entrée en janvier de l'année demandée : c'est le comportement
        d'avant, et il reste juste pour qui commence sa carrière cette
        année-là.

        **Un régime peut n'être dû qu'au-delà d'un seuil de revenu.** L'élu
        local n'est assujetti au régime général que « lorsque le montant
        total [de ses indemnités] est supérieur à une fraction, fixée par
        décret, de la valeur du plafond » (L. 382-31) — la moitié. Une
        période porte alors ``seuil_pass: {regime: fraction}`` ; quand
        ``revenu`` et ``plafond`` (de l'année) sont fournis, les régimes dont
        le seuil n'est pas atteint sont retirés. Sans eux, la période est
        rendue telle quelle : c'est la liste des régimes POSSIBLES, celle
        que l'inventaire et les tests de cohérence attendent.
        """
        periode = self._periode(affiliation, annee, annee_entree)
        if periode is None:
            return ()
        regimes = tuple(periode.get("regimes") or ())
        seuils = periode.get("seuil_pass") or {}
        if seuils and revenu is not None and plafond is not None:
            regimes = tuple(
                code for code in regimes
                if revenu >= float(seuils.get(code, 0.0)) * plafond
            )
        return regimes

    def services_passes(self, affiliation: str, annee: int,
                        annee_entree: int | DateMois | None = None
                        ) -> tuple[frozenset[str], int]:
        """Ceux des régimes de l'année qui la VALIDENT SANS COTISATION, et
        l'année à compter de laquelle une pension les sert.

        Ce sont les SERVICES PASSÉS : les années accomplies avant que
        l'affiliation à l'Arrco soit obligatoire, que l'institution valide
        gratuitement quand la retraite complémentaire se généralise. En
        Nouvelle-Calédonie, l'accord territorial du 29 août 1994 généralise
        l'Arrco au 1er janvier 1995 ; à Saint-Pierre-et-Miquelon, les arrêtés
        du 21 juin 1988 l'étendent au 1er janvier 1988. Le modèle routait ces
        années comme des années cotisées, et le compte notionnel y portait des
        cotisations que personne n'avait versées. Une période porte alors
        ``services_passes: {regimes: [...], pension_depuis: AAAA}`` : le
        scénario 1 inscrit les points de ces années comme ceux d'une année
        cotisée, mais à une pension prise à compter du 1er janvier de
        ``pension_depuis`` seulement — avant, le régime n'existait pas pour ce
        statut —, et le compte notionnel n'en porte rien, comme des points
        de la maladie. Rien, et l'année zéro, pour une année sans services
        passés. Voir la fiche `services_passes_outre_mer`.
        """
        periode = self._periode(affiliation, annee, annee_entree)
        regle = (periode or {}).get("services_passes")
        if not regle:
            return frozenset(), 0
        return frozenset(regle.get("regimes") or ()), int(regle["pension_depuis"])

    def validee_sans_cotisation(self, affiliation: str, annee: int,
                                annee_entree: int | DateMois | None = None) -> bool:
        """L'année est-elle validée SANS AUCUNE COTISATION, par tous ses régimes ?

        Ce sont les années d'activité cultuelle d'avant 1979, que la CAVIMAC
        valide gratuitement (D. 721-11 du code de 1985) : elles comptent dans
        la durée du régime, jamais parmi les trimestres COTISÉS — ni pour la
        carrière longue, ni pour le minimum contributif majoré. Le modèle les
        comptait cotisées, sans les router nulle part. Les services passés
        d'un salarié calédonien s'ajoutent au contraire à une année que la
        CAFAT encaisse : elle reste cotisée. Voir la fiche
        `cultes_fractions_de_pension`.
        """
        periode = self._periode(affiliation, annee, annee_entree)
        regle = (periode or {}).get("services_passes")
        if not regle:
            return False
        regimes = frozenset(periode.get("regimes") or ())
        return bool(regimes) and regimes <= frozenset(regle.get("regimes") or ())

    def _periode(self, affiliation: str, annee: int,
                 annee_entree: int | DateMois | None = None) -> dict | None:
        """La période du statut qui couvre cette année, pour cette entrée."""
        if affiliation not in self._profils:
            raise KeyError(
                f"affiliation inconnue : {affiliation!r}. Disponibles : "
                + ", ".join(self.codes)
            )
        if annee_entree is None:
            entree = DateMois(annee, 1).rang
        elif isinstance(annee_entree, DateMois):
            entree = annee_entree.rang
        else:
            entree = DateMois(int(annee_entree), 1).rang
        for periode in self._profils[affiliation].get("periodes", []):
            fin = periode.get("fin")
            if not (periode["debut"] <= annee and (fin is None or annee <= fin)):
                continue
            avant, depuis = periode.get("entres_avant"), periode.get("entres_depuis")
            if avant is not None and entree >= rang_borne(avant):
                continue
            if depuis is not None and entree < rang_borne(depuis):
                continue
            return periode
        return None
