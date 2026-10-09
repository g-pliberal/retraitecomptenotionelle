# 3. Le scénario « système actuel » est une approximation

Reproduire exactement le droit positif de tous les régimes depuis 1930 suppose
un moteur législatif complet, du type de ceux de la DREES (TRAJECTOiRE) ou de
l'Institut des politiques publiques (PENSIPP). Écarts connus :

- **régimes en points** — la pension est calculée en points, sur l'historique
  réel des valeurs d'achat et de service (Agirc depuis 1947, Arrco depuis 1949,
  Ircantec depuis 1949), avec conversion des points aux fusions. S'y ajoutent
  depuis peu deux régimes dont le barème n'est pas un prix d'achat mais un
  NOMBRE DE POINTS par tranche d'assiette : le régime de base des professions
  libérales (<!--chiffre:valeur(data/reference/regimes/cnavpl.yaml:periodes.debut=2015;assiette=plafonnee.points_maximum)-->525<!--/--> points au plafond jusqu'en 2024, <!--chiffre:valeur(data/reference/regimes/cnavpl.yaml:periodes.debut=2025.points_maximum)-->557<!--/--> depuis 2025, <!--chiffre:valeur(data/reference/regimes/cnavpl.yaml:periodes.debut=2024;assiette=plafonnee_5_pass.points_maximum)-->25<!--/--> sur la
  seconde tranche) et la complémentaire agricole (<!--chiffre:valeur(data/reference/regimes/msa_rco.yaml:periodes.debut=2003.points_maximum)-->100<!--/--> points pour <!--chiffre:valeur(data/reference/regimes/msa_rco.yaml:periodes.debut=2003.assiette_repere_smic)-->2 028<!--/--> SMIC).
  Le même régime de base en connaît une troisième forme pour ce qui précède
  2004 : <!--chiffre:valeur(data/reference/regimes/cnavpl.yaml:periodes.debut=1949.points_par_trimestre_valide)-->100<!--/--> POINTS PAR TRIMESTRE VALIDÉ, sans égard au montant cotisé. La complémentaire des
  avocats les a rejoints, avec le prix d'achat publié par la CNBF et les cinq
  tranches en euros de la classe C1, depuis 2019 seulement — les tranches
  antérieures ne sont pas publiées. Restent au rendement instantané, faute
  d'une série de prix d'achat, les complémentaires des sections libérales et de
  l'IRCEC, quelques petits régimes — CAFAT, tranche B de la Polynésie,
  additionnel des enseignants du privé, gérants de débits de tabac, conjoints du
  bâtiment —, et les années postérieures au dernier barème publié de
  l'Agirc-Arrco, de l'Ircantec, du RCI et de la complémentaire des avocats. Le
  RAFP, lui, a sa série ;
- **montée en charge des réformes** — le modèle a trois horloges, comme le
  droit. Ce qui s'ACQUIERT est lu à l'année travaillée : taux de cotisation,
  assiette et ses bornes, plafond de la Sécurité sociale, prix d'achat du point,
  heures de SMIC pour valider un trimestre. Ce qui commande la MONTÉE EN CHARGE
  est lu à la génération : durée requise, âge d'ouverture, âge d'annulation de
  la décote, coefficient de minoration et nombre d'années retenues au salaire de
  référence — quatre de ces cinq tables sont lues dans le texte même des
  articles du code, et recontrôlées à chaque exécution. Ce qui LIQUIDE est lu à l'année
  de liquidation : formule du régime, valeur de service du point, décote de la
  fonction publique et barème du minimum garanti, comme leurs articles
  l'écrivent. Reste approchée la montée en charge propre à chaque régime
  spécial ;
- **avantages datés** — la fiche de chaque période dit ce que le régime
  accordait cette année-là, et le moteur ne sert que cela : ni minimum
  contributif avant 1983, ni surcote avant 2004, ni trimestres pour enfants
  avant 1972. Restent hors du modèle les avantages familiaux des régimes que
  leur fiche ne déclare pas, faute de barème sourcé : le régime de base des
  professions libérales, celui des avocats, et celui des exploitants
  agricoles. La SURCOTE de l'Ircantec, elle, en est sortie : le IV de
  l'article 16 de l'arrêté du 30 décembre 1970 est servi depuis le
  1er janvier 2010, à ses deux taux — <!--chiffre:mesure(constante?de=retraite_notionnelle.droit.liquider&nom=_SURCOTE_IRCANTEC_AGE&echelle=100)-->0,75<!--/--> % par trimestre entier écoulé
  au-delà de l'âge du taux plein, <!--chiffre:mesure(constante?de=retraite_notionnelle.droit.liquider&nom=_SURCOTE_IRCANTEC_DUREE&echelle=100)-->0,625<!--/--> % par trimestre cotisé au-delà de la
  durée requise en deçà de cet âge —, et le coefficient d'un régime en points
  peut désormais dépasser un, des deux côtés du portage. Les neuf autres
  régimes en points dont la fiche écrit une surcote la servent aussi depuis
  l'action 22, chacun à sa règle, lue dans son texte : la CNAVPL et la MSA des
  non-salariés à celle du régime général — trimestres cotisés au-delà de l'âge
  légal et de la durée requise, R. 643-8 et D. 732-42 —, les sept
  complémentaires de sections libérales À L'ÂGE SEUL, en trimestres civils
  entiers écoulés depuis l'âge que leurs statuts nomment — soixante-deux ans à
  la CARMF et à l'ASV, soixante-cinq à la CAVEC, l'âge du taux plein à la
  CARPIMKO, à la CAVP, à la CPRN et à la CIPAV —, et bornés comme ils le
  sont : soixante-dix ans chez les médecins et, jusqu'en 2023, les notaires,
  vingt trimestres à la CAVEC et à la CARPIMKO, douze à la CAVP, années
  pleines seulement à la CIPAV et à la CARMF d'avant 2017. Rien n'est servi
  avant le texte qui date chaque règle, et les taux que les fiches
  reportaient en arrière sans texte — <!--chiffre:illustration()-->0,75<!--/--> % à la CARPIMKO, <!--chiffre:illustration()-->1<!--/--> % à la CPRN —
  sont ceux des arrêtés. Ce que la fiche ne porte pas est dit dans ses
  notes : la CIPAV ne majore que les points des trente premières années, la
  CAVP borne les générations 1951 à 1955 à un ou deux ans, la CNAVPL sert
  <!--chiffre:valeur(data/reference/regimes/cnavpl.yaml:periodes.debut=2024;assiette=plafonnee.surcote_par_trimestre*100)-->1,25<!--/--> % aux liquidations de 2024 et non aux trimestres accomplis depuis
  septembre 2023, la MSA ramène à <!--chiffre:valeur(data/reference/regimes/msa_non_salaries.yaml:periodes.debut=2004.surcote_par_trimestre*100)-->0,75<!--/--> % l'escalier de <!--chiffre:illustration()-->3<!--/-->, <!--chiffre:illustration()-->4<!--/--> et <!--chiffre:illustration()-->5<!--/--> % d'avant
  2009 ;
