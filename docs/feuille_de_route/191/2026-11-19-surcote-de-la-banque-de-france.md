# La surcote de la Banque de France, lue dans son règlement

Le 19 novembre 2026, sur l'accord du propriétaire (« dans une étape à part »,
« je veux que cela soit le réel »), le scénario 1 sert à l'agent titulaire de
la Banque de France la surcote de l'article 33 de son règlement, trimestre
par trimestre, et non plus le taux plat de l'année du départ. L'écart avait
été trouvé le matin même (`2026-11-19-quatre-dates-au-jour.md`). L'étape
s'est menée sur Fable 5.2.

**Le texte.** Règlement annexé au décret n° 2007-262 du 27 février 2007,
article 33, dans les quatorze rédactions de l'annexe que porte l'index LEGI.
Il a quatre textes.

- L'origine (`LEGIARTI000006778516`) : 0,75 % par trimestre, « dans la limite
  de vingt trimestres », pour les seuls trimestres « effectués après le
  1er avril 2007, au-delà de l'âge de soixante ans » et en sus de la durée.
- Le décret n° 2008-1514 du 30 décembre 2008, article 1er
  (`JORFARTI000020018201`) : 1,25 %, mais pour les seuls « trimestres
  d'assurance cotisés et effectués à compter du 1er janvier 2009 ». Ceux
  d'avril 2007 à décembre 2008 gardent 0,75 %.
- Le décret n° 2012-701 du 7 mai 2012, article 26 (`JORFARTI000025824221`) :
  l'âge devient celui de l'article 26, la limite de vingt trimestres tombe et
  les bonifications sortent de la durée ; ces deux derniers points ne valent
  que pour les pensions prenant effet depuis le 1er janvier 2016 (article 41).
- La rédaction du 1er janvier 2025 (`LEGIARTI000047909725`) ajoute la surcote
  des parents, sans toucher au reste.

**Ce qui change.** Une fiche, `surcote_banque_de_france`, en trois versions
sur la date d'effet : aucune surcote avant le règlement (supposée), vingt
trimestres au plus jusqu'en 2015, sans limite depuis 2016 ; chacune porte les
deux taux, par date de trimestre. Les seize périodes du régime, depuis avril
2007, y renvoient, et celle d'avril à décembre 2007 retrouve sa surcote. Le
portage lit la version (`coefficientSurcoteBanqueDeFrance`, `liquider.js`) :
les trimestres cotisés entiers depuis le mois où l'âge est révolu, au plus
tôt la première date de la table, dans la limite de ceux qui dépassent la
durée, les plus récents d'abord. Aucun chiffre de la loi n'entre dans le
code. Les trimestres se comptent en mois (`trimestresCotisesAuMois`) : le
mois de janvier d'un départ en février, qui ne valide rien à lui seul, achève
le trimestre commencé l'année d'avant.

**Ce qui bouge.** Un témoin de simulation sur 934 : l'agent né en 1945 parti
à 64 ans en 2009, majoré de 5,25 % et non de 20 %, perd 12,3 % de sa pension.
Aucun des 86 rendus de page. Sur des carrières simples, commencées à vingt
ans, nées en janvier :

| Né en | Départ | Surcote avant | Surcote après | Pension mensuelle |
|---|---|---|---|---|
| 1945 | novembre 2007 | aucune | 1,5 % | 2 226 € → 2 259 € |
| 1945 | février 2008 | 9 % | 2,25 % | 2 477 € → 2 324 € |
| 1945 | février 2009 | 20 % | 5,25 % | 2 745 € → 2 408 € |
| 1946 | février 2009 | 15 % | 5,25 % | 2 631 € → 2 408 € |
| 1947 | février 2010 | 15 % | 10,25 % | 2 711 € → 2 599 € |
| 1948 | février 2010 | 10 % | 8 % | 2 593 € → 2 546 € |
| 1948 | février 2011 | 15 % | 13 % | 2 768 € → 2 720 € |
| 1949 et après | tout départ | inchangée | inchangée | inchangée |

Ne bougent que les agents qui avaient soixante ans avant 2009 : les autres
n'ont que des trimestres à 1,25 %, tous d'après le 1er avril 2007.

**Les deux cliquets.** La fiche entre par un renvoi neuf et trois versions
sans exemple publié, que les cliquets 2 et 4 de la note 0009 refusent sans
leurs preuves. Plutôt que de relever leurs nombres, l'étape donne au renvoi
la place qui manquait, au plus court : une période cite le texte du renvoi
qu'elle ouvre (`textes_des_renvois`, schéma des régimes), et l'étape qui
datera et citera tous les renvois peut refaire ce champ. Les versions disent
ce qui a été cherché dans `exemples_cherches`, que l'étape 2 du cumul a
ajouté au contrat de la fiche le même jour.

**Ce qui reste.** La fiche est approchée.

- Deux présomptions, que la fiche déclare : un trimestre à cheval sur le
  1er janvier 2009 garde 0,75 % ; quand la limite de vingt trimestres joue,
  les plus anciens tombent. Aucun exemple chiffré publié n'a été trouvé, et
  ni la Banque ni une circulaire n'ont été interrogées.
- Ne sont pas servies : la surcote des parents, depuis 2025 ; les
  bonifications écartées de la durée, depuis 2016 ; la catégorie de l'agent
  dont le droit s'ouvre à 55 puis 57 ans, que la saisie ne dit pas.
