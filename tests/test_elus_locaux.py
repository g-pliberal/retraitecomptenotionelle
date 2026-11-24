"""La fiche de l'affiliation des élus locaux (`elus_locaux_affiliation`).

Ses versions se coupent aux dates que ses textes nomment, et non à celles
que LEGI donne à leurs rédactions (note de décision 0009) :

- la loi n° 72-1201 affilie les maires et adjoints à l'Ircantec, « à partir
  du 1er janvier 1973 » (D. 2123-25 du CGCT) ;
- l'article 41 de la loi n° 92-108 applique son titre IV, la retraite des
  élus locaux, « depuis le 30 mars 1992 », au renouvellement des conseils
  généraux et régionaux (réponse ministérielle n° 334, JO AN du 2 août
  1993) ; LEGI date ses rédactions du 5 février 1992, jour de sa publication ;
- la loi n° 2002-276, publiée au Journal officiel du 28 février 2002,
  récrit le régime général des élus qui ont cessé leur activité ;
- le décret n° 2013-362 applique L. 382-31 du code de la sécurité sociale
  aux mandats « débutant à compter du 1er janvier 2013 », et à ceux en cours
  « au titre de la période du mandat postérieure à cette date » ;
- l'assujettissement sur demande, que l'article 23 de la loi n° 2023-270
  ajoute à L. 382-31, vaut pour les « pensions prenant effet à compter du
  1er septembre 2023 » (son IV), et le décret n° 2023-838 l'applique aux
  mandats « débutant à compter du 1er septembre 2023 », et à ceux en cours
  « au titre de la période postérieure à cette date » (son article 3) : deux
  dates qui décident, celle de la période et celle de la pension ;
- l'article 99 de la loi n° 2023-1250, publiée au Journal officiel du
  27 décembre 2023, l'ouvre au délégué d'un établissement de coopération
  intercommunale ; LEGI date la rédaction du lendemain.
"""

from __future__ import annotations

from datetime import date

import yaml

from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.noyau import carte

FICHE = "elus_locaux_affiliation"


def _fiche() -> dict:
    return carte.fiches()[FICHE]


def test_les_versions_des_elus_locaux_se_coupent_aux_dates_de_leurs_textes():
    periode, pension = "periode.debut", "liquidation.date_effet"
    septembre_2023 = date(2023, 9, 1)
    assert _fiche()["dates_qui_decident"] == [periode, pension]
    assert [version["bornes"] for version in _fiche()["versions"]] == [
        {periode: [None, date(1973, 1, 1)]},
        {periode: [date(1973, 1, 1), date(1992, 3, 30)]},
        {periode: [date(1992, 3, 30), date(2002, 2, 28)]},
        {periode: [date(2002, 2, 28), date(2013, 1, 1)]},
        {periode: [date(2013, 1, 1), septembre_2023]},
        # la pension prise avant septembre 2023 ne connaît pas la demande
        {periode: [septembre_2023, None], pension: [None, septembre_2023]},
        {periode: [septembre_2023, date(2023, 12, 28)], pension: [septembre_2023, None]},
        {periode: [date(2023, 12, 28), None], pension: [septembre_2023, None]},
    ]


def test_chaque_version_des_elus_locaux_garde_la_trace_de_sa_lecture():
    """Chaque texte cité l'est avec sa date de lecture et la citation exacte ;
    faute d'exemple officiel, la version dit ce qui a été cherché."""
    for version in _fiche()["versions"]:
        assert version.get("statut", "lue") == "lue", version["id"]
        assert version["textes"], version["id"]
        for texte in version["textes"]:
            assert texte.get("lu_le") and texte.get("citation"), (version["id"], texte)
        assert version["exemples"] == "aucun trouvé", version["id"]
        assert version["exemples_cherches"].strip(), version["id"]


def test_le_routage_de_l_elu_local_tombe_aux_bornes_de_la_fiche():
    """Le statut `elu_local` route l'Ircantec à compter de 1973 et le régime
    général, au-dessus de « la moitié du plafond » (D. 382-34), à compter de
    2013 : les années du modèle sont celles où les versions de la fiche
    commencent."""
    lu = yaml.safe_load((RACINE_DONNEES / "reference" / "legislation" / "affiliations.yaml")
                        .read_text(encoding="utf-8"))
    periodes = lu["affiliations"]["elu_local"]["periodes"]
    assert [(p["debut"], p["fin"], p["regimes"]) for p in periodes] == [
        (1973, 2012, ["ircantec"]),
        (2013, None, ["regime_general", "ircantec"]),
    ]
    assert periodes[1]["seuil_pass"] == {"regime_general": 0.5}
    debuts = [version["bornes"]["periode.debut"][0] for version in _fiche()["versions"]]
    assert date(1973, 1, 1) in debuts and date(2013, 1, 1) in debuts
