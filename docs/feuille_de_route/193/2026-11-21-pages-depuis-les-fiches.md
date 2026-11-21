# Les caisses et les droits non cotisés, fabriqués depuis les fiches

Le 21 novembre 2026, le propriétaire veut que « Les caisses » et « Droits non
cotisés » montrent tout, sans rien recopier de ce que le modèle sait.

**Ce qui est fait.** La table des régimes de l'inventaire (114, une ligne par
fichier de `data/reference/regimes/`, lue au paquet sous `inventaire`) quitte
Méthode pour « Les caisses », sous un dépliant `les-regimes` dont le titre
compte ce que le modèle calcule (« 36 calculés en entier, 44 en partie »).
Chaque ligne dit sa couverture en mots simples (« calculé en entier », « en
partie », « pas encore calculé », « calculé par un autre régime », « hors
champ ») et cite ses textes, liés à Légifrance par leur identifiant DILA
(`adresseLegifrance`) ; la colonne des statuts part. Méthode y renvoie, depuis
la fiche « Régimes recensés », et l'accueil aussi. Sur « Droits non cotisés »,
chaque dispositif porte « calculé, chiffré », « calculé, chiffré à part »,
« déclaré, pas encore calculé » ou « pas encore calculé », et la réversion,
servie au seul conjoint déclaré, « calculé en partie » (champ
`servi_en_partie`, venu du chantier des droits non cotisés du même jour, sur
lequel ce travail est posé). Le paquet ne change pas, aucun témoin de
simulation ne bouge ; le budget déplié de la page passe de 7 650 à 7 700 mots.

**Les tests.** Sept, dans `test_page_caisses.py`, vus rouges : chaque régime de
l'inventaire et chaque régime du catalogue a sa ligne et son statut ; le titre
compte juste ; chaque texte est cité et lié ; la table n'est qu'à un endroit ;
chaque dispositif, et chaque code qu'une fiche déclare, est sur « Droits non
cotisés ». Deux tests de `test_web_revues.py` suivent la table.

**À savoir.** « Les caisses » passe de 110 à 288 Ko, la table étant repliée.
Les adresses `loda/` et `codes/` se choisissent sur la référence : un texte
mal rangé donnera un lien mort, pas un faux texte.
