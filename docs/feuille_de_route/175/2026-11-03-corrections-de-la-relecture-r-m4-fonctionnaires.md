# Corrections de la relecture R-M4 : le congé de maternité, et quatre écarts faibles, chez les fonctionnaires parents de trois enfants

File M4-bis de la sixième vague, le 3 novembre 2026 : corriger ce que la relecture R-M4
(note `2026-11-03-relecture-taux-plein-parents-fonctionnaires.md`, commit e14c779) relève
dans le taux plein à 65 ans des fonctionnaires parents de trois enfants nés de juillet
1951 à 1955 (commit 8ea1ce7, note `2026-11-03-taux-plein-parents-de-trois-enfants-fonctionnaires.md`).
Chaque texte a été rouvert dans la session, dans l'index de la DILA mis à jour (LEGI et
JORF à jour au 3 novembre 2026), à la rédaction en vigueur aux dates qui comptent ; aucune
citation n'est reprise de R-M4 ni de M4 sans avoir été relue. Un script a cherché chacun
des 58 fragments cités entre « » des textes de la version de 2011 dans le texte de
l'index : aucun n'y manque ; un fragment altéré à dessein y est bien dit absent.

**Ce qui est fait.**

- *L'écart moyen* : une année que la saisie dit « congé de maternité » n'ouvre plus la
  borne. La règle lit ses motifs dans la fiche : `fonctionnaires.interruptions` passe de
  `[maternite, education_enfant]` à `[education_enfant]`, et le paquet refait ne change que
  par lui ; le portage (`remplitPourLEnfantFonctionnaire`, `moteur/js/droit/categories.js`)
  et son jumeau (`_remplit_pour_l_enfant_fonctionnaire`) le lisent sans autre changement.
- *Le test*, `tests/test_taux_plein_a_soixante_cinq_ans.py` : « un an de maternité, 1978 »
  attend 66,25 au lieu de 65 ; un cas de plus, « maternité en 1978, puis un an à élever un
  enfant », 65 ; de bout en bout, « État, un an de maternité, 65 ans », 70,3125 % ; la fiche
  doit déclarer L. 331-3, L. 381-1, la plus grande part de l'année et L. 18, III. Vus rouges
  pour la raison attendue — 65 au lieu de 66,25, 75 % au lieu de 70,3125 %, les quatre
  déclarations absentes —, puis verts, dans les deux moteurs (`droit_et_refait`,
  `servi_et_refait`).
- *La fiche* `taux_plein_a_soixante_cinq_ans` : douze textes de plus à la version de 2011,
  chacun par son identifiant et mot pour mot ; l'approximation des fonctionnaires et son
  effet, l'effet général, le commentaire du paramètre, `lit`, une lecture, un « à relire ».
  Le cliquet des textes ne bouge pas (9 350) : les rédactions citées hors de la liste de
  contrôle (code du travail, loi n° 84-16, L. 331-3 à L. 331-5) n'y comptent pas, et les
  autres avaient déjà un statut.
- *La limite*, `docs/limites/ecarts-au-droit-positif.md` : la phrase des fonctionnaires.

**Les textes lus, et ce qu'ils décident.**

- R. 26 ter, I, 1° (LEGIARTI000024111781, seule rédaction) : « interrompu leur activité
  pendant une durée d'au moins une année » dans la fenêtre ; « Cette interruption
  d'activité doit être intervenue dans le cadre des congés ou de la disponibilité
  mentionnés au 1° de l'article R. 13 du présent code ». Le pluriel admet que des congés
  différents s'additionnent. Le texte ne dit pas l'année continue ; son II, pour l'aidant
  familial, dit « au moins trente mois consécutifs ». R. 13, 1°, ouvre par « L'interruption
  d'activité doit être d'une durée continue au moins égale à deux mois » : que R. 26 ter,
  qui renvoie aux congés « mentionnés » au 1°, reprenne cette durée, le texte ne le dit pas.
- R. 13, 1° (LEGIARTI000023449727, du 1er janvier 2011 au 1er octobre 2025) : a) « Du
  congé pour maternité » de l'article 34, 5°, de la loi n° 84-16, de la fonction publique
  territoriale et hospitalière, et « aux articles L. 331-3 et L. 615-19 du code de la
  sécurité sociale » ; c) le congé parental, celui de L. 122-28-1 du code du travail
  compris ; e) « D'une disponibilité pour élever un enfant de moins de huit ans ».
