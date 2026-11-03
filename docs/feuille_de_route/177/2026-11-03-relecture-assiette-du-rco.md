# Relecture de l'assiette du RCO des artisans et du NRCO des commerçants

File R-M2, le 3 novembre 2026 : relecture indépendante des commits f716130, f63fec0,
93906ff, 1aa23ce, 4209a8a, 5cda81f, c48cd2c et 144a622 (session M2, notes
`2026-11-03-etape-9-assiette-du-rco-des-artisans.md` et
`2026-11-03-etape-9-assiette-du-rco-ecrite.md`). Chaque source a été rouverte ici, sans
rien reprendre de la session ni de mémoire : les index LEGI et JORF de la DILA récupérés et
mis à jour (LEGI à jour au 2 novembre 2026 ; JORF, l'incrément du 3 novembre appliqué) ;
les exposés, l'exemple et la table de la Cnav servis le jour par sa base de législation,
leur empreinte calculée ; la série de l'IPP des revenus de référence des commerçants. Les
33 citations de la fiche `assiette_rco_independants` ont été comparées au texte de l'index
par un script, fragment par fragment entre les « [...] ». Rien n'a été modifié : ni règle,
ni donnée, ni test, ni fiche.

**Verdict.** La règle, ses bornes et chaque citation : **conforme** — le RCO des artisans
assis, jusqu'aux cotisations de 2008, sur le revenu de l'avant-dernière année, borné aux
plafonds de l'année due, sans ajustement ; le NRCO des commerçants de même, de 2004 à 2008 ;
l'artisan qui commence au tiers puis à la moitié du plafond de la sécurité sociale, de 1979
à 2011 ; la cotisation additionnelle de 0,10 %, de 1985 à 1996, sans points. Les deux
moteurs rendent les valeurs refaites à la main ; ses tests, le lot rapide et la garde des
présomptions sont verts. La marge relevée dans `tests/test_cout.py` s'explique entièrement
par la correction. **Quatre écarts, tous mineurs**, aucun ne touchant la règle écrite : un
cas non servi ni déclaré, le conjoint collaborateur à une fraction du revenu du chef
(point 5, a) ; une incertitude restée hors de la limite publiée, le forfait de l'artisan de
2009 à 2011 (5, b) ; une explication incomplète de la marge (4) ; un effet décrit à moitié
(6). Une date à préciser (5, c).

## 1. Les textes, à la version en vigueur

| Texte | Identifiant ouvert | Constat |
|---|---|---|
| Décret n° 78-351, art. 12 | LEGIARTI000006766114 | « Pour l'obligation de cotiser, le 1er janvier 1979 » : **conforme** |
| Décret n° 78-351, art. 3 | LEGIARTI000006766103 | seule rédaction, du 19 mars 1978 au 21 décembre 1985 ; citation exacte ; les passages élidés (« A défaut de déclaration [...] sur la base de ladite limite », « Toutefois [...] revenu minimum ») ne changent pas la règle ; le IV, « deux fois le plafond visé au premier alinéa du I » assis « sur le double plafond », lu en entier : **conforme** |
| Décret n° 78-351, art. 4, II | LEGIARTI000006766104 | « sur demande motivée, la cotisation [...] peut être assise sur un revenu inférieur » : **conforme** |
| Décret n° 78-351, art. 5, rédactions de 1978 et de 1985 | LEGIARTI000006766105, LEGIARTI000006766106 | 4,40 % ; « A compter du 1er janvier 1985, est due en sus [...] une cotisation additionnelle fixée à 0,10 p. 100 » ; le III et le IV lus en entier : le III : « Le remboursement de tout solde visé à l'avant-dernier alinéa de l'article 9 du décret du 22 janvier 1973 susvisé n'intervient que pour la part qui excède le montant des cotisations dues en application du présent décret » ; le IV ne rend applicables que les articles 12 à 14, 16 et 18 de ce décret : **conforme** |
| Décret n° 78-351, art. 6, rédactions de 1978 et de 1985 | LEGIARTI000006766107, LEGIARTI000006766108 | « la cotisation prévue à l'article 5-I, 1er alinéa » : **conforme** |
| Décret n° 73-76, art. 9, 12 à 14, 16, 18 ; art. 2, 6 et 11 | LEGIARTI000006765793 ; LEGIARTI000006765797 à LEGIARTI000006765800, LEGIARTI000006765802, LEGIARTI000006765804 ; LEGIARTI000006765785, LEGIARTI000006765789, LEGIARTI000006765796 | l'article 9 est l'« ajustement des cotisations provisionnelles [...] sur la base des revenus de l'année à laquelle se rapportent ces cotisations » ; 12 à 14, 16 et 18 ne règlent que les majorations de retard, les pénalités, le précompte et les frais : la complémentaire n'a pas d'ajustement, **conforme**. L'article 6 assied le débutant du régime de base sur « un revenu forfaitaire égal au tiers du plafond visé à l'article L. 663-9 », puis « à la moitié dudit plafond », l'article 11 l'aide familial sur « un revenu égal au tiers du plafond visé à l'article L. 663-9 » : l'article 3, II et III, du décret n° 78-351 reprend ce schéma, nouvel appui à la lecture du plafond de la sécurité sociale, non de l'assiette maximale |
| Décret n° 84-1064 | JORFTEXT000000516015 (notice) | « INSTITUTION D'UNE COTISATION ADDITIONNELLE FIXEE A 0,10% DU REVENU », articles 5-1 et 6-1 modifiés « A COMPTER DU 01-01-1985 » : **conforme** |
| D. 635-4, quatre rédactions de 1985 à 2004 | LEGIARTI000006738335 à LEGIARTI000006738338 | chacune porte l'avant-dernière année, le plafond « en vigueur dans l'année où la cotisation est due », le minimum et les deux forfaits ; trois plafonds jusqu'au 26 février 1997, quatre ensuite : **conforme** |
| Décret n° 97-166, art. 1er et 2 | JORFARTI000001797721, JORFARTI000002186642 | « les mots << trois fois >> sont remplacés par les mots << quatre fois >> » ; D. 635-6 à 4,90 % « à compter du 1er janvier 1997 », et « Le deuxième alinéa du même article est abrogé » : la cotisation additionnelle s'arrête avec 1996, **conforme** |
| D. 635-6 (1985, 1997, 2003) ; D. 635-7 (1985) | LEGIARTI000006738071, LEGIARTI000006738072, LEGIARTI000006738075 ; LEGIARTI000006738024 | **conforme** |
| L. 635-1, rédaction du 1er janvier 2004 | LEGIARTI000006743725 | non lu par la session : « Toute personne relevant de l'une des organisations mentionnées au l° ou au 2° de l'article L. 621-3 [...] est affiliée d'office au régime complémentaire obligatoire de l'organisation dont elle relève » — la borne de 2004 du NRCO, **conforme** |
| Décret n° 2004-848, art. 1er et 2 | JORFARTI000001334654, JORFARTI000001869280 | écrit D. 635-1, D. 635-2 et D. 635-10 tels que cités ; « 6,70 % au titre de l'année 2004 » pour les artisans : **conforme** |
| D. 635-1, D. 635-2 (2004, 2008), D. 635-7 (2004), D. 635-10 (2004, 2005) | LEGIARTI000006738013, LEGIARTI000006738016, LEGIARTI000006738017, LEGIARTI000006738025, LEGIARTI000006738027, LEGIARTI000006738028 | citations exactes : **conforme** |
| Décret n° 2005-272, art. 1er | JORFARTI000001098796 | D. 635-10 « à 6,5 % » : **conforme** |
| L. 131-6, rédactions de 2003, 2007 et 2009 | LEGIARTI000006740118, LEGIARTI000006740121, LEGIARTI000020169101 | citations exactes ; en 2003, le sixième alinéa est celui des forfaits (« Par dérogation aux quatrième et sixième alinéas ») ; en 2009, le cinquième est celui du provisionnel et de la régularisation, le septième celui des forfaits : **conforme** |
| R. 242-16 (2002, 2008) | LEGIARTI000006748778, LEGIARTI000006748779 | dix-huit fois la base mensuelle, puis « majorée de 50 % » ou vingt-sept fois ; la reprise « soit dans l'année au cours de laquelle est survenue la cessation d'activité, soit dans l'année suivante » n'est pas un début : **conforme** |
| D. 635-10-2 ; D. 633-19-2 | LEGIARTI000006738041 ; LEGIARTI000006737951 | citations exactes : **conforme**, mais voir le point 5, a |
| Décret n° 2007-1900, art. 1er | JORFARTI000017765872 | 7,2 % et 7,6 % au I, mais « 7 % au titre de l'année 2008 et [...] 7,1 % au titre de l'année 2009 » (III), 7 % et 7,5 % (IV) : les taux des tests de 2008 et 2009 sont justes |
| Décret n° 2008-1427, art. 1er à 3 et visas | JORFARTI000019996956, JORFARTI000019996958, JORFARTI000019996960, JORFTEXT000019996954 | « aux cotisations dues au titre des revenus des années 2009 et suivantes » ; aucune disposition de passage ; l'article 2 renumérote le renvoi de D. 635-10 : **conforme** |
| D. 635-2 (29 décembre 2008), D. 635-7 (2008), D. 635-10 (2009) | LEGIARTI000020032159, LEGIARTI000017869802, LEGIARTI000020032165 | **conforme** |
| Décret n° 2011-2038, art. 1er à 4 | JORFARTI000025055794, JORFARTI000025055797, JORFARTI000025055800, JORFARTI000025055807 | l'article 3, II, 1°, supprime les sixième à huitième alinéas de D. 635-7 — la rédaction qui en naît (ligne suivante) garde les aides familiaux et perd le seul forfait — ; l'article 4 : « Les dispositions du présent décret entrent en vigueur le 1er janvier 2012 » (l'index date l'article de sa publication, le 30 décembre 2011) : **conforme** |
| D. 635-7 (2012), L. 131-6-2 (2011) | LEGIARTI000025091410, LEGIARTI000025013725 | le forfait a disparu : **conforme** |
| D. 635-2 (2012, 2013, 2015, 2016) | LEGIARTI000025629861, LEGIARTI000025263548, LEGIARTI000030034575, LEGIARTI000031799392 | l'assiette du régime de base dès quatre-vingt-dix jours (2012-2014), « 5,25 % de la valeur du plafond » (2015), plus de minimum (2016) : **conforme** |
| D. 633-2 (1985-2012) | LEGIARTI000006737877 à LEGIARTI000006737879 | « 200 fois le montant horaire du salaire minimum de croissance », jusqu'au 5 avril 2012 : voir le point 5, c |
| Arrêtés du 23 avril et du 7 juillet 2009 | JORFARTI000020676129, JORFARTI000021059798 | les citations de la note de lecture sont exactes ; « Pour les périodes antérieures au 1er janvier 2009 », les cotisations « en application de l'article D. 635-2 », et « Pour les périodes débutant à compter du 1er janvier 2009 », provisionnelles puis définitives : la borne de 2009 corroborée |

| Document de la Cnav | Version, empreinte | Constat |
|---|---|---|
| Exposé « Points cotisés artisans avant 2013 » | modifié le 24 octobre 2025 ; sha256 00551d94d96eebe54eccf80d066a88907ecdf53c69dab241690aeaed9476b6e5 (contenu servi par l'API) | « Le nombre de points cotisés est égal à : Montant des cotisations RCO réglées sur l'année N ÷ Revenu de référence de l'année N » ; « Une cotisation additionnelle de 0,10 point a été prélevée entre 1985 et 1996. [...] Cette cotisation n’etait pas génératrice de droit » : **conforme** |
| Exposé « Rachat aide familial » | modifié le 14 octobre 2026 ; sha256 d00ae42d2af53483685fa009aa656240494293cb791456a390ed74985f3bc85a | « Les cotisations sont calculées sur le tiers du plafond de la sécurité sociale multiplié par le taux de la cotisation pour l’année considérée » : **conforme** |
| Exposé « Points cotisés commerçants avant 2013 », non cité par la session | modifié le 24 octobre 2025 ; sha256 02bdd67b2c4cfeefd3db7da9a935d569e1915b93acc05a413628e66f7c452fdb | « Le 01/01/2004, un nouveau régime complémentaire obligatoire (NRCO) est mis en place » ; « Ce nombre de points cotisés est égal au montant des cotisations NRCO réglées sur l'année N divisé par le revenu de référence de l’année N » : corrobore |
| Exposé « Evolution des régimes complémentaires » | modifié le 24 octobre 2025 ; sha256 41010307a9be8de20293e0f5cd43f911d13213dcdb745dfab9fce7567a7a7277 | le RCO « Du 01/01/1979 au 31/12/2012 », le NRCO dès le 1er janvier 2004 : corrobore |
| Exemple « Régime complémentaire obligatoire - Dispense après le 01/01/2009 » | modifié le 2 juin 2023 ; sha256 f961c7aa89b8a06b5253e89f8570da28f1f1dbcc225e15596960d7e2259fe7e3 | « Cotisation provisionnelle 2010 : 18 000 € x 7,1 % », sur le « Revenu 2008 », puis « Régularisation 2010: 15 000 € x 7,1 % » : les citations de la note de lecture sont exactes |
| Table « ARTISANS : RCO - revenu de référence » (Info-doc RSI du 14 juin 2012), jointe au barème « Valeur d'achat du point de retraite complémentaire » | PDF, sha256 fbce0850ae56806933cae95dad4122c84040ca9d95aa17fa9307abf16c0b91a9 | chaque revenu de référence des tests, de 5,86 F en 1979 à 4,89113 € en 2012, converti à 6,55957 F, est celui de `valeurs_point.csv` : **conforme** |

*Un autre texte change-t-il la règle ?* Toutes les rédactions de D. 635-1 à D. 635-10-2, de
D. 633-19 à D. 633-19-10, de R. 242-16, de L. 131-6, de L. 131-6-2 et de L. 635-1 (jusqu'en
2011) que porte l'index ont été listées, et lues celles qui portent l'assiette, le taux, les
points ou le début d'activité : aucune ne change l'année du revenu avant les cotisations de
2009, ni les forfaits avant 2012 ; D. 635-2 de 1985 à 2004 (LEGIARTI000006738015) institue le
régime, D. 635-4 depuis 2004 (LEGIARTI000006738339) règle le rachat. Dans le JORF, de 2003 à
2005, « complémentaire obligatoire » avec les commerçants et « avant-dernière » ne trouve que
le décret n° 2004-848. Le plafond de la sécurité sociale des forfaits : 60 120 F en 1980
(décret n° 79-1136, JORFTEXT000000329018), 68 760 F en 1981 (décret n° 80-1080,
JORFTEXT000000861295).

## 2. Les valeurs refaites à la main

Points = assiette × taux / revenu de référence de l'exercice ; revenus de référence de la
table de la caisse (en francs jusqu'en 2000, convertis à 6,55957), plafonds des décrets,
revenu de référence des commerçants de l'IPP (14,389 €, à la date d'effet du 1er janvier
2006 ; sha256 de la série 35cbc1b5…, la table de la caisse étant un lien mort). Rendu par les deux moteurs, par le chemin même des tests.

| Cas | À la main | Python | JavaScript |
|---|---|---|---|
| artisan qui débute en 1980 : 60 120 F / 6,55957 / 3 × 4,40 % / (6,58 F / 6,55957) | 134,0061 | 134,0026 | 134,0026 |
| même artisan, 1981 : 68 760 F / 6,55957 / 2 × 4,40 % / (7,46 F / 6,55957) | 202,7775 | 202,7698 | 202,7698 |
| même artisan, 1982 : revenu de 1980, 10 000 € × 4,40 % / (8,41 F / 6,55957) | 343,1880 | 343,1880 | 343,1880 |
| artisan de 1990 (15 000 € en 1985, 1 000 € de plus chaque année) : revenu de 1988, 18 000 € × 4,40 % (et non 4,50) / (13,19 F / 6,55957) | 393,8726 | 393,8725 | 393,8725 |
| même année, revenu de 1988 de 70 000 €, borné à trois plafonds de 1990 (19 977 €, la valeur « certifiée » du fichier, dont l'index ne m'a pas rendu le texte) : 3 × 19 977 € × 4,40 % / (13,19 F / 6,55957) | 1 311,3985 | 1 311,3985 | 1 311,3985 |
| commerçant depuis 2001, 2006 : revenu de 2004, 18 000 € × 6,5 % / 14,389 | 81,3121 | 81,3121 | 81,3121 |
| commerçant installé en 2005, 2006 : revenu de l'année (l'approximation déclarée), 13 000 € × 6,5 % / 14,389 | 58,7254 | 58,7254 | 58,7254 |

Les deux moteurs rendent les mêmes valeurs ; l'écart à la main, 4 × 10⁻⁵ au plus, vient du
plafond d'avant 2002 que `plafond_securite_sociale.csv` garde arrondi à l'euro (9 165 € pour
9 165,23 €).

## 3. Les deux moteurs et les tests

Sur 144a622 : les six tests de la session, **6 réussis** ; `python -m pytest -m rapide`,
**4 209 réussis, 6 sautés** ; `PRESOMPTIONS_DECALEES=1 python -m pytest -m rapide`,
**4 014 réussis, 201 sautés**. La relecture R-M4 avait relevé, avant 144a622, 24 échecs du
lot rapide nés de f716130 (son journal de veille) ; 144a622 refait le paquet, « sans eux,
les comparaisons des deux moteurs échouaient ».

## 4. La marge de `tests/test_cout.py`

Mesuré ici, par le calcul même de `_ecarts_par_groupe`, dans trois arbres :

| État | Complémentaires | Non-salariés |
|---|---|---|
| eab4dae, avant la session | +7,8721 % | +10,8459 % |
| 144a622, après | +8,1703 % | +11,2390 % |
| 144a622 sans les quatre commits du modèle (f716130, f63fec0, 93906ff, 1aa23ce retirés) | +7,8721 % | +10,8459 % |

Les six commits des autres sessions passés entre-temps ne déplacent rien, à la quatrième
décimale : **tout le déplacement vient de la correction**, +0,30 point pour les
complémentaires, +0,39 pour les non-salariés. Commit par commit : l'avant-dernière année
+0,303 et +0,409 ; les forfaits −0,029 et −0,045 ; le NRCO rien, la grille du coût n'ayant
aucun commerçant (`GRILLE_DU_COUT`) ; le 0,10 % +0,024 et +0,029. Les anciennes tolérances,
8 et 11 %, étaient dépassées de 0,17 et 0,24 point ; les nouvelles, 9 et 12 %, suivent la
règle que tient l'historique du fichier (l'écart mesuré arrondi au point supérieur : 5,2 à
6, 8,2 à 9, 6,3 à 7, 7,9 à 8, 10,8 à 11), et laissent 0,83 et 0,76 point de jeu. **L'élargissement est justifié.**

