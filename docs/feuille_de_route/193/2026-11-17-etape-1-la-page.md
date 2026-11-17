# Étape 1 : la page « Les caisses »

Le 17 novembre 2026, à la demande du propriétaire, qui a validé la maquette
(gardée dans le dossier partagé du projet, `maquettes/les-caisses.html`) et
choisi de l'intégrer au site.

**Ce qui est fait.** Une dixième page, `caisses/`, rangée au bandeau en tête
du groupe « Pour vérifier ». Dix-huit caisses, rangées par famille (salariés
du privé, fonction publique, indépendants et libéraux, agriculture, régimes
spéciaux), chacune une bulle dont la surface suit le nombre de ses retraités.
Chaque bulle mène, par `data-vers`, au dépliant de sa caisse, que le routeur
ouvre. La fiche répond à cinq questions ; les chiffres viennent du paquet.

**Les données.** `donnees/caisses_du_site.py` lit, à une année fixe chacun,
les cotisants et les retraités de 2024 (`cotisants.csv`,
`retraites_projetes.csv`, COR juin 2024), la structure de financement de 2023
regroupée en six postes (`structure_financement.csv`), les réserves de fin
2025 (`reserves_regimes.csv`, COR juin 2026) et le prix, la valeur et le taux
d'appel du point de 2026 (`valeurs_point.csv`). `construire_donnees.py` les
met au paquet sous `caisses` ; la version du paquet passe à 45.

**Les tests.** `tests/test_page_caisses.py` recoupe chaque donnée à sa
source, lue à la main, et la page : chaque caisse, sa bulle et sa fiche, le
rapport de la CNRACL, la part de l'État pour la SNCF, ce que rapportent
100 euros cotisés à l'Agirc-Arrco (100 ÷ 1,27 ÷ 20,1877 × 1,4587), l'ordre
des fiches. Les listes de pages des tests, de Lighthouse, de la fabrique et
du plan du site comptent la dixième.

**Ce qui reste.** Les curseurs de la maquette (étape 2) ; les montants versés
par chaque caisse, que le dépôt n'a que pour certaines (étape 3) ; l'histoire
« Où va votre argent ? » (étape 4), que le propriétaire n'a pas encore
retenue. Le texte de chaque fiche reste à relire avec lui.
