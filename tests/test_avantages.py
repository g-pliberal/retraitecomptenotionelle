"""L'inventaire des avantages non contributifs, et son exhaustivité.

Le dépôt portait trois listes partielles et discordantes de ce que le scénario 1
sert au-delà de la cotisation : les champs de ``Neutralisations``, les codes
``avantages_non_contributifs`` des fiches de régime, et les lignes de la cascade
``AvantageApplique``. Aucune ne disait ce que chaque ligne coûte, et aucune ne
contenait les deux autres.

``legislation/avantages_non_contributifs.yaml`` est leur union, complétée de ce
qu'aucune ne portait. Ces tests sont ce qui l'empêche de redevenir partielle :
tout code employé par l'une des trois listes doit avoir sa ligne dans
l'inventaire, sous son code ou sous un alias.
"""

from __future__ import annotations

import re

import pytest
import yaml

from retraite_notionnelle import memoire
from retraite_notionnelle.config import RACINE_DONNEES, Neutralisations

CHEMIN = RACINE_DONNEES / "reference" / "legislation" / "avantages_non_contributifs.yaml"

#: Les quatre états possibles du modèle à l'égard d'un avantage, et les trois
#: façons d'en mesurer le coût. Le vocabulaire est fermé : un cinquième état
#: inventé au fil de l'eau rendrait l'inventaire illisible.
ETATS = {"chiffre", "integre", "declare", "absent"}
MESURES = {"modele", "serie_publiee", "aucune"}


@pytest.fixture(scope="module")
def inventaire() -> dict:
    with CHEMIN.open(encoding="utf-8") as flux:
        return yaml.safe_load(flux)


@pytest.fixture(scope="module")
def par_code(inventaire) -> dict[str, dict]:
    """Chaque avantage sous son code ET sous chacun de ses alias."""
    table: dict[str, dict] = {}
    for avantage in inventaire["avantages"]:
        for nom in [avantage["code"], *avantage.get("alias", [])]:
            assert nom not in table, f"code ou alias en double : {nom}"
            table[nom] = avantage
    return table


def _codes_de_la_cascade() -> set[str]:
    """Les codes que ``ScenarioActuel.calculer`` peut émettre : ce que la
    liquidation mesure par des liquidations d'essai, ce que l'étape qui
    complète applique, et l'ASPA de l'étape « foyer et net ».

    Lus dans la SOURCE plutôt que par une simulation : une cascade ne rend que
    les avantages qu'une carrière donnée déclenche, et aucune carrière ne les
    déclenche tous. La source, elle, les porte tous.
    """
    from retraite_notionnelle.droit import completer, foyer, liquidation

    source = "".join(__import__("inspect").getsource(module)
                     for module in (liquidation, completer, foyer))
    return set(re.findall(r'AvantageApplique\(\s*code="([a-z_]+)"', source))


def test_le_vocabulaire_de_l_inventaire_est_ferme(inventaire):
    familles = set(inventaire["familles"])
    for avantage in inventaire["avantages"]:
        code = avantage["code"]
        assert avantage["famille"] in familles, f"{code} : famille inconnue"
        assert avantage["etat_modele"] in ETATS, f"{code} : état inconnu"
        assert avantage["cout"]["mesurable_par"] in MESURES, f"{code} : mesure inconnue"


def test_une_ligne_de_cascade_est_declaree_si_et_seulement_si_elle_chiffre(inventaire):
    """``ligne_cascade`` et ``etat_modele: chiffre`` disent la même chose.

    Un avantage chiffré est un avantage dont la cascade isole le montant ; il a
    donc une ligne. Un avantage qui n'est pas chiffré n'en a pas, et doit dire
    pourquoi — c'est le champ ``pourquoi_pas_chiffre``, qui est ce qui empêche
    un « non » de passer pour une évidence.
    """
    for avantage in inventaire["avantages"]:
        code, etat = avantage["code"], avantage["etat_modele"]
        if etat == "chiffre":
            assert avantage["ligne_cascade"], f"{code} : chiffré sans ligne de cascade"
        else:
            assert avantage["ligne_cascade"] is None, f"{code} : ligne de cascade sans chiffrage"
            assert avantage.get("pourquoi_pas_chiffre"), f"{code} : non chiffré sans raison écrite"


def test_toute_ligne_de_cascade_a_sa_ligne_d_inventaire(par_code):
    manquants = {
        code for code in _codes_de_la_cascade()
        if code not in par_code and not any(
            a["ligne_cascade"] == code for a in par_code.values()
        )
    }
    assert manquants == set(), (
        "lignes de cascade absentes de l'inventaire : " + ", ".join(sorted(manquants))
    )


def test_toute_ligne_de_cascade_pointe_un_avantage_chiffre(inventaire):
    cascade = _codes_de_la_cascade()
    for avantage in inventaire["avantages"]:
        ligne = avantage["ligne_cascade"]
        if ligne is not None:
            assert ligne in cascade, f"{avantage['code']} : ligne {ligne} inconnue de la cascade"


def test_tout_champ_de_neutralisations_a_sa_ligne_d_inventaire(par_code):
    manquants = {nom for nom in vars(Neutralisations()) if nom not in par_code}
    assert manquants == set(), (
        "champs de Neutralisations absents de l'inventaire : " + ", ".join(sorted(manquants))
    )


def test_tout_code_declare_par_une_fiche_a_sa_ligne_d_inventaire(par_code):
    """Les fiches de régime déclarent, l'inventaire répond.

    C'est le test qui coûte le plus cher à ignorer : une fiche nouvelle peut
    introduire un code d'un trait de plume, et sans ce test personne ne saurait
    que le dépôt prétend servir un avantage qu'il n'a jamais inventorié.
    """
    declares: set[str] = set()
    dossier = RACINE_DONNEES / "reference" / "regimes"
    for chemin in sorted(dossier.glob("*.yaml")):
        with chemin.open(encoding="utf-8") as flux:
            declares |= _codes_declares(yaml.safe_load(flux))
    manquants = declares - set(par_code)
    assert manquants == set(), (
        "codes déclarés par une fiche et absents de l'inventaire : "
        + ", ".join(sorted(manquants))
    )


