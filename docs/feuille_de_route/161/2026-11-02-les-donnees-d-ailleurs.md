# Le coût sous un modèle modifié, deuxième sous-étape : les données d'ailleurs — mesurées contre le droit contrefactuel, calculées par le portage sur leur paquet

**La demande.** La deuxième sous-étape du plan
(`2026-11-02-le-cout-sous-un-modele-modifie.md`) : `scripts/facteurs_depense.py
--sans-suspension` calculait par le moteur Python, sur la copie des données
que `reforme_entiere` récrit sous la réforme de 2023 entière, puisque
`pont.par_le_portage` renvoyait au jumeau toute racine autre que `data/`.
Mesurer d'abord le droit contrefactuel que le moteur connaît,
`Parametres.droit_contrefactuel = "loi_2023_sans_suspension"`, contre la
copie : au bit près, il la remplace ; sinon, le paquet se bâtit depuis la
copie, qui garde les nombres, et le propriétaire choisit.

**La confirmation du propriétaire, ce 2 novembre 2026.** Sur la frontière des
deux langages, il veut « tout ce qui est présent côté utilisateur en
JavaScript », et le précise : ce que le visiteur utilise — le simulateur de sa
carrière, les formulaires, les pages. Il confirme ainsi le plan des notes de
décision 0005 et 0006 : les grands totaux — le coût, les carrières types, le
bilan — restent fabriqués en Python et lus au paquet.

**La mesure.** La colonne « sans la suspension », `modele("cor_reference")`,
calculée deux fois : sur la copie, par le moteur Python, en 91 secondes ; sous
le droit contrefactuel, sur les données du dépôt, par le portage, en 30. Sur
ses 94 nombres, 77 diffèrent : les retraités de 2022, 16 543 933 sur la copie
et 16 543 795 sous le contrefactuel ; la dépense de 2070, 15,782 et 15,781
points de PIB ; sur 2022-2030, la variation de la dépense, +0,422 et +0,431
point, l'effet de la prestation, −0,170 et −0,161. La ligne « la suspension »
du départage de la couverture ne bouge qu'à la quatrième décimale, 0,0608 et
0,0609 point. Deux écarts de construction séparent les deux calculs, sans que
la session ait mesuré la part de chacun : le contrefactuel ôte de plus à la
carrière longue les décrets qui prennent effet à compter du 1er septembre
2026 (`CarriereLongue.avant`), que la copie garde ; la copie récrit la durée
requise que lit aussi la complétude des générations (`CarrieresIncompletes`,
171 et 172 trimestres pour 1964 et 1965 au lieu de 170), quand le paramètre ne
change que le moteur du scénario 1. Pas au bit près : la copie reste, et le
choix va au propriétaire.

**Le paquet des données d'ailleurs.** `pont.paquet_des_donnees(racine)` bâtit
depuis une autre racine ce que la fabrique bâtit depuis `data/` :
`scripts/construire_donnees.py`, dans un processus à lui, sa constante
`DONNEES` prise à la racine, une fois par état des fichiers de celle-ci et des
sources (`_signature_des_fichiers` : le chemin, la taille et la date de
chacun, sans les lire). Trois secondes ; bâti depuis la copie de
`--sans-suspension`, il ne diffère du paquet du dépôt que par `ages_ouverture`,
`durees_requises` et `population`, et celui du dépôt, bâti de même, est
celui du pont à l'octet. Une garde l'empêche de rien lire des données du
dépôt : un crochet d'audit relève ce que la fabrique ouvre ou liste sous le
`data/` du dépôt, et le processus s'arrête s'il y a lu quoi que ce soit. Bâti
depuis `data/` même, le crochet y voit 389 chemins ; depuis la copie, aucun.

