# Les droits familiaux, règle par règle : dix-sept fiches, pour le stock et pour l'avenir

**Reprise, au 13 novembre 2026.** Les dix-sept dispositifs sont tranchés
(décisions 50 à 61). Le 13 novembre, le propriétaire a fixé la base du partage
: la moitié de l'économie comptée avant la garantie va aux parents, soit 0,40
point de PIB par an (décision 114). Reste à étudier aux sources la prestation
en argent aux parents d'aujourd'hui, et celle des parents d'enfants handicapés
; puis une session du modèle, sur la proposition seule (« Ce qui reste à faire
»). Restent au chantier 3 les 49 autres dispositifs.

*Le 7 novembre 2026, à la lecture de l'étude des enfants
(`2026-11-07-enfants-etude-et-couts.md`), le propriétaire ne retient aucune
règle d'ensemble : « Il faut évaluer règle par règle ». Cette note évalue donc
chaque dispositif à part, pour les retraités déjà servis (le stock) et pour
les carrières à venir (l'avenir). Elle est menée en série, comme le
propriétaire l'a choisi, sans recherche nouvelle hors du dépôt : les règles
sont celles des fiches (`data/reference/regles/`,
`data/reference/legislation/avantages_non_contributifs.yaml`), les chiffres
et les décisions de justice ceux de l'étude, que cette note répartit
dispositif par dispositif. Ce qui n'a été lu ni à la source ni dans le dépôt
est marqué « à vérifier ».*

## Comment lire les fiches

Chaque fiche dit la règle et son article ; les quatre questions du programme
(subi ? constaté par un tiers ? qui paie ? forfaitaire ?) ; le coût et le
payeur d'aujourd'hui ; qui en profite ; le risque juridique d'une reprise sur
le stock et d'une suppression pour l'avenir ; les options et leur coût face
au droit actuel ; une proposition.

**Les chiffres.** (publié), (dépôt), (à côté) et (relais) ont le sens de
l'étude. Les coûts moyens sur 2026-2070 sont en points de PIB, face au droit
actuel (le scénario 1) : « + » est une économie, « − » un coût, « brut →
net » retranche ce que la garantie vieillesse, servie d'office, rend aux
parents qui passent sous le plancher. Ils sont tous à côté, tirés de l'étude
et répartis ainsi :

- *Le stock* — les pensions liquidées avant la bascule, qui est en 2026 au
  modèle (`annee_bascule`, `src/retraite_notionnelle/config.py`, l. 500) —
  vaut 0,295 brut, 0,232 net. Réparti au prorata du profil du COR pour 2022
  (majoration 2,92 % des pensions, MDA et bonifications 2,68 %, AVPF 1,19 %,
  départs 0,49 %, l'hypothèse H1 de l'étude), il redonne exactement ses
  systèmes B et C. La garantie rend 29 % des droits liés à la carrière, 9 %
  de la majoration.
- *L'avenir* vaut 0,681 brut, 0,570 net. La majoration y pèse 0,234 (le coût
  de l'« enveloppe constante » F3a de l'étude), l'AVPF 0,137 (F6) ; le reste,
  0,310, est la MDA, les bonifications, la surcote parentale et le salaire de
  référence des parents. Le partage entre ces derniers, et entre les régimes,
  suit les coûts de 2024 du COR et les ordres de grandeur publiés : c'est la
  part la plus fragile, à 0,01 ou 0,02 point près.
- *Le prix d'un droit nouveau.* Un crédit d'une année de cotisation, au taux
  de 18 % sur le salaire moyen, pour chacun des 650 000 enfants de l'année,
  vaut 5,0 Md€ en 2026 et 0,16 point en moyenne, en cotisations versées comme
  en pension servie, les enfants déjà nés crédités ; il rend environ 27 € de
  pension par mois et par enfant. Sur l'assiette de l'AVPF (2 031,38 € par
  mois en 2026, dépôt, `legislation/assiette_avpf.csv` ; 0,57 salaire moyen),
  0,09 point et 15 €. Un forfait de pension de 10 € par mois et par enfant
  coûte 0,06 point (tirés des systèmes F4, F5 et F3 de l'étude).

## Ce qui vaut pour toutes les fiches

1. **Le compte ne connaît ni trimestre, ni âge légal, ni salaire de
   référence.** Pour l'avenir, un droit qui agit par la durée, l'âge ou
   l'assiette n'a plus d'objet : il disparaît, ou il se traduit en argent —
   un crédit de cotisation porté au compte, ou un forfait de pension. C'est
   la décision 27 : les droits suivent l'argent.
2. **Pour le stock, la règle est la baisse** (décisions 2 et 3) : la pension
   entière, droits familiaux compris, descend en cinq ans au plus vers ce que
   les cotisations justifient, sous la garantie servie d'office
   (décision 20). Garder un dispositif jusqu'à extinction est une exception,
   comme la décision 16 l'a faite pour la réversion ; il reste alors payé par
   les régimes, donc par les autres cotisants, sauf si un tiers le reprend.
3. **Le droit** (étude) : reprendre d'un coup est exposé (élevé ; très élevé
   pour la MDA et la bonification, qui vont aux femmes : discrimination
   indirecte, *Brachner*) ; baisser en cinq ans avec un plancher l'est moins
   (moyen) ; supprimer pour l'avenir l'est peu (faible ; moyen sans transition
   près du départ). Une règle réservée à la mère tient pour la maternité
   (*Abdoulaye*), non pour l'éducation (*Griesmar*, *WA*, C-623/23) ; faute
   d'accord des parents, l'attribuer à celui qui a la plus petite pension est
   sûr (C-623/23).
4. **La décision 4** — ne pas faire payer deux fois une génération — touche
   les enfants : les retraités d'aujourd'hui ont payé la pension de leurs
   aînés et élevé les cotisants qui paient la leur. Leur reprendre ce qui
   compense l'éducation peut se lire comme un double paiement ; c'est un
   argument pour garder le stock, non une règle.
5. **Le fil — les cotisants et les petites pensions.** La MDA, l'AVPF et les
   départs anticipés vont à 96 à 98 % aux femmes, et d'abord aux petites
   pensions ; la majoration de 10 % suit la pension.
6. **La décision 28** : ce qui se décide ici vaut pour le scénario 6 ; les
   autres scénarios notionnels ne montrent que les parts contributives.

## Le tableau d'ensemble