def _codes_declares(objet) -> set[str]:
    if isinstance(objet, dict):
        codes: set[str] = set()
        for cle, valeur in objet.items():
            if cle == "avantages_non_contributifs" and isinstance(valeur, list):
                codes |= set(valeur)
            else:
                codes |= _codes_declares(valeur)
        return codes
    if isinstance(objet, list):
        return set().union(*(_codes_declares(x) for x in objet)) if objet else set()
    return set()


def test_les_renvois_a_la_carte_existent(inventaire):
    """Chaque avantage renvoie aux fiches de la carte qui le portent
    (data/reference/regles/), et à des fiches qui existent."""
    from retraite_notionnelle.noyau import carte

    connues = set(carte.fiches())
    for avantage in inventaire["avantages"]:
        inconnues = set(avantage.get("fiches") or ()) - connues
        assert inconnues == set(), (
            f"{avantage['code']} : fiches inconnues de la carte — "
            + ", ".join(sorted(inconnues))
        )


def test_les_renvois_au_manifeste_des_sources_existent(inventaire):
    with (RACINE_DONNEES / "sources.yaml").open(encoding="utf-8") as flux:
        connues = _ids(yaml.safe_load(flux))
    for avantage in inventaire["avantages"]:
        source = avantage["cout"].get("source_id")
        if source is not None:
            assert source in connues, f"{avantage['code']} : source_id inconnu — {source}"


def _ids(objet) -> set[str]:
    if isinstance(objet, dict):
        trouves = {objet["id"]} if isinstance(objet.get("id"), str) else set()
        for valeur in objet.values():
            trouves |= _ids(valeur)
        return trouves
    if isinstance(objet, list):
        return set().union(*(_ids(x) for x in objet)) if objet else set()
    return set()


def test_une_source_publiee_nomme_toujours_sa_source(inventaire):
    for avantage in inventaire["avantages"]:
        if avantage["cout"]["mesurable_par"] == "serie_publiee":
            assert avantage["cout"].get("source_id"), (
                f"{avantage['code']} : série publiée annoncée sans source_id"
            )


# ---------------------------------------------------------------------------
# Le chiffrage par recalcul : ce que la cascade n'isole pas
#
# Deux avantages — les périodes assimilées et la catégorie active — sont servis
# par le scénario 1 sans que la cascade les sépare : leur effet passe par un
# trimestre ou par un âge. `scripts/cout_avantages.py` les mesure en refaisant
# la pension sans l'avantage, à date de liquidation inchangée. Ces tests
# protègent les deux hypothèses dont ce recalcul dépend, et qu'une fiche
# modifiée casserait sans bruit.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def script_cout():
    """Le module du modèle, qui porte la mesure — le script n'en est qu'un appelant."""
    from retraite_notionnelle import avantages

    return avantages


def test_un_avantage_chiffre_par_recalcul_nomme_un_script_qui_existe(inventaire):
    racine = RACINE_DONNEES.parent
    chiffres = [a for a in inventaire["avantages"] if a.get("chiffre_par")]
    assert chiffres, "plus aucun avantage n'est chiffré par recalcul"
    for avantage in chiffres:
        chemin = racine / avantage["chiffre_par"]
        assert chemin.is_file(), f"{avantage['code']} : {chemin} n'existe pas"


def test_le_statut_sedentaire_temoin_releve_des_memes_regimes(script_cout):
    """Le statut témoin sert de CONTRÔLE au retrait par le catalogue.

    La catégorie active se mesure en retirant sa déclaration des fiches. Une
    seconde mesure, indépendante, refait la pension avec le statut sédentaire de
    mêmes régimes ; les deux doivent coïncider, et le test suivant l'exige. Pour
    que cette coïncidence ait un sens, encore faut-il que le témoin relève
    bien des mêmes caisses — sans quoi l'écart mesurerait un changement de
    régime. Cela tient à deux lignes d'un fichier de données qu'une session
    pourrait remanier sans y penser.
    """
    import yaml as _yaml

    chemin = RACINE_DONNEES / "reference" / "legislation" / "affiliations.yaml"
    with chemin.open(encoding="utf-8") as flux:
        affiliations = _yaml.safe_load(flux)["affiliations"]

    def regimes(code: str) -> set[str]:
        return {regime for periode in affiliations[code]["periodes"]
                for regime in periode["regimes"]}

    for classe, (temoin, _) in script_cout.SEDENTAIRE.items():
        assert regimes(classe) == regimes(temoin), (
            f"{classe} et son témoin {temoin} ne relèvent pas des mêmes régimes"
        )


def test_aucun_cas_type_ne_porte_les_deux_avantages_recalcules(script_cout):
    """Deux retraits d'âge ne s'additionnent pas, la décote étant plafonnée.

    Le script mesure chaque avantage isolément et les additionne. C'est exact
    tant qu'aucune carrière ne porte les deux — ce qui est le cas : les
    interruptions sont sur une carrière du privé, le classement sur des
    carrières publiques. Si un cas type venait à porter les deux, l'addition
    surestimerait, et ce test le dirait avant le chiffre.
    """
    from retraite_notionnelle.castypes import CAS_TYPES

    fautifs = [cas.code for cas in CAS_TYPES
               if cas.interruptions_relatives and cas.affiliation in script_cout.SEDENTAIRE]
    assert fautifs == [], (
        "cas types portant à la fois des interruptions et un statut classé : "
        + ", ".join(fautifs)
        + " — le recalcul les additionne, ce qui surestime : voir `recalculer`."
    )


