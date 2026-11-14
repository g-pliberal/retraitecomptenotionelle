# Correction de la ligne 18 de la file : la CARMF et l'ASV majorent du trimestre civil qui suit l'âge

Dix-huitième ligne de la file `2026-11-13-corrections-decidees.md`, décidée par le
propriétaire le 13 novembre 2026. Une ligne, rien d'autre.

**Le texte, relu à l'index JORF** (à jour du 11 novembre 2026). Arrêté du 30 novembre
2016, annexe (JORFARTI000033521562), article 15 des statuts du régime complémentaire :
« il est fait application d'un coefficient de majoration de 1,25 % par trimestre
séparant le premier jour du trimestre civil suivant celui où le médecin atteint cet âge
de la date d'effet de la retraite. Le coefficient de majoration est le cas échéant
réduit à 0,75 % par trimestre à partir du premier jour du trimestre civil suivant celui
où le médecin atteint l'âge de 65 ans, sans pouvoir s'appliquer au-delà du premier jour
du trimestre civil suivant le soixante dixième anniversaire du médecin. » Arrêté du
1er décembre 2016 (JORFARTI000033538061), article 12 des statuts de l'ASV : mêmes mots.
L'arrêté du 22 mars 2017 (JORFARTI000034298521) n'y change que l'âge (« après l'âge de
62 ans »). Règlements du 10 juillet 2026 (JORFARTI000054435859), I, article 2, et III,
article 2 : mêmes mots. Le texte tranche ce que la ligne dit.

**L'erreur.** Le modèle comptait les trimestres de trois mois écoulés depuis le premier
jour du mois où l'âge est atteint (le mois de naissance pour qui est né un 1er, le
suivant sinon). Deux cas en comptaient un de trop : le médecin né le premier jour d'un
trimestre civil, dont le trimestre de l'âge comptait ; et celui qui, né un autre jour,
prenait sa pension ailleurs qu'au premier jour d'un trimestre civil — la complémentaire
ne s'y tient que depuis le 18 juillet 2026, l'ASV jamais. Le passage à 0,75 % se lisait
de même à l'âge, non au trimestre civil qui suit les 65 ans : le reste que la ligne 13
avait déclaré.

**Le test d'abord** (`tests/test_sections_sante.py`, `CARMF_AU_TRIMESTRE_CIVIL`, joué
par `test_la_carmf_sert_ses_coefficients_dans_les_deux_moteurs`), quatre cas posés à la
main depuis le texte, servis par le portage et refaits au bit près par le moteur Python
(`servi_et_refait`), vu rouge (1,21 où le texte donne 1,2025), puis vert :

- né le 1er janvier 1958, pension au 1er janvier 2025 : 62 ans le 1er janvier 2020,
  décompte du 1er avril 2020 ; 65 ans le 1er janvier 2023, 0,75 % du 1er avril 2023 ;
  douze trimestres à 1,25 %, sept à 0,75 %, 1,2025 ;
- né le 10 février 1955, pension au 1er mars 2019 : décompte du 1er avril 2017,
  vingt-trois mois, sept trimestres, 1,0875 (le modèle, huit, 1,10) ;
- né le 10 septembre 1951, pension au 1er janvier 2017 (le reste de la ligne 13) :
  dix-huit trimestres à 1,25 % du 1er avril 2012, un à 0,75 % du 1er octobre 2016,
  1,2325 (le modèle, 1,2375) ;
- né le 1er janvier 1950, pension au 1er avril 2021 : douze trimestres à 1,25 %, vingt
  à 0,75 % jusqu'au 1er avril 2020, 1,30 (inchangé : la limite glissait avec le début).

**L'effet au cas posé** (médecin libéral entré à 22 ans, deux salaires moyens, euros de
2026). Né le 1er janvier 1958, pension au 1er janvier 2025 : la CARMF sert 16 016,14 €
au lieu de 16 116,03 €, **99,89 € par an** de moins ; l'ASV 19 147,78 € au lieu de
19 267,20 €, **119,42 € par an** de moins. Né le 10 février 1955, pension au 1er mars
2019 : 12 044,36 € à la CARMF et 14 951,30 € à l'ASV, au coefficient 1,0875 au lieu de
1,10 (138,44 € et 171,85 € par an de moins). Né le 10 septembre 1951 : 13 598,10 € et
17 432,50 €, 55,16 € et 70,72 € de moins.

**La correction.**

- Les données : un interrupteur de période, `surcote_du_trimestre_civil_suivant`,
  déclaré au schéma et à la fiche `surcote_par_age_seul`, posé sur chaque période de
  `carmf_complementaire.yaml` et d'`asv_conventionnes.yaml` qui majore (depuis 2017).
- Le moteur, des deux côtés (`surcotePoints`, `surcote_points`) : sous l'interrupteur,
  les trimestres se comptent du premier jour du trimestre civil qui suit celui où l'âge
  de départ est atteint jusqu'à la date d'effet, sans dépasser celui qui suit les 70 ans ;
  le second taux vaut du premier jour du trimestre civil qui suit les 65 ans
  (`trimestreCivilSuivant`, `_trimestre_civil_suivant`, que le décompte de la CARCDSF
  reprend).
- Le chargeur et le paquet (`regimes.py`, `construire_donnees.py`) portent le champ.

**Ce que la correction déplace ailleurs.** Sept témoins de simulation, tous de
médecins nés un 1er janvier, de −0,23 % à −0,78 % au scénario 1 ; un rendu de page
(`simuler_cumul`). Cinq essais dont le médecin est né un 1er janvier, reposés à la main
à leur coefficient du texte : `test_la_carmf_majore_des_62_ans_puis_moins_apres_65_et_plus_rien_a_70`
(douze trimestres et trois, non quatre) ; les trois cas de la dispense des deux
premières années de la CARMF (1,2025 au lieu de 1,21 : 51 098,31 € au lieu de
51 417,01 €, la dispense retirant 2 270,09 € et non 2 284,25 €) ; l'ASV d'un an
d'exercice (onze trimestres, 363,02 € au lieu de 367,01 €). Les fiches
`decret_2026_418_liberaux` et `asv_medecins_points` gardent, dans leur histoire, les
montants du jour de leur correction, au coefficient d'alors.

**La classe, pas le cas.** Les mêmes mots ne se lisent qu'à la CARMF et à l'ASV ; la
CARCDSF, dont le texte compte aussi du trimestre civil suivant, est corrigée depuis la
ligne 24. La CARPIMKO (« par trimestre civil entier d'ajournement postérieur à l'âge »)
garde son point non tranché, hors de la file ; la CAVEC, la CAVP, la CPRN et la Cipav
écrivent autrement.

**Les fiches.** `surcote_par_age_seul` : l'erreur sort des approximations et passe à
l'histoire (`effet`) ; les dix versions depuis 2017 disent l'interrupteur.
`carmf_asv_minoration_enfants` : ses trois versions depuis 2017 le portent.

**Vérifié** : `python -m pytest -m rapide`, les fichiers de tests des sections, de la
carte, des coupures au mois, des données et des textes, les confrontations légères
(`test_oracle.py`, `test_destinie.py`, `test_estimation_officielle.py`,
`test_verification.py`), `test_moteur.py`, `test_pont.py -k refait`, verts ; le paquet
et les témoins refaits, `regenerer.py` laissé à GitHub.