Coûts de 2024 publiés par le COR (rapport de novembre 2025, tableau 1.9),
sauf mention ; « femmes » est leur part de la masse (COR, 2020).

| # | Dispositif | Coût 2024 | Payeur aujourd'hui | Femmes | Subi ? | Tiers ? | Forfait ? | Proposition, stock | Proposition, avenir |
|---|---|---|---|---|---|---|---|---|---|
| 1 | MDA de maternité | ≈ 3,6 Md€ (à côté) | les régimes | 100 % | en partie | état civil | non | gardée | crédit de maternité, assurance maternité |
| 2 | MDA d'éducation | ≈ 3,6 Md€ (à côté) | les régimes | ≈ 100 % | non | non | non | gardée | crédit d'éducation, branche famille |
| 3 | MDA d'adoption | non publié, faible | les régimes | — | non | jugement | non | gardée | comme 1 et 2 |
| 4 | MDA de congé parental | non publié | les régimes | — | non | employeur, CAF | non | gardée | fondue dans l'AVPF |
| 5 | MDA d'enfant handicapé | non publié, faible | les régimes | — | **oui** | **CDAPH** | non | gardée | crédit, payeur de l'AEEH |
| 6 | Bonification de la fonction publique (avant 2004) | dans 1,82 Md€ | l'État, la CNRACL | surtout | non | employeur | non | gardée, à l'employeur | le droit commun (1 et 2) |
| 7 | Majoration de durée de la fonction publique (depuis 2004) | dans 1,82 Md€ | l'État, la CNRACL | 100 % | en partie | état civil | non | gardée, à l'employeur | le droit commun (1) |
| 8 | Trimestres d'enfants des régimes spéciaux | dans 1,82 Md€ | les régimes, l'État | surtout | en partie | employeur | non | gardés, au payeur du régime | le droit commun |
| 9 | Majoration de 10 %, régime général et alignés | 5,21 Md€ | la branche famille | 38 % | non | état civil | **non** | suit la baisse | retirée |
| 10 | Majoration des fonctionnaires et des régimes spéciaux | 2,65 Md€ | l'État, les employeurs | — | non | état civil | non | suit la baisse | retirée |
| 11 | Majoration des complémentaires | 1,84 Md€ | leurs cotisants | — | non | état civil | non | suit la caisse | sa caisse, puis le n° 9 |
| 12 | AVPF | 4,39 Md€ servis ; 5,10 cotisés (dépôt) | la branche famille | 96 % | en partie | CAF | **oui** | gardée | gardée |
| 13 | Surcote parentale | ≈ 0 | les régimes | surtout | non | état civil | non | sans objet au modèle | sans objet |
| 14 | Salaire de référence des parents | 0 ; 0,2 Md€ en 2030 (presse) | les régimes | surtout | non | état civil | non | sans objet au modèle | sans objet |
| 15 | Trimestres d'enfants réputés cotisés | non publié | les régimes | surtout | non | état civil, CAF | non | sans objet au modèle | sans objet |
| 16 | Départs anticipés des parents de trois enfants | 1,19 Md€ | l'État, la CNRACL | 98 % | non | employeur | non | gardés, à l'employeur | fermés |
| 17 | Majorations de la réversion pour enfants | non isolé | les régimes | surtout | **oui** (le décès) | état civil | 17a oui | gardées (décision 16) | 17a : branche famille ; 17b : suit le n° 9 |

## Les fiches

### 1. La MDA de maternité

**La règle.** Quatre trimestres par enfant à la mère, « au titre de
l'incidence sur [sa] vie professionnelle de la maternité, notamment de la
grossesse et de l'accouchement » (L. 351-4, I, CSS ; pensions depuis le
1er avril 2010, loi n° 2009-1646, article 65). Pour un enfant né avant 2010,
les huit trimestres vont à la mère, sauf si le père a prouvé dans le délai
qu'il l'a élevé seul (dépôt, `majoration_duree_assurance_enfants.yaml`).

**Les quatre questions.** *Subi* : en partie. L'enfant est voulu, mais le
congé de maternité est imposé par la loi, et l'incidence de la grossesse sur
la carrière ne se choisit pas. *Constaté* : oui, par l'état civil. *Qui
paie* : les régimes, sans aucune compensation : les autres cotisants. *Forfaitaire* :
non ; quatre trimestres ne valent rien à la mère qui a sa durée, jusqu'à
7 % de pension environ à celle qui ne l'a pas (à côté : 4/172 de prorata et
5 points de décote effacés).

**Coût et payeur.** Aucune série ne sépare la maternité de l'éducation ; la
MDA entière coûte 9,64 Md€ (publié), dont 7,16 pour la Cnav et la MSA et
0,66 d'effet induit sur les complémentaires. La moitié des trimestres du
régime général, environ 3,6 Md€ (à côté, à vérifier).

**Qui en profite.** Les mères seules, par la loi. Avec l'AVPF, la MDA est le
droit familial « le plus redistributif » (publié, COR, novembre 2025) : les
droits familiaux font 25 % de la pension des femmes du premier quartile, 6 %
au dernier (publié, COR, octobre 2023, doc. 8).

**Le droit.** Stock : reprise élevée (discrimination indirecte, protection
des biens ; *Brachner*, *Béláné Nagy*). Avenir : suppression faible ; un droit
réservé à la mère y est admis, s'il compense un désavantage professionnel réel
(*Abdoulaye*, directive 79/7, article 4, § 2) : faible.

**Options.**

| Option | Stock | Avenir | Qui paie |
|---|---|---|---|
| Reprise avec la baisse, rien pour l'avenir (la proposition) | +0,044 → +0,031 | +0,10 → +0,08 | les mères |
| Gardée, rien pour l'avenir | 0 | +0,10 → +0,08 | les mères à venir |
| Gardée ; un crédit d'une année sur l'assiette de l'AVPF, à la naissance, au compte de la mère (15 € par mois et par enfant) | 0 | ≈ +0,01 | l'assurance maternité, 0,09 point |
| Gardée ; un crédit d'une année au salaire moyen (27 €) | 0 | ≈ −0,06 | l'assurance maternité, 0,16 point |

**Proposition.** Garder le stock jusqu'à extinction ; pour l'avenir, un crédit
de cotisation au compte de la mère, d'une année sur l'assiette de l'AVPF,
payé par l'assurance maternité, qui sert déjà le congé : à coût public à peu
près égal, le payeur change, et le crédit va d'abord aux petits comptes, en
forfait. Le congé de maternité lui-même relève des périodes assimilées, que
la pile des accidents du chantier 3 met à la charge de l'assureur du risque.

