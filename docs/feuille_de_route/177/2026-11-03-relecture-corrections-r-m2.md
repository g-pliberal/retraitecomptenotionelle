# Relecture des corrections de R-M2 (file M2-bis)

File R-M2-bis, le 3 novembre 2026 : relecture indépendante des commits cc55cdd et 06e2e9a
(session M2-bis, note `2026-11-03-corrections-de-la-relecture-r-m2.md`), qui répondent à
la relecture R-M2 (`2026-11-03-relecture-assiette-du-rco.md`). Chaque source a été rouverte
ici, sans rien reprendre de la session ni de mémoire : les index LEGI et JORF de la DILA
récupérés et mis à jour (LEGI à jour au 2 novembre 2026, JORF au 3 novembre, aucun
incrément depuis) ; la table « ARTISANS : RCO - revenu de référence » de la caisse et la
série `salref_rc_com` de l'IPP, téléchargées le jour (sha256 fbce0850…c0b91a9 et
35cbc1b5…e703b6a1b, les empreintes que la session cite) ; les 633 exposés de la base de la
Cnav, servis le jour par `/api/v1/expose` (sha256 4a7a66c5…dc8421cb828). Rien n'a été
modifié : ni règle, ni donnée, ni test, ni fiche.

**Verdict.** La règle et ses bornes : **conforme** — le conjoint collaborateur à l'option
(une fraction du revenu du chef) cotise au RCO des artisans et au NRCO des commerçants, de
2007 à 2012, sur le revenu de l'avant-dernière année ; au forfait, sur le tiers du plafond
de l'année. Chaque citation est exacte, mot pour mot (les 48 fragments de citation de la
fiche, par un script) ; les quinze valeurs des tests, refaites à la main, aussi ; le
témoin, −21,3551 points et −0,19 % de pension, refait à la main ; les deux moteurs rendent
ces valeurs, les tests sont verts, sous les présomptions décalées aussi ; le paquet refait
ne change rien. Les quatre écarts de R-M2 et sa date sont chacun corrigés ou déclarés.
**Trois écarts faibles**, de documentation, sans effet sur aucune valeur : deux empreintes
de commit qui n'existent pas (point 8) ; le commentaire de `tests/test_cout.py` dit à tort
que la correction ne touche que les années d'avant 2009 (point 7) ; un témoin de page
bougé, que la note ne dit pas (point 5).

## 1. Les textes, à la version en vigueur

Lus dans l'index LEGI, par `dila_cherche.py legi --num … --le` et `--diff`, et pour les
décrets dans l'index du JORF :