- **revalorisation des salaires portés au compte** — le modèle ne les
  reconstitue plus, il les LIT dans la circulaire annuelle de la Cnav
  (`legislation/revalorisation_salaires.csv`, perceptions 1930-2025). Il les
  approchait par « les salaires jusqu'en 1986, les prix depuis » ; cette
  approximation sur-revalorise les salaires anciens.
  Dix colonnes publiées sont dans le dépôt ; hors d'elles, le coefficient est
  ancré sur la plus proche, et l'approximation ne reprend toute la main
  qu'avant 1930, où elle joue À LA HAUSSE ;
- **départs anticipés** — la carrière longue est modélisée, et sert à dire si le
  droit ouvre la liquidation demandée ; l'inaptitude, l'invalidité et le
  handicap aussi, au régime général, dans les régimes alignés et dans la
  fonction publique, à qui les déclare. La pénibilité ne l'est pas : elle
  demande des informations professionnelles que le modèle ne collecte pas ;
- **polypensionnés** — chaque régime liquide sur ses seules années, à sa
  date, et la durée acquise dans chacun est comptée séparément ; mais un
  régime et celui qui lui succède ne sont pas deux régimes, et liquident
  ensemble (voir « Les régimes alignés » ci-dessous). La liquidation unique des régimes alignés
  DISTINCTS (LURA) et sa proratisation croisée du salaire annuel moyen sont
  servies depuis le 22 septembre 2026 ; seule en reste dehors sa troisième
  condition, la retraite de même nature déjà obtenue avant le 1er juillet
  2017 (voir « Ce qui reste hors du modèle »).

Un écart de quelques pour cent avec la pension réelle est attendu.

## Ce que dit la confrontation à une seconde implémentation

Le scénario 1 est l'étalon : tous les écarts affichés se mesurent par rapport à
lui, et il n'avait aucune contre-expertise. « Mon estimation retraite », le seul
simulateur officiel qui chiffre une pension entière, exige FranceConnect et le
relevé de carrière réel ; les simulateurs anonymes des caisses ne répondent
qu'une saisie à la fois, dans un budget (§ 3.5 de l'architecture), et leurs
réponses rejoignent les exemples publiés, plus bas. Et relire deux fois le même
code ne prouve rien : une réimplémentation écrite par la même main hérite des
mêmes hypothèses.

**OpenFisca-France-Pension** comble ce trou. Ce n'est pas une source officielle,
c'est un autre MODÈLE — le module « retraites » de l'écosystème OpenFisca — mais
il est écrit par d'autres à partir des mêmes textes.
`scripts/fetch/openfisca_regime_general.py` y calcule dix profils à salaire
nominal constant et fige le relevé dans `tests/temoins/`, que `tests/test_oracle.py`
rejoue sans avoir à installer le paquet.

**Cinq familles de régimes y passent aujourd'hui**, et c'est tout ce
qu'OpenFisca expose : le régime général, la pension civile (État et CNRACL),
l'Arrco d'avant 2019, l'Agirc des cadres et l'Ircantec des agents non
titulaires — <!--chiffre:mesure(profils_oracle)-->48<!--/--> profils en tout. Les régimes alignés — MSA des
salariés agricoles, artisans, commerçants — n'ont chez lui aucun module, et
n'en ont pas besoin : la loi les calcule comme le régime général, et c'est à
l'oracle du régime général qu'ils se confrontent — à une table près : le
revenu annuel moyen des artisans et des commerçants nés de 1935 à 1952,
partis avant 2026, retient moins d'années que le salaire annuel moyen
(`R. 634-1-1`), et le test leur prête la table du régime général pour les
y opposer. Restent hors de portée le
régime unifié Agirc-Arrco, dont son code lève une exception, et tout ce qui
n'est ni salarié ni fonctionnaire : les régimes spéciaux, les libéraux, les
exploitants agricoles, que personne d'autre ne modélise. Les exploitants sont
le seul trou qui porte plus d'un million d'assurés — 1 023 064 retraités de
droit direct en 2024 —, et il ne se comblera pas par cette voie : leur régime
est MIXTE, une retraite forfaitaire plus une proportionnelle en points, sans
équivalent au régime général auquel l'opposer.

Le résultat, sur dix profils — et les régimes alignés le partagent, puisque
leur pension est, à table égale, celle du régime général :

| Grandeur | Accord |
|---|---|
| Durée d'assurance | **exacte** sur les dix |
| Trimestres de décote | **exacts** sur les dix |
| Taux de liquidation | **exact** sur les dix |
| Coefficient de proratisation | **exact** sur les dix |
| Salaire annuel moyen | jusqu'à <!--chiffre:mesure(ecart_openfisca)-->2,52<!--/--> %, **et c'est OpenFisca qui s'écarte de la source** |
| Pension de base | l'écart du salaire annuel moyen, et rien d'autre |

Le décompte des trimestres de décote est le contrôle le plus exigeant du lot :
il met en jeu la durée requise par génération, l'âge d'annulation par
génération, la règle du minimum entre les deux décomptes, le plafond de vingt
trimestres et l'arrondi à l'entier supérieur. Cinq tables et trois règles
tombent juste ensemble, dix fois.