### 2. La MDA d'éducation

**La règle.** Quatre trimestres par enfant pour son éducation pendant les
quatre années qui suivent sa naissance ou son adoption, « au choix des
parents », « à défaut d'accord des parents, la mère » (L. 351-4, II ; fiche
`majoration_duree_assurance_enfants.yaml`, l. 171-173). Le modèle présume
qu'aucun accord n'a été exprimé, et sert tout à la mère.

**Les quatre questions.** *Subi* : non ; élever l'enfant suit le choix de
l'avoir. *Constaté* : mal ; l'état civil dit que l'enfant existe, personne
ne constate qui l'élève, et l'option est déclarative. *Qui paie* : les
régimes. *Forfaitaire* : non, comme le n° 1.

**Coût et payeur.** Environ 3,6 Md€ en 2024, l'autre moitié des trimestres
du régime général (à côté, à vérifier), adoption, congé parental et enfant
handicapé compris.

**Qui en profite.** Presque toutes des mères, par le défaut et par le stock,
où l'éducation des enfants nés avant 2010 leur revenait ; combien de pères
l'ont reçue par accord n'est pas publié (à vérifier).

**Le droit.** Stock : reprise élevée. Avenir : suppression faible ; un droit
d'éducation réservé aux mères, élevé (très élevé dans la fonction publique,
*Griesmar*) ; à la mère faute d'accord, moyen (*WA*, C-623/23) ; au parent
qui a la plus petite pension faute d'accord, minime (C-623/23).

**Options.**

| Option | Stock | Avenir | Qui paie |
|---|---|---|---|
| Reprise avec la baisse, rien pour l'avenir (la proposition) | +0,044 → +0,031 | +0,10 → +0,08 | les parents |
| Gardée, rien pour l'avenir | 0 | +0,10 → +0,08 | les parents à venir |
| Gardée ; un crédit d'une année sur l'assiette de l'AVPF, au parent choisi, à défaut au plus petit compte | 0 | ≈ +0,01 | la branche famille, 0,09 point |
| Gardée ; un forfait de pension de 15 € par enfant, à la liquidation | 0 | ≈ +0,01 | la branche famille, au fil de l'eau |

**Proposition.** Garder le stock ; pour l'avenir, retirer le droit aux
régimes et le confier, s'il est gardé, à la branche famille, en crédit
forfaitaire d'une année sur l'assiette de l'AVPF, au parent que les parents
désignent, à défaut au parent dont le compte est le plus petit à la date du
choix. La branche famille le paie avec ce qu'elle verse aujourd'hui pour la
majoration de 10 % (n° 9), que la proposition retire pour l'avenir.

### 3. La MDA d'adoption

**La règle.** Quatre trimestres par enfant adopté mineur, au titre de
l'accueil de l'enfant et des démarches qui le précèdent, au choix des parents
(L. 351-4, III) ; ils tiennent la place de la maternité, et l'éducation
s'y ajoute. Le modèle ne la porte pas (fiche, l. 222).

**Les quatre questions.** *Subi* : non. *Constaté* : oui, par le jugement
d'adoption. *Qui paie* : les régimes. *Forfaitaire* : non.

**Coût.** Non publié ; la population est étroite (à vérifier : le nombre
d'adoptions par an).

**Le droit.** Comme le n° 2 : un droit au choix des parents ; reprise sur le
stock élevée, suppression pour l'avenir faible.

**Proposition.** Garder le stock ; pour l'avenir, le même crédit que la
maternité (n° 1), payé par l'assurance maternité, qui sert le congé
d'adoption, au parent que les parents désignent, à défaut au plus petit
compte. Coût négligeable.

### 4. La MDA de congé parental

**La règle.** La durée effective du congé parental d'éducation s'ajoute à la
durée d'assurance, quand elle vaut mieux que la MDA d'éducation ; les deux ne
se cumulent pas (L. 351-5 CSS). Le modèle ne la sert pas : la saisie ne dit
pas la durée du congé (`avantages_non_contributifs.yaml`).

**Les quatre questions.** *Subi* : non. *Constaté* : oui, par l'employeur, et
par la CAF quand une prestation le paie. *Qui paie* : les régimes. *Forfaitaire* :
non.

**Coût.** Non publié ; borné par le haut, puisqu'il ne vaut jamais moins que
la MDA d'éducation, déjà comptée.

**Le droit.** Comme le n° 2.

**Proposition.** Garder le stock, avec la MDA ; pour l'avenir, ne pas en
faire un droit à part : le parent en congé qui touche une prestation de la
branche famille y a, sous ses conditions, l'AVPF (L. 381-1 ; à vérifier, les
conditions du congé indemnisé), qui est déjà une cotisation au compte
(n° 12).

### 5. La MDA d'enfant handicapé

**La règle.** Un trimestre par période de trente mois d'éducation d'un
enfant ouvrant droit à l'allocation d'éducation de l'enfant handicapé (AEEH),
huit au plus ; elle se cumule avec la MDA ordinaire (L. 351-4-1 CSS ;
`avantages_non_contributifs.yaml`). Le modèle ne la sert pas.

**Les quatre questions.** *Subi* : oui ; le handicap d'un enfant est un
accident de la vie, et la première répartition du chantier 3 le range parmi
les droits gardés. *Constaté* : oui, par la commission des droits et de
l'autonomie, qui ouvre l'AEEH. *Qui paie* : les régimes. *Forfaitaire* : non.

**Coût.** Non publié (étude : non trouvé) ; « probablement le plus faible de
la famille » (dépôt).

**Le droit.** Reprise sur le stock : élevée, et sans justification à
opposer. Suppression pour l'avenir : faible en droit, contraire au critère
du programme.

**Proposition.** Gardée, pour le stock et pour l'avenir ; pour l'avenir, un
crédit forfaitaire au compte du parent qui élève l'enfant, payé par la branche
qui sert l'AEEH (la branche autonomie depuis 2021, à vérifier), et non plus par
les autres cotisants. La branche famille cotise déjà à l'AVPF pour le parent
d'un enfant handicapé (L. 381-1), et l'assurance vieillesse des aidants
existe depuis 2023 ; le crédit s'y raccorde.