**L'aiguillage.** `pont.par_le_portage` dit oui sur toute racine : seul
`pont.par_le_jumeau()` renvoie au moteur Python. Les six demandes du coût qui
prenaient le paquet du jour prennent celui de la racine de leurs paramètres —
`cout._simulations`, `cout._grille_batie`, `facteurs_depense.dates_des_departs`
et les trois du coût des avantages —, et les sept demandes du pont qui
reçoivent des paramètres passent par `_paquet_de` : sur des données d'ailleurs,
sans paquet, le pont prend le leur ; un autre, il le refuse. Le défaut qu'elle
ferme était latent : une demande sans paquet, sur des données d'ailleurs, se
calculait en silence sur `moteur/donnees.json` — son test l'a vu rougir, la
génération 1968 d'une copie retouchée lue à l'âge légal du dépôt, 63 ans et
9 mois, et non au sien.
Aucun script n'y passait encore : le coût des avantages et les grilles
renvoyaient au jumeau toute racine d'ailleurs.

**Ce qui ne change pas.** Aucune règle, aucune donnée, aucun chiffre publié :
`--sans-suspension` n'a ni sonde ni chiffre ancré, aucune étape de la
fabrique ne le lance, et le jumeau rend sur la copie, au bit près, ce que le
portage y rend. Les données du dépôt suivent le chemin d'avant : leur paquet,
la mémoire des calculs, le pont gardé ouvert.

**Tests.** Vus rouges d'abord, cinq de `tests/test_pont.py` :
`test_sur_des_donnees_d_ailleurs_le_cout_calcule_par_le_portage` (l'aiguillage
disait non), `test_des_donnees_d_ailleurs_ont_leur_paquet` (le paquet ne
prenait pas de racine), `test_le_paquet_de_donnees_d_ailleurs_ne_lit_rien_de_celles_du_depot`
(une fabrique d'essai qui lit le `data/` du dépôt par un chemin écrit en dur ;
la garde manquait), `test_des_donnees_d_ailleurs_se_calculent_sur_leur_paquet`
(le défaut latent) et
`test_sur_des_donnees_d_ailleurs_le_cout_date_bat_et_simule_sa_grille_par_le_portage`
(le jumeau datait la grille de la copie ; elle est la sienne au bit près, et
le salarié au salaire moyen né en 1968 y part en 2034, non en 2032). Puis,
dans `tests/test_facteurs_depense.py`, sur la copie même de
`--sans-suspension`, vus rouges par contre-épreuve, le changement retiré :
`test_sans_la_suspension_les_cohortes_se_datent_au_portage_sur_la_copie`
(rapide ; les générations 1964 et 1965 y partent en novembre 2027 et en
février 2029, et non en août 2027 et 2028, le premier jour du mois qui suit
l'âge de leur durée, R. 351-37) et
`test_sans_la_suspension_le_modele_se_refait_au_portage_comme_au_jumeau`, le
test du plan, à GitHub (2 min 14 s ici) : chaque colonne du modèle refait sur
la copie, portage contre jumeau, au bit près. `tests/outils_pont.py` gagne
`empecher_les_jumeaux_du_cout`, que les deux tests de la grille par le portage
partagent avec eux, et `ecarts_d_ecriture` écrit un chemin dont une clé est une
année.

**La question du 31 octobre.** « Garder cette relecture, ou faire rendre un
flottant au jumeau Python ? », posée par la session des confrontations par le
pont (`2026-10-31-etape-6-les-confrontations-par-le-pont.md`) : close. Le
propriétaire a tranché le jour même, garder la relecture par
`pont.relu_du_droit`, le jumeau intact (`2026-10-31-etape-6-test-oracle-par-le-pont.md`).

**Soumis au propriétaire.** La colonne « sans la suspension » de l'étude
contre l'Ageing Report : passer au droit contrefactuel du moteur, qui en
déplace les nombres de quelques millièmes de point de PIB, et retirer la copie
retouchée des données ? Oui, une session remplace la copie par le paramètre ;
non, la copie reste, calculée par le portage.

**Ce qui reste.** Les sous-étapes 3 à 6 du plan, une par session : la
proposition prospective en univers, le stock à l'âge légal, le régime unique
par barème, puis le levier `pont.par_le_jumeau()` réservé aux confrontations.
