# L'ASV des auxiliaires médicaux : le taux plein à 65 ans, un coefficient par année d'âge

Le 20 novembre 2026, sur le constat de la relecture des régimes du même jour,
et selon la règle du propriétaire (« on corrige tout ce qui est faux »).

**Lu.** Règlement des prestations complémentaires de vieillesse de la
CARPIMKO, approuvé par l'arrêté du 10 juillet 2026 (JORFARTI000054435915, II),
relu mot à mot dans l'index du Journal officiel. Article 3 : « Etre âgé de 65
ans révolus ou de 60 ans en cas d'inaptitude au travail dûment constatée ».
Article 4 : dès 60 ans, « 0,75 si la pension est liquidée à l'âge de 60 ans »,
0,80 à 61 ans, 0,85 à 62 ans, 0,90 à 63 ans, 0,95 à 64 ans. Ni la durée
d'assurance ni le taux plein du régime de base n'y figurent.

**Le moteur** servait l'ASV sans coefficient à qui avait sa durée, et comptait
1,25 % par trimestre manquant aux autres.

**Corrigé.** Une fiche neuve, `asv_auxiliaires_medicaux_coefficients_d_age`,
à deux versions : le règlement de 2026, lu, depuis le 18 juillet 2026 ; la
même règle présumée avant, sur la foi du guide de la CNAVPL de 2025. Les
périodes du régime y renvoient (`abattement_points`,
`decote_annulee_par_la_duree`) : c'est le barème par année d'âge que le moteur
appliquait déjà à la CAVOM, sans une ligne de code de plus. L'inapte est au
taux plein dès 60 ans, l'ancien combattant à l'âge de sa fiche.

**Ce qui bouge.** Né le 10 mars 1964, entré à 17 ans, parti à 63 ans, au
salaire d'un Smic et demi : 1 297,93 points à 1,542606 €, soit 2 002,20 € par
an avant, 1 801,98 € après (0,90). Sept témoins du scénario 1, tous des
auxiliaires médicaux, baissent de 0,22 à 0,47 % de leur pension totale.

**Reste.** Depuis quand le barème vaut : les statuts d'avant 2026 ne sont pas
au Journal officiel. Le grand invalide de guerre et l'ancien déporté, que le
règlement sert sans coefficient dès 60 ans, ne le sont pas. L'ASV se liquide
toujours à la date de la complémentaire, quand le règlement lui donne sa
propre demande : la fiche le déclare en approximation. Les trois autres ASV
(chirurgiens-dentistes, sages-femmes, directeurs de laboratoire) portent la
même présomption et ne sont pas relus ici.
