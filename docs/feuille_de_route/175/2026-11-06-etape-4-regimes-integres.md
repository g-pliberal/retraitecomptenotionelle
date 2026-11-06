# Étape 4, thème « Régimes intégrés » : les exposés et leurs références

**Reprise, au 6 novembre 2026.** « Retraite personnelle de base », les huit thèmes de
« Carrière », « Avantages liés au décès de l'assuré », « Allocation du minimum », « RCI »,
« Anciennes prestations » et « Régimes intégrés » sont rangés, ce dernier par cette note (H13).
Suivant : « Accords internationaux et d'outre-mer » (223 exposés : accords 184, règlements
européens 24, outre-mer 15), par sous-thème, sous la convention de la note du premier thème,
avec les listes d'accords, de l'Union et de l'Espace économique européens, et 9 références que
seule lie la liste des personnes qui relèvent des règlements ; puis « Mayotte », avec les quatre
exposés mahorais du décès. La base se relit par l'API hors de 5 h–6 h UTC. Aux sessions des
données : le candidat de cette note. Aux sessions du modèle : ceux de H12, H11, H10, H9, H8, des
majorations et des thèmes précédents ; l'activité accessoire (H6) ; l'AVPF du père (H7).

**Le 6 novembre 2026, ce qui est fait.**