### 6. La bonification pour enfants de la fonction publique

**La règle.** Pour chaque enfant né avant 2004, quatre trimestres de services
à l'un ou l'autre parent, après une interruption ou une réduction d'activité
de deux mois, le congé de maternité compris (L. 12 b CPCMR ; CNRACL et
FSPOEIE de même ; fiche `enfants_fonction_publique.yaml`, l. 142-145).

**Les quatre questions.** *Subi* : non. *Constaté* : oui, l'interruption par
l'employeur. *Qui paie* : l'État employeur et les employeurs de la CNRACL.
*Forfaitaire* : non ; des services ajoutés, au pourcentage du traitement.

**Coût et payeur.** Dans les 1,82 Md€ de la MDA des régimes de base autres
que la Cnav et la MSA (publié). Fin 2025, 1,59 million de pensions de
fonctionnaires la portent, avec huit trimestres en moyenne ; elle vaut
191 € par mois aux civils de l'État liquidés en 2025 (publié, jaune des
pensions pour 2027, tableaux A-7 et 50, dépôt,
`legislation/bonifications_jaune.csv`). Ces deux chiffres donneraient plus de
1,8 Md€ aux seuls civils de l'État si le gain des liquidants valait pour le
stock : l'écart avec le COR reste à comprendre (à vérifier).

**Qui en profite.** Surtout des mères : la Cour de justice note qu'elle leur
profite par le congé de maternité (*Leone*).

**Le droit.** Elle est née de *Griesmar* (2001), qui l'a ouverte aux pères ;
la condition d'interruption est une discrimination indirecte sauf
justification (*Leone*, C-173/13, 2014), et le Conseil d'État l'a jugée
justifiée par la compensation des retards de carrière des femmes
(*Quintanel*, 2015). Reprise sur le stock : très élevée — la reprendre
retirerait la compensation même que le juge a validée. Pour l'avenir, elle ne
vaut que pour les enfants nés avant 2004, donc pour des mères qui partiront
d'ici 2050 environ : moyen sans transition.

**Options.** Stock : reprise +0,021 → +0,015, avec les n° 7 et 8 (à côté).
Avenir : retirée, environ +0,05 → +0,04 avec les n° 7 et 8 ; traduite en
crédit payé par l'employeur, une année de cotisation sur le traitement par
enfant, coût voisin du droit actuel.

**Proposition.** Garder le stock jusqu'à extinction, à la charge de
l'employeur public, comme aujourd'hui : c'est la pile « accordés par l'État
ou un employeur » du chantier 3. Pour l'avenir, le droit commun des n° 1 et 2,
le même pour un fonctionnaire que pour un salarié : le régime est unique.

### 7. La majoration de durée de la fonction publique

**La règle.** Pour chaque enfant né depuis 2004, deux trimestres à la mère
qui a accouché après son recrutement : en durée seulement (L. 12 bis CPCMR),
puis, pour les pensions depuis le 1er septembre 2026, dont un en services
(L. 12 b ter, loi n° 2025-1403, article 104 ; décret n° 2026-699 ; fiche,
l. 173-186). Les interruptions et temps partiels pour élever un enfant
comptent en outre comme services, jusqu'à trois ans par enfant (L. 9 ;
`decompte_des_services_fonction_publique.yaml`, l. 25).

**Les quatre questions.** Celles du n° 1 : *subi* en partie, *constaté* par
l'état civil, *payé* par l'employeur public, *non forfaitaire*.

**Coût.** Dans les 1,82 Md€ du n° 6 (publié) ; non séparé.

**Le droit.** Réservée à la mère qui accouche : faible (*Abdoulaye*).
Reprise sur le stock : élevée.

**Proposition.** Garder le stock, à la charge de l'employeur ; pour l'avenir,
le crédit de maternité du n° 1, le même pour toutes les mères.

### 8. Les trimestres d'enfants des régimes spéciaux

**La règle.** À la SNCF, deux trimestres de durée par enfant à la mère qui a
accouché après son recrutement ; à la RATP et aux IEG, une année de services
par enfant né avant le 1er juillet 2008 — deux pour le second d'une fratrie
de deux aux IEG —, puis deux trimestres de durée pour le premier enfant et
quatre pour les suivants ; à la CRPCEN, quatre trimestres par enfant né avant
le 1er juillet 2006, puis deux et quatre (fiches `enfants_sncf.yaml`,
`enfants_ratp.yaml`, `enfants_ieg.yaml`, `enfants_crpcen.yaml`). Les
bonifications vont à la mère ; le père qui a pris deux mois de congé n'en
reçoit pas.

**Les quatre questions.** *Subi* : en partie, pour ce qui suit
l'accouchement. *Constaté* : oui. *Qui paie* : le régime, et, par sa
subvention d'équilibre ou les employeurs, l'État et les entreprises.
*Forfaitaire* : non.

**Coût.** Dans les 1,82 Md€ du n° 6 ; non séparé.

**Le droit.** Les bonifications réservées aux mères pour l'éducation sont
exposées comme dans la fonction publique avant 2003 (*Griesmar*), mais c'est
leur reprise, non leur maintien, que la proposition envisage : reprise sur le
stock élevée.

**Proposition.** Garder le stock, à la charge de celui qui équilibre le
régime ; pour l'avenir, le droit commun des n° 1 et 2.

### 9. La majoration de 10 %, au régime général et dans les régimes alignés

**La règle.** Dix pour cent de la pension au père comme à la mère de trois
enfants, nés ou élevés neuf ans avant leurs seize ans (L. 351-12 CSS ;
non-salariés agricoles ; professions libérales depuis le 1er septembre 2023,
loi n° 2023-270, article 21 ; fiches `majoration_dix_pour_cent.yaml`,
`cnavpl_majoration_duree_assurance.yaml`).

**Les quatre questions.** *Subi* : non ; le troisième enfant est voulu.
*Constaté* : oui, par l'état civil. *Qui paie* : la branche famille, qui la
rembourse à la Cnav et à la MSA, 5,77 Md€ en 2024 (dépôt,
`macro/transferts_retraite.csv`, l. 105 ; 5,21 selon le COR). *Forfaitaire* :
non ; proportionnelle à la pension, c'est le seul droit familial qui croît
avec le salaire.

**Coût.** 5,21 Md€ pour la Cnav et la MSA en 2024 (publié).