*L'écart : son explication est incomplète.* Le commentaire dit que l'assiette « ôte de 0,1 à
2,3 % à la pension des artisans et des commerçants d'avant 2009 » et chiffre le déplacement,
sans dire deux choses. Pourquoi une correction qui baisse les pensions élève l'écart :
l'écart compare la croissance de la dépense de 2025 à 2070, et la correction porte sur les
années d'avant 2009, qui pèsent dans les pensions servies en 2025 bien plus qu'en 2070.
Pourquoi les non-salariés bougent plus que les complémentaires, quand leur groupe n'a aucun
RCO (`GROUPES_DU_MODELE` : `msa_non_salaries`, `cnavpl`, `cnbf`) : par le calage des poids
par groupe (`_poids_par_groupe`), qui multiplie le coefficient de chaque cas type par la
correction de ses groupes et ramène les poids à leur somme. Ces deux explications se lisent
dans le code et la règle ; la mesure ne les isole pas. Mineur, de documentation.

*D'où vient le reste de l'écart.* La documentation le dit : l'historique daté au-dessus de
`DECOMPOSITION_GROUPES_SUIVIS` — l'inapte et l'ex-invalide de la Cnav le 19 octobre
(complémentaires +5,2 %, non-salariés +8,2 %), la valeur de service de l'Agirc-Arrco le
20 octobre (de +5,2 à +6,3 %), chaque caisse divisée par les têtes de ses cas types le
24 octobre (complémentaires de +6,4 à +7,9 %, non-salariés de +7,5 à +10,8 %), l'artisan, le
libéral et le contractuel de l'Ircantec pesant plus en 2025, le COR faisant reculer la
dépense des exploitants — et `docs/limites/5-ter-trajectoire.md` : les polypensionnés, qu'une
grille de carrières à un seul régime ne représente pas, le COR multipliant les retraités de
la Cnav, de l'Ircantec, du RCI et de la CNAVPL plus vite que les personnes, et la grille par
pas de cinq générations.

