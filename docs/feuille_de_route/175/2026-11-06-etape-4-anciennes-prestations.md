# Étape 4, thème « Anciennes prestations » : les exposés et leurs références

**Reprise, au 6 novembre 2026.** « Retraite personnelle de base », les huit thèmes de
« Carrière », « Avantages liés au décès de l'assuré », « Allocation du minimum », « RCI » et
« Anciennes prestations » sont rangés, ce dernier par cette note (H12). Suivant : « Régimes
intégrés » (29 exposés), sous la convention de la note du premier thème. La base se relit par
l'API hors de 5 h–6 h UTC. Restent à lire avec leur thème : les listes d'accords, de l'Union et
de l'Espace économique européens, et 9 références que seule lie la liste des personnes qui
relèvent des règlements ; les quatre exposés mahorais du décès, avec « Mayotte ». Aux sessions
du modèle : le candidat et le point non tranché de cette note ; ceux de H11, de H10, de H9, de
H8 ; ceux des notes des majorations et des thèmes précédents ; l'activité accessoire (H6) ;
l'AVPF du père (H7).

**Le 6 novembre 2026, ce qui est fait.**

- *La relecture de la base.* Par l'API, le 6 novembre 2026 de 13 h 19 à 13 h 20 UTC, par
  `_obtenir` et `_fenetre` de `scripts/fetch/cnav_legislation.py`, sans écrire le registre
  par le script : `/expose`, `/liste`, les trois collections des fenêtres, `/mises-a-jour`,
  sans aucun lien du site SharePoint de la caisse. Les 29 exposés sont servis à la date que
  le registre porte (`dateModification`, du 24 octobre 2025 à 6 h 47, 6 h 52, 6 h 58 ou
  7 h 25 UTC), les 3 fenêtres à lire aussi (9 août 2023 et 2 juin 2023).
  `python scripts/veille_droit.py` : rien de changé dans le thème (un exposé d'un autre thème
  a changé de date, `prelevement_retraite_cotisation_assurance_maladie_ex.aspx`).
- *La lecture* : les 29 exposés, en entier, par cette session — l'allocation supplémentaire
  (7), l'allocation aux mères de famille (4), l'allocation aux vieux travailleurs salariés (4),
  la majoration de L. 814-2 (6), la majoration pour conjoint à charge (3), la rente des
  assurances sociales, les retraites ouvrières et paysannes, le secours viager (3) —, les 3
  fenêtres et les 2 listes à lire. Chacun confronté aux fiches `minimum_vieillesse`,
  `residence_et_minimum_vieillesse`, `majoration_conjoint_a_charge`, `minimum_contributif`
  (lignes 644 à 649), aux régimes `avts`, `assurances_sociales` et
  `retraites_ouvrieres_paysannes` (`data/reference/regimes/`), à la série
  `legislation/minimum_vieillesse_avant_2007.csv`, et au code des deux moteurs :
  `condition_de_residence`, `avant_l_aspa` et `foyer_et_net`
  (`src/retraite_notionnelle/droit/foyer.py`, lignes 135, 176 et 211, la porte de la
  résidence lignes 238 à 242) et `conditionDeResidence`, `avantLAspa`, `foyerEtNet`
  (`moteur/js/droit/foyer.js`, lignes 116, 167 et 197, la porte lignes 216 à 219). Les
  textes, à l'index LEGI à jour au 2 novembre 2026 : L. 814-2 (sept rédactions, de 1985 à
  2006 ; LEGIARTI000006745108, 1990-1992), D. 814-2 (LEGIARTI000006739551, 1999-2007),
  D. 814-9 (LEGIARTI000006739756, 1991-1999), R. 816-2 (LEGIARTI000006753370, en vigueur
  le 30 mars 1993). Les cas ont été calculés par `avant_l_aspa`, sur les lignes 1990 et 2000
  de la série.
- *Le rapprochement de l'index* (LEGI à jour au 2 novembre 2026, JORF au 3). Les exposés
  lient 347 fois Légifrance, sous 163 identifiants. 146 se trouvent à l'index : 111 articles
  de LEGI, chacun concordant avec son ancre par son numéro, sauf trois ancres fautives (plus
  bas) ; 6 textes de LEGI et 29 du JORF, chacun concordant par son numéro et sa date, sauf un
  (plus bas). 17 sont absents : 8 articles et un texte de codes que l'index ne garde pas
  (code civil, articles 171, 516 à 529, 870, 871, 873 et 2134 ; code général des impôts, 669 ;
  code de l'action sociale et des familles, L. 132-8 ; code de la famille et de l'aide
  sociale, 146) ; 7 textes du JORF, que l'index n'a ni par l'identifiant, ni par le numéro ou
  la date du titre (loi n° 49-1095, décrets n° 46-1662, 72-788 et 80-866, arrêtés du 9 avril
  1971 et du 25 février 1976, loi du 30 juin 1956) ; le décret n° 82-307, lié sous
  LEGITEXT000006063740, absent, que le JORF a sous JORFTEXT000000701321.
