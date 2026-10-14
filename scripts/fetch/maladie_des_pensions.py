"""La cotisation maladie des pensions des régimes de base que l'IPP n'écrit pas.

Importé par ``ipp_prelevements_sociaux.py``, qui écrit ces séries dans
``data/reference/legislation/prelevements_historiques.yaml`` à côté de celles de
l'IPP (action 138, étape 9, septième et huitième parties).

POURQUOI. La branche du régime général de l'IPP n'a que la cotisation maladie
des pensions du régime général et des complémentaires, et sa branche des
indépendants celle de leurs retraités. Les autres régimes de base prélevaient la
leur, de 1976 ou de 1980 à 1997, et deux régimes spéciaux la prélèvent encore.
Chaque série est lue dans les index JORF et LEGI de la DILA (``dila_index.py``),
version par version.

CE QUE DIT CHAQUE MARCHE. ``texte`` cite le texte qui fixe le taux, le texte
modificatif d'abord, que l'ancrage relie au Journal officiel ; ``lu`` nomme les
documents de l'index — un article de LEGI, un article ou une notice du JORF — et
les mots qu'un test y relit quand l'index est là
(``tests/test_prelevements_historiques.py``) ; le script ne l'écrit pas dans la
donnée. Une série naît à sa première marche : ce qui la précède n'est pas lu, et
le dépôt n'y prélève rien.

TROIS CONVENTIONS, qui sont celles de toute l'histoire des pensions. Un taux par
tranches, ou borné par un plafond, est celui d'une pension sous le premier
plafond — la SNCF prélevait 3,60 % puis 2,25 % au-delà de 109 040 F et de
163 560 F par an en 1996, et prélève aujourd'hui 0,70 % sous 5 128 € par
trimestre, rien au-delà. Les exonérations des retraités non imposables et le
taux réduit d'un exploitant soigné par un autre régime ne jouent pas : le dépôt
prélève au taux plein. Un taux s'applique aux pensions dues à sa date, même
quand la caisse les paie par trimestre et d'avance, sauf quand le texte dit
autrement : les IEG et la SNCF au 1er octobre 1996.

CE QUI N'EST PAS LU. Les décrets annuels de l'assurance maladie des exploitants
de 1980 à 1989 et celui de 1993 (n° 93-1153), que l'index n'a qu'en notice ; les
taux que les conseils de la SNCF, de la RATP et de la Banque de France fixaient
avant le 1er juillet 1991 ; celui des mines avant le 1er juillet 1988, que
l'arrêté du 27 octobre 1972 fixait et que l'arrêté du 30 juin 1987 relève, à
3 % selon LEGI, à 3,4 % selon la notice du JORF ; la cotisation des pensionnés
des chemins de fer secondaires avant 60 ans (2,5 %, puis 2,9 % en 1987, décret
n° 50-1448, article 6), que le dépôt ne distingue pas de celle d'après ; les
pensions de la SEITA, du port autonome de Strasbourg, des marins, des cultes,
des assemblées et du Conseil économique, social et environnemental. La
cotisation de la SNCF et celle des mines, qui courent encore, ne sont pas sur la
fiche de paie du site (``prelevements_remuneration.yaml``).
"""

from __future__ import annotations

#: Chaque série de la maladie des pensions lue aux textes : ses marches, de la
#: plus ancienne à la plus récente.
PENSIONS_LUES_AUX_TEXTES: dict[str, list[dict]] = {}

