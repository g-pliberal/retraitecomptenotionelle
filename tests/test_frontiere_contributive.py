"""La frontière contributive : son vocabulaire, ses attaches, et ses lectures.

`avantages_non_contributifs.yaml` dit ce qui est non contributif aujourd'hui.
`frontiere_contributive.yaml` dit quand la frontière a BOUGÉ, dans quel sens et
sur laquelle de ses trois faces — ce que l'assuré acquiert sans cotiser, ce
qu'il verse sans acquérir, et qui paie la charge.

Ces tests tiennent trois choses, et la troisième est la seule qui coûte :

1. le vocabulaire est fermé — trois faces, deux sens par face ;
2. toute bascule s'attache à l'inventaire par des codes qui y existent, et à
   un article déclaré comme pivot ;
3. **toute version d'article citée existe dans l'index LEGI, sous cet article
   et à cette date.** C'est ce qui sépare une lecture d'une mémoire. Le test
   se passe quand l'index n'est pas là — une session qui ne l'a pas récupéré
   ne doit pas être bloquée —, et il échoue quand il est là et qu'une ligne
   ne s'y retrouve pas.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest
import yaml

from retraite_notionnelle.config import RACINE_DONNEES

RACINE = RACINE_DONNEES.parent
sys.path.insert(0, str(RACINE / "scripts"))

import frontiere_contributive as frontiere  # noqa: E402

CHEMIN_INVENTAIRE = RACINE_DONNEES / "reference" / "legislation" / "avantages_non_contributifs.yaml"


@pytest.fixture(scope="module")
def donnees() -> dict:
    return frontiere.charger()


@pytest.fixture(scope="module")
def codes_inventaire() -> set[str]:
    with CHEMIN_INVENTAIRE.open(encoding="utf-8") as flux:
        inventaire = yaml.safe_load(flux)
    codes: set[str] = set()
    for avantage in inventaire["avantages"]:
        codes.add(avantage["code"])
        codes.update(avantage.get("alias", []))
    return codes


@pytest.fixture(scope="module")
def dates_inventaire() -> dict[str, tuple[int, int | None]]:
    """Pour chaque code, l'année de création et celle de fin."""
    with CHEMIN_INVENTAIRE.open(encoding="utf-8") as flux:
        inventaire = yaml.safe_load(flux)
    table: dict[str, tuple[int, int | None]] = {}
    for avantage in inventaire["avantages"]:
        for nom in [avantage["code"], *avantage.get("alias", [])]:
            table[nom] = (avantage["creation"], avantage["fin"])
    return table


def test_le_vocabulaire_des_faces_et_des_sens_est_ferme(donnees):
    """Trois faces, deux sens chacune, et pas un de plus.

    Une quatrième face inventée au fil de l'eau rendrait la carte illisible :
    c'est précisément la confusion entre ces trois sens du mot « contributif »
    que ce fichier existe pour défaire.
    """
    for bascule in donnees["bascules"]:
        code, face = bascule["code"], bascule["face"]
        assert face in frontiere.SENS_PAR_FACE, f"{code} : face inconnue « {face} »"
        assert bascule["sens"] in frontiere.SENS_PAR_FACE[face], (
            f"{code} : sens « {bascule['sens']} » impossible sur la face {face}")
        assert bascule["portee_modele"] in frontiere.PORTEES, (
            f"{code} : portée « {bascule['portee_modele']} » inconnue")


def test_chaque_bascule_est_identifiee_une_fois_et_datee(donnees):
    codes = [b["code"] for b in donnees["bascules"]]
    doublons = {c for c in codes if codes.count(c) > 1}
    assert doublons == set(), f"codes en double : {', '.join(sorted(doublons))}"
    for bascule in donnees["bascules"]:
        code = bascule["code"]
        for champ in ("date", "libelle", "quoi", "article", "version", "lu_le",
                      "effet_modele"):
            assert bascule.get(champ), f"{code} : champ {champ} manquant ou vide"