def test_le_motif_sans_activite_ne_valide_rien(script_cout):
    """La contrefactuelle des périodes assimilées repose sur ce seul motif.

    `sans_activite` est ce par quoi le script remplace une interruption pour
    mesurer ce qu'elle valait. S'il venait à valider un trimestre, le recalcul
    mesurerait la différence entre deux avantages au lieu de la valeur de l'un.
    """
    import csv as _csv

    chemin = RACINE_DONNEES / "reference" / "legislation" / "periodes_non_travaillees.csv"
    with chemin.open(encoding="utf-8") as flux:
        lignes = {ligne["motif"]: ligne for ligne in _csv.DictReader(
            l for l in flux if not l.lstrip().startswith("#"))}
    neant = lignes["sans_activite"]
    assert int(neant["trimestres_assimiles"]) == 0
    assert neant["ouvre_droits_complementaires"] == "non"
    assert neant["avpf"] == "non"


def test_le_recalcul_rend_un_montant_positif_et_conserve_la_pension(script_cout):
    """Le recalcul mesure un AVANTAGE : il ne peut pas être négatif.

    Et la décomposition doit rester complète : les montants recalculés sont
    pris sur la part contributive, où la cascade les avait laissés, si bien que
    la somme des parts vaut toujours la pension entière. C'est la propriété qui
    rend la table lisible ligne à ligne, et elle se vérifie sur un cas type qui
    porte chacun des deux avantages.
    """
    from retraite_notionnelle import Parametres
    from retraite_notionnelle.castypes import CAS_TYPES
    from retraite_notionnelle.simulateur import Simulateur

    simulateur = Simulateur(Parametres())
    generation = 1960
    porteurs = ("carriere_interrompue", "fonctionnaire_actif")
    for cas in (c for c in CAS_TYPES if c.code in porteurs):
        age = cas.age_liquidation_pour(simulateur, generation)
        carriere = script_cout.carriere_variante(simulateur, cas, generation, age)
        actuel = simulateur.scenario_actuel.calculer(carriere)
        parts, _ = script_cout.recalculer(simulateur, cas, generation, age, actuel)
        assert parts, f"{cas.code} devrait porter un avantage recalculé"
        for ligne, montant in parts.items():
            assert montant > 0.0, f"{cas.code} : {ligne} mesuré négatif ({montant})"
            assert montant < actuel.pension_annuelle, (
                f"{cas.code} : {ligne} dépasse la pension entière"
            )
        total = (actuel.total_contributif
                 + sum(a.montant for a in actuel.avantages_appliques))
        assert total == pytest.approx(actuel.pension_annuelle), (
            f"{cas.code} : la cascade ne somme plus à la pension"
        )


def test_les_deux_mesures_de_la_categorie_active_coincident(script_cout):
    """Deux chemins indépendants, et ils doivent donner le même euro.

    Le premier retire la DÉCLARATION `categorie_active` des fiches de régime :
    le moteur cesse d'opposer l'âge anticipé, sans qu'aucune ligne de code
    change. Le second change le STATUT de l'assuré pour le statut sédentaire de
    mêmes caisses. Les deux mesurent la même chose par des voies qui n'ont rien
    de commun — l'une passe par les données du régime, l'autre par celles de la
    carrière — et leur accord est ce qui donne confiance dans le chiffre.

    C'est la mesure par le catalogue qui est retenue : elle vaut pour tout
    avantage qu'une fiche déclare, là où le statut témoin suppose qu'il en
    existe un, ce qui n'est pas le cas des régimes spéciaux.
    """
    from retraite_notionnelle import Parametres
    from retraite_notionnelle.castypes import CAS_TYPES
    from retraite_notionnelle.simulateur import Simulateur

    simulateur = Simulateur(Parametres())
    variantes = script_cout.scenarios_neutralises(simulateur)
    cas = next(c for c in CAS_TYPES if c.code == "fonctionnaire_actif")
    temoin = script_cout.SEDENTAIRE[cas.affiliation][0]
    compares = 0
    for generation in (1955, 1960, 1970, 1975, 1985):
        age = cas.age_liquidation_pour(simulateur, generation)
        reelle = simulateur.scenario_actuel.calculer(
            script_cout.carriere_variante(simulateur, cas, generation, age))
        par_catalogue = reelle.pension_annuelle - variantes["categorie_active"].calculer(
            script_cout.carriere_variante(simulateur, cas, generation, age)
        ).pension_annuelle
        par_statut = reelle.pension_annuelle - simulateur.scenario_actuel.calculer(
            script_cout.carriere_variante(
                simulateur, cas, generation, age, affiliation=temoin)
        ).pension_annuelle
        assert par_catalogue == pytest.approx(par_statut, abs=1e-6), (
            f"génération {generation} : {par_catalogue:.2f} € par le catalogue, "
            f"{par_statut:.2f} € par le statut"
        )
        compares += 1
    assert compares == 5


def test_chaque_neutralisation_dit_ce_qu_elle_retire(script_cout, par_code):
    """Un écart ne veut rien dire sans sa contrefactuelle.

    Chaque ligne mesurée par retrait doit nommer ce que le retrait fait, et
    viser une ligne de l'inventaire : c'est ce que la page affiche sous le
    chiffre, et ce qui permet de relire la mesure sans rouvrir le code.
    """
    voies = {"carriere", "catalogue", "table"}
    for neutralisation in script_cout.NEUTRALISATIONS:
        assert neutralisation.code in par_code, (
            f"{neutralisation.code} : neutralisation sans ligne d'inventaire"
        )
        assert neutralisation.par in voies, (
            f"{neutralisation.code} : voie de retrait inconnue {neutralisation.par!r}"
        )
        assert len(neutralisation.quoi) > 40, (
            f"{neutralisation.code} : la contrefactuelle n'est pas décrite"
        )