#: LA FONCTION PUBLIQUE — État, militaires, ouvriers de l'État, collectivités
#: locales —, précomptée dans la limite du plafond : D. 712-39, D. 713-16 et
#: l'article 3 du décret n° 67-850, que LEGI date du 30 septembre 1976. Avant
#: le décret n° 76-896, son taux n'est pas lu, et le plafond n'est pas appliqué.
PENSIONS_LUES_AUX_TEXTES["maladie_fonction_publique"] = [
    {"depuis": "1976-10-01", "taux": 0.0225,
     "texte": "Décret 76-896 du 29/09/1976 (JORFTEXT000000861798) : décret 67-850 du "
              "30/09/1967, art. 3 (LEGIARTI000006770629)",
     "lu": (("LEGIARTI000006770629", "ou à leurs familles, est fixé à 2,25 p. 100"),)},
    {"depuis": "1988-07-01", "taux": 0.0265,
     "texte": "Décret 88-795 du 22/06/1988 (JORFTEXT000000693584) : CSS, D. 712-39 et D. 713-16 ; "
              "décret 67-850, art. 3",
     "lu": (("LEGIARTI000006770630", "ou à leurs familles, est fixé à 2,65 p. 100"),
            ("JORFTEXT000000693584", "VERSES A COMPTER DU 01-07-1988"))},
    {"depuis": "1996-03-01", "taux": 0.0305,
     "texte": "Décret 96-155 du 28/02/1996, art. 1 et 2 (JORFTEXT000000557800)",
     "lu": (("JORFARTI000001149353", "pour les pensions dues à compter du 1er mars 1996"),)},
    {"depuis": "1997-01-01", "taux": 0.028,
     "texte": "Décret 96-1151 du 26/12/1996, art. 10 : CSS, D. 712-39 (LEGIARTI000006739102) ; "
              "décret 67-850, art. 3 (LEGIARTI000006770632)",
     "lu": (("LEGIARTI000006739102", "ou à leur famille est fixé à 2,80 p. 100"),)},
    {"depuis": "1998-01-01", "taux": 0.0,
     "texte": "Décret 97-1249 du 29/12/1997, art. 4, 9 et 17 : CSS, D. 712-39 "
              "(LEGIARTI000006739103) et décret 67-850, art. 3, les seuls non-résidents",
     "lu": (("JORFARTI000001906463", "Les cotisations dues par les fonctionnaires de l'Etat "
                                     "retraités ou leurs ayants cause, en application du "
                                     "deuxième alinéa de l'article L. 131-7-1"),)},
]

#: LES EXPLOITANTS AGRICOLES, sur leur pension de base (code rural, art. 1106-6-1,
#: II) : la part technique de la cotisation, 2,8 %, et sa part complémentaire,
#: 1 %, que chaque décret annuel du financement de leur protection sociale
#: refixe, en 1990, 1991, 1992, 1994, 1995 et 1996 ; celui de 1993
#: (n° 93-1153), que l'index n'a qu'en notice, est tenu. Un point de moins en
#: 1997, contre un point de CSG ; rien depuis 1998, hors des non-résidents. La
#: réduction de 20 % du retraité soigné par un autre régime ne joue pas.
PENSIONS_LUES_AUX_TEXTES["maladie_exploitants"] = [
    {"depuis": "1990-01-01", "taux": 0.038,
     "texte": "Décret 90-765 du 28/08/1990, art. 7 et 9 (2,8 % et 1 %), puis 91-912, 92-793, "
              "94-715, 95-1038 et 96-679",
     "lu": (("JORFARTI000001121684", "est égale à 2,80 p. 100 du montant annuel des avantages "
                                     "de vieillesse agricoles perçus"),
            ("JORFARTI000001158321", "1 p. 100 du montant annuel des avantages de vieillesse "
                                     "agricoles perçus"),
            ("JORFARTI000001568435", "est égale à 2,8 p. 100 du montant annuel"),
            ("JORFARTI000001960028", "est égale à 2,8 p. 100 du montant annuel"),
            ("JORFARTI000001769527", "1 p. 100 du montant annuel des avantages de vieillesse"),
            ("JORFARTI000001971431", "est égale à 2,8 p. 100 du montant annuel"),
            ("JORFARTI000001005619", "1 p. 100 du montant annuel des avantages de vieillesse"),
            ("JORFARTI000001013202", "est égale à 2,8 p. 100 du montant annuel"),
            ("JORFARTI000002378319", "1 p. 100 du montant annuel des avantages de vieillesse"),
            ("JORFARTI000001362068", "est égale à 2,8 p. 100 du montant annuel"),
            ("JORFARTI000001897324", "1 p. 100 du montant annuel des avantages de vieillesse"))},
    {"depuis": "1997-01-01", "taux": 0.028,
     "texte": "Décret 97-140 du 13/02/1997, art. 1 à 3 (1,8 % et 1 %)",
     "lu": (("JORFARTI000001924846", "est égale à 1,8 % du montant annuel des avantages de "
                                     "vieillesse agricoles perçus"),
            ("JORFARTI000001409844", "1 % du montant annuel des avantages de vieillesse "
                                     "agricoles servis par le régime obligatoire"),
            ("JORFARTI000001797766", "s'appliquent aux pensions dues à compter du 1er janvier "
                                     "1997"))},
    {"depuis": "1998-01-01", "taux": 0.0,
     "texte": "Décret 97-1252 du 29/12/1997, art. 7 et 13 : les seuls non-résidents",
     "lu": (("JORFARTI000002398867", "par les personnes mentionnées au deuxième alinéa de "
                                     "l'article L. 131-7-1 du code de la sécurité sociale"),
            ("JORFARTI000001346386", "pensions et allocations versés à compter du 1er janvier "
                                     "1998"))},
]

