# Le musée des horreurs de la retraite — les pièces relevées le 4 octobre 2026

Catalogue établi le 4 octobre 2026 pour une page du site qui reste à faire,
l'action 146 de la feuille de route : les cas les plus loufoques, ou les plus
cruels, que le dépôt a croisés dans les retraites françaises, d'hier et
d'aujourd'hui. Cinquante-six pièces, en sept salles, pour faire rire ou
pleurer le visiteur ; la page en garderait une vingtaine.

Chaque pièce a été relevée dans un fichier du dépôt, au commit `714ad0c`, et
relue dans ce fichier, qui porte sa propre lecture datée du texte officiel.
Aucune n'a été relue sur Légifrance pour ce catalogue : la page relira le
droit en vigueur au moment de s'écrire. C'est un récit, et ses chiffres sont
ceux de ce jour. Le propriétaire trie les pièces dans une copie de travail,
un document Claude privé, colonne « Verdict » :
<https://claude.ai/code/artifact/33a7da7f-fed5-4c98-be38-0e07d7b47973>.

L'effet attendu de chaque pièce est noté *rire*, *larmes* ou *rire jaune*.

## Salle des seuils : un jour, une heure, un point de trop

Un jour de naissance, une heure de travail ou un point de retraite suffisent
à faire basculer un droit entier.

| Pièce | Ce qu'on y voit | Effet | Source |
|---|---|---|---|
| **600 heures valent une année** | Un trimestre ne s'acquiert pas au temps passé mais au montant : 150 heures payées au SMIC, quatre trimestres au plus par an. 600 heures au SMIC valident autant de trimestres qu'un salaire de PDG ; 149 heures dans l'année n'en valident aucun. | rire jaune | décret n° 2014-349, 200 heures avant 2014 ; `data/reference/legislation/validation_trimestres.csv` |
| **Né un jour trop tard** | Pour un enfant né le 31 décembre 2003, une fonctionnaire peut obtenir un an de bonification, si elle a interrompu son activité. Né le 1er janvier 2004, il ne lui vaut que deux trimestres de durée. Au régime général, chaque enfant vaut huit trimestres. | larmes | L. 12 b et L. 12 bis CPCMR, loi n° 2003-775 ; fiche F16336 ; `data/reference/legislation/frontiere_contributive.yaml`, `tests/temoins/exemples_officiels.yaml` |
| **Mort un jour trop tôt, ou trop tard** | Le conjoint d'un assuré mort avant le 1er janvier 2009 peut toucher sa réversion du régime général dès 51 ans. Mort le lendemain, son conjoint attend 55 ans. | larmes | décret n° 2008-1509, art. 2, II ; `data/reference/regles/reversion.yaml` |
| **Un point de moins, et la rente devient un capital** | La retraite additionnelle des fonctionnaires se verse en rente à partir de 5 125 points. Avec 5 124, elle se verse en capital. | rire | décret n° 2004-569, art. 9 ; `data/reference/regles/rafp_majoration_capital.yaml` |
| **Un an de plus, une annuité de moins** | Jusqu'en 2023, la bonification du cinquième était maximale pour le militaire parti à 59 ans, puis « diminuée d'une annuité pour chaque année supplémentaire de service ». L'année servie en plus en effaçait une offerte. | rire jaune | L. 12 i CPCMR, phrase supprimée par la loi n° 2023-270 ; `data/reference/legislation/frontiere_contributive.yaml` |
| **Trois mois en mer en valent six** | Le régime des marins compte les services au semestre : une fraction d'au moins trois mois compte pour six, le reste est négligé. Deux mois et demi en mer ne comptent pas. | rire | code des pensions de retraite des marins, R. 12 ; `data/reference/regimes/marins.yaml` |
| **Quarante ans de mine valent trente** | Le régime des mines ne compte pas plus de 120 trimestres, sauf ceux accomplis avant 55 ans. Les trimestres au-delà ne comptent pas. | larmes | décret n° 46-2769, art. 136 ; `data/reference/regimes/mines.yaml` |

## Salle des cotisations perdues : payer pour rien

Une part de ce que l'on verse n'achète aucun droit : par construction, par
accord, ou parce qu'on a eu le tort de retravailler.