def test_toute_bascule_s_attache_a_des_avantages_de_l_inventaire(donnees, codes_inventaire):
    """Les codes cités doivent exister là-bas, sous leur code ou un alias.

    Une bascule peut n'en citer aucun — le déplafonnement des cotisations ne
    déplace aucun dispositif, il stérilise un prélèvement — mais elle ne peut
    pas en citer un qui n'existe pas : ce serait une attache rompue que rien
    ne signalerait.
    """
    for bascule in donnees["bascules"]:
        inconnus = set(bascule["dispositifs"]) - codes_inventaire
        assert inconnus == set(), (
            f"{bascule['code']} : dispositifs absents de l'inventaire : "
            + ", ".join(sorted(inconnus)))


def test_une_bascule_ne_precede_pas_le_dispositif_qu_elle_deplace(donnees, dates_inventaire):
    """On ne déplace pas ce qui n'existe pas encore, ni ce qui est éteint.

    Le contrôle est à l'année : l'inventaire ne date qu'à cette maille, et
    prétendre au jour près serait se donner une précision qu'il n'a pas.
    """
    for bascule in donnees["bascules"]:
        annee = int(str(bascule["date"])[:4])
        for code in bascule["dispositifs"]:
            creation, fin = dates_inventaire[code]
            assert annee >= creation, (
                f"{bascule['code']} ({annee}) précède la création de {code} ({creation})")
            if fin is not None:
                assert annee <= fin, (
                    f"{bascule['code']} ({annee}) suit la fin de {code} ({fin})")


def test_tout_article_cite_est_un_pivot_declare_et_tout_pivot_sert(donnees):
    """Les pivots sont ce que le script relit. Un pivot qui ne sert pas est un
    ornement ; un article cité hors pivot échappe à la vérification."""
    pivots = {frontiere._normalise(p["article"]) for p in donnees["pivots"]}
    cites = set()
    for bascule in donnees["bascules"]:
        for champ in ("article", "article_precedent"):
            if bascule.get(champ):
                cites.add(frontiere._normalise(bascule[champ]))
    # Un article peut fonder une LIGNE de l'inventaire sans dater de bascule :
    # L. 6243-3 du code du travail porte le droit de l'apprenti, que le code de
    # la sécurité sociale ignore. Il est alors cité par la liste légale, sous
    # `lectures`, et la sonde en vérifie la version comme celle d'une bascule.
    legale = donnees["liste_legale"]
    cites.add(frontiere._normalise(legale["article"]))
    for lecture in legale.get("lectures") or ():
        cites.add(frontiere._normalise(lecture["article"]))
    assert cites <= pivots, (
        "articles cités sans pivot déclaré : " + ", ".join(sorted(cites - pivots)))
    assert pivots <= cites, (
        "pivots qu'aucune bascule n'emploie : " + ", ".join(sorted(pivots - cites)))


def test_deux_dates_ne_passent_jamais_sans_leur_raison(donnees):
    """`date_preuve` sépare l'effet d'une bascule de la version qui en fait foi.

    L'article 24 de la LFSS 2025 est en vigueur au 1er mars 2025 et supprime le
    FSV au 1er janvier 2026 : les deux dates sont vraies. Les séparer est
    légitime ; le faire en silence ne l'est pas.
    """
    for bascule in donnees["bascules"]:
        if bascule.get("date_preuve") is None:
            continue
        assert str(bascule["date_preuve"]) != str(bascule["date"]), (
            f"{bascule['code']} : date_preuve identique à date, donc inutile")
        assert bascule.get("pourquoi_deux_dates"), (
            f"{bascule['code']} : deux dates sans raison écrite")


def test_la_carte_et_la_chronologie_s_impriment(donnees, capsys):
    """Les deux sorties du script rendent toutes les bascules.

    Un `FLECHE` incomplet lèverait un KeyError ; une face oubliée dans la
    boucle de `carte` ferait disparaître des lignes sans bruit.
    """
    frontiere.carte(donnees)
    frontiere.chronologie(donnees)
    imprime = capsys.readouterr().out
    for bascule in donnees["bascules"]:
        assert bascule["libelle"] in imprime, f"{bascule['code']} absent des sorties"


@pytest.mark.skipif(not frontiere.INDEX_LEGI.exists(),
                    reason="index LEGI absent : python scripts/fetch/dila_index.py legi --recuperer")