- La durée du congé de maternité. Loi n° 84-16, article 34 (LEGIARTI000006450574, du 12
  janvier 1984 au 27 juillet 1991, et chacune de ses rédactions jusqu'au 27 novembre 2020,
  la phrase numérotée « 5° a) » dès le 22 avril 2016) : « 5° Au congé pour maternité, ou
  pour adoption, avec traitement, d'une durée égale à celle prévue par la législation sur
  la sécurité sociale ». Le code de la sécurité sociale : L. 331-3 (LEGIARTI000006742541,
  1985-1994) : « six semaines avant la date présumée de l'accouchement et se termine dix
  semaines après celui-ci », « prolongée de deux semaines en cas de naissances
  multiples » ; L. 331-4 (LEGIARTI000006742546, 1985-1994) : huit et dix-huit semaines dès
  le troisième enfant, « vingt semaines en cas de naissances multiples », vingt-deux après
  l'accouchement quand des naissances multiples portent les enfants à trois ; L. 331-3 de
  1994 à 2006 (LEGIARTI000006742542 à LEGIARTI000006742544) et depuis
  (LEGIARTI000006742545) : douze semaines avant pour des jumeaux, « vingt-quatre semaines en
  cas de naissance de plus de deux enfants », vingt-deux après, « seize ou de trente-quatre
  semaines, quarante-six semaines en cas de naissance de plus de deux enfants » ; L. 331-4
  (LEGIARTI000006742547 à LEGIARTI000006742550) : vingt-six semaines dès le troisième
  enfant ; L. 331-5 (LEGIARTI000006742551 à LEGIARTI000006742553) : « une période
  supplémentaire n'excédant pas deux semaines ». Depuis le 20 décembre 2005, l'enfant né
  plus de six semaines avant terme et hospitalisé allonge l'indemnisation « du nombre de
  jours courant entre la naissance de l'enfant et six semaines avant la date présumée de
  l'accouchement » (LEGIARTI000006742544), puis, depuis le 24 mars 2006, « de la date
  effective de l'accouchement au début de la période de repos » (LEGIARTI000006742545) :
  un allongement que le texte ne borne pas. Au code du travail, en 1978 (L. 122-26,
  LEGIARTI000006646773 jusqu'au 1er octobre 1978, LEGIARTI000006646774 ensuite) : six
  semaines avant, huit puis dix après, quatorze puis seize en tout, « sans pouvoir excéder
  huit semaines avant la date présumée de l'accouchement et quatorze semaines après »
  pour un état pathologique, deux de plus pour des naissances multiples ; dans sa
  dernière rédaction (LEGIARTI000006646786, du 6 mars 2007 au 1er mai 2008), les mêmes
  seize, vingt-six, trente-quatre et quarante-six semaines que la sécurité sociale, un
  état pathologique « dans la limite de deux semaines avant la date présumée de
  l'accouchement et de quatre semaines après » (L. 1225-17 à L. 1225-20 depuis, pour les
  durées), et, pour l'adoption, « dix semaines au plus », dix-huit si elle porte les
  enfants à trois, « vingt-deux semaines en cas d'adoptions multiples ». Le statut des fonctionnaires d'avant 1984
  (ordonnance n° 59-244) n'est pas dans l'index du dépôt : la durée de leur congé n'est pas
  lue.
- L'AVPF, code de la sécurité sociale, L. 381-1 (LEGIARTI000006742941, du 21 décembre 1985
  au 1er janvier 1987) : « La personne isolée et, pour un couple, l'un ou l'autre de ses
  membres n'exerçant pas d'activité professionnelle, bénéficiaire du complément familial,
  de l'allocation au jeune enfant ou de l'allocation parentale d'éducation » « est affilié
  obligatoirement à l'assurance vieillesse du régime général de sécurité sociale sous
  réserve que ses ressources ou celles du ménage soient inférieures à un plafond fixé par
  décret » ; puis, de même, la personne à charge d'un enfant ou d'un adulte handicapé. Les
  rédactions de 2002 (LEGIARTI000006742945) et de 2010 (LEGIARTI000023034972), lues, y
  ajoutent le temps partiel avec l'allocation à taux partiel et l'allocation de présence
  parentale, puis la prestation d'accueil du jeune enfant ; aucune ne fait d'un congé ou
  d'une disponibilité pour l'enfant une condition, et celle de 2010 ouvre aussi l'AVPF à
  « la personne bénéficiaire du congé de soutien familial », qui n'est pas de R. 13.
