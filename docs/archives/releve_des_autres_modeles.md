# Le relevé des autres modèles, au 4 octobre 2026

*Un récit, gelé à sa date. Ce qui vit est au registre, `data/reference/referents.yaml`, que chaque relecture d'un modèle récrit ; l'étape et ce qu'elle a appris sont à la feuille de route, action 138, note du 4 octobre 2026.*

Le propriétaire a demandé, le 4 octobre 2026, « tout ce que notre modèle fait de moins bien comparé à chaque modèle », en prévenant qu'un écart ne prouve pas que le modèle public a raison : on en avait déjà vu d'erronés ou de périmés. Dix recherches menées en parallèle, une par famille, ont relu les soixante-neuf modèles du registre ; chaque point a été vérifié chez le modèle, dans le code du dépôt et contre le texte en vigueur ou la source officielle.

**Les rapports bruts**, tels que les dix recherches les ont rendus, avant leur intégration, sont dans le dossier `releve_des_autres_modeles/`, un fichier par famille. Ils gardent ce que le registre ne garde pas : les 29 points que la vérification n'a pas tenus, et leur raison (« pas meilleur », doublon, chiffre périmé) ; les verdicts sur les points déjà au registre ; la comparaison des barèmes de l'IPP famille par famille (`ipp.yaml`, clé `familles_ipp`) ; les séries d'OpenFisca-France confrontées à celles du dépôt (`openfisca.yaml`, clé `series_confrontees`) ; ce que chaque modèle a d'à jour (clé `a_jour`). Leurs numéros de ligne sont ceux du dépôt au commit `714ad0c`. À l'intégration, les points ont été rangés dans les étapes de l'action 138, dont cinq nouvelles (138.15 à 138.19) : c'est le registre, et non ces rapports, qui dit l'étape d'un point.

**La vue modèle par modèle**, ci-dessous, est tirée du registre au commit `73ecb32` : pour chaque modèle, son bilan, ce qu'il fait mieux que le dépôt, avec son état et son étape, et ses propres erreurs ou retards, chacun réduit à sa première phrase. La preuve et la vérification de chaque point sont au registre.

## L'IPP, OpenFisca, et ce qui s'y alimente

### Barèmes IPP (`baremes_ipp`)

**Bilan.** L'IPP a raison contre le dépôt sur des règles anciennes ou mal reconstruites : les dix dernières années avant 1973, les trimestres d'avant 1972, la réversion à 65 ans, l'assiette de l'AVPF, le revenu moyen des artisans et commerçants, la série du minimum contributif et l'IGRANTE de 1948. Ailleurs il est identique au dépôt, en retard (fonction publique, plusieurs séries de 2021 à 2025) ou faux (dix écarts). Le barème de la Cnav, accessible par API, tranche presque tous les cas mieux que lui.

**Ce qu'il fait mieux que le dépôt :**
- Il porte les séries de l'AVTS (1962-2026, 4 023,51 € en 2025) et de l'allocation supplémentaire d'une personne seule (1956-2022). *(à reprendre, étape 138.6)*
- Il porte la pension majorée de référence des exploitants agricoles de 2009 à 2026 ; *(à reprendre, étape 138.8)*
- Il porte le salaire qui valide un trimestre outre-mer, plus bas qu'en métropole de 1948 à 1951 et de 1972 à 1995 : en 1980, 1 897,5 F à La Réunion et 2 112 F aux Antilles et en Guyane, contre 2 586 F. *(à reprendre, étape 138.6)*
- Avant 1973, le salaire de base du régime général était la moyenne des dix DERNIÈRES années, pas des dix meilleures. *(à reprendre, étape 138.16)*
- Avant 1972, un trimestre se validait par un montant. *(à reprendre, étape 138.6)*
- Avant 1973, la réversion du régime général s'ouvrait à 65 ans, ou 60 en cas d'inaptitude. *(à reprendre, étape 138.4)*
- L'IPP a trois tables anciennes des coefficients de revalorisation des salaires portés au compte : arrêtés de 1949, de 1952 et du 24 janvier 1994 (salaires de 1947 à 1992). *(à reprendre, étape 138.16)*
- L'IPP a la série complète du minimum contributif : chaque revalorisation de 1984 à 2023, le minimum majoré de 2004 à 2023, le plafond de 2012 à 2023. *(à reprendre, étape 138.15)*
- L'IPP a l'assiette publiée de l'AVPF de 1972 à 2021, en métropole et outre-mer (plus basse aux Antilles et à La Réunion jusqu'en 1995) : 169 heures de SMIC par mois, au SMIC du 1er juillet de l'année précédente, soit 1 715,35 € … *(à reprendre, étape 138.16)*
- Pour les artisans et commerçants, le revenu annuel moyen passe de 10 à 25 années plus lentement que chez les salariés : 11 années pour les générations 1934-1935 … 24 pour 1952, et 25 seulement dès 1953. *(à reprendre, étape 138.16)*
- L'IPP a la majoration pour conjoint à charge de 1948 à 2002 et son plafond de ressources : 14 500 AF en 1948, 36 190 AF en 1956 (la moitié de l'AVTS), 4 000 F en 1976, puis 609,80 €. *(à reprendre, étape 138.17)*
- L'IPP a des coefficients d'anticipation et de majoration d'ajournement pour l'Agirc avant 1955 et l'Arrco avant 1965. *(à reprendre, étape 138.16)*
- Pour 1948, l'IPP donne le bon salaire de référence de l'IGRANTE et de l'IPACTE : 0,37 F, soit 0,0564 €. *(à reprendre, étape 138.16)*
- L'IPP a le minimum de réversion de 1964 à 2021 et le plafond de la majoration de 11,1 % de 2010 à 2025. *(à reprendre, étape 138.4)*
- L'IPP a la valeur de service des points acquis avant 1973 au régime de base des commerçants (1949-2019) et des artisans (1973-2019, puis rsi_vp jusqu'en 2021). *(à reprendre, étape 138.18)*
- L'IPP a l'ASPA d'un couple de 2006 à 2026, les plafonds de ménage de l'AVTS et de l'allocation supplémentaire depuis 1956, et l'abattement sur les revenus d'activité (0,9 et 1,5 SMIC depuis 2015). *(à reprendre, étape 138.2)*
- L'IPP a le point de la CNRO (PRO BTP) de 1960 à 1998, l'institution Arrco des ouvriers du bâtiment. *(à trancher)*
- L'IPP a l'histoire des prélèvements sur les pensions : cotisation maladie de 1 % à 2,8 % de 1980 à 1997 (2 % puis 3,8 %, puis 1 % sur les complémentaires) ; *(à reprendre, étape 138.9)*

**Ses erreurs ou retards (13) :**
- Le taux de cotisation des chirurgiens-dentistes s'y arrête en 2019, quand la caisse l'a changé en 2023.
- Ses seuils de CSG des pensions s'arrêtent au 1er janvier 2025 : aucun pour 2026.
- Sa cotisation maladie d'Alsace-Moselle y reste à 1,5 %.
- E1. Dans la table de l'arrêté du 24 janvier 1994, le coefficient des salaires de 1957 vaut 11,875 (reval_s_49/arrete_24_01_1994_jo_27_01_1994.yaml:25-26), entre 24,59 pour 1956 et …
- E2. Le minimum contributif de 636,56 € est daté du 1er octobre 2019 (montant_mico.yaml:105), alors que l'IPP cite lui-même la circulaire Cnav 2019/4 du 9 janvier 2019.
- E3. La décote de la fonction publique vaut 0,65 % par trimestre pour l'année 2010 (secteur_public/pension_civile/decote.yaml:66-70).
- E4. La PMR est entièrement calculée par l'IPP de 2010 à 2026 (independants/pmr_msa.yaml, notes) : indexée sur les prix jusqu'en 2020, en baisse en 2015 (8 075,55 €, lignes …
- E5. Pour l'Agirc de 1947 à 1955, l'IPP reprend les coefficients de l'Arrco (0,95 à 64 ans … 0,75 à 60 ans) et met 1,05 dès 65 ans (agirc/coefficient_de_minoration.yaml:63-69, …
- E6. La fonction publique s'arrête en 2012-2014 : âges d'ouverture et limites d'âge (aod_a, aod_s, la_a, la_s : dernière législation au 1er janvier 2012), durées (trimtp, 2014). On …
- E7. Les coefficients de solidarité et majorants de l'Agirc-Arrco s'appliquent depuis 2019 sans date de fin (regimes_complementaires/coeff_temp.yaml).
- E8. Le nombre d'années du salaire annuel moyen s'arrête aux 25 années de la génération 1948 (sam.yaml, dernière législation en 2008).
- E9. Plusieurs séries s'arrêtent avant 2026 : minimum contributif (1er septembre 2023), minimum de réversion (2021), plafond de la majoration de réversion et plafond de ressources …
- E10. L'IPP date de 1972 (loi n° 71-1132) le passage aux dix meilleures années (sam.yaml, valeur au 1er janvier 1972).

### OpenFisca-France (`openfisca_france`)

**Bilan.** Il fait mieux sur tout ce qui sépare la pension brute du revenu du retraité — CSG selon le revenu fiscal, ASPA du couple, impôt avec ses abattements — et sur les montants historiques du minimum vieillesse et des avantages d'avant 2011. Il ne calcule pas la pension ; ses séries de plafond, de SMIC et de point d'indice sont celles du dépôt, à l'euro, et sa CSG d'avant 2015 est fausse.

**Ce qu'il fait mieux que le dépôt :**
- Il calcule la CSG, la CRDS et la CASA des pensions selon le revenu fiscal de référence de N−2 et le nombre de parts. *(à reprendre, étape 138.2)*
- Il sert l'ASPA d'un couple sous le plafond du couple (19 442,21 €), sur les ressources des trois derniers mois, salaires abattus de 0,9 ou 1,5 SMIC, comme le veulent L. *(à reprendre, étape 138.2)*
- Il calcule l'impôt sur le revenu des retraités : abattement de 10 % des pensions (454 € par pensionné au moins, 4 439 € par foyer au plus, revenus de 2025), abattement des contribuables de 65 ans ou invalides, parts, décote. *(à reprendre, étape 138.5)*
- Il porte le minimum vieillesse d'avant l'ASPA : AVTS (1962-2022), allocation supplémentaire d'une personne seule (1956-2022) et d'un ménage (1982-2022), leurs plafonds, le complément exceptionnel, l'AVTS d'avant 1961 par taille … *(à reprendre, étape 138.6)*
- Il porte la majoration pour conjoint à charge (4 000 F par an depuis 1976, 609,80 € depuis 2002) et le plafond de ressources du conjoint jusqu'en 2022. *(à reprendre, étape 138.17)*
- Il oppose à l'ASPA et à l'ASI la condition de séjour de dix ans de l'étranger hors Espace économique européen et Suisse. *(à trancher)*
- Il calcule l'ASI, minimum des pensionnés d'invalidité avant l'âge de l'ASPA. *(écarté)*

**Ses erreurs ou retards (5) :**
- Sa CSG des pensions ignore le lissage — le taux de 3,8 % reste dû si le revenu fiscal de référence de N−2 ou de N−3 ne dépasse pas le second seuil —, les seuils des DOM, qu'il ne …
- La cotisation maladie de 1 % des pensions complémentaires est paramétrée (`regimes_comp.yaml`, sous `mmid_ret/`), mais aucune variable ne la lit.
- La cotisation maladie d'Alsace-Moselle des salariés y reste à 1,5 % (`maladie_alsace_moselle.yaml:35-36`, appliquée par `travail_prive.py:831-841`).
- Avant 2015, sa CSG et sa CRDS des pensions sont au taux plein pour tous (`remplacement.py:333-338, 399-404, 461-466`, formules « à corriger », dit-il).
- Sa condition de nationalité de l'ASPA omet les réfugiés, apatrides, bénéficiaires de la protection subsidiaire et anciens combattants, et l'attestation par les périodes …

### OpenFisca-France-Pension (`openfisca_france_pension`)

**Bilan.** Ce qu'il fait de mieux tient à des paramètres datés texte par texte que le dépôt projette ou ignore — d'abord le minimum contributif, dont le dépôt sert la majoration et l'écrêtement avant leur création —, et à quelques règles qui manquent au dépôt (seuil de validation d'avant 1972, salaire moyen sur années validantes, minimum de réversion, catégories de L. 351-8). Il reste borné à cinq familles de régimes, arrêté à la loi de 2023, et faux sur le minimum surcoté, la majoration de durée et la revalorisation de 2020.

**Ce qu'il fait mieux que le dépôt :**
- Il code le départ anticipé des fonctionnaires parents de trois enfants — trois enfants et quinze ans de services réunis avant 2012 — et, selon les dates, la décote de l'année où les conditions l'ont été plutôt que celle de la … *(à reprendre, étape 136.3)*
- Sa quotité de travail réduit les services sans réduire la durée d'assurance. *(à reprendre, étape 136.3)*
- Il calcule, et le plus souvent teste, la majoration de durée et la bonification pour enfants, la majoration de 10 %, les points enfants de l'Arrco, la catégorie active, la carrière longue de la fonction publique, les minima … *(à reprendre, étape 136.2)*
- Il rend, pour toute simulation, chaque variable calculée, sa valeur, et les variables et paramètres qu'elle a lus ; *(à reprendre, étape 136.4)*
- Il calcule une population d'un coup, en vecteurs, et sa documentation dit l'avoir essayé sur les données de Destinie et sur l'EIR 2012, au régime général et à l'Arrco ; *(à reprendre, étape 136.6)*
- `openfisca serve` expose `/calculate`, `/trace`, `/variables`, `/parameters` et une description OpenAPI (`/spec`) ; *(à reprendre, étape 136.5)*
- Il écrit chaque règle une fois, dans un moteur Python que d'autres appellent ; *(écarté)*
- Il date le minimum contributif texte par texte : montants de 1984 à 2023 à chaque revalorisation, majoration créée en 2004, condition des 120 trimestres cotisés pour les seules pensions d'avril 2009 et après, écrêtement en 2012 … *(à reprendre, étape 138.15)*
- Il valide les trimestres d'avant 1972 au seuil de R. *(à reprendre, étape 138.6)*
- Depuis 2004, son salaire annuel moyen ne retient que les années dont le salaire valide au moins un trimestre. *(à reprendre, étape 138.16)*
- Il porte le minimum de réversion du régime général de 1964 à 2021 (3 492,37 € par an en 2021). *(à reprendre, étape 138.4)*
- Il porte, en entrée, les taux pleins par catégorie de L. *(à reprendre, étape 138.17)*
- Il borne la pension du régime général à la moitié du plafond, surcote en sus. *(à reprendre, étape 138.17)*
- Il sert la majoration de l'Agirc-Arrco pour enfants à charge, 5 % par enfant, quand elle passe celle des enfants nés ou élevés. *(à reprendre, étape 138.17)*
- Il porte la valeur de service des points d'avant 1973 des artisans (CANCAVA, 1973-2019) et des commerçants (ORGANIC, 1949-2019). *(à reprendre, étape 138.18)*
- Il porte le seuil de validation des Antilles-Guyane et de La Réunion, plus bas qu'en métropole de 1948 à 1995 (en 1980 : 2 112 F et 1 897,5 F contre 2 586 F). *(à reprendre, étape 138.6)*