def test_toute_version_citee_se_retrouve_dans_l_index_legi(donnees):
    """Le seul test qui tienne vraiment ce fichier.

    Une date de bascule sans version d'article opposable serait une mémoire.
    Le contrôle rouvre le dump, et confronte chaque identifiant à ce qu'il
    porte : le bon article, la bonne date d'entrée en vigueur — ou de FIN
    quand c'est la disparition d'une version qui fait l'événement.

    Ce qu'il ne dit pas : que la prose de la ligne rende fidèlement ce que la
    version énonce. Cela, seul un lecteur le fait, et c'est pourquoi chaque
    ligne porte `lu_le`.
    """
    ecarts = frontiere.verifier(donnees)
    assert ecarts == [], "\n".join(ecarts)


#: Les comptes que la prose de `docs/frontiere_contributive.md` écrit en
#: toutes lettres, et l'expression du fichier de données qui les recalcule.
#: « Un nombre qui vit dans une phrase est un nombre qui ment un jour » —
#: docs/avantages_non_contributifs.md, § 4 sexies. Celui-ci mentira le jour où
#: une bascule sera ajoutée, et ce test le dira ce jour-là.
def _droits_par_code(donnees: dict) -> dict[str, dict[str, int]]:
    """Les mouvements de DROITS, rangés par code — la dissymétrie du § 5.

    L'article porte le code dans son libellé (« L. 12 CPCMR », « L. 351-3 CSS »),
    et c'est la seule information dont ce découpage a besoin.
    """
    par: dict[str, dict[str, int]] = {"CSS": {}, "CPCMR": {}, "SPECIAUX": {}}
    for bascule in donnees["bascules"]:
        if bascule["face"] != "droit":
            continue
        article = bascule["article"]
        if "CPCMR" in article:
            code = "CPCMR"
        elif "décret" in article:
            # Les régimes spéciaux ne vivent ni dans un code ni dans une loi :
            # leurs bonifications sont dans deux décrets propres à chaque
            # caisse, et c'est ce qui les distingue ici.
            code = "SPECIAUX"
        else:
            code = "CSS"
        par[code][bascule["sens"]] = par[code].get(bascule["sens"], 0) + 1
    return par


COMPTES_DE_LA_PROSE = {
    "Quarante et un déplacements datés":
        lambda d: len(d["bascules"]) == 41,
    "soixante-quatorze identifiants cités":
        lambda d: sum(1 for b in d["bascules"]
                      for c in ("version", "version_precedente") if b.get(c))
                  + 1 + len(d["liste_legale"].get("lectures") or ()) == 74,
    # Le partage par code, qui est le résultat de la section 5 : le privé ne
    # se referme jamais, la fonction publique est le seul endroit où la
    # frontière a reculé. Un chiffre faux ici retournerait la conclusion.
    "| Code de la sécurité sociale (privé) | **5** | 1 |":
        lambda d: _droits_par_code(d)["CSS"] == {"ouvre": 5, "ferme": 1},
    "| Code des pensions civiles et militaires | 4 | **6** |":
        lambda d: _droits_par_code(d)["CPCMR"] == {"ouvre": 4, "ferme": 6},
    "| Régimes spéciaux (SNCF, RATP) | 3 | 3 |":
        lambda d: _droits_par_code(d)["SPECIAUX"] == {"ouvre": 3, "ferme": 3},
    "six fermetures contre quatre ouvertures":
        lambda d: _droits_par_code(d)["CPCMR"] == {"ouvre": 4, "ferme": 6},
    "Dix bascules, lues dans trois articles du code des pensions":
        lambda d: sum("CPCMR" in b["article"] for b in d["bascules"]) == 10,
    "trois fois en dix-huit ans":
        lambda d: sum("décret" in b["article"] and b["sens"] == "ouvre"
                      for b in d["bascules"]) == 3,
    "Dix charges ont été isolées chez un payeur nommé, dont neuf avant 2015":
        lambda d: (sum(b["sens"] == "identifie" for b in d["bascules"]) == 10
                   and sum(b["sens"] == "identifie" and str(b["date"]) < "2015"
                           for b in d["bascules"]) == 9),
    "six ont été refondues dans les comptes des régimes, et cinq de ces six "
    "sont postérieures à 2016":
        lambda d: (sum(b["sens"] == "fond" for b in d["bascules"]) == 6
                   and sum(b["sens"] == "fond" and str(b["date"]) >= "2016"
                           for b in d["bascules"]) == 5),
}