- L. 18 (LEGIARTI000025076852, du 1er janvier 2012 au 16 avril 2023, en vigueur aux dates
  d'effet), III : « A l'exception des enfants décédés par faits de guerre, les enfants
  devront avoir été élevés pendant au moins neuf ans, soit avant leur seizième
  anniversaire, soit avant l'âge où ils ont cessé d'être à charge » — pour la majoration
  de pension de son I. L'article 28, III (LEGIARTI000025014566) : « Pour l'application aux
  fonctionnaires du 1° du IV de l'article 20, les enfants sont ceux énumérés au II de
  l'article L. 18 » ; l'article 20, IV, 1° (LEGIARTI000023023835) : « Avoir eu ou élevé,
  dans les conditions prévues au deuxième alinéa de l'article L. 351-12 du code de la
  sécurité sociale, au moins trois enfants » ; L. 351-12 (LEGIARTI000006742643, 1998-2023),
  deuxième alinéa : « Ouvrent également droit à cette majoration les enfants élevés dans
  les conditions prévues au deuxième alinéa de l'article L. 342-4 ».
- L. 14, I, en vigueur aux dates d'effet (LEGIARTI000028498863, du 22 janvier 2014 au 15
  juillet 2018 ; LEGIARTI000037200740, jusqu'au 1er septembre 2023) : « 1° Soit au nombre
  de trimestres correspondant à la durée qui sépare l'âge auquel la pension est liquidée de
  la limite d'âge du grade détenu par le pensionné » ; « Le nombre de trimestres
  correspondant est arrondi à l'entier supérieur dans des conditions définies par décret.
  Le plus petit des deux nombres de trimestres résultant des dispositions du 1° et du 2° du
  présent I est pris en considération ». Relus pour les âges : la loi n° 2003-775, article
  66, III (LEGIARTI000006758610 : « 2015 II : 1,25 % III : Limite d'âge moins 5
  trimestres », « 2016 [...] moins 4 », « 2017 [...] moins 3 ») ; le décret n° 2011-2103,
  article 1er (JORFARTI000025061553 : « 1954 61 ans et 7 mois ») et article 8
  (JORFARTI000025061595 : « De cinq mois par génération pour les fonctionnaires atteignant
  cet âge entre le 1er janvier 2012 et le 31 décembre 2014 ») ; l'article 28, I : « nés à
  compter du 1er janvier 1955, la limite d'âge est fixée à soixante-sept ans ».

**L'écart moyen : ce que le texte exige, et ce que la saisie en dit.** Le texte veut au
moins une année d'interruption, faite de congés ou d'une disponibilité de R. 13, 1° —
maternité, adoption, congé parental, présence parentale, disponibilité pour élever un
enfant de moins de huit ans —, qui peuvent s'additionner. Le congé de maternité en est,
mais il ne fait pas l'année seul : seize à quarante-six semaines aux textes lus, deux de
plus pour un état pathologique ; seul l'allongement d'une naissance très prématurée, depuis
décembre 2005, n'a pas de borne écrite. La saisie dit une année par motif : par le champ
« Interruptions », année par année (`interruptionsAnalysees`, `moteur/js/saisie.js`), ou
par une période sans emploi bornée au mois, dont l'année prend le motif quand elle en
occupe plus de la moitié des mois (`anneesCreuses`) ; un relevé range sous le même motif
l'année sans revenu qu'il dit de « maternité » ou d'« adoption » (`MOTIFS`,
`moteur/js/releve-lu.js`). Une année « congé de maternité » ne dit ni la durée du congé, ni
le nombre des enfants nés, ni ce qui l'a suivi : elle ne prouve pas l'année. Le modèle ne
la compte donc plus. Il ne la compte pas non plus avec une année « élever un enfant » : la
saisie ne dit que des années entières, et une seule année « élever un enfant » dans la
fenêtre suffit déjà. Le congé de maternité suivi d'un congé parental ou d'une disponibilité
se dit « élever un enfant » : la fiche et la limite le déclarent.

**Les calculs posés à la main**, pour les valeurs nouvelles. La fonctionnaire de l'État née
le 15 mars 1955, en service de 1973 à 1977 et de 2003 à 2019, enfants d'avril 1978, juin
1980 et juin 1982, partie à 65 ans, effet le 1er avril 2020.

- *Un an de maternité, 1978* : l'enfant d'avril 1978 (premier semestre), fenêtre 1978-1980,
  aucune année « élever un enfant » ; celui de juin 1980, fenêtre 1980-1982, aucune, et
  1978 + 1979 = 4 + 0 = 4 < 8 ; celui de juin 1982, fenêtre 1982-1984, aucune. Pas de
  borne : soixante-deux ans le 15 mars 2017, « Limite d'âge moins 3 trimestres » de
  soixante-sept ans : 67 − 0,75 = **66,25**.
- *Maternité en 1978, puis un an à élever un enfant, 1979* : 1979 dans la fenêtre 1978-1980,
  une année ≥ 1 ; 1976 + 1977 = 4 + 4 = 8 ≥ 8 ; l'activité avant 1979, l'emploi de 1973 à
  1977, 20 ≥ 8 : **65**.