**Qui en profite.** Pour 62 % les hommes, qui n'en sont pas plus souvent
bénéficiaires : 136 € par mois en moyenne contre 77 € ; les 10 % d'hommes les
plus aisés en reçoivent 2,2 des 8,4 Md€ de 2020 (relais, DREES, dossier
n° 128). Mais elle vaut 10 % pour tous : elle reproduit les écarts sans les
créer, et c'est le seul droit familial qui creuse, d'un rien, l'écart entre
femmes et hommes (étude).

**Le droit.** Stock : reprise d'un coup élevée ; en cinq ans sous le
plancher, moyen. Avenir : suppression faible ; le gouvernement propose
lui-même de la remplacer par un forfait de 105 à 110 € par mois pour une
carrière complète, aux pensions de juillet 2027 (projet de loi de financement
pour 2027, article 34, rejeté par l'Assemblée le 23 octobre 2026, au Sénat) :
s'il est voté, c'est le droit actuel qui change.

**Options.**

| Option | Stock | Avenir | Qui paie |
|---|---|---|---|
| Suit la baisse, retirée pour l'avenir (la proposition) | +0,064 → +0,058 | +0,126 → +0,12 | les parents de trois enfants, au prorata de leur pension |
| Gardée jusqu'à extinction, retirée pour l'avenir | 0 | +0,126 → +0,12 | les parents à venir |
| Suit la baisse ; le forfait du gouvernement pour l'avenir (≈ 35 € par enfant au-delà du deuxième) | +0,064 → +0,058 | ≈ 0 | la branche famille |
| Suit la baisse ; son budget redéployé vers les crédits des n° 1 et 2 | +0,064 → +0,058 | ≈ +0,13, moins ces crédits | la branche famille |

**Proposition.** La laisser suivre la baisse générale pour le stock, en cinq
ans, sous la garantie, qui en rend 9 % ; la retirer pour l'avenir : elle
donne le plus à qui a le plus, et un enfant n'y ouvre rien avant le
troisième. Ce que la branche famille y consacre aujourd'hui paie les crédits
forfaitaires des n° 1, 2 et 3.

### 10. La majoration des fonctionnaires et des régimes spéciaux

**La règle.** Dix pour cent pour trois enfants et 5 % par enfant au-delà,
sans que la pension majorée excède le traitement (L. 18 CPCMR ; CNRACL,
FSPOEIE ; fiche `majoration_enfants_plafond_fonction_publique.yaml`) ; de même
à la SNCF, à la RATP, aux IEG, à la CRPCEN, au SEITA, à l'Opéra et à la
Comédie-Française ; 8,5 % puis 4,25 % à la Banque de France ; un dixième aux
mines ; chez les marins, 5 %, 10 % et 15 % de la pension pour deux, trois et
quatre enfants élevés neuf ans (fiches `majoration_enfants_regimes_speciaux.yaml`,
`marins_bonification_enfants.yaml`).

**Les quatre questions.** Celles du n° 9 ; *qui paie* : l'État employeur,
environ 2,15 Md€ (dépôt, jaune de 2024, cité par l'étude), les employeurs de
la CNRACL, les régimes spéciaux et leur subvention.

**Coût.** 2,65 Md€ pour les régimes de base autres que la Cnav et la MSA en
2024 (publié).

**Le droit.** Comme le n° 9 ; ouverte aux deux parents, elle n'a pas le
risque de *Griesmar*.

**Options.** Stock : suit la baisse, +0,032 → +0,029 ; gardée, 0. Avenir :
retirée, +0,064 → +0,06 (à côté).

**Proposition.** Comme le n° 9 : suit la baisse, puis retirée. Le régime étant
unique, un fonctionnaire n'a pas, pour l'avenir, d'autre droit familial qu'un
salarié.

### 11. La majoration des complémentaires

**La règle.** À l'Agirc-Arrco, 10 % pour trois enfants, plafonnés (2 367,48 €
par an, étude), ou 5 % par enfant à charge au départ, tant qu'il le reste,
quand c'est plus ; des taux anciens selon l'année d'acquisition des points
(fiches `majoration_enfants_agirc_arrco.yaml`,
`majoration_enfants_a_charge_agirc_arrco.yaml`). À l'Ircantec, de 10 % pour
trois enfants à 30 % pour sept, sans plafond (`ircantec_majoration_enfants.yaml`).

**Les quatre questions.** *Subi* : non. *Constaté* : oui. *Qui paie* : les
cotisants de la caisse, sans argent extérieur. *Forfaitaire* : non, mais
plafonnée à l'Agirc-Arrco.

**Coût.** 1,84 Md€ en 2024 (publié).

**Le droit.** Le régime de l'Agirc-Arrco est conventionnel : la retirer par
la loi touche la liberté contractuelle des partenaires sociaux (CC
2013-672 DC ; l'étude cote le risque faible). L'Ircantec est réglementaire.

**Les décisions qui la règlent déjà.** Une complémentaire ne vit que de ses
cotisations (décision 12), garde ses cotisations jusqu'à son intégration
(décision 40), puis rejoint le régime général. Ce que ses pensions deviennent
jusque-là est l'une des questions ouvertes du chantier 6.

**Options.** Stock : suit la baisse de la caisse, +0,022 → +0,020 ; gardée,
0. Avenir : retirée à l'intégration, +0,044 → +0,04 (à côté).

**Proposition.** Jusqu'à l'intégration, la règle de la caisse : les
partenaires sociaux pour l'Agirc-Arrco, l'État pour l'Ircantec ; ensuite, la
règle du régime général (n° 9). Elle ne coûte rien aux autres cotisants du
régime général, et la doctrine ne la touche qu'à l'intégration.

### 12. L'AVPF

**La règle.** La branche famille cotise à l'assurance vieillesse du régime
général pour le parent qui interrompt ou réduit son activité, s'il touche
certaines prestations familiales sous condition de ressources, ou s'il a la
charge d'un enfant ou d'un adulte handicapé, sur une assiette de 169 heures
du SMIC par mois, 2 031,38 € en 2026 (L. 381-1 CSS ; fiche `avpf.yaml` ;
dépôt). La mère seule jusqu'en 1984, l'un ou l'autre parent depuis 1985.

**Les quatre questions.** *Subi* : en partie ; l'arrêt est un choix, mais la
condition de ressources le réserve aux ménages modestes. *Constaté* : oui,
par la CAF. *Qui paie* : la branche famille, 5,10 Md€ de cotisations en 2024
(dépôt, `macro/transferts_retraite.csv`, l. 104 ; 6,04 selon le COR).
*Forfaitaire* : oui, l'assiette est la même pour tous.

**Coût.** 4,39 Md€ de pensions servies en 2024 (publié).

**Qui en profite.** À 96 % des femmes ; 85 à 90 % des mères qui l'ont sont
dans les cinq premiers déciles (publié, COR, octobre 2023, doc. 9).

**Le droit.** Stock : reprise très élevée (inféré : un droit pour lequel un
tiers a cotisé est un bien, au sens de la Convention, plus encore qu'un
trimestre gratuit). Avenir : suppression faible.

**Ce qu'elle dit de la proposition.** L'AVPF est déjà, à la lettre, la règle
du programme : un assureur extérieur verse la cotisation au compte. La
proposition la retire pourtant, aux retraités comme aux carrières à venir,
parce que le modèle retire la recette avec le droit
(`src/retraite_notionnelle/cout.py`, l. 82-85) : c'est contraire à la
décision 27, les droits suivent l'argent.

**Options.**

| Option | Stock | Avenir | Qui paie |
|---|---|---|---|
| Reprise, retirée pour l'avenir (la proposition) | +0,048 → +0,034 | +0,137 → +0,108 ; la branche famille garde 0,174 de cotisations | les parents au foyer |
| Gardée, pour le stock et pour l'avenir | 0 | 0 ; les régimes y gagnent 0,036, la cotisation dépassant la pension | la branche famille, comme aujourd'hui |

**Proposition.** La garder, pour le stock et pour l'avenir, comme une
cotisation : ses années comptent au compte comme des années payées. C'est le
seul droit familial qui remplit déjà les quatre critères.

### 13. La surcote parentale

**La règle.** 1,25 % par trimestre cotisé dans l'année qui précède l'âge légal
et au-delà de la durée requise, quatre au plus, à qui détient un trimestre de
MDA, dès que l'âge légal atteint 63 ans (L. 351-1-2-1 CSS, loi n° 2023-270 ;
fiche `surcote_parentale.yaml`) : la génération 1965 née après mars et les
suivantes. Elle compense le recul de l'âge légal de 2023.

**Les quatre questions.** *Subi* : non. *Constaté* : par la MDA, donc l'état
civil. *Qui paie* : les régimes. *Forfaitaire* : non, un pourcentage de la
pension.

**Coût.** Rien avant 2027 ; 0,3 % des droits directs en 2070 (publié, COR),
environ 0,03 point en moyenne (à côté, ordre de grandeur).

**Qui en profite.** Surtout des mères, mais à carrière longue, qui ont leur
durée avant l'âge légal : pas les plus petites pensions.

**Le droit.** Rien à reprendre au stock : au modèle, la bascule de 2026
précède ses premières pensions. Suppression pour l'avenir : faible.

**Proposition.** Sans objet pour l'avenir : le compte n'a ni âge légal ni
durée requise, et chaque année travaillée y relève la pension au prix juste.
Dans la réalité, si la bascule venait après 2027, les pensions liquidées
entre-temps suivraient la baisse.

### 14. Le salaire de référence des parents

**La règle.** Les vingt-quatre meilleures années pour qui a une majoration
ou une bonification au titre d'un enfant, vingt-trois pour deux et plus, aux
pensions depuis le 1er septembre 2026 (R. 173-3-2, I, CSS, décret
n° 2026-699 ; fiche `sam_parents_24_23.yaml`, qui cite l'article 103 de la
loi n° 2025-1403, quand le décret viserait le 104 : à la session des
données). La Cnav l'appliquera courant 2027, avec un rappel.

**Les quatre questions.** *Subi* : non. *Constaté* : l'état civil. *Qui
paie* : les régimes. *Forfaitaire* : non ; elle relève le salaire de
référence de 1 à 2 % (dépôt).

**Coût.** 0,2 Md€ en 2030, 2,2 en 2050 (presse, à vérifier) ; environ
0,03 point en moyenne (à côté, ordre de grandeur). Le retrait vaut 729 € par
an à la carrière interrompue de la génération 1985 (dépôt).

**Proposition.** Sans objet pour l'avenir : le compte retient toutes les
années, il n'a pas de meilleures années. Rien au stock au modèle ; dans la
réalité, ce que les pensions liquidées avant la bascule en ont reçu suit la
baisse.

### 15. Les trimestres d'enfants réputés cotisés

**La règle.** Deux trimestres au plus de MDA ou de bonification réputés
cotisés pour la carrière longue, aux pensions depuis le 1er septembre 2026
(L. 351-1-1, 3°, CSS et D. 351-1-2-1 ; L. 25 bis, 4°, et D. 16-2 CPCMR ; loi
n° 2025-1403, article 104 ; fiche
`carriere_longue_enfants_reputes_cotises.yaml`) ; et, pour la majoration du
minimum contributif, les trimestres d'AVPF et d'assurance vieillesse des
aidants comptés parmi les 120 trimestres cotisés, 24 au plus, depuis 2023
(fiche `minimum_contributif.yaml`, version `avpf_et_ava_2023`).

**Les quatre questions.** *Subi* : non. *Constaté* : l'état civil, la CAF.
*Qui paie* : les régimes. *Forfaitaire* : non.

**Coût.** Non publié.

**Proposition.** Sans objet pour l'avenir : le compte n'a pas de carrière
longue, que la première répartition du chantier 3, encore à valider, range
parmi les choix de vie retirés pour l'avenir ; et la même répartition
remplace les minima, minimum contributif compris, par la garantie vieillesse,
où la décision 41 (la première des deux qui portent ce numéro) range tous les
planchers propres à une caisse. Au stock, ces trimestres suivent le sort du
départ anticipé et du minimum qu'ils ont ouverts.

### 16. Les départs anticipés des parents de trois enfants

**La règle.** Le fonctionnaire civil ou le militaire qui avait quinze ans de
services avant le 1er janvier 2012 et trois enfants vivants à cette date
garde le droit de partir à tout âge, s'il a interrompu ou réduit son activité
pour chacun, au calcul de l'année où il remplissait ces conditions (loi
n° 2010-1330, article 44 ; L. 24, I, 3°, CPCMR ; CNRACL et FSPOEIE de même ;
fiche `depart_anticipe_parents_trois_enfants.yaml`, l. 186-205). Fermé aux
nouveaux droits depuis 2012.