def test_les_comptes_ecrits_dans_la_prose_sont_ceux_du_fichier(donnees):
    """La prose annonce des nombres ; le fichier les porte. Les deux doivent
    dire la même chose, sans quoi le document se périme en silence.

    Le test vérifie DEUX choses pour chaque ligne : que la phrase est bien dans
    le document — une phrase reformulée sans mettre le compte à jour passerait
    sinon inaperçue — et que le compte qu'elle annonce est celui des données.
    """
    # Les blancs sont écrasés des deux côtés : la prose est coupée à
    # soixante-dix-neuf colonnes, et une phrase à cheval sur deux lignes est la
    # même phrase.
    brut = (RACINE / "docs" / "frontiere_contributive.md").read_text(encoding="utf-8")
    prose = re.sub(r"\s+", " ", brut)
    for phrase, compte in COMPTES_DE_LA_PROSE.items():
        assert phrase in prose, f"phrase absente de la prose : « {phrase} »"
        assert compte(donnees), f"le compte de « {phrase} » n'est plus celui du fichier"


def test_le_renvoi_de_l_inventaire_annonce_le_bon_compte(donnees):
    """`avantages_non_contributifs.md` renvoie ici en annonçant un nombre.

    Un compte écrit dans un document et tenu dans un autre est exactement ce
    qui se périme sans bruit : la session qui ajoutera une bascule n'ira pas
    relire l'inventaire. Ce test exigeait la formule en toutes lettres,
    « vingt-quatre fois depuis 1991 », et devait donc être réécrit à chaque
    bascule. Le renvoi porte maintenant son ancre, et
    `scripts/verifier_prose.py` recompte depuis ce fichier-ci : ce qui reste
    à exiger, c'est que l'ancre soit là et qu'elle interroge la bonne liste.
    """
    prose = re.sub(r"\s+", " ", (RACINE / "docs" / "avantages_non_contributifs.md")
                   .read_text(encoding="utf-8"))
    assert "entrees(data/reference/legislation/frontiere_contributive.yaml:bascules)" \
        in prose, ("le renvoi de l'inventaire vers la frontière contributive a "
                   "perdu son ancre : sans elle, plus rien ne recompte ce nombre")
    assert min(str(b["date"]) for b in donnees["bascules"])[:4] == "1991"


# --- Ce que le dépôt ne saura jamais certifier -----------------------------

def test_les_bascules_hors_legi_ont_le_meme_vocabulaire(donnees):
    """Une preuve d'une autre nature ne donne pas droit à un autre vocabulaire.

    Les accords nationaux interprofessionnels ne sont pas au Journal officiel
    et n'entrent pas dans l'index LEGI : la sonde n'a rien à quoi les
    confronter. Ce qui change est la PREUVE — une adresse et une date de
    lecture —, pas la grammaire.
    """
    for bascule in donnees["bascules_hors_legi"]:
        code, face = bascule["code"], bascule["face"]
        assert face in frontiere.SENS_PAR_FACE, f"{code} : face inconnue « {face} »"
        assert bascule["sens"] in frontiere.SENS_PAR_FACE[face], (
            f"{code} : sens « {bascule['sens']} » impossible sur la face {face}")
        assert bascule["portee_modele"] in frontiere.PORTEES, f"{code} : portée inconnue"


def test_une_bascule_hors_legi_porte_une_adresse_et_une_date_de_lecture(donnees):
    """C'est tout ce qui la sépare d'un souvenir.

    Aucun script ne peut revérifier ces lignes. Le minimum exigible est donc
    qu'un LECTEUR le puisse : l'adresse consultée, et le jour où elle l'a été.
    """
    for bascule in donnees["bascules_hors_legi"]:
        code = bascule["code"]
        assert str(bascule.get("source", "")).startswith("http"), (
            f"{code} : pas d'adresse consultable")
        assert bascule.get("lu_le"), f"{code} : pas de date de lecture"


def test_aucun_code_ne_vit_des_deux_cotes(donnees):
    codes = [b["code"] for b in donnees["bascules"] + donnees["bascules_hors_legi"]]
    doublons = {c for c in codes if codes.count(c) > 1}
    assert doublons == set(), f"codes en double : {', '.join(sorted(doublons))}"


