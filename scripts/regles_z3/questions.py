"""Les propriétés posées à Z3, toutes de la même forme : des hypothèses qui
décrivent un CONTRE-EXEMPLE (Z3 en cherche un ; s'il n'en trouve aucun, la
propriété est prouvée sur tout son champ), et les champs qui le situent — une
date, une génération, des trimestres —, sur lesquels un cas attendu se
déclare (`tests/cliquets_de_justesse/proprietes_attendues.yaml`).

Un champ est de genre ``mois`` (écrit ``AAAA-MM``), ``jour`` (``AAAA-MM-JJ``)
ou ``entier``. Les propriétés sont celles des deux essais du 21 novembre 2026,
moins celles que l'essai a jugées mal posées (« naître plus tard n'avance
jamais la carrière longue », vraie pour qui a passé l'âge)."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import z3

from . import duree as _duree, fiches as _fiches
from .calcul import AUCUN, Z3, age_ecrit, entier_du_jour, gen, jour_lu, mois_lu
from .pension import Modele, date_effet


@dataclass
class Propriete:
    id: str
    titre: str
    hypotheses: list
    champs: dict                       # nom -> (terme Z3, genre)
    lire: Callable = field(repr=False)  # modèle -> le contre-exemple, en clair


def val(mod, e) -> int:
    return mod.eval(e, model_completion=True).as_long()


def _m(mod, e) -> str:
    return mois_lu(val(mod, e))


# ------------------------------------------------------------- durée requise
def de_la_duree(versions, pratique) -> list[Propriete]:
    rg = _duree.regle(versions, Z3, pratique)
    g, g1, g2, d, d1, d2 = z3.Ints("g g1 g2 d d1 d2")
    # Les générations de la table et d'avant : la table s'arrête à 2099, et le
    # moteur oppose sa valeur par défaut au-delà.
    GEN = lambda x: z3.And(gen(1800, 1) <= x, x < gen(2100, 1))

    def valide(x):
        """Une vraie date AAAAMMJJ (le 29 février laissé de côté)."""
        jj, mm = x % 100, x / 100 % 100
        return z3.And(jj >= 1, mm >= 1, mm <= 12, x >= 10000101,
                      jj <= z3.If(mm == 2, 28, z3.If(z3.Or(mm == 4, mm == 6, mm == 9, mm == 11), 30, 31)))

    j = lambda mod, x: jour_lu(val(mod, x))
    return [
        Propriete(
            "duree.naitre_plus_tard",
            "Durée requise : à date d'effet égale, naître plus tard ne l'abaisse jamais",
            [GEN(g1), GEN(g2), g1 < g2, valide(d), rg(g1, d) > rg(g2, d)],
            {"date_effet": (d, "jour"), "ne_avant": (g1, "mois"), "ne_apres": (g2, "mois")},
            lambda mod: (f"pension du {j(mod, d)} : né en {_m(mod, g1)}, {val(mod, rg(g1, d))} "
                         f"trimestres ; né en {_m(mod, g2)}, {val(mod, rg(g2, d))}")),
        Propriete(
            "duree.partir_plus_tard",
            "Durée requise : à génération égale, partir plus tard ne l'abaisse jamais",
            [GEN(g), valide(d1), valide(d2), d1 < d2, rg(g, d1) > rg(g, d2)],
            {"ne": (g, "mois"), "avant": (d1, "jour"), "apres": (d2, "jour")},
            lambda mod: (f"né en {_m(mod, g)} : pension du {j(mod, d1)}, {val(mod, rg(g, d1))} "
                         f"trimestres ; du {j(mod, d2)}, {val(mod, rg(g, d2))}")),
    ]


# ------------------------------------------------- couverture des dates
def de_la_couverture(F) -> list[Propriete]:
    """Toute fiche datée par la seule date d'effet : une version et une seule
    pour chaque jour, de l'an 1 à l'an 9999. Les autres (datées aussi par
    l'âge atteint, l'année du revenu…) sont hors du champ."""
    jour = z3.Int("jour")
    props = []
    for nom, fiche in sorted(F.items()):
        vs = [v for v in fiche["versions"] if v.get("exception_de") is None]
        if not all(set(v["bornes"]) == {"liquidation.date_effet"} for v in vs):
            continue
        bornes = [tuple(entier_du_jour(x) for x in v["bornes"]["liquidation.date_effet"]) for v in vs]
        compte = z3.Sum([z3.If(z3.And(*([a <= jour] if a else []), *([jour < b] if b else [])), 1, 0)
                         for a, b in bornes])
        props.append(Propriete(
            f"couverture.{nom}",
            f"Fiche {nom} : une version et une seule pour chaque date d'effet",
            [10101 <= jour, jour <= 99991231, compte != 1],
            {"date_effet": (jour, "jour")},
            lambda mod, compte=compte: (f"le {jour_lu(val(mod, jour))} tombe dans "
                                        f"{val(mod, compte)} version(s)")))
    return props


# --------------------------------------------- âge légal, âge du taux plein
GEN = lambda x: z3.And(gen(1900, 1) <= x, x < gen(2011, 1))
DATE = lambda x: z3.And(gen(1945, 1) <= x, x < gen(2100, 1))
DEPUIS_1983 = lambda x: z3.And(gen(1983, 4) <= x, x < gen(2100, 1))


def ouvert(R, gg, dd):
    """La personne née au mois gg a-t-elle, au 1er du mois dd, l'âge que la
    version de ce jour lui oppose (ses âges comptés du mois qui suit sa naissance) ?"""
    a = R(gg, dd)
    return z3.And(a != AUCUN, dd >= gg + 1 + a)


def _monotonies(R, cle, nom, domaine) -> list[Propriete]:
    g, g1, g2, d, D1, D2 = z3.Ints(f"{cle}_g {cle}_g1 {cle}_g2 {cle}_d {cle}_D1 {cle}_D2")
    a = lambda mod, x, y: age_ecrit(val(mod, R(x, y)))
    premier = lambda gg, DD: z3.And(domaine(DD), ouvert(R, gg, DD), z3.Not(ouvert(R, gg, DD - 1)))
    return [
        Propriete(f"{cle}.naitre_plus_tard", f"{nom} : à date fixe, naître plus tard ne le baisse jamais",
                  [GEN(g1), GEN(g2), g1 < g2, domaine(d), R(g2, d) != AUCUN, R(g1, d) > R(g2, d)],
                  {"date_effet": (d, "mois"), "ne_avant": (g1, "mois"), "ne_apres": (g2, "mois")},
                  lambda mod: (f"pension du 1er {_m(mod, d)} : né en {_m(mod, g1)}, {a(mod, g1, d)} ; "
                               f"né en {_m(mod, g2)}, {a(mod, g2, d)}")),
        Propriete(f"{cle}.version_suivante",
                  f"{nom} : à génération fixe, la version du mois suivant ne le baisse jamais",
                  [GEN(g), domaine(d), R(g, d + 1) < R(g, d), R(g, d + 1) != AUCUN],
                  {"ne": (g, "mois"), "date_effet": (d + 1, "mois")},
                  lambda mod: (f"né en {_m(mod, g)} : pension du 1er {_m(mod, d)}, {a(mod, g, d)} ; "
                               f"du 1er {_m(mod, d + 1)}, {a(mod, g, d + 1)}")),
        Propriete(f"{cle}.reste_atteint", f"{nom} : une fois atteint, il le reste le mois suivant",
                  [GEN(g), domaine(d), ouvert(R, g, d), z3.Not(ouvert(R, g, d + 1))],
                  {"ne": (g, "mois"), "date_effet": (d + 1, "mois")},
                  lambda mod: (f"né en {_m(mod, g)} : atteint au 1er {_m(mod, d)} ({a(mod, g, d)}), "
                               f"plus au mois suivant ({a(mod, g, d + 1)})")),
        Propriete(f"{cle}.plus_age_aussi",
                  f"{nom} : quand un plus jeune l'a atteint, un plus âgé l'a atteint aussi",
                  [GEN(g1), GEN(g2), g1 < g2, domaine(d), ouvert(R, g2, d), z3.Not(ouvert(R, g1, d))],
                  {"date_effet": (d, "mois"), "ne_avant": (g1, "mois"), "ne_apres": (g2, "mois")},
                  lambda mod: (f"1er {_m(mod, d)} : né en {_m(mod, g2)} l'a atteint, "
                               f"né en {_m(mod, g1)} non")),
        Propriete(f"{cle}.age_de_la_personne",
                  f"{nom} : l'âge de la personne (celui de la version sous laquelle elle "
                  "l'atteint) ne baisse jamais quand elle naît plus tard",
                  [GEN(g1), GEN(g2), g1 < g2, premier(g1, D1), premier(g2, D2), R(g1, D1) > R(g2, D2)],
                  {"ne_avant": (g1, "mois"), "ne_apres": (g2, "mois")},
                  lambda mod: (f"né en {_m(mod, g1)} : {a(mod, g1, D1)} (le 1er {_m(mod, D1)}) ; "
                               f"né en {_m(mod, g2)} : {a(mod, g2, D2)} (le 1er {_m(mod, D2)})")),
    ]


def des_ages(F) -> list[Propriete]:
    L, T = _fiches.age_legal(Z3, F), _fiches.age_taux_plein(Z3, F)
    g, d = z3.Ints("ages_g ages_d")
    ne_date = {"ne": (g, "mois"), "date_effet": (d, "mois")}
    props = [Propriete("age_legal.defini", "Âge légal : toute génération de 1900 à 2010 en a un, à toute date",
                       [GEN(g), DATE(d), L(g, d) == AUCUN], ne_date,
                       lambda mod: f"né en {_m(mod, g)}, pension du 1er {_m(mod, d)}")]
    props += _monotonies(L, "age_legal", "Âge légal", DATE)
    props += [
        Propriete("taux_plein.muette_avant_1983",
                  "Âge du taux plein : la fiche ne se tait qu'avant le 1er avril 1983",
                  [GEN(g), DEPUIS_1983(d), T(g, d) == AUCUN], ne_date,
                  lambda mod: f"né en {_m(mod, g)}, pension du 1er {_m(mod, d)}"),
        Propriete("taux_plein.jamais_avant_l_age_legal",
                  "Âge du taux plein : jamais avant l'âge légal de la même date",
                  [GEN(g), DEPUIS_1983(d), T(g, d) < L(g, d)], ne_date,
                  lambda mod: (f"né en {_m(mod, g)}, 1er {_m(mod, d)} : taux plein "
                               f"{age_ecrit(val(mod, T(g, d)))}, âge légal {age_ecrit(val(mod, L(g, d)))}")),
        Propriete("taux_plein.cinq_ans_au_plus_apres_l_age_legal",
                  "Âge du taux plein : jamais plus de cinq ans après l'âge légal, pour qui "
                  "peut partir sans l'avoir",
                  [GEN(g), DEPUIS_1983(d), ouvert(L, g, d), z3.Not(ouvert(T, g, d)), T(g, d) - L(g, d) > 60],
                  ne_date,
                  lambda mod: (f"né en {_m(mod, g)}, 1er {_m(mod, d)} : âge légal "
                               f"{age_ecrit(val(mod, L(g, d)))}, taux plein {age_ecrit(val(mod, T(g, d)))}")),
    ]
    props += _monotonies(T, "taux_plein", "Âge du taux plein", DEPUIS_1983)
    return props


# --------------------------------------------------------- carrière longue
def de_la_carriere_longue(F) -> list[Propriete]:
    """Seuls les âges : chaque porte s'ouvre à qui a commencé avant la fin de
    l'année de sa borne d'entrée, TOUTES SES DURÉES RÉUNIES. L'âge de la
    carrière longue d'une borne est le plus petit âge qu'ouvrent les portes de
    borne au moins égale, que la personne passe toutes."""
    L = _fiches.age_legal(Z3, F)
    DEPUIS_2004 = lambda x: z3.And(gen(2004, 1) <= x, x < gen(2100, 1))
    bornes = sorted({c[0] for c in _fiches.cles_des_portes(F)})
    props = []
    for borne in bornes:
        B = _fiches.meilleur_age(Z3, F, borne)
        g, g1, g2, d = z3.Ints(f"cl{borne}_g cl{borne}_g1 cl{borne}_g2 cl{borne}_d")
        a = lambda mod, x, y, B=B: age_ecrit(val(mod, B(x, y)))
        props += [
            Propriete(f"carriere_longue.avant_{borne}_ans.plus_age_aussi",
                      f"Carrière longue, débuts avant {borne} ans : quand un plus jeune peut "
                      "partir, un plus âgé le peut aussi (par la carrière longue ou l'âge légal)",
                      [GEN(g1), GEN(g2), g1 < g2, DEPUIS_2004(d), ouvert(B, g2, d),
                       z3.Not(ouvert(B, g1, d)), z3.Not(ouvert(L, g1, d))],
                      {"date_effet": (d, "mois"), "ne_avant": (g1, "mois"), "ne_apres": (g2, "mois")},
                      lambda mod, g1=g1, g2=g2, d=d, a=a: (
                          f"1er {_m(mod, d)} : né en {_m(mod, g2)} part à {a(mod, g2, d)} ; "
                          f"né en {_m(mod, g1)} ne peut pas (porte : {a(mod, g1, d)})")),
            Propriete(f"carriere_longue.avant_{borne}_ans.depart_reste_ouvert",
                      f"Carrière longue, débuts avant {borne} ans : un départ ouvert le reste "
                      "le mois suivant (ou l'âge légal prend le relais)",
                      [GEN(g), DEPUIS_2004(d), ouvert(B, g, d), z3.Not(ouvert(B, g, d + 1)),
                       z3.Not(ouvert(L, g, d + 1))],
                      {"ne": (g, "mois"), "date_effet": (d + 1, "mois")},
                      lambda mod, g=g, d=d, a=a: (
                          f"né en {_m(mod, g)} : départ ouvert au 1er {_m(mod, d)} ({a(mod, g, d)}), "
                          f"fermé au 1er {_m(mod, d + 1)} ({a(mod, g, d + 1)})")),
        ]
    return props


# ------------------------------------------------------------------ pension
def de_la_pension(M: Modele) -> list[Propriete]:
    g, m, m1, m2, T, T2 = z3.Ints("p_g p_m p_m1 p_m2 p_T p_T2")

    def voir(mod, mx, Tx, avec_surcote=True):
        p, x = M.pension(g, mx, Tx, avec_surcote)
        ev = lambda e: mod.eval(e, model_completion=True)
        age = val(mod, mx - g)
        texte = (f"le 1er {_m(mod, mx)} à {age // 12} ans {age % 12} mois, {val(mod, Tx)} trim. : "
                 f"requis {val(mod, x['requis'])}, décote {val(mod, x['n'])} trim.")
        if avec_surcote:
            texte += f", surcote {float(ev(x['surcote']).as_fraction()) * 100:.4g} %"
        return texte + f" -> {float(ev(p).as_fraction()) * 100:.4g} % du SAM"

    p0, _ = M.pension(g, m, T)
    p1, _ = M.pension(g, m, T + 1)
    sans_a, _ = M.pension(g, m1, T, False)
    sans_b, _ = M.pension(g, m2, T, False)
    travail = T2 == T + (m2 / 3 - m1 / 3)          # un trimestre par trimestre civil achevé
    pa, _ = M.pension(g, m1, T)
    pb, xb = M.pension(g, m2, T2)
    sa, _, _ = M.surcote(g, m1, T, M.rg(g, date_effet(m1)))
    deux = lambda mod, avec=True, T2_=T2: (f"né en {_m(mod, g)} | {voir(mod, m1, T, avec)} | "
                                           f"{voir(mod, m2, T2_, avec)}")
    plus_tard = {"ne": (g, "mois"), "depart": (m1, "mois"), "report": (m2, "mois"),
                 "trimestres": (T, "entier")}
    return [
        Propriete("pension.trimestre_de_plus",
                  "Pension : un trimestre de plus ne la baisse jamais (surcote comprise)",
                  [M.admis(g, m, T), p1 < p0],
                  {"ne": (g, "mois"), "date_effet": (m, "mois"), "trimestres": (T, "entier")},
                  lambda mod: f"né en {_m(mod, g)} | {voir(mod, m, T)} | {voir(mod, m, T + 1)}"),
        Propriete("pension.partir_plus_tard_meme_duree",
                  "Pension hors surcote : partir plus tard avec la même durée ne la baisse jamais",
                  [M.admis(g, m1, T), m1 < m2, sans_b < sans_a], plus_tard,
                  lambda mod: deux(mod, False, T)),
        Propriete("pension.partir_plus_tard_en_travaillant",
                  "Pension : partir plus tard en continuant de travailler ne la baisse jamais",
                  [M.admis(g, m1, T), m1 < m2, travail, pb < pa], plus_tard,
                  lambda mod: deux(mod)),
        Propriete("pension.un_mois_de_plus_depuis_2004",
                  "Pension : depuis 2004, un mois de plus au travail ne la baisse jamais",
                  [M.admis(g, m1, T), m1 >= gen(2004, 1), m2 == m1 + 1, travail, pb < pa], plus_tard,
                  lambda mod: deux(mod)),
        Propriete("pension.surcote_acquise",
                  "Surcote : un changement de version ne baisse jamais la surcote déjà acquise",
                  [M.admis(g, m1, T), m1 >= gen(2004, 1), m2 == m1 + 1, travail,
                   M.rg(g, date_effet(m1)) == M.rg(g, date_effet(m2)), xb["surcote"] < sa], plus_tard,
                  lambda mod: deux(mod)),
    ]


# ------------------------------------------- les renvois des régimes, au jour
def _effet(periode) -> tuple:
    """Les jours que la période liquide, comme `Periode.effet` du moteur :
    `date_effet`, sinon ses années ; en entiers AAAAMMJJ, la fin exclue."""
    bornes = periode.get("date_effet")
    if bornes:
        return tuple(entier_du_jour(b) for b in bornes)
    fin = periode.get("fin")
    return periode["debut"] * 10000 + 101, None if fin is None else (fin + 1) * 10000 + 101


def _jour_valide(x):
    """Une vraie date AAAAMMJJ (le 29 février laissé de côté)."""
    jj, mm = x % 100, x / 100 % 100
    return z3.And(jj >= 1, mm >= 1, mm <= 12,
                  jj <= z3.If(mm == 2, 28, z3.If(z3.Or(mm == 4, mm == 6, mm == 9, mm == 11), 30, 31)))


def des_renvois_des_regimes(racine, regimes_lus=None) -> list[Propriete]:
    """Chaque renvoi d'un régime qui cite son texte (`textes_des_renvois`, note
    0009, étape 4) vaut au jour cité : la période qui l'ouvre liquide depuis ce
    jour, celle d'avant jusqu'à la veille, et une seule période liquide chaque
    jour, de la période d'avant à la fin du renvoi. Lu dans les fichiers de
    régime, comme les cliquets (`tests/outils_droit_date.py`)."""
    if regimes_lus is None:
        from retraite_notionnelle.donnees import regimes as _regimes
        regimes_lus = [(f["code"], list(f.get("periodes") or []))
                       for _, f in _regimes.fichiers_de_regimes(Path(racine) / "data")]
    jour = z3.Int("jour")
    props = []
    for code, periodes in regimes_lus:
        effets = [_effet(p) for p in periodes]
        dans_p = [z3.And(*([a <= jour] if a else []), *([jour < b] if b else [])) for a, b in effets]
        compte = z3.Sum([z3.If(x, 1, 0) for x in dans_p])
        for i, periode in enumerate(periodes):
            for champ, cite in sorted((periode.get("textes_des_renvois") or {}).items()):
                cible = periode.get(champ)
                if cible is None or (i and periodes[i - 1].get(champ) == cible):
                    continue
                depuis = entier_du_jour(cite["depuis"])
                j = i
                while j + 1 < len(periodes) and periodes[j + 1].get(champ) == cible:
                    j += 1
                fin = effets[j][1]
                debut = effets[i - 1][0] if i else depuis - 10000
                porte = z3.Or(*[dans_p[k] for k in range(len(periodes))
                                if periodes[k].get(champ) == cible])
                props.append(Propriete(
                    f"renvoi.{code}.{champ}",
                    f"{code} : le renvoi `{champ}` vaut depuis le {cite['depuis']} ({cite['id']}), "
                    "une seule période chaque jour",
                    [debut <= jour, *([jour < fin] if fin else [jour <= 99991231]), _jour_valide(jour),
                     z3.Or(porte != (jour >= depuis), compte != 1)],
                    {"date_effet": (jour, "jour")},
                    lambda mod, porte=porte, compte=compte, depuis=depuis: (
                        f"pension du {jour_lu(val(mod, jour))} : "
                        f"{'renvoi' if z3.is_true(mod.eval(porte, model_completion=True)) else 'sans renvoi'}"
                        f" (cité depuis le {jour_lu(depuis)}), {val(mod, compte)} période(s)")))
    return props


def catalogue(racine, extrait) -> list[Propriete]:
    F = _fiches.charger(racine)
    versions = _duree.lire_versions(racine)
    return (de_la_couverture(F) + de_la_duree(versions, extrait["durees_avant_le_decret"])
            + des_ages(F) + de_la_carriere_longue(F)
            + de_la_pension(Modele(racine, extrait, versions, F))
            + des_renvois_des_regimes(racine))