**Les quatre questions.** *Subi* : non. *Constaté* : oui. *Qui paie* :
l'État employeur et la CNRACL. *Forfaitaire* : non ; c'est un âge, et un
barème d'avant les réformes.

**Coût.** 1,19 Md€ en 2024 (publié).

**Qui en profite.** À 98 % des femmes.

**Le droit.** *Leone* y voit une discrimination indirecte sauf
justification ; *Quintanel* la juge justifiée, pour compenser les retards de
carrière des mères. Reprise sur le stock : très élevée — c'est la population
la plus féminine de toutes, et le recalcul actuariel d'un départ à cinquante
ans en réduirait fortement la pension. Pour l'avenir, les ayants droit qui
ne sont pas encore partis le perdraient près de leur départ : moyen.

**Options.** Stock : reprise +0,020 → +0,014 ; gardés, 0. Avenir : fermés à la
bascule, le reste du flux est faible (non chiffré).

**Proposition.** Garder les pensions servies jusqu'à extinction, à la charge
de l'employeur public qui a accordé le départ ; pour l'avenir, fermer à la
bascule : le compte ouvre la pension à tout âge, au prix juste, et l'ayant
droit qui part après la bascule n'y perd que le barème ancien.

### 17. Les majorations de la réversion pour enfants

**La règle.** *17a* : un forfait par enfant à charge, ajouté à la réversion
du survivant qui n'a pas de retraite personnelle et n'a pas l'âge du taux
plein, réduit comme la réversion, servi par le régime de la dernière
affiliation : 1 363,08 € par an et par enfant en 2026 (L. 353-5, R. 353-10,
R. 353-11, D. 353-2 CSS ; fiche `majoration_forfaitaire_reversion.yaml`).
*17b* : la réversion du survivant parent de trois enfants majorée de 10 % de
son montant non majoré au régime général (circulaire Cnav n° 2022-26,
§ 3.6), de la moitié de la majoration du défunt dans la fonction publique,
de la majoration reversée à l'Agirc-Arrco (fiches `reversion.yaml`,
`reversion_fonction_publique.yaml`, `reversion_agirc_arrco.yaml`).