| Texte | Version, en vigueur | Ce que la session en cite | Verdict |
|---|---|---|---|
| D. 635-10-2 | LEGIARTI000006738041, du 13 décembre 2006 au 1er janvier 2013 | « La cotisation d'assurance vieillesse complémentaire du conjoint collaborateur est calculée sur le revenu retenu, dans les limites [...], pour le calcul de sa cotisation d'assurance vieillesse de base. La cotisation d'assurance complémentaire ne fait toutefois pas l'objet de la régularisation à laquelle la cotisation d'assurance de base donne lieu le cas échéant. » ; les a) et b) des deux premières années | **conforme** |
| D. 633-19-1 | LEGIARTI000006737949, du 13 décembre 2006 | « sont définies et recouvrées dans les conditions prévues par la sous-section 1 de la présente section » | **conforme** ; l'index porte un autre D. 633-19-1 (LEGIARTI000029557626, 2008-2015), sur les majorations, sans rapport |
| D. 633-19-2 | LEGIARTI000006737951, du 13 décembre 2006 au 5 avril 2012 | le tiers du plafond (1°), 33,33 % ou 50 % du revenu du chef (2°, 3°), un tiers ou la moitié en partage (4°, 5°) | **conforme** ; la rédaction du 5 avril 2012 (LEGIARTI000025629841) ne change que « professionnel » en « d'activité » |
| D. 633-19-6 | LEGIARTI000006737955, du 13 décembre 2006 au 5 avril 2012 | « sur le revenu retenu pour le calcul des cotisations dues par le chef d'entreprise pour ces années » | **conforme** ; la rédaction de 2012 (LEGIARTI000025629836) n'ôte que « Par exception aux dispositions de l'article D. 633-6 » |
| L. 633-10 | LEGIARTI000006743702, du 3 août 2005 au 23 décembre 2011 | « Les cotisations sont définies conformément aux dispositions de l'article L. 131-6 et calculées dans la limite d'un plafond, dans des conditions déterminées par décret. » | **conforme** |
| L. 131-6 | LEGIARTI000006740121 (6 mars 2007 → 2009), LEGIARTI000020169101 (1er janvier → 29 mai 2009), LEGIARTI000020675442 (→ 23 décembre 2011) | « Elles sont calculées, à titre provisionnel, en pourcentage du revenu professionnel de l'avant-dernière année ou des revenus forfaitaires. Lorsque le revenu professionnel est définitivement connu, les cotisations font l'objet d'une régularisation. » | **conforme**, dans chacune des trois ; du 1er janvier au 6 mars 2007, LEGIARTI000006740120 dit de même (« Les cotisations sont calculées, chaque année, à titre provisionnel [...] ») ; le journal de la session la nomme, la note et la fiche non : sans effet |
| L. 131-6-2 et L. 633-10, en 2012 | LEGIARTI000025013725 ; LEGIARTI000025013919, du 23 décembre 2011 | « Elles sont calculées, à titre provisionnel, en pourcentage du revenu d'activité de l'avant-dernière année » ; L. 633-10 renvoie à « L. 131-6, L. 131-6-1 et L. 131-6-2 » | **conforme** |
| D. 635-7 | LEGIARTI000006738025 (2004-2008) : « fixé à 7 % » ; LEGIARTI000017869802, LEGIARTI000025091410, LEGIARTI000025629857 (2008-2012) : « 1° 7,2 % pour la part du revenu professionnel n'excédant pas le plafond » | 7 % en 2007, 7,2 % de 2010 à 2012 | **conforme** |
| Décret n° 2007-1900, article 1er, III | JORFARTI000017765872 | « le taux de la cotisation annuelle prévue au 1° de l'article D. 635-7 est fixé à 7 % au titre de l'année 2008 et à 7,1 % au titre de l'année 2009 » | **conforme** |
| D. 635-10 | LEGIARTI000006738028 (2005-2009), LEGIARTI000020032165 (2009-2012), et en 2012 LEGIARTI000025091405, LEGIARTI000025629850 | « fixé à 6,5 % » | **conforme** |
| D. 633-2 | LEGIARTI000006737877 à LEGIARTI000006737879, de 1985 au 5 avril 2012 | « 200 fois le montant horaire du salaire minimum de croissance en vigueur le 1er janvier de l'année considérée » | **conforme**, dans les trois ; la rédaction du 5 avril 2012 (LEGIARTI000025629830) passe à « 5,25 % de la valeur » du plafond |
| D. 635-2 | LEGIARTI000020032159, du 29 décembre 2008 au 5 avril 2012 | « suivant les modalités prévues au cinquième alinéa de l'article L. 131-6 » | **conforme** |

Les citations de la fiche `assiette_rco_independants` ont été comparées au texte de
l'index par un script, fragment par fragment entre les « [...] » : 48 fragments, 48
trouvés. Les revenus de référence : la table de la caisse, « Mis à jour le 14/06/2012 »,
donne 4,145 € en 2007, 4,207 € en 2008, 4,500 € en 2009, 4,692 € en 2010, 4,79053 € en
2011, 4,89113 € en 2012 ; l'IPP, 14,648 € au 1er janvier 2007, 14,809 € au 1er décembre
2008, 15,3 € au 1er avril 2009, 15,483 € au 1er avril 2010, 15,808 € au 1er avril 2011,
16,14 € au 1er avril 2012 : ceux des tests et de `valeurs_point.csv`. Les plafonds :
2 682 € par mois en 2007 (arrêté du 15 novembre 2006, JORFARTI000001856457), soit
32 184 € ; 33 276 € « par année » en 2008 (arrêté du 30 octobre 2007, JORFARTI000001910321).