- *Les sorts*, sous la convention de la note du premier thème. 29 exposés `limite` :
  l'allocation supplémentaire, l'allocation aux vieux travailleurs salariés et la majoration
  de L. 814-2 à `minimum_vieillesse` et à la limite, avec `residence_et_minimum_vieillesse`
  pour les trois qui en disent la résidence et pour les règlements européens ; l'allocation
  aux mères de famille et le secours viager à la limite seule ; la majoration pour conjoint à
  charge à sa fiche et à la limite ; la rente des assurances sociales à
  `minimum_contributif`, qui dit que le modèle ne la connaît pas, et à la limite ; les
  retraites ouvrières et paysannes à leur régime, hors du champ, et à
  `ecarts-au-droit-positif.md`, qui dit leur rente non servie. 3 fenêtres : la liste des
  conventions qui autorisent l'exportation de l'allocation aux vieux travailleurs salariés et
  de l'allocation aux mères de famille, `limite` (`residence_et_minimum_vieillesse`, la
  limite) ; « Hypothèque » et « Nantissement », du lexique, `hors_modele`. Les 2 listes des
  ressources exclues de l'allocation supplémentaire, la même en deux classements, `limite`
  (`minimum_vieillesse`, qui ne compte que les pensions, et la limite). Les 3 listes des
  règlements européens restent à lire, avec leur thème, comme les thèmes précédents les ont
  laissées ; les 11 fenêtres et 3 listes déjà rangées, et les 10 avis `hors_modele`, restent
  tels.
- *Les références*, des exposés, fenêtres et listes rangés ici qui les lient, sans les
  barèmes ni les avis : 162 rangées `limite`, aux renvois de ces objets ; 45 déjà `limite`
  dont le renvoi s'étend (ci-dessous) ; 77 qui les portaient déjà. Les 10 `branche` et les 6
  `hors_modele` restent telles. Restent `a_lire` 59 que seuls lient des barèmes et des avis,
  et 9 que seule lie la liste des personnes qui relèvent des règlements européens.
- *Les renvois qui s'étendent* (45 références). `minimum_vieillesse` et
  `residence_et_minimum_vieillesse` (15) : circulaires Cnav 20/74, 82/74, 65/72, 31/75,
  105/88, 79/89, 42/90, 22/99, 34/98, 2012/44, ministérielles 67/SS du 13 juin 1962,
  du 6 décembre 1991 et 99/06 du 7 janvier 1999, lettre ministérielle du 16 janvier 1963,
  diffusion 2002/5 ; les deux et la limite (4) : circulaire Cnav 65/76, lettres Cnav du
  21 juillet 1997, ministérielles du 2 décembre 1965 et du 6 janvier 1987 ;
  `residence_et_minimum_vieillesse` seule : circulaire ministérielle 85/SS du 27 juillet
  1956 ; `minimum_vieillesse` seule (5) : circulaires Cnav 2006/6, 2013/42, 2014/39,
  ministérielle 28/SS du 25 février 1957, lettre ministérielle du 2 mai 1951 ;
  `minimum_vieillesse` et la limite (4) : circulaires Cnav 103/93 et 40/88, lettres Cnav du
  4 mars 1986 et ministérielle du 29 mars 1965 ; `majoration_conjoint_a_charge` (9) :
  circulaires Cnav 77/86, 49/86, 2011/14, 2018/24, 2025/22, 2010/54 (note 2), ministérielle
  4/SS du 14 janvier 1975, lettres ministérielles du 6 octobre 1977 et du 22 juin 1988 ;
  `majoration_conjoint_a_charge` avec d'autres (4) : circulaires Cnav 46/75 (avec le régime
  des retraites ouvrières et paysannes et `ecarts-au-droit-positif.md`), 87/94 et 2006/66
  (avec `minimum_vieillesse`, et la résidence pour la seconde), 2004/37 (avec les deux et la
  limite) ; `minimum_contributif` : circulaire ministérielle 20/SS du 6 février 1961 ; la
  limite (2) : circulaires Cnav 111/76 et 2006/13.
- *La limite* « anciennes prestations » (`docs/limites/3-systeme-actuel.md`), neuve : ce que
  le modèle sert des anciennes allocations, ce qu'il n'en sert pas, le candidat et le point
  non tranché de cette note.

