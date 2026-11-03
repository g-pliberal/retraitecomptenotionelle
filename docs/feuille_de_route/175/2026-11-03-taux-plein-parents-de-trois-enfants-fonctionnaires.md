# Le taux plein à 65 ans des parents de trois enfants nés de juillet 1951 à 1955, chez les fonctionnaires

File M4 de la sixième vague, sur la décision 14 du propriétaire : servir aux fonctionnaires
le cas que le régime général sert depuis la note
`2026-11-03-taux-plein-parents-de-trois-enfants.md`, et que la note
`2026-11-03-correction-taux-plein-parents-de-trois-enfants.md` déclarait en écart. Chaque
texte a été ouvert dans la session : l'index de la DILA (LEGI à jour au 2 novembre 2026,
aucun incrément depuis ; JORF au 3 novembre), et les pages des deux caisses, téléchargées
le jour. Aucune référence n'est reprise d'une note sans avoir été rouverte.

**Ce qui est fait.**

- *La règle, dans les deux moteurs* : l'âge d'annulation de la décote que rend la décote en
  table de la fonction publique (`decoteOpposable`, `moteur/js/droit/liquider.js` ; son
  jumeau `decote_opposable`), la limite d'âge moins les trimestres du tableau de l'article
  66, III, est borné à soixante-cinq ans pour le sédentaire de l'État, de la CNRACL et de
  l'ouvrier de l'État (`ageDuParentSedentaire` : ni catégorie active dont il a les
  services, ni militaire) qui remplit les conditions (`ageDuFonctionnaireParentDeTroisEnfants`
  et `remplitPourLEnfantFonctionnaire`, `moteur/js/droit/categories.js` ; leurs jumeaux dans
  `droit/categories.py`). Les trimestres de décote (L. 14, I, 1°) et le minimum garanti
  (L. 17) lisent cet âge sans autre changement. Le décompte des générations et des enfants,
  commun au régime général, passe dans `regleDuParent` et `pourUnEnfantDeclare` (remaniement,
  les tests du régime général verts).
- *La fiche* `taux_plein_a_soixante_cinq_ans` : les paramètres `fonctionnaires` de la version
  de 2011 (les régimes, les motifs d'interruption, la durée, les deux seuils de huit
  trimestres) ; onze textes de plus, chacun par son identifiant et mot pour mot ; le droit de
  la version de 2011, et celui de 2026 (ci-dessous) ; l'approximation des fonctionnaires
  récrite à ce qui reste ; l'effet, le « à relire », les lectures, le code, l'historique ;
  trois régimes de plus à la fiche. Le cliquet des textes ne bouge pas (9 350 rédactions
  sans statut) : quatre rédactions passent de « à rattacher » ou « à examiner » à citées.
- *Le test*, `tests/test_taux_plein_a_soixante_cinq_ans.py` : l'âge d'annulation de
  dix-sept carrières (`CAS_FONCTIONNAIRES`), les trois régimes et la catégorie active, rendus
  par le portage et refaits par le jumeau (`droit_et_refait`) ; la pension de bout en bout,
  sept requêtes (`BOUT_EN_BOUT`), et le minimum garanti, deux requêtes, servies et refaites
  (`servi_et_refait`). Vus rouges pour la raison attendue — 66,25 au lieu de 65, « taux
  70.312% » au lieu de 75 %, le minimum fermé —, puis verts ; sans le jumeau, la
  confrontation rougit (8, 3 et 28 écarts). Les trois fonctionnaires de `ECARTS_DECLARES`
  en sortent.
- *La limite*, `docs/limites/ecarts-au-droit-positif.md` : ce que le modèle sert aux
  fonctionnaires, et ce qu'il ne lit pas.
- *Le paquet* refait : il ne diffère de celui de main que par le bloc `fonctionnaires`.
  Aucun témoin ne bouge (`construire_temoins.py`) : aucun ne porte ces naissances avec une
  interruption « élever un enfant ».

**Les textes lus, et ce qu'ils décident** (citations entières dans la fiche).

- Loi n° 2010-1330, article 28, III (LEGIARTI000023023851, du 1er juillet au 23 décembre
  2011 ; LEGIARTI000025014566, depuis ; le III identique, `--diff`) : « Pour les
  fonctionnaires nés entre le 1er juillet 1951 et le 31 décembre 1955 dont la limite d'âge
  était fixée à soixante-cinq ans avant l'entrée en vigueur de la présente loi et qui
  remplissent les conditions prévues aux 1° à 3° du IV de l'article 20, l'âge auquel
  s'annule le coefficient de minoration prévu à l'article L. 14 [...] ne peut être supérieur
  à soixante-cinq ans » ; « les enfants sont ceux énumérés au II de l'article L. 18 ».
  Article 118, II (JORFARTI000023022348) : « Les articles 18 à 40 [...] sont applicables aux
  pensions prenant effet à compter du 1er juillet 2011 ».
