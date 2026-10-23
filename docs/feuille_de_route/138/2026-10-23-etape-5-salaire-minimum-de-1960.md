# Étape 5, dix-septième partie : le salaire minimum de 1960, lu au Journal officiel des débats, et les autres montants du minimum garanti, cherchés sans être trouvés

**La demande.** La vague du 23 octobre 2026 : la session de suivi « Qu'est-ce
qu'il reste à faire ? » lance, sur la demande du propriétaire (« Fait ça »),
douze sessions en parallèle, une étape chacune. Celle-ci : les montants non
lus de l'exonération au minimum garanti (art. 5, 2°), de 1960 à 1970 et de
1972 à 1992, le point « une session » du bloc de l'étape ; un montant qui ne
se lit qu'au fac-similé du Journal officiel se déclare ; les décisions du
bloc restent au propriétaire.

**Où les textes se lisent.**

- *L'Assemblée nationale*, à ses archives (archives.assemblee-nationale.fr),
  qui gardent en PDF, avec leur texte, le Journal officiel des débats : les
  1 245 numéros des questions écrites et des réponses des ministres, de 1959
  à 1994 ; les 2 573 comptes rendus des séances de 1958 à 1975, où
  paraissent aussi des réponses ; les tables analytiques de 1958 à 1992. Le serveur
  n'envoie pas son certificat intermédiaire : il se prend chez son autorité
  (cacerts.digicert.com, GandiCert), et la chaîne se vérifie.
- *Le Sénat* : les rapports généraux sur les lois de finances pour 1974 à
  1990 et pour 1993, tome II ; le projet de 1959 en deuxième lecture
  (ta1959_1960_0016.pdf) ; les tables annuelles des questions écrites de 1960
  à 1986 (u1960.pdf à u1986.pdf), et les comptes rendus de 1967 ; la base des
  questions de data.senat.fr, depuis 1978, leur texte depuis 1986.
- *Les archives du BOFiP* : de la série 5 B, rien d'avant 1995.
- Refusés au réseau de la session : Légifrance et Gallica (403).

**Ce que disent les textes.**

- *La loi de 1959.* Le Sénat avait adopté en première lecture « Les
  contribuables salariés dont l'unique revenu n'est pas supérieur au salaire
  minimum interprofessionnel garanti ne sont pas assujettis » (art. 13,
  dernier alinéa), le texte que citait la donnée. L'Assemblée nationale lui
  substitue en deuxième lecture l'amendement n° 28 de M. Marc Jacquet : « Les
  contribuables qui bénéficient principalement de traitements, salaires,
  pensions et rentes viagères, et dont le revenu global n'est pas supérieur
  au salaire minimum interprofessionnel garanti, ne sont pas assujettis à
  l'impôt sur le revenu des personnes physiques », pour « préciser le sens de
  l'alinéa 3 [...] en ce qui concerne les rentiers-viagers » (JO, débats,
  séance du 9 décembre 1959, p. 3243) ; le Sénat vote l'article 13 conforme le
  17 décembre (ta1959_1960_0016.pdf, p. 5) ; il est l'article 17 de la loi,
  dit le ministre en 1961. Le texte qui étend l'exemption aux pensions, que
  la note du 19 octobre ne lisait pas, est la loi elle-même.
- *1960.* La question écrite n° 10046 de M. Cance (JO, débats de
  l'Assemblée nationale, 28 avril 1961, p. 554) cite une note de la direction
  générale des impôts du 1er mars 1961 : « le revenu global à comparer au
  montant annuel du S. M. I. G. doit s'entendre avant application de la
  réfaction forfaitaire [...] les revenus exonérés de 3.250 NF en 1959 et
  3.360 NF en 1960, indiqués par la note susvisée ». Le ministre répond
  (16 juin 1961, p. 1131) que l'abattement de 20 % « ne saurait [...] être
  considéré comme intervenant dans l'appréciation de ce revenu pour le
  comparer au S. M. I. G. », et qu'« il n'est pas envisagé de modifier le sens
  des instructions susvisées ».
- *1965.* Un sénateur écrit qu'« un retraité célibataire peut bénéficier de
  ces dispositions jusqu'à concurrence de 4.110 F en 1965 », un ménage de
  8 220 F devant 485,50 F d'impôt (question n° 6549 de M. Auguste Pinton, JO,
  débats du Sénat, 5 février 1967) ; la réponse (18 octobre 1967, p. 973) ne
  parle que de la réduction de 5 %. Un chiffre sans sa source, que
  l'administration ne reprend pas : la donnée ne le prend pas.
