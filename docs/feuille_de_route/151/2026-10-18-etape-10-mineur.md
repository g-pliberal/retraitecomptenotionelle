# Étape 10 : la limite d'âge du mineur, et le jour où une limite naît

**Le 18 octobre 2026 : depuis le 18 janvier 1954, le mineur affilié au régime spécial a pour
limite d'âge l'âge d'ouverture de sa pension, cinquante-cinq ans, et peut, dans l'intérêt du
service, rester en activité au-delà, sans borne ; le modèle le présume maintenu jusqu'à son
départ, et ne le radie jamais. Les exceptions à toute limite se lisent désormais au jour où
l'agent l'atteint, celui où une version la crée quand il l'avait déjà passée. Python et
JavaScript (25c80df).**

## Ce qui a été lu

- **Le décret n° 54-51 du 16 janvier 1954**, dans l'index LEGI, en vigueur et jamais récrit
  (`LEGITEXT000020255038`). Article 1er : il vise les affiliés à la caisse autonome nationale
  et les employés, techniciens, agents de maîtrise et ingénieurs des deux caisses de
  retraites des mines. Article 2 : « L'âge limite de maintien en activité [...] est l'âge fixé
  pour l'ouverture du droit à rente ou pension de retraite par les dispositions du premier
  alinéa de l'article 146 du décret n° 46-2769 », reculé, pour l'employé, le technicien et
  l'agent de maîtrise d'une caisse complémentaire, à l'âge de sa pension d'ancienneté
  normale, et fixé à soixante ans pour l'ingénieur. Article 3 : « Tout agent peut, dans
  l'intérêt du service, être admis à rester en activité au delà de l'âge limite défini
  ci-dessus. Ce maintien au service prend fin à l'initiative de l'une ou de l'autre partie,
  sous réserve des règles applicables en matière de préavis. »
- **L'article 146 du décret n° 46-2769**, en 1971 et en 1985 : « L'assurance vieillesse
  garantit une rente ou pension de retraite aux affiliés âgés de cinquante-cinq ans », puis
  l'ouverture à cinquante ans du mineur de trente ans de services, dont vingt au fond, « qui
  se mettent en instance de pension » (1971), ou l'abaissement d'un an par quatre années au
  fond (1985). Depuis le 1er janvier 1993, l'article ne fixe plus d'âge :
  le décret n° 92-1354 y met l'allocation d'attente de la pneumoconiose, la pension étant
  garantie « aux affiliés âgés de cinquante-cinq ans au moins » à l'article 125, et
  l'abaissement passant à l'article 127. La rédaction de 1946 à 1971 n'est pas dans l'index,
  qui ne garde pas non plus les alinéas. Les articles 144 et 145 servent, depuis 1993, une
  indemnité au mineur de trente ans de services qui travaille encore après cinquante-cinq ans.
- **Le décret n° 53-711, article 5**, dont le décret n° 54-51 est le règlement d'adaptation
  aux mines : il n'interdisait que la mise à la retraite d'office avant la limite des
  fonctionnaires civils.
- **La SNCF, la RATP et la Banque avant 2010 et 2012** : les décrets n° 54-24, n° 54-23 et
  n° 54-776, dont l'index JORF ne porte que le titre et, pour les deux premiers, un sommaire ;
  Légifrance et Gallica refusent le réseau de la session (défi de Cloudflare, 403). Pour la
  SNCF, l'arrêt de la Cour de cassation du 16 février 2011 (chambre sociale, n° 10-10.465),
  lu sur dictionnaire-juridique.com, cite la cour d'appel de Paris : « le réglement des
  retraites de la SNCF fixe à 60 ans l'âge limite de maintien en service », et l'article 2 du
  décret n° 54-24 permet « à la SNCF de prononcer d'office l'admission à la retraite des
  agents remplissant la double condition d'âge et d'ancienneté de services prévue par
  l'article 7 du réglement des retraites, soit à 55 ans pour les agents sédentaires ayant
  comptabilisé 25 années de services et pouvant bénéficier d'une pension de retraite
  normale » ; le Conseil d'État a jugé cette faculté non discriminatoire en soi, le 19 mai
  2006.

## Ce que fait le modèle

- **La fiche `limite_age_mines`**, trois versions : rien avant le 18 janvier 1954
  (`avant_1954`) ; cinquante-cinq ans, par l'article 146 (`decret_de_1954`) ; depuis le
  1er janvier 1993, cinquante-cinq ans encore, la limite suivant l'âge d'ouverture passé à
  l'article 125 (`article_125_de_1993`, supposée). Chacune ouvre l'exception neuve
  `interet_du_service`.
