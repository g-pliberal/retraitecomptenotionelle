# Étape 6 : les confrontations par le pont — l'estimation officielle et Destinie 2 au portage, le point d'entrée du droit pour les exemples officiels

**La demande.** Le 31 octobre 2026, le propriétaire ouvre l'étape suivante de
l'action 161 : que les confrontations aux références extérieures éprouvent le
portage, l'exemplaire qui fait foi (note de décision 0005), par `pont.py` et
`pont.mjs` — dans l'ordre, un commit au vert pour chacune :
`test_estimation_officielle.py` et son script, `test_destinie.py`, puis
`test_oracle.py`, d'abord inventorié, basculé s'il tient proprement dans la
session, sinon seulement son point d'entrée au pont. Chaque confrontation
garde ses cas et ses tolérances ; tant que le jumeau Python reste, le moteur
Python doit y refaire au bit près ce que rend le portage, pour qu'aucun
chemin que les témoins n'exercent ne perde sa vérification. Une session du
site met à jour la page « Méthode » en parallèle, sur ses fichiers.

**La demande au pont** (a89ddef). Les confrontations lisent du scénario 1 ce
que `Comparaison.dictionnaire()` n'écrit pas tout entier : la part de chaque
régime dans la majoration pour enfants (`par_regime`), la durée validée, le
taux. `pont.simulations` ne leur suffisait pas, et le dictionnaire ne pouvait
pas grandir sans récrire les témoins. D'où `scenario_actuel`, dans `pont.mjs`
et `pont.py` : chaque requête du simulateur, lue par la saisie du portage et
simulée comme le site la simule — tel quel un relevé que l'appelant a déjà
prolongé, avec `"prolonger": False` (`releveTelQuel`, que
`carrieres_des_saisies` partage désormais) — ; ce qu'il en rend : la date du
départ, le passage aux euros constants, la pension et ce qui est hors de la
répartition, chaque pension de régime (montant, détail), chaque avantage
(montant, part de chaque régime), la durée validée, le taux, l'ouverture et
son motif, et la réversion (son année, chaque régime, sa date d'effet). Le
Python le relit sous ses types (`scenario_actuel_des_donnees`, les entiers
vérifiés). Son test, vu rouge d'abord, le confronte au moteur Python sur une
requête de chaque forme — un veuf de Destinie, sa réversion et sa majoration
pour trois enfants ; une saisie par les métiers ; un relevé prolongé par le
site, puis tel quel : au bit près, et un ulp déplacé dans le miroir Python se
voit. `TOLERANCE_DU_MOTEUR_PYTHON` et `ecarts_d_ecriture` passent de
`test_pont.py` à `tests/outils_pont.py`, que les confrontations partagent,
avec le miroir Python du scénario 1 (`scenario_actuel_en_donnees`,
`Saisies.scenario_actuel`) et `servi_et_refait`, le pont dont chaque réponse
est refaite au moteur Python.

**L'estimation officielle** (a89ddef). `scripts/estimation_officielle.py` fait
liquider chaque départ par le portage (`Confrontation.scenario_actuel`), et
`servi` lit ce qu'il sert ; il ne garde en Python que ce qu'il lit pour
lui-même — les régimes et leurs étages, les séries des prix, du salaire moyen
et du plafond — et `salaire_moyen_annuel` (`carriere.py`), qui prolonge le
relevé à sa convention. Un test vu rouge le tient : le moteur Python empêché
de simuler, le rapport chiffre ses deux départs. Le contrôle du Python est
dans la confrontation même : une fixture met `servi_et_refait` à la place du
pont, et chaque départ que huit de ses tests font servir — toutes les
conventions des revenus à venir, les corrections, le jeune, les euros de
2028, le plafond, la ligne de commande — est refait au bit près. Un ulp
déplacé dans le miroir Python les rougit tous les huit.

**Destinie 2** (6a59552). `test_destinie.py` mesure les dix-huit cas du témoin
sur ce que le portage sert (`ecarts_du_temoin`, une demande pour tous), le
moteur Python empêché d'y entrer (test vu rouge d'abord) ; un test lui fait
refaire chaque cas au bit près, réversion et majoration de chaque régime
comprises, et rougit sous le même ulp. Les tolérances, les écarts déclarés et
leurs bornes ne bougent pas : les nombres sont ceux d'avant, au bit près.