def test_toute_ligne_integree_est_mesuree_ou_dit_pourquoi_elle_ne_l_est_pas(inventaire):
    """Douze lignes `integre`, et aucune ne doit rester sans réponse.

    Une ligne que le scénario 1 sert sans que la cascade l'isole est soit
    mesurée par retrait — elle porte alors `chiffre_par` —, soit lue dans un
    poste publié qui remplace toute ligne calculée — le taux plein par
    inaptitude ou invalidité, servi depuis le 30 septembre 2026 à qui les
    déclare —, soit d'une autre nature, et sa note doit dire par quoi elle se
    chiffre. Ce test interdit qu'une treizième apparaisse en silence.
    """
    avantages = __import__("retraite_notionnelle.avantages", fromlist=["x"])
    codes = {n.code for n in avantages.NEUTRALISATIONS}
    for avantage in inventaire["avantages"]:
        if avantage["etat_modele"] != "integre":
            continue
        if avantage["code"] in codes:
            assert avantage.get("chiffre_par"), (
                f"{avantage['code']} : mesuré par retrait, mais sans `chiffre_par`"
            )
            continue
        if avantage["code"] in avantages.POSTES_PUBLIES:
            assert avantage["cout"]["mesurable_par"] == "serie_publiee", (
                f"{avantage['code']} : lu dans un poste publié, mais sans sa série"
            )
            continue
        # Les autres ne sont pas des dispositifs : elles se chiffrent ailleurs,
        # et la note doit dire où.
        assert avantage["famille"] == "ecarts_structurels", (
            f"{avantage['code']} : ligne intégrée sans neutralisation ni raison"
        )
        assert "CHIFFRÉ" in avantage["cout"]["note"], (
            f"{avantage['code']} : ni mesuré par retrait, ni chiffré ailleurs"
        )


def test_les_variantes_ne_changent_que_ce_qu_elles_retirent(script_cout):
    """Un retrait ne doit pas déplacer une pension qu'il ne concerne pas.

    Le catalogue privé de `categorie_active` ne doit rien faire à un salarié du
    privé ; le barème de carrière longue vidé ne doit rien faire à qui est entré
    tard ; la fiche de l'apprentissage retirée, rien à qui n'a pas été apprenti.
    Sans ce contrôle, une variante trop large gonflerait toutes les lignes à la
    fois, et l'erreur passerait pour un résultat.
    """
    from retraite_notionnelle import Parametres
    from retraite_notionnelle.castypes import CAS_TYPES
    from retraite_notionnelle.simulateur import Simulateur

    simulateur = Simulateur(Parametres())
    variantes = script_cout.scenarios_neutralises(simulateur)
    cas = next(c for c in CAS_TYPES if c.code == "cadre")
    generation = 1955
    age = cas.age_liquidation_pour(simulateur, generation)
    carriere = script_cout.carriere_variante(simulateur, cas, generation, age)
    reelle = simulateur.scenario_actuel.calculer(carriere).pension_annuelle
    for code in ("categorie_active", "carriere_longue", "bonification_cinquieme_militaires",
                 "apprentissage"):
        obtenue = variantes[code].calculer(carriere).pension_annuelle
        assert obtenue == pytest.approx(reelle), (
            f"le retrait de {code} déplace la pension d'un cadre du privé "
            f"de {reelle - obtenue:.2f} €"
        )


def _apprenti_puis_salarie(simulateur, fin_du_salariat: int, age_liquidation: float):
    """Né en 1998, apprenti du 1er juillet 2014 au 31 décembre 2016 pour
    quelques centaines d'euros par an, moins que les cent cinquante heures de
    SMIC qui valident un trimestre (R. 351-9), puis salarié à 30 000 € par an
    de 2017 à ``fin_du_salariat`` exclue. Le relevé porte les euros sans les
    trimestres : le modèle les valide du salaire, comme la caisse."""
    from retraite_notionnelle import chronologie
    from retraite_notionnelle.carriere import Carriere, LigneRelevee

    apprentissage = {2014: 400.0, 2015: 900.0, 2016: 900.0}
    salaires = {**apprentissage, **dict.fromkeys(range(2017, fin_du_salariat), 30000.0)}
    construite = chronologie.du_releve(
        annee_naissance=1998, sexe="H", age_liquidation=age_liquidation,
        releve=[LigneRelevee(annee=annee, affiliation="salarie_prive_non_cadre", revenu=revenu)
                for annee, revenu in salaires.items()])
    for fait in construite["faits"]:
        if fait["id"].startswith("releve_") and int(fait["debut"][:4]) in apprentissage:
            fait["attributs"]["apprentissage"] = True
            if fait["debut"][:4] == "2014":
                fait["debut"] = "2014-07-01"
    return Carriere.depuis_chronologie(chronologie.completer(construite), simulateur.macro)


def test_le_retrait_de_l_apprentissage_ne_retire_que_le_complement(script_cout):
    """Sans sa fiche, le contrat d'apprentissage ne valide plus que ce que ses
    salaires portent : c'est la mesure du complément (action 130, sixième
    domaine, étape 6).

    Le contrat court du 1er juillet 2014 au 31 décembre 2016 : trente mois,
    dix trimestres (D. 373-3), que ses salaires ne valident pas ; le
    complément les donne tous (D. 373-4), et le retrait les ôte tous, sans
    rien d'autre.

    Ils ne comptent que pour la durée d'assurance. Salarié de dix-neuf à
    soixante-quatre ans, l'apprenti a sans eux 180 trimestres, plus que les
    172 que sa génération doit (L. 161-17-3) : sa pension n'en dépend pas, et
    le complément ne lui vaut rien. Salarié de dix-neuf à cinquante ans, il en
    a 124 de ses salaires et 134 avec eux ; parti à soixante-sept ans, l'âge
    où la décote s'annule, il a le taux plein des deux côtés, et sa pension
    du régime général, proratisée sur la durée (L. 351-1), est dans le
    rapport de 134 à 124 ; sa complémentaire, faite de points, ne bouge pas.
    """
    from retraite_notionnelle import Parametres
    from retraite_notionnelle.simulateur import Simulateur

    simulateur = Simulateur(Parametres())
    variante = script_cout.scenarios_neutralises(simulateur)["apprentissage"]

    complete = _apprenti_puis_salarie(simulateur, 2062, 64.0)
    reelle, sans = simulateur.scenario_actuel.calculer(complete), variante.calculer(complete)
    assert reelle.trimestres_requis == sans.trimestres_requis == 172
    assert (reelle.trimestres_valides, sans.trimestres_valides) == (190, 180)
    assert sans.pension_annuelle == pytest.approx(reelle.pension_annuelle)

    incomplete = _apprenti_puis_salarie(simulateur, 2048, 67.0)
    reelle, sans = simulateur.scenario_actuel.calculer(incomplete), variante.calculer(incomplete)
    assert (reelle.trimestres_valides, sans.trimestres_valides) == (134, 124)
    assert reelle.taux_liquidation == sans.taux_liquidation
    assert not reelle.minimum_applique and not sans.minimum_applique
    avec = {pension.regime: pension.montant for pension in reelle.pensions_par_regime}
    sans_complement = {pension.regime: pension.montant for pension in sans.pensions_par_regime}
    assert avec.pop("regime_general") / sans_complement.pop("regime_general") == (
        pytest.approx(134 / 124))
    assert avec == pytest.approx(sans_complement)