| Pièce | Ce qu'on y voit | Effet | Source |
|---|---|---|---|
| **Payer 127 € pour 100 € de points** | Depuis 2019, l'Agirc-Arrco appelle 127 % de la cotisation qui achète les points : plus d'un cinquième du versement n'achète rien. Deux contributions « non génératrices de droits » s'y ajoutent. Le secrétariat général du COR dit le mécanisme « peu connu des cotisants » ; né en 1952, c'était un rabais, à 78 %. | rire jaune | ANI du 17 novembre 2017, art. 36 et 37 ; `data/reference/legislation/frontiere_contributive.yaml` |
| **17,9 milliards pour rien** | La cotisation vieillesse « déplafonnée » frappe le salaire dès le premier euro, et n'ouvre aucun droit. Le dépôt l'estime à 17,9 Md€ en 2025, dont 3,0 payés par les salariés. | larmes | L. 241-3 et D. 242-4 CSS ; `docs/frontiere_contributive.md`, § 8 |
| **Retravailler pour rien** | Depuis 2015, travailler après sa première pension n'ouvre plus aucun droit. La salariée partie en 2022 sans la durée requise, qui retravaille dix-huit mois, n'acquiert rien. Partie au taux plein, elle se constitue une seconde pension. | larmes | L. 161-22-1 A et L. 161-22-1 CSS ; `data/reference/regles/droits_apres_la_premiere_pension.yaml` |
| **La seule pension « purement contributive » de France** | Cette seconde pension, créée en 2023, ne retient que les périodes cotisées : « Aucune majoration, aucun supplément ni aucun accessoire ». C'est la seule pension purement contributive du droit français, et elle est réservée aux retraités qui retravaillent. | rire jaune | L. 161-22-1-1 CSS ; `docs/frontiere_contributive.md`, § 4 |
| **Le malus pour être parti à l'heure** | Créé en 2015 pour les assurés nés à partir de 1957 : qui partait au taux plein sans attendre un an perdait 10 % de complémentaire pendant trois ans. L'avenant du 22 novembre 2023 l'a supprimé. | rire jaune | ANI du 30 octobre 2015 ; avenant n° 17 du 22 novembre 2023 ; `data/reference/regimes/agirc_arrco.yaml` |
| **Les célibataires payaient pour les épouses des autres** | De 1973 à 2003, le régime des conjoints de commerçants et d'industriels était financé par une cotisation de tous les assujettis. Célibataires, veufs et divorcés devaient demander à en être exonérés. | rire | D. 635-32 à D. 635-35 CSS ; `data/reference/regimes/organic_conjoints_batiment.yaml` |

## Salle des régimes à part : un métier, une caisse

L'inventaire du dépôt compte 108 lignes, des régimes vivants aux caisses
éteintes : chacune ses âges, ses barèmes et ses cotisants, parfois jusqu'au
dernier.