**L'écart vu, de type seulement.** Sur six des dix profils d'OpenFisca au
régime général, le jumeau Python de `liquider.trimestres_de_decote` rend un
entier (2, 5, 6, 4, 18 et 5 trimestres), quand son annotation dit un
flottant ; le portage rend le même nombre. `test_oracle.py` le passait déjà
par `float()`. La confrontation relit les deux sous le type que le pont
déclare (`pont.relu_du_droit`), comme la table des types relit le zéro d'une
somme vide des témoins : aucune valeur n'est tolérée, seul le type est
ramené. Soumis au propriétaire : garder cette relecture, ou faire rendre
`float` au jumeau Python.

**`test_oracle.py`, l'inventaire.** 2 399 lignes, 45 fonctions de test, dont
une paramétrée sur les 218 exemples officiels (`exemples_officiels.yaml`).
Il ne passe pas par la saisie : il bâtit ses carrières à la main
(`Carriere`, `AnneeCarriere`) ou par `simulateur.carriere_simple`, et appelle
le droit fonction par fonction. Ce qu'il appelle du modèle Python, bloc par
bloc :

| Bloc | Lignes | Ce qu'il appelle |
|---|---|---|
| OpenFisca, régime général (6 tests, `_notre_calcul`) | 111–287 | `scenario_actuel.calculer` ; `catalogue[…].periode` ; `ouvrir.duree_requise` ; `liquider.duree_proratisation`, `decote_opposable`, `salaire_de_reference`, `trimestres_de_decote` |
| OpenFisca, pension civile (9 tests, `_notre_calcul_fonction_publique`) | 288–549 | les mêmes |
| OpenFisca, Arrco (5 tests, `_nos_points_arrco`) | 550–704 | `scenario_actuel.calculer` ; `liquider.valeur_du_point` |
| OpenFisca, Agirc (8 tests ; `_nos_points`, `_assiette_et_cotisation`) | 705–1028 | `scenario_actuel.calculer` ; `scenario_actuel.valeurs_point.achat` ; `liquider.valeur_du_point` ; les taux du `catalogue`, `macro.plafond_securite_sociale`, `BORNES_ASSIETTE` |
| OpenFisca, Ircantec (10 tests ; `_nos_points`, `_cotisation_ircantec`) | 1029–1360 | `scenario_actuel.calculer` ; `scenario_actuel.valeurs_point.achat` et `.service` ; `scenario_actuel.ages_annulation_decote` ; le `catalogue`, `macro.plafond_securite_sociale`, `BORNES_ASSIETTE` |
| Régimes alignés (4 tests, `_notre_pension_alignee`) | 1361–1565 | `scenario_actuel.calculer` |
| Exemples officiels (3 tests ; `_carriere_exemple`, `_mesurer`, `_cumul_exemple`) | 1566–2399 | `simulateur.carriere_simple`, `chronologie.valeur`, `calendrier.origine_des_ages`, `en_mois` ; `scenario_actuel.calculer` ; pour 53 grandeurs mesurées : `ouvrir.age_ouverture_droit`, `departs.age_legal`, `liquider.salaire_de_reference`, `valeur_du_point`, `nombre_d_annees_retenues`, `mois_apres_le_depart`, `majoration_rafp`, `prestation_rafp`, `invalidite.exigences_du_handicap`, `pension_du_fonctionnaire_invalide`, `retraite_pour_invalidite`, `reversion.reversion`, `Echeancier`, `cumul.cumuler`, `releve.construire` et `LigneRelevee`, `foyer.foyer_et_net`, `revalorisation.faire_vivre`, `remuneration.fiche_depuis_brut`, `moteur.compte.ConstructeurCompte`, le `catalogue`, la `macro`, les `affiliations`, l'`indexation`, `parametres.avec` ; et la carte des fiches (`noyau.carte`) |

