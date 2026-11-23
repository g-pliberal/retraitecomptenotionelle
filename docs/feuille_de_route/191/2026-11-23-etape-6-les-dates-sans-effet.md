# Le passage au jour, second lot : vingt et une dates lues au texte

**La demande.** Finir l'étape 6 de la séparation des axes (note de décision
0009) : poser les dates qui ne changent aucun résultat, corriger les quatre
défauts que le premier lot avait laissés, puis dater les taux de cotisation
qui changent en cours d'année. Sur Fable 5.2, relue sur Opus 5.5 dans un
contexte neuf, qui a confirmé les vingt et une dates. Ce lot fait la première partie et deux des quatre défauts.

**La méthode.** Chaque date est lue dans l'index de la DILA, à la phrase qui
dit à quelles pensions le texte s'applique (`dila_cherche.py legi --num …
--le`). La sonde du premier lot, élargie à une mère et à un père de trois
enfants, puis les 935 cas témoins disent si la date change un résultat. Une
date ne se pose que si le texte est lu, et si la règle d'avant elle l'est
aussi.

**Posé, sans qu'aucun cas témoin bouge.** `tests/test_frontieres_au_jour.py`
tient la liste et cite chaque texte.

- Le 1er juillet 2011, au lieu du 1er janvier : le régime général, les
  salariés et les exploitants agricoles, les fonctionnaires de l'État, la
  CNRACL, les ouvriers de l'État et l'Ircantec. Loi n° 2010-1330,
  article 118, II : « pensions prenant effet à compter du 1er juillet 2011 ».
- Le 1er septembre 2023, au lieu du 1er janvier : le régime général, les
  salariés agricoles, les fonctionnaires de l'État, la CNRACL et les ouvriers
  de l'État. Loi n° 2023-270, articles 10 et 11.
- Le 1er décembre 1964 pour les fonctionnaires de l'État (loi n° 64-1339,
  article 1er) ; le 1er avril 1983 pour l'Ircantec (arrêté du 27 janvier
  1983) ; le 1er juillet 1992 pour les mines, première date de la série de
  leur barème ; le 3 juin 2011 pour la retraite additionnelle de la
  fonction publique ; le 30 juin 2011 pour la CAVP et pour les prestations
  complémentaires des directeurs de laboratoire ; le 10 janvier 2024 pour la
  CARPIMKO.

**Corrigé : la caisse des avocats, au 1er septembre 2023.** L. 653-3, créé
par l'article 21 de la loi n° 2023-270, étend L. 351-12 aux avocats pour les
pensions « prenant effet à compter du 1er septembre 2023 » ; la ligne ne
commençait qu'en 2024. Un avocat né en août 1956, père de trois enfants,
entré à vingt-sept ans et parti à soixante-sept ans le 1er septembre 2023 :
sa pension de base de 17 527,36 € par an reçoit 1 752,74 € de majoration,
qu'il n'avait pas. La caisse écrit « au 1er octobre 2023 ou postérieure » :
si ses pensions de base ne partent qu'au trimestre civil, ce qui n'est pas
lu, le cas du 1er septembre n'existe pas chez elle.

**Corrigé : la base des libéraux, au 1er avril 2010.** L. 643-1-1, créé par
l'article 65 de la loi n° 2009-1646, donne la majoration de durée pour enfant
aux pensions « prenant effet à compter du 1er avril 2010 » ; la ligne
commençait en janvier. L'exemple de la fiche
`cnavpl_majoration_duree_assurance` : une libérale née en janvier 1949, mère
de deux enfants, entrée à vingt-quatre ans et partie le 1er février 2010.
Elle recevait seize trimestres que le texte ne lui donne pas, et une pension
de base de 8 258 € par an ; elle a 148 trimestres, une minoration de 22,75 %
et 6 239,22 €. Partie le 1er avril, elle a les 164 trimestres.

**Essayé, retiré : la CAVP au 7 juin 2009.** Les statuts de l'arrêté du
11 mai 2009 valent le 7 juin. Mais ceux d'avant ne sont qu'au Bulletin
officiel, et la ligne d'avant 2009 sert à leur place la décote du régime de
base, que la durée annule. Poser la date ôte l'abattement de 5 % à deux cas
témoins (le pharmacien et le biologiste nés en 1945, partis à soixante-quatre
ans au premier semestre 2009), sans qu'aucun texte lu le dise. La date reste
au 1er janvier 2009 tant que les statuts d'avant ne sont pas lus.

**Essayé, retiré : l'ASV des médecins au 15 février 1985.** La rédaction qui
demande un an d'exercice vaut ce jour-là (LEGIARTI000006765959), et celle
d'avant en demandait dix. Mais la ligne d'avant n'en demande aucun : poser la
date étendrait de six semaines une règle fausse. Elle se posera avec la
condition des dix ans. Relevé par la relecture sur Opus 5.5.

**Laissé, faute de texte lu.** L'Agirc, l'Arrco et leurs variantes au
1er avril 1983 (accord du 4 février 1983) et au 1er juillet 2011 (accord du
18 mars 2011) : ni l'un ni l'autre n'est dans KALI. La Banque de France en
2011, la Comédie-Française en 2012 et l'Opéra en 2014 : leurs âges et leurs
durées se lisent à la génération, et la date de la rédaction n'a pas été
relue. Les ouvriers de l'État en 1964 : le décret n° 65-836 n'est qu'en
notice. La CRPCEN en 2008, à couper en deux, le 18 février et le 1er juillet.
Le calendrier des réformes garde trois dates de publication à corriger d'un
jour ou de quelques-uns : le 26 décembre 1964, le 29 juin 2011, le 9 janvier
2024.

**Reste des quatre défauts.** La surcote de la base des libéraux : R. 643-8
donne « 0,75 % par trimestre accompli avant le 1er septembre 2023 et 1,25 %
par trimestre accompli à compter de la même date ». Le barème daté existe
(`surcote_baremes.csv`), mais la branche en points du moteur ne le lit pas
(`surcotePoints`, mode `regime_general`) ; et le texte ne dit pas le taux du
trimestre civil de juillet à septembre 2023. Les droits d'avant 1973 des
artisans et des commerçants au 1er juillet 1984 : rien de fait.

**Les taux de cotisation en cours d'année : non commencé.** Le dépôt date
tout taux au 1er janvier, et le dit (`taux_cotisation_annuels.csv` : « un
relèvement du 30 juillet ne commande que l'année suivante »). L'acquisition
se compte à l'année : un taux changé en cours d'année demande une moyenne
pondérée par les mois, pour tous les régimes et toutes les années, et
déplace le compte notionnel de presque tous les cas témoins. C'est une
décision du propriétaire.

**Les compteurs.** Aucune ligne n'est ajoutée : le compteur des valeurs de
repli reste à 370.