| Pièce | Ce qu'on y voit | Effet | Source |
|---|---|---|---|
| **Retraite à 40 ans, depuis 1698** | À l'Opéra de Paris, dont la caisse remonte à 1698, les artistes du ballet liquident à 40 ans : la fiche y voit « le seul régime français où l'on liquide à quarante ans ». Les chœurs partent à 57 ans, les musiciens à 60. Jusqu'en 2002, les danseuses partaient à 40 ans et les danseurs à 45. | rire | décret n° 68-382, art. 6, rédaction du décret n° 2011-953 ; `data/reference/regimes/opera_de_paris.yaml` |
| **Comédiennes à 50 ans, ouvrières des tabacs à 55** | Jusqu'en 1993, la Comédie-Française ouvrait la pension à 50 ans aux femmes, à 55 aux hommes. À la SEITA, la règle est toujours en vigueur : les ouvrières peuvent partir à 55 ans avec trente ans de services, les autres agents à 60. | rire jaune | décret n° 68-960 ; décret n° 62-766, art. 110 ; `data/reference/regimes/comedie_francaise.yaml`, `data/reference/regimes/seita.yaml` |
| **La réforme qui a oublié l'Opéra** | La loi de 2023 relève l'âge de presque tous les régimes. Elle laisse l'Opéra, la Comédie-Française, les mines et la SEITA à leurs âges, les marins à 55 ans, les navigants de l'aviation civile à 50. | rire jaune | loi n° 2023-270, art. 1er ; décret n° 2023-840 ; `data/reference/legislation/reformes.yaml` |
| **Zéro cotisant, des pensions quand même** | Plus personne ne cotise à l'ORTF depuis 1975, ni à la SEITA, qui servait encore 6 131 pensions en 2024. Les chemins de fer franco-éthiopiens n'ont plus de cotisants non plus. Depuis 2025, le régime général équilibre ces régimes fermés, et l'État le rembourse. | rire | L. 134-3 CSS ; PAP 2026, programme 195 ; `data/reference/regimes/ortf.yaml`, `data/reference/regimes/pap_regimes_subventionnes.csv`, `docs/regimes.md` |
| **Le dernier pensionné** | La caisse de l'Imprimerie nationale, créée en 1927, comptait dix affiliés en 2007. Elle s'est éteinte fin 2013, « avec le décès du dernier pensionné ». | larmes | loi du 29 juin 1927 ; PAP du programme 195 ; `data/reference/regimes/imprimerie_nationale.yaml` |
| **Même pension pour l'abatteur et l'ingénieur** | La pension du mineur n'a jamais dépendu de son salaire : c'est un forfait par trimestre de service, le même pour l'abatteur et pour l'ingénieur. Le régime comptait 765 cotisants en 2024 pour 86 133 retraités ; ses bénéficiaires ont 79 ans en moyenne. | rire jaune | décret n° 46-2769, art. 131 ; `data/reference/regimes/mines.yaml`, `data/reference/regimes/cotisants.csv` |
| **Même retraite de base pour tous les avocats** | Le régime de base des avocats sert un forfait : 19 154 € par an au taux plein en 2026, quel que soit le revenu. Le montant n'est pas dans le code : l'assemblée générale de la caisse le fixe. | rire | R. 723-43 CSS ; `data/reference/regimes/cnbf.yaml` |
| **Les notaires choisissaient leur classe** | De 1962 à 2013, une section de la caisse des notaires comptait sept classes, numérotées 0, 1, 2, 3, 4, 6 et 8. « Le choix de la classe elle-même » était « laissé à l'appréciation du notaire » ; sans indication, il cotisait en classe 1. | rire | rapport IGAS n° 2012-110P ; `data/reference/regimes/cprn_complementaire.yaml` |
| **Les vétérinaires cotisaient à l'acte, les paysans à l'hectare** | De 1950 à 1997, la cotisation des vétérinaires se calculait « en fonction d'un certain nombre d'actes médicaux, compte tenu de l'âge ». Avant 1990, celle des exploitants agricoles reposait sur un forfait tiré de la surface de l'exploitation. | rire | décret n° 50-1318, art. 2 ; `data/reference/regles/cotisation_par_classes_liberales.yaml`, `data/reference/regimes/msa_non_salaries.yaml` |
| **Le tabac paie la retraite des buralistes** | Le fonds des redevances des débits de tabac verse une participation « égale au double de la cotisation des gérants » : les deux tiers du financement. Et l'assiette, ce sont « les remises allouées pour la vente des tabacs ». | rire | arrêté du 13 novembre 1963, art. 5 et 6 ; `data/reference/regimes/gerants_debits_tabac.yaml` |
| **Les députés à 84,4 %, les sénateurs en secret** | Jusqu'en 2008, chaque annuité de député valait 2,11 % de l'indemnité : 84,4 % après quarante ans, dès 60 ans. Le règlement de la caisse des sénateurs n'est pas publié. Au CESE, la retenue vaut 3,42 fois celle d'un fonctionnaire. | rire jaune | règlement de la caisse des députés, art. 21 ; Bureau du Sénat, 12 juillet 2023 ; sources hors Journal officiel ; `data/reference/regimes/assemblees_parlementaires.yaml`, `data/reference/regimes/cese_membres.yaml` |
| **Le chômage partiel compte comme de la conduite** | À la SNCF, chaque année de conduite au-delà de la troisième vaut un trimestre gratuit. Depuis mars 2020, les mois de chômage partiel comptent comme des mois de conduite, pour un droit jamais cotisé. | rire | décret n° 2008-639, art. 9, modifié par le décret n° 2020-1489 ; `data/reference/legislation/frontiere_contributive.yaml` |

## Salle des veuves : la réversion, une loterie

Le même décès ne rapporte pas la même chose selon la caisse, la date du
mariage ou le salaire du survivant : un mois d'écart peut valoir 1 050 € par
mois.

