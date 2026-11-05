# Étape 21, fin : le SRE lit la date d'effet, le modèle n'a pas à présumer la demande

**Le 5 novembre 2026, la demande.** Le propriétaire, depuis son poste : « On
peut tout faire ». Le dernier reste de l'étape attendait un poste qui atteigne
l'archive du web, et celui-ci l'atteint, sans rien lui demander.

**Ce qui a été lu.** L'actualité du Service des retraites de l'État
« Réforme 2010 – dispositif des carrières longues », du 7 avril 2011, à
l'archive du web (captures d'août 2011 à mai 2012). Les articles 43 et 118 de
la loi n° 2010-1330 et le décret n° 2010-1748 y valent pour toute demande de
retraite anticipée qui prend effet à compter du 1er juillet 2011, « quelle que
soit la date de dépôt de cette demande ».

**Ce que cela tranche.** L'article 118, III, parle des demandes déposées à
compter de cette date ; la caisse a lu la date d'effet. La table, qui applique
D. 16-1 aux pensions de juillet 2011, fait donc ce que la caisse faisait, et le
scénario 1 est ce que la caisse applique. La présomption de la date de la
demande, que la note du 24 octobre gardait en réserve, n'a plus d'objet. Le
décret n° 2010-1740, pour la CNRACL, dit de même « pensions liquidées ».

**Ce qui change.** La fiche
`duree_requise_carriere_longue_fonction_publique` perd son `a_relire` et gagne
la lecture. `tests/test_simulateur.py`,
`test_des_juillet_2011_la_date_d_effet_decide_quelle_que_soit_la_demande`,
tient le né de juin 1952 à cinquante-neuf ans et quatre mois, aux deux régimes :
vert dès l'écriture, le modèle avait raison. Ni pension, ni âge, ni témoin ne
bouge.

**Ce qui reste.** Rien à l'étape : son bloc « Reprise » est retiré.