#: LES RÉGIMES SPÉCIAUX PLACÉS SOUS LE RÉGIME GÉNÉRAL pour la maladie (L. 711-2,
#: R. 711-8 puis D. 711-3) : l'Opéra de Paris, la Comédie-Française et, passé
#: 60 ans, les chemins de fer secondaires, que la notice du décret n° 96-680
#: énumère avec les IEG. Le relèvement de 1987, temporaire, est reconduit en
#: 1988 (n° 88-789) et repris par D. 711-3 en 1991 (n° 91-613, art. 2) ; celui
#: de 3,80 % que le décret n° 96-680 prévoyait au 1er juillet 1997 devient 2,80 %
#: (n° 96-1151). Depuis 1998, D. 711-3 ne prélève plus que 1 % des
#: complémentaires, déjà dans leur série.
PENSIONS_LUES_AUX_TEXTES["maladie_regimes_speciaux"] = [
    {"depuis": "1980-07-31", "taux": 0.015,
     "texte": "Décret 80-598 du 30/07/1980, art. 1",
     "lu": (("LEGIARTI000006761316", "est fixé à 1,5 p. 100 des avantages de retraite"),)},
    {"depuis": "1987-07-01", "taux": 0.019,
     "texte": "Décret 87-466 du 30/06/1987, art. 1, puis décret 88-789 du 22/06/1988 : CSS, R. 711-8",
     "lu": (("LEGIARTI000006770390", "est porté à 1,9 p. 100 en ce qui concerne les avantages "
                                     "de vieillesse versés à compter du 1er juillet 1987"),
            ("LEGIARTI000006752901", "est fixé à 1,9 p. 100 des avantages de retraite"),
            ("LEGIARTI000006772629", "versés à compter du 1er juillet 1988"))},
    {"depuis": "1996-08-01", "taux": 0.0285,
     "texte": "Décret 96-680 du 31/07/1996, art. 1 : CSS, D. 711-3",
     "lu": (("JORFARTI000002089418", "pour les avantages de retraite dus à compter du 1er août "
                                     "1996"),)},
    {"depuis": "1997-01-01", "taux": 0.0185,
     "texte": "Décret 96-1151 du 26/12/1996, art. 3 : CSS, D. 711-3",
     "lu": (("JORFARTI000001216371", "1,85 p. 100 >> à compter du 1er janvier 1997"),)},
    {"depuis": "1997-07-01", "taux": 0.028,
     "texte": "Décret 96-1151 du 26/12/1996, art. 3 : CSS, D. 711-3",
     "lu": (("JORFARTI000001216371", "2,80 p. 100 >> à compter du 1er juillet 1997"),)},
    {"depuis": "1998-01-01", "taux": 0.0,
     "texte": "Décret 97-1249 du 29/12/1997, art. 2 et 17 : CSS, D. 711-3, les seules "
              "complémentaires",
     "lu": (("JORFARTI000002001439", "Les avantages de retraite complémentaire servis aux "
                                     "pensionnés des régimes spéciaux"),
            ("JORFARTI000001032378", "pensions et allocations versés à compter du 1er janvier "
                                     "1998"))},
]