**Ses erreurs ou retards (15) :**
- Ses coefficients de revalorisation des salaires portés au compte s'écartent de la table de la Cnav : de −3 à −5,5 % après 1990, faute de la revalorisation de 4 % du 1er juillet …
- Sa décote de la pension civile porte 0,65 % pour l'année d'ouverture 2010, là où la loi écrit 0,625 % ;
- Son Agirc ne suit ni le taux d'appel de 1989 ni le contractuel de 1994, fait cotiser la tranche C par le salarié dès l'origine, et lit le prix d'achat au 1er janvier, un millésime …
- Son Ircantec porte l'assiette de la tranche B à huit plafonds dès 1992, quand le décret n° 2008-996 le fait au 25 septembre 2008.
- Son régime unifié Agirc-Arrco ne s'exécute pas : le code demande un paramètre que les barèmes livrés ne définissent pas.
- Chez nous, la durée de proratisation était confondue avec la durée requise, que R.
- Chez nous, la décote de L. 14 se lisait à l'année de liquidation et non d'ouverture du droit, et la montée en charge 2004-2008 de la durée de services était ignorée.
- Sa durée requise et son âge d'ouverture s'arrêtent à la loi de 2023 : 171 trimestres et 63 ans à la génération 1964, 172 trimestres et 63 ans et 3 mois à 1965 …
- Depuis avril 2009, son minimum contributif multiplie le minimum par (1 + surcote) (`regimes/regime_general_cnav.py:959-962`).
- Sa majoration de durée au-delà de l'âge du taux plein prend le taux de décote de la génération, 1,25 % par trimestre dès 1953, et court dès l'âge d'annulation de la catégorie, 60 …
- Il sert le taux plein à 60 ans à tout ancien combattant dès 1975 (`aad.yaml:246-262`) ;
- Sa revalorisation des pensions de 2020 est uniforme, 0,3 %, et sa série s'arrête en 2024 (`regime_general_cnav/revalorisation_pension.yaml`).
- De janvier 2004 à juin 2005, il proratise la majoration du minimum contributif sur la durée cotisée (`regimes/regime_general_cnav.py:988`).
- Ses points des indépendants ont des fautes de saisie : la valeur ORGANIC du 1er avril 2011 reprend celle de la CANCAVA, 8,8124 € au lieu d'environ 12,15 € …
- Avant 1983, son minimum de pension lit `prestations_sociales.…avts_av_1961` (`regimes/regime_general_cnav.py:1017-1020`), que le paquet ne livre pas : `parameters/` n'a que …

### LexImpact (simulateur socio-fiscal) (`leximpact`)

**Bilan.** Rien sur la pension elle-même : il hérite d'OpenFisca-France, déjà relu. Ses avantages propres sont des ménages types de retraités, la veille des projets et des décrets, et un chiffrage sur données que le dépôt ne peut pas reproduire ; son dépôt de réformes pour 2027 est en chantier.

**Ce qu'il fait mieux que le dépôt :**
- Il code les projets de loi pour 2027 dès leur dépôt : le sous-plafond de 3 000 € par foyer de l'abattement des pensions (PLF 2027, art. *(à reprendre, étape 138.12)*
- Il décrit seize ménages de retraités rangés par décile de niveau de vie, chacun situé par sa part dans le décile : couples du 2e au 9e décile, célibataires du 4e au 6e, trois cas pour les trois taux de CSG, deux pour l'ASPA (une … *(à reprendre, étape 138.2)*
- Il tient, avec l'Assemblée nationale, un baromètre de la parution des décrets d'application, loi par loi. *(à reprendre, étape 138.12)*
- Il chiffre l'effet budgétaire des mesures sur les ménages, pensions comprises, sur l'ERFS-FPR vieillie et calée. *(écarté)*

**Ses erreurs ou retards (1) :**
- Sa réforme `plf_plfss_2027` date du 1er janvier 2026 un barème de revalorisation des retraites à trois tranches, 0,9 % sous 1 260 €, 1 % jusqu'à 2 034 €, 0 % au-delà …

### TAXIPP (`taxipp`)

**Bilan.** Microsimulation statique sur données administratives, il ne calcule pas la pension ; ce qu'il fait de mieux tient à ses données — un taux de CSG tiré du revenu fiscal réel, un recours à l'ASPA calé sur les allocataires observés. Le reste exige le CASD.

**Ce qu'il fait mieux que le dépôt :**
- Il calcule un prélèvement effectif sur les pensions, tiré du revenu fiscal de référence réel de Félin. *(à reprendre, étape 138.3)*
- Il cale le recours à l'ASPA, année par année, sur le nombre d'allocataires que publie la DREES (722 510 fin 2023), en tirant les recourants parmi les éligibles, et confronte nombre et masse d'ASPA aux agrégats officiels. *(à reprendre, étape 138.3)*
- Il mesure les effets redistributifs d'une mesure par décile, sur données fiscales et sociales appariées. *(écarté)*

**Ses erreurs ou retards (2) :**
- Son taux de CSG des pensions vient d'un seul revenu fiscal de référence, sans le lissage sur N−3.
- Le passage de la pension imposable à la pension brute oublie la cotisation maladie de 1 % des complémentaires.

### TIL (TaxIPP-Life) et Til-Pension (`til_pension`)

**Bilan.** Til-Pension couvre le régime général, le RSI, la fonction publique, l'Agirc et l'Arrco avec le droit de 2014. Il n'a ni réversion, ni régimes spéciaux, ni minimum garanti (Fonction_publique.py:204-205), et confie l'ASPA à OpenFisca (regime_prive.py:164) ; til-france ne calcule plus de pension dans sa dernière version. Son seul apport propre est la majoration de l'Agirc-Arrco pour enfants à charge ; pour l'AVPF, il confirme l'assiette des barèmes IPP.