## 5. Ce qui n'est pas fait, et sa déclaration

Déclarés, et conformes aux textes rouverts (fiche, approximations ; `docs/limites/3-systeme-actuel.md`,
« assiette de la complémentaire des artisans et des commerçants ») : **le minimum de la
cotisation** — le revenu minimum du régime de base jusqu'au 5 avril 2012, l'assiette de ce
régime dès quatre-vingt-dix jours d'affiliation, 5,25 % du plafond en 2015, rien en 2016 — ;
**le forfait du commerçant qui commence**, le modèle gardant le revenu de ses deux premières
années ; l'assiette inférieure sur demande motivée ; la reprise, le prorata, l'arrondi.

*a) Le conjoint collaborateur à une fraction du revenu du chef : non servi, non déclaré.*
D. 635-10-2 (LEGIARTI000006738041, du 13 décembre 2006 au 1er janvier 2013) assied sa
complémentaire sur « le revenu retenu [...] pour le calcul de sa cotisation d'assurance
vieillesse de base », et « La cotisation d'assurance complémentaire ne fait toutefois pas
l'objet de la régularisation à laquelle la cotisation d'assurance de base donne lieu le cas
échéant ». Aux options 2° à 5° de D. 633-19-2, une fraction du revenu du chef, cette cotisation de
base — les cotisations du conjoint « sont définies et recouvrées dans les conditions prévues
par la sous-section 1 » (D. 633-19-1, LEGIARTI000006737949) — est provisionnelle comme celle
du chef : « à titre
provisionnel, en pourcentage du revenu professionnel de l'avant-dernière année », puis
régularisée (L. 131-6, LEGIARTI000006740121, LEGIARTI000020169101) ; ses deux premières
années, « sur le revenu retenu pour le calcul des cotisations dues par le chef d'entreprise
pour ces années » (D. 633-19-6, LEGIARTI000006737955) ; à défaut de déclaration du chef,
« sur le même revenu que celui pris en compte pour la cotisation du chef d'entreprise,
retenu à hauteur de la fraction » (D. 633-19-7, LEGIARTI000006737957). Sans régularisation, sa
complémentaire reste donc assise sur la fraction du revenu du chef de l'avant-dernière année,
de 2007 à 2012, après 2009 encore ; et, s'il débute dans l'une des deux premières années de
l'artisan, sur les forfaits de D. 635-7 : « la cotisation de la première année est calculée
sur le revenu prévu au 1° de l'article D. 635-7 et celle de la deuxième année sur celui prévu
au 2° de ce même article », « à hauteur du pourcentage [...] correspondant à l'option ». Le
modèle sert l'assiette de l'année, que porte la ligne du conjoint (« le revenu de la ligne
est l'assiette que le conjoint a choisie », fiche `conjoint_collaborateur_independants`) :
juste au forfait du 1°, le seul que le test vérifie, pas aux options 2° à 5°. La fiche écrit
« sur l'assiette de sa cotisation de base, sans régularisation », et ni elle ni la limite ne
disent ce cas. Mineur : les seuls conjoints à une fraction du revenu du chef, de 2007 à 2012,
l'écart étant la croissance de ce revenu sur deux ans.

*b) Le forfait de l'artisan qui commence de 2009 à 2011 : une incertitude hors de la limite
publiée.* Depuis 2009, D. 635-2 calcule toute la cotisation « suivant les modalités prévues
au cinquième alinéa de l'article L. 131-6 » (LEGIARTI000020032159) — « à titre provisionnel,
en pourcentage du revenu professionnel de l'avant-dernière année ou des revenus
forfaitaires », puis « une régularisation » (LEGIARTI000020169101) —, quand D. 635-7
(LEGIARTI000017869802) assied toujours l'artisan qui commence sur un tiers puis la moitié du
plafond. Les deux lectures se tiennent : un forfait définitif, règle spéciale ; ou une base
provisionnelle, régularisée sur le revenu de l'année, comme le modèle traite celui du
commerçant de la même période. Le modèle le tient pour définitif. La session l'a vu (fiche,
`sources.a_relire` ; sa note, « Ce qui reste, déclaré »), mais ni les approximations de la
fiche ni `docs/limites/3-systeme-actuel.md` ne le portent. Mineur.