**Ce que la lecture a trouvé, sans écart.** Les deux étages d'avant 2007 : la majoration de
L. 814-2, « Le montant de la majoration art. L814-2 correspond au montant de l'allocation aux
vieux travailleurs salariés (AVTS) diminué du montant des avantages non cumulables » (exposé
« Montant »), que le modèle sert comme premier étage, `max(0, avts − ressources)`, borné au
plafond ; l'allocation supplémentaire, réduite de ce que son total et les ressources du
ménage dépassent le plafond, « Si chaque conjoint a droit à l'allocation, chaque allocation
est réduite de la moitié du dépassement » (exposé « Montant »), au montant du ménage, que le
modèle partage par moitié ; le montant des villes de plus de 5 000 habitants avant avril 1962,
déjà déclaré dans la fiche. La pension étrangère comptée depuis le 1er avril 1993, « les
prestations et les ressources d'origine étrangère […] sont prises en compte pour
l'appréciation de ces conditions » (R. 816-2, 1993), « L'avantage de vieillesse étranger est
assimilé à un avantage de vieillesse français » (exposé « Evaluation des ressources -
Majoration article L814-2 du CSS ») ; elle est retranchée du premier étage par le modèle, comme par
la caisse. La majoration pour conjoint à charge, son montant entier « pas revalorisé depuis le
01/01/1977 » (fiche : 4 000 F depuis le 1er juillet 1976), proratisé, différentiel. Ce que
d'autres ont déjà déclaré, que ces exposés touchent : la bonification de 2 000 F pour trois
enfants et l'arrondi à 200 F (étape 6) ; la majoration de 50 F du conjoint de moins de
soixante-cinq ans (G9, et la version `loi_du_23_aout_1948` de sa fiche, qui ne la sert pas) — l'exposé « Montant - Majoration pour conjoint à charge » la date
« Avant le 01/07/1974 », maintenue « chaque fois qu'elles étaient plus avantageuses, pour
les retraites attribuées jusqu'au 01/03/1975 » — ; l'allocation supplémentaire dans un autre
État de la Communauté avant juin 1992 (point non tranché de G14) : « les personnes qui, avant
le 01/06/1992, remplissaient les conditions d'attribution de l'allocation et relevaient des
règlements européens, bénéficient du maintien des droits acquis » ; le versement forfaitaire
unique, que la majoration de L. 814-2 ne majore pas (exposé « Conditions d'attribution -
Majoration article L814-2 du CSS », circulaire Cnav 31/75, § 34), qui touche le point de H10
sur l'allocation après un versement forfaitaire unique ; l'âge abaissé des titulaires d'une retraite d'ancien
combattant, de travailleur manuel ou de mère de famille ouvrière, « réputées inaptes au
travail de plein droit » (approximation de la fiche `minimum_vieillesse`) ; les ressources
hors des pensions, la période de trois ou douze mois, le plafond de la veuve de guerre, des
séparés, la récupération sur la succession, l'aide aux anciens migrants, les versements de
2008 et de 2009 (fiche et limite « allocations du minimum ») ; la majoration pour conjoint à
charge à soixante ans du conjoint inapte, au titulaire de l'allocation aux vieux travailleurs
salariés, le divorce et le décès (approximations de sa fiche).