#: LES INDUSTRIES ÉLECTRIQUES ET GAZIÈRES : leurs taux, fixés à part en 1980
#: (n° 80-916), puis ceux de D. 711-3, que leur statut national leur applique
#: depuis le 1er juillet 1991 (n° 91-613, art. 9). Leurs pensions étant payées
#: par trimestre et d'avance, le relèvement de 1996 prend effet au 1er octobre
#: (notice du décret n° 96-680).
PENSIONS_LUES_AUX_TEXTES["maladie_ieg"] = [
    {"depuis": "1980-11-22", "taux": 0.015,
     "texte": "Décret 80-916 du 20/11/1980, art. 1",
     "lu": (("LEGIARTI000006770300", "est fixé à 1,50 %"),)},
    {"depuis": "1987-07-01", "taux": 0.019,
     "texte": "Décret 87-466 du 30/06/1987, art. 2, puis décret 88-789 du 22/06/1988 : décret "
              "80-916, art. 1",
     "lu": (("LEGIARTI000006770391", "est porté à 1,9 p. 100 en ce qui concerne les avantages "
                                     "de vieillesse versés à compter du 1er juillet 1987"),
            ("LEGIARTI000006770301", "est fixé à 1,90 %"))},
    {"depuis": "1991-07-01", "taux": 0.019,
     "texte": "Décret 91-613 du 28/06/1991, art. 9 : statut national, art. 23 ; CSS, D. 711-3",
     "lu": (("JORFARTI000000988628", "Les dispositions des articles R.711-15 et D.711-3 du code "
                                     "de la sécurité sociale sont applicables aux titulaires "
                                     "d'un avantage de vieillesse"),)},
    {"depuis": "1996-10-01", "taux": 0.0285,
     "texte": "Décret 96-680 du 31/07/1996, art. 1, et sa notice : au 4e trimestre",
     "lu": (("JORFARTI000002089418", "pour les avantages de retraite dus à compter du 1er août "
                                     "1996"),
            ("JORFTEXT000000734595", "LE 1ER RELEVEMENT DE TAUX DE COTISATION PRENDRA "
                                     "CONCRETEMENT EFFET AU 01-10-1996"))},
    {"depuis": "1997-01-01", "taux": 0.0185,
     "texte": "Décret 96-1151 du 26/12/1996, art. 3 : CSS, D. 711-3",
     "lu": (("JORFARTI000001216371", "1,85 p. 100 >> à compter du 1er janvier 1997"),)},
    {"depuis": "1997-07-01", "taux": 0.028,
     "texte": "Décret 96-1151 du 26/12/1996, art. 3 : CSS, D. 711-3",
     "lu": (("JORFARTI000001216371", "2,80 p. 100 >> à compter du 1er juillet 1997"),)},
    {"depuis": "1998-01-01", "taux": 0.0,
     "texte": "Décret 97-1249 du 29/12/1997, art. 2, 14 et 17 : CSS, D. 711-3",
     "lu": (("JORFARTI000002398865", "La couverture des prestations en nature du régime "
                                     "général d'assurance maladie et maternité est assurée par "
                                     "une cotisation à la charge des entreprises"),)},
]