| Pièce | Ce qu'on y voit | Effet | Source |
|---|---|---|---|
| **Un mois de mariage, 1 050 € par mois** | Un fonctionnaire retraité meurt le 15 août 2026. Épousée le 14 août 2022, sa veuve touche 1 050 € par mois ; épousée le 15 septembre 2022, rien. Sans enfant, un mariage célébré après le départ doit avoir duré quatre ans. | larmes | L. 39 CPCMR ; simulateur officiel de réversion, saisi le 1er octobre 2026 ; `tests/temoins/exemples_officiels.yaml` |
| **Trois caisses, trois tarifs du deuil** | Le même survivant touche 54 % de la pension de base, sous plafond de ressources et à partir de 55 ans ; 60 % de la complémentaire, sans plafond, à 55 ans ; 50 % d'une pension de fonctionnaire, sans âge ni plafond. | rire jaune | L. 353-1 CSS ; accord Agirc-Arrco ; L. 38 CPCMR ; `data/reference/regles/reversion.yaml`, `data/reference/regles/reversion_agirc_arrco.yaml`, `data/reference/regles/reversion_fonction_publique.yaml` |
| **Chaque euro gagné, un euro de réversion en moins** | Dans l'exemple de la Cnav, la veuve qui gagne 1 150 € par mois voit sa réversion fondre de 530 € à 169,06 € : au-delà du plafond, tout euro de salaire est repris sur la pension. | larmes | circulaire Cnav n° 2005/17, § 31 ; `tests/temoins/exemples_officiels.yaml` |
| **Le même deuil, deux calendriers** | Une veuve de 50 ans, deux enfants à charge : l'Agirc-Arrco lui verse 420 € dès le mois qui suit le décès. Le régime général lui répond « vous n'avez pas encore atteint l'âge requis (55 ans) ». | larmes | simulateur officiel de réversion, saisi le 1er octobre 2026 ; `tests/temoins/exemples_officiels.yaml` |
| **Se remarier, c'est tout perdre, ou rien** | Remariée, la veuve perd sa réversion Agirc-Arrco, et celle de la fonction publique dès un « concubinage notoire ». Le régime général la garde, et paie même l'ex-épouse divorcée et remariée. Ni le PACS ni le concubinage n'ouvrent de réversion. | rire jaune | L. 46 CPCMR ; L. 353-1 CSS ; `data/reference/regles/reversion_fonction_publique.yaml`, `data/reference/regles/reversion.yaml`, `data/reference/regles/reversion_agirc_arrco.yaml` |
| **Le veuf de seconde zone** | De 1982 à 2003, le veuf d'une fonctionnaire n'avait sa moitié de pension qu'à l'âge minimal de jouissance, plafonnée à 37,5 % du traitement de l'indice brut 550. La veuve d'un fonctionnaire touchait la sienne aussitôt, sans plafond. | larmes | L. 38 et L. 50 CPCMR, versions de 1980 à 2003 ; `data/reference/regles/reversion_fonction_publique.yaml` |
| **Orphelin de fonctionnaire, orphelin de salarié** | L'enfant d'un fonctionnaire mort reçoit une pension d'orphelin jusqu'à 21 ans. Les régimes spéciaux ont la leur ; le régime général n'en a pas. | larmes | L. 40 CPCMR ; `data/reference/legislation/avantages_non_contributifs.yaml` |

## Salle des cadeaux : les années qui comptent double

Chez les militaires, 404 478 pensions sur 406 645 portent des annuités jamais
cotisées : près de sept ans en moyenne. Les chiffres viennent du jaune
budgétaire des pensions (stock 2024, départs 2023), relevé par le dépôt.