- *De bout en bout, « État, un an de maternité, 65 ans »* : la requête de `NEE_EN_1955`, 1978
  dit « congé de maternité », 1979 à 2002 « sans activité ». Pas de borne : 66 ans et 3
  mois, le 15 juin 2021 ; partie le 1er avril 2020, à 65 ans et 17 jours, 14,5 mois, 4,83
  trimestres, « arrondi à l'entier supérieur » : 5 ; la durée en manque bien davantage —
  104 trimestres liquidables sur 166 au détail de la pension, et aucune période validée
  de 1979 à 2002, soit au plus 108 de durée d'assurance —, le plus petit est 5 : 75 % ×
  (1 − 5 × 1,25 %) = **70,3125 %**, comme « sans activité ».
- *L'effet de 1954 (écart b)* : née de janvier à mai 1954, 61 ans et 7 mois d'août à
  décembre 2015, « moins 5 trimestres » de 66 ans et 7 mois (soixante ans en 2014, cinq
  mois par génération : 65 ans + 4, + 5, + 5, + 5 mois de 1951 à 1954) : 65 ans et 4 mois ;
  partie à soixante-cinq ans, 4 mois, 1,33 trimestre, arrondi à **2** : 75 % × (1 − 2 ×
  1,25 %) = **73,125 %** au lieu de 75 %. Née de juin à décembre 1954, 61 ans et 7 mois de
  janvier à juillet 2016, « moins 4 trimestres » : 65 ans et 7 mois, 7 mois, 2,33, arrondi
  à **3**, 72,1875 %. Née en 1955 : 15 mois, **5**, 70,3125 %. « Au plus » : L. 14, I,
  prend le plus petit des deux nombres, et la durée peut en manquer moins.

**Les écarts faibles.**

- b. L'effet général de la fiche disait « 3 trimestres de décote de moins en 1954 » : il dit
  désormais 2 au plus pour les nés de janvier à mai 1954, 3 de juin à décembre, 5 en 1955,
  et cite « arrondi à l'entier supérieur » ; l'effet de l'approximation ajoute le cas de
  janvier à mai. Le calcul du modèle était juste (65,33, R-M4, point 3).
- c. L'AVPF ne prouve pas l'interruption exigée : L. 381-1 ne demande ni congé ni
  disponibilité pour l'enfant ; elle sert le parent « n'exerçant pas d'activité
  professionnelle », qu'il soit en congé ou ait quitté son emploi, et aussi, selon les
  rédactions, celui qui travaille à temps partiel avec l'allocation à taux partiel, et
  celui qui a la charge d'un handicapé. Le
  choix : le modèle garde l'année d'AVPF d'un relevé pour une année « élever un enfant »,
  comme l'année que le lecteur dit ainsi, et la présume prise dans un congé ou une
  disponibilité ; la fiche, son effet et la limite le déclarent. L'écarter priverait de la
  borne le parent en congé parental qu'un relevé ne dit qu'« AVPF », sans que la saisie
  dise mieux l'autre cas.
- d. Les neuf ans : non tranché, déclaré, en nommant L. 18, III ; le modèle ne lit pas cette
  durée, que la saisie ne porte pas.
- e. L. 14, I, cité aux deux rédactions en vigueur aux dates d'effet, avec « arrondi à
  l'entier supérieur » et « Le plus petit des deux nombres ».

**La même erreur ailleurs** (la classe, pas le cas). Seul R. 26 ter demande une année
d'interruption. La bonification de L. 12, b, et le départ anticipé des parents de trois
enfants demandent deux mois (R. 13, 1°), qu'un congé de maternité remplit ; les fiches
des carrières longues comptent les trimestres de maternité, que le congé valide. Une erreur
voisine reste : une année « élever un enfant » compte entière quand une période saisie au
mois peut n'en couvrir que sept. La règle ne peut la lire au mois : la carrière ne porte
que l'année. Déclarée dans la fiche et la limite, et inscrite à son « à relire ».

**Ce que les textes ne tranchent pas**, et que la fiche dit comme tel : l'année d'interruption
continue ou non ; la durée continue de deux mois de R. 13, 1°, reprise ou non par R. 26 ter ;
les neuf ans de L. 18, III ; la durée de l'allongement d'une naissance très prématurée.

**Les vérifications.** Les 58 fragments cités entre « » des textes de la version de 2011,
retrouvés mot pour mot dans l'index ; `python scripts/verifier_prose.py --corriger` : la
prose dit le vrai. Les tests : le fichier de la règle, 17 passés ; `-m rapide`, sa variante
`PRESOMPTIONS_DECALEES=1`, `test_regle_de_chacun.py` et les fichiers qui lisent les fichiers
touchés, ci-dessous.

**Ce qui reste**, qui n'est pas de cette session : lire l'année d'interruption au mois, si
la carrière vient à porter la durée des périodes sans emploi (au site) ; le statut des
fonctionnaires d'avant 1984, que l'index ne porte pas ; la réduction d'activité de R. 26
ter, I, 2°, déjà inscrite.