#: LA SNCF : la cotisation de ses pensionnés à sa caisse de prévoyance (décret du
#: 6 août 1938, art. 3, § 6 bis, puis décret n° 2007-1056, art. 7, IV), sur la
#: part de la pension sous le premier plafond que fixe son conseil. Au-delà,
#: 3,60 % puis 2,25 % en 1991, relevés au 1er octobre 1996 et en 1997 ; rien
#: depuis 1998, quand la première tranche garde 0,70 %, sous 5 128 € par
#: trimestre aujourd'hui. Avant 1991, le taux était celui du règlement de la
#: caisse, que le décret ne chiffre pas.
PENSIONS_LUES_AUX_TEXTES["maladie_sncf"] = [
    {"depuis": "1991-07-01", "taux": 0.045,
     "texte": "Décret 91-613 du 28/06/1991, art. 8 : décret du 06/08/1938, art. 3, § 6 bis",
     "lu": (("JORFARTI000001370701", "1o 4,50 p. 100 du montant de la pension de retraite "
                                     "inférieur à un plafond fixé par le conseil "
                                     "d'administration"),)},
    {"depuis": "1997-01-01", "taux": 0.035,
     "texte": "Décret 96-1151 du 26/12/1996, art. 12 : décret du 06/08/1938, art. 3, § 6 bis",
     "lu": (("LEGIARTI000006776178", "1° 3,50 % du montant de la pension de retraite inférieur "
                                     "à un plafond"),)},
    {"depuis": "1998-01-01", "taux": 0.007,
     "texte": "Décret 97-1249 du 29/12/1997, art. 11, puis décret 2007-1056, art. 7, IV "
              "(LEGIARTI000052041125)",
     "lu": (("JORFARTI000001608705", "est fixé à 0,70 % du montant de la pension de retraite "
                                     "inférieur à un plafond fixé par le conseil "
                                     "d'administration"),
            ("LEGIARTI000052041125", "est fixé à 0,70 % du montant trimestriel de la pension "
                                     "inférieur à un plafond fixé à 5 128 euros"))},
]

#: LA RATP : la part des pensionnés de la contribution à sa caisse de
#: coordination, dans la limite du plafond de la sécurité sociale (décret
#: n° 50-1566, art. 12), que son conseil fixait avant le 1er juillet 1991 ; la
#: régie seule depuis 1998.
PENSIONS_LUES_AUX_TEXTES["maladie_ratp"] = [
    {"depuis": "1991-07-01", "taux": 0.0165,
     "texte": "Décret 91-613 du 28/06/1991, art. 11 : décret 50-1566, art. 12",
     "lu": (("JORFARTI000001760109", "1,65 p. 100 à la charge des titulaires de ces "
                                     "avantages"),)},
    {"depuis": "1996-08-01", "taux": 0.0285,
     "texte": "Décret 96-680 du 31/07/1996, art. 3 : décret 50-1566, art. 12",
     "lu": (("JORFARTI000001748197", "2,85 p. 100 >> à compter du 1er août 1996"),)},
    {"depuis": "1997-01-01", "taux": 0.0185,
     "texte": "Décret 96-1151 du 26/12/1996, art. 14 : décret 50-1566, art. 12",
     "lu": (("JORFARTI000001410284", "1,85 p. 100 >> à compter du 1er janvier 1997"),)},
    {"depuis": "1997-07-01", "taux": 0.028,
     "texte": "Décret 96-1151 du 26/12/1996, art. 14 : décret 50-1566, art. 12",
     "lu": (("JORFARTI000001410284", "2,80 p. 100 >> à compter du 1er juillet 1997"),)},
    {"depuis": "1998-01-01", "taux": 0.0,
     "texte": "Décret 97-1249 du 29/12/1997, art. 13 : décret 50-1566, art. 12",
     "lu": (("JORFARTI000001414164", "est assurée par une contribution à la charge de la "
                                     "régie"),)},
]