Le salaire de référence, lui, a divergé — et l'enquête qu'il a déclenchée a
trouvé une erreur de chaque côté, la nôtre d'abord.

Il s'écartait de +0,30 % à +7,55 %, toujours dans le même sens, parce que le
modèle APPROCHAIT les coefficients de revalorisation des salaires portés au
compte : « les salaires jusqu'en 1986, les prix depuis ». Mesurée sur les
coefficients réels, cette approximation sur-revalorise les salaires anciens de
**12,1 % sur 1970-2018** et de **13,6 % sur 1980-2018**. L'erreur comptait
double, parce que la grandeur compte double : le salaire de référence retient
les N MEILLEURES années, et « meilleures » se juge sur des salaires revalorisés
— changer les coefficients ne déplace pas seulement le niveau de chaque année,
cela change lesquelles sont retenues.

Le dépôt a d'abord repris la table cumulée d'OpenFisca, faute d'avoir cherché
plus haut. **C'était une erreur de méthode, et elle a duré un commit.** Une
seconde implémentation est une contre-expertise ; ce n'est pas une source. La
source existe : la Cnav publie chaque année, dans sa circulaire de
revalorisation, la table entière des coefficients qu'elle applique. Confrontée à
celle du 9 janvier 2023, la table d'OpenFisca s'en écarte :

