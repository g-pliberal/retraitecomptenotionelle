# Correction de la ligne 29 de la file : la CAVAMAC minore la longue carrière de 15 % depuis 2024

Vingt-neuvième ligne de la file `2026-11-13-corrections-decidees.md`, décidée par le
propriétaire le 13 novembre 2026. Une ligne, rien d'autre.

**Le texte, relu à l'index JORF** (à jour du 11 novembre 2026). Arrêté du 4 août 2023,
article 2, 2° (JORFARTI000047977903) : le d du 7° de l'annexe entre en vigueur « le
1er janvier 2024 ». Annexe, 7°, d (JORFARTI000047977908), à l'article 16 des statuts :
« Par dérogation au deuxième alinéa et sous réserve que l'assuré réponde aux conditions
pour bénéficier du dispositif prévu à l'article L. 351-1-1 du code de la sécurité
sociale, la retraite complémentaire peut être liquidée au plus tôt : - à 62 ans pour les
assurés ayant commencé leur activité avant l'âge de 20 ans ; - à 63 ans pour les assurés
ayant commencé leur activité avant l'âge de 21 ans. Avec, dans les deux cas,
l'application d'un coefficient de minoration de 15 %. » Le règlement de 2026, article 5
(JORFARTI000054436046), en vigueur le 18 juillet 2026, reprend ces mots et ajoute : « A
compter de l'âge de 64 ans, les assurés mentionnés au quatrième et cinquième alinéa
n'entrent plus dans le champ de la dérogation. Ils se voient appliquer le régime de
droit commun de minoration prévu au deuxième alinéa ». L'index LEGI n'a pas été
récupéré : les conditions de L. 351-1-1 sont celles que la base sert déjà, et la
correction n'y touche pas.

Le texte tranche ce que la ligne dit, pour le départ que la longue carrière ouvre avant
l'âge légal. Il ne tranche pas tout : voir « Ce qui reste déclaré ».

**L'erreur.** Le modèle opposait à la longue carrière la minoration de tous, 1,25 % par
trimestre manquant jusqu'à 67 ans : 25 % à 62 ans, 20 % à 63 ans.

**Le test d'abord** (`tests/test_sections_liberales.py`,
`test_la_cavamac_minore_la_longue_carriere_de_quinze_pour_cent_depuis_2024`), vu rouge
sur six des dix cas (0,75, 0,775, 0,80 ou 0,825 où le texte donne 0,85), puis vert ;
servis par le portage et refaits au bit près par le moteur Python (`servi_et_refait`).
Agent général au double du salaire moyen, euros de 2026 ; chaque attendu est la pension
du taux plein multipliée à la main par le coefficient du texte :

- né le 1er janvier 1962, entré à 18 ans, pension au 1er janvier 2024, premier jour de
  la rédaction, à 62 ans : 22 898,2905 × 0,85 = 19 463,55 € au lieu de 17 173,72 € ;
- né le 1er janvier 1964, entré à 18 ans, le cas de la note du 5 novembre : au
  1er janvier 2026, à 62 ans, 25 598,2503 × 0,85 = **21 758,51 € par an au lieu de
  19 198,69 €** (2 559,82 € de plus) ; au 1er juillet 2026, à 62 ans et 6 mois,
  22 032,87 € au lieu de 20 088,80 € (0,775) ;
- né le 1er janvier 1965, entré à 18 ans, au 1er janvier 2027, sous le règlement de
  2026 : 22 351,31 € au lieu de 19 721,74 € ;
- né le 1er janvier 1968 : entré à 20 ans, parti à 63 ans, 24 542,01 € au lieu de
  23 098,36 € (0,80) ; entré à 18 ans, parti à 63 ans et 6 mois, 25 598,18 € au lieu de
  24 845,29 € (0,825) ;
- inchangés : sans longue carrière, 0,80 à 63 ans ; avant 62 ans et avant le
  1er janvier 2024, 0,75.

**La correction.** Deux paramètres de période (schéma, chargeur, paquet du portage) :
`carriere_longue_minoree_de`, le coefficient fixe, et
`carriere_longue_minoree_depuis_l_age`, l'âge depuis lequel il est servi. Quand la
longue carrière ouvre la liquidation, `abattementRegimeDeBase` et son jumeau
`abattement_regime_de_base` rendent 1 − 0,15 depuis 62 ans ; le motif d'ouverture y
descendait déjà, depuis la ligne 11 (CAVP). Posés aux périodes de 2024 et de 2026 de
`cavamac_complementaire.yaml`. Aucun témoin de simulation ne bouge.

**Fichiers fabriqués refaits** : le paquet (`moteur/donnees.json`) ; les témoins,
inchangés ; l'inventaire des régimes et `docs/regimes.md`
(`construire_inventaire.py`, `construire_regimes_md.py`), parce que le champ `manque`
du régime change ; la page `methode/index.html` (`construire_pages.py`), que la suite
rapide réclamait.

**La fiche.** `cavamac_minoration_age_seul` : les deux paramètres dans les versions de
2024 et de 2026 ; l'écart passe à l'histoire, et l'approximation ne garde que ce qui
suit. Les limites (`docs/limites/`) ne nommaient pas cet écart : rien n'y change.

**Ce qui reste déclaré**, dans la fiche.

- L'assuré qui remplit les conditions de la longue carrière et part après l'âge légal de
  sa génération, avant 64 ans : le modèle ne nomme la longue carrière que lorsqu'elle
  ouvre le départ, et lui garde la minoration de tous (né le 1er janvier 1964, âge légal
  62 ans et 9 mois, parti à 63 ans : 0,80). Le règlement de 2026 ne le sort de la
  dérogation qu'à 64 ans, ce qui lui donnerait 0,85 ; les statuts de 2024 ne disent pas
  quand elle cesse. C'est le « 5 points de trop à 63 ans » de la note du 5 novembre : non
  corrigé. Le corriger demande que l'ouverture dise si les conditions de L. 351-1-1 sont
  remplies même passé l'âge légal, dans les deux moteurs.
- Avant 62 ans, et avant le 1er janvier 2024, où ces textes n'ouvrent pas la longue
  carrière, le modèle sert la complémentaire dès que la base l'ouvre, à la minoration de
  tous (`liquidation_regime_par_regime`).
- Les deux entrées du texte, avant 20 ans et avant 21 ans, sont lues aux âges de la base
  (D. 351-1-1), non comptées à part.

**La classe, pas le cas.** Parmi les fichiers des caisses des libéraux, seules la CAVP
(ligne 11, corrigée) et la CAVAMAC écrivent une minoration propre à la longue carrière ;
les textes des autres sections n'ont pas été relus ici pour elle.

**Vérifié** : `python -m pytest -m rapide` ; `test_sections_liberales.py`,
`test_sections_sante.py`, `test_sections_juridiques.py`, `test_invalidite.py`,
`test_carte.py`, `test_donnees.py`, `test_coupures_au_mois.py`, les confrontations
légères (`test_oracle.py`, `test_destinie.py`, `test_estimation_officielle.py`,
`test_verification.py`), `test_pont.py -k refait`, verts.