**Les quatre questions.** *17a* : *subi*, oui, le décès ; *constaté*, oui ;
*qui paie*, les régimes ; *forfaitaire*, oui. *17b* : la majoration de 10 %
reportée sur la réversion, mêmes réponses qu'au n° 9.

**Coût.** Non isolé : compris dans les majorations des pensions de réversion
(dépôt). 17a est étroit : de jeunes survivants sans pension, qui élèvent
encore leurs enfants.

**Au regard des décisions 16 à 28.** Les réversions servies sont gardées
jusqu'à extinction (décision 16) : leurs majorations, servies avec elles,
aussi. Pour les décès à venir, la rente sur deux têtes au prix du couple
(décisions 17 à 21) sert 50 % de ce que la pension contient : 17b n'a plus
d'objet si la majoration elle-même est retirée (n° 9). Le décès d'un actif
verse la moitié de son compte au conjoint, tout de suite s'il a des enfants
à charge (décisions 22 et 25) : 17a s'y ajouterait.

**Proposition.** Le stock, avec la réversion (décision 16). Pour l'avenir,
17a reste, comme un droit d'accident, mais payé par la branche famille, qui
sert déjà l'allocation de soutien familial aux enfants orphelins d'un parent
(à vérifier : son montant et son cumul) ; 17b suit le n° 9.

## Ce que coûteraient les propositions, toutes ensemble

Si chaque proposition était retenue (à côté, moyenne 2026-2070, face au droit
actuel) :

- *Le stock* : la majoration suit la baisse, +0,118 brut, +0,108 net ; le
  reste est gardé jusqu'à extinction — c'est le stock S3 de l'étude, que le
  propriétaire n'a pas retenu comme règle d'ensemble, retrouvé ici dispositif
  par dispositif.
- *L'avenir* : les régimes ne paient plus aucun droit familial, +0,54 brut
  (majoration 0,234, MDA, bonifications, surcote et salaire de référence
  0,310) ; l'AVPF reste, 0 ; les crédits de maternité et d'éducation, une
  année chacun sur l'assiette de l'AVPF, coûtent 0,18 aux payeurs. Solde :
  +0,36 brut.
- *Ensemble* : environ +0,48 brut, la moitié de l'économie de la proposition
  (+0,98), pour un risque juridique faible sur l'avenir et moyen sur le stock.
- *La branche famille* verse aujourd'hui 0,37 point à la retraite (AVPF et
  majorations). L'AVPF (0,17) et les deux crédits (0,18) lui coûteraient
  0,35 point : elle paierait le crédit de maternité aussi, si on le lui
  confiait, avec ce qu'elle verse déjà. Le net n'est pas calculé.

## Les questions au propriétaire