## 2. Les bornes, 2007 et 2012

*2012.* La rédaction de D. 635-10-2 du 1er janvier 2013 (LEGIARTI000025263590), lue mot à
mot (`--diff`), ôte « La cotisation d'assurance complémentaire ne fait toutefois pas
l'objet de la régularisation à laquelle la cotisation d'assurance de base donne lieu le cas
échéant » : dès 2013, la complémentaire suit la cotisation de base régularisée, celle de
l'année. Les cotisations de 2012 sont les dernières sur l'avant-dernière année : la borne
est **conforme**.

*2007.* D. 635-10-2 naît du décret n° 2006-1580 du 11 décembre 2006, article 4
(JORFARTI000001720946), en vigueur le 13 décembre 2006 ; le modèle n'affilie le conjoint
au RCO et au NRCO que de 2007 à 2012 (`affiliations.yaml`, ses périodes de 2007 à 2012), ce
que la session n'a pas touché. Les données posent la clé `conjoint_collaborateur_*: 2` dès
les périodes qui commencent en 2005 (`rco_artisans`, 2005 à 2007 ; `nric`, 2005 à 2008),
mais aucune ligne du conjoint n'y entre avant 2007 : sans effet, la règle s'applique des
cotisations de 2007 à celles de 2012. **Conforme.** Celle de 2007 lit la ligne de 2005, où
le conjoint cotisait à l'assurance volontaire, que L. 742-9 (LEGIARTI000006744141, jusqu'au
3 août 2006) permettait de fixer « à une fraction du revenu professionnel du chef
d'entreprise » : la lecture se tient, l'écart d'une autre fraction étant déclaré.

## 3. Ce que les textes disent de l'option

Le texte qui l'ouvre : la loi, L. 633-10 (LEGIARTI000006743702) — « Les cotisations du
conjoint collaborateur mentionné à l'article L. 121-4 du code de commerce sont calculées, à
sa demande : 1° Soit sur un revenu forfaitaire ou sur un pourcentage du revenu
professionnel du chef d'entreprise ; 2° Soit, avec l'accord du chef d'entreprise, sur une
fraction du revenu professionnel de ce dernier » —, puis D. 633-19-2, ses cinq assiettes.
L'assiette : une fraction du revenu du chef. L'année de revenu : celle de la cotisation de
base, que D. 633-19-1 et L. 633-10 renvoient à L. 131-6, provisionnelle sur l'avant-dernière
année puis régularisée ; D. 635-10-2 assied la complémentaire sur le revenu de la base sans
la régularisation. Elle reste donc sur la fraction du revenu du chef de l'avant-dernière
année, de 2007 à 2012, après 2009 encore. **Conforme** au code des deux moteurs : la ligne à
l'option lit le revenu de ses lignes à l'option deux ans plus tôt (`revenu_a_l_option`,
`revenuALOption`), la ligne au forfait (`forfait_conjoint`) garde le sien. Les deux jumeaux
sont écrits ligne pour ligne, la marque du forfait posée au même endroit
(`carriere.py`, `_ligne_annuelle` ; `carriere.js`, après `assietteDuConjointCollaborateur`).

## 4. Les valeurs des tests, refaites à la main

Points = assiette × taux ÷ revenu de référence, en fractions exactes :

