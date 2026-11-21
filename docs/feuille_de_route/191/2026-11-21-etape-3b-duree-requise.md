# Étape 3 de la note 0009, deuxième session : la durée requise lue dans les versions de sa fiche

**Reprise, au 21 novembre 2026.** La durée requise pour le taux plein se lit
dans les huit versions de sa fiche : la date d'effet de la pension choisit la
version, la génération sa ligne. Les deux copies d'avant réforme et la table
qui les posait l'une sur l'autre sont parties. Aucun résultat ne bouge ; six
fiabilités changent de niveau. Restent à l'étape 3, chacune dans une session
neuve : la carrière longue, puis la surcote. Une pratique de la Cnav de 2011
reste dans le code, à migrer quand le contrat saura la dire. Commencer par
lire la note de l'étape suivante dans le résumé de la note de décision 0009.

Le 21 novembre 2026, la nuit, sur Opus 5.5, au choix du propriétaire, et non
sur Fable 5.2 que le dépôt règle pour le scénario 1 ; aucun point n'a demandé
de consulter Fable. Préparée sur la première session de l'étape, non encore
publiée, et remise au coordinateur en correctif, sans envoi sur `main`.
Quatre heures environ ; le coût en jetons n'a pas été mesuré.

**La fiche** (`duree_requise_par_generation.yaml`). Huit versions, bornées
sur la date d'effet de la pension, qui se suivent sans trou.

- Jusqu'au 1er janvier 1994 : 150 trimestres (R. 351-27 de 1985). Lue.
- Du 1er janvier 1994 au 1er janvier 2003 : l'escalier de R. 351-45, II,
  150 au né avant 1934, puis un trimestre par génération jusqu'à 159 au né en
  1942, 160 au-delà (R. 351-27 de 1993). Lue.
- Le 1er janvier 2003 seul : 159 au né en décembre 1942 (R. 351-45, III),
  160 aux autres. Lue.
- Du 2 janvier 2003 au 1er janvier 2009 : 160, « quelle que soit la date de
  naissance » (R. 351-45, I). Lue.
- Du 1er janvier 2009 au 22 janvier 2014 : la loi de 2003 (article 5, III),
  161 à 164 pour les nés de 1949 à 1952, puis les décrets de génération :
  n° 2010-1734 (165, 1953 et 1954), n° 2011-916 (166, 1955), n° 2012-1487
  (166, 1956), n° 2013-1155 (166, 1957) ; 160 aux nés avant 1949 (R. 351-27
  de 2009). Les lignes de la loi sont `haute`, le reste `certifiee`.
- Du 22 janvier 2014, du 1er septembre 2023 et du 1er septembre 2026 :
  L. 161-17-3 dans ses trois rédactions (2014, 2023, suspension). Lues.

Les tables viennent d'un fichier neuf, `duree_requise_par_version.csv`, que
le récupérateur `dila_legi_parametres_retraite.py` tire de l'index LEGI,
rédaction par rédaction, sans fusion, R. 351-45 partie par partie ; deux
certifications le recoupent (`verifier_donnees.py`), 30 et 4 lignes
identiques. Une valeur générale (150, 160) s'écrit en paramètre de la
version (`trimestres`), non en ligne de table.

**La loi de 2003 ne dit rien des nés à compter de 1958** : ses décrets ne les
avaient pas atteints le 22 janvier 2014. Aucun assuré né en 1958 ne pouvait
partir avant cette date (56 ans au plus tôt en janvier 2014). Mais une
liquidation fictive le peut : les droits acquis à une bascule de 2014, datés
du 1er janvier, avant la loi du 20 janvier. La pension prend alors la durée
du premier texte suivant qui fixe sa génération (`DureesRequises.deLaPension`) :
171 trimestres au né en 1971, ce que lui donnait la copie d'avant 2023. Une
carrière tirée au hasard par le test du site l'a montré : sans ce repli, 172,
et une pension figée de 1 452,78 euros devenait 1 446,03.

**Le moteur** (`moteur/js/regimes.js`, `droit/ouvrir.js`). `DureesRequises`
lit la fiche du paquet (`fiches_datees`) ; sans date d'effet, la dernière
version. Partis : `DureesRequisesAvantSuspension`,
`DureesRequisesAvantReforme2023`, `TableRecouverte` et huit constantes
datées, en JavaScript comme en Python, avec les deux copies
(`duree_requise_avant_reforme_2023.csv`, `duree_requise_avant_suspension.csv`)
et leurs clés du paquet. La retraite anticipée des handicapés, qui garde la
durée d'avant 2023, nomme sa version (`duree_d_avant_2023_version`). Les deux
couches remplacent la fiche (`remplacer_une_version`) : la version de 2014
sans fin, puis celle de 2023 sans fin ; 169 et 172 trimestres au né en juin
1965 parti en septembre 2027.

**La table par génération reste**, `duree_assurance_requise.csv`, que la
fabrique, le coût et la prose lisent : elle n'est pas une vue des versions,
mais elle leur est égale, l'escalier jusqu'à la génération 1942, la dernière
version au-delà (`tests/test_duree_requise.py`). Le dénominateur du prorata
(`duree_proratisation`) n'est pas touché.

**La pratique de la Cnav de 2011 reste au code** (`DUREES_AVANT_LE_DECRET`) :
aux nés de 1953 à 1955, la caisse opposait, jusqu'au décret de leur
génération, la durée de la génération d'avant (circulaire 2011/25). Le
contrat de la fiche ne sait pas dire une valeur qui dépend de la date de la
demande ; la constante garde sa place au cliquet, comme le brief l'admet. La
circulaire 2011/24, lue, ne contredit pas la 2011/25 : 164 au né en 1952, 165
aux nés de 1953 et 1954, la suite « en attente des décrets ».

**Ce qui bouge.** Aucune pension : 937 témoins de simulation, 86 rendus de
page, 60 carrières tirées au hasard, et une grille de 4 680 carrières simples
(générations 1925 à 1989, départs de 56 à 67 ans et demi, sous les trois
états du droit) identiques à l'octet. Six demandes du témoin du droit
changent, toutes de fiabilité, jamais de durée : `certifiee` au lieu de
`haute` pour les nés de 1945 à 1948 partis après 2009 (R. 351-27 de 2009, lu) ;
`haute` au lieu de `certifiee` pour les nés de 1934 à 1953 partis entre 2003
et 2008, la valeur de R. 351-45, I étant un paramètre de version et non une
ligne recoupée. Exemple : né en juin 1940, pension du 1er juillet 2003, 160
trimestres, `haute`. Ce dernier recul se lèverait en faisant lire le I par le
récupérateur.

**Les cliquets.** Copies d'avant réforme : zéro. Constantes datées : 175 à 167.
Couples réforme et fiche à classer : 93 à 91. Citations sans réponse : 433 à
432. Le témoin du droit garde ses 320 entrées que plus aucun test ne demande :
le refaire en entier les ôterait, et croiserait la file des envois.

**Reste.** Les versions de 1994 à 2008 n'ont pas d'exemple officiel
(exposé de la Cnav « Durée d'assurance pour le taux plein », circulaire
2008/41, non relus). Le test du tableau de bord (`test_justesse.py`) était
déjà rouge avant cette session : le tableau se refait sur GitHub.
