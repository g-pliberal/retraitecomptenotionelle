# Étape 5, suite : l'impôt sur le revenu confronté au calcul officiel de la DGFiP

**La demande.** Le propriétaire, le 21 novembre 2026 : OpenFisca s'étant
trompé sur les pensions, vérifier l'impôt du moteur sur un outil officiel de
l'administration plutôt que sur lui. Essai borné : ce qui est disponible, une
cinquantaine de foyers, les écarts, le coût d'un contrôle permanent ; corriger
sans attendre ce qui est contraire à la loi.

**Ce qui est disponible.** Le code M de la DGFiP (dépôt `ir-calcul` de
l'Adullact, revenus 2010 à 2025), que Mlang exécute pour les revenus 2019 à
2025 seulement ; le simulateur d'impots.gouv, revenus 2015 à 2025 ; rien
d'officiel et d'exécutable avant 2010.

**Ce qui a été fait, en trois envois.**

1. *Le plafond de l'abattement des pensions* (art. 158, 5, a du CGI). Un couple
   de retraités au plafond voyait ses deux abattements arrondis chacun à
   l'euro, et leur somme dépasser le plafond d'un euro (2022 : 6 952 € au lieu
   de 6 951 €). Le calcul de la DGFiP donne à la dernière part le reste du
   plafond (variable APRC) ; le module et son portage font de même depuis 1998,
   la règle d'avant 1998 arrondissant chaque base au centime (art. 1657, 1).
   La borne de 1998 est une déduction du texte, aucun calcul officiel ne
   tournant avant 2010.
2. *Le témoin officiel* : `tests/temoins/impot_revenu_dgfip_m.json`, 329
   foyers-années figés (47 foyers, 2019 à 2025), refait chaque année par
   `scripts/fetch/dgfip_m_impot_revenu.py`, qui dit la procédure (Mlang,
   sources de l'année, réparation des fichiers `m_ext` de 2024 et 2025). Le
   moteur s'y accorde à l'euro sur les sept grandeurs, aucun désaccord
   déclaré. OpenFisca reste témoin de 2002 à 2018, avec deux défauts déclarés
   au registre des référents : l'âge de 65 ans lu au premier mois, et le
   plafond des pensions. Le simulateur d'impots.gouv, vu sur neuf cas de 2015
   à 2018 et de 2024, s'accorde aussi.
3. *L'année blanche de 2018* : loi n° 2016-1917, art. 60, II
   (JORFARTI000033734238), décalée d'un an par l'ordonnance n° 2017-1390. Le
   crédit d'impôt de modernisation du recouvrement efface l'impôt des revenus
   non exceptionnels de 2018, que le cycle de vie comptait. Il s'écrit en
   donnée, la série `credit_modernisation_recouvrement` de
   `impot_revenu.yaml`, et le module et son portage le retranchent. Exemple :
   21 000 € de salaire en 2018, impôt de 794 € avant crédit, 0 € après ; 2017
   et 2019 ne bougent pas.

**Ce qui bouge.** Aucun des 937 témoins de simulation ; seize rendus de la
page « Simuler » sur 86, chacun à la seule ligne 2018 des revenus autour du
départ ; rien au coût.

**Limite déclarée.** Pour un indépendant, la loi ne tient pour non
exceptionnel que le bénéfice de 2018 borné par celui des trois années
d'avant ; le module efface tout le bénéfice de 2018.

**Relectures.** Les deux premiers envois relus sous Fable 5.2 ; l'année
blanche relue sous Opus 5.5, Fable étant indisponible jusqu'au 25 novembre.

**Ce qui reste.** Les revenus 2010 à 2018 au calcul officiel, qui demandent
une version ancienne de Mlang ; le signalement des deux défauts à OpenFisca.