def test_les_taux_agirc_arrco_se_recomposent(donnees):
    """Le taux appelé EST le taux de calcul des points multiplié par 1,27.

    La fiche de la fédération le dit et le montre : « 6,20 x 1,27 = 7,87 % sur
    la tranche 1 », les taux étant « arrondis au centième ». Ce contrôle n'est
    donc pas une redondance : c'est ce qui attrape une faute de frappe dans
    une table que nul script ne peut aller revérifier.
    """
    baremes = donnees["taux_agirc_arrco"]
    appel = baremes["pourcentage_appel"]
    for tranche in baremes["tranches"]:
        attendu = round(tranche["taux_calcul_des_points"] * appel, 4)
        assert tranche["taux_appele"] == attendu, (
            f"{tranche['nom']} : {tranche['taux_calcul_des_points']:.4f} × {appel} "
            f"donne {attendu}, non {tranche['taux_appele']}")


def test_la_part_sans_droits_de_la_complementaire_est_celle_qu_on_annonce(donnees):
    """38 % sur la tranche 1 : le chiffre le plus fort de ce chantier.

    Il ne vaut que si l'on additionne au taux appelé la contribution
    d'équilibre général, que la fédération qualifie elle-même de « non
    génératrice de droits ». Le test fixe la convention autant que le nombre.
    """
    par_tranche = {t["nom"]: t for t in frontiere.part_sans_contrepartie_complementaire(donnees)}
    assert round(par_tranche["Tranche 1"]["part_sous_plafond"], 3) == 0.381
    assert round(par_tranche["Tranche 2"]["part_sous_plafond"], 3) == 0.300


# --- Le chiffrage ----------------------------------------------------------

@pytest.mark.skipif(not frontiere.CHEMIN_ASSIETTE.exists(),
                    reason="assiette Urssaf absente du dépôt")
def test_la_cotisation_sans_contrepartie_est_le_produit_de_ses_deux_termes():
    """Taux déplafonné × assiette déplafonnée, et rien d'autre.

    Le contrôle est tautologique par construction, et c'est voulu : il
    attrape un refactor qui glisserait un facteur — une conversion d'unité,
    une part salariale appliquée deux fois — au milieu du produit.
    """
    lignes = frontiere.cotisations_sans_contrepartie()
    assert lignes, "aucune année chiffrée"
    for annee, l in lignes.items():
        assert l["total_md"] == pytest.approx(l["assiette_md"] * l["taux"]), annee
        assert l["salariale_md"] + l["patronale_md"] == pytest.approx(l["total_md"]), annee
        assert 0 <= l["salariale_md"] < l["patronale_md"], (
            f"{annee} : la part salariale n'est plus la plus petite des deux")


@pytest.mark.skipif(not frontiere.CHEMIN_ASSIETTE.exists(),
                    reason="assiette Urssaf absente du dépôt")
def test_le_salarie_n_entre_dans_le_deplafonne_qu_en_2005():
    """Un recoupement que rien n'avait préparé, et qui tombe juste.

    La bascule `cotisation_deplafonnee_salarie` est datée du 22 août 2003 par
    la version de L. 241-3 qui ajoute « et des salariés ». La table des taux,
    certifiée et construite par un tout autre chemin — les décrets
    d'application, lus dans LEGI par `dila_legi_taux_cotisation.py` —, porte
    une part salariale NULLE jusqu'en 2004 et positive à partir de 2005.

    Les deux dates ne se contredisent pas : la loi autorise, le décret
    exécute, et le dépôt garde les deux. Ce test tient l'écart, qui
    disparaîtrait sans bruit si quelqu'un alignait l'une sur l'autre.
    """
    lignes = frontiere.cotisations_sans_contrepartie()
    assert all(l["salariale_md"] == 0 for a, l in lignes.items() if a <= 2004)
    assert all(l["salariale_md"] > 0 for a, l in lignes.items() if a >= 2005)


@pytest.mark.skipif(not frontiere.CHEMIN_ASSIETTE.exists(),
                    reason="assiette Urssaf absente du dépôt")