- Décret n° 2003-1306, article 65-3, et décret n° 2004-1056, article 50-3
  (LEGIARTI000024113270, LEGIARTI000024113274) : la même règle à la CNRACL et aux ouvriers de
  l'État, insérée par le décret n° 2010-1740, article 7 (JORFARTI000023334770), « applicables
  aux pensions liquidées à compter du 1er juillet 2011 » (article 16, III,
  JORFARTI000023334739) ; leurs « modalités d'application [...] sont celles prévues pour les
  fonctionnaires de l'Etat à l'article R. 26 ter » (décret n° 2011-620, article 10).
- R. 26 ter, I (LEGIARTI000024111781, seule rédaction, inséré par le décret n° 2011-620,
  article 3) : 1° une interruption « pendant une durée d'au moins une année » l'année de la
  naissance et les deux suivantes, ou les trois suivantes pour l'enfant né au second
  semestre, « dans le cadre des congés ou de la disponibilité mentionnés au 1° de l'article
  R. 13 », et « au titre des deux années précédant l'année de la naissance [...] une durée
  d'assurance, telle que définie à l'article L. 14, égale ou supérieure à huit trimestres » ;
  2° ou un temps partiel de R. 13, 2°, deux ans à 50 %, un an et huit mois à 60 %, un an et
  cinq mois à 70 %, avec la même durée d'assurance avant ; 3° huit trimestres « à raison de
  l'exercice d'une activité professionnelle, préalablement à l'interruption ».
- R. 13, 1° (LEGIARTI000023449727, du 1er janvier 2011 au 1er octobre 2025 ; la rédaction
  suivante ne change que les références aux statuts) : le congé de maternité, d'adoption,
  parental — celui du code du travail compris, L. 122-28-1 —, de présence parentale, et la
  disponibilité pour élever un enfant de moins de huit ans.
- L. 18, II (LEGIARTI000006362714 ; le II le même dans les quatre rédactions suivantes) :
  les enfants du titulaire, de son conjoint, délégués, sous tutelle, recueillis.
- L. 14, I (LEGIARTI000025014534 ; la première phrase la même de 2004 à aujourd'hui) : la
  durée d'assurance totalise les services et bonifications et « la durée d'assurance et des
  périodes reconnues équivalentes validées dans un ou plusieurs autres régimes de retraite
  de base obligatoires » ; le 1°, les trimestres qui séparent l'âge de liquidation de la
  limite d'âge. Loi n° 2003-775, article 66, III (LEGIARTI000006758610) : l'âge
  d'annulation, la limite d'âge moins les trimestres de l'« Année au cours de laquelle sont
  réunies les conditions mentionnées au I et au II de l'article L. 24 ».
- L. 17 (LEGIARTI000023033916) : le minimum garanti est dû « si l'intéressé a atteint l'âge
  ou la durée de services auxquels s'annule le coefficient de minoration prévu aux I et II
  de l'article L. 14 ». Décret n° 2010-1744, article 3 (JORFARTI000023334941) : cet âge n'est
  minoré que pour qui atteint l'âge d'ouverture de 2011 à 2015.
- Décret n° 2011-2103 : article 1er (JORFARTI000025061553), l'âge d'ouverture, « 1954 61 ans
  et 7 mois A compter de 1955 62 ans » ; article 8 (JORFARTI000025061595), la limite d'âge,
  de quatre mois par génération pour qui atteint soixante ans de juillet à décembre 2011, de
  cinq mois de 2012 à 2014 : 65 ans et 4 mois (1951), et 9 mois (1952), 66 ans et 2 mois
  (1953), et 7 mois (1954) ; soixante-sept ans dès 1955 (article 28, I).
- Loi n° 2025-199, article 87, IV (JORFARTI000051269910) : « Les III et IV de l'article 20
  [...] sont abrogés » ; l'article 28 ne l'est pas.
- Le Service des retraites de l'État (« La décote ») et la CNRACL (« La décote et la
  surcote »), pages lues le 3 novembre 2026 : elles ne nomment plus ces parents. Aucune
  circulaire de ces caisses sur l'article 28, III, ni aucun exemple chiffré, n'a été trouvé.

**Chaque condition, et ce que le simulateur en connaît.**