| Pièce | Ce qu'on y voit | Effet | Source |
|---|---|---|---|
| **Retraité à 35 ans** | Un engagé à 18 ans peut liquider sa pension à 35 : 17 ans de services suffisent au non-officier, 27 à l'officier, sans condition d'âge. La feuille de route y voit « le départ le plus précoce du système, plus précoce que l'Opéra ». | rire | L. 24 II CPCMR ; `docs/archives/feuille_de_route.md` |
| **Une année offerte pour cinq servies** | Le militaire qui a 17 ans de services reçoit une annuité gratuite par tranche de cinq ans, cinq au plus. 98,4 % des militaires partis en 2023 l'ont eue : 146 € de plus par mois. Policiers, pompiers, surveillants et douaniers ont la leur : 312 € par mois. | rire jaune | L. 12 i CPCMR ; lois de 1957, 1989, 1996 et 2003 ; `data/reference/legislation/avantages_non_contributifs.yaml` |
| **La guerre compte double** | Le temps passé en opérations, à la mer ou outre-mer compte double, ou davantage. Avec le cinquième, il figure sur 404 478 des 406 645 pensions militaires, pour 27,4 trimestres en moyenne. | rire jaune | L. 12 c CPCMR ; `data/reference/legislation/avantages_non_contributifs.yaml` |
| **L'heure de vol vaut de l'or** | Heures de vol et plongées en sous-marin rapportent des annuités gratuites, selon des coefficients fixés à l'ouverture du droit. Une pension militaire sur deux en porte : 16,9 trimestres en moyenne. | rire | L. 12 d CPCMR ; `data/reference/legislation/avantages_non_contributifs.yaml` |
| **Le dépaysement** | Servir l'État hors d'Europe rapporte des annuités gratuites. 180 010 pensions civiles en portent, 17,3 trimestres en moyenne : 266 € de plus par mois. | rire | L. 12 a CPCMR ; `data/reference/legislation/avantages_non_contributifs.yaml` |
| **La retraite sous les cocotiers** | Le fonctionnaire retraité qui réside dans certaines collectivités d'outre-mer touche 35 à 75 % de pension en plus, à vie, sans cotisation supplémentaire. Fermée aux nouveaux venus en 2009, elle coûtait encore 0,26 Md€ en 2024. | rire | décret n° 52-1050 du 10 septembre 1952 ; LFR 2008, art. 137 ; `data/reference/legislation/avantages_non_contributifs.yaml`, `docs/avantages_non_contributifs.md` |
| **Dix ans offerts à la RATP** | Les nouveaux retraités de 2023 ont cotisé 125,2 trimestres et en ont validé 168,5 : 43 trimestres payés sans cotisation, toutes bonifications confondues. Le ratio ne bouge pas depuis 2012. | rire jaune | décret n° 2008-637, art. 20 ; PAP 2026, programme 198 ; `data/reference/legislation/avantages_non_contributifs.yaml` |

## Salle des fantômes : les règles d'antan

Le plus vieux régime de France a plus de trois siècles, et des règles d'hier
feraient scandale aujourd'hui. Viennent ensuite l'Opéra en 1698, la Banque de
France en 1806 et la Comédie-Française en 1812.

| Pièce | Ce qu'on y voit | Effet | Source |
|---|---|---|---|
| **Colbert, 1673** | Le régime des marins, fondé par Colbert en 1673, est le plus ancien de France. Cotisations et pensions y reposent encore sur des salaires forfaitaires, en vingt catégories définies par le métier : « 1re : apprenti ; 2e : matelot de moins de 18 ans ; 3e : élève officier, matelot léger… » | rire | décret n° 2020-649 ; `data/reference/regimes/marins.yaml` |
| **Quarante ans de carrière payés comme vingt** | En 1945, la pension du régime général valait 20 % du salaire à 60 ans, 40 % à 65. Jusqu'à l'ordonnance du 26 mars 1982, une carrière de quarante ans liquidée à 60 ans était servie au même taux réduit qu'une carrière de vingt. | larmes | ordonnances des 4 et 19 octobre 1945 ; ordonnance du 26 mars 1982 ; `data/reference/regimes/regime_general.yaml` |
| **La capitalisation ruinée** | Les retraites ouvrières de 1910 et les assurances sociales de 1930 plaçaient les cotisations ; l'inflation des années 1940 a ruiné les secondes. La loi du 14 mars 1941 crée le premier mécanisme en répartition : une allocation forfaitaire, sous condition de ressources. | larmes | loi du 5 avril 1910 ; lois de 1928 et 1930 ; loi du 14 mars 1941 ; `data/reference/regimes/assurances_sociales.yaml`, `data/reference/regimes/avts.yaml` |
| **Une retraite allemande en France** | En Alsace-Moselle, la législation allemande de 1889 et de 1911 est restée en vigueur après 1918, jusqu'à sa fusion dans le régime général en 1946. | rire | décret n° 76-405 ; `data/reference/regimes/regime_local_alsace_moselle.yaml` |
| **La mère d'un seul enfant n'avait droit à rien** | De 1972 à 1974, le régime général accordait un an d'assurance par enfant élevé, mais seulement à la mère d'au moins deux enfants. | larmes | loi n° 71-1132 ; `data/reference/regles/majoration_duree_assurance_enfants.yaml` |
| **Trois enfants, et la retraite tout de suite** | De 1982 à 2011, le fonctionnaire parent de trois enfants pouvait liquider sa pension immédiatement, la mère seule jusqu'en 2004. L'expression « trois enfants » a quitté le code en 2011, et n'y est jamais revenue. | rire jaune | L. 24 CPCMR ; loi n° 2010-1330 ; `data/reference/legislation/frontiere_contributive.yaml` |
| **La loterie de la caisse** | Avant 1999, la majoration pour enfants de l'Arrco n'existait que si le règlement de la caisse la prévoyait. La Capaves n'en servait pas ; la Camarca, celle des salariés agricoles, servait 2,5 % par enfant. | rire | accords de l'Arrco ; `data/reference/regles/majoration_enfants_agirc_arrco.yaml` |
| **Veuve à 50 ans, veuf à 65** | À l'Agirc, pour un décès survenu avant mai 1990, la veuve touchait sa réversion à 50 ans, le veuf à 65. | larmes | lu sur le site de la fédération Agirc-Arrco, pas encore sur Légifrance ; `data/reference/regles/reversion_agirc_arrco.yaml` |
| **Cent onze réformes, et la dernière en pause** | Le calendrier du dépôt compte 111 réformes datées, de 1945 à 2026. La plus récente suspend celle de 2023 jusqu'au 1er janvier 2028 : 62 ans et 9 mois, et 170 trimestres, pour les nés de 1963 à mars 1965. L'élection présidentielle de 2027 peut tout refaire. | rire jaune | loi n° 2025-1403, art. 105 ; `data/reference/legislation/reformes.yaml`, `data/reference/regles/fin_de_la_suspension_2028.yaml` |

