# La carte des fiches : le code et les régimes du dernier lot, écrits

**La demande.** Vague du 28 octobre 2026 : le propriétaire demande une session
par tâche qui se mène sans lui ; la session de suivi ouvre celle-ci après les
quatre premiers lots, onze, douze, onze et dix fiches. Celle-ci, de
l'action 130 : le dernier lot des fiches tirées du registre de veille qui
n'avaient ni code ni régimes, les treize du régime général, des durées, des
minima et des paramètres (note
`130/2026-10-28-carte-des-fiches-fonctionnaires-marins-et-mines.md`), puis les
trois qui n'avaient pas de régimes. Aucun chiffre du modèle ne bouge : seuls
changent les champs `code` et `regimes` de treize fiches, le champ `regimes` de
trois autres, et un test.

## Ce qui est fait

- **Le test d'abord** : `CODE_ET_REGIMES_ECRITS` (`tests/test_carte.py`)
  grandit de seize fiches, vu rouge de treize, deux champs chacune, et de trois,
  leurs régimes, puis vert ; le code des treize,
  `test_le_code_de_chaque_fiche_tient` le confronte au dépôt.
- **Les treize fiches.** La carrière longue : ses portes, lues à la date d'effet
  et aux seules générations que chacune nomme, l'entrée précoce et les quatre
  trimestres du né du dernier trimestre, la durée cotisée, réputée comprise, et
  la durée d'assurance d'avant novembre 2012 (`CarriereLongue`, `ouvrir`,
  `age_carriere_longue`, `_carriere_longue_acquise`). Sa lecture, aux deux
  régimes de base en points, sur la liste des périodes qui opposent une durée,
  et cette durée elle-même (`periodes_opposant_une_duree`,
  `age_taux_plein_droit`, `abattement_regime_de_base`). Les limites du chômage
  non indemnisé (`limiter_chomage_non_indemnise`). La liquidation unique des
  régimes alignés (`lura_applicable`, `groupes_de_succession`). L'ASPA et, avant
  2007, ses deux étages (`foyer_et_net`, `avant_l_aspa`, `MinimumVieillesse`).
  Le plafond de vingt trimestres de décote, que le catalogue donne par défaut
  (`trimestres_de_decote`, `CatalogueRegimes._construire`). Les points gratuits
  de la RCO (`points_gratuits`). La revalorisation des pensions servies, régime
  par régime (`PensionServie.coefficient`, `faire_vivre`). Une ligne par année
  et par activité, et quatre trimestres par année civile tous régimes
  (`_lignes_du_parcours`, `Carriere.trimestres_par_annee`). La suspension de
  2026, sans terme dans le code (`SUSPENSION_2026_EFFET`, les tables d'avant
  elle, `_sous_le_droit`). Les séries de l'année, chacune par son accesseur. Et
  la certification sur l'index LEGI à jour, qui vit dans les récupérateurs
  (`dila_index.py`, `verifier_donnees.py`) : les deux moteurs n'en lisent que la
  fiabilité des valeurs et le journal.
- **Le champ `regimes`**, lu à la règle et au code : les régimes alignés pour la
  liquidation unique (`REGIMES_ALIGNES`) ; ceux que la revalorisation rattache à
  L. 161-23-1 et ceux de la fonction publique (`REGIMES_REGLE_GENERALE`,
  `REGIMES_FONCTION_PUBLIQUE`) ; pour la carrière longue, le régime général et
  ceux dont la fiche lit les portes — artisans et commerçants, non-salariés
  agricoles, fonctionnaires —, avec les salariés agricoles et les libéraux ; les
  deux régimes de base en points pour leurs deux fiches ; le régime général et
  les salariés agricoles pour le chômage non indemnisé ; pour l'ASPA, les neuf
  régimes dont les périodes la portent parmi leurs avantages non contributifs,
  avec ceux de la fiche de la résidence (`residence_et_minimum_vieillesse`) ;
  pour la suspension, les 56 régimes dont l'âge ou la durée suivent les tables
  par génération (fiches `age_legal_par_generation` et
  `duree_requise_par_generation`) ; pour le plafond de décote, ceux des cinq
  textes que la fiche lit ; la RCO et le régime de base des exploitants pour les
  points gratuits ; pour un statut par année, le régime général, les régimes
  alignés et la CNRACL, dont les textes bornent la durée à quatre trimestres par
  année ; le régime général, les salariés agricoles et l'Agirc-Arrco pour les
  paramètres de 2026 ; pour la certification, les quinze régimes dont un
  récupérateur certifie une série, relevés script par script par l'éclaireur.