| Cas | Assiette | Taux | Référence | À la main | Note de la session |
|---|---|---|---|---|---|
| conjoint d'artisan à l'option, 2007 | 10 000 € (2005) | 7 % | 4,145 | 168,87817 | 168,8782 |
| 2008 | 11 000 € (2006) | 7 % | 4,207 | 183,02829 | 183,0283 |
| 2009 | 12 000 € (2007) | 7,1 % | 4,500 | 189,33333 | 189,3333 |
| 2010 | 13 000 € (2008) | 7,2 % | 4,692 | 199,48849 | 199,4885 |
| 2011 | 14 000 € (2009) | 7,2 % | 4,79053 | 210,41513 | 210,4151 |
| 2012 | 15 000 € (2010) | 7,2 % | 4,89113 | 220,80787 | 220,8079 |
| au forfait puis à l'option, 2007 | 32 184 / 3 € | 7 % | 4,145 | 181,17250 | 181,1725 |
| 2008 | 33 276 / 3 € | 7 % | 4,207 | 184,55907 | 184,5591 |
| 2009 | 14 000 € (l'année) | 7,1 % | 4,500 | 220,88889 | 220,8889 |
| 2010 | 15 000 € (l'année) | 7,2 % | 4,692 | 230,17903 | 230,1790 |
| 2011 | 14 000 € (2009) | 7,2 % | 4,79053 | 210,41513 | 210,4151 |
| conjoint de commerçant à l'option, 2007 | 10 000 € (2005) | 6,5 % | 14,648 | 44,37466 | 44,3747 |
| 2008 | 11 000 € (2006) | 6,5 % | 14,809 | 48,28145 | 48,2815 |
| 2009 | 12 000 € (2007) | 6,5 % | 15,3 | 50,98039 | 50,9804 |
| 2010 | 13 000 € (2008) | 6,5 % | 15,483 | 54,57599 | 54,5760 |

Toutes **conformes**. Le rouge que la note rapporte, 202,6538 points en 2007 sur le revenu
de l'année, est bien 12 000 × 7 % ÷ 4,145 (non rejoué sur l'ancien code). Une remarque,
déjà relevée par R-M2 et hors du travail relu : l'IPP donne 14,648 € jusqu'au
30 novembre 2008 et 14,809 € au 1er décembre ; le test prend le second pour 2008, comme
`valeurs_point.csv`, et la fiche dit les deux dates.

## 5. Le témoin, refait à la main

`conjoint_collaborateur_au_tiers` : les revenus de ses lignes du conjoint de commerçant, que
la saisie donne (lus par `Saisies().lire`, `tests/outils_pont.py`), puis le NRCO à 6,5 % sur
les références de l'IPP, très loin des trois plafonds :

| Année | Revenu de l'année | Revenu de l'avant-dernière | Référence | Avant | Après |
|---|---|---|---|---|---|
| 2007 | 15 583,0853 | 14 600,2664 | 14,648 | 69,1494 | 64,7882 |
| 2008 | 16 024,3171 | 15 153,2766 | 14,809 | 70,3343 | 66,5111 |
| 2009 | 16 265,9813 | 15 583,0853 | 15,3 | 69,1038 | 66,2026 |
| 2010 | 16 817,5536 | 16 024,3171 | 15,483 | 70,6027 | 67,2725 |
| 2011 | 17 216,7058 | 16 265,9813 | 15,808 | 70,7924 | 66,8831 |
| 2012 | 17 569,9560 | 16 817,5536 | 16,14 | 70,7588 | 67,7287 |
| Total | | | | 420,7414 | 399,3863 |

−21,3551 points, −5,076 % : **conforme** aux 399,39 et 420,74 de la note, et aux points que
le moteur Python crédite, année par année, à 10⁻⁴ près. Le témoin sert ces points à
1,469061 € (« 399.39 points × valeur de service 1.469061 € », avant comme après) :
−21,3551 × 1,469061 = −31,37 €, et sa pension du scénario 1 passe de 16 687,32 à
16 655,95 € (−0,188 %) ; aux scénarios 3 et 5 (`notionnel_prospectif`, `…_employeur`),
de 14 146,41 à 14 118,41 € (−0,198 %) : **conforme** aux −0,19 et −0,20 % de la note. La
valeur de service projetée en 2031 n'est pas l'objet du travail relu, et ne change pas.

*Un témoin sur 930* : des témoins de simulation, `conjoint_collaborateur_au_tiers` seul
bouge entre cc55cdd^ et cc55cdd, **conforme**. *L'écart, faible* : un témoin de page bouge
aussi, `simuler_conjoint_collaborateur` (conjointe d'artisan à la moitié du revenu du chef
depuis 2010 : sa ligne de 2012 lit celle de 2010), de 1 237 à 1 236 € par mois, et la note
ne le dit pas. La grille du coût n'a aucun conjoint (`castypes.py`) : l'écart au COR ne
peut pas bouger, **conforme**.

## 6. Les deux moteurs et les tests

`tests/test_independants.py` entier : 52 réussis, dont le nouveau test, qui confronte les
deux moteurs. Le lot rapide : 4 242 réussis, 6 sautés. La confrontation du jumeau aux
témoins (`tests/test_pont.py -k refait`) : verte. Sous `PRESOMPTIONS_DECALEES=1`, le
fichier rend 38 réussis et 14 sautés : les tests qui confrontent le Python au portage sont
sautés par construction (`tests/conftest.py`, `pytest_collection_modifyitems`), le nouveau
compris. Le moteur Python seul a donc été rejoué ici sous les présomptions décalées
(`_decaler_les_presomptions`), sur les trois cas du test : les quinze valeurs, identiques à
10⁻⁴ près. La règle ne lit ni naissance, ni enfants, ni mariage.

## 7. La marge de `tests/test_cout.py`

Les tolérances ne bougent pas (9 et 12 %), **conforme** à « inchangée ». Le commentaire
ajouté, comparé au code : l'écart compare la croissance de la dépense « de la dernière
année observée à l'horizon » à celle du COR (`_ecarts_par_groupe`, `depuis =
comptes.derniere_annee_observee`, `modele / attendu - 1.0`), **conforme** ; les
non-salariés sont `msa_non_salaries`, `cnavpl`, `cnbf`, et `rci` est parmi les
complémentaires (`GROUPES_DU_MODELE`, `donnees/equilibre.py`), où vont `rco_artisans` et
`nric` (`integre_dans: rci`), **conforme** ; le calage multiplie le coefficient de chaque
cas type « par la moyenne des corrections de ses groupes, pondérée par ce qu'il y touche »,
puis ramène les poids « à la somme qu'ils avaient » (`_poids_par_groupe`, `cout.py`),
**conforme** ; +8,1703 et +11,2390 % après le conjoint, la grille n'en ayant pas,
**conforme**.

*L'écart, faible* : « la correction ne touche que les années d'avant 2009 » est inexact.
Les forfaits de début valent jusqu'en 2011 (D. 635-7, LEGIARTI000017869802), et la grille
du coût en sert : l'artisan y commence à 24 ans (`castypes.py`, `age_debut=24`), dans les
générations de 1880 à 2020, de cinq en cinq (`cout.py`, `PREMIERE_GENERATION`,
`PAS_GENERATIONS`) ; celui de 1985 commence en 2009, au forfait en 2009 et 2010, pour une
pension servie en 2049, qui pèse à l'horizon et non au départ. L'explication tient pour
l'essentiel (l'avant-dernière année et le 0,10 %, avant 2009 ; les forfaits, de −0,029 et
−0,045 point en tout selon R-M2), mais la phrase est à corriger : « d'avant 2009 pour
l'essentiel, les forfaits jusqu'en 2011 ». R-M2 écrivait déjà « la correction porte sur
les années d'avant 2009 ».

## 8. Les quatre écarts de R-M2, et sa date

- *5, a) le conjoint à une fraction du revenu du chef* : **corrigé** dans les deux
  moteurs (points 3 à 6) et ses approximations déclarées (point 9).
- *5, b) le forfait de l'artisan de 2009 à 2011* : **déclaré**, dans les approximations
  de la fiche (`version: [regularisation_2009]`, les citations de D. 635-7, D. 635-2 et
  L. 131-6 exactes) et dans `docs/limites/3-systeme-actuel.md` (« aucun texte lu ne dit
  si ce forfait l'était »).
- *4, la marge* : **expliquée**, à la phrase près (point 7).
- *6, l'effet décrit à moitié* : **écrit** dans l'effet de la fiche et dans la note du
  travail (`2026-11-03-etape-9-assiette-du-rco-ecrite.md`, un paragraphe daté, ajouté sans
  rien réécrire). Refait sur les témoins d'eab4dae (avant le
  travail, parent de f716130) et de 144a622 : `dispense_rsa_releve_artisane`, 1 242,32
  puis 1 470,04 points du RCO (+18,3 %) ; total contributif du scénario 1, 1 340,77 puis
  1 420,54 € (+5,9 %) ; pension du scénario 1, 12 742,23 € les deux fois ; scénarios 3 et
  5, 1 469,66 puis 1 554,90 € (+5,8 %) : **conforme**.
- *5, c) la date* : « jusqu'au 5 avril 2012 », **corrigée** (point 1, D. 633-2).

*L'écart, faible : deux empreintes mortes.* La note écrit « corrigé (8f5447b) » et
« Mesuré ici sur les témoins de e24714d (avant le travail) » ; le journal de veille de la
session, « (8f5447b) ». Ni l'un ni l'autre n'est un objet du dépôt (`git cat-file`) : le
commit publié est cc55cdd, et la mesure d'avant se refait sur eab4dae, aux mêmes chiffres.
Sans doute des commits locaux d'avant le rebasage ; la preuve écrite n'y renvoie pas moins
à rien.

## 9. Ce que le texte ne tranche pas : déclaré ?

Déclarés dans les approximations de la fiche, à la version de 2004 à 2012 : la ligne qui
manque ou est au forfait deux ans plus tôt — les deux premières années (D. 633-19-6), le
passage du forfait à l'option —, dont le revenu du chef manque au modèle ; les forfaits de
D. 635-7 du conjoint qui débute dans l'une des deux premières années de l'artisan
(D. 635-10-2, a et b) ; le changement de fraction ; les acomptes sur le revenu estimé
(L. 131-6, « sur la base des revenus de cette année estimés par l'assuré », texte vérifié).
La limite publiée en dit les deux premiers cas, la fiche tous : **conforme**. Le négatif de
la caisse, « Aucun des 633 exposés de la base de la Cnav ne traite cette complémentaire » :
**conforme** — des 633 exposés servis le jour, dix nomment le conjoint collaborateur, et
aucun ne dit l'assiette de sa complémentaire (le seul passage qui rapproche les deux mots,
« Affiliation des travailleurs indépendants », parle des droits de conjoint avant 2004).

Une remarque, sans gravité : D. 633-19-7 (LEGIARTI000006737957) assied le conjoint, quand
le chef n'a pas déclaré son revenu, sur le revenu de la cotisation provisoire du chef
(D. 633-4) ; la fiche ne le dit pas, mais le modèle ne connaît nulle part la déclaration
manquante.

## 10. Le paquet

Sur le dernier `main` (7c45287), `python scripts/construire_donnees.py` (trois minutes) :
`git status` vide, rien ne change. **Conforme.**

## Ce qui reste

Trois retouches de documentation, faibles, à la session qui reprendra l'action : la phrase
de `tests/test_cout.py` (« d'avant 2009 pour l'essentiel, les forfaits jusqu'en 2011 ») ;
les empreintes 8f5447b et e24714d, à dire cc55cdd et eab4dae dans un ajout daté ; le témoin
de page `simuler_conjoint_collaborateur`, à nommer. Aucune ne touche une valeur.
