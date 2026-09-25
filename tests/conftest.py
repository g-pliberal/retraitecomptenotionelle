"""Les trois niveaux de la suite, et la suite rapide.

    python -m pytest -m rapide    # les règles et les étapes, sous deux minutes
    python -m pytest              # tout : la suite complète, avant d'envoyer sur main

``docs/architecture.md`` (§ 10) range les tests en trois niveaux :

``rapide``
    Les règles — exemples officiels et cas de bascule — et les étapes, chacune
    seule. C'est la suite qu'on relance en travaillant ; son budget est de
    deux minutes (§ 9.1).
``complet``
    Les témoins, joués par les deux moteurs, le site et ses pages, et les
    agrégats de la page Coût, avec les scripts qui les déplacent.
``controle``
    La confrontation aux autres modèles, la certification des données et les
    lecteurs de sources, la prose et les affirmations du site, les registres,
    l'outillage du dépôt.

Chaque test reçoit la marque de son niveau, et ``-m`` choisit. Un fichier
qu'aucune table ne nomme est ``rapide`` : les fichiers de tests qui naissent
sont presque tous ceux d'une règle, et une règle doit être dans la suite
rapide. Un fichier lent qui naît se range donc ici, dans ``COMPLETS`` ou dans
``CONTROLES``, sans quoi il ferait sortir la suite rapide de son budget.

``python -m pytest``, sans ``-m``, ne choisit rien : il lance les trois
niveaux, comme avant. C'est la suite complète, que ``CLAUDE.md`` demande avant
tout envoi sur ``main``, et que GitHub rejoue à chaque envoi.
"""

from __future__ import annotations

import pytest

NIVEAUX = {
    "rapide": "les règles et les étapes, chacune seule : la suite rapide",
    "complet": "les témoins, le site et les agrégats de la page Coût",
    "controle": "les confrontations, la certification, la prose, les registres, l'outillage",
}

#: Les témoins, le site et les agrégats : niveau ``complet``.
COMPLETS = {
    # Le site : ses pages, figées en témoins et rejouées par le portage
    # JavaScript (``node --test`` compris), son formulaire, le parcours de
    # présentation.
    "test_web.py", "test_formulaire.py", "test_parcours.py",
    # La page Coût et les scripts qui la déplacent : chacun recalcule le coût
    # agrégé, sous une variante.
    "test_cout.py", "test_cout_age_depart.py", "test_age_conjoncturel.py",
    "test_age_depart_csp.py", "test_avantages.py", "test_garantie_par_sexe.py",
    "test_solde_fusion.py", "test_stock_age_legal.py",
    "test_proposition_prospective.py", "test_postes_ecartes.py",
    "test_chiffrage_plf.py", "test_scenarios_meres.py",
}

#: Les contrôles : niveau ``controle``.
CONTROLES = {
    # La prose et les affirmations du site, confrontées au dépôt.
    "test_prose.py", "test_affirmations.py",
    # La confrontation à OpenFisca, seconde implémentation écrite par d'autres
    # (ses exemples officiels restent rapides, plus bas).
    "test_oracle.py",
    # Les données : leur socle, leur certification, les lecteurs des
    # documents qui les apportent.
    "test_donnees.py", "test_verification.py", "test_bonifications_jaune.py",
    "test_juris_cnracl_taux.py", "test_lecture_pdf.py", "test_sre_jaune_pensions.py",
    "test_pap_plf_2026.py", "test_opef_frais_per.py",
    # Les registres.
    "test_frontiere_contributive.py", "test_sources_a_explorer.py",
    "test_source_locale.py",
    # L'outillage du dépôt : l'index de la DILA, la publication sur main, ce
    # partage-ci, et le filet des déplacements (docs/architecture.md, § 12).
    "test_dila_index.py", "test_pousser.py", "test_niveaux.py",
    "test_conservation.py",
}

#: Les tests qui ne sont pas du niveau de leur fichier.
EXCEPTIONS = {
    # Les exemples officiels sont des règles, et la suite rapide les joue.
    ("test_oracle.py", "test_les_exemples_publies_par_les_caisses_sont_reproduits"): "rapide",
    ("test_oracle.py", "test_le_temoin_des_exemples_officiels_est_source"): "rapide",
    ("test_oracle.py", "test_un_ecart_connu_entre_et_ne_change_pas_en_silence"): "rapide",
    # Le portage JavaScript, rejoué contre le Python : deux moteurs.
    ("test_cumul_activites.py",
     "test_le_portage_javascript_concorde_sur_des_cumuls_tires_au_hasard"): "complet",
    ("test_releve_lu.py", "test_le_portage_javascript_lit_les_memes_releves"): "complet",
}


def niveau(fichier: str, test: str) -> str:
    """Le niveau d'un test, par son fichier et, au besoin, par son nom."""
    if (fichier, test) in EXCEPTIONS:
        return EXCEPTIONS[(fichier, test)]
    if fichier in COMPLETS:
        return "complet"
    if fichier in CONTROLES:
        return "controle"
    return "rapide"


def pytest_configure(config):
    for nom, sens in NIVEAUX.items():
        config.addinivalue_line("markers", f"{nom}: {sens}")


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config, items):
    """Marque chaque test de son niveau, avant que ``-m`` ne choisisse."""
    for item in items:
        nom = getattr(item, "originalname", None) or item.name
        item.add_marker(niveau(item.path.name, nom))
