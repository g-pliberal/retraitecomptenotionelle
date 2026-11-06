# Étape 6, règlements européens : les 496 références sans thème, rapprochées des textes de l'Office des publications de l'Union

**Le 5 novembre 2026, ce qui est fait.**

- *La lecture* : les 496 références sans thème dont le titre dit un règlement, toutes
  `a_lire`, relues par l'API le 5 novembre 2026 vers 21 h 20 UTC, toutes servies, de
  nature « règlement » : 463 pages et 33 PDF, que le site sert sous `/Pdf/` à leur nom.
  122 du règlement (CEE) n° 1408/71, 149 du n° 574/72, 99 du (CE) n° 987/2009, 92 du
  n° 883/2004, la décision A1 de la commission administrative, et 33 pages ou PDF de 26
  autres règlements. La page sert le texte même de l'article, ou un PDF ; une seule lie
  Légifrance, celle du n° 1086/2006, dont le mot « taux » mène au texte
  `JORFTEXT000022284967`, non ouvert ici. Le dépôt ouvre ces textes au dépôt de l'Office des publications de l'Union
  (`publications.europa.eu/resource/celex/<CELEX>`, en XHTML ou en PDF, langue
  française), comme les fiches de la coordination, et en liste les versions consolidées
  par son point SPARQL.
- *Le rapprochement des textes* : chaque règlement par son numéro, jamais par sa date —
  le numéro CELEX que le numéro donne, puis le titre français et la date que l'Office
  porte sous ce CELEX, qui disent le même numéro et le même jour pour les 30 règlements
  et la décision A1 (CELEX `32010D0424(01)`, du 12 juin 2009). Un écart : l'API date le
  règlement n° 1135/2007 du 10 février 2007 (`date_texte` 2007-02-10), quand son titre
  et l'Office le datent du 10 juillet 2007.
- *Le rapprochement des articles* : 448 pages des quatre grands règlements. 25 pages
  d'annexes ne servent que le numéro, l'intitulé et un lien — vers les dix PDF du CLEISS
  que la base sert pour les annexes 1 à 4 et 6 à 11 du n° 574/72, vers `cleiss.fr` pour
  neuf annexes du n° 883/2004 et cinq du n° 987/2009, vers quatre PDF par État —
  Belgique, France, Italie, Luxembourg — pour l'annexe V du n° 1408/71 — ; leur numéro et leur intitulé sont ceux de l'annexe du
  même numéro. Les 423 autres ont été comparées mot à mot, accents, ponctuation et casse
  à part, à l'article du même numéro de l'acte d'origine et de chaque version consolidée
  de l'Office : 9 du n° 1408/71 depuis 2000, 18 du n° 574/72 depuis 1997, 8 du
  n° 883/2004 depuis 2010, 7 du n° 987/2009 depuis 2011 (celles d'avant 2005 des deux
  premiers en PDF). Le texte d'une version s'y retrouve à 97 % au moins pour 387, de 90
  à 97 % pour 29 (intitulés de section, bruit des PDF), moins pour 7 : l'annexe VIII du
  n° 1408/71 (23 %, ci-dessous), les articles 32 bis, 33, 40, 74 et 96 du n° 574/72,
  dont seul l'intitulé diffère, et l'article 41 du n° 987/2009 (75 %, ci-dessous).
- *Les textes entiers* : 15 pages servent un règlement entier, dont 14 se retrouvent à
  97 % au moins dans l'acte d'origine — celle du n° 723/2004 en est un extrait, 9 005
  mots sur 55 759, celle du n° 311/2007 ses articles, son annexe étant en PDF — ; celle
  du n° 2866/98, ci-dessous, n'en suit aucune version. Des 33 PDF, 12 reproduisent
  l'acte : 96 % au moins de leurs mots sont dans l'acte, et 94 % au moins des mots de
  l'acte dans le PDF, l'ordre de l'extraction à part ; celui du n° 870/2013 est une
  image, que l'extraction ne lit pas : son numéro et sa date se lisent sur sa première
  page. Les six annexes du n° 805/2004 sont les formulaires du Journal officiel L 143 du
  30 avril 2004, leur intitulé lu ; les onze annexes du n° 574/72, des documents du
  CLEISS de janvier 2007, dont 66 à 90 % des mots sont dans l'annexe d'une version de
  2006 à 2008 — l'annexe 11, supprimée en 2005, est vide — ; les trois PDF de l'annexe V
  du n° 1408/71, 96 % de leurs mots dans l'annexe V.