- de **−3 % à −5,5 %** sur toutes les perceptions postérieures à 1990, un
  déficit à peu près uniforme — c'est la revalorisation exceptionnelle de 4 % du
  1<sup>er</sup> juillet 2022 (loi « pouvoir d'achat ») qui lui manque ;
- de **−17 % à +10 %**, sans régularité, sur les années 1949-1962.

Le modèle lit donc la circulaire, et le désaccord résiduel avec OpenFisca —
jusqu'à <!--chiffre:mesure(ecart_openfisca)-->2,52<!--/--> %, toujours dans le même sens — n'est plus le nôtre.

**Le coefficient se lit dans une colonne, par rapport de deux de ses valeurs.**
L'arrêté annuel applique un coefficient unique à tous les salaires déjà portés
au compte, quelle que soit leur année de perception : une colonne suffit donc,
en théorie, à en reconstruire toutes les autres.

En pratique, non — et c'est mesuré. La caisse arrondit sa table publiée à trois
décimales et repart chaque année de la précédente : les arrondis s'accumulent, et
reconstruire une colonne depuis une autre dérive avec la distance. Le tableau
donne l'écart relatif entre une colonne publiée et sa reconstruction, en
médiane sur les années de perception qu'elle porte :

| Colonne de janvier reconstruite | depuis 2026 | depuis la colonne suivante |
|---|---|---|
| 2025 (1 an) | <!--chiffre:mesure(derive_revalorisation?annee=2025&ancre=2026)-->0,012<!--/--> % | <!--chiffre:mesure(derive_revalorisation?annee=2025&ancre=voisine)-->0,012<!--/--> % |
| 2024 (<!--chiffre:illustration()-->2<!--/--> ans) | <!--chiffre:mesure(derive_revalorisation?annee=2024&ancre=2026)-->0,019<!--/--> % | <!--chiffre:mesure(derive_revalorisation?annee=2024&ancre=voisine)-->0,005<!--/--> % |
| 2023 (<!--chiffre:illustration()-->3<!--/--> ans) | <!--chiffre:mesure(derive_revalorisation?annee=2023&ancre=2026)-->0,059<!--/--> % | <!--chiffre:mesure(derive_revalorisation?annee=2023&ancre=voisine)-->0,009<!--/--> % |
| 2022 (<!--chiffre:illustration()-->4<!--/--> ans) | <!--chiffre:mesure(derive_revalorisation?annee=2022&ancre=2026)-->0,096<!--/--> % | <!--chiffre:mesure(derive_revalorisation?annee=2022&ancre=voisine)-->0,028<!--/--> % |
| 2021 (<!--chiffre:illustration()-->5<!--/--> ans) | <!--chiffre:mesure(derive_revalorisation?annee=2021&ancre=2026)-->0,127<!--/--> % | <!--chiffre:mesure(derive_revalorisation?annee=2021&ancre=voisine)-->0,005<!--/--> % |
| 2020 (<!--chiffre:illustration()-->6<!--/--> ans) | <!--chiffre:mesure(derive_revalorisation?annee=2020&ancre=2026)-->0,130<!--/--> % | <!--chiffre:mesure(derive_revalorisation?annee=2020&ancre=voisine)-->0,006<!--/--> % |
| 2019 (<!--chiffre:illustration()-->7<!--/--> ans) | <!--chiffre:mesure(derive_revalorisation?annee=2019&ancre=2026)-->0,135<!--/--> % | <!--chiffre:mesure(derive_revalorisation?annee=2019&ancre=voisine)-->0,007<!--/--> % |

Le dépôt n'a d'abord gardé que la colonne la plus récente, en annonçant 0,13 %
sur la foi d'un seul recoupement.

**Le dépôt porte maintenant <!--chiffre:distinctes(data/reference/legislation/revalorisation_salaires.csv:date_effet)-->10<!--/--> colonnes**, de 2017 à 2026 : le modèle sert
la colonne publiée quand elle existe — l'écart est alors nul, pas petit — et
ancre sinon sur la plus proche. Ce que cela gagne dépend de ce qu'on mesure. En
médiane, la reconstruction de la colonne la plus éloignée tombe de
<!--chiffre:mesure(derive_revalorisation?annee=2019&ancre=2026)-->0,135<!--/--> à <!--chiffre:mesure(derive_revalorisation?annee=2019&ancre=voisine)-->0,007<!--/--> %. Au pire, toutes colonnes et toutes années de perception
confondues, elle ne tombe que de <!--chiffre:mesure(derive_revalorisation?ancre=recente&stat=max)-->0,26<!--/--> à <!--chiffre:mesure(derive_revalorisation?ancre=voisine&stat=max)-->0,12<!--/--> %, et c'est ce pire que
`test_la_reconstruction_entre_colonnes_reste_dans_sa_derive` tient sous
<!--chiffre:tenu(test_la_reconstruction_entre_colonnes_reste_dans_sa_derive)-->0,2<!--/--> %. Le récupérateur recoupe chaque colonne contre chacune des autres
à chaque exécution et refuse d'écrire si l'une s'écarte, et deux tests rejouent
les colonnes figées dans `tests/temoins/`.

Ce document a un temps affirmé qu'« aucune formule ne reproduit les arrêtés,
une série d'ancrages fuit de 20 % ». Cette mesure portait sur la table
d'OpenFisca : ce sont ses incohérences qu'elle mesurait, pas celles du droit.

Ce que cela ne referme pas, et les trois bornes sont différentes.

- **Avant octobre 2017**, la caisse publie aussi ses colonnes :
  <!--chiffre:distinctes(data/reference/legislation/revalorisation_salaires_anciennes.csv:date_effet)-->88<!--/-->
  dates d'effet, de l'arrêté du 14 mai 1946 à la colonne d'octobre 2015, sur la
  page de ses coefficients d'avant avril 2013 et dans ses barèmes d'avril 2013
  et d'octobre 2015 (`revalorisation_salaires_anciennes.csv`). Le modèle sert à
  toute liquidation de ces années la colonne **en vigueur à sa date d'effet**,
  telle quelle, sans rapport de deux valeurs : avant 1952, l'arrêté fixait un
  coefficient par année de perception, et jusqu'en 1993 la revalorisation de
  janvier ne touchait pas encore le salaire de l'année tout juste close —
  aucune colonne ne s'y reconstruit depuis une autre. Restent les salaires
  d'avant 1947, que ces colonnes ne portent qu'en cotisations, revalorisés par
  le rapport de la colonne récente la plus proche ; et deux cellules de la
  colonne de juillet 1990, qui s'écartent de la chaîne des autres, gardées
  telles que la caisse les publie.
- **Après 2026**, le coefficient est ancré sur la dernière colonne et
  l'approximation ne couvre que les dernières années ; avant 1930, il n'y a rien
  sur quoi ancrer et elle reprend toute la main, à la hausse.
- **Le mois existe désormais, et il désigne la colonne applicable.** Le modèle
  retenait l'état au 1<sup>er</sup> janvier : la revalorisation s'étant
  appliquée au 1<sup>er</sup> avril de 2009 à 2013, puis au 1<sup>er</sup>
  octobre jusqu'en 2017, une liquidation de cette période était lue avant la
  revalorisation de son année — **0,52 % en médiane, 0,93 % au maximum**,
  toujours à la baisse. Le cas le plus lourd n'était pas celui-là : la
  **revalorisation exceptionnelle du 1<sup>er</sup> juillet 2022** dépasse celle
  du 1<sup>er</sup> janvier de **3,9 %**, et toutes les liquidations du second
  semestre 2022 lisaient la colonne de janvier. La colonne retenue est
  maintenant la plus récente dont la date d'effet n'est pas postérieure à la
  liquidation, ce que le mois suffit à trancher. Ce qui reste : les années
  qu'aucune circulaire ne couvre, où le modèle passe par la colonne la plus
  proche et son rapport de deux valeurs — le mois n'y change rien, faute de
  colonne à désigner.

Les régimes qui liquident sur le dernier traitement ou les six derniers mois ne
portent aucun salaire à un compte : les coefficients de la Cnav ne leur sont pas
appliqués.

Trois désaccords sont sortis de la confrontation, **et pas tous du même côté**.
Chez nous : la durée de proratisation, confondue avec la durée requise, et les
coefficients de revalorisation, approchés au lieu d'être lus — corrigés tous
deux, et ce sont les paragraphes précédents. Chez lui, deux fois. Sa table de
revalorisation, à laquelle il manque la revalorisation exceptionnelle de juillet
2022 — c'est le paragraphe précédent. Et : une table de durée requise
antérieure à la réforme du 14 avril 2023, qui oppose <!--chiffre:illustration()-->169<!--/--> trimestres à la
génération 1965 là où l'article L. 161-17-3, lu dans la base LEGI, en donne
<!--chiffre:cellule(data/reference/legislation/duree_assurance_requise.csv:trimestres?generation=1965)-->170<!--/--> depuis la suspension de la réforme.
**Un désaccord ne désigne donc pas d'office le coupable.**

Quatre bornes à connaître, et elles sont étroites :

* **le régime unifié Agirc-Arrco est hors de portée.** Son code demande le
  paramètre `agirc_arrco.salaire_de_reference.salaire_reference_en_euros`, que
  les barèmes livrés ne définissent pas — ils portent
  `salaire_reference_prix_achat_valeur_nominale`. Toute liquidation postérieure
  à 2019 y lève une erreur. L'Arrco d'avant, lui, se confronte : voir plus bas ;
* **les liquidations antérieures à 2025.** Ses barèmes s'arrêtent : valeur du
  point Agirc-Arrco en novembre 2024, revalorisations CNAV en 2023. Cinq des
  sept générations de la grille de cas types sont hors de portée ;
* **il rend zéro sans se plaindre.** Sans `simulation.max_spiral_loops`, la
  durée d'assurance, le coefficient de proratisation et la pension valent tous
  zéro, sans qu'aucune exception ne soit levée. Un oracle silencieusement nul
  valide tout : le récupérateur refuse donc d'écrire un profil dont la durée ou
  la pension serait nulle, et le test le revérifie ;
* **et ce même réglage a une borne HAUTE**, découverte en écrivant les oracles
  de l'Agirc et de l'Ircantec. Le total de points d'un régime en points lit le
  total de l'année précédente et remonte ainsi jusqu'à ce que
  `max_spiral_loops` l'arrête. Laissé à cent, il atteint 1947 à l'Agirc, dont
  la formule de points commence au 1<sup>er</sup> janvier quand son prix
  d'achat commence au 1<sup>er</sup> avril, et 1910 à l'Ircantec, dont la
  cotisation lit un plafond de la Sécurité sociale qu'OpenFisca ne définit pas
  avant 1931 : `ParameterNotFoundError` dans les deux cas. Le nombre de
  reprises est donc calculé pour que la remontée s'arrête à la première année
  sûre, et le récupérateur vérifie qu'il couvre encore la carrière. Trop peu de
  reprises tronque la carrière en silence, trop lève une exception : la fenêtre
  est étroite des deux côtés.

**TRAJECTOiRE**, le modèle de la DREES dont un module calcule les cas types du
COR, s'exécute à part, sa licence à réciprocité (EUPL) le tenant hors du dépôt :
`scripts/fetch/trajectoire.py` fige ses sorties, sur les cas types du COR et sur
les carrières de Destinie 2, et `tests/test_trajectoire.py` y confronte le
scénario 1 sans R. Il confirme les durées, la carrière longue et le minimum
contributif ; refaits sur ses propres paramètres, ses écarts de salaire annuel
moyen ne sont que sa chaîne de coefficients, et ses écarts de points la
convention des taux d'acquisition, que le propriétaire tranchera. Il a montré au
dépôt une erreur, corrigée le 5 octobre 2026 (action 138, étape 20) : la valeur
de service de l'Agirc-Arrco était celle du 31 décembre de l'année de la
liquidation, quand la caisse sert celle du jour du départ, et la retraite
complémentaire d'un départ antérieur au relèvement de l'année en sortait trop
haute du montant de ce relèvement. Les deux moteurs servent désormais **la
valeur du jour**, datée de 1947 à 2025 dans `regimes/valeurs_service_datees.csv`
(fiche `agirc_arrco_valeur_service`). Restent lues au 31 décembre les valeurs
des régimes en points que ce fichier ne date pas : l'Ircantec, qui relevait la
sienne au 1er avril à partir de 2009 avant de suivre en 2018 la date de
l'article L. 161-23-1, et les autres, à relire. La bonification du cinquième
des super-actifs et la majoration de durée des hospitaliers actifs, qu'il sert,
le dépôt les sert aussi : les durées concordent, et TRAJECTOiRE borne la
bonification à cinq points de taux proratisés, quand la loi la fait entrer aux
services liquidés, sous le pourcentage maximum.

## Ce que disent les exemples publiés par les caisses

OpenFisca est un autre modèle ; les caisses, elles, publient des EXEMPLES —
une carrière de trois lignes dont la réponse est écrite par l'organisme qui
applique la règle. `tests/temoins/exemples_officiels.yaml` en transcrit
<!--chiffre:entrees(tests/temoins/exemples_officiels.yaml:exemples)-->189<!--/-->, chacun avec sa source et sa date de vérification, et
`tests/test_oracle.py` les rejoue : le test construit la carrière — une
affiliation, un salaire constant, le nombre de trimestres de l'exemple, l'âge
d'entrée cherché au mois près — et compare la grandeur que l'exemple nomme.

| Source | Ce qu'elle fait rejouer | Accord |
|---|---|---|
| service-public.gouv.fr, fiches F19666 et F20349 | décote du privé et de la fonction publique, né en 1964, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->159<!--/--> trimestres sur 170 : taux <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->43,125<!--/--> %, réduction de <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->13,75<!--/--> % | **exact** |
| fiches F19643 et F16494 | surcote du privé et de la fonction publique, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->4<!--/--> trimestres civils après l'âge légal : +<!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->5<!--/--> % | **exact**, une fois la période de référence comptée au trimestre civil |
| fiches F21552 et F36464 | taux plein à 170, taux plein à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->67<!--/--> ans avec 158, taux minoré à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->65<!--/--> ans (<!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->45<!--/--> %), proratisation <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->158<!--/-->/170 | **exact** |
| actualité A15703 | minimum contributif 2026 : <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->170<!--/--> trimestres dont 135 cotisés, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->873,53<!--/--> € par mois | **exact** au centime |
| circulaire Cnav 2026-07 | âges légaux et durées de la suspension pour trois dates de naissance, décote d'un né en novembre 1961 (<!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->44,375<!--/--> %) | **exact**, une fois les tables réécrites |
| circulaire Cnav 2026-29 | carrière longue par génération, 1964 à 1971, ouverte à la borne et refusée un trimestre plus tôt | **exact**, une fois la borne lue par génération |
| circulaire Cnav 2018-04 | surcote à un, deux et trois taux (<!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->2,5<!--/--> %, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->4,75<!--/--> %, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->10,25<!--/--> %) ; la réversion d'une pension ramenée au maximum des pensions, la surcote en sus : <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->836,77<!--/--> € par mois en 2012 | **exact**, une fois le barème daté ; au centime pour la réversion, depuis le 9 octobre 2026 |
| fiche F16336 et circulaire carrière Cnav 2017-01, fiche 6.2b | huit trimestres par enfant au régime général — quatre de maternité, quatre d'éducation | **exact** |
| fiche F37311 | bonification de la fonction publique : quatre trimestres par enfant né avant 2004, deux pour ceux nés depuis | **exact** |
| circulaire Cnav 2022-26 | assiette de la majoration pour trois enfants : <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->10<!--/--> % de la retraite telle qu'elle est servie, surcotée, décotée ou pile au taux plein | **exact** |
| ENIM, pages « Le mode de calcul » et « Les conditions d'attribution » | marin : bonification de <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->5<!--/--> % dès deux enfants (R. 14), pension d'ancienneté ouverte à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->50<!--/--> ans pour <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->25<!--/--> ans de services et refusée un trimestre plus tôt (R. 2) | **exact** |
| CARCDSF, CARMF et CAVAMAC, pages et document d'exemples des sections libérales | la mère de deux enfants au taux plein dès <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->65<!--/--> ans à la CARCDSF ; le coefficient de <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->1,15<!--/--> à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->65<!--/--> ans de la CARMF ; à la CAVAMAC, la décote du régime de base au plus favorable de l'âge et de la durée (<!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->5<!--/--> %), sa surcote de <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->7,5<!--/--> % pour six trimestres, et la décote de la complémentaire par l'âge seul (<!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->6,25<!--/--> %) | **exact**, une fois les complémentaires minorées par l'âge seul |
| Cour des comptes, « Les retraites des fonctionnaires de l'État », tableau n° 20 | durée requise des emplois classés, génération par génération : super-active <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->166<!--/--> trimestres pour 1965, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->168<!--/--> jusqu'en août 1971, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->169<!--/--> ensuite ; active <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->168<!--/--> pour 1965 et jusqu'en août 1966 | **exact**, une fois la durée lue à l'année d'ouverture du droit |
| Service des retraites de l'État, pages « La décote » et « La surcote » | la même fonctionnaire née en mars 1962, à l'âge légal avec <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->163<!--/--> trimestres sur <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->169<!--/--> : décote de <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->7,5<!--/--> % ; à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->64<!--/--> ans avec <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->175<!--/--> : surcote de <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->7,5<!--/--> % | **exact**, une fois la pension datée au premier du mois qui suit la cessation, comme la caisse la date |
| Agirc-Arrco, page « La pension de réversion » | la date d'effet de la réversion de huit survivants : le mois qui suit le décès, ou celui qui suit leurs cinquante-cinq ans | **exact** pour cinq, dont le survivant devenu invalide, que l'âge n'arrête pas, depuis le 1er octobre 2026 ; en écart connu pour trois défunts payés par trimestre ou par an, dont la retraite court jusqu'au terme de sa période |
| circulaires Cnav 2024/25, point 6.4, et 2012/27, point 4 | l'ex-invalide né en novembre 1962, dont la retraite commence d'office à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->62<!--/--> ans, le 1er décembre 2024, avant l'âge légal de sa génération ; l'inapte au taux plein avec <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->158<!--/--> trimestres ; l'un et l'autre ne cumulent entièrement qu'à l'âge légal de leur génération avec la durée requise, ou à celui du taux plein automatique | **exact** |
| Service des retraites de l'État, pages « Le minimum garanti » et « Le calcul de la pension » des invalides | le minimum garanti de l'invalidité en quinzièmes, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->7 542,25<!--/--> € par an pour douze ans de services ; la pension portée à la moitié du traitement à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->65<!--/--> % d'invalidité, non à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->55<!--/--> % ; pension et rente ramenées ensemble au traitement | **exact** ; la page partage ce total en comptant le seuil de la rente sur la rente, quand L. 28 le compte sur le traitement, et ce partage ne se compare pas |
| circulaire Cnav 2005/17, § 31 | la réversion réduite au plafond de ressources : <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->530<!--/--> € avant, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->169,06<!--/--> € après, pour <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->1 150<!--/--> € de salaire mensuel | **exact** au centime, la circulaire tronquant le plafond que le modèle arrondit |
| Union Retraite, simulateurs anonymes d'info-retraite : carrière longue et réversion saisis à la main le 1er octobre 2026, complétés par Claude le 4 octobre 2026 avec l'âge légal | l'âge légal des nés en 1968, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->63<!--/--> ans et <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->9<!--/--> mois, et des nés en 1969 et après, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->64<!--/--> ans, avec <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->172<!--/--> trimestres ; les quatre portes de la carrière longue ; la réversion à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->54<!--/--> % au régime général et à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->60<!--/--> % à l'Agirc-Arrco, l'âge de <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->55<!--/--> ans, le mariage de quatre ans de la fonction publique, que l'enfant commun lève à la CNRACL ; la MSA des salariés ; la moitié au RAFP et à l'Ircantec, et à la complémentaire des indépendants le taux de l'Agirc-Arrco ; l'invalidité, qui lève l'âge à l'Agirc-Arrco et non au régime général | **exact**, une fois deux arrondis de la carrière longue corrigés ; en écart connu pour la condition d'âge de l'Agirc-Arrco, que deux enfants à charge lèvent, pour la réversion du RAFP, que le simulateur refuse quand le mariage ne remplit pas la condition de la pension civile, qu'aucun texte du RAFP ne pose, et pour le plafond de ressources, où c'est le simulateur qui se trompe : il n'a pas revalorisé ses seuils depuis 2024, et refuse ce que D. 353-1-1 accorde |
| ERAFP, simulateur de prestation : dix saisies par Claude le 4 octobre 2026 | le coefficient de majoration du RAFP au mois — <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->1,03<!--/--> à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->62<!--/--> ans et 9 mois, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->1,10<!--/--> à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->64<!--/--> ans et 6 mois — et <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->1,81<!--/--> à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->75<!--/--> ans, comme la délibération du 5 février 2015 ; l'âge légal qui ouvre le droit ; le capital au coefficient de conversion de l'âge, la rente dès <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->5 125<!--/--> points, le capital versé en deux fois de 4 900 à 5 124 | **exact** pour huit ; en écart connu pour deux : le simulateur arrondit au centième le coefficient qu'il interpole, ce qu'aucun texte ne dit, et prête à la génération 1958 l'âge légal de <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->64<!--/--> ans |
| ERAFP, prestations-types des rapports annuels 2015 et 2022, page « Calcul et paiement de votre prestation » | le capital de 2015 au barème de conversion de 2005 (<!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->24,62<!--/--> à soixante-deux ans), celui de 2022 au barème de 2021 (<!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->27,11<!--/-->) ; la première fraction de quinze mois de rente, puis de quatre depuis avril 2024 ; le capital versé en une fois quand la retraite de base précède le RAFP de plus de quinze mois ; les rentes de soixante-deux, soixante-quatre et soixante-sept ans | **exact** |
| Union Retraite, simulateur du départ anticipé des assurés handicapés : vingt-quatre saisies par Claude le 4 octobre 2026 ; circulaire Cnav 2026-18 | la durée cotisée en situation de handicap, de <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->60<!--/--> à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->100<!--/--> trimestres sous la durée requise, de <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->55<!--/--> à <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->59<!--/--> ans, et la durée validée de la double condition de 2015 ; les trimestres retranchés en plus aux nés avant 1973, puis la durée d'avant 2023 de ces générations ; le départ ouvert à l'âge saisi et refusé un trimestre plus tôt ; la majoration de la pension, le tiers du rapport arrondi au centième, <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->0,28<!--/--> et <!--chiffre:tenu(test_les_exemples_publies_par_les_caisses_sont_reproduits)-->0,29<!--/-->, écrêtée à la pension entière | **exact** |

**Ce que la confrontation a trouvé, dans l'ordre.** Le premier exemple lu
contredisait les tables certifiées du dépôt : non que le récupérateur se soit
trompé, mais parce que le droit avait changé depuis le dump qu'il avait lu —
la suspension de la réforme est de décembre 2025, ses décrets de mai 2026, et
le dump LEGI du dépôt de juillet 2025. Une table certifiée est certifiée à une
date ; c'est pourquoi les lignes réécrites sont redescendues au niveau
`moyenne` plutôt que de porter un `certifiee` que rien ne soutient plus, et
pourquoi ce niveau remonte jusqu'au résultat affiché à qui est né de 1964 à
1968 — jusqu'à ce que l'action 27, le même jour, fasse relire les articles
réécrits au récupérateur dans l'index LEGI du dépôt, qui porte les
incréments quotidiens de la DILA : toutes les lignes sont redevenues
`certifiee`, sans qu'un chiffre bouge. Puis la surcote : 5 % dans les deux fiches quand le modèle en servait
6,25, parce qu'il comptait le trimestre de l'anniversaire ; et les trois
exemples de 2018, qui ne se rejouent qu'avec le taux de chaque trimestre à sa
date. Puis la carrière longue, dont la borne des vingt ans n'avait jamais été
lue par génération. Le minimum contributif, la décote, la proratisation, le
taux plein sont tombés justes du premier coup — c'est aussi un résultat.

**Six exemples de plus, le 21 septembre 2026, et ce qu'ils ont demandé de
neuf.** Les enfants n'avaient aucun témoin — ni les trimestres qu'ils
accordent, ni la majoration de 10 % —, et pour une raison de forme : aucune
caisse ne publie une carrière entière dont elle donne la durée d'assurance.
Ce qu'elle publie, c'est **le nombre de trimestres ajoutés par enfant**, et
**le taux de la majoration**. Deux grandeurs neuves ont donc été ajoutées au
banc, qui se mesurent l'une et l'autre sans rien recalculer du modèle :
`trimestres_de_majoration_enfants` rejoue LA MÊME carrière sans enfant et
compare les deux durées — l'écart, lui, ne dépend ni de l'âge d'entrée ni de
la durée requise de la génération ; `majoration_enfants_sur_pensions` rapporte
la majoration servie à la somme des pensions de régime. Les six exemples
tombent justes : 16 trimestres pour deux enfants au régime général, 24 pour
trois, 8 pour deux enfants nés avant 2004 dans la fonction publique et 4 pour
deux enfants nés depuis — et 10 % exactement dans les trois cas, sur une
carrière surcotée à 58,125 %, au taux plein, et minorée à 41,25 %.

Ce dernier point est ce que la circulaire 2022-26 tient à dire et que le
modèle aurait pu manquer : « la surcote majore la retraite et fait partie
intégrante de l'avantage de base », si bien que la majoration pour enfants
« est donc calculée sur la base du montant annuel de la retraite, majorée par
la surcote ». Son exemple le chiffre — <!--chiffre:illustration()-->10<!--/--> % × (600 + 22,50) = 62,25 — et
c'est un ordre d'opérations, pas un barème : appliquer les <!--chiffre:illustration()-->10<!--/--> % à la pension
d'AVANT la surcote rendrait <!--chiffre:illustration()-->9,52<!--/--> % de celle d'après, et le témoin le verrait.

**Une circulaire annulée ne certifie plus rien.** Les six témoins de carrière
longue citaient la circulaire Cnav 2026-17 du 12 juin 2026, que la 2026-29 du
4 septembre a annulée et remplacée. Ses âges et ses durées ont été relus ligne
à ligne dans la circulaire en vigueur : aucun n'a bougé — 60 ans et 6 mois et
170 trimestres pour 1964, 60 ans et 9 mois pour 1965, deux ans et six mois
avant l'âge légal de 1966 à 1969 — mais les témoins citent désormais celle qui
fait foi. C'est la même leçon qu'en juillet, d'un cran plus loin : une table
certifiée l'est à une date, et une SOURCE aussi.

**Ce que les exemples ne couvrent pas.** Ils restent courts par construction :
une affiliation, pas de polypension, pas de carrière hachée. Les vingt-quatre
et vingt-trois années des parents et les âges des catégories actives n'ont pas
d'exemple publié que le dépôt ait trouvé : ils sont transcrits du texte, et
attendent le leur. La durée requise des catégories actives a trouvé le sien, et
il ne vient pas d'une caisse : c'est la Cour des comptes qui la publie
génération par génération, et sa table a démenti celle du dépôt. Les trimestres réputés cotisés
de la carrière longue en ont un, maintenant lu — les trois exemples du point
1.2 de la circulaire 2026-29 —, mais il ne se rejoue pas : il arbitre entre
des périodes assimilées de nature différente, maladie, chômage, service
national, invalidité, maternité, que le modèle ne distingue pas dans une
carrière qu'il synthétise. Le rejouer demanderait d'abord de porter ces
natures, ce que l'entrée `carriere_longue_reputes_cotises_autres` du registre
de veille dit toujours.

**Ce que cette source vaut, et ce qu'elle ne vaut pas.** Un exemple de
circulaire est antérieur à la règle qui le suit — ceux de 2018 valent pour le
droit de 2018 — et une fiche de service-public est réécrite sans que son
exemple le soit toujours : chaque désaccord se tranche par le texte, jamais
par l'exemple seul. Mais quand les <!--chiffre:entrees(tests/temoins/exemples_officiels.yaml:exemples)-->189<!--/--> tombent justes ensemble, hors
les écarts connus que chacun déclare, sur une douzaine de sources et autant de
règles, c'est le droit que le modèle applique, et non une
lecture qu'il aurait de lui.

## La pension d'aujourd'hui d'un retraité : ce qui est lu, et ce qui est reconstitué

Le simulateur montre à qui est déjà parti la pension qu'il touche cette année,
et non plus celle de son premier mois ramenée par l'indice des prix. Chaque
régime la revalorise par son texte (`src/retraite_notionnelle/revalorisation.py`,
porté dans `moteur/js/revalorisation.js`). L'écart n'est pas un détail : le
salarié non cadre du cas type, parti en janvier 2012, touche en 2026
<!--chiffre:mesure(aujourd_hui?generation=1950&niveau=0.8)-->−2,9<!--/--> % de
moins que sa pension de départ ramenée par les prix — ce que la page lui
affichait. Le calcul est exact là où un texte donne un coefficient ou une
valeur de point ; ailleurs il est reconstitué, et le dépliant « Votre pension,
de votre départ à aujourd'hui » le dit au retraité concerné.

**Ce qui est lu.** Le régime général et les régimes alignés : chaque date
d'effet depuis 1949, les cinq tranches de 2020 comprises, dans le barème de la
Cnav. Les régimes en points : la valeur de service de l'année, le long des
fusions et des changements d'échelle — le point Arrco d'avant 1999 est converti
à l'échelle de l'année. La fonction publique depuis 2004 : un décret par an
jusqu'en 2008, puis l'article L. 161-23-1. La majoration pour enfants suit,
part par part, le régime qui la porte, et celle des enfants à charge de la
complémentaire cesse à leurs dix-huit ans ; la majoration pour conjoint à
charge, qui ne se revalorise pas, commence aux soixante-cinq ans du conjoint
quand ils tombent avant 2011. Deux contrôles le tiennent : le cas
type, refait à la main coefficient par coefficient
(`tests/test_revalorisation.py`), et les cas types du COR, figure 3.14 du
rapport de juin 2026, dont le non-cadre des quatre générations est retrouvé en
2026 à <!--chiffre:tenu(test_le_pouvoir_d_achat_du_non_cadre_du_cor_est_retrouve)-->0,1<!--/-->
point et, pour la génération 1952, année après année à
<!--chiffre:tenu(test_le_non_cadre_de_1952_se_suit_annee_apres_annee)-->0,3<!--/-->
point.

**Ce qui s'y ajoute.** La majoration exceptionnelle des petites pensions, due
depuis le 1<sup>er</sup> septembre 2023 aux pensions de base du régime général,
des indépendants, des salariés agricoles et des cultes prises avant cette date
au taux plein, quand l'assuré a cotisé la durée du décret tous régimes :
proratisée sur la durée cotisée dans le régime, sous un plafond proratisé sur
sa durée validée que la pension du régime ne dépasse pas avec elle, puis sous
celui du minimum contributif, revalorisée ensuite comme la pension (fiche
`majoration_exceptionnelle_2023`, loi n° 2023-270, article 18, V). L'échéancier
l'inscrit au mois où elle est due ; l'ASPA la compte, la réversion ne la lit
pas. Restent approchées la surcote des autres pensions de base, que la
comparaison tous régimes garde, et la révision par la seconde pension de qui
retravaille ou par une pension modifiée après coup.

**Ce qui est reconstitué.**

- *La péréquation de la fonction publique, avant 2004.* La pension suivait le
  traitement de l'indice auquel elle avait été liquidée. Le modèle suit la
  valeur du point d'indice, et non les tableaux d'assimilation qui relevaient
  aussi les pensions d'un grade réformé : un fonctionnaire parti avant 2004
  dont le corps a été revalorisé depuis touche davantage que ce que la page
  lui montre.
- *Les régimes spéciaux avant 2009.* Leurs pensions suivaient les salaires de
  leurs actifs, qu'aucune série publique ne donne ; la règle du régime général
  en tient lieu, et la fiabilité affichée tombe à « estimée ».
- *Les régimes en points au-delà de leur dernière valeur publiée* — le régime
  de base des libéraux en 2026 — suivent la règle générale, comme ceux dont le
  dépôt ne porte pas la série des valeurs de service, la complémentaire de la
  Cipav par exemple ; la fiabilité affichée le dit.
- *La revalorisation du jour du départ, dans la fonction publique depuis
  2009.* Les décrets de 2004 à 2007 la servaient aux pensions « dont la date
  d'effet est au plus tard » ce jour-là ; aucun texte lu ne le redit sous
  l'article L. 161-23-1, et le modèle prolonge la règle. Un départ au
  1er janvier 2024 reçoit ainsi la revalorisation de ce jour-là.
- *La tranche de 2020 d'une pension de la fonction publique prise le
  1er janvier 2020.* L'article 81 de la loi n° 2019-1446 choisit le
  coefficient sur la retraite totale reçue le mois précédent, nulle ici : le
  modèle sert le coefficient des petites retraites. Aucune circulaire lue ne
  dit comment le service des retraites de l'État l'a appliqué.
- *Ce qui n'est pas une revalorisation* n'est pas servi : la prime
  exceptionnelle de 2015 aux petites retraites, notamment. Et la pension
  d'aujourd'hui est calculée en brut, puis nette aux prélèvements de cette
  année — la CSG du départ n'intervient nulle part.

**Le cadre du COR s'écarte davantage, et la cause n'est pas trouvée.** Le
dépôt le retrouve à
<!--chiffre:tenu(test_le_cadre_du_cor_est_retrouve_a_un_tiers_de_point)-->0,2<!--/-->
point en 2025, et à
<!--chiffre:tenu(test_le_cadre_du_cor_est_retrouve_a_un_tiers_de_point)-->0,4<!--/-->
point en 2026, l'année prévisionnelle du rapport, toujours du côté d'une perte
plus forte. Aucune hypothèse d'inflation ou de revalorisation de novembre ne le
résorbe sans ouvrir l'écart du non-cadre, et les conventions publiées de
l'annexe n'en disent pas davantage.

**Ce qui reste celui du départ.** Le graphique des cumuls de la trajectoire
additionne la pension du premier mois, supposée garder son pouvoir d'achat, et
sa légende le dit. Les systèmes 2 à 4 ne sont pas le droit : leur pension
servie suit la règle que le modèle prête aux comptes notionnels, celle de la
page Coût, et la garantie vieillesse du système 4 se recalcule sur la pension
d'aujourd'hui.
