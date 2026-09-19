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
    """Les codes que ``ScenarioActuel.calculer`` peut émettre.

    Lus dans la SOURCE plutôt que par une simulation : une cascade ne rend que
    les avantages qu'une carrière donnée déclenche, et aucune carrière ne les
    déclenche tous. La source, elle, les porte tous.
    """
    from retraite_notionnelle.scenarios import actuel

    source = __import__("inspect").getsource(actuel)
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


def test_les_renvois_a_la_veille_existent(inventaire):
    chemin = RACINE_DONNEES / "reference" / "legislation" / "veille.yaml"
    with chemin.open(encoding="utf-8") as flux:
        connues = {entree["id"] for entree in yaml.safe_load(flux)["entrees"]}
    for avantage in inventaire["avantages"]:
        inconnues = set(avantage.get("veille") or ()) - connues
        assert inconnues == set(), (
            f"{avantage['code']} : entrées de veille inconnues — "
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
    """Onze lignes `integre`, et aucune ne doit rester sans réponse.

    Une ligne que le scénario 1 sert sans que la cascade l'isole est soit
    mesurée par retrait — elle porte alors `chiffre_par` —, soit d'une autre
    nature, et sa note doit dire par quoi elle se chiffre. Ce test interdit
    qu'une douzième apparaisse en silence.
    """
    codes = {n.code for n in __import__(
        "retraite_notionnelle.avantages", fromlist=["x"]).NEUTRALISATIONS}
    for avantage in inventaire["avantages"]:
        if avantage["etat_modele"] != "integre":
            continue
        if avantage["code"] in codes:
            assert avantage.get("chiffre_par"), (
                f"{avantage['code']} : mesuré par retrait, mais sans `chiffre_par`"
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
    tard. Sans ce contrôle, une variante trop large gonflerait toutes les
    lignes à la fois, et l'erreur passerait pour un résultat.
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
    for code in ("categorie_active", "carriere_longue"):
        obtenue = variantes[code].calculer(carriere).pension_annuelle
        assert obtenue == pytest.approx(reelle), (
            f"le retrait de {code} déplace la pension d'un cadre du privé "
            f"de {reelle - obtenue:.2f} €"
        )


def test_toute_ligne_sans_montant_dit_pourquoi(script_cout, inventaire):
    """Un blanc sans raison est une dette ; une raison écrite est une limite.

    La page nomme les trente-neuf dispositifs et donne, pour chacun, son coût de
    la dernière année publiée. Vingt-quatre n'en ont pas : la colonne reste
    vide, et c'est précisément là qu'il faut écrire pourquoi. Sans ce test, un
    dispositif ajouté demain apparaîtrait sur le site avec deux cases vides et
    rien pour les expliquer.
    """
    from retraite_notionnelle import Parametres
    from retraite_notionnelle.donnees.depenses import DepensesRetraite
    from retraite_notionnelle.donnees.population import Population
    from retraite_notionnelle.simulateur import Simulateur

    parametres = Parametres()
    simulateur = Simulateur(parametres)
    cout = script_cout.calculer_avantages(
        simulateur,
        DepensesRetraite(parametres.racine_donnees),
        Population(parametres.racine_donnees),
    )
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
    from retraite_notionnelle.donnees.depenses import DepensesRetraite
    from retraite_notionnelle.donnees.population import Population
    from retraite_notionnelle.simulateur import Simulateur

    parametres = Parametres()
    cout = script_cout.calculer_avantages(
        Simulateur(parametres),
        DepensesRetraite(parametres.racine_donnees),
        Population(parametres.racine_donnees),
    )
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
    from retraite_notionnelle.donnees.depenses import DepensesRetraite
    from retraite_notionnelle.donnees.population import Population
    from retraite_notionnelle.simulateur import Simulateur

    parametres = Parametres()
    cout = script_cout.calculer_avantages(
        Simulateur(parametres),
        DepensesRetraite(parametres.racine_donnees),
        Population(parametres.racine_donnees),
    )
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