- *La version visée* : la base ne date pas sa version, hors des mentions « Applicable à
  compter du 01/05/2010 » et « Modifié par règlement (CE) n° 988/2009 ». Son texte est
  celui de la dernière version consolidée de l'Office pour 377 des 423 pages : du
  7 juillet 2008 pour le n° 1408/71 (110), du 2 mars 2009 pour le n° 574/72 (96), du
  31 juillet 2019 pour le n° 883/2004 (80), du 1er janvier 2018 pour le n° 987/2009
  (91). Dix gardent une rédaction antérieure : les articles 15 et 17 du n° 1408/71, de
  1971, ses articles 22 ter et 34 ter, de 2000 à 2004 ; les articles 1er, 20, 32, 76 et
  94 du n° 574/72, de 1972 à 2004 ; les considérants du n° 987/2009, de 2009. Les 36
  autres ne se départagent pas à 97 %.
- *Les sorts* : 490 références rangées, 77 `limite`, 413 `hors_modele` ; le registre
  seul a changé (`data/reference/legislation/cnav/references.csv`, 490 lignes). Les
  articles de ces 496 que les fiches citent prennent leur renvoi : du n° 883/2004, les
  articles 6, 51, 54, 59 et 60 et les annexes VIII et XI, que la fiche de la
  totalisation lit (« articles 6 (totalisation), 50 à 60 et annexes VIII, X et XI »),
  l'article 60 et l'annexe VIII aussi à `pension_proratisee`, l'article 54 aussi à
  `minimum_contributif_international`, les articles 23 à 25 à
  `cotisation_maladie_des_non_residents`, l'article 70 à
  `residence_et_minimum_vieillesse` ; l'article 13 du n° 987/2009 et l'article 45 du
  n° 1408/71 à la totalisation. Leur objet donne aux autres le même renvoi : la
  cotisation du titulaire de pension (n° 883/2004 et n° 987/2009, article 30 ;
  n° 1408/71, article 33), la levée des clauses de résidence (n° 883/2004, article 7),
  dont l'article 70 excepte les prestations spéciales à caractère non contributif. Vont
  à la fiche de la totalisation, qui lit les règlements dans leurs versions consolidées
  (58 en tout) : les définitions, le champ, les
  conventions entre États, les dispositions transitoires et finales, les annexes des
  conventions maintenues, les règlements qui modifient le n° 1408/71 ou le n° 883/2004 ;
  le nouveau calcul et la revalorisation, que la fiche dit ne réviser que par
  l'écrêtement du minimum contributif ; à `pension_proratisee`, ce qui touche le prorata
  et les fonctionnaires (5) ; à `minimum_contributif_international`, le non-cumul (6) ;
  l'assurance volontaire, à la limite « rachats et versements » de
  `docs/limites/3-systeme-actuel.md` (3).
- *Hors du modèle, 413*, sous 18 raisons, par chapitre du règlement : la maladie et la
  maternité (78), les institutions de la coordination et leur coopération (57), les
  accidents du travail (46), la législation applicable (37), la procédure, la
  répétition de l'indu et le titre exécutoire européen du n° 805/2004 (30), les
  prestations familiales (27), le remboursement entre institutions (26), l'invalidité
  (25), l'instruction coordonnée de la demande (24), le chômage et la préretraite (23),
  la conversion des monnaies, dont huit règlements de l'introduction de l'euro et de ses
  taux de conversion (10),
  les allocations de décès (10), le paiement à qui réside dans un autre État (10), le
  recouvrement des cotisations (4), l'égalité de traitement (2), l'administration (2),
  le statut des fonctionnaires des Communautés (n° 723/2004), la libre circulation des
  travailleurs (n° 492/2011).

**Six à lire, et quatre candidats pour la session du modèle**, sans y toucher :