#: LA BANQUE DE FRANCE : sa cotisation des prestations en nature (décret
#: n° 91-613, art. 13), que la Banque fixait avant le 1er juillet 1991 ; depuis
#: 1998, les seuls agents détachés à l'étranger.
PENSIONS_LUES_AUX_TEXTES["maladie_banque_de_france"] = [
    {"depuis": "1991-07-01", "taux": 0.0265,
     "texte": "Décret 91-613 du 28/06/1991, art. 13, I, 2°",
     "lu": (("JORFARTI000002342227", "2o 2,65 p. 100 pour les titulaires d'un avantage de "
                                     "retraite au titre de ce régime spécial"),)},
    {"depuis": "1996-08-01", "taux": 0.0305,
     "texte": "Décret 96-680 du 31/07/1996, art. 4 : décret 91-613, art. 13",
     "lu": (("JORFARTI000001896731", "3,05 p. 100 >> pour les avantages de retraite dus à "
                                     "compter du 1er août 1996"),)},
    {"depuis": "1997-01-01", "taux": 0.0205,
     "texte": "Décret 96-1151 du 26/12/1996, art. 15 : décret 91-613, art. 13",
     "lu": (("JORFARTI000001216376", "2,05 p. 100 >> à compter du 1er janvier 1997"),)},
    {"depuis": "1997-07-01", "taux": 0.028,
     "texte": "Décret 96-1151 du 26/12/1996, art. 15 : décret 91-613, art. 13",
     "lu": (("JORFARTI000001216376", "2,80 p. 100 >> à compter du 1er juillet 1997"),)},
    {"depuis": "1998-01-01", "taux": 0.0,
     "texte": "Décret 97-1249 du 29/12/1997, art. 15 : décret 91-613, art. 13",
     "lu": (("JORFARTI000002488777", "qui sont détachées à l'étranger sans être rémunérées"),)},
]

#: LES CLERCS ET EMPLOYÉS DE NOTAIRES : la cotisation que leur caisse précompte
#: sur leurs pensions (décrets n° 80-600 et 85-1093, puis décret n° 91-613,
#: art. 4), abrogée en 1998. Le relèvement de 1987, temporaire, est reconduit en
#: 1988 (n° 88-791) ; celui de 3,80 % que le décret n° 96-471 prévoyait en 1997
#: devient 2,80 % (n° 96-1151).
PENSIONS_LUES_AUX_TEXTES["maladie_crpcen"] = [
    {"depuis": "1980-07-31", "taux": 0.015,
     "texte": "Décret 80-600 du 30/07/1980, art. 2",
     "lu": (("LEGIARTI000006761325", "est fixé à 1,5 p. 100 du montant des arrérages de la "
                                     "pension"),)},
    {"depuis": "1986-01-01", "taux": 0.0225,
     "texte": "Décret 85-1093 du 11/10/1985, art. 18 et 19",
     "lu": (("LEGIARTI000006768805", "est fixé à 2,25 p. 100 du montant des arrérages de la "
                                     "pension"),
            ("LEGIARTI000006768807", "aux pensions versées aux clercs et employés retraités à "
                                     "compter du 1er janvier 1986"))},
    {"depuis": "1987-07-01", "taux": 0.0265,
     "texte": "Décret 87-467 du 30/06/1987, art. 2, puis décret 88-791 du 22/06/1988, art. 2",
     "lu": (("LEGIARTI000006770394", "est porté à 2,65 p. 100"),
            ("LEGIARTI000006772884", "est porté à 2,65 p. 100"),
            ("JORFARTI000001760108", "par le régime spécial des clercs et employés de notaires "
                                     "est fixé à 2,65 p. 100"))},
    {"depuis": "1996-06-01", "taux": 0.0305,
     "texte": "Décret 96-471 du 31/05/1996, art. 6 : décret 91-613, art. 4",
     "lu": (("JORFARTI000002311144", "3,05 p. 100 >> pour les avantages de retraite dus à "
                                     "compter du 1er juin 1996"),)},
    {"depuis": "1997-01-01", "taux": 0.028,
     "texte": "Décret 96-1151 du 26/12/1996, art. 15 : décret 91-613, art. 4",
     "lu": (("JORFARTI000001216376", "<< 15,35 p. 100 >> et << 2,80 p. 100 >>"),)},
    {"depuis": "1998-01-01", "taux": 0.0,
     "texte": "Décret 97-1249 du 29/12/1997, art. 16 : décret 91-613, art. 4, 4°, abrogé",
     "lu": (("JORFARTI000001032377", "Le 4o de l'article 4 et l'article 16-1 du décret du 28 "
                                     "juin 1991 susvisé"),)},
]

