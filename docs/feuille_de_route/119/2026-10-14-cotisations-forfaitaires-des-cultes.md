# Les cotisations de la CAVIMAC de 1979 à 1997 : deux montants par arrêté, et non le SMIC

**Le 14 octobre 2026 : de 1979 à 1997, le régime des cultes appelait, par
assuré non retraité, deux montants fixés chaque année par arrêté — la
cotisation forfaitaire de l'assuré et la solidarité de sa collectivité —, que
le compte notionnel porte désormais
(`legislation/cultes_cotisations_forfaitaires.csv`), au lieu du forfait du
SMIC aux taux du régime général. Le scénario 1 ne bouge pas ; les ministres et
les religieux des témoins, dans les scénarios notionnels, de −24 % à +65 %.**

Demande du propriétaire, pour la session de nuit : « action 119, les
cotisations forfaitaires de la CAVIMAC de 1979 à 1997, le dernier reste de
l'action. Commence par la dernière question de la fiche
`cultes_fractions_de_pension`, texte en main. »

- *La règle.* Le décret n° 79-607, art. 24, puis R. 721-29 du code de 1985 :
  la cotisation de l'assuré « correspond[ait] à la cotisation d'assurance
  vieillesse qui serait due pour le compte d'un assuré du régime général
  percevant un salaire lui permettant d'acquérir à soixante-cinq ans, pour la
  durée maximum d'assurance », la pension maximum — soit le taux TOTAL du
  régime général sur deux fois le maximum : 12,9 % de 18 200 F en 1980,
  2 348 F, la valeur de l'arrêté, 13,9 % de 30 900 F en 1984, 4 295 F.
  L'article 25, puis R. 721-30 : la solidarité des collectivités, « fixée
  chaque année de manière à assurer l'équilibre du régime compte tenu
  notamment des charges » des périodes d'avant 1979, « due pour tout assuré non
  retraité ». En 1995, la charge passe de l'assuré (7 304 F en 1994, 2 960 F en
  1995) à la collectivité (858 F, puis 5 300 F), le total à peu près constant.
- *Les montants.* Les arrêtés de 1983 à 1997, article par article, dans
  l'index LEGI ; ceux de 1980, 1981 et 1991 par le résumé ou le titre que
  l'index JORF en garde ; l'assuré de 1979 (1 935 F) par le titre de l'arrêté
  du 8 janvier 1980. Estimés : la solidarité de 1979, au rapport de 1980, et
  les deux montants de 1982, dont l'arrêté n'est pas dans l'index. Le compte
  portait 25 % de trop de 1983 à 1997, 20 % de moins de 1979 à 1982.
- *Le modèle* (`moteur/compte.py` et `compte.js`, `CotisationsDesCultes`) :
  sous la convention salariale, la cotisation de l'assuré ; sous la totale, les
  deux, la solidarité comptée en part employeur.
- *Un défaut voisin, réparé.* La part déplafonnée du régime général, que la
  CAVIMAC reprend (1,6 % de 1992 à 1997), était prélevée sur le revenu saisi de
  l'assuré, quand le régime cotise sur un forfait : elle se prend désormais sur
  le forfait du SMIC depuis 1998, et pas du tout avant, les arrêtés la
  comprenant.
- *En passant, le maximum de pension.* Les arrêtés de 1984 et de 1986 sont dans
  l'index LEGI, que le fichier croyait réduits à leur titre : 15 450 F et
  17 300 F, au lieu des 15 474 F et 17 220 F de la moyenne géométrique. Pour
  1983, le texte consolidé écrit 14 250 F, le résumé du Journal officiel
  14 252 F, que la cotisation de l'assuré confirme : le fichier garde le second.
- *Ce que ça déplace* (`resumer_temoins.py`) : scénario 1, rien ; scénario 2,
  les dix-huit témoins des cultes, + 12 % en médiane, + 65 % pour le ministre
  né en 1925 ; scénarios 4 et 6, − 13 et − 16 % en médiane, jusqu'à − 24 % pour
  le religieux né en 1935.

Reste : l'arrêté du 22 décembre 1981 (1982) et la solidarité de 1979, sur le
fac-similé du Journal officiel. L'action n'a plus d'autre étape : elle passe
aux archives à la première session qui déplace des fichiers. La question des
taux spécifiques de l'Arrco des cultes reste au propriétaire (note du
13 octobre).