def test_toute_ligne_sans_montant_dit_pourquoi(script_cout, inventaire):
    """Un blanc sans raison est une dette ; une raison écrite est une limite.

    La page nomme les trente-neuf dispositifs et donne, pour chacun, son coût de
    la dernière année publiée. Vingt-quatre n'en ont pas : la colonne reste
    vide, et c'est précisément là qu'il faut écrire pourquoi. Sans ce test, un
    dispositif ajouté demain apparaîtrait sur le site avec deux cases vides et
    rien pour les expliquer.
    """
    from retraite_notionnelle import Parametres

    parametres = Parametres()
    cout = memoire.avantages(parametres)
    montants = cout.derniere.lignes
    muets = []
    for avantage in inventaire["avantages"]:
        ligne = avantage["ligne_cascade"] or avantage["code"]
        if montants.get(ligne):
            continue
        if not (avantage.get("sans_chiffre") or "").strip():
            muets.append(avantage["code"])
    assert muets == [], (
        "dispositifs sans montant ET sans raison écrite : " + ", ".join(muets)
    )


def test_un_poste_publie_vise_une_ligne_de_l_inventaire(script_cout, par_code):
    """Les comptes remplacent le modèle : encore faut-il savoir sur quelle ligne.

    Chaque poste des Comptes de la protection sociale renseigne une ligne
    nommée de l'inventaire, et c'est ce qui permet au tableau de la page de
    dire, case par case, si le chiffre est LU ou CALCULÉ. Un poste qui viserait
    une ligne inexistante passerait inaperçu : il produirait une bande sans
    libellé sur le graphique.
    """
    for ligne in script_cout.POSTES_PUBLIES:
        assert ligne in par_code, f"{ligne} : poste publié sans ligne d'inventaire"
    for ligne in script_cout.LIGNES_LUES:
        assert ligne in par_code, f"{ligne} : ligne lue sans ligne d'inventaire"


def test_toute_ligne_chiffree_appartient_a_une_famille(script_cout, par_code):
    """Le graphique empile des FAMILLES : une ligne sans famille disparaîtrait.

    Le tracé de la page groupe les lignes de coût par famille de l'inventaire,
    parce que quinze lignes pour neuf couleurs donnaient six bandes portant la
    couleur d'une autre. Le groupement écarte, par sécurité, toute ligne dont
    il ne sait pas la famille — et une ligne écartée ne fait aucun bruit : elle
    manque au total du tracé sans que rien ne le dise, quand le tableau juste
    en dessous la compte. Ce test refuse ce silence.
    """
    from retraite_notionnelle import Parametres
    from retraite_notionnelle.avantages import charger_avantages

    parametres = Parametres()
    cout = memoire.avantages(parametres)
    inventaire = charger_avantages(parametres.racine_donnees)
    orphelines = [ligne for ligne in cout.lignes
                  if inventaire.famille_de_ligne(ligne) is None]
    assert orphelines == [], (
        "lignes de coût sans famille, absentes du graphique : "
        + ", ".join(orphelines)
    )


def test_une_ligne_lue_ne_s_interrompt_jamais(script_cout):
    """Une ligne publiée commence, puis ne s'arrête plus jusqu'au bord.

    La fenêtre du graphique est l'intersection des fenêtres de publication des
    lignes LUES, et elle se calcule en gardant les années où toutes sont
    présentes. Ce calcul suppose que chaque ligne forme un bloc : si l'une
    d'elles avait un trou au milieu, la fenêtre se couperait en deux et le
    tracé empilerait deux morceaux comme s'ils se suivaient.

    Le jour où ce test tombe, il ne faut pas élargir la fenêtre : il faut
    regarder quelle série a un trou, et pourquoi son producteur l'a laissé.
    """
    from retraite_notionnelle import Parametres

    parametres = Parametres()
    cout = memoire.avantages(parametres)
    for lue in script_cout.LIGNES_LUES:
        servies = [ligne.annee for ligne in cout.annees if lue in ligne.lignes]
        if not servies:
            continue
        attendues = list(range(servies[0], servies[-1] + 1))
        connues = [ligne.annee for ligne in cout.annees
                   if servies[0] <= ligne.annee <= servies[-1]]
        assert servies == [a for a in attendues if a in connues], (
            f"{lue} : série publiée à trous, de {servies[0]} à {servies[-1]}"
        )