- **Les trois fiches sans régimes** : le micro-entrepreneur, que les
  affiliations routent du RSI et de la NRIC au régime général et au RCI, et à la
  CNAVPL et à la complémentaire de la Cipav (`regimes_du_forfait`) ; le départ
  pour incapacité permanente, le compte de prévention et l'amiante, le régime
  général, les salariés agricoles et le RSI ; les rachats et les versements, les
  mêmes et l'État, dont le code des pensions écrit les siens. Les deux fiches pas
  encore modélisées n'ont pas de code à écrire.
- **Les tests nommés, relevés par une sonde de session**, hors du dépôt : seize
  neutralisations de onze fiches dans le seul Python, par un greffon de session
  — la carrière longue entière, sa durée d'assurance d'avant 2012, les quatre
  trimestres du dernier trimestre et la borne de ses générations ; sa lecture par
  les régimes en points ; la durée qu'ils opposent ; les limites du chômage ; la
  suspension ; la liquidation unique ; l'ASPA, ses deux étages et le barème du
  couple ; le plafond de décote ; les points gratuits ; la revalorisation ; les
  quatre trimestres par année —, chacune rejouée sur les 913 témoins en Python,
  comparés au Python intact, sur la suite rapide et sur les 188 tests qui
  confrontent les deux moteurs. Les fiches nomment les fichiers qui tombent, les
  exemples officiels, les confrontations et les témoins. Les paramètres de 2026
  et la certification n'ont pas de règle à neutraliser : leurs fiches nomment
  les tests qui tiennent leurs valeurs ou leur outil. Dans le clone, sept
  confrontations de la suite rapide et onze des 188 tombent avec ou sans
  neutralisation, le paquet du site datant d'avant les derniers envois ; GitHub
  le refait avant la suite.
- **Ce que la sonde a montré**, que les fiches disent sans le trancher. Le
  plafond de décote mord : sa fiche lui prête un effet nul, sur un balayage de la
  grille, quand huit témoins changent sans lui — les quatre parents de trois
  enfants de la fonction publique partis avant 2012, la complémentaire de la
  CPRN d'un notaire parti à l'âge légal en 2022, deux départs non ouverts et un
  détail — et sept tests tombent, dont la pension provisoire de la retraite
  progressive et l'âge d'annulation d'un actif ; à bon droit dans la fonction
  publique, dont le texte l'écrit. Aucun témoin ne tient
  les limites du chômage non indemnisé dans le seul Python : le portage bâtit
  leurs carrières, avec sa propre limite. La liquidation unique ne déplace que
  des témoins qui ont des périodes hors de France, la grille n'exerçant qu'un
  statut à la fois. Aucun cas posé à la main ne tient la carrière longue des
  régimes en points, ni la durée qu'ils opposent : deux tests seulement tombent
  sans elles, dont une confrontation.

L'écriture s'est faite par un outil de session, hors du dépôt, qui a vérifié
qu'aucun autre champ ne bougeait. Les phrases `moteur` disent ce que le code
fait, relu fonction par fonction. L'étape n'écrit aucune règle du scénario 1 :
ni veille, ni entrée au journal. Rien n'est dû aux pages.

## Ce que l'étape laisse

- Toute fiche a ses régimes et son code, confronté au dépôt, hors de
  `pension_non_salaries_agricoles_2026`, sans régimes et seule de `EN_PROSE`, à
  la session de l'action 131. La carte passe de 659 manques à 630 ; ses 106
  fiches à lire au droit restent, et les points ouverts des phases 2 à 8.
- Pour une session du modèle : l'effet du plafond de décote, que sa fiche dit
  nul ; un cas posé à la main pour la carrière longue des régimes en points et
  pour la durée qu'ils opposent, que la fiche de chacune cite sans test.

## Ce qui attend le propriétaire

Rien de neuf : la septième étape du sixième domaine, la décision de la
proposition, et celle sur la retraite progressive, le cumul et la seconde
pension, README muet.