Posées dispositif par dispositif, quatre au plus à la fois ; chacune se
suffit à elle-même. Pour chaque dispositif : le stock (repris avec la baisse,
ou gardé jusqu'à extinction) et l'avenir (rien, un crédit ou un forfait payé
par un tiers, ou la règle de la caisse) ; puis, pour ceux qui sont gardés en
argent, le montant et le parent faute d'accord.

## Ce que le propriétaire a répondu

Le 7 novembre 2026, il choisit le travail en série, avec l'éclaireur pour les
recherches dans le dépôt, sans recherche en parallèle. Puis, aux questions
posées dispositif par dispositif — chacune disait le coût, le payeur, qui en
profite et le risque juridique —, il ne suit pas les propositions : l'argent
des droits familiaux va aux parents d'aujourd'hui, non aux retraités.

- *La MDA de maternité* : « Il me semble que j'avais dit il y a longtemps que
  la moitié de ses dépenses devaient aller aux mères qui avaient un enfant
  aujourd'hui et non aux retraités, et l'autre moitié pour baisser le
  déficit. Tu peux vérifier ? Les mères qui ont un enfant maintenant en ont
  plus besoin que les mères qui ont accouché depuis des années et qui sont à
  la retraite aujourd'hui. » **Vérifié : le dépôt n'en garde aucune trace.**
  L'éclaireur a cherché les archives, la feuille de route, ses notes, le
  programme et l'historique git : le plus proche est l'action 59 du
  20 septembre 2026, qui partage les impôts que la proposition n'encaisse
  plus — « la moitié est rendue aux salaires, la moitié éteint de la dette »
  (`docs/archives/feuille_de_route.md`, l. 10007-10009) —, et la décision
  29, qui partage la baisse des pensions entre le déficit et les cotisants ;
  ni l'une ni l'autre ne parle d'enfants. Le propriétaire répond : « j'ai
  pris la décision en septembre je pense ». Elle s'écrit donc comme la
  décision 50, au 7 novembre, et vaut, à sa demande, « À tous les droits
  retirés ».
- *La forme de la part des parents* : « Une prestation en argent », versée
  maintenant, hors de la retraite ; sa forme, son montant et ses conditions,
  « À étudier aux sources » (décision 51).
- *La MDA d'éducation* : « C'est un choix familial et cet argent serait mieux
  utilisé à être directement aux parents qui éduquent leurs enfants
  aujourd'hui plutôt qu'aux retraités. On a besoin de l'argent pour les
  besoins d'aujourd'hui et pas pour les besoins passés. » (décision 52, avec
  la maternité).
- *L'adoption, le congé parental, les bonifications et majorations de durée
  des fonctionnaires, les trimestres des régimes spéciaux* : « Oui, la même
  règle » (décision 53). La question disait le risque d'une reprise, très
  élevé pour la bonification que le Conseil d'État a jugée justifiée en 2015.
- *La majoration de 10 %* : « on en a pas besoin, c'est une mesure populiste
  qui prive d'argent les parents d'aujourd'hui » ; celle des fonctionnaires
  et des régimes spéciaux, « Comme le régime général » (décision 54) ; celle
  des complémentaires, « Sa caisse, puis le régime général » (décision 55) ;
  celle qui s'ajoute aux réversions servies, posée d'abord trop
  abstraitement (« la question n'est pas assez claire »), puis par l'exemple
  d'une veuve qui touche 600 € de réversion et 60 € de majoration :
  « Retirés comme sur les pensions » (décision 56).
- *L'AVPF* : « Gardée partout » (décision 57).
- *La MDA d'enfant handicapé* : « on fait les deux. on garde payée par un
  tiers et on donne de l'argent aux parents d'enfants handicapés. on sort un
  peu du programme retraite mais j'aimerais qu'on sauvegarde cette
  décision » (décision 58).
- *Les départs anticipés des parents de trois enfants* : « Suivent la baisse,
  fermés » (décision 59), le risque très élevé ayant été dit.
- *La surcote parentale, le salaire de référence des parents, les trimestres
  réputés cotisés* : « Supprimées, la règle du partage » (décision 60).
- *La majoration forfaitaire de réversion pour enfant à charge* : « Gardée,
  payée par la famille » (décision 61).

**Ce que cela coûte** (à côté, moyenne 2026-2070, face au droit actuel, par
la répartition de « Comment lire les fiches »). Retirer tout sauf l'AVPF :
au stock, la MDA et les bonifications, la majoration et les départs,
+0,247 brut, +0,199 net ; pour l'avenir, la majoration, la MDA, les
bonifications, la surcote et le salaire de référence, +0,544 brut, environ
+0,46 net. Ensemble, environ +0,79 brut et +0,66 net, contre +0,98 et +0,80
pour la proposition : l'écart est l'AVPF gardée, 0,185 brut. La majoration
retirée des réversions servies ajoute une économie non chiffrée ; la MDA
d'enfant handicapé et la majoration forfaitaire de réversion, gardées, des
coûts faibles, non chiffrés.

**La moitié aux parents** : si la base est l'économie brute, environ
0,40 point de PIB par an en moyenne ; environ 2,7 Md€ en 2026, le stock
baissant par cinquièmes (décision 3), 17 Md€ en 2040, 37 Md€ en 2070, en
euros courants (à côté, AVPF ôtée au prorata de l'étude). C'est, pour
650 000 naissances, de l'ordre de 4 000 € par naissance la première année et
de 26 000 € en 2040. Le déficit reçoit alors l'économie nette moins cette
part, environ 0,26 point, la garantie rendant 0,13 aux parents retraités
passés sous le plancher ; si la base est l'économie nette, 0,33 chacun. La
base, et le lien avec le partage de la décision 29 (lecture A ou B), restent
au propriétaire.

## Ce qui reste à faire

- À étudier aux sources, dans une étape à part : la prestation en argent aux
  parents d'aujourd'hui (décision 51) — prime à la naissance, allocation pour
  les jeunes enfants, pour tous ou sous conditions de ressources, à la mère
  pour la part de maternité —, son payeur (la branche famille), et ce que la
  branche famille sert déjà (prime de naissance, allocation de base) ; celle
  des parents d'enfants handicapés (décision 58), face à l'AEEH ; le payeur du
  crédit d'enfant handicapé.
- Au propriétaire : la base du partage (brute ou nette) et son lien avec la
  décision 29.
- Au modèle, au seul scénario 6 (décision 28) : retirer, au stock par la
  baisse et pour l'avenir, tous les droits familiaux sauf ceux des décisions
  55, 57, 58 et 61 ; compter l'AVPF au compte comme une cotisation, que la
  branche famille continue de verser ; servir le crédit d'enfant handicapé
  et la majoration forfaitaire de réversion à la charge de leur payeur ;
  retirer des réversions servies leur majoration de 10 % (décision 56) ;
  verser la moitié de l'économie à la prestation, hors des pensions, et
  l'autre au solde ; régler ce que la branche famille verse à la retraite,
  que le chantier 4 compte parmi « les versements de l'État et de la branche
  famille ». Le modèle ne sait pas chiffrer les droits familiaux de la
  population : un seul cas type a des enfants (étude).
- Aux données, sans rien en corriger ici : les deux écarts de l'étude (le
  champ du poste de la majoration dans
  `macro/prestations_non_contributives.csv`, l'article 103 au lieu du 104
  dans `sam_parents_24_23.yaml`) ; et l'écart entre le gain de la
  bonification publié au jaune et les 1,82 Md€ du COR (n° 6).
- À vérifier aux sources : le partage de la MDA entre maternité et éducation ;
  le nombre de pères qui ont l'éducation ; les adoptions par an ; les
  conditions de l'AVPF pendant un congé parental ; la branche qui paie
  l'AEEH ; l'allocation de soutien familial des orphelins d'un parent.
- À la veille : l'article 34 du projet de loi de financement pour 2027 (n° 9).