def test_une_ligne_ne_melange_jamais_deux_perimetres(script_cout):
    """Une ligne LUE n'existe que là où son producteur la publie.

    C'est la règle la plus chère de ce chantier, et elle a été posée après
    coup : une ligne gardait sa valeur CALCULÉE pour les années d'avant le
    premier poste PUBLIÉ. Le minimum vieillesse valait donc 0,02 milliard en
    2019, par le modèle, et 4,01 en 2020, par les comptes — un facteur deux
    cents à l'intérieur d'une seule série, que personne ne pouvait voir tant
    que le graphique commençait en 2020.

    Une falaise cachée dans une ligne est pire qu'une falaise entre deux
    lignes : nul ne va la chercher. Ce test vérifie qu'aucune ligne lue ne
    déborde de la fenêtre de sa source, en comparant sa série à celle des
    dépenses publiées.
    """
    from retraite_notionnelle import Parametres
    from retraite_notionnelle.donnees.depenses import DepensesRetraite

    parametres = Parametres()
    depenses = DepensesRetraite(parametres.racine_donnees)
    cout = memoire.avantages(parametres)

    for ligne in script_cout.LIGNES_LUES:
        postes = script_cout.POSTES_PUBLIES.get(ligne)
        for annee in cout.annees:
            if ligne not in annee.lignes:
                continue
            if postes is None:  # la réversion, lue dans l'enquête aux caisses
                publie = depenses.reversion(annee.annee) is not None
            else:
                publie = any(depenses.prestation(poste, annee.annee) is not None
                             for poste in postes)
            assert publie, (
                f"{ligne} portée en {annee.annee} alors qu'aucune source ne la "
                f"publie cette année-là : c'est la valeur du modèle qui a servi"
            )


def test_la_decomposition_du_modele_couvre_toute_la_fenetre(script_cout):
    """Le modèle seul garde ses lignes même là où un poste les remplace.

    La règle du test précédent JETTE la valeur calculée d'une ligne lue. Elle
    ne doit pas la jeter partout : c'est la seule série qui remonte à la
    première pension servie sur un périmètre qui ne change jamais, et le
    graphique long de la page s'en sert. Les deux vivent donc côte à côte,
    ``lignes`` pour le niveau et ``modele`` pour la forme, et ce test interdit
    qu'une simplification future confonde les deux.
    """
    from retraite_notionnelle import Parametres

    parametres = Parametres()
    cout = memoire.avantages(parametres)
    assert cout.lignes_modele, "la décomposition du modèle est vide"
    portees = {ligne for annee in cout.annees for ligne in annee.modele}
    remplacees = portees & set(script_cout.LIGNES_LUES)
    assert remplacees, (
        "aucune ligne lue n'a de valeur calculée : le graphique long a perdu "
        "sa raison d'être, ou LIGNES_LUES a changé sans que ce test suive"
    )
    for ligne in remplacees:
        annees = [a.annee for a in cout.annees if a.modele.get(ligne)]
        lues = [a.annee for a in cout.annees if ligne in a.lignes]
        assert annees and annees[0] < min(lues), (
            f"{ligne} : le modèle ne remonte pas plus haut que la publication, "
            f"le graphique long n'y gagne rien"
        )


def test_la_majoration_pour_enfants_se_recoupe_avec_le_jaune(script_cout):
    """Le poste des comptes, confronté au détail de la fonction publique.

    LA PAGE REPOSE SUR DES POSTES PUBLIÉS QU'ELLE NE VÉRIFIE PAS. Elle les
    recopie, et c'est le prix de la règle « le producteur prime sur le
    repreneur » : on prend le chiffre de celui qui compte des personnes
    réelles. Mais une ligne recopiée peut être recopiée SOUS LA MAUVAISE
    ÉTIQUETTE, et rien ne le dirait — un poste voisin mal mappé rendrait un
    montant plausible.

    Le jaune budgétaire annexé au PLF 2027 permet un recoupement, parce qu'il
    détaille la fonction publique là où les comptes agrègent tous les régimes.
    Pour les pensions en paiement fin 2025 (tableau A-7) et la part qui porte
    la majoration avec son supplément moyen (tableau B-1, flux de 2025) :

        1 656 399 × 24,3 % × 277,5 € × 12 = 1,34 Md€   pensions civiles d'État
          408 750 × 12,0 % × 337,7 € × 12 = 0,20 Md€   pensions militaires
          830 114 × 26,5 % × 145,1 € × 12 = 0,38 Md€   FPT
          640 195 × 25,1 % × 151,2 € × 12 = 0,29 Md€   FPH
                                            ‾‾‾‾‾‾‾‾
                                            2,21 Md€

    La fonction publique ferait donc 28 % du poste des comptes de 2024, le
    dernier qu'ils publient. Elle pèse environ un cinquième des retraités
    français, avec des pensions plus élevées : l'écart est du bon côté et du
    bon ordre. Le jaune du PLF 2026 en donnait 2,15 Md€, et la même part.

    LA BANDE EST LARGE À DESSEIN. Les termes ne sont pas du même millésime —
    un stock de fin 2025, une part mesurée sur le flux de la même année, le
    poste des comptes de 2024 —, et ce test ne prétend pas valider le poste au
    pourcent près. Il attrape une
    ERREUR D'ÉTIQUETTE : un poste mal mappé sortirait de [15 %, 45 %] sans
    qu'aucun autre garde-fou ne bronche.
    """
    from retraite_notionnelle import Parametres
    from retraite_notionnelle.donnees.depenses import DepensesRetraite

    # Jaune budgétaire annexé au PLF 2027, tableaux A-7 et B-1 : effectif du
    # stock de fin 2025, part des pensions majorées du flux de 2025 et
    # supplément mensuel moyen, régime par régime.
    JAUNE = {
        "pensions civiles de l'État": (1_656_399, 0.243, 277.5),
        "pensions militaires": (408_750, 0.120, 337.7),
        "FPT (CNRACL)": (830_114, 0.265, 145.1),
        "FPH (CNRACL)": (640_195, 0.251, 151.2),
    }
    fonction_publique = sum(
        effectif * part * euro * 12 / 1e6 for effectif, part, euro in JAUNE.values()
    )

    depenses = DepensesRetraite(Parametres().racine_donnees)
    tous_regimes = depenses.prestation("majoration_enfants", 2024)
    assert tous_regimes, "le poste « majorations pour enfant » a disparu des comptes"

    part = fonction_publique / tous_regimes
    assert 0.15 <= part <= 0.45, (
        f"la fonction publique ferait {part:.0%} du poste « majorations pour "
        f"enfant » ({fonction_publique / 1000:.2f} sur "
        f"{tous_regimes / 1000:.2f} Md€) : l'un des deux ne compte pas ce "
        f"qu'on croit"
    )