- *La relecture de la base.* Par l'API, le 6 novembre 2026 de 13 h 42 à 13 h 57 UTC, par
  `_obtenir` et `_reference` de `scripts/fetch/cnav_legislation.py`, sans écrire le registre
  par le script : `/expose`, `/liste`, les 8 références du thème encore à lire et les
  circulaires Cnav 34/98, 79/89, 83/91 et 49/91, sans aucun lien du site SharePoint de la
  caisse. Les 29 exposés sont servis à la date que le registre porte (`dateModification`, le
  24 octobre 2025, de 6 h 47 à 7 h 04 UTC). `python scripts/veille_droit.py` : rien de changé
  dans le thème (le seul exposé changé, `prelevement_retraite_cotisation_assurance_maladie_ex.aspx`,
  est d'un autre).
- *La lecture* : les 29 exposés, en entier, par cette session — agent de change (5), chambre de
  commerce et d'industrie de Paris (5) et de Roubaix (5), Crédit foncier de France (7),
  Compagnie générale des eaux (7) : l'intégration, la rente garantie, la rente de réversion
  garantie et sa majoration, l'allocation de veuvage, et pour le Crédit foncier et la compagnie
  la retraite de substitution garantie et la pension de vieillesse de veuve ou de veuf. Les
  cinq exposés de la majoration de la rente de réversion garantie sont un même texte, aux blancs
  près. Lus aussi, au texte servi : les lettres Cnav du 31 mars et du 18 avril 2005, la
  référence « Décret 91/408 », l'objet des circulaires 34/98, 79/89, 83/91 et 49/91, et ce que
  la 34/98 dit de la rente et la 49/91 des périodes. Chacun confronté aux fiches
  `credit_foncier_transfert_1989`, `compagnie_generale_eaux_transfert_1991`,
  `cci_roubaix_transfert_1998` et `cci_paris_transfert_2006`, toutes `pas_encore_modelisee` ;
  aux régimes `credit_foncier` (hors du champ), `compagnie_generale_eaux`, `cci_roubaix` et
  `cci_paris` (à modéliser, sans statut) ; à la fiche `reversion` ; aux statuts de
  `data/reference/legislation/affiliations.yaml` (`salarie_prive_non_cadre`, ligne 101 ;
  `officier_ministeriel`, ligne 931, « commissaire de justice, greffier de tribunal de commerce,
  avocat aux Conseils ») ; à la série `macro/plafond_securite_sociale.csv`. Aucun des deux
  moteurs ne nomme ces régimes ni ces fiches : `credit_foncier`, `cci_paris`, `cci_roubaix`,
  `compagnie_generale_eaux` n'ont aucune occurrence dans le code de `src/` ni de `moteur/js/`
  (de même la relecture R-H6, écart 1), et le paquet `moteur/donnees.json` ne porte que leur
  code. Les textes, à l'index LEGI à jour au 2 novembre 2026 et JORF au
  3 : loi n° 89-18, articles 13 (LEGIARTI000006756499) et 19 (LEGIARTI000006756506) ; décret
  n° 89-640, articles 1er à 7 (LEGIARTI000006774863 à LEGIARTI000006774869) ; décret
  n° 89-157, article 5 (LEGIARTI000006774343) ; loi n° 91-73, article 17
  (LEGIARTI000006696468) ; décret n° 91-408, article 10 (LEGIARTI000006775865, et au JORF
  JORFARTI000001543934 et JORFARTI000000965964, que l'index range sous le titre d'un « Décret du
  26 avril 1991 portant délégation de signature ») ; loi n° 97-1164, article 20
  (LEGIARTI000006757374) ; décret n° 98-183, articles 2 et 5 (LEGIARTI000006772198,
  LEGIARTI000006772201) ; décret n° 2006-1748, articles 2 et 5 (JORFARTI000001497936,
  JORFARTI000001137923). Aucun exposé du thème ne publie d'exemple chiffré.
- *Le rapprochement de l'index* (LEGI à jour au 2 novembre 2026, JORF au 3). 17 exposés lient
  Légifrance 54 fois, sous 15 identifiants. 13 se trouvent à l'index, et chacun concorde avec
  son ancre : 6 articles du code de la sécurité sociale par leur numéro (L. 342-6, L. 351-9,
  L. 353-1, R. 351-26, D. 342-3, D. 355-1), 6 textes de LEGI et 1 du JORF par leur numéro et
  leur date (loi n° 97-1164, décrets n° 89-157, 89-640, 91-408, 98-183, 2006-1748 et
  2016-117) ; chaque article qu'une ancre nomme dans ces textes existe à l'index. 2 sont
  absents par l'identifiant et se trouvent par le numéro : « Loi 89/18 du 13/01/1989 art. 19 »
  et « art.13 » (LEGITEXT000006069078) sont les articles 19 et 13 de la loi n° 89-18 ; « Loi
  91/73 du 18/01/1991 art. 17 » (LEGITEXT000006077122) est l'article 17 de la loi n° 91-73.
  Aucun lien vers un autre site.
- *Les sorts*, sous la convention de la note du premier thème. 29 exposés `limite` : ceux du
  Crédit foncier, de la compagnie et des deux chambres à leur fiche de transfert, à leur régime
  et à la limite ; ceux de l'agent de change, qu'aucune fiche ne porte, à la limite seule ;
  ceux qui servent un survivant (rente de réversion garantie, sa majoration, pension de
  vieillesse de veuve ou de veuf) à la fiche `reversion` aussi, dont ils appliquent les règles.
  Les objets qu'ils lient, déjà rangés, restent tels : la fenêtre « Avantage complémentaire »
  (`hors_modele`, du lexique), 7 barèmes (`branche` ou `recoupe`), 6 exposés d'autres thèmes
  (`limite`). La liste des accords de sécurité sociale, que lient 7 exposés (« la rente
  garantie n'est pas proratisée »), et les 77 autres listes d'accords que la fermeture des liens
  range aussi sous ce thème, restent `a_lire` avec leur thème, « Accords internationaux et
  d'outre-mer », comme les thèmes précédents les ont laissées.
- *Les références*, toutes celles du thème, chacune liée par un exposé rangé ici, qui lui donne
  ses renvois. 8 `a_lire` passent `limite` : circulaires Cnam 68/2000, Cnav 2001/22 et 68/90
  (Crédit foncier et la limite) ; Cnav 47/92 (la compagnie et la limite) ; la référence
  « Décret 91/408 » (la compagnie, `reversion` et la limite) ; Cnav 2006/14 (`reversion`, la
  limite, les quatre fiches et leurs régimes) ; lettres Cnav du 18 avril 2005 (la limite, le
  Crédit foncier et la compagnie) et du 31 mars 2005 (la limite, la chambre de Roubaix). 12 déjà
  `limite` dont le renvoi s'étend (ci-dessous). 1 qui les portait déjà, la circulaire Cnav
  42/90.
- *Les renvois qui s'étendent* (12 références), chaque fois par la fiche de transfert et le
  régime nommés : le Crédit foncier (3) : circulaires Cnav 17/91, 23/90 et, avec la compagnie,
  120/82 ; le Crédit foncier et la compagnie : circulaire Cnav 79/89, que lie aussi l'exposé de
  la pension de vieillesse de veuve ou de veuf de la compagnie ; les quatre (3) : circulaires
  Cnav 2006/37, 2010/15 et 2014/29 ; la chambre de Paris (2) : circulaires Cnav 2007/17 et
  2013/26 ; la chambre de Roubaix et la compagnie : circulaire Cnav 34/98, que lie aussi
  l'exposé de la rente garantie de la compagnie ; la compagnie (2) : circulaires Cnav 83/91 et,
  avec `reversion`, 49/91.
- *La limite* « régimes intégrés » (`docs/limites/3-systeme-actuel.md`), neuve : les rentes
  garanties des cinq régimes, que le modèle ne sert pas, et l'agent de change, qu'aucun statut
  ne nomme.

**Ce que la lecture a trouvé, sans écart.** La rente garantie de chaque régime est celle de son
décret, et de sa fiche quand il en a une : au Crédit foncier, « le salaire plafond annuel
soumis à cotisations de 1988 : 120 360,00 Francs », au taux de 50 % (décret n° 89-157,
article 5 : « 50 p. 100 du salaire plafond moyen ») ; à la compagnie, « d'un salaire annuel de
référence égal à 98,66 % du salaire plafond annuel soumis à cotisations au régime général en
1990, soit 129 300,00 Francs », la moitié faisant les 64 650 F de l'article 10 du décret
n° 91-408 ; à la chambre de Roubaix, « d'un salaire annuel égal à 75,49 % du salaire plafond
annuel soumis à cotisations en 1997 soit 124 300,00 F », la moitié faisant les 62 150 F de
l'article 5 du décret n° 98-183 ; à la chambre de Paris, « d'un salaire annuel de référence égal
à 90 % du salaire plafond annuel soumis à cotisations au régime général en 2005 soit 27 172,80
euros », la moitié de 90 % du plafond de 2005 de la fiche ; à l'agent de change, « du salaire
plafond moyen de sécurité sociale de l'année 1988 soit 120360,00 F » et « d'un taux de 30 %
applicable à ce salaire », soit le décret n° 89-640, article 3 : « 50 p. 100 d'un salaire
lui-même égal à 60 p. 100 du salaire plafond moyen soumis à cotisation à l'assurance vieillesse
du régime général en 1988 », pour cent cinquante trimestres. Calculé à la main sur la série du
dépôt, arrondie à l'euro : 120 360 F font le plafond de 1988 (18 349 €, 120 361,55 F) ;
129 300 F, 98,672 % de celui de 1990 (19 977 €, 131 040,53 F) ; 124 300 F, 75,498 % de celui
de 1997 (25 099 €, 164 638,65 F) ; 27 172,80 €, 90 % de celui de 2005 (30 192 €). La rente pleine du Crédit
foncier vaut donc 60 180 F, ce que la fiche disait « environ », « à confirmer contre le
« salaire plafond moyen » que la Cnav a retenu » (`sources.a_relire`) : l'exposé le confirme ;
et les rentes de 1991 et de 1998 ne sont pas la moitié du plafond de l'année d'avant, mais la
moitié d'une fraction de ce plafond, ce que la même entrée demandait de vérifier. La chambre de
Paris : ses agents qui n'avaient pas liquidé « ont été rétablis dans les droits qu'ils auraient
eus si le régime général leur avait été applicable » (exposé « Intégration »), ce que le
modèle fait en les simulant salariés du privé, comme le dit le régime `cci_paris` ; la
réversion de qui tenait déjà une réversion de la chambre, sans la condition de ressources
(décret n° 2006-1748, article 2 : « à l'exception de la condition de ressources prévue à
l'article R. 353-1 du code de la sécurité sociale » ; l'article 5, la même, différée), comme la
fiche, quand le conjoint d'un titulaire mort depuis 2006 la reçoit « s'il réunit toutes les
conditions pour l'attribution de la retraite de réversion du régime général », ressources
comprises. Les lettres Cnav de 2005 : la rente garantie est servie dès la retraite anticipée
(« je ne suis pas opposé à faire rétroagir à la date d'effet fixée pour la retraite anticipée
le point de départ de la rente garantie »), et « les trimestres durant lesquels les assurés ont
relevé d'un régime d'assurance vieillesse intégré au régime général peuvent être retenus au
titre de la durée totale d'assurance et de la durée d'assurance cotisée » de la retraite
anticipée des assurés handicapés, comme le modèle les compte quand ces années sont saisies au
régime général. Ce que d'autres ont déjà déclaré, que ces exposés touchent : les années d'avant
l'intégration simulées au régime général sur le salaire, quand la loi les rend en rente
(régimes `compagnie_generale_eaux`, `cci_roubaix`, `cci_paris`, champ `manque` ; limite 4,
« Des régimes hors champ dont la loi garde une part ») ; l'assurance volontaire des préretraités
du Crédit foncier de 1997 (la limite « rachats et versements ») ; la réversion du régime
général, son taux, ses ressources et leur partage entre régimes depuis le 1er juillet 2006, et
la pension de vieillesse de veuve ou de veuf (note du thème « Avantages liés au décès de
l'assuré ») ; le versement forfaitaire unique, abrogé par le décret n° 2016-117 (thème
« Retraite personnelle de base »).

**Un candidat, aux sessions des données** (rien n'a été corrigé) : *deux populations que les
fiches mettent au régime spécial, et que la caisse dit au régime général.* La chambre de
Roubaix : la circulaire Cnav 34/98, servie, dit que seuls les personnels recrutés avant le
1er janvier 1967 sont restés affiliés au régime spécial — « Les personnels recrutés à compter
de cette date relèvent du régime général de la sécurité sociale » — ; la loi n° 97-1164,
article 20, ne transfère que les salariés « qui relevaient antérieurement, pour les risques
invalidité et vieillesse, du régime spécial de cette chambre ». Le régime `cci_roubaix` porte
`fermeture: 1997`, que son schéma définit « année de fermeture aux nouveaux entrants », et sa
population « Salariés de l'ancienne CCI de Roubaix avant 1998 » ; la fiche
`cci_roubaix_transfert_1998`, en `effet` : « Les salariés de l'ancienne chambre de Roubaix
entrés avant 1998 : leurs années d'avant 1998 valent une rente forfaitaire du régime général ».
La compagnie : l'exposé « Rente garantie de la Compagnie générale des eaux » : « Le personnel
de la Région lyonnaise a été affilié au régime général à partir du 01/01/1971. Les périodes
validées par la CGE sont arrêtées au 31/12/1970. » (circulaire Cnav 49/91, § 11, servie :
« effectif de 80 personnes environ ») ; la fiche `compagnie_generale_eaux_transfert_1991`, en
`effet` : « leurs années d'avant 1991 valent une rente forfaitaire du régime général ». *Cas
posés*, sur les rentes des décrets : l'agent recruté par la chambre de Roubaix en janvier 1970,
resté jusqu'en 1997 (112 trimestres) — la fiche lui donne une rente de 62 150 × 112 / 150 =
46 405,33 F par an au 1er janvier 1998, à la place d'une pension sur son salaire ; la circulaire,
aucune rente : ses années sont au régime général, sur son salaire. L'agent lyonnais de la
compagnie de 1960 à 1990 (124 trimestres) — la fiche : 64 650 × 124 / 150 = 53 444 F ; la
circulaire : 64 650 × 44 / 150 = 18 964 F pour 1960 à 1970, et 1971 à 1990 au régime général.
Le modèle, qui ne route aucun des deux régimes, simule ces années au régime général quand elles
sont saisies en salarié du privé : pour ces deux populations, c'est le droit, et c'est la fiche
qui dit un écart qui n'existe pas ; aucune pension calculée ne bouge. Le texte de 1967 qui
ferme le régime de Roubaix n'est pas à l'index du JORF, filtré : la circulaire seule le dit.

**Ce que la base sert de travers.** L'exposé « Intégration de la Chambre de commerce et
d'industrie de Roubaix » cite « Circulaire Cnav 34/98 du 02/06/1997 § 4117 », que le lien mène
à la circulaire du 2 juin 1998. Deux exposés de la compagnie citent la circulaire d'un autre
régime : « Rente garantie de la Compagnie générale des eaux », pour la condition de cessation
d'activité, « Circulaire Cnav 34/98 du 02/06/1998 § 326, § 31217, § 31226, §3115 », la
circulaire de l'intégration de la chambre de Roubaix, aux paragraphes que cite l'exposé de la
chambre ; « Pension vieillesse de veuve ou de veuf de la Compagnie générale des eaux », pour le
cumul, « Circulaire Cnav 79/89 du 04/08/1989 § 4414 », dont l'objet est « Intégration du régime
spécial du Crédit Foncier de France au régime général », au paragraphe qu'en cite l'exposé du
Crédit foncier. L'exposé « Intégration des agents de change » dit le régime général chargé
« des droits des salariés de ce régime et de leurs conjoints survivants », quand la loi
n° 89-18, article 19, transfère les droits des agents de change « pour les périodes au cours
desquelles les agents de change ont exercé une activité exclusivement libérale ». « 98,66 % »
du plafond de 1990, quand 129 300 F en font 98,672 % au plafond de la série, et de 98,670 à
98,675 % quel que soit l'arrondi de celle-ci à l'euro ; le montant, lui, est celui du décret.

**Ce que la lecture n'a pas fait.** Aucune règle, aucune fiche, aucune série, aucune valeur
servie, aucun test n'a été changé ; le registre seul, en ses colonnes `sort` et `renvoi`, et la
limite neuve. Les références prennent les renvois des objets rangés ici qui les lient, sans ceux
des barèmes, des avis, ni des fiches qui les citent par leur numéro. Les circulaires du thème
ne sont pas lues en entier ; le décret n° 89-640, article 5, la rente du régime des industriels
et commerçants de l'agent de change qui exerçait encore, n'est confronté à aucune fiche, faute
d'en avoir une.