| Condition | Ce que la saisie demande | Ce que le modèle en fait |
|---|---|---|
| Sédentaire, limite d'âge de 65 ans avant la loi | le statut, son classement | lue : ni catégorie active dont il a les services, ni militaire |
| Né du 1er juillet 1951 au 31 décembre 1955, trois enfants de L. 18, II | la naissance, le nombre des enfants | lue ; les enfants du conjoint, délégués, sous tutelle, recueillis, comptés dans le nombre ; l'adoption non saisie |
| Interruption d'un an au moins, dans un congé ou une disponibilité de R. 13, 1° | les interruptions, année par année, et leur motif | lue : une année « élever un enfant » ou « congé de maternité » dans la fenêtre ; « sans activité » ne l'ouvre pas ; une année « élever un enfant » est tenue pour un congé ou une disponibilité de R. 13 (approximation) |
| Ou un temps partiel de R. 13, 2° | les années à temps partiel et leur quotité, sans motif | non lue (approximation) |
| Huit trimestres de durée d'assurance les deux années d'avant | la carrière | lue : les trimestres de tous les régimes |
| Huit trimestres d'activité avant l'interruption | la carrière | lue : l'emploi des années qui précèdent la première année de l'interruption dans la fenêtre |

Le champ « Interruptions » suffit pour l'interruption : son motif « élever un enfant » dit le
congé parental ou la disponibilité pour élever un enfant. Rien n'a été changé au site. La
réduction demanderait un motif au temps partiel saisi — « élever un enfant », un temps
partiel de R. 13, 2° — et sa durée au mois (un an et huit mois, un an et cinq mois) : un
champ de plus, que cette session n'a pas ouvert.

**Les calculs posés à la main**, pour chaque valeur que le test attend. La fonctionnaire de
l'État naît le 15 mars 1955 sauf mention, en service de 1973 à 1977 et de 2003 à 2019,
aucune ligne de 1978 à 2002 sauf les années de congé que le cas dit ; enfants d'avril 1978,
juin 1980 et juin 1982 ; partie à 65 ans, effet le 1er avril 2020.

- *Les âges du tableau.* Née en 1955 : soixante-deux ans le 15 mars 2017 ; 2017, « Limite
  d'âge moins 3 trimestres », de soixante-sept ans : 67 − 0,75 = **66,25**. Née le 15
  septembre 1954 : 61 ans et 7 mois le 15 avril 2016 ; 2016, « moins 4 trimestres », de 66
  ans et 7 mois : **65,58** (65 ans et 7 mois). Née le 15 mars 1953 : 61 ans et 2 mois le 15
  mai 2014 ; 2014, « moins 6 trimestres », de 66 ans et 2 mois : **64,67** (64 ans et 8
  mois), sous soixante-cinq ans, que la borne ne change pas. Née le 15 janvier 1956 :
  soixante-deux ans en janvier 2018 ; « moins 2 trimestres » : **66,5**, hors des
  générations. Née le 15 décembre 1955 : soixante-deux ans en décembre 2017 : 66,25.
- *Trois ans à élever un enfant* (1978 à 1980) : l'enfant d'avril 1978, fenêtre 1978-1980,
  trois années de congé, au moins une ; 1976 + 1977 = 4 + 4 = 8 trimestres ≥ 8 ; activité
  avant 1978, 1973-1977, 20 ≥ 8 : **65**. *Un an, 1980* : dans la fenêtre ; avant 8 ;
  activité avant 1980, 20 : **65**. *Un an de maternité, 1978* : un congé de R. 13, 1°, a :
  **65**. *Sans activité* : aucune année de congé : **66,25**.
- *Mars 1978, congé en 1981* : fenêtre 1978-1980 sans congé ; l'enfant de juin 1980, fenêtre
  1980-1982 avec 1981, mais 1978 + 1979 = 0 < 8 ; celui de juin 1982, fenêtre 1982-1984 sans
  congé : **66,25**. *Septembre 1978, congé en 1981* : fenêtre 1979-1981 avec 1981 ; avant
  8 ; activité avant 1981, 20 : **65**.
- *À l'année, congé en 1979* (« 1978 », « 1980 », « 1982 ») : 1979 est dans 1978-1980 et
  dans 1979-1981 ; avant 8 ; activité 20 : **65**. *À l'année, congé en 1981* : « 1978 »,
  1981 hors de 1978-1980 ; « 1980 », avant 0 ; « 1982 », aucun congé de 1982 à 1985 :
  **66,25**.
- *Huit trimestres d'activité* (en service de 1976 à 1977, congé de 1978 à 1980) : avant 8,
  activité 8 ≥ 8 : **65**. *Quatre* (1976 au chômage indemnisé, 4 trimestres validés) :
  avant 4 + 4 = 8, mais l'activité avant 1978 n'en compte que 4 ; l'enfant de juin 1980,
  congé en 1980, n'a que 4 trimestres d'activité avant 1980 ; celui de 1982, aucun congé de
  1982 à 1984 : **66,25**.
- *Deux enfants* : 2 < 3 : **66,25**. *Naissances non dites* : aucune fenêtre : **66,25**.
- *Née en septembre 1954*, congé de 1978 à 1980 : **65** ; sans activité : **65,58**. *Née en
  mars 1953* : **64,67**. *Née en décembre 1955* (en service dès 1974) : **65**. *Née en
  janvier 1956* (en service dès 1974, enfants de 1979, 1981, 1983, congé de 1979 à 1981,
  reprise en 2004) : **66,5**.