- *Le reste.* Aucune autre réponse, aucun débat ni aucun rapport ne chiffre
  le seuil, de 1961 à 1970 ni de 1972 à 1992 : les rapports généraux du Sénat
  ne commentent que les limites d'exonération des lois de finances (le
  2° bis), et les réponses sur les salariés au SMIC, ces limites.

**Ce qui est fait.**

- `scripts/fetch/ipp_impot_revenu.py` : la marche de 1960 porte 3 360 NF,
  `origine: question`, et cite le texte définitif de la loi
  (`LOI_DE_1959_SALAIRE_MINIMUM`), la note que cite la question et la
  réponse ; une marche de 1961 sans montant. La donnée refaite ne gagne que
  ces deux marches.
- `impot_revenu.py` et son jumeau : la remarque d'un foyer sous le minimum
  garanti avant 1993 dit ce qui chiffre le seuil
  (`SEUILS_DU_MINIMUM_GARANTI_CITES`) — pour 1960, une question écrite qui
  cite une note de l'administration ; pour 1971, un rapport du Sénat ;
  `HORS_CHAMP` dit 1961 à 1970.
- Les tests, vus rouges avant le code, valeurs des textes : le montant de
  1960, et nul de 1961 à 1970 ; en 1960, un salaire et un bénéfice de 3 360 NF
  ne paient rien, de 3 370 NF paient ; le salaire comparé avant les 20 %
  (3 330 NF nets exonérés, 3 420 NF non) ; la pension ; la remarque ; la
  marche qui cite l'amendement n° 28 ; 1961 sans montant. La grille des deux
  moteurs exonère l'invalide de 1960, et leur confrontation a rougi sur la
  remarque avant le portage. Au registre des référents, IR13.

**Ce que montrent les mesures.** En 1960, de 205 foyers qui ne vivent que de
salaires ou de pensions, de 2 000 à 6 000 NF — seuls, retraités de 62 et de
70 ans, en couple, parent —, 80 tombent sous le seuil, et aucun impôt ne
change : la franchise et la réduction de 5 % les dispensaient déjà, le premier
impôt d'un salarié seul naissant à 3 771 NF nets (4 190 NF bruts), celui d'un
retraité seul à 3 770 NF, comme le disait la question de 1961 (« déjà
exonérés jusqu'à [...] 3.000 NF », le revenu après les 20 %). Le bénéfice mêlé
au salaire est imposé plus tôt : de 806 personnes seules, de 1 500 à 4 000 NF
de salaire et jusqu'à 3 000 NF de bénéfice, 232 sont exonérées, et 51 y
gagnent de 1,20 NF à 145,60 NF (1 900 NF de salaire, 1 710 NF nets, et
1 600 NF de bénéfice).

**Ce qui reste** de l'étape, dans l'ordre :

1. *Au propriétaire* : l'impôt dans les cartes de résultats, l'effet retour
   dans le solde, les trois décisions sur le bénéfice (note de l'impôt au
   site) ; la loi qui porte la décote à 70 F et 210 F par part, et le texte
   définitif de la loi de finances pour 1962 (le taux de 6 % des revenus de
   1961), depuis un poste.
2. *Les montants non lus*, 1961 à 1970 et 1972 à 1992. Aucun ne se lit au
   Journal officiel : ni aux débats de l'Assemblée, parcourus ici au texte
   de leur numérisation (les questions de 1959 à 1994, les séances de 1958 à
   1975), ni dans ce que les tables du Sénat en signalent ; le fac-similé des
   lois et décrets ne porte
   que les valeurs horaires du SMIG et du minimum garanti, dont aucun texte
   lu n'écrit la règle qui fait le montant annuel. Ils sont dans la doctrine
   de chaque année, dont la note du 1er mars 1961 est le modèle, et
   qu'aucune archive en ligne lue ne garde ; Gallica, refusée ici, est à
   essayer depuis un poste. Le montant compte de 1961 à 1970, et en 1972, où
   l'exonération des salariés à 9 500 F ne couvre ni les pensions ni le
   salaire mêlé d'un bénéfice ; de 1973 à 1992, seulement s'il dépasse la
   limite du 2° bis, ce qu'il ne fait d'aucune année lue. Ceux de 2011 à
   2013, aux versions de 2012 à 2014 du BOFiP, sans effet ; la loi de finances
   pour 2015, art. 2.
3. *La taxe complémentaire, ce qui n'est pas lu* (point 3 de la note de la
   taxe), le seuil de recouvrement d'avant 1977 et d'avant 1970, les points 6
   à 10 de la note sur les lois de finances de 1974 à 1981.
