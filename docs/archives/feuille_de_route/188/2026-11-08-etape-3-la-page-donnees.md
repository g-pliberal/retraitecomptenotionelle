# Étape 3 : les gestionnaires sur la page Données

**Ce qui est fait.** La table des régimes de la page Méthode — sa seconde
partie, « D'où viennent les chiffres », l'ancienne page Données — gagne une
colonne, « Géré par », juste après le nom du régime : le nom de chaque
organisme qui le gère, et, quand il confie sa gestion à un autre, « gestion
confiée à : » suivi du nom de celui-là (la CNRACL, l'Ircantec, le FSPOEIE,
l'ERAFP et deux caisses fermées à la Caisse des dépôts ; le CPSTI à la Cnav).
Le champ de recherche, qui promettait déjà « un nom, un statut, une
caisse… », trouve désormais une caisse. Le chapeau de la table dit ce que la
colonne nomme, renvoie au référentiel et compte : 54 organismes gèrent les
83 régimes encore en vie, un compte que la page fait sur l'inventaire.

**Le paquet.** Il porte le référentiel (`gestionnaires` : le nom de chaque
organisme et son opérateur, sans les notes), que `construire_donnees.py`
tire de `charger_gestionnaires` ; les lignes de l'inventaire n'en portent que
les codes. La structure change, et sa version monte des deux côtés, de 41 à
42 (`VERSION`, `VERSION_PAQUET`) : un navigateur qui garde l'ancien paquet le
redemande.

**Les tests.** `test_l_inventaire_nomme_le_gestionnaire_de_chaque_regime`
(`tests/test_web_revues.py`), vu rouge : chaque ligne nomme ses
organismes, la SEITA l'APC, la CNRACL la Caisse des dépôts, le régime
général aucun opérateur, et la phrase de compte suit l'inventaire ; la table
compte huit boutons de tri au lieu de sept ; le paquet porte la CNRACL et
son opérateur (`test_le_paquet_contient_les_donnees_du_modele`).

**Le budget.** Tout dépliée, la page Méthode passait à 5 678 mots pour 5 650
au plus. Le budget n'a pas bougé : le chapeau de la table a perdu ce qu'il
disait d'un test (« une fiche sans ligne d'inventaire, ou une ligne qui
prétend calculer ce qu'aucune fiche ne calcule, fait échouer les tests »), et
la phrase neuve s'est resserrée ; la page tient, à quelques mots près.

**Vu dans le navigateur.** La table, trop large pour huit colonnes, se replie
en fiches au large comme au téléphone, « Géré par » sous le nom ; rien ne
déborde (`tests/test_ecrans.py`, vingt-quatre cas). Aucun témoin de
simulation ne bouge ; seul le rendu de la page Méthode change.