- *Les régimes* : la même carrière à la CNRACL et aux ouvriers de l'État, **65** avec trois
  enfants, **66,25** avec deux. L'emploi classé actif de la CNRACL, ses services actifs
  acquis, dont la limite d'âge n'était pas de soixante-cinq ans : le même âge avec trois
  enfants qu'avec deux, sous soixante-cinq ans.
- *De bout en bout* : la requête de `NEE_EN_1955`, les années 1978 à 1980 dites « élever un
  enfant », 1981 à 2002 « sans activité ». La durée, 112 trimestres sur 166 (108 avec deux
  enfants), en manque plus que l'âge : le plus petit des deux nombres est celui de l'âge
  (L. 14, I). À 65 ans : 0 trimestre, **75 %** ; sans la borne, 66,25 − 65 = 1,25 an, 5
  trimestres : 75 % × (1 − 5 × 1,25 %) = **70,3125 %**, de même à la CNRACL et aux ouvriers
  de l'État. À 64 ans (effet le 1er avril 2019) : 65 − 64 = 4 trimestres, 75 % × (1 − 4 ×
  1,25 %) = **71,25 %** ; sans elle, 2,25 ans, 9 trimestres, 75 % × (1 − 9 × 1,25 %) =
  **66,5625 %**. Les cas témoins, deux enfants à 65 et 64 ans, et trois enfants « sans
  activité » à 65 ans : 70,3125 %, 66,5625 %, 70,3125 %. Le test lit le taux de la formule
  au millième près.
- *Le minimum garanti* : la même requête au tiers du salaire moyen. Avec trois enfants,
  l'âge d'annulation, 65 ans, est atteint : la pension, « 5,200.71 € », est **portée au
  minimum garanti**. Avec deux, ni la durée (108 < 166) ni l'âge (65 < 66,25), et le décret
  n° 2010-1744 ne minore pas l'âge de qui atteint l'âge d'ouverture en 2017 : **pas de
  minimum**. Le test n'en affirme pas le montant, que la règle ne change pas.

**Ce que les textes ne tranchent pas**, et que la fiche dit comme tel.

- Depuis le 1er janvier 2026, l'article 28, III, toujours en vigueur, renvoie aux conditions
  du IV de l'article 20, abrogé. Rien n'en dépend : né au plus tard le 31 décembre 1955, le
  fonctionnaire a alors soixante-dix ans au moins, au-delà de l'âge d'annulation de sa
  décote, qui ne passe pas sa limite d'âge, soixante-sept ans au plus. Le modèle date la
  borne avec la version de 2011, jusqu'au 1er janvier 2026.
- Les décrets de la CNRACL et des ouvriers de l'État visent les pensions « liquidées » à
  compter du 1er juillet 2011, la loi celles « prenant effet » à cette date ; le modèle date
  les trois par la date d'effet. Né à compter de juillet 1951, le sédentaire ouvre son
  droit en novembre 2011 au plus tôt, et n'est concerné qu'en 1954 et 1955 : sans effet.
- R. 26 ter dit « une durée d'au moins une année », sans la dire continue ; la saisie compte
  des années entières.

**Les vérifications.** Un script a cherché chaque fragment cité entre « » des versions de la
fiche dans le texte de l'index : aucun n'y manque ; les citations de l'approximation et des
lectures de même, et celle du SRE dans sa page. `python -m pytest -m rapide` : 4 323
passés ; sous `PRESOMPTIONS_DECALEES=1` : 4 125 passés ; `test_regle_de_chacun.py`, les
confrontations légères, et les tests qui lisent les fichiers touchés (`test_carte.py`,
`test_textes.py`, `test_pont.py`, `test_fabrique.py`, `test_agirc_arrco_au_droit.py`,
`test_simulateur.py`…) : verts. `test_prose.py` rougit deux fois, comme tout envoi qui
touche au moteur : le tableau de bord, et le poids du moteur ancré dans `README.md` (916 à
918), que GitHub refait.

**Ce qui reste**, et qui n'est pas de cette session : la réduction d'activité des
fonctionnaires (le champ ci-dessus) ; à la file M4, la CAVIMAC et les points d'avant 1973,
puis les non-salariés agricoles, les libéraux et les avocats ; une circulaire du SRE ou de
la CNRACL sur l'article 28, III, si elle existe.

*Renvoi du 3 novembre 2026* : la relecture R-M4 a relevé qu'une année « congé de maternité »
ouvrait seule la borne, quand R. 26 ter veut une année d'interruption ; corrigé, avec
quatre écarts faibles, par la file M4-bis (note
`2026-11-03-corrections-de-la-relecture-r-m4-fonctionnaires.md`).