def test_les_retraites_de_moins_de_soixante_ans_confrontes_au_jaune_pensions_2027(script_cout):
    """Ce que la grille sert avant soixante ans, contre le stock de fin 2025.

    ``--duree`` compte les annuités servies avant l'âge légal sur les têtes de
    la grille : chaque cas type, pesé par sa caisse, suit la pyramide de l'INSEE
    depuis son départ. Le jaune pensions annexé au PLF 2027 compte au
    31 décembre 2025 les pensionnés de droit direct de chaque régime par tranche
    d'âge, et parmi eux ceux d'invalidité, que la grille ne sert pas (tableau
    A-2). Sous soixante ans, aucune génération n'a atteint l'âge légal : la part
    y est une mesure sans convention.

    - Le militaire en a 35,4 % dans la grille, entre les 31,5 % du jaune hors
      invalidité et ses 39,2 % avec. Il en avait 31,6 % tant que la pyramide,
      qui commençait à 50 ans, lui retirait ses 48 et 49 ans (action 138,
      étape 3) : le recalage de l'action 152 sur le jaune de 2026 tombait juste
      sur ce défaut. Les quatre points de trop restent à expliquer.
    - L'agent de la CNRACL n'en a aucun, quand la caisse en compte 1,3 % hors
      invalidité, 3,3 % avec. Le cas type part au taux plein depuis l'étape 5
      de l'action 159, comme les actifs de 2025, partis à 61,0 ans ; le 1,3 %
      est fait des actifs partis plus tôt, que le cas type moyen ne représente
      pas. Il partait à l'âge d'ouverture jusque-là, et en comptait 12,1 % :
      4,4 des 8,3 milliards que le classement servait avant l'âge légal en
      2024 étaient les siens. L'écart est DÉCLARÉ
      (``docs/limites/5-hors-du-modele.md``).
    - Le civil de l'État ne part jamais avant soixante ans, quand 1,0 % de ses
      pensionnés y sont, hors invalidité : la catégorie active de l'État, la
      carrière longue et les parents de trois enfants, 11 139 départs avant
      l'âge légal en 2025 (tableau C-1), que la grille ne sert pas.
    """
    from retraite_notionnelle import Parametres
    from retraite_notionnelle.castypes import CAS_TYPES
    from retraite_notionnelle.cout import _ponderation, _tetes_par_poids
    from retraite_notionnelle.donnees.population import Population
    from retraite_notionnelle.simulateur import Simulateur

    annee = 2025
    simulateur = Simulateur(Parametres())
    population = Population(RACINE_DONNEES)
    pensionnes, _ = script_cout.decomposer(simulateur, "droit")
    poids = _ponderation(simulateur, "effectifs", CAS_TYPES,
                         tetes=_tetes_par_poids(pensionnes, population))(annee)
    # Les têtes comme ``masses_anticipees`` pèse les masses : la part de la
    # caisse, l'effectif de l'âge, chaque cohorte de la tranche une fois partie.
    tetes: dict[str, list[float]] = {}
    for pensionne in pensionnes:
        part = poids.get(pensionne.code, 0.0)
        if part <= 0.0:
            continue
        for decalage in range(-script_cout._DEMI_TRANCHE, script_cout._DEMI_TRANCHE + 1):
            if annee < pensionne.liquidation(decalage):
                continue
            age = annee - (pensionne.generation + decalage)
            effectif = part * population.effectif(age, annee)
            compte = tetes.setdefault(pensionne.code, [0.0, 0.0])
            compte[0] += effectif if age < 60 else 0.0
            compte[1] += effectif
    grille = {code: avant / total for code, (avant, total) in tetes.items()}

    # Pensionnés de droit direct au 31 décembre 2025 : de moins de soixante
    # ans, dont d'invalidité, et en tout (tableau A-2).
    jaune = {"militaire": (160_236, 31_356, 408_750),
             "fonctionnaire_actif": (49_069, 29_956, 1_470_309),
             "fonctionnaire_sedentaire": (25_204, 9_060, 1_656_399)}
    observee = {code: (avant - invalides) / total
                for code, (avant, invalides, total) in jaune.items()}
    avec_invalides = {code: avant / total for code, (avant, _, total) in jaune.items()}
    assert observee["militaire"] < grille["militaire"] < avec_invalides["militaire"]
    assert grille["fonctionnaire_actif"] == 0.0
    assert 0.005 < observee["fonctionnaire_actif"] < 0.02
    assert grille["fonctionnaire_sedentaire"] == 0.0
    assert observee["fonctionnaire_sedentaire"] > 0.005


