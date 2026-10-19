# Étape 7, suite : 2025, sous la loi seule, déclaré dans la fiche du diviseur

**La demande.** Vague du 19 octobre 2026, troisième salve, lancée par la
session de suivi « Tâches restantes » sur la demande du propriétaire (« Lance
les sessions qui n'ont pas besoin de moi ») : le second point du bloc
« Reprise » de l'étape au 19 octobre, *2025, rangé au léger, à déclarer* —
dans les approximations de sa fiche ou au registre, comme la coupe du
14 octobre l'a fait de chaque reste léger (`2026-10-14-la-coupe.md`).

**Le reste.** En 2025, qu'Eurostat ne publie pas encore et que la projection
de l'INSEE, ouverte en 2026, ne couvre pas, la table de mortalité lit à tous
les âges la loi de Gompertz-Makeham seule : sa forme et, faute de table où se
raccorder, son niveau sont calés sur l'espérance de vie à 60 ans que l'INSEE
publie pour l'année (28,0 et 23,9 ans) et sur celle à 65 ans, interpolée
entre 2024, observée, et 2026, projetée (23,61 et 19,97 ans ; `_calibrer`,
`loi`). Le classement du 9 octobre le range au léger, la coupe du 14 le
déclare sans le faire ; aucun modèle du registre n'y fait mieux, et le point
n'y a pas sa place. Deux fiches de la carte disent lire la table :
`coefficient_de_conversion`, le diviseur, et `capitalisation_obligatoire`,
dont la rente, servie sur un capital cotisé à compter de la bascule (2026 par
défaut), ne lit pas 2025 ; la valorisation des droits acquis et l'âge de
référence indexé lisent le diviseur à compter de la bascule eux aussi. La
déclaration va donc à la première.

**Ce que l'écart vaut, mesuré.** Faute de la table d'Eurostat, 2025 refait de
ses voisines : la moyenne géométrique des quotients observés de 2024 et
projetés de 2026, âge par âge (au-delà de 98 ans, en 2024, la loi raccordée).
La mesure, un script jetable que le dépôt ne garde pas : une sous-classe de
`DonneesMortalite` dont `_survie_cellule` rend cette moyenne en 2025, et
l'espérance résiduelle de génération (`esperance_residuelle`, le diviseur au
taux nul) des deux tables, pour chaque génération de 1905 à 1970 et chaque
âge de départ de 55 à 70 ans, jusqu'en 2025, unisexe et par sexe.

- *Les quotients* : calée sur deux espérances, la loi fait mourir trop tôt
  vers 75 ans, de 14 % (hommes) et 26 % (femmes) au-dessus des voisines, et
  vivre trop longtemps au-delà de 90 ans, de 30 et 27 % en dessous à 95 ans ;
  à 62, 65 et 85 ans, elle les suit à quelques pour cent.
- *Le diviseur* : au plus 0,28 % du diviseur unisexe, la table par défaut,
  et 0,29 % par sexe (un homme né en 1949 parti à 70 ans) ; trop court pour
  les générations qui ont de 70 à 80 ans en 2025, trop long pour celles qui en
  ont 90, à 0,26 % au plus ; rien pour un départ d'après 2025, qui ne lit pas
  l'année. Les pensions notionnelles de ces générations, dans les scénarios
  rétroactifs, en bougent d'autant, en sens inverse. Léger, comme le
  classement le disait.

**Ce qui est fait.**

- *La fiche* `coefficient_de_conversion` reçoit sa première approximation :
  l'année, la loi, la mesure, la coupe. Elle reste `transcrite`, comme toute
  fiche de la proposition (`test_univers.py`), et comme cinq fiches du droit
  réel qui portent des approximations.
- *Le test* `test_l_annee_sans_table_est_declaree_dans_la_fiche_du_diviseur`
  (`tests/test_donnees.py`), vu rouge avant la fiche, tient la déclaration :
  tant qu'une année sépare le dernier millésime observé du premier projeté,
  une approximation de la fiche la nomme, et une seule ; dès qu'Eurostat
  publiera 2025, il demandera de la retirer.
- *Les limites* (`docs/limites/1-certification.md`) : la ligne qui joignait
  2025 à la queue d'au-delà de 98 ans y disait la loi « raccordée au dernier
  quotient observé » ; en 2025, il n'y en a aucun. Deux lignes désormais, la
  seconde nomme la fiche.
- Aucun chiffre du modèle ne bouge. Le scénario 1 ne lit pas la table : ni
  veille du droit, ni entrée au journal.

**Ce qui reste** de l'étape : les ex-invalides de la Cnav (note du 19 octobre,
« inaptes de la Cnav », à une autre session) ; les scénarios 2 à 5 sous la
variante (note du 16 octobre, « indexation sous la variante ») ; à la session
des pages, les phrases de la page Coût (notes du 16, du 17 et du 19
octobre) ; au propriétaire, les départs qui suivent l'espérance de vie (note
du 18 octobre). Quand Eurostat publiera ses décès de 2025, la session qui les
certifiera retirera l'approximation, sur la demande du test.