def test_le_chiffrage_de_2025_est_celui_que_la_prose_annonce():
    """Une année CLOSE ne bouge plus : on peut donc l'ancrer.

    Ancrer « la dernière année » se périmerait à chaque trimestre publié par
    l'Urssaf ; ancrer 2025 ne se périme jamais, et c'est ce que le document
    imprime.
    """
    lignes = frontiere.cotisations_sans_contrepartie()
    assert round(lignes[2025]["total_md"], 1) == 17.9
    assert round(lignes[2025]["salariale_md"], 1) == 3.0
    prose = re.sub(r"\s+", " ", (RACINE / "docs" / "frontiere_contributive.md")
                   .read_text(encoding="utf-8"))
    assert "17,9 milliards" in prose


@pytest.mark.skipif(not frontiere.CHEMIN_ASSIETTE.exists(),
                    reason="assiette Urssaf absente du dépôt")
def test_l_assiette_deplafonnee_n_est_pas_celle_des_comptes_nationaux():
    """Le piège qui coûterait le plus cher, et qu'aucun autre test ne verrait.

    `assiette_activite.csv` porte les salaires bruts de TOUTE l'économie,
    fonction publique comprise, qui ne relève pas de l'article L. 241-3.
    Prendre l'une pour l'autre gonflerait la masse d'environ 45 % sans que
    rien ne change de forme — mêmes colonnes, même unité, même allure de
    série. Le test fixe l'ordre de grandeur de l'écart.
    """
    from retraite_notionnelle.donnees.chargement import charger_serie_annuelle

    privee = charger_serie_annuelle(frontiere.CHEMIN_ASSIETTE, "montant_meur",
                                    interpolation="ponctuelle")
    nationale = charger_serie_annuelle(
        RACINE / "data" / "reference" / "macro" / "assiette_activite.csv",
        "montant_meur", interpolation="ponctuelle", filtre={"poste": "salaires_bruts"})
    rapport = privee(2024) / nationale(2024)
    assert 0.60 < rapport < 0.80, (
        f"l'assiette privée vaut {rapport:.0%} des salaires bruts des comptes "
        f"nationaux : l'une des deux séries a changé de champ")


# --- La liste que le législateur tient lui-même ---------------------------

def test_chaque_poste_de_la_liste_legale_porte_un_avantage_ou_une_raison(donnees, codes_inventaire):
    """Un blanc sans raison est une dette ; une raison écrite est une limite.

    C'est la règle de l'inventaire des avantages non contributifs, et elle vaut
    ici pour le motif inverse : cette liste-ci est celle du LÉGISLATEUR, et
    chacun de ses postes doit trouver une ligne du dépôt, ou dire pourquoi il
    n'en trouve pas. Deux dettes ont été découvertes ainsi — l'apprentissage et
    les périodes reconnues équivalentes —, qu'aucune des trois listes internes
    ne pouvait révéler, puisqu'elles décrivent ce que le modèle sait faire et
    non ce que le système verse.
    """
    for poste in donnees["liste_legale"]["postes"]:
        numero = poste["numero"]
        assert poste["quoi"], f"{numero} : poste sans description"
        avantages, manque = poste["avantages"], poste.get("manque")
        assert bool(avantages) != bool(manque), (
            f"{numero} : il faut des avantages OU une raison écrite, pas les deux "
            f"ni aucun des deux")
        inconnus = set(avantages) - codes_inventaire
        assert inconnus == set(), (
            f"{numero} : avantages absents de l'inventaire : {', '.join(sorted(inconnus))}")


def test_la_liste_legale_est_lue_sous_une_version_verifiable(donnees):
    """La liste change à chaque loi de financement : sa version fait foi.

    Elle a déjà changé d'article une fois — L. 135-2 jusqu'en 2025, L. 222-2-1
    depuis —, et le poste qui portait les périodes équivalentes y a été abrogé
    au passage. Sans version citée, la confrontation ci-dessus serait datée de
    nulle part.
    """
    legale = donnees["liste_legale"]
    assert legale["lu_le"], "liste légale sans date de lecture"
    pivots = {frontiere._normalise(p["article"]) for p in donnees["pivots"]}
    assert frontiere._normalise(legale["article"]) in pivots, (
        "l'article de la liste légale n'est pas un pivot : sa version échappe "
        "à la sonde")
    assert any(b["version"] == legale["version"] for b in donnees["bascules"]), (
        "la version de la liste légale n'est vérifiée par aucune bascule : "
        "ajouter la vérification ou citer la version qui l'est")