*c) Une date à préciser.* L'effet de la première approximation de la fiche dit le revenu
minimum « deux cents heures de Smic jusqu'en 2011 » : D. 633-2 le garde à « 200 fois le
montant horaire du salaire minimum de croissance » jusqu'au 5 avril 2012
(LEGIARTI000006737879), et D. 635-2 y renvoie jusqu'à la même date, comme l'écart de la même
approximation le dit.

## 6. Ce que la règle déplace

Refait ici : `construire_donnees.py` puis `construire_temoins.py` dans l'arbre sans les
quatre commits, comparé à 144a622 (`resumer_temoins.py --depuis 144a622`). Au scénario 1,
**31 témoins bougent**, la session les faisant baisser de 0,12 à 2,27 %, de 1,19 % en
médiane : le chiffre de la note, « 31 des 929 [...] de 0,1 à 2,3 % [...] en médiane 1,2 % »,
est **conforme** (930 témoins aujourd'hui).

*L'écart : un effet décrit à moitié.* La fiche dit que « Les témoins des artisans et des
commerçants perdent de 0,1 à 2,3 % de leur pension », la note « tous à la baisse ». Mais le
forfait élève les droits de l'artisan qui commence sous le tiers du plafond : le témoin
`dispense_rsa_releve_artisane` (née en 1962, artisane à 3 000 € par an depuis 1990) a, en 1990
et 1991, 145,71 et 220,09 points au lieu de 67,14 et 64,31, 18 % de points du RCO de plus ;
son total contributif du scénario 1 monte de 5,9 %, ce qu'absorbe le minimum vieillesse
(ASPA), différentiel, qui fait sa pension, et
sa pension des scénarios 3 et 5, qui convertissent les droits acquis, de 5,8 % — 32 témoins y
bougent, dont lui en hausse. C'est la règle du texte (la demande motivée qui l'abaisserait
restant une limite déclarée) ; l'effet est à écrire. Mineur, de documentation.