def test_chaque_cohorte_part_l_annee_que_lui_donne_le_droit_de_sa_generation(script_cout):
    """La grille des avantages ne simule qu'une génération sur cinq, et
    faisait partir les cinq cohortes qu'elle représente à son âge de départ,
    la date décalée d'autant : l'erreur que la grille du coût a quittée le
    18 octobre 2026 (note « la date de chaque cohorte »). Le salarié au SMIC
    entré à 18 ans, né en janvier 1965, part au titre des carrières longues à
    61 ans, en 2026 ; né en 1963, à 60 ans, en 2023 ; né en 1964, à 60 ans et
    9 mois, en 2024 ; né en 1966 ou en 1967, à 61 ans, en 2027 et en 2028.
    Chaque cohorte part désormais l'année et à l'âge que le droit de sa
    génération lui donne (``Pensionne.departs``, ``Pensionne.ages_depart``) :
    les masses ne la comptent qu'à partir de là, et ses années servies avant
    l'âge légal se comptent au sien — 62 ans et 9 mois nés de 1963 à 1965,
    63 ans et 3 mois en 1966, 63 ans et demi en 1967 (L. 161-17-2, sous la
    suspension de 2026) —, au prorata de l'année passée entre son départ et
    cet âge. Sans dates, celles de la grille, et l'âge légal de la grille."""
    from dataclasses import replace

    from retraite_notionnelle import Parametres
    from retraite_notionnelle.donnees.population import Population
    from retraite_notionnelle.simulateur import Simulateur

    parts = {script_cout.CONTRIBUTIF: 1.0, "periodes_assimilees": 0.25}
    grille = script_cout.Pensionne(code="x", generation=1965, annee_liquidation=2026,
                                   age_liquidation=61.0, parts=parts,
                                   motif="carriere_longue")
    datee = replace(grille, departs=(2023, 2024, 2026, 2027, 2028),
                    ages_depart=(60.0, 60.75, 61.0, 61.0, 61.0))
    decalages = range(-2, 3)
    assert [grille.liquidation(d) for d in decalages] == [2024, 2025, 2026, 2027, 2028]
    assert [datee.liquidation(d) for d in decalages] == [2023, 2024, 2026, 2027, 2028]
    assert [grille.age_de_depart(d) for d in decalages] == [61.0] * 5
    assert [datee.age_de_depart(d) for d in decalages] == [60.0, 60.75, 61.0, 61.0, 61.0]

    population = Population(RACINE_DONNEES)
    simulateur = Simulateur(Parametres())

    def effectif(cohorte: int, annee: int) -> float:
        return population.effectif(annee - cohorte, annee)

    # En 2024, les cohortes de 1963 et de 1964 sont parties ; la grille ne
    # faisait partir que celle de 1963. La première passe l'année entière
    # avant l'âge légal, à 61 ans ; la seconde, partie à 60 ans et 9 mois, en
    # passe le dernier quart.
    parties = effectif(1963, 2024) + effectif(1964, 2024)
    assert script_cout.masses([datee], population, 2024, {"x": 1.0}) == pytest.approx(
        {cle: parties * montant for cle, montant in parts.items()}, rel=1e-12)
    # Le total, puis sa ventilation : `pytest.approx` refuse, depuis pytest
    # 9.2, un dictionnaire dans un tuple.
    total, par_motif = script_cout.masses_anticipees([datee], simulateur, population, 2024,
                                                     {"x": 1.0})
    assert total == pytest.approx(1.25 * parties, rel=1e-12)
    assert par_motif == pytest.approx(
        {"carriere_longue": 1.25 * (effectif(1963, 2024) + 0.25 * effectif(1964, 2024)),
         "classement": 0.0, "regime_special": 0.0}, rel=1e-12)
    seule = effectif(1963, 2024)
    assert script_cout.masses([grille], population, 2024, {"x": 1.0}) == pytest.approx(
        {cle: seule * montant for cle, montant in parts.items()}, rel=1e-12)

    # Toutes parties, en 2029 : la cohorte de 1966, à 63 ans, passe son
    # premier trimestre avant l'âge légal de sa génération, celle de 1967, à
    # 62 ans, l'année entière. Sous l'âge légal de la grille, 62 ans et 9 mois,
    # la première n'y passait rien, la seconde trois trimestres.
    toutes = sum(effectif(1965 + d, 2029) for d in decalages)
    totale, par_motif = script_cout.masses_anticipees([datee], simulateur, population,
                                                      2029, {"x": 1.0})
    assert totale == pytest.approx(1.25 * toutes, rel=1e-12)
    assert par_motif["carriere_longue"] == pytest.approx(
        1.25 * (0.25 * effectif(1966, 2029) + effectif(1967, 2029)), rel=1e-12)
    _, par_motif = script_cout.masses_anticipees([grille], simulateur, population, 2029,
                                                 {"x": 1.0})
    assert par_motif["carriere_longue"] == pytest.approx(
        1.25 * 0.75 * effectif(1967, 2029), rel=1e-12)

    # Partie à l'heure, une cohorte n'est jamais anticipée : la carrière
    # interrompue née en 1962 part en 2024 à 62 ans et demi, son âge légal, et
    # l'année de son départ ne passait avant lui que comptée à l'année.
    a_l_heure = script_cout.Pensionne(
        code="x", generation=1960, annee_liquidation=2022, age_liquidation=62.0,
        parts=parts, motif="regime_special", departs=(2020, 2021, 2022, 2023, 2024),
        ages_depart=(62.0, 62.0, 62.0, 62.0, 62.5))
    totale, par_motif = script_cout.masses_anticipees([a_l_heure], simulateur, population,
                                                      2024, {"x": 1.0})
    assert totale == pytest.approx(1.25 * sum(effectif(1960 + d, 2024) for d in decalages),
                                   rel=1e-12)
    assert par_motif == {"carriere_longue": 0.0, "classement": 0.0, "regime_special": 0.0}


def test_la_decomposition_date_chaque_cohorte_au_droit_de_sa_generation(script_cout,
                                                                         monkeypatch):
    """Le salarié au salaire moyen entré à 21 ans : né en janvier 1963, 1964
    ou 1965, la suspension de la loi de financement pour 2026 lui demande 170
    trimestres (L. 161-17-3) — il part à 63 ans et demi, en 2026, 2027 et
    2028 ; né en 1966 ou en 1967, il lui en faut 172, 43 ans — il part à
    64 ans, en 2030 et en 2031. La décomposition, qui ne simule que la
    génération 1965, faisait partir ces deux-là en 2029 et en 2030."""
    from retraite_notionnelle import Parametres
    from retraite_notionnelle.simulateur import Simulateur

    salarie = next(cas for cas in script_cout.CAS_TYPES if cas.code == "salaire_moyen")
    monkeypatch.setattr(script_cout, "CAS_TYPES", (salarie,))
    monkeypatch.setattr(script_cout, "generations", lambda: (1965,))
    pensionnes, _ = script_cout.decomposer(Simulateur(Parametres()))
    assert [(p.code, p.generation, p.annee_liquidation) for p in pensionnes] == [
        ("salaire_moyen", 1965, 2028)]
    assert pensionnes[0].departs == (2026, 2027, 2028, 2030, 2031)
    assert pensionnes[0].ages_depart == (63.5, 63.5, 63.5, 64.0, 64.0)
