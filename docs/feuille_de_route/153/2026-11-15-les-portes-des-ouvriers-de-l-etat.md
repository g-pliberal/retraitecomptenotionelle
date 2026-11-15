# Les portes de la carrière longue des ouvriers de l'État, et l'audit de la table

**Le 15 novembre 2026, à la demande du propriétaire, qui voulait la table des
portes de la carrière longue irréprochable au droit.** La note de l'étape 2
(16 octobre 2026) l'avait vu en passant : le FSPOEIE gardait les portes du
régime général dès 2004, son texte n'ayant pas été lu. Il l'est : la loi
n° 2004-1484 de finances pour 2005, article 119, crée L. 25 bis et le rend,
en son II, « applicable[s] aux ouvriers » des établissements industriels de
l'État au 1er janvier 2005 ; l'article 22 ter du décret n° 2004-1056 fait de
même de L. 25 bis et de D. 16-1 à compter du 1er juillet 2011. L'ouvrier de
l'État a donc les portes des fonctionnaires : chacune à sa date (59 ans en
2005, 58 au 1er juillet 2006, 56 en 2008) et sur la durée fixe d'avant 2009.
Le modèle le laissait partir à 58 ans en 2004 et en 2005, à 56 ans en 2006.

**Le correctif** : le FSPOEIE rejoint les régimes des fonctionnaires de
`CarriereLongue` (`REGIMES_FONCTION_PUBLIQUE`), dans le portage et dans son
jumeau Python ; ses tests, vus rouges, sont dans
`tests/test_oracle_carriere_longue_fonction_publique.py` (le portage, par la
façade) et `tests/test_cnracl.py` (le jumeau). Aucun témoin ne bouge : aucun
ne liquide un ouvrier de l'État avant 2009.

**L'audit du reste de la table** (`legislation/carriere_longue.csv`), relu
dans l'index LEGI : les six rédactions de D. 351-1-1, de 2003 à septembre
2026, génération par génération, et les quatre-vingts portes concordent,
âges, suppléments de durée cotisée, durée d'assurance d'avant novembre 2012
et dates d'effet ; la suspension de la loi de financement pour 2026 ne vaut
que pour les pensions prenant effet à compter du 1er septembre 2026, comme la
table. Les portes de l'État et de la CNRACL, et leur durée fixe, sont celles
de L. 25 bis. Restent ouvertes les questions que la fiche `carriere_longue`
porte déjà : la voie des quatre trimestres agricoles du non-salarié agricole,
lue et non portée, et l'option du né au dernier trimestre chez les artisans
et commerçants de 2011 à 2012.