## Vu en chemin, hors du travail relu

- Le revenu de référence du NRCO de 2008 : l'IPP le donne à 14,648 € du 1er janvier 2007 et
  à 14,809 € du 1er décembre 2008 ; `valeurs_point.csv` prend le second pour toute l'année
  2008, la table de la caisse des commerçants étant un lien mort. Quel revenu de référence
  achète les points de 2008, aucun texte lu ne le dit.
- La caisse se contredit : l'exposé « Evolution des régimes complémentaires » convertit les
  points du RCO « par le biais d'un coefficient (0,2278) au 31/12/2005 », l'exposé « Points
  cotisés artisans avant 2013 » « par un coefficient de conversion d’une valeur de 0.2778 »
  au 1er janvier 2013 ; le dépôt prend 0,2778 (`conversions_points.csv`).
- Le plafond de 1982 change au 1er juillet (décrets n° 81-1164 et n° 82-543) ;
  `plafond_securite_sociale.csv` en garde la valeur annuelle, 12 504 €, « haute », que borne
  l'assiette du RCO de 1982.

## Ce qui reste

Déclarer, ou servir, le conjoint collaborateur à une fraction du revenu du chef (5, a) ;
porter l'incertitude du forfait de 2009 à 2011 dans la limite publiée et les approximations
de la fiche (5, b) ; compléter le commentaire de `tests/test_cout.py` (4) et l'effet de la
fiche (6) ; préciser la date du revenu minimum (5, c). Aucun ne touche les valeurs que les
tests vérifient.