**Ce qu'il fait mieux que le dépôt :**
- Il sert la majoration de l'Agirc et de l'Arrco pour enfants À CHARGE, 5 % des points par enfant, et retient la plus forte de celle-ci ou de la majoration pour enfants nés ou élevés (regime.py:234-272 ; *(à reprendre, étape 138.17)*
- Il prend pour l'AVPF l'assiette mensuelle publiée, multipliée par douze (trimesters_functions.py:42-52 ; *(à reprendre, étape 138.16)*

**Ses erreurs ou retards (2) :**
- Il valide un trimestre pour 200 heures de SMIC dès 1945 (param.xml:1153-1156).
- Sa législation s'arrête en 2014 : le SMIC de 2014 (9,53 €) vaut « jusqu'en 2100 » (param.xml, deb="2014-01-01" fin="2100-12-01").

### PENSIPP (`pensipp`)

**Bilan.** PENSIPP couvre le régime général, la fonction publique, l'Agirc, l'Arrco et les indépendants avec le droit de 1946 à 2011. Il ne calcule pas la réversion (variables rev_* seulement revalorisées, OutilsRetr.R:763-799) et laisse le minimum vieillesse en commentaire (:745, :795). Il ne fait mieux que le dépôt sur aucune règle en vigueur : ses apports sont des choix de programme (comportement de départ, crédits non cotisés dans le compte, diviseur avec gain d'héritage) et des contrefactuels par millésime de législation.

**Ce qu'il fait mieux que le dépôt :**
- Il code quatre règles de départ : au taux plein ; *(à trancher)*
- Ses comptes notionnels peuvent créditer des périodes non cotisées, chaque crédit étant désactivable par une option : le chômage (cotisation sur le dernier salaire, entre le SMIC et 4 plafonds) ; *(à trancher)*
- La fonction UseLeg(Leg, g) applique à une génération le barème que prévoyait la législation d'une année donnée, par exemple « UseLeg(1992,1942) » (OutilsLeg.R:30-49, :69-140). *(à reprendre, étape 138.10)*
- Son coefficient de conversion vaut S(40)/Σ(1+g)^(a−u)·S(u), calculé sur une table de mortalité du moment, hommes et femmes additionnés (OutilsCN.R:57-80). *(à trancher)*

**Ses erreurs ou retards (2) :**
- Son salaire de base est toujours la moyenne des meilleures années, avant 1973 compris (OutilsRetr.R:209-230).
- Sa législation s'arrête en 2011-2012 (OutilsLeg.R, branche Leg >= 2011 ;

## La statistique publique : l'INSEE

### Destinie 2 (`destinie_2`)

**Bilan.** Au-delà de la réversion et de l'ASPA du ménage, il fait mieux par ses séries annuelles longues (minimum contributif depuis 1984, minimum vieillesse depuis 1970, AVPF à 169 heures), là où le dépôt projette des ancres ou déduit, et par quatre règles du scénario 1 qui nous manquent (AVPF dans le minimum depuis 2023, départ des fonctionnaires parents de trois enfants, versement forfaitaire unique, plafond de L. 18). Il a tort sur onze points, outre la loi du 30 décembre 2025 : CSG à 6,6 %, coefficient de solidarité après avril 2024, ressources et taux historique de la réversion, Ircantec, complémentaire des indépendants.

**Ce qu'il fait mieux que le dépôt :**
- Il calcule la réversion du régime général entière : minimum proratisé sous quinze ans et maximum, majoration de 10 % du survivant de trois enfants, réversion d'un assuré mort avant son départ, plafond de ressources du ménage, … *(à reprendre, étape 138.4)*
- Il sert l'ASPA au ménage, sur ses ressources, celles du conjoint comprises. *(à reprendre, étape 138.2)*
- Il importe les variantes démographiques de l'INSEE — fécondité, espérance de vie, migrations, « central, bas, haut » —, en 64 jeux. *(à reprendre, étape 138.7)*
- Il lit les quotients de mortalité projetés de l'INSEE par sexe, âge et année, et s'en sert tels quels. *(à reprendre, étape 138.7)*
- Il calcule un taux de rendement interne des cotisations ; *(à reprendre, étape 138.9)*
- Il porte le minimum contributif de chaque année depuis 1984 et son majoré depuis 2004, avec la règle de chaque époque : pas de majoration avant 2004, majoration sans seuil de 2004 à mars 2009, seuil de 120 trimestres ensuite. *(à reprendre, étape 138.15)*
- Il porte le minimum vieillesse de chaque année depuis 1970, seul et en couple. *(à reprendre, étape 138.6)*
- Pour les pensions prenant effet depuis septembre 2023, il compte l'AVPF, jusqu'à six ans, dans le seuil de 120 trimestres et dans le prorata de la majoration du minimum contributif. *(à reprendre, étape 138.15)*
- Il porte au compte, pour une année d'AVPF, 2 028 heures de SMIC de l'année précédente (169 heures par mois). *(à reprendre, étape 138.16)*
- Il ouvre la liquidation anticipée du fonctionnaire parent de trois enfants qui a quinze ans de services avant 2012, avec la durée et la décote de l'année des conditions s'il était à moins de cinq ans de son âge d'ouverture en … *(à reprendre, étape 138.17)*
- Il remplace la petite pension du régime général par un versement forfaitaire unique de quinze annuités jusqu'en 2015, et celle de l'Arrco (moins de 100 points) et de l'Agirc (moins de 500) par un capital jusqu'en 2018. *(à reprendre, étape 138.17)*
- Il plafonne la pension civile majorée pour enfants au traitement de référence. *(à reprendre, étape 138.17)*
- Il calcule la retraite nette : CSG, CRDS et CASA nulles, au taux réduit ou au taux plein selon les ressources du foyer et des seuils à une et deux parts, plus 1 % de cotisation maladie sur les complémentaires. *(à reprendre, étape 138.2)*
- Il applique le coefficient de solidarité de l'Agirc-Arrco aux liquidations de 2019 à 2023 (10 % trois ans au plus, jusqu'à 67 ans ; *(à trancher, étape 138.13)*
- L'Insee y a simulé en 2025 l'indexation des droits sur les salaires, avec correcteur démographique ou correcteur tenant les retraites/PIB, et en publie l'effet jusqu'en 2070 sur les retraites/PIB, la pension relative et la … *(à trancher, étape 138.13)*
- Il simule une population (naissances, unions, séparations, migrations, décès calés sur l'Insee ; *(à reprendre, étape 138.14)*

**Ses erreurs ou retards (17) :**
- Il lève au régime général la condition d'âge de 55 ans de la réversion pour le survivant qui a deux enfants à charge (`src/Retraite.cpp:224-229`).
- Tout couple simulé y est marié (`src/Separations.cpp:189-190` ;
- La majoration de la réversion pour enfant à charge lui manque ;
- Quand un seul membre du couple a 65 ans, il sert l'ASPA jusqu'au barème du couple (`src/Retraite.cpp:12-30`).
- Sans la loi du 30 décembre 2025, il ouvre les droits de la génération 1964 à 63 ans et lui demande 171 trimestres (`src/Legislation.cpp:57-59`).
- Il projette l'ASPA de 2025 à 12 493,58 € par an.
- Il réserve la majoration de durée d'assurance pour enfants et la surcote parentale aux mères, celle-ci dès 1964 (`src/DroitsRetr.cpp:172`, `src/Legislation.cpp:246-250`).
- Pour le polypensionné des régimes alignés d'avant la liquidation unique, il garde le même nombre d'années dans chaque régime : `max(1, arr(durée du régime / durée totale))` vaut …
- Sous le plafond de la réversion du régime général, il compte les réversions de l'Agirc-Arrco, et deux fois la réversion du RG pour le survivant qui n'a pas liquidé …
- Il sert 54 % de réversion au régime général dès 1975 (ParamRev, colonne TauxRevRG).
- Il garde le coefficient de solidarité jusqu'à son terme pour les retraites prises avant décembre 2023 (`src/Retraite.cpp:151-178`).
- Sa CSG sur les retraites n'a que 4,3 % et 9,1 % (CRDS et CASA comprises), seuils arrêtés en 2018 (ParamAutres, TauxCSGRet*, SeuilExoCSG*).
- Il inscrit les contractuels de droit public à l'Arrco, ce que son code dit « à corriger » (`src/DroitsRetr.cpp:667, 701`, `src/Cotisations.cpp:194`).
- Il ne sert aux indépendants aucune complémentaire : ses points ne naissent que d'un statut salarié (`src/DroitsRetr.cpp:666-667, 698-702`).
- Par défaut, il revalorise le plafond d'écrêtement des minima (1 120 € par mois en 2014) sur les prix (`src/DroitsRetr.cpp:1087-1097`).
- Il écrête le minimum garanti avec le minimum contributif, et le refuse à qui n'a pas tout liquidé ensemble (`src/DroitsRetr.cpp:1109-1124`).
- Sa série porte 24 000 F de minimum vieillesse pour une personne seule en 1982 (ParamRetrBase).

### Destinie 1 (`destinie_1`)

**Bilan.** Rien de mieux : code non public, résultats d'un droit (réforme de 1993) et d'un échantillon (enquête Actifs financiers de 1991) anciens. Destinie 2 l'a remplacé en 2010 et en reprend les fonctions.

### Ines (`ines`)

**Bilan.** Ines fait mieux que le dépôt sur tout ce qui entoure la pension d'un retraité : le net selon le RFR et les parts, le 1 % des complémentaires, l'ASPA du couple sur les ressources du foyer et hors des prélèvements, l'impôt, le barème de l'ASPA daté. Il ne fait rien sur la pension elle-même ni sur la réversion, qui sont des données. Deux de ses paramètres sont faux : l'abattement de l'ASPA de 2026 et une part complémentaire de 2020.

**Ce qu'il fait mieux que le dépôt :**
- Il fixe le taux de CSG des pensions selon le revenu fiscal de référence et le nombre de parts ; *(à reprendre, étape 138.2)*
- Il prélève la cotisation maladie de 1 % sur les retraites complémentaires du privé (D. *(à reprendre, étape 138.2)*
- Il sert l'ASPA d'un couple sous le plafond du couple, sur des ressources qui comptent les revenus d'activité abattus et le patrimoine, et ne sert au membre seul éligible que le montant d'une personne seule. *(à reprendre, étape 138.2)*
- L'ASPA reste hors de l'assiette de la CSG, de la CRDS et de la CASA : il calcule ces prélèvements sur les pensions seules, puis l'ASPA. *(à reprendre, étape 138.2)*
- Il calcule l'impôt sur le revenu des pensions : abattement de 10 %, avec un plancher par pensionné et un plafond par foyer ; *(à reprendre, étape 138.5)*
- Il tient le barème de l'ASPA au mois depuis janvier 2021, 1er juillet 2022 compris. *(à reprendre, étape 138.2)*
- Il cale le recours à l'ASPA par type de ménage, par tirage sur les effectifs servis : personnes seules, couples à un et à deux allocataires (442 756, 107 923 et 12 164 en 2024). *(à reprendre, étape 138.14)*
- Il sert l'ASI aux invalides avant l'âge de l'ASPA, seuls ou en couple. *(à trancher)*
- Il impose les rentes viagères à titre onéreux sur une fraction fixée par l'âge : 70, 50, 40 ou 30 %. *(écarté)*

**Ses erreurs ou retards (4) :**
- Il fait payer la cotisation maladie de 1 % aux pensions exonérées de CSG : `case_when(exo_csg == 1 ~ coprmal, reduc_csg == 1 ~ 0, …)` (`R/12_cotisations.R:2016-2017`).
- L'exonération de CSG des pensions des allocataires de l'ASPA lui manque, « écart à la législation » qu'il déclare (`R/12_cotisations.R:2006-2010`).
- abat_aspa_celib et abat_aspa_couple valent 0 en janvier 2026 (param_presta_mensuel.xlsx, Minima, l.
- retrCP_t5, la part complémentaire des anciens cadres du dernier quintile, vaut 64,9 pour 2020, contre 0,65 les autres années (param_prelev.xlsx, onglet Imput, l.

## La statistique publique : la DREES

### TRAJECTOiRE (`trajectoire`)

**Bilan.** Ce qu'il fait de mieux tient à la population et aux chroniques : une microsimulation qui chiffre coût et redistribution, des départs modélisés, des indicateurs de cycle de vie ; et, au scénario 1, des règles que le dépôt n'a pas, de la majoration exceptionnelle de 2023 aux versements uniques des complémentaires, aux bonifications de service et aux minima des exploitants. Sa version publique est à jour de la loi du 14 avril 2023 et de ses décrets d'août 2023, non de la loi du 30 décembre 2025 ; ses valeurs sont réelles jusqu'en 2024 et projetées ensuite, son coefficient de solidarité et son VFU de la Cnav ne s'éteignent jamais.

**Ce qu'il fait mieux que le dépôt :**
- Il calcule, par cas type et génération, les taux de récupération, de remplacement sur le cycle de vie et d'annuité, la durée de retraite rapportée à la carrière, le TRI, la pension nette rapportée à l'ASPA, et le remplacement net … *(à reprendre, étape 138.9)*
- Il refait les treize cas types du COR sans les données du CASD. *(à reprendre, étape 138.4)*
- Il lit les variantes de fécondité et d'espérance de vie de l'INSEE ; *(à reprendre, étape 138.7)*
- Il impute aux cas types du COR le taux de CSG de la convention du COR : réduit pour le 2 bis, médian pour les 2 à 5 et 8 à 10, normal pour les 1, 6, 7 et 11. *(à reprendre, étape 138.2)*
- Depuis septembre 2023, il compte les trimestres d'AVPF parmi les 120 trimestres cotisés qui ouvrent la majoration du minimum contributif, et dans sa proratisation. *(à reprendre, étape 138.15)*
- Il sert, dans la chronique des pensions, la majoration exceptionnelle due depuis le 1er septembre 2023 aux pensions du régime général et des salariés agricoles liquidées avant cette date au minimum contributif. *(à reprendre, étape 138.17)*
- Il sert aux exploitants la pension majorée de référence et le complément différentiel de la RCO, et les relève aussi pour les pensions déjà liquidées. *(à reprendre, étape 138.8)*
- Il applique les coefficients temporaires de l'Agirc-Arrco aux liquidations depuis 2019 des générations 1957 et suivantes : 10 % de minoration pendant trois ans au plus et jusqu'à 67 ans, 5 % au taux réduit de CSG, aucune pour les … *(à trancher)*
- Il verse en capital les petites complémentaires : à l'Agirc-Arrco jusqu'à 100 points (pension annuelle × coefficient de l'âge), à l'Ircantec sous 300 points (points × salaire de référence). *(à reprendre, étape 138.17)*
- Ses cas types servent la bonification du cinquième au super-actif (quatre trimestres par cinq ans de services, vingt au plus) et la majoration de durée d'assurance d'un an pour dix ans à l'hospitalier de catégorie active, sur le … *(à reprendre, étape 138.17)*
- Sa microsimulation range chaque retraité dans l'un des quatre taux de CSG d'après sa pension, prise pour seule ressource, abattement de 10 % compris, contre les seuils de revenu fiscal de l'année, et retire la cotisation maladie … *(à reprendre, étape 138.2)*
- Il projette l'âge de départ que le COR publie : âge conjoncturel de 63,1 ans en 2025 et de 64,6 ans à partir des années 2040 ; *(à reprendre, étape 138.3)*
- Il chiffre une réforme sur une population : 750 000 carrières de l'EIC prolongées, calées sur les cotisants par régime et le chômage du COR, salaires bruités, tous niveaux de revenu, avec masses de cotisations et de prestations … *(à reprendre, étape 138.14)*
- Il modélise les départs : probabilité de liquider à chaque trimestre entre l'âge d'ouverture et 70 ans selon la distance au taux plein, la caisse, le sexe (logistique estimée sur l'EIR), non-recours à la carrière longue, … *(à trancher)*
- Il retire du salaire annuel moyen, depuis 2004, les années sans trimestre cotisé ; *(à reprendre, étape 138.16)*

**Ses erreurs ou retards (8) :**
- Sans la loi du 30 décembre 2025, il ouvre les droits de la génération 1964 à 63 ans et lui demande 171 trimestres (`inst/extdata/trajectoire/ageDuree.csv:144-148, 515-516`).
- Il garde le versement forfaitaire unique de la Cnav et des salariés agricoles après 2016, sans condition de date (R/fonctionsCalculsPensions.R:3296-3306), « Il a temporairement …
- Ses coefficients temporaires de l'Agirc-Arrco valent pour toute liquidation depuis 2019, projections comprises, sans fin (R/fonctionsCalculsPensions.R:3222, 3236-3249).
- Sa revalorisation de 2020 (revaloSpeciale2020, R/fonctionsCalculsPensions.R:3647-3664) ignore la zone de lissage de 2 000 à 2 014 €, comme calcul_pension ;
- Il partage les années du SAM entre régimes alignés à l'arrondi inférieur (floor, R/fonctionsCalculsPensions.R:2105).
- Il compte tous les trimestres d'AVPF au seuil et dans la proratisation de la majoration du minimum contributif (R/fonctionsCalculsPensions.R:2835-2841).
- Ses paramètres réglementaires (inst/extdata/trajectoire/*.csv) s'arrêtent en 2020-2022 (valeurPtService.csv en 2020, revalo.csv en juillet 2022, pmr.csv en janvier 2020, avts.csv …
- Sa garantie minimale de points de l'Agirc vient de la série IPP, 144 points dès 1947 et 120 dès 1997 (R/1-lecture-ipp.R:274-278, gmp.yaml de seriesIPP.Rds), qui remplace un CSV …

### calcul_pension (paquet R calculPension) (`calcul_pension`)

**Bilan.** C'est le moteur de TRAJECTOiRE figé en janvier 2023 et, selon la DREES, la réécriture en R de CALIPER : il fait mieux que le dépôt sur les minima des exploitants et sur le salaire annuel moyen depuis 2004, et porte les règles de TRAJECTOiRE. Sa législation est celle de la loi du 20 janvier 2014, ses paramètres s'arrêtent en 2022 ; ses écarts sont ceux de TRAJECTOiRE, plus la CSG des salaires prélevée sur les pensions.

**Ce qu'il fait mieux que le dépôt :**
- Il sert aux exploitants agricoles la pension majorée de référence, proratisée et écrêtée au niveau de l'ASPA, et le complément différentiel de la RCO, qui relève au seuil le total tous régimes (`dureeValidee>=70 & aTauxPlein`). *(à reprendre, étape 138.8)*
- Il retire du salaire annuel moyen les années sans trimestre cotisé, pour les liquidations depuis 2004. *(à reprendre, étape 138.16)*
- Il porte déjà, figées en janvier 2023, les règles de TRAJECTOiRE que le dépôt n'a pas : coefficients temporaires de l'Agirc-Arrco, versements uniques de l'Agirc-Arrco et de l'Ircantec, bonification du cinquième et majoration d'un … *(à reprendre, étape 138.17)*

**Ses erreurs ou retards (4) :**
- Sa pension nette (`calculePensionNette`, `R/fonctionsCalculsDivers.R:1745-1764`) prélève sur la pension la CSG et la CRDS des salaires, abattement de 1,75 % compris.
- Sa revalorisation de 2020 (`revaloSpeciale2020`, `R/fonctionsCalculsDivers.R:3094-3109`) ignore la zone de lissage de 2 000 à 2 014 €.
- Sa législation s'arrête avant la réforme de 2023 : âge d'ouverture de 62 ans pour toute génération depuis 1955, 169 trimestres pour 1964 (ageDuree de inst/extdata/parametres.Rds).
- Les écarts de TRAJECTOiRE y sont déjà : VFU de la Cnav sans fin en 2016 (R/fonctionsCalculsPensions.R:2790), coefficients temporaires sans fin (:2712, 2738), arrondi inférieur du …

### CALIPER (CALcul Interrégimes des PEnsions de Retraite) (`caliper`)

**Bilan.** Son code est désormais calcul_pension : CALIPER ne compte plus que pour une confirmation avec lui et TRAJECTOiRE. Sa documentation de 2011 apprend encore au dépôt le SAM trimestrialisé d'avant 1995 et l'exclusion des années sans trimestre depuis 2004, et lui donne une précision à viser, celle d'une validation sur des pensions réelles ; elle décrit la législation de 2010.

**Ce qu'il fait mieux que le dépôt :**
- Il a été validé sur des pensions réelles, celles de l'EIR 2004 : « 95,5 % des pensions de la CNAV sont estimées correctement […] l'écart […] n'excède pas un euro mensuel en 2004 ». *(à reprendre, étape 138.14)*
- Il calcule le SAM tel que la Cnav le calculait avant 1995 : la somme des meilleurs salaires rapportée aux trimestres validés de ces années, fois quatre, et non au nombre d'années. *(à reprendre, étape 138.16)*
- Il exclut du SAM, depuis 2004, les années qui ne valident aucun trimestre ; *(à reprendre, étape 138.16)*

### PROMESS (`promess`)

**Bilan.** Fermé, de 2010, refondu dans TRAJECTOiRE : seul l'effet horizon de ses fins de carrière se confronte au dépôt, qui raisonne à comportement inchangé. Rien d'autre de ses publications ne vaut contre le dépôt d'aujourd'hui.

**Ce qu'il fait mieux que le dépôt :**
- Il modélise les fins de carrière après 54 ans et l'effet horizon : une probabilité de cesser tout emploi pour chacun des six âges qui précèdent l'âge d'ouverture, décalée quand cet âge recule, et une sortie plus fréquente après … *(à trancher)*

### ANCETRE (`ancetre`)

**Bilan.** Il donne ce qu'aucune caisse ne donne seule — des retraités sans doublon, leur pension par régime principal, leur répartition par taux de CSG — que la page Coût n'a pas. Mais les deux points du registre citent un document qui ne les contient pas, et la projection de l'âge de départ est celle de TRAJECTOiRE.

**Ce qu'il fait mieux que le dépôt :**
- Il décrit des personnes, non des caisses : un pseudo-EIR calé « par la méthode du calage sur marges » sur l'EACR, qui donne la pension par régime principal, fin 2024 : 1 610 € par mois au régime général, 2 570 € aux civils de … *(à reprendre, étape 138.3)*
- Il donne la répartition tous régimes, sans doublon, des retraités par taux de CSG : en 2024, droits directs, 3 815 436 exonérés, 2 320 138 au taux réduit, 3 742 249 au taux médian, 7 420 422 au taux plein (22,1, 13,4, 21,6 et … *(à reprendre, étape 138.2)*

### legiretraite (paquet R) (`legiretraite`)

**Bilan.** Ses paramètres de législation ne valent pas mieux que les séries certifiées du dépôt, et les trois écarts du registre tiennent au même commit (dureeRequise.csv:136-137, aod.csv:31, 33, 85, 87). Ses âges sont à jour de la loi du 30 décembre 2025, ses durées en sont restées à la loi de 2023, ses revalorisations vont jusqu'en janvier 2026. Son apport est l'EACR de mai 2026 mise en tables, que le dépôt ne lit qu'en partie.

**Ce qu'il fait mieux que le dépôt :**
- Il embarque les tables de l'EACR, dont la répartition des retraités de droit direct par taux de CSG en 2024, donnée d'ANCETRE (source « Ancetre 2024 ») que le paquet redistribue : 22,1 % d'exonérés, 13,4 % au taux réduit, 21,6 % … *(à reprendre, étape 138.3)*
- Il embarque, prêtes à lire, les autres tables de l'EACR du 26 mai 2026 : E, les minima (bénéficiaires du minimum contributif, du minimum garanti, de la PMR) ; *(à reprendre, étape 138.3)*

**Ses erreurs ou retards (3) :**
- Son fichier `dureeRequise.csv`, sans date d'effet, donne 171 trimestres à la génération 1964 et 172 à 1965, les valeurs de la loi de 2023, quand ses âges suivent la loi du 30 …
- Le retard de `dureeRequise.csv` sur la loi du 30 décembre 2025 ne touche pas que le droit commun : l'actif de la fonction publique y a 171 trimestres pour 1969 et 172 pour 1970, …
- Son `aod.csv` ouvre les droits de l'actif à 58 ans dès la génération de janvier 1970, et ceux du super-actif à 53 ans dès janvier 1975 (`inst/extdata/aod.csv:31, 33, 85, 87`).

### EDIFIS (`edifis`)

**Bilan.** Rien sur les pensions. Il apporte un barème de cotisations année par année, qui montre que le dépôt applique au régime général des moyennes par période, et un coût du travail complet, déjà au registre.

**Ce qu'il fait mieux que le dépôt :**
- Son coût du travail compte la formation, l'apprentissage, la construction et le versement mobilité, 4,13 % de plus. *(à reprendre, étape 138.12)*
- Ses barèmes de 2015 à 2025 portent les taux de vieillesse de chaque année. *(à reprendre, étape 138.16)*
- Il calcule le revenu disponible d'un ménage type d'actifs selon le salaire : impôt sur le revenu (barème, décote, quotient familial), RSA, prime d'activité, aides au logement, prestations familiales, AAH, ASS. *(à trancher, étape 138.13)*

**Ses erreurs ou retards (1) :**
- Le supplément par quart de part du seuil du taux réduit de CSG reprend celui de l'exonération (feuille « Barème » 2025, lignes 283 et 285 : 142,58 € par mois chacun).

## Le COR

### Maquette globale de projection du COR (`maquette_globale_cor`)

**Bilan.** La maquette globale décompose ce que la page Coût agrège : la dépense par groupe de régimes, les effectifs et la pension relative, les variantes démographiques, les leviers et leurs effets macroéconomiques, les réserves. Elle localiserait l'écart de 2070 (18,24 % contre 15,3 %), et son enquête Emploi donne la part des reportés en emploi que le dépôt fixe à un.

**Ce qu'il fait mieux que le dépôt :**
- Il décompose la dépense en effectifs et pension relative, par groupe de régimes : de 2025 à 2070, les retraités de droit direct passent de 17,4 à 22,1 millions, les cotisants de 30,6 à 28,9 millions, la pension relative de 54,6 à … *(à reprendre, étape 138.3)*
- Il chiffre ce qui équilibrerait le système d'ici 2030 ou 2070 : abaisser les pensions de 1,4 à 8,6 % (« pension gap »), relever le prélèvement de 0,4 à 2,8 points (« tax gap »), ou, par l'âge seul, partir à 67,6 ans en 2070. *(à reprendre, étape 138.3)*
- Il publie, par cas type et génération, le taux de rendement interne net (« calcul SG-COR ») : 1,98 % pour le non-cadre de la génération 1940, 0,88 % pour 1970, 0,80 % pour 1980 et 0,83 % pour 2000. *(à reprendre, étape 138.9)*
- Il projette l'ASPA du FSV, 0,15 % du PIB en 2023 et 0,11 % en 2070, et une dépense du FSV qui passerait en 2070 de 0,50 à 0,70 % si l'ASPA suivait le SMIC. *(à reprendre, étape 138.5)*
- Il projette la dépense par groupe de régimes (fig. *(à reprendre, étape 138.3)*
- Il publie la situation sur le marché du travail par âge fin, de 50 à 69 ans (fig. *(à reprendre, étape 138.3)*
- Il chiffre la sensibilité de la dépense aux hypothèses démographiques. *(à reprendre, étape 138.7)*
- Il projette les rémunérations publiques sur les hypothèses de la Direction du budget. *(à reprendre, étape 138.3)*
- Il publie les effets macroéconomiques des leviers (tab. *(à trancher)*
- Il projette ce que le FSV verse aux régimes de base pour les périodes de chômage : 61,9 % de ses dépenses en 2023 (0,68 % du PIB) et 59,2 % en 2070 (« Pec cot chômage RB »). *(à trancher)*
- Il tient le stock : les réserves des régimes en répartition valent 223,9 Md€ fin 2025, 7,5 % du PIB, dont 91 % aux complémentaires et 52 % à l'Agirc-Arrco (p. *(à trancher)*

**Ses erreurs ou retards (1) :**
- Dans le classeur Données_RA2026_P2, la feuille du tableau 2.11 porte des notes périmées : « Sources : projections COR - juin 2025 », et une lecture « baisse de 3,7 % dès 2025 […] …

### Maquette simplifiée du secrétariat général du COR (`maquette_sg_cor`)

**Bilan.** Rien de nouveau au-delà des chocs stylisés, déjà au registre (138.11). Ses autres conclusions confirment des choix du dépôt (`limites.md:2958-2962`) : l'équilibre par construction quand on indexe sur la masse salariale, et un coefficient qui doit anticiper la croissance quand les pensions suivent les prix.

**Ce qu'il fait mieux que le dépôt :**
- Il soumet un système stylisé à quatre chocs, en annuités, en points et en comptes notionnels : sur un choc démographique, les comptes notionnels laissent des déficits « de l'ordre de 10% de la masse des cotisations, contre près … *(à reprendre, étape 138.11)*

### Simulateur du COR (`simulateur_cor`)

**Bilan.** Fermé, le simulateur ne se confronte que par sa documentation de 2016. Celle-ci apporte l'équation de bouclage (déjà au registre) et le facteur de 0,5 avec sa sensibilité : c'est le premier repère pour remplacer le plafond de un du dépôt.

**Ce qu'il fait mieux que le dépôt :**
- Il boucle la projection par une équation, « S = B x [ T – ( NR / NC ) x ( P + dP ) ] » : un an d'âge retire G retraités et ajoute 0,5 G cotisants, facteur « conventionnel », pour 0,6 à 0,9 point de PIB. *(à reprendre, étape 138.3)*
- Sa documentation fixe à 0,5 la part des retraités retardés qui deviennent cotisants, parce qu'« une partie des nouveaux retraités ne sont plus en emploi au moment où ils liquident leurs droits ». *(à reprendre, étape 138.3)*

## Les caisses

### PRISME (Projection des Retraites, Simulations, Modélisation et Évaluations) (`prisme`)

**Bilan.** Prisme fait mieux sur ce qu'une population seule permet de voir : la part et la distribution des droits non contributifs, la mortalité par type de pension, les départs et le non-recours. Ses chiffrages publiés (réforme de 2023, solidarité de 26 %, gain d'héritage de 2009) se confrontent dès maintenant.

**Ce qu'il fait mieux que le dépôt :**
- Il a chiffré la mesure d'âge du PLFRSS 2023 : 3,3, 5,3 et 7,5 Md€ en 2024, 2025 et 2026. *(à reprendre, étape 138.3)*
- Il différencie le non-recours à l'ASPA « selon la situation conjugale, le sexe, le montant de l'allocation ainsi que l'âge ». *(à reprendre, étape 138.3)*
- Il chiffre, dispositif par dispositif, la part de la solidarité dans les masses de droits propres de tous les régimes : 26 % en 2016 et 25 % en 2070. *(à reprendre, étape 138.19)*
- Sa bascule de 2009 en comptes notionnels intègre au coefficient de conversion le décès des actifs avant la retraite : « L'effet correcteur dû au décès prématuré d'un certain nombre d'actifs augmente les coefficients de conversion … *(à trancher)*
- Il applique aux retraités de la Cnav des quotients de mortalité estimés sur ses fichiers (2013-2014), par type de pension (normale, inapte, invalide), et ceux de l'INSEE aux autres. *(à reprendre, étape 138.7)*
- Il projette le rapport de la durée de retraite à la durée de vie (« proche de 28 % » pour les générations que touche la réforme de 2023) et la pension moyenne à la liquidation par sexe et génération. *(à reprendre, étape 138.9)*
- Il fait partir chacun par 48 équations logistiques au pas mensuel (estimées sur 2011-2016), selon la carrière, le taux, la carrière longue et l'inaptitude. *(à reprendre, étape 138.14)*

**Ses erreurs ou retards (1) :**
- Sa bascule de 2009 calcule les coefficients de conversion sur des tables transversales, alors que ses assurés meurent selon des tables longitudinales : « Les pensions sont par …

### Moteur de calcul des retraites de l'Assurance retraite (`moteur_cnav`)

**Bilan.** Les fiches décrivent des étapes sans formules ; le dépôt les couvre toutes (coordination internationale, LURA, minimum contributif, cumul et seconde pension), à la revalorisation près, déjà au registre. Ce qui se confronte reste les exemples officiels de la Cnav, déjà au banc.

**Ce qu'il fait mieux que le dépôt :**
- À chaque date de revalorisation, il applique le coefficient au « montant mensuel théorique » de la seconde pension, le compare au « plafond réglementaire » de la date, et retient le plus petit, comme le veulent L. *(à reprendre, étape 138.12)*

**Ses erreurs ou retards (1) :**
- Deux fiches décrivent « une majoration de durée d'assurance associée au minimum contributif, destinée à garantir un niveau minimal de la retraite » : « calcul et proratisation de …

### RGCU et moteur de valorisation des carrières (`rgcu_mvc`)

**Bilan.** Le RGCU et son moteur calculent durées et salaire annuel moyen à la demande, sans rien stocker ni publier (« les droits ne sont pas stockés suite à un calcul ») : aucune sortie ne se confronte, et ses règles sont celles que le dépôt applique déjà. Il annonce des extractions complètes pour le CASD « à une date qui reste à préciser » (p. 23), utiles un jour à l'étape 14.

**Ce qu'il fait mieux que le dépôt :**
- Son modèle de données porte des éléments de carrière que la carrière du dépôt ne saisit pas : rachats, versements volontaires, stages de formation, périodes de guerre, apprentissage, handicap, choix de majoration de durée … *(à reprendre, étape 138.12)*

### Pablo (`pablo`)

**Bilan.** Pablo fait mieux par sa population exhaustive et sa mortalité propre, dont il mesure le biais de l'individu moyen, et par un engagement par régime publié chaque année. Cet engagement est le contrôle par régime qui manque au dépôt ; le dépôt a déjà repris la décomposition du taux de l'État de la Cour des comptes du 22 septembre 2026 (`contribution_etat_retraite_seule.csv`).

**Ce qu'il fait mieux que le dépôt :**
- Microsimulé sur le compte individuel de retraite, il chiffre le biais de l'individu moyen : 1 845 Md€ d'engagements, contre 1 535 Md€ selon le modèle agrégé Ariane, un écart qui tient pour 140 Md€ aux pensions moyennes, pour 79 à … *(à reprendre, étape 138.3)*
- Il calcule chaque année, pour le compte général de l'État, l'engagement de retraite des fonctionnaires civils et militaires, par unités de crédit projetées et avec la mortalité du régime : 1 573 Md€ fin 2024 au taux réel de 1,38 … *(à reprendre, étape 138.3)*
- Il fait mourir les fonctionnaires de l'État selon 23 tables relationnelles (Hannerz) : 60 000 décès de moins qu'avec l'INSEE d'ici 2029, 2,2 Md€ de pensions de plus en 2034, 45 Md€ d'engagements. *(à reprendre, étape 138.7)*
- Il chiffre la réforme de 2023 au régime de l'État par rapport à un droit sans réforme : dépenses −0,4 % en 2025 et −2 % en 2033 ; *(à reprendre, étape 138.3)*

### Oscar (`oscar`)

**Bilan.** Oscar est l'outil en R du SRE pour les cas types et le système en points de 2020. Le dépôt a déjà son pas mensuel, son calcul du RAFP et un moteur commun aux cas types et à la population ; il ne lui manque que la plage d'âges (138.10) et la validation sur un flux réel (138.14). Son usage depuis 2020 n'est pas publié et aucun résultat ne se confronte.

**Ce qu'il fait mieux que le dépôt :**
- Il calcule chaque cas type sur une plage d'âges de liquidation (« par exemple 62-70 ans »), à partir de grilles indiciaires par génération. *(à reprendre, étape 138.10)*
- Son moteur du système actuel a été « testé avec succès sur le flux de liquidation réel 2018 » du SRE. *(à reprendre, étape 138.14)*

### Ariane (`ariane`)

**Bilan.** Rien. Ariane était une méso-simulation par génération en quatre groupes (civils, militaires, La Poste, Orange), qui raisonnait sur des « individus moyens » comme les cas types du dépôt, et Pablo l'a remplacée. Son seul résultat publié, 1 535 Md€ d'engagements fin 2015 contre 1 845 pour Pablo, mesure le biais de l'individu moyen, déjà au point de Pablo.

### Canopée (`canopee`)

**Bilan.** Canopée fait mieux par la composition de la CNRACL : actifs ou sédentaires, invalidité, grades, mortalité propre. Ses chiffres publiés montrent que le dépôt pèse toute la caisse sur un départ à 57 ans quand l'âge moyen y est de 61,5 ans, une erreur de pondération qui grossit les économies des scénarios notionnels.

**Ce qu'il fait mieux que le dépôt :**
- Il projette les retraités de droit direct de la CNRACL, de 1,34 million en 2023 à 2,13 millions en 2070. *(à reprendre, étape 138.3)*
- Il sépare, à la CNRACL et grade par grade, les départs actifs, sédentaires, pour invalidité et en carrière longue. *(à reprendre, étape 138.3)*
- Il fait mourir les fonctionnaires territoriaux et hospitaliers selon des tables adaptées par sexe, invalidité et catégorie hiérarchique (QRS n° 19, Soulat 2017), parce qu'ils « décèdent en moyenne plus tardivement que la moyenne … *(à reprendre, étape 138.7)*

**Ses erreurs ou retards (1) :**
- La description de 2020 suit les grilles de 2015, sans le protocole PPCR (« celles prévalant en 2015 »), et fait liquider tout le monde au taux plein, sans décote ni surcote (p.

### Mistral (`mistral`)

**Bilan.** Mistral, l'outil de la Caisse des dépôts pour l'Ircantec (avec Prévir pour l'emploi des contractuels), n'est connu que par une ligne de la note de 2024 et par ses projections dans le classeur du COR. Il ne fait mieux que par ces projections, qui sont à lire comme des droits de polypensionnés.

**Ce qu'il fait mieux que le dépôt :**
- Il projette les droits directs servis par l'Ircantec, de 2,04 millions en 2023 à 5,47 millions en 2070. *(à reprendre, étape 138.3)*
- Il évalue chaque année la solvabilité de l'Ircantec à long terme « au regard d'indicateurs définis dans le cadre de sa convention d'objectifs et de gestion (COG) et de ses textes réglementaires ». *(écarté)*

### MisrAA (`misraa`)

**Bilan.** MisrAA fait mieux par la mortalité différentielle, qui manque aux masses du Coût, et par la seule trajectoire publiée de la valeur du point (déjà en a_trancher). Le point existant est à corriger sur l'auteur de la convention, la nature des 24,6 et 16,4 %, et les lignes du dépôt citées.

**Ce qu'il fait mieux que le dépôt :**
- Il projette l'Agirc-Arrco sous une convention de la Fédération Agirc-Arrco, « après consultation des partenaires sociaux », que le COR reprend : sur 2027-2037, la valeur de service suivrait le salaire moyen minoré de 1,16 %, puis … *(à trancher)*
- Il pose qu'ignorer la mortalité différentielle « est susceptible de sous-estimer les dépenses » : les anciens cadres vivent plus longtemps et ont plus de droits. *(à reprendre, étape 138.7)*

## Les ministères

### Osiris (`osiris`)

**Bilan.** Osiris, maquette interne de la DSS, ne publie que ses cas types de 2020, calculés sous un droit périmé. Il n'en reste que la forme de deux de ses cas types : une carrière heurtée par le chômage, que la grille du dépôt n'a pas, et une plage d'âges.

**Ce qu'il fait mieux que le dépôt :**
- Ses cas types comprennent une carrière heurtée : un non-cadre du tiers inférieur des salaires perd son emploi à 42 ans, touche l'ARE deux ans puis l'ASS deux ans, reste un an et demi au chômage non indemnisé, puis est inactif … *(à reprendre, étape 138.19)*
- Il présente chaque cas type à six âges de départ (62 à 67 ans) pour les générations 1975, 1980, 1990 et 2003. *(à reprendre, étape 138.10)*

**Ses erreurs ou retards (1) :**
- Ses résultats « sans réforme » de 2020 font partir les générations 1975 à 2003 dès 62 ou 63 ans.

### Aphrodite (`aphrodite`)

**Bilan.** Aphrodite fait mieux par ses fins de carrière et sa réversion complète (ex-conjoints, décès avant le départ), deux points déjà prévus par les étapes 3 et 4, et par son bouclage avec Mésange. Ses résultats chiffrés, de 2016, ne se confrontent plus ; son usage après 2020 n'est pas publié.

**Ce qu'il fait mieux que le dépôt :**
- Il simule les fins de carrière après 55 ans (emploi, chômage, inactivité, maladie) par des logits emboîtés estimés sur l'EIC 2009, et peut y ajouter un effet horizon. *(à reprendre, étape 138.3)*
- Il calcule la réversion sur quatre mariages successifs, avec les conditions de ressources, de non-remariage et de durée de mariage. *(à reprendre, étape 138.4)*
- Il se boucle avec Mésange : réforme simulée, effets sur l'emploi, les salaires et les prix, réinjectés jusqu'à convergence. *(à trancher)*
- Il projette au choix sous les projections de l'INSEE ou sous les scénarios démographiques de l'Ageing Working Group. *(à reprendre, étape 138.7)*

**Ses erreurs ou retards (1) :**
- Ses résultats publiés reposent sur la législation de 2016 et le scénario B du COR de 2015 (productivité 1,5 %) : dépenses de droit direct de 12,4 % du PIB en 2015 à 11,3 % en 2060.

### Saphir (`saphir`)

**Bilan.** Saphir ne fait rien qu'Ines ne fasse à jour. Il confirme, pour 2017 seulement, le régime de CSG à trois cas selon le RFR et les parts, l'ASPA du couple et l'impôt des pensions. Ses paramètres se recopient, mais ils sont figés en 2017, et son abattement de l'ASPA est faux.

**Ce qu'il fait mieux que le dépôt :**
- Il fixe le régime de CSG des pensions — exonération, taux réduit, taux plein — selon le revenu fiscal de référence et les parts, au barème de 2017 : 10 996 € plus 2 936 € par demi-part, 14 375 € plus 3 838 €. *(à reprendre, étape 138.2)*
- Il sert l'ASPA de 2017 sous le plafond du couple et borne le membre seul éligible au montant d'une personne seule. *(à reprendre, étape 138.2)*
- Il calcule l'impôt des pensions de 2016 et 2017 : abattement de 10 % (au moins 379 €, au plus 3 711 € pour l'impôt 2016, relevés pour 2017), abattement des personnes âgées ou invalides, fractions imposables des rentes à titre … *(à reprendre, étape 138.5)*

**Ses erreurs ou retards (1) :**
- Il retranche une seule fois 0,9 SMIC mensuel (1,5 pour un couple) de revenus d'activité annuels, au lieu de quatre fois.

## L'Urssaf : les règles publicodes

### modele-ti (`modele_ti`)

**Bilan.** Il fait mieux sur le détail des cotisations des indépendants après 2025 (assiette, taux, sections libérales année par année, PCV, incapacité, Mayotte, conjoint, dispenses) et sur la traçabilité. Il fait moins bien sur les droits : trimestres CNAVPL surestimés, annulés par l'Acre ou l'incapacité, et une pension de base à 50 % du revenu de l'année.

**Ce qu'il fait mieux que le dépôt :**
- Chaque règle porte ses `références`, et l'application en tire une page par valeur, qui explique le calcul. *(à reprendre, étape 136.4)*
- Il calcule l'assiette sociale depuis le revenu brut : abattement de 26 % borné entre 1,76 % et 130 % du PASS, plus les revenus de remplacement abattus (indemnités journalières, AJPA), moins l'épargne salariale ; *(à reprendre, étape 138.18)*
- Il applique aux artisans et commerçants les taux du code : vieillesse de base 17,15 % plafonnée plus 0,72 % sur tout depuis 2025 (0,60 % avant), RCI 8,1 et 9,1 %. *(à trancher)*
- Il accorde les 400 points CNAVPL de l'année d'incapacité d'exercice de plus de six mois (et exonère chez lui la complémentaire de la section). *(à reprendre, étape 138.18)*
- Il porte les grilles de la CAVEC de 2023 à 2026 (2025 : 782 € jusqu'à 16 190 €, 2 934 € jusqu'à 32 350 €, 4 629 € jusqu'à 44 790 €…). *(à reprendre, étape 138.18)*
- Il cite, règle par règle, le guide annuel de la CNAVPL (édition 2025) : cotisations, classes, points, valeurs du point et seuils de toutes les sections et de leurs PCV, pour l'année. *(à reprendre, étape 138.18)*
- Il porte les cotisations PCV (ex-ASV) de toutes les professions de santé conventionnées, 2023 à 2026, avec la part de l'assurance maladie : médecins de secteur 1 et 2, auxiliaires médicaux, chirurgiens-dentistes, sages-femmes, … *(à reprendre, étape 138.18)*
- Il porte l'indépendant de Mayotte : vieillesse de base 10,05 % en 2025, 10,75 % en 2026, vers 17,75 % en 2036, assiette d'au moins 450 SMIC horaires de Mayotte, pas de RCI. *(à reprendre, étape 138.18)*
- Il calcule les cotisations retraite du conjoint collaborateur selon les options du code : forfait d'un tiers du PASS (la moitié à la CNAVPL), un tiers ou la moitié du revenu du chef, avec ou sans partage, et la complémentaire qui … *(à reprendre, étape 138.18)*
- Il dispense de l'assiette minimale l'activité saisonnière, comme le bénéficiaire du RSA ou de la prime d'activité, sur question posée. *(à reprendre, étape 138.18)*
- Il appelle le forfait CNBF selon l'ancienneté (363 € la première année à 1 988 € dès la sixième en 2026), de 2023 à 2026. *(à reprendre, étape 138.18)*
- Il modélise l'Acre, réforme de 2026 comprise (exonération au quart, publics restreints). *(écarté)*

**Ses erreurs ou retards (4) :**
- Chez nous, l'assiette minimale de 2025 (450 SMIC horaires) ne validait que deux trimestres : une division en virgule flottante rendait 2,999….
- L'Acre abat la cotisation de base (cotisations.publicodes:400-409), donc le revenu cotisé qui valide les trimestres (retraite-base.publicodes:74-79) : un créateur de 2025 sous 75 …
- Trimestres CNAVPL validés sur (tranche 1 + tranche 2) / taux de tranche 1 (retraite-base.publicodes:74-106 ;
- Vieillesse de base de l'indépendant de Mayotte en 2032 : 14,85 % (cotisations.publicodes:466-467).

### modele-social (`modele_social`)

**Bilan.** Côté salarié et micro-entrepreneur, il est à jour de 2026 et fait mieux sur ce qui entoure la retraite : chiffre d'affaires, Mayotte, taxe sur les salaires, coût complet, Lodeom, précompte des auteurs, PRCI. Sa branche indépendante (d'avant 2025) et ses trimestres d'apprenti sont faux : modele-ti ou le dépôt y font foi.

**Ce qu'il fait mieux que le dépôt :**
- Il saisit le micro-entrepreneur par son chiffre d'affaires et son activité, abattus de 71, 50 ou 34 %, et suit celui de la Cipav par tranches. *(à reprendre, étape 138.12)*
- Il porte le seuil d'affiliation des artistes-auteurs au RAAP (900 SMIC horaires de N−1), le taux réduit sur option et la conversion des BNC (× 1,15). *(à reprendre, étape 138.12)*
- Il dispense des cotisations minimales le bénéficiaire du RSA ou de la prime d'activité ; *(à reprendre, étape 138.12)*
- Chaque règle porte ses `références`, et l'application en tire une page par valeur ; *(à reprendre, étape 136.4)*
- Il porte le plafond de première tranche du RCI de 2021 à 2025 (38 493, 38 916, 40 784, 42 946, 43 891 €). *(à reprendre, étape 138.18)*
- Il porte le salarié de Mayotte : vieillesse 5,54 % salariale et 9,90 % patronale en 2026, sans déplafonnée ni complémentaire ; *(à reprendre, étape 138.18)*
- Il porte la taxe sur les salaires (4,25, 8,50 et 13,60 %) et l'employeur qui la doit (non assujetti à la TVA). *(à reprendre, étape 138.12)*
- Il compte le versement mobilité au taux de la commune, la taxe d'apprentissage, la formation, la PEEC, le dialogue social, le forfait social. *(à reprendre, étape 138.12)*
- Il applique outre-mer la Lodeom au lieu de la réduction générale. *(à reprendre, étape 138.18)*
- Il calcule le précompte de l'artiste-auteur : plafonnée moins 0,75 point et déplafonnée nulle (prises en charge par l'État), CSG abattue sur les seuls traitements et salaires, formation 0,35 %, RAAP, RACD, RACL. *(à reprendre, étape 138.12)*

**Ses erreurs ou retards (6) :**
- Le paquet porte encore les paramètres d'avant 2025 : 8,23 % et 525 points pour la CNAVPL, 9 et 22 % pour la Cipav ;
- Il valide les trimestres du micro-entrepreneur sur son revenu abattu, aux coefficients 0,29, 0,50 et 0,66, quand le revenu cotisé, CA × 12,3 % × 43,45 % / 17,87 %, donne 0,299, …
- Il fixe à 2 860 € le seuil de la Cipav pour 2026 (`protection-sociale.publicodes:88`).
- Sa branche `dirigeant . indépendant` est d'avant 2025 : assiette = revenu professionnel (dirigeant/indépendant/indépendant.publicodes:47-58), vieillesse 17,75 % et 0,60 % …
- Seuils de la taxe sur les salaires de 2025 : 9 147 et 18 258 € (salarié.publicodes:517-535).
- Trimestres de l'apprenti validés sur sa cotisation salariale après exonération (contrat/apprentissage.publicodes:126-150 ;

### modele-as (`modele_as`)

**Bilan.** Rien de mieux sur les droits, ceux d'un salarié, que le dépôt calcule bien mieux (sa pension de base vaut 50 % du revenu de l'année). Seule sa fiche de paie, sans chômage ni réduction générale, manque au dépôt.

**Ce qu'il fait mieux que le dépôt :**
- Ses règles portent leurs `références`, comme celles de modele-social et de modele-ti, et l'application en tire une page par valeur ; *(à reprendre, étape 136.4)*
- Il décrit la fiche de paie du dirigeant assimilé salarié (président de SAS) : régime général et Agirc-Arrco, mais ni assurance chômage, ni AGS, ni réduction générale. *(à reprendre, étape 138.12)*

## Les transcriptions du droit en code

### Catala (catala-examples) (`catala`)

**Bilan.** Sa seule avance reste la traçabilité, chaque règle sous l'alinéa qu'elle transcrit. Ses règles de retraite, d'avant la LFSS pour 2026 et fautives pour 1967, ne valent rien comme référence ; seul son SMIC de Mayotte sert au dépôt.

**Ce qu'il fait mieux que le dépôt :**
- Chaque règle y est écrite sous l'alinéa qu'elle transcrit, recopié à côté : le code se relit contre son texte. *(à reprendre, étape 136.4)*
- Il recopie, décret par décret, le SMIC de Mayotte de 2019 à novembre 2024 (7,57 € à 8,98 €) ; *(à reprendre, étape 138.18)*
- Il calcule les aides au logement de tout ménage, retraité compris, avec ses tests. *(écarté)*

**Ses erreurs ou retards (3) :**
- Pour la génération 1967, le code dit 62 ans et 9 mois, quand le texte qu'il recopie juste au-dessus dit 63 ans et 9 mois ;
- Son calendrier d'âges précède la LFSS pour 2026 : L.
- Son SMIC s'arrête au 1er novembre 2024, et 8,98 € à Mayotte vaut dès « |2024-01-01| », en conflit avec 8,80 € de janvier à octobre 2024 (smic/Smic.catala_fr:431-490).

### ir-catala (`ir_catala`)

**Bilan.** Une brique pour 138.2 et 138.5 : l'abattement des pensions et le quotient familial des retraités, transcrits du CGI. Montants de 2022, preuve de concept arrêtée depuis octobre 2024.

**Ce qu'il fait mieux que le dépôt :**
- Il calcule l'abattement de 10 % des pensions (CGI, art. *(à reprendre, étape 138.2)*
- Il calcule le quotient familial avec les demi-parts des retraités : plus de 74 ans titulaires de la carte du combattant, veuves de guerre, invalides. *(à reprendre, étape 138.5)*

**Ses erreurs ou retards (1) :**
- Abattement des pensions à 4 123 € et 422 € (archives_cgi.catala_fr:341-370).

## La recherche

### EUROMOD (France) (`euromod`)

**Bilan.** EUROMOD fait mieux que le dépôt sur le net des pensions : CSG et CASA graduées par RFR et parts au barème exact de 2026, recopiable sous CC BY 4.0, et l'ASPA hors des prélèvements. Il fait mieux aussi sur l'impôt des pensions. Il ne simule aucune pension, faute d'historique de carrière ; il sert l'ASPA plus mal que la loi et prélève la CRDS sur toutes les pensions : on lui reprend ses seuils, pas ses assiettes. Son outil de ménages types (HHoT) peut confronter à part le net d'un couple de retraités une fois 138.2 fait.

**Ce qu'il fait mieux que le dépôt :**
- Il fixe le taux de CSG des pensions (0, 3,8, 6,6 ou 8,3 %) et la CASA, due aux deux derniers taux, selon le revenu fiscal et les parts. *(à reprendre, étape 138.2)*
- L'ASPA reste hors de l'assiette de la CSG, de la CRDS et de la CASA. *(à reprendre, étape 138.2)*
- Il calcule l'impôt des pensions de 2026 : abattement de 10 % (au moins 454 €, au plus 4 439 €), abattement des 65 ans et plus ou invalides (2 822 € sous 17 670 € de revenu, 1 411 € jusqu'à 28 430 €), CSG déductible de 3,8, 4,2 ou … *(à reprendre, étape 138.5)*

**Ses erreurs ou retards (7) :**
- Son rapport pays décrit pour 2022 à 2025 le critère d'un « impôt inférieur à 61 € », abrogé en 2015, et se dément deux paragraphes plus bas ;
- Il prend les ressources de l'ASPA nettes imposables.
- Il sert le plafond du couple, 1 620,18 € par mois, quand un seul membre a 65 ans (FR.xml:1518454-1518469 ;
- Il refuse l'ASPA à qui a un revenu d'activité (ils_earns#1=0, FR.xml:1518417 et 1518456) ;
- Il prélève la CRDS sur toutes les pensions, même exonérées de CSG (tscdf_fr, « Base fully taxed », FR.xml:1522462-1522487).
- Il plafonne l'abattement de 10 % des pensions par personne (TAX_UNIT tu_individual_fr, FR.xml:1497573 et 1497599).
- Le rapport (février 2026, tableau 1.1, p.

### retraites (simulateur du COR réécrit) (`retraites_scherrer`)

**Bilan.** Il reste le seul à piloter le système par l'âge et par la part de vie en retraite, et il ajoute une analyse de sensibilité (Sobol) que la page Coût n'a pas. Tout le reste date du COR de 2019.

**Ce qu'il fait mieux que le dépôt :**
- Il pilote le système par n'importe quel levier, l'âge compris, avec le niveau de vie relatif des retraités et la part de la vie passée en retraite. *(à reprendre, étape 138.3)*
- Il propage par Monte-Carlo l'incertitude de trois entrées (âge de départ, élasticité du report, chômage). *(à reprendre, étape 138.19)*
- Il calcule la part de la vie passée en retraite, (60 + e60 − âge)/(60 + e60), et l'âge qui la tient constante : 29,05 % en 2020 et 32,25 % en 2070 au COR de 2019. *(à reprendre, étape 138.9)*

### retraites-cor2026 (`retraites_cor2026`)

**Bilan.** Les variantes démographiques restent son seul apport. Le reste est une maquette moins fine que la page Coût, avec deux paramètres faux, inutilisés, et l'erreur de noria déjà au registre.

**Ce qu'il fait mieux que le dépôt :**
- Il porte les variantes démographiques de l'INSEE de 2026 : fécondité de 1,20 ou 1,70, solde migratoire de +70 000 ou +230 000. *(à reprendre, étape 138.7)*

**Ses erreurs ou retards (2) :**
- Sa pension relative ignore l'effet de noria (`maquette.py:146-149`) : 40,4 % en 2070, contre 45,3 % au COR, un écart qu'il attribue à tort à l'Agirc-Arrco …
- Ses hypothèses économiques, dites du COR de 2025, portent une productivité haute de 1,6 % et un chômage de 4,5 % (`config/hypotheses.yaml:41, 59-63`).

## La société civile et la presse

### Retraites 2027 (`retraites_2027`)

**Bilan.** Son seul avantage reste le net par foyer (138.2), qui est déjà au registre. Rien d'autre ne fait mieux que le dépôt, et sa borne d'impôt contient une erreur de calcul.

**Ce qu'il fait mieux que le dépôt :**
- Il calcule la pension nette par foyer : la CSG selon le revenu fiscal de référence, les exonérations de CRDS et de CASA, le 1 % maladie de la complémentaire, l'impôt avec ses abattements ; *(à reprendre, étape 138.2)*

**Ses erreurs ou retards (2) :**
- Il dit 29 % des retraités au taux plein de CSG, d'après la CFDT (`app.js:200`).
- Son barème 2027, « barème revenus 2025 (LF 2026) indexé de 2 % » (`params.js:58`), porte une deuxième borne de 30 091 € (`params.js:62`, `outils/simulation-plafond.py:20`).

### Simulateur de dépense publique, volet retraites (`simulateur_aurain`)

**Bilan.** Il apporte deux hypothèses sourcées pour la page Coût (part des reportés en emploi, effet retour), une interface budgétaire que le site n'a pas, et le contrefactuel de la suspension au trimestre près. Sa lecture d'une sortie de suspension en 2028 n'est pas dans la loi.

**Ce qu'il fait mieux que le dépôt :**
- Il source la part des reportés restés en emploi : « 62 à 75 % […] Défaut retenu : 65 % ». *(à reprendre, étape 138.3)*
- Il chiffre l'effet retour d'une baisse des pensions : moins de CSG et d'impôt, plus d'ASPA. *(à reprendre, étape 138.5)*
- Son interface résout un problème budgétaire à l'envers, par dichotomie, compare deux jeux d'hypothèses (A/B) et imprime un rapport avec ses repères budgétaires. *(à reprendre, étape 138.10)*
- Il compare, au trimestre de naissance, la loi de 2023 sans suspension (B0) au droit en vigueur (B1), et donne le gain de la suspension génération par génération. *(à reprendre, étape 138.10)*
- Il porte les seuils de CSG à 1, 2, 2,5 et 3 parts, avec le supplément par demi-part (3 484, 4 555 et 7 066 €), et la règle de lissage sur deux ans. *(à reprendre, étape 138.2)*
- Il donne l'incidence d'une mesure par décile de pension (onglet « Qui paie »). *(écarté)*

**Ses erreurs ou retards (1) :**
- Il écrit que la loi pour 2026 « fixe le terme de la suspension au 2028-01-01 sans préciser les modalités de sortie ».

### « Quand pourrai-je partir à la retraite ? » (`outil_quand_partir`)

**Bilan.** Rien de neuf au-delà du point contrefactuel déjà au registre ; j'ai examiné ses tables d'âge et de durée et sa partie santé. Sa comparaison avec l'espérance de vie sans incapacité est un contresens.

**Ce qu'il fait mieux que le dépôt :**
- Il donne, pour une génération, son âge et sa durée sous trois états du droit, la loi du 30 décembre 2025 comprise, et l'écart en mois. *(à reprendre, étape 138.10)*

**Ses erreurs ou retards (2) :**
- Il ouvre les droits de toute la génération 1961 à 62 ans et 3 mois, avec 169 trimestres (`outil.js`, l.
- Il oppose l'âge de départ à l'espérance de vie sans incapacité À LA NAISSANCE (64,1 et 63,7 ans), « l'âge jusqu'auquel une personne née aujourd'hui peut espérer vivre sans être …

### Simulateur de SUD éducation (`simulateur_sud_education`)

**Bilan.** La saisie par indice reste son seul apport. Son calcul de 2020 cumule cinq erreurs ou retards, que les textes en vigueur tranchent tous en faveur du dépôt.

**Ce qu'il fait mieux que le dépôt :**
- Il saisit l'enseignant par son corps et son échelon. *(à reprendre, étape 138.10)*
- Il compare le droit de 2020 au système universel à points du rapport Delevoye, primes comprises. *(à trancher)*

**Ses erreurs ou retards (5) :**
- Sa pension de fonctionnaire multiplie 75 % du dernier traitement par une décote sans borne ni critère d'âge, 1 − 1,25 % × (requis − acquis), et par un prorata non plafonné …
- Il sert aux fonctionnaires le minimum contributif du régime général, 695,59 € au prorata (`static/js/retraites.js:47, 207-225`).
- Il liquide les contractuels à 75 % de la moyenne de leurs 25 meilleures années, « avec intégration des primes » (`static/js/retraites.js:46, 186-201`).
- Saisir des années de direction d'une école de quatre classes arrête le calcul : la ligne 125 lit `anneesDirection24`, une variable jamais déclarée (`static/js/retraites.js:108, …
- Ses durées requises sont celles de la loi de 2014 (`:150-164`) et son point est celui de février 2017, 4,686 € (`:51`).

### devcrafting/retraites (`devcrafting_retraites`)

**Bilan.** Modèle jouet de 2020, mais j'y trouve trois avantages vérifiés : le plafond propre du RCI, que le dépôt sait lui manquer, le 1 % maladie de la complémentaire, et le taux propre des artisans au-dessus du plafond. Ses erreurs sur le prorata, la surcote et la durée sont tranchées par les textes.

**Ce qu'il fait mieux que le dépôt :**
- Il arrête la première tranche du RCI (7 %) à un plafond propre au régime (37 846 €), et non au plafond de la sécurité sociale. *(à reprendre, étape 138.18)*
- Son taux de remplacement net retire 10,1 % à l'Agirc-Arrco et 9,1 % à la base. *(à reprendre, étape 138.2)*
- Au-dessus du plafond, il prélève sur l'artisan 0,60 %, son taux propre. *(à reprendre, étape 138.18)*
- Il calcule le système universel à points du projet de 2019 pour les salariés et les indépendants : achat à 10 €, service à 0,55 €, âge d'équilibre à 64 ans à 5 % par an, 25,31 % générateurs de droits et 2,81 % déplafonnés, … *(à trancher)*

**Ses erreurs ou retards (6) :**
- Son prorata, trimestres validés sur requis, n'est pas plafonné (`CurrentRegimeGeneralDeBase.fs:9-14`).
- Au-delà de la durée, les trimestres manquants deviennent négatifs : la décote se change en surcote de 0,625 point par trimestre en sus, à tout âge.
- Ses coefficients Agirc-Arrco dépassent 1 pour des trimestres en sus (`CurrentSalaries.fs:22-23`), et il ignore le coefficient de solidarité, en vigueur à sa date.
- Sa seconde tranche du RCI part du plafond de la sécurité sociale, pas du plafond du régime, et va jusqu'à quatre plafonds au-dessus de lui (`CurrentSsi.fs:17-19`).
- Sa durée requise est celle de la loi de 2014 (`Domain.fs:65-70`) : 169 trimestres à 1964-1966.
- Son salaire moyen est la moyenne brute des 25 dernières années d'un profil linéaire, sans revalorisation (`CurrentRegimeGeneralDeBase.fs:7-8`).

### calcul-verification-pension-retraite (`calcul_verification_pension`)

**Bilan.** Ses deux avantages déjà au registre tiennent toujours, et le JO confirme une valeur de son seuil d'avant 1972. Rien d'autre : son calcul s'arrête à la base, et je lui trouve deux erreurs de plus.

**Ce qu'il fait mieux que le dépôt :**
- Il valide les trimestres d'avant 1972 par un seuil trimestriel en montant : 362,5 F en 1968, 437,5 F en 1971. *(à reprendre, étape 138.6)*
- Il recalcule les trimestres d'un relevé réel depuis ses montants, et le contrôle ainsi. *(à reprendre, étape 138.10)*

**Ses erreurs ou retards (3) :**
- Il réserve aux mères la majoration de pension de 10 %.
- Il retient 24 meilleures années pour la mère d'un enfant et 23 au-delà, quelle que soit la date de départ, et pour les seules mères (nom défini `nA_RAM_M`, cellules `Pension!F30` …
- Il compte les trimestres jusqu'à l'âge du taux plein en jours divisés par 91, arrondis à l'entier inférieur (`Pension!K27`) : un départ un mois avant 67 ans n'a donc pas de décote.

### Simulateur de cas types de Nos Retraites (`nosretraites_cas_types`)

**Bilan.** Rien de neuf au-delà de la table d'âges déjà au registre. Son droit est celui d'un moment, et les textes en vigueur le contredisent sur trois points.

**Ce qu'il fait mieux que le dépôt :**
- Il donne, de 58 à 67 ans et sous deux états du droit, ce que vaut chaque âge — départ possible, taux plein, décote, surcote —, résumé en phrases. *(à reprendre, étape 138.10)*

**Ses erreurs ou retards (3) :**
- Son droit « mac » met toute la génération 1961 à 62 ans et 3 mois, avec 169 trimestres (`legalParametersByYearOfBirth.json`, clé 1961).
- Il donne à la mère fonctionnaire quatre trimestres par enfant né avant 2004, sans condition (`calculationUtils.js:55-60`).
- Ses deux états, le droit d'avant 2023 et le projet du 10 janvier 2023, sont tous deux périmés : 63 ans et 171 trimestres à 1964, et pas de carrière longue pour un début d'activité …

## À l'étranger : les comptes notionnels

### Pensionsmodellen (`pensionsmodellen`)

**Bilan.** Ce qu'il fait de mieux tient au bilan (durée de rotation, actif de cotisation, fonds tampon et son rendement), calculé sur une population par états. De quoi donner à la page Coût un indicateur de stock et ses réserves ; mais son manuel date de 2015 et son code ignore l'accélérateur de 2026.

**Ce qu'il fait mieux que le dépôt :**
- Il projette le bilan du système suédois, durée de rotation (`x_Y_turnover_duration`) et indice d'équilibre (`x_Y_balance_ratio`). *(à trancher)*
- Il projette sur « 498 status groups », croisés par âge, sexe et origine, quand la page Coût du dépôt pondère 13 cas types (`castypes.py:127`). *(à reprendre, étape 138.14)*
- Il projette le fonds tampon (AP1 à AP4 et AP6), sa valeur de marché et son rendement, et le compte à l'actif du système (`x_Y_buffer_fund`, `x_Y_buffer_fund_return`). *(à reprendre, étape 138.19)*
- On y choisit le scénario démographique de SCB (« Du kan välja olika befolkningsscenarier »), en plus de la croissance, de l'inflation et du rendement. *(à reprendre, étape 138.7)*

**Ses erreurs ou retards (2) :**
- Son manuel est celui de 2015, même dans l'archive de la v2.2.
- La v2.2 ne distribue un excédent que pendant le rattrapage d'un frein.

### Typfallsmodellen (`typfallsmodellen`)

**Bilan.** Au-delà des gains d'héritage et des frais déjà au registre, il montre des choix que la proposition n'a pas faits : droits après le départ, années d'enfant, garantie à retrait partiel, transition par génération. Il sert aussi une rente capitalisée qui garde son rendement, ce que le dépôt devrait reprendre ; son diviseur projeté porte deux coquilles de moyenne, sans effet sur les tables officielles.

**Ce qu'il fait mieux que le dépôt :**
- Il impute chaque année au compte les gains d'héritage, les comptes des morts redistribués aux survivants de la génération, sur des facteurs « desamma för kvinnor och män » (SFB 62:11). *(à trancher)*
- Il déduit du compte les frais de gestion : 0,0319 % en 2025, 0,0334 % en 2026 (SFB 62:22-25 ; *(à trancher)*
- Il rend la pension par étage, avant et après impôt, en part du dernier salaire, et le revenu autour du départ. *(à reprendre, étape 138.9)*
- Il calcule l'uttag partiel, et les droits acquis après un premier uttag, portés chaque année à la pension. *(à trancher)*
- Il porte au compte les années d'enfant (« barnår », trois méthodes, la plus favorable retenue), payées par une cotisation de l'État. *(à trancher)*
- Sa garantie se retire à 48 % au-delà de 1,26 base de prix : chaque couronne de pension au-dessus du seuil en laisse 52 öre. *(à trancher)*
- La transition suédoise réelle a recalculé pour tous les droits notionnels de 1960 à 1998, au taux nouveau de 18,5 % sur les revenus enregistrés, années d'enfant comprises. *(à trancher)*
- Sa prime pension liquidée suit le rendement de ses fonds : la pension de l'année vaut celle de l'an passé × rendement ÷ 1,0165, le taux avancé dans le diviseur. *(à reprendre, étape 138.11)*
- Il lit des risques de décès projetés par année de 1980 à 2120, par sexe et par âge. *(à reprendre, étape 138.7)*

**Ses erreurs ou retards (1) :**
- Son diviseur projeté (`Calculate_Deltal`) fait une moyenne « sur cinq ans » qui compte deux fois l'année génération + âge cible − 3, soit quatre années distinctes en tout …

### Le diviseur suédois (delningstal) (`delningstal_suede`)

**Bilan.** Il apporte un exemple officiel que le dépôt n'a pas et qui se refait au centième, et une définition du diviseur en mensualités. Sur la mortalité, le dépôt est plus exact, et Pensionsmyndigheten chiffre elle-même ce que lui coûte la table du moment.

**Ce qu'il fait mieux que le dépôt :**
- La pension servie y est revalorisée moins la norme du diviseur, 1,016, la même qui actualise le diviseur (62:36). *(repris, étape 138.1)*
- Sa grille de 2026 (PFS 2026:2 : 19,13 à 62 ans, 17,34 à 65, 1,93 à 100) se recalcule au centième sur la table unisexe de SCB 2020-2024, en mensualités à échoir, survie linéaire dans l'année et facteur 1,016. *(à reprendre, étape 138.11)*
- Son diviseur est la valeur des mensualités, versées d'avance (« en kommande månadsutbetalning », 62:36). *(à trancher)*

**Ses erreurs ou retards (1) :**
- Son diviseur lit la mortalité du moment, cinq années observées (62:17, 62:36).

### L'indice d'équilibre suédois (balanstal) (`balanstal_suede`)

**Bilan.** Il apporte une mesure de solvabilité de stock, écrite dans la loi, que la page Coût peut calculer sans l'appliquer. Il apporte aussi un calendrier d'indexation sur des indices publiés, que le compte du dépôt devance d'un an ; l'équilibrage appliqué reste au propriétaire.

**Ce qu'il fait mieux que le dépôt :**
- L'indice d'équilibre se calcule sur un stock — cotisations fois durée de rotation, plus les fonds, sur la dette de pension — et s'applique : sous 1, il freine l'indexation des comptes et des pensions jusqu'au rattrapage ; *(à trancher)*
- De 1999 à 2016, l'indice de revenu suédois lissait sur trois ans la seule croissance réelle, multipliée par l'inflation de l'année. *(à reprendre, étape 138.11)*
- Calculer l'indice d'équilibre comme indicateur, sans l'appliquer. *(à reprendre, étape 138.19)*
- Un compte suédois ne reçoit que des indices publiés. *(à reprendre, étape 138.11)*

### SESIM (`sesim`)

**Bilan.** Son seul avantage, la population simulée, est déjà au registre (138.14), et il est plus mince qu'il n'y paraît : départs non incitatifs, pas de pension partielle. Le reste de la fiche double des points déjà relevés ailleurs — la décomposition (ageing_report), le fonds à 4 % (pensionsmodellen), le frein codé mais inactif (balanstal_suede) — et ignore l'accélérateur de 2026.

**Ce qu'il fait mieux que le dépôt :**
- Il simule environ 320 000 personnes, dont le départ dépend de l'éducation, de l'âge, du sexe et du revenu, et dont les conjoints coordonnent leur départ. *(à reprendre, étape 138.14)*

**Ses erreurs ou retards (2) :**
- La fiche décrit l'accélérateur comme une proposition au seuil de 1,1, « not enacted, and is not included in the pension calculations ».
- Sa base, l'échantillon LINDA tiré en 1999, s'arrête en 2018 et n'est plus tenue : « LINDA is no longer updated » (§ 4.2, note 19).

### MOSART (`mosart`)

**Bilan.** Code fermé (C#, sur un serveur de SSB). Ce qu'il fait de mieux tient à sa population — départs simulés, validation sur les pensions déclarées, indicateurs par décile — et demande des microdonnées, sauf l'hypothèse des deux tiers, transposable aux cas types ; sur l'arithmétique du compte, il applique la loi norvégienne, que delingstall_norvege couvre.

**Ce qu'il fait mieux que le dépôt :**
- Il projette des départs qui suivent l'espérance de vie. *(à reprendre, étape 138.7)*
- Il rapporte les pensions de toute la retraite aux revenus de toute la carrière, par décile de revenu et par sexe, pour la génération 1963. *(à reprendre, étape 138.9)*
- Il se valide sur les pensions observées : la distribution simulée des pensions de 2017, partie de la population de 1980, est confrontée à celle des déclarations fiscales. *(à reprendre, étape 138.14)*
- Il boucle sur l'offre de travail et un modèle d'équilibre général : pour les finances publiques, l'effet de la réforme de 2011 sur l'emploi pèserait plus que la baisse des pensions. *(écarté)*

### Le diviseur norvégien (delingstall) (`delingstall_norvege`)

**Bilan.** Son diviseur porte le gain d'héritage, déjà au registre et vérifié au millième, et NAV publie ses grilles et leur prévision, ce que le dépôt ne fait pas. Sa mortalité du moment est moins exacte que la table de génération du dépôt.

**Ce qu'il fait mieux que le dépôt :**
- Son diviseur rapporte la survie à l'âge de départ à la survie moyenne de 27 à 66 ans, si bien que la mortalité d'avant 62 ans y entre comme un gain d'héritage, « uavhengig av opptjeningsprofil ». *(à trancher)*
- NAV publie chaque juin la grille entière de ses diviseurs, génération par génération et mois par mois de 62 à 75 ans (générations 1954-1965 ; *(à reprendre, étape 138.11)*

**Ses erreurs ou retards (1) :**
- Après 60 ans, son diviseur lit la mortalité moyenne observée des dix années qui précèdent les 61 ans de la génération (§ 4-3), puis se fige.

### Modèle de prévision de la Ragioneria Generale dello Stato (`modello_rgs`)

**Bilan.** Il fait mieux sur les sorties : taux nets après impôt, variantes de longévité qui isolent l'effet du diviseur, décomposition de la dépense. Le reste du modèle n'est pas public, et je n'y ai trouvé aucune erreur.

**Ce qu'il fait mieux que le dépôt :**
- Ses taux de remplacement nets comptent l'impôt ; *(à reprendre, étape 138.2)*
- Il mesure ce que l'ajustement automatique du diviseur absorbe d'un choc de longévité : espérance de vie haute et basse, avec et sans révision des coefficients. *(à reprendre, étape 138.7)*
- Il décompose la dépense en pension moyenne sur productivité, fois pensions sur occupés. *(à reprendre, étape 138.3)*
- Le départ anticipé du régime contributif (64 ans, 20 ans de cotisation) exige une pension d'au moins trois fois l'assegno sociale, soit 1 638,72 € par mois en 2026, et 3,2 fois dès 2030. *(à trancher)*

### Les coefficients de transformation italiens (`coefficienti_italie`)

**Bilan.** Il fait mieux sur trois points : la réversion tarifée dans le diviseur (à trancher), le plancher à rattrapage, et un exemple officiel au millième. Sa mortalité par âge et sa correction de fréquence ne sont que des raffinements, et son taux de 1,5 % est plus généreux que la croissance qu'il constate lui-même.

**Ce qu'il fait mieux que le dépôt :**
- Son diviseur tarife la réversion : Δx = [Σs (a_x,s + A_x,s)]/2 − k, avec η = 0,6 et δ = 0,9 pour les hommes, 0,7 pour les femmes ; *(à trancher)*
- Le tableau C.2 de la Nota tecnica publie le diviseur à 65 ans, 19,049, et ses deux termes, 17,590 et 1,460 : un exemple officiel, que la fiche du diviseur du dépôt n'a pas (`coefficient_de_conversion.yaml:48`). *(à reprendre, étape 138.11)*
- La loi revalorise les comptes sur la moyenne du PIB nominal des cinq années qui précèdent, avec un plancher « salvo recupero ». *(à reprendre, étape 138.11)*
- Ses diviseurs lisent la mortalité âge par âge (probabilités de l'Istat pour 2023), et des probabilités prospectives pour le conjoint survivant. *(à reprendre, étape 138.7)*
- Son diviseur corrige la fréquence des versements : k = 1/2 − 6/(13n), soit 0,4615 pour douze mensualités d'avance et la treizième. *(à reprendre, étape 138.11)*

**Ses erreurs ou retards (1) :**
- Le taux d'actualisation de 1,5 % (« prevedibile tasso di crescita reale di lungo periodo del PIL ») n'est confirmé qu'en écartant 2008-2009, 2012-2013 et 2020-2021.

### T-DYMM (`t_dymm`)

**Bilan.** Tout ce qu'il fait de mieux demande des microdonnées : départs choisis, population réelle, validation, distribution. Il ne dit rien de l'arithmétique du compte, que l'article ne décrit pas, et son code n'est pas publié.

**Ce qu'il fait mieux que le dépôt :**
- Le départ y est un choix : chaque année, tout éligible compare la valeur de partir et celle d'attendre (option value de Stock et Wise, paramètres estimés pour l'Italie par Belloni et Alessie, 2013), sur salaires et pensions nets, … *(à reprendre, étape 138.14)*
- Il simule une population réelle et se valide sur elle. *(à reprendre, étape 138.14)*
- Il en tire la distribution des retraités : Gini, pauvreté relative, effet redistributif des transferts et de l'impôt, par un module socio-fiscal (IRPEF, minima sociaux). *(à reprendre, étape 138.14)*

### Modèle FUS23 (`fus23`)

**Bilan.** Il fait mieux sur la projection : une population de retraités en décréments multiples, et des sensibilités par paramètre, mortalité comprise. Il rappelle aussi qu'un compte notionnel porte les cotisations que l'État verse pour les périodes de garde d'enfant, ce que le dépôt refuse à l'AVPF.

**Ce qu'il fait mieux que le dépôt :**
- Il projette les retraités par cohorte d'âge et de sexe, sur les données de la ZUS, avec un modèle à décréments multiples (conversion, perte du droit, décès), en trois variantes. *(à reprendre, étape 138.14)*
- Il chiffre l'effet d'une mortalité de ±5 % sur recettes, dépenses et solde, et celui de ±1 point sur chaque hypothèse (salaire réel, chômage, prix, recouvrement, indexation). *(à reprendre, étape 138.7)*
- En Pologne, l'État cotise pour le congé parental, la maternité et la garde d'enfant, et ces sommes entrent dans les recettes de cotisation du fonds. *(à trancher)*

### Le diviseur polonais (`diviseur_pologne`)

**Bilan.** Il fait mieux sur l'arithmétique appliquée : capital initial sans trou, revalorisation trimestrielle l'année du départ, exemple officiel, plancher, taux lu sur une année publiée. Son diviseur sur table du moment est moins exact que celui du dépôt, et son art. 26 ust. 6 ne corrige que ce défaut-là.

**Ce qu'il fait mieux que le dépôt :**
- Son capital initial comble les trous : la pension hypothétique au 1er janvier 1999 est multipliée par l'espérance de vie à 62 ans, avec un prorata sur les 24 % de base ; *(à reprendre, étape 138.11)*
- L'année du départ, la revalorisation y est trimestrielle. *(à reprendre, étape 138.11)*
- Le GUS publie chaque année la table qui fait le diviseur, 222,7 mois à 65 ans en 2026 : un exemple officiel, sans actualisation, que la fiche du diviseur du dépôt n'a pas (`coefficient_de_conversion.yaml:48`). *(à reprendre, étape 138.11)*
- Le compte ne baisse jamais, et sa revalorisation ne passe pas sous les prix : l'indice vaut les prix majorés de la croissance réelle de la somme des cotisations, et il « nie może być niższy » que l'indice des prix. *(à trancher)*
- L'indice du 1er juin de l'année t se lit sur l'année t−1, déjà publiée : les prix et la somme des cotisations de l'année précédente. *(à trancher)*

### Modèle de projection des pensions lettonnes (`modele_lettonie`)

**Bilan.** Ce qu'il fait de mieux est un résultat : la stabilité d'un notionnel de génération face à la longévité, que le dépôt devrait pouvoir retrouver. Le modèle lui-même, une projection agrégée par cellules, est fermé et reconnu imparfait par ses auteurs.

**Ce qu'il fait mieux que le dépôt :**
- Il publie ce que la longévité coûte à un système notionnel de génération : +2 ans d'espérance de vie ne font que +0,1 point de PIB en 2070, et une fécondité de −20 % +0,2 point. *(à reprendre, étape 138.7)*

**Ses erreurs ou retards (1) :**
- Sa fiche reconnaît deux défauts du modèle.

### Le diviseur letton (P = K / G) (`diviseur_lettonie`)

**Bilan.** Ses règles éclairent surtout ce que le dépôt doit trancher : l'assiette qui fait le rendement, les cotisations d'après le départ, le plancher à rattrapage. Son diviseur est de génération comme celui du dépôt, mais interpolé plus grossièrement.

**Ce qu'il fait mieux que le dépôt :**
- Son capital initial se passe d'archives : Ks = Vi × As × 0,2, où Vi est le salaire cotisé de 1996 à 2000, au moins 40 % de la moyenne nationale ; *(à reprendre, étape 138.11)*
- Le capital se revalorise sur la somme des salaires cotisés, et la fiche précise que cette assiette compte les revenus des non-salariés et les cotisations versées par le budget. *(à trancher)*
- Les cotisations versées après le départ entrent au compte : la pension est recalculée automatiquement, au plus tôt tous les douze mois, en ajoutant P = K/G sur le capital accumulé depuis. *(à trancher)*
- La table G du 1er janvier 2026 (17,76 à 65 ans, 18,49 à 64, 19,95 à 62) est un exemple officiel de diviseur unisexe de génération, sans actualisation. *(à reprendre, étape 138.11)*

**Ses erreurs ou retards (1) :**
- G est interpolé linéairement entre les âges quinquennaux : le pas vaut exactement 0,73 an de 60 à 65 ans, puis 0,67-0,68 de 65 à 70.

### Projections de l'Autorité actuarielle nationale (`projections_grece`)

**Bilan.** Sa formule couple rente et revalorisation, et le dépôt l'a reprise ; ce qui reste chez lui relève de choix : suspension de l'indexation en déficit, réversion tarifée, plafond aux prix. Je n'y ai pas trouvé d'erreur.

**Ce qu'il fait mieux que le dépôt :**
- Taux technique et revalorisation y sont couplés : Δt = min[(1+g_{t−2})/(1+r) − 1, CPI_{t−1}], avec r = 1,3 %, la formule de la fiche grecque. *(repris, étape 138.1)*
- L'indexation y est suspendue en cas de déficit. *(à trancher)*
- Sa rente tarifie la réversion : « a whole life annuity is used, taking into account the transfer of pension rights to Assignees (survivors) », recalculée tous les trois ans. *(à trancher)*

### Le fator previdenciário (`fator_previdenciario`)

**Bilan.** Rien de mieux : Es se lit sur la table du moment de l'IBGE, unisexe, sans rendement, que le bonus (Id + Tc·a)/100 remplace ; le dépôt, lui, divise par une table de génération. Le facteur n'est plus qu'une règle de transition, et le registre devrait le dire.

**Ses erreurs ou retards (1) :**
- Le registre le traite comme une variante en usage du diviseur.

### Le coefficient d'espérance de vie finlandais (elinaikakerroin) (`elinaikakerroin`)

**Bilan.** Sa formule est celle du dépôt, au millionième : un exemple officiel tout prêt. Il n'apporte en plus qu'un indicateur, l'âge qui compense la longévité, et une règle d'âge liée à l'espérance de vie, que la proposition n'a pas choisie.

**Ce qu'il fait mieux que le dépôt :**
- Le mémo de l'ETK publie un exemple complet, EAL2024 = 17,718722 et EAK = 0,94692, avec ses quotients ; *(à reprendre, étape 138.11)*
- L'ETK publie pour chaque génération l'âge qui compense le coefficient (« tavoite-eläkeikä ») : 66 ans et 3 mois pour la génération 1962, soit quinze mois de report. *(à reprendre, étape 138.9)*
- Depuis la réforme de 2017, l'âge minimal des générations 1965 et suivantes suit l'espérance de vie. *(à trancher)*

**Ses erreurs ou retards (1) :**
- Son coefficient lit la mortalité des cinq dernières années observées, et ne bouge plus une fois fixé à 62 ans.

## Les organisations internationales

### PROST (Pension Reform Options Simulation Toolkit) (`prost`)

**Bilan.** Il fait mieux sur la transition : diviseur de la génération de l'assuré pour les droits acquis (à trancher), imputation des salaires manquants, indicateurs individuels de cycle de vie. Le dépôt a déjà son équivalent de dette implicite (cout.py:3460-3527) ; l'outil reste non téléchargeable.

**Ce qu'il fait mieux que le dépôt :**
- Il valorise les droits acquis au diviseur de la génération de l'assuré, AF(P_AGE, P_YEAR) avec P_YEAR = T + P_AGE − a (éq. *(à trancher)*
- Il impute les salaires manquants par leur moyenne revalorisée. *(à reprendre, étape 138.11)*
- Il produit, par individu, le taux de remplacement initial (sur le salaire moyen et sur le dernier salaire), le taux de remplacement au décès, le taux de rendement interne réel et la valeur actuelle nette d'être couvert. *(à reprendre, étape 138.9)*

### Les modèles de pension de l'OCDE (`modeles_ocde`)

**Bilan.** Il fait mieux sur les indicateurs : patrimoine retraite, taux nets après impôt, durées de retraite, tous publiés pour la France et lisibles par l'API SDMX. Sur la France, il est à jour : la LFSS pour 2026 ne touche pas ses carrières types.

**Ce qu'il fait mieux que le dépôt :**
- Il calcule le patrimoine retraite, valeur actuelle des pensions à 1,5 % sur une mortalité de cohorte ; *(à reprendre, étape 138.9)*
- Il publie, pour la France et une carrière de 22 à 65 ans, des taux de remplacement bruts de 56,6, 56,6 et 47,4 % à 0,5, 1 et 2 salaires moyens, un taux net de 70,0 %, un patrimoine retraite de 11,5 années de salaire pour les … *(à reprendre, étape 138.9)*
- Son taux de remplacement net compte l'impôt et les cotisations sur le salaire comme sur la pension : 70,0 % net contre 56,6 % brut au salaire moyen. *(à reprendre, étape 138.2)*
- Il publie les âges et les durées de la retraite. *(à reprendre, étape 138.9)*

### Ageing Report et ses fiches pays (`ageing_report`)

**Bilan.** Il fait mieux sur l'analyse de la dépense : décomposition, scénarios standard, rétro-évaluation de ses propres projections, dépense nette. Sur la France, il est antérieur à la suspension de 2025.

**Ce qu'il fait mieux que le dépôt :**
- Il décompose la dépense en dépendance, couverture, prestation et marché du travail ; *(à reprendre, étape 138.3)*
- Pour la France, il projette 14,4 % du PIB en 2022 et 13,6 % en 2070 : dépendance +6,0 points, couverture −2,2, prestation −3,4, un ratio de prestation qui passe de 47 à 37 %. *(à reprendre, étape 138.3)*
- Il soumet la projection à des scénarios standard. *(à reprendre, étape 138.7)*
- Il décompose aussi le flux des pensions nouvelles : nombre, durée de cotisation, taux d'acquisition, salaire de référence, facteur de soutenabilité, mois servis la première année. *(à reprendre, étape 138.3)*
- Il confronte sa projection précédente à l'observé et décompose l'erreur. *(à reprendre, étape 138.19)*
- Il publie la dépense nette d'impôts et de cotisations des retraités (12,8 % du PIB en 2022, 12,1 % en 2070, contre 14,4 et 13,6 en brut), les cotisations (11,1 %) et le solde (−3,3 %). *(à reprendre, étape 138.3)*

**Ses erreurs ou retards (1) :**
- La fiche France projette la loi du 14 avril 2023 entière (§ 3.3 et tableau 14 : la réforme « should reduce the number of pensioners by 1.3% in 2040 »).

### ILO/PENSIONS (`ilo_pensions`)

**Bilan.** Il fait mieux sur la projection actuarielle : une population par états et ses transitions, et les taux de cotisation d'équilibre. Il n'est pas ouvert, et son guide technique de 2018 suffit à en confronter la méthode.

**Ce qu'il fait mieux que le dépôt :**
- Il projette des flux par cohorte, année par année, avec des probabilités de transition entre états (décès, retraite, retrait, entrées), une densité de cotisation, un taux de couverture et un facteur de recouvrement, sur la … *(à reprendre, étape 138.14)*
- Il calcule le taux de cotisation qui équilibre la répartition, décomposé en rapport de dépendance du système (pensionnés sur cotisants) fois rapport de remplacement du système (pension moyenne sur revenu assuré moyen). *(à reprendre, étape 138.19)*

### OG-Core (`og_core`)

**Bilan.** Rien de mieux sur l'arithmétique : son diviseur est stationnaire, et la réversion et la fréquence de versement n'y sont que des paramètres nuls par défaut. Son seul apport possible, l'équilibre général, est hors du champ du dépôt, et faussé par une marge du travail qui traite la cotisation notionnelle en impôt.

**Ses erreurs ou retards (3) :**
- La condition du travail ignore la pension notionnelle : le coin fiscal vaut 1 − tau_payroll − MTR (household.py:760-780).
- tax.py:303-305 passe Y = 1 à pension_amount, avec le commentaire « TODO: replace '1' with Y ».
- Le coefficient de conversion prend la mortalité stationnaire de fin de période (p.rho[-1]) pour toutes les cohortes, et un âge de départ unique (issue #1014).