Chacune de ces fonctions a son jumeau dans `moteur/js/`, sous le même nom en
casse de chameau et dans le même ordre d'arguments (`dureeRequise`,
`decoteOpposable`, `foyerEtNet`, `faireVivre`, `ficheDepuisBrut`…). Le
basculement entier ne tenait pas proprement dans la session : une trentaine
de fonctions, des carrières bâties en Python, l'échéancier, la réversion, le
cumul, quatre cents lignes de mesures.

**Le point d'entrée du droit** (5e83127). `pont.droit` fait appeler au
portage une fonction du droit sous le nom de son jumeau Python, ses arguments
dans l'ordre du jumeau : `pont.MOTEUR` pour le moteur du scénario 1,
`pont.Periode(code, annee)` pour la période d'un régime, une carrière que le
Python a bâtie, passée une fois en données (`carriere_en_donnees`), une
valeur telle quelle, sous les paramètres du simulateur. Ce que la fonction
rend se relit sous le type de son jumeau (`LECTURES_DU_DROIT`, dans
`pont.py`, que `FONCTIONS_DU_DROIT` de `pont.mjs` suit) ; une fonction qui n'y
est pas est refusée avant node, et le portage arrête une demande qui en nomme
une qu'il ne porte pas. Elle porte les six fonctions du premier bloc, dont
`scenario_actuel.calculer`, qui rend le scénario 1 sous les champs de
`scenario_actuel` (`actuelEnDonnees`, `pont.actuel_des_donnees`). Son test,
vu rouge, les appelle sur les dix profils d'OpenFisca au régime général,
chaque carrière bâtie comme `_notre_calcul` la bâtit : au bit près des
jumeaux Python.

**Ce qu'il faudrait à `test_verification.py`.** Rien du pont : il n'éprouve
aucune règle du moteur. Il confronte la vérification des données
(`scripts/verifier_donnees.py`) et vingt-quatre scripts de `scripts/fetch/`
à des sources simulées, qui restent en Python, côté fabrique
— le Python garde ce qui lit le YAML et fabrique le paquet (note 0005). Du
modèle, il ne lit que `somme_ordonnee`. Il ne retient donc aucun jumeau, et
n'est pas à basculer.

**Ce qui ne change pas.** Aucun octet des témoins, des agrégats, du paquet ni
des pages : aucun fichier fabriqué n'est touché. Aucune garde, aucune règle du
scénario 1, aucune dépendance. Sans node, chaque confrontation s'arrête
(`pont.PontIndisponible`), sans repli sur le moteur Python : le test de l'arrêt
couvre `scenario_actuel` et `droit`.

**Tests.** `python -m pytest -m rapide`, 3 530 ; les confrontations légères,
`tests/test_pont.py` en entier et `tests/test_jumeaux.py`, 449 ;
`node --test tests/js/*.test.js`, 115 essais.

**Ce qui suit.** Le basculement de `test_oracle.py`, bloc par bloc, dans
l'ordre du tableau : chaque bloc déclare ses fonctions au pont
(`FONCTIONS_DU_DROIT`, `LECTURES_DU_DROIT`), les fait appeler par
`pont.droit` au lieu du jumeau, et garde le contrôle du Python par
`relu_du_droit`, au bit près ; les exemples officiels, qui bâtissent leurs
carrières par `carriere_simple` et lisent l'échéancier, la réversion et le
cumul, viennent les derniers. Puis le coût daté par le portage ; puis les
retraits, par sous-ensemble cohérent. D'autres confrontations, hors de cette
étape, simulent encore au moteur Python et retiennent ses jumeaux :
`test_trajectoire.py`, `test_ines.py`, les huit `test_oracle_*.py`,
`test_flux_fonction_publique.py`, `test_cycle_de_vie_references.py` ;
`scenario_actuel` et `droit` leur sont ouverts.