- **`droit/limite_age.py` et son jumeau** : le mineur entre dans `FICHE_DU_REGIME` ; le
  maintien dans l'intérêt du service (`MAINTIEN_DANS_L_INTERET_DU_SERVICE`), présumé, court
  jusqu'au départ saisi, si bien que la radiation du mineur n'est jamais forcée : ni les
  départs, ni l'échéancier, ni la page n'en changent.
- **Le jour où une limite naît, pour toute la classe.** `_limite` rend aussi le jour où
  l'agent atteint sa limite : son anniversaire, ou le premier jour de la version qui la crée
  quand il l'avait déjà passée. Les exceptions, la version de la limite et les enfants à
  charge se lisaient à l'anniversaire mensuel qui précède, sous la version d'avant. Ils se
  lisent ce jour-là : l'agent de la Banque qui avait passé sa limite le 26 juillet 2012 garde
  la prorogation pour enfants du statut de 2012, celui de l'Opéra qui avait passé la sienne le
  1er juillet 2008 la prolongation pour carrière incomplète (né en janvier 1942 et entré à
  quarante ans, il part en janvier 2011, et non en août 2008), et le mineur qui avait passé
  cinquante-cinq ans le 18 janvier 1954, son maintien.
- **Mesuré** : trois tests neufs dans `test_limite_age.py` — le mineur né en 1930 et en
  1950 ; le mineur né en 1898, sans limite parti en 1953, maintenu parti en 1956 ; l'agent de
  la Banque né en 1950 et ses deux enfants — et un repris, le mineur recruté depuis 2010
  restant sans limite ; un essai dans `tests/js/moteur.test.js`, qui les rejoue en
  JavaScript, une radiation non forcée ne paraissant dans aucun témoin. Aucun des
  882 témoins de simulation ni des 76 rendus ne bouge, ni les agrégats. Le cliquet des
  textes descend à 9691.

## Les choix, que le propriétaire peut reprendre

1. **Le maintien dans l'intérêt du service est présumé accordé jusqu'au départ saisi**, par
   la présomption `exceptions_a_la_limite_d_age` : aucun mineur n'est radié par sa limite.
   L'autre lecture — la mise à la retraite à la limite comme règle, le maintien comme
   exception que les Houillères n'accordaient qu'à certains — radierait à cinquante-cinq ans
   tout mineur dont le départ saisi la passe, et baisserait sa pension.
2. **Tout mineur est traité en agent de la seule caisse autonome nationale** : l'employé, le
   technicien et l'agent de maîtrise d'une caisse complémentaire, et l'ingénieur, limité à
   soixante ans, ne sont pas distingués, comme la saisie ne les distingue pas.
3. **La limite ne suit pas l'abaissement par les années au fond**, que la rédaction de 1985
   écrit peut-être au premier alinéa : la limite reste à cinquante-cinq ans.
4. **Depuis 1993, la limite suit l'âge d'ouverture passé à l'article 125**, le renvoi à
   l'article 146 n'ayant plus d'objet.

## Ce que la page peut dire (session du site)

Rien de neuf ne paraît : `limiteDAgePassee` ne parle que d'une radiation forcée.
`radiation(moteur, carriere)` rend pour le mineur une radiation non forcée, sous la fiche
`limite_age_mines`, dont le recul `maintien_dans_l_interet_du_service`, présumé, va de la
limite au départ, et que `EXCEPTIONS_A_LA_LIMITE` ne nomme pas : « vous êtes maintenu en
activité dans l'intérêt du service ». L'agent de la Banque ou de l'Opéra prolongé au jour où
sa limite naît se dit comme les autres.

## Ce qui reste

- **La SNCF et la RATP avant 2010** : deux règles pour la SNCF, une limite à soixante ans du
  règlement des retraites et une faculté de l'employeur dès cinquante-cinq ans (décret
  n° 54-24, article 2), qu'il faut lire dans le règlement des retraites, que l'index ne porte
  pas, et dans le décret de 1954, au Journal officiel du 10 janvier 1954 ; puis décider si la
  faculté est présumée exercée, ce que le départ saisi, souhait de l'agent, ne dit pas. Pour
  la RATP, rien n'est lu que le sommaire de l'index.
- **La Banque avant 2012** : le décret n° 54-776 et le décret n° 68-299, absents de l'index ;
  deux arrêts du Conseil d'État, de 2015 et de 2019, commentés à la Gazette du Palais, sur les
  limites et la mise à la retraite des agents de la Banque, non lus.
- Au site, nommer la fin de l'emploi des quatre fiches neuves et le maintien du mineur ; pour
  le propriétaire, la radiation dans les comptes notionnels, l'actif d'avant 2010, les choix
  des étapes 4, 6, 8, 9 et 10.