## Salle des calculs impossibles : quand même les caisses se trompent

Le droit est si touffu que les caisses publient des barèmes périmés, que les
chiffres officiels se contredisent, et que l'État cotise à 126 % de la solde.

| Pièce | Ce qu'on y voit | Effet | Source |
|---|---|---|---|
| **Même les caisses se trompent** | La fiche pratique 2026 de la Cipav applique encore 8,23 %, quand le décret écrit 8,73 % depuis 2025 : son exemple à 40 000 € rend 450,1 points au lieu de 467,8. La calculette de la CAVEC ne connaît que huit classes sur neuf, et facture 25 627 € là où la grille dit 30 616 €. | rire | D. 642-3 CSS ; `docs/archives/limites.md` |
| **La cotisation à 126 %** | Pour ses militaires, l'État employeur verse 126,07 % de la solde depuis 2013, contre 78,28 % pour un civil en 2025. La Cour des comptes n'en rattache que 51,2 points à la retraite proprement dite. Même ce taux se recopie mal : le Service des retraites de l'État écrit 106,83 % pour 2010, où le décret fixe 108,63 %. | rire jaune | décret n° 2010-53 et suivants ; Cour des comptes, 22 septembre 2026, tableau 15 ; `docs/limites.md`, `docs/feuille_de_route.md` |
| **Un archipel, sa propre loi** | Saint-Pierre-et-Miquelon, six mille habitants, a son propre régime. Sa loi du 17 juillet 1987 écrit sa table de durées dans les mêmes termes que le régime général : 152 trimestres pour la génération 1956, contre 166. | rire | loi du 17 juillet 1987 ; `docs/archives/limites.md` |
| **Les TUC, validés quarante ans après** | Les stages d'insertion des années 1980, TUC compris, ne validaient rien. Depuis le 1er septembre 2023, ils valident : un droit qui change quarante ans après coup. | rire jaune | L. 351-3 9° CSS ; `docs/frontiere_contributive.md`, § 5 |
| **Les caisses se contredisent** | La circulaire 2024/15 de la caisse des industries électriques et gazières compte huit trimestres de décote à son § 5, quatre à son § 6. La page de la CRPCEN écrit 66 ans et 2 mois dans un exemple, 66 ans et 5 mois dans le tableau voisin. Celle des marins renvoie à 64 ans, puis fait partir son exemple « à 60 ans ». | rire | `data/reference/regles/decote_regimes_speciaux.yaml`, `data/reference/regimes/marins.yaml` |
| **Une règle écrite trois fois, qui ne sert jamais** | Le plafond de vingt trimestres de décote figure dans trois textes et manque dans deux autres. Il ne mord sur aucune liquidation : l'écart entre l'âge d'ouverture et celui du taux plein ne dépasse jamais vingt trimestres. | rire | `data/reference/regles/plafond_des_trimestres_de_decote.yaml` |
| **Liquidées deux fois** | Les pensions des exploitants agricoles partis en 2026 et 2027 sont calculées selon les anciennes règles, puis recalculées selon les nouvelles d'ici au 31 mars 2028. Si le second calcul donne plus, la caisse régularise. | rire jaune | loi n° 2025-199, art. 87 ; décret n° 2025-1409, art. 6 ; `data/reference/regimes/msa_non_salaries.yaml` |
| **Le minimum contributif n'est pas contributif** | Le minimum de pension du régime général s'appelle « minimum contributif ». Depuis 2016, la solidarité en finance au moins la moitié : son nom dit le contraire de ce qu'il est. | rire | L. 135-2 CSS ; `data/reference/legislation/frontiere_contributive.yaml` |