**Un candidat, aux sessions du modèle** (rien n'a été corrigé) : *la majoration de L. 814-2
de qui réside hors de France, avant 2006.* L'exposé « Conditions d'attribution - Majoration
article L814-2 du CSS » : « Cette majoration était attribuée sans condition de nationalité et
ni de résidence. » ; « Changement de situation » : « Le bénéficiaire domicilié fiscalement
hors de France devait fournir un document de l'administration fiscale ou communale du pays de
son domicile. » ; « Conditions d'attribution - AVTS » : « L'allocation est maintenue pour le
Français qui part résider hors de France. » D. 814-2 (LEGIARTI000006739551) : « Peut
bénéficier de la majoration prévue à l'article L. 814-2, la personne âgée de plus de
soixante-cinq ans ou de soixante ans en cas d'inaptitude au travail qui remplit les
conditions de ressources définies audit article. » ; D. 814-9 (LEGIARTI000006739756) n'y
ajoute que la demande, sa date et les ressources ; D. 814-1 (LEGIARTI000006739738) ne pose
la condition de « résider sur le territoire de la France métropolitaine » que « Pour
l'application de l'article L. 814-1 », l'allocation spéciale. La lecture contraire tient à
L. 814-2 depuis 1987, « ayant résidé sur le territoire métropolitain, dans les départements
mentionnés à l'article L. 751-1, […] pendant une durée et dans des conditions fixées par
décret » : une résidence passée, dont aucun décret lu ne fixe la durée, et non une résidence
au jour du service ; elle ne tient pas. Le modèle ne sert aucun des deux étages à qui déclare
résider hors de France : `foyer_et_net` ne les calcule que si `condition_de_residence` est
remplie (`droit/foyer.py`, lignes 238 à 242 ; `foyer.js`, lignes 216 à 219), et la version
`allocation_supplementaire_avant_2006` de `residence_et_minimum_vieillesse`, sur l'annexe X
du règlement n° 883/2004, qui ne nomme que les « Allocations supplémentaires », exige la
résidence (`residence_requise: true`). *Cas posé* : un Français retraité du régime général,
seul, qui réside au Maroc (hors des règlements européens), pension de 1 500 € par an en 2000,
sans autres ressources. La caisse : majoration = 2 688,13 − 1 500 = 1 188,13 € par an
(série, 2000 : allocation aux vieux travailleurs salariés 2 688,13 €, plafond 6 699,68 € ;
2 688,13 ≤ 6 699,68, entière), et pas d'allocation supplémentaire, que la résidence hors de
France supprime (L. 815-11 ancien, exposé) ; le modèle : 0 €. 1 188,13 € de moins par an,
et autant chaque année de son service, que la caisse poursuit après 2006 selon les règles
d'avant.

**Un point non tranché, sans candidat** : *la pension étrangère avant le 1er avril 1993.*
L'exposé « Evaluation des ressources - Majoration article L814-2 du CSS », « Avant le
01/04/1993 - Avantage de vieillesse étranger » : « Si la convention prévoyait des règles de
non cumul, l'avantage de vieillesse étranger était retenu en avantage non cumulable. Si la
convention ne prévoyait pas des règles de non-cumul, l'avantage de vieillesse étranger était
pris en compte dans les ressources. » (circulaire Cnav 38/88, § 5) ; de même l'exposé
« Conditions d'attribution - Majoration pour conjoint à charge ». R. 816-2 n'existe que depuis
le 30 mars 1993. Le modèle ajoute toute pension étrangère aux ressources
(`ressources += etrangeres`), et la retranche donc du premier étage. Ni l'exposé ni le modèle
ne disent quelles conventions avaient des règles de non-cumul. *Cas posé* : seul, en France,
en 1990, pension du régime général de 1 000 € par an et pension d'un État lié par une
convention sans règle de non-cumul de 1 000 €. Lu comme la caisse : majoration 2 285,21 −
1 000 = 1 285,21 € ; ressources 3 285,21 € ; allocation supplémentaire 3 076,42 − (3 285,21 +
3 076,42 − 5 498,84) = 2 213,63 € ; 3 498,84 € en tout. Lu comme le modèle (`avant_l_aspa`) :
2 285,21 − 2 000 = 285,21 €, puis 3 076,42 € entière ; 3 361,63 € en tout. 137,21 € d'écart par
an, quand la convention n'avait pas de règle de non-cumul ; aucun quand elle en avait.

**Ce que la base sert de travers.** Trois ancres mènent à un autre article que celui
qu'elles nomment : « Css art.D813-3 » à D. 813-2 (« Conditions d'attribution - Allocation aux
mères de famille »), « Css art. L811-3 » à L. 811-13 (« Montant - Allocation aux mères de
famille »), « Css art. L811-1 » à L. 811-11 (« Conditions d'attribution - Secours viager »).
« Décret 2002/1371 du 29/11/2002 » mène au décret n° 2002-1371 du 19 novembre 2002. « Loi
56/638 du 30/06/1956 » : la loi du 30 juin 1956 qui institue le Fonds national de solidarité
porte le n° 56-639 (titre du décret n° 56-665 au JORF, et la série) ; le n° 56-638 est un
décret du 28 juin. « Lettre ministérielle du 21/03/199 », date tronquée ; l'exposé
« Evaluation des ressources - Allocation supplémentaire » parle de « l'attribution de la
retraite de réversion », repris de la réversion.

**Ce que la lecture n'a pas fait.** Aucune règle, aucune fiche, aucune série, aucune valeur
servie, aucun test n'a été changé ; le registre seul, en ses colonnes `sort` et `renvoi`, et
la limite neuve. Les références prennent les renvois des objets rangés ici qui les lient, sans
ceux des barèmes, des avis, ni des fiches qui les citent par leur numéro. Les textes du JORF
absents de l'index ne sont pas lus ; aucun ne décide d'un rangement.