#: LES MINES : la cotisation des pensionnés du régime minier (décret n° 46-2769,
#: art. 53, puis art. 91, 3°, a), à leur charge exclusive depuis 1993. Avant le
#: 1er juillet 1988, un arrêté de 1972 que l'index n'a qu'en notice, et un
#: relèvement de 1987 dont LEGI et la notice ne disent pas le même taux. Celui
#: de 4,30 % que le décret n° 96-471 prévoyait en 1997 devient 3,30 %
#: (n° 96-1151) ; 0,50 % depuis 1998, toujours.
PENSIONS_LUES_AUX_TEXTES["maladie_mines"] = [
    {"depuis": "1988-07-01", "taux": 0.034,
     "texte": "Arrêté du 22/06/1988, art. 1 (JORFTEXT000000318381) : décret 46-2769, art. 53",
     "lu": (("LEGIARTI000006785739", "Pour les pensions versées à compter du 1er juillet 1988, "
                                     "le taux de la cotisation prévue à l'article 53 du décret "
                                     "du 27 novembre 1946 est porté à 3,4 p. 100"),
            ("LEGIARTI000006764778", "est fixé à 3,4 p. 100"))},
    {"depuis": "1996-06-01", "taux": 0.0385,
     "texte": "Décret 96-471 du 31/05/1996, art. 4 : décret 46-2769, art. 91",
     "lu": (("JORFARTI000002180039", "3,85 p. 100 >> pour les avantages, prestations et "
                                     "allocations dus à compter du 1er juin 1996"),)},
    {"depuis": "1997-01-01", "taux": 0.033,
     "texte": "Décret 96-1151 du 26/12/1996, art. 13 : décret 46-2769, art. 91",
     "lu": (("JORFARTI000001023416", "<< 4,30 p. 100 >> et << 5,5 p. 100 >> sont remplacés "
                                     "respectivement par les termes : << 3,30 p. 100 >>"),)},
    {"depuis": "1998-01-01", "taux": 0.005,
     "texte": "Décret 97-1249 du 29/12/1997, art. 12 : décret 46-2769, art. 91 "
              "(LEGIARTI000037456798)",
     "lu": (("JORFARTI000001420042", "a) De 0,50 % pour"),
            ("LEGIARTI000037456798", "a) De 0,50 % pour"))},
]

#: Les régimes dont chaque série de pensions prélève la part, hors des
#: complémentaires (``maladie_complementaire`` de ``prelevements_remuneration.yaml``).
#: Le régime des salariés agricoles suit celui du régime général, taux pour taux :
#: 1 % en 1980 (décret n° 80-481), 1,4 % en 1987 (n° 87-453), 2,6 % en 1996
#: (n° 95-1401), 2,8 % en 1997 (n° 96-1167), rien depuis 1998 (n° 97-1252). La
#: cotisation des retraités indépendants ne porte que sur leur pension de base
#: (D. 612-3), celle des exploitants aussi (code rural, art. 1106-6-1, II). Les
#: droits en points d'avant 1973 des artisans et des commerçants sont une pension
#: de base (L. 634-3 ; action 138, étape 18).
REGIMES_DES_PENSIONS = {
    "maladie_regime_general": ("regime_general", "msa_salaries"),
    "maladie_fonction_publique": ("fonction_publique_etat", "cnracl", "fspoeie"),
    "maladie_independants": ("cancava", "cancava_avant_1973", "organic",
                             "organic_avant_1973", "cnavpl", "cnbf"),
    "maladie_exploitants": ("msa_non_salaries",),
    "maladie_regimes_speciaux": ("opera_de_paris", "comedie_francaise", "chemins_fer_secondaires"),
    "maladie_ieg": ("ieg",),
    "maladie_sncf": ("sncf",),
    "maladie_ratp": ("ratp",),
    "maladie_banque_de_france": ("banque_de_france",),
    "maladie_crpcen": ("crpcen",),
    "maladie_mines": ("mines",),
}


def a_ecrire(marche: dict) -> dict:
    """La marche telle que la donnée l'écrit : sans ce que le test relit."""
    return {cle: valeur for cle, valeur in marche.items() if cle != "lu"}