## Monter la page

Une page à part, `/musee`, rangée sous « Faire connaître » à côté de
« Partager » : le menu garde ses quatre onglets essentiels, que la refonte du
23 septembre 2026 a voulus seuls en tête. Variante plus sobre : une section
repliée de « Pourquoi changer ».

1. **La vitrine.** Un titre de quatre à six mots, la phrase-choc en gras,
   deux phrases d'explication repliées, la source citée dans la page,
   l'étiquette rire, larmes ou rire jaune. Elle finit sur une ligne « Dans le
   compte notionnel », qui renvoie à une phrase déjà vérifiée de l'accueil,
   comme « Pas de trimestres, pas de barèmes, pas de surprise. »
2. **Le code.** Une fonction `musee(contexte)` dans `moteur/js/pages.js`,
   appelée par `rendre` comme `risque` ; son titre et sa description dans
   `TITRES` et `DESCRIPTIONS` ; son lien dans `GROUPES_NAVIGATION` de
   `moteur/js/gabarit.js`.
3. **Les chiffres.** Ceux que le dépôt tient en données se lisent dans le
   paquet, jamais recopiés : 126,07 %, 150 heures, les durées requises. Ceux
   d'un document extérieur, jaune budgétaire ou simulateur officiel, gardent
   leur source et leur date.
4. **Les garde-fous.** Chaque phrase en gras entre au catalogue
   `data/reference/site/affirmations.yaml` : `hors_modele` avec sa source pour
   un fait du droit, `verifiee` avec un contrôle quand le modèle le calcule,
   comme le militaire à 35 ans ou le plafond de réversion. Il faut aussi un
   témoin dans `scripts/construire_temoins.py`, un budget de mots dans
   `tests/test_web.py`, une borne d'incises et le test du menu dans
   `tests/test_web_revues.py`. Les explications repliées tiennent le budget.
5. **Le droit.** Les pièces du droit en vigueur se relisent sur Légifrance au
   moment d'écrire, selon la règle du scénario 1. Les chiffres datés se
   redatent.
6. **Le ton.** On rit des règles, jamais des gens : chaque vitrine donne la
   raison officielle quand elle existe, pénibilité ou risques du métier, et ne
   vise aucun assuré.
7. **Le partage.** Chaque vitrine peut devenir une carte 1200 × 675 de la
   page Partager.
8. **Avant d'écrire.** Une seule session sur les pages à la fois.

## Ce qui reste à vérifier avant de publier

- **Deux pièces reposent sur une source faible.** Les assemblées : règlements
  publiés par elles, hors Journal officiel, et celui du Sénat ne l'est pas.
  Les âges de réversion de l'Agirc avant 1990 : version supposée, lue sur le
  site de la fédération.
- **Des chiffres datés** : le jaune budgétaire (stock 2024, départs 2023), les
  projets annuels de performances de 2026, les simulateurs officiels saisis
  le 1er octobre 2026.
- **Deux chiffres calculés par le dépôt**, et non publiés : les 17,9 Md€ de
  la cotisation déplafonnée, et les deux tiers du financement des
  buralistes, qui se déduisent du « double » de l'arrêté.
- **Partout**, la relecture sur Légifrance des pièces du droit en vigueur, au
  moment d'écrire la page.