- `REG_CEE_8832004_29042004_art57.aspx`, article 57 du n° 883/2004 (version du
  31 juillet 2019) : « l'institution d'un Etat membre n'est pas tenue de servir des
  prestations au titre de périodes accomplies sous la législation qu'elle applique […]
  si: - la durée totale desdites périodes n'atteint pas une année; et - compte tenu de
  ces seules périodes, aucun droit aux prestations n'est acquis en vertu de cette
  législation ». Le modèle sert la pension de chaque régime quelle que soit la durée de
  ses périodes (`liquider_chaque_regime`,
  `src/retraite_notionnelle/droit/liquider.py:683`) ; la fiche de la totalisation compte
  l'article parmi ses lectures (« 50 à 60 »), sans en dire ni en déclarer la règle. Ce
  que le texte ne tranche pas ici : si le droit français seul ouvre une pension sur
  moins d'une année, la seconde condition manque, et l'article ne joue pas.
- `REG_CEE_8832004_29042004_art58.aspx` et `REG_CEE_140871_14061971_art50.aspx`,
  l'attribution d'un complément : le bénéficiaire ne peut, dans l'État de résidence,
  « percevoir un montant de prestations inférieur à celui de la prestation minimale
  fixée par ladite législation pour une période d'assurance ou de résidence égale à
  l'ensemble des périodes prises en compte » (n° 883/2004, article 58). Le modèle porte
  la pension proratisée au minimum contributif proratisé (fiche
  `minimum_contributif_international`), qui ne cite ni l'un ni l'autre article — la
  fiche de la totalisation compte le premier parmi ses lectures, sans en dire la règle ;
  que ce minimum soit une « prestation minimale » au sens de l'article, le texte ne le
  dit pas.
- `REG_CEE_9872009_16092009_art44.aspx`, article 44 du n° 987/2009 : quand l'État
  compétent ne compte pas les périodes d'éducation d'un enfant, l'institution de l'État
  dont la législation s'appliquait à l'activité de l'intéressé quand elles ont commencé
  « reste tenue de prendre en compte ladite période en tant que période d’éducation
  d’enfants selon sa propre législation, comme si l’enfant était éduqué sur son propre
  territoire ». Aucune fiche ne le cite ; ce que fait le modèle d'un enfant élevé
  hors de France est à lire dans `majoration_duree_assurance_enfants`.
- `REG_CEE_140871_14061971_art9bis.aspx` (prolongation de la période de référence) et
  `REG_CEE_8832004_29042004_art5.aspx` (assimilation de prestations, de revenus, de
  faits ou d'événements) : des règles générales, dont ce qu'elles changent à la retraite
  que le modèle calcule n'a pas été lu.

**Ce que la base sert de travers.**

- L'article 41 du n° 987/2009 n'a pas son paragraphe 2, que l'acte d'origine et la
  version du 1er janvier 2018 portent : « L’article 32, paragraphe 2, deuxième alinéa,
  et l’article 32, paragraphe 3, du règlement d’application s’appliquent mutatis
  mutandis. »
- L'annexe VIII du n° 1408/71 nomme l'Islande, le Liechtenstein et la Norvège, que
  l'annexe VIII de la version du 7 juillet 2008 ne nomme pas : 23 % de ses mots s'y
  retrouvent.
- Le n° 2866/98 joint ses considérants de 1998 à un tableau des taux qui va jusqu'à la
  couronne estonienne, sans le lats letton : il ne suit mot pour mot ni l'acte
  d'origine (76 % de ses mots), ni les versions de 2009, 2011 et 2014 (77 %).
- La date du n° 1135/2007, ci-dessus.

**Ce que la lecture n'a pas fait.** Le contenu des 77 articles renvoyés aux fiches n'a pas
été confronté ici à leurs règles, au-delà de ce que ces fiches en disent ; aucune règle,
aucune fiche, aucun bloc « Reprise » d'une autre étape n'a changé. Les textes de l'Office
ont été lus le 5 novembre 2026 ; les PDF du CLEISS que lient les annexes des n° 883/2004
et 987/2009 n'ont pas été ouverts.
