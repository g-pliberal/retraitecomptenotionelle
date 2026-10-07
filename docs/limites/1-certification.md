# 1. État de certification des données

La page **Données** du site affiche l'état exact, et date chaque série du jour
où elle a été relue contre sa source (`verifiee_le` dans le journal, §6). En
résumé :

| Donnée | Période | Niveau | Source |
|---|---|---|---|
| Inflation (IPC) | <!--chiffre:minimum(data/reference/macro/ipc_annuel.csv:annee?fiabilite=certifiee)-->1950<!--/-->-<!--chiffre:maximum(data/reference/macro/ipc_annuel.csv:annee?fiabilite=certifiee)-->2025<!--/--> | **certifiée** | INSEE BDM, idbanks 000008965 et 001764363 |
| Inflation | <!--chiffre:minimum(data/reference/macro/ipc_annuel.csv:annee?fiabilite=estimee)-->1930<!--/-->-<!--chiffre:maximum(data/reference/macro/ipc_annuel.csv:annee?fiabilite=estimee)-->1949<!--/--> | estimée | reconstitution, dérive cumulée recoupée à l'INSEE idbank 010605954 (1901-) |
| Salaire moyen par tête | <!--chiffre:minimum(data/reference/macro/salaire_moyen.csv:annee?fiabilite=certifiee)-->1950<!--/-->-<!--chiffre:maximum(data/reference/macro/salaire_moyen.csv:annee?fiabilite=certifiee)-->2025<!--/--> | **certifiée** | INSEE BDM, idbanks 011785411 et 011793486 |
| Salaire moyen par tête | <!--chiffre:minimum(data/reference/macro/salaire_moyen.csv:annee?fiabilite=estimee)-->1930<!--/-->-<!--chiffre:maximum(data/reference/macro/salaire_moyen.csv:annee?fiabilite=estimee)-->1949<!--/--> | estimée | reconstitution |
| Productivité réelle | <!--chiffre:minimum(data/reference/macro/productivite.csv:annee?fiabilite=certifiee)-->1950<!--/-->-<!--chiffre:maximum(data/reference/macro/productivite.csv:annee?fiabilite=certifiee)-->2025<!--/--> | **certifiée** | INSEE BDM, idbanks 011785223 et 011793334 |
| Productivité réelle | <!--chiffre:minimum(data/reference/macro/productivite.csv:annee?fiabilite=estimee)-->1930<!--/-->-<!--chiffre:maximum(data/reference/macro/productivite.csv:annee?fiabilite=estimee)-->1949<!--/--> | estimée | reconstitution |
| Produit intérieur brut, en niveau | <!--chiffre:minimum(data/reference/macro/pib_courant.csv:annee?fiabilite=certifiee)-->1949<!--/-->-<!--chiffre:maximum(data/reference/macro/pib_courant.csv:annee?fiabilite=certifiee)-->2025<!--/--> | **certifiée** | INSEE BDM, idbank 011779992 |
| Profil de salaire par tranche d'âge | <!--chiffre:minimum(data/reference/macro/profil_salaire_age.csv:annee?fiabilite=certifiee)-->1962<!--/-->-<!--chiffre:maximum(data/reference/macro/profil_salaire_age.csv:annee?fiabilite=certifiee)-->2024<!--/--> | **certifiée** | INSEE Melodi, DS_DERA_PRIVE_SERIES_LONGUES |
| Profil de salaire par âge et catégorie | 2024 | **certifiée** | INSEE Melodi, DS_DERA_PRIVE_ANNUEL |
| Profil de salaire public par âge et statut | 2023 | **certifiée** | INSEE Melodi, DS_DERA_PUBLIC_ANNUEL |
| Profil de salaire par âge et secteur | 2018, 2022 | **certifiée** | Eurostat, enquête sur la structure des salaires |
| Population par âge, <!--chiffre:minimum(data/reference/macro/population_par_age.csv:age)-->50<!--/--> ans et plus | <!--chiffre:minimum(data/reference/macro/population_par_age.csv:annee?fiabilite=certifiee)-->1962<!--/-->-<!--chiffre:maximum(data/reference/macro/population_par_age.csv:annee?fiabilite=certifiee)-->2023<!--/--> | **certifiée** | INSEE, estimations de population (classeur des projections 2026) |
| Population par âge, <!--chiffre:minimum(data/reference/macro/population_par_age.csv:age)-->50<!--/--> ans et plus | <!--chiffre:minimum(data/reference/macro/population_par_age.csv:annee?fiabilite=projetee)-->2024<!--/-->-<!--chiffre:maximum(data/reference/macro/population_par_age.csv:annee?fiabilite=projetee)-->2070<!--/--> | projetée | INSEE, projections de population 2026, scénario central |
| Population des 20-64 ans | 1962-2023 / 2024-2070 | **certifiée** / projetée | mêmes sources |
| Dépenses de vieillesse-survie, tous régimes | <!--chiffre:minimum(data/reference/macro/depenses_retraite.csv:annee?fiabilite=certifiee)-->1959<!--/-->-<!--chiffre:maximum(data/reference/macro/depenses_retraite.csv:annee?fiabilite=certifiee)-->2024<!--/--> | **certifiée** | DREES, Comptes de la protection sociale, poste E11-2 |
| Dépenses de vieillesse-survie, par système | <!--chiffre:minimum(data/reference/macro/depenses_retraite_regimes.csv:annee?fiabilite=certifiee)-->1990<!--/-->-<!--chiffre:maximum(data/reference/macro/depenses_retraite_regimes.csv:annee?fiabilite=certifiee)-->2024<!--/--> | **certifiée** | DREES, mêmes comptes, ventilation par organisme |
| Dépenses de vieillesse-survie, par système | 1981-1989 | absentes | nomenclature d'alors sans raccord publié — voir §5 bis |
| Retraités de droit direct, par caisse | 2004-2024, <!--chiffre:distinctes(data/reference/regimes/effectifs_retraites.csv:caisse)-->27<!--/--> séries, les caisses et le total tous régimes | **certifiée** | DREES, enquête annuelle auprès des caisses de retraite, fichier diffusé |
| Retraités de droit direct, par caisse | hors 2004-2024 | estimée | la répartition du bord est reconduite — voir §5 bis |
| Distribution des pensions mensuelles brutes de droit direct | fin 2020, <!--chiffre:distinctes(data/reference/macro/distribution_pensions.csv:borne_mensuelle?sexe=ensemble)-->46<!--/--> tranches | **certifiée** | DREES, échantillon interrégimes de retraités 2020, tableau 1 |
| Patrimoine des ménages : déciles, moyennes et médianes par âge | début 2021 et début 2024 | **haute** | INSEE, enquête Histoire de vie et Patrimoine, Insee Focus n° 287 et page « Distribution du patrimoine des ménages », classeurs lus par script |
| Mode de résidence après <!--chiffre:minimum(data/reference/macro/vie_en_couple.csv:age)-->65<!--/--> ans, par âge et par sexe | 2021, <!--chiffre:distinctes(data/reference/macro/vie_en_couple.csv:age)-->36<!--/--> âges | **haute** | INSEE, recensement 2021, *Insee Première* n° 2040, figure 2, classeur lu par script |
| Patrimoine des ménages retraités selon leur revenu disponible | 2018, <!--chiffre:lignes_csv(data/reference/macro/patrimoine_menages.csv?source_id=cor_patrimoine_retraites)-->6<!--/--> valeurs | **saisie** | COR, « Le patrimoine des retraités », séance du 16 décembre 2021, sur l'enquête Patrimoine 2018 — les graphiques du PDF ne se lisent pas |
| Hypothèses de projection | 2026-2100 | **saisie** | COR, rapport annuel de juin 2025, jeu reconduit en juin 2026 |
| Emploi projeté (croissance de l'emploi, dérivée) | 2026-2070 | **saisie** | COR, rapport annuel de juin 2026, données de la partie 1 : population active et chômage du scénario de référence |
| Espérance de vie à 0 et <!--chiffre:illustration()-->60<!--/--> ans | <!--chiffre:minimum(data/reference/mortalite/esperances_vie.csv:annee?mesure=e0&fiabilite=certifiee)-->1946<!--/-->-<!--chiffre:maximum(data/reference/mortalite/esperances_vie.csv:annee?mesure=e0&fiabilite=certifiee)-->2025<!--/--> | **certifiée** | INSEE BDM, quatre idbanks, annuel par sexe |
| Espérance de vie à <!--chiffre:illustration()-->65<!--/--> ans | 1960-2024 | **certifiée** | OCDE `DSD_HEALTH_STAT@DF_LE` |
| Espérance de vie à <!--chiffre:illustration()-->65<!--/--> ans | 1946-1959 | haute | **dérivée** des quotients INED, recalculée à chaque exécution |
| Espérances de vie e0, e60, e65 | 2026-2125 | projetée | **dérivée** des quotients projetés par l'INSEE, projections 2026 |
| Espérance de vie par vingtile de niveau de vie, e0, e60, e65 | 2012-2016 et 2020-2024 | haute | INSEE, tables de mortalité par niveau de vie (Insee Résultats 2025), lues telles quelles, l'ensemble contrôlé contre la série certifiée |
| Espérance de vie à <!--chiffre:illustration()-->65<!--/--> ans des fonctionnaires civils de l'État | 2024 | **saisie** | Service des retraites de l'État, PAP 741 du PLF 2026, apporté par l'utilisateur |
| Quotients de mortalité par âge | 1986-2024 | **certifiée** | Eurostat `demo_mlifetable`, âges 0-<!--chiffre:maximum(data/reference/mortalite/quotients_periode.csv:age?annee=2024)-->94<!--/--> depuis 2014, 0-<!--chiffre:maximum(data/reference/mortalite/quotients_periode.csv:age?annee=2010)-->84<!--/--> de 1998 à 2013 |
| Quotients de mortalité par âge | 1899-1985 | **certifiée** | INED, tables de Vallin et Meslé, âges 0-104 |
| Quotients de mortalité par âge | 1986-1997, jusqu'à <!--chiffre:maximum(data/reference/mortalite/quotients_periode.csv:age?annee=1990)-->104<!--/--> ans | **certifiée** | INED, là où Eurostat s'arrête |
| Quotients de mortalité par âge | après 1997, au-delà de <!--chiffre:maximum(data/reference/mortalite/quotients_periode.csv:age?annee=2010)-->84<!--/--> ans jusqu'en 2013 et de <!--chiffre:maximum(data/reference/mortalite/quotients_periode.csv:age?annee=2024)-->94<!--/--> ans depuis | absents | calibration paramétrique, dont le biais est mesuré |
| Minimum contributif et plafond d'écrêtement | ancres de 1983 à 2023, à leur date | **certifiée** | DILA, base LEGI, code de la sécurité sociale, R. 351-25, D. 351-2-1 et D. 173-21-0-0-1 |
| Minimum contributif, minimum majoré et plafond | chaque revalorisation entre les ancres, de 1984 à juin 2026 | haute | barèmes de la Cnav, que le récupérateur refuse s'ils ne redonnent pas les ancres du code au centime ; recoupés contre les circulaires que transcrit OpenFisca-France-Pension, jusqu'en 2023, et contre la réponse ministérielle de 2020 |
| Minimum vieillesse (ASPA) | ancres 2006, 2009-2012, 2014, 2018-2020 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `D. 815-1` |
| Minimum vieillesse (ASPA) | ancres 2007, 2016, 2017, depuis 2021 | haute / moyenne | publications — l'article n'est pas réécrit à chaque revalorisation |
| Minimum vieillesse (ASPA) d'un couple | ancres 2006, 2009, 2014, 2018-2020 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `D. 815-1`, b |
| Minimum vieillesse (ASPA) d'un couple | les quinze autres années, 2007 à 2026 | haute | barèmes de la Cnav, que le récupérateur refuse s'ils ne redonnent pas au centime les montants de l'article |
| Minimum garanti, traitement de référence | 2004 et année courante | **certifiée** | Service des retraites de l'État, sa page du minimum garanti |
| Minimum garanti, traitement de référence | ancres intermédiaires | haute | non publiées : la page ne porte que l'ancre et l'année courante |
| Âge d'ouverture des droits par génération | <!--chiffre:minimum(data/reference/legislation/age_ouverture_requis.csv:generation?fiabilite=certifiee)-->1900<!--/-->-<!--chiffre:maximum(data/reference/legislation/age_ouverture_requis.csv:generation?fiabilite=certifiee)-->1975<!--/--> | **certifiée** | DILA, base LEGI, code de la sécurité sociale `D. 161-2-1-9` |
| Durée d'assurance requise par génération | 1958-1975 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `L. 161-17-3` |
| Durée d'assurance requise par génération | 1953-1957 | **certifiée** | DILA, base LEGI, décrets d'application des lois de 2003 et de 2010 |
| Durée d'assurance requise par génération | 1934-1942 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `R. 351-45` II |
| Durée d'assurance requise par génération | 1943-1952 | haute | 160 vient de la règle générale, non d'un alinéa qui les nomme ; les 161-164 sont dans des décrets absents de la base — recoupées à chaque exécution contre la table d'OpenFisca-France-Pension |
| Durée de services de la fonction publique, droits ouverts 2004-2008 | <!--chiffre:minimum(data/reference/legislation/duree_requise_fonction_publique.csv:trimestres)-->152<!--/--> à <!--chiffre:maximum(data/reference/legislation/duree_requise_fonction_publique.csv:trimestres)-->160<!--/--> trimestres | haute | loi n° 2003-775, article 66 II, lu dans la base LEGI et mis en table ; recoupé contre OpenFisca-France-Pension |
| Coefficient de minoration par génération | <!--chiffre:minimum(data/reference/legislation/coefficient_minoration.csv:generation?fiabilite=certifiee)-->1900<!--/-->-<!--chiffre:maximum(data/reference/legislation/coefficient_minoration.csv:generation?fiabilite=certifiee)-->1975<!--/--> | **certifiée** | DILA, base LEGI, code de la sécurité sociale `R. 351-27` |
| Bornes de la carrière longue | 2023-, règle générale et borne des vingt ans par génération | **certifiée** | DILA, base LEGI, `L. 351-1-1` et `D. 351-1-1` (I et II, versions de 2023 et de 2026, lues à leur date d'effet) |
| Bornes de la carrière longue | 2004, 2011 et 2012, par génération | **certifiée** | DILA, base LEGI, versions abrogées de `D. 351-1-1` que l'index expose |
| Durée maximale prise en compte par la proratisation | avant 1944 à 1947 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `R. 351-6` II |
| Heures de SMIC à cotiser pour valider un trimestre | 1972 et 2014 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `R. 351-9` |
| Années retenues au salaire annuel moyen, par génération | avant 1934 à 1948 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `R. 351-29-1` |
| Années retenues au revenu annuel moyen des artisans et commerçants, par génération | avant 1934 à 1953 | **certifiée** | DILA, base LEGI, code de la sécurité sociale `R. 634-1-1` |
| Décote de la fonction publique, coefficient et âge d'annulation | <!--chiffre:minimum(data/reference/legislation/decote_fonction_publique.csv:annee?fiabilite=certifiee)-->2006<!--/-->-<!--chiffre:maximum(data/reference/legislation/decote_fonction_publique.csv:annee?fiabilite=certifiee)-->2019<!--/--> | **certifiée** | DILA, base LEGI, loi n° 2003-775 du 21 août 2003, article 66 III |
| Barème du minimum garanti, montée en charge | <!--chiffre:minimum(data/reference/legislation/minimum_garanti.csv:annee?fiabilite=certifiee)-->2004<!--/-->-<!--chiffre:maximum(data/reference/legislation/minimum_garanti.csv:annee?fiabilite=certifiee)-->2013<!--/--> | **certifiée** | DILA, base LEGI, loi n° 2003-775 du 21 août 2003, article 66 V |
| Âge d'annulation de la décote, régime général | 1930-1955 | haute | calculé — l'âge d'ouverture certifié majoré de cinq ans, comme l'écrit `L. 351-8` ; recontrôlé à chaque exécution, et recoupé contre la table transcrite d'OpenFisca-France-Pension |
| Point d'indice de la fonction publique | <!--chiffre:minimum(data/reference/legislation/point_indice_fonction_publique.csv:annee?fiabilite=certifiee)-->1996<!--/-->-<!--chiffre:maximum(data/reference/legislation/point_indice_fonction_publique.csv:annee?fiabilite=certifiee)-->2027<!--/--> | **certifiée** | DILA, base LEGI, décret n° 85-1148 du 24 octobre 1985, article 3 |
| Point d'indice de la fonction publique | <!--chiffre:minimum(data/reference/legislation/point_indice_fonction_publique.csv:annee?fiabilite=haute)-->1960<!--/-->-<!--chiffre:maximum(data/reference/legislation/point_indice_fonction_publique.csv:annee?fiabilite=haute)-->1995<!--/--> | haute | OpenFisca-France, `point_indice_en_euros` — deux versions manquent au dump avant 1996 |
| SMIC horaire | 1997-2017, sauf 2002 | **certifiée** | DILA, base LEGI, décrets portant relèvement du SMIC |
| SMIC horaire | 1970-1996, 2002 et depuis 2018 | haute | OpenFisca-France, `smic_horaire_brut` |
| SMIC annuel à temps complet, le revenu du cas type au SMIC | <!--chiffre:minimum(data/reference/macro/smic_annuel.csv:annee?fiabilite=certifiee)-->1951<!--/-->-<!--chiffre:maximum(data/reference/macro/smic_annuel.csv:annee?fiabilite=certifiee)-->2025<!--/--> | **certifiée** | INSEE, séries longues sur les salaires (tableaux SM02 et SM01) jusqu'en 2012, puis BDM, idbank 000822484, qui les refait au centime ; la garantie mensuelle de rémunération des années 2000 à 2005 n'y est pas |
| Salaire moyen par tête, en niveau | <!--chiffre:minimum(data/reference/macro/salaire_moyen_niveau.csv:annee?fiabilite=certifiee)-->1949<!--/-->-<!--chiffre:maximum(data/reference/macro/salaire_moyen_niveau.csv:annee?fiabilite=certifiee)-->2025<!--/--> | **certifiée** | INSEE BDM, idbanks 011785411 et 011793486 : le niveau de 2024 ancre le cumul des croissances |
| Plafond Sécurité sociale | 2002-2025 | **certifiée** | INSEE BDM, idbank 000822494 |
| Plafond Sécurité sociale | 1963, 1965-1981, 1984, 1987, 1988, 1990-1993, 1996-2001 | **certifiée** | DILA, base JORF, décrets portant fixation du plafond |
| Plafond Sécurité sociale | le reste de 1931-2001 | haute | OpenFisca-France, daté décret par décret — la notice ancienne du JORF n'a pas d'écriture stable |
| Revalorisation des salaires portés au compte | <!--chiffre:distinctes(data/reference/legislation/revalorisation_salaires.csv:date_effet)-->10<!--/--> colonnes, effets 2017-2026, perceptions depuis 1930 | haute | Cnav, circulaires de revalorisation, recoupées deux à deux |
| Taux de cotisation, régime général | <!--chiffre:minimum(data/reference/regimes/taux_cotisation_annuels.csv:annee?regime=regime_general&fiabilite=certifiee)-->1982<!--/-->-<!--chiffre:maximum(data/reference/regimes/taux_cotisation_annuels.csv:annee?regime=regime_general&fiabilite=certifiee)-->2026<!--/--> | **certifiée** | DILA, base LEGI, code de la sécurité sociale `D. 242-4` et décret n° 81-1013 du 13 novembre 1981, article 2 ; la hausse temporaire de 1987-1988, qui n'a pas réécrit l'article, est lue dans la base JORF |
| Taux de cotisation, régime général | 1967-1979 | haute | OpenFisca-France, transcrit des barèmes IPP — l'article 3 du décret n° 67-803 n'a qu'une version dans LEGI, datée de 1967 et portant l'état de 1979. Chaque marche est **ancrée** à son décret, retrouvé au JORF au numéro et à la date que l'IPP annonce (35 sur 36 ; le n° 70-680 manque à l'index) |
| Taux de cotisation, régime général | 1980 et 1981 | haute, **comme leurs voisines** | le décret n° 79-650 du 30 juillet 1979 a relevé des taux « à titre exceptionnel » du 1er août 1979 au 31 janvier 1981 : c'est le point du plan Barrot, porté par la seule cotisation MALADIE du salarié, et la vieillesse n'y est pas — voir plus bas |
| Taux de cotisation, salariés agricoles | <!--chiffre:minimum(data/reference/regimes/taux_cotisation_annuels.csv:annee?regime=msa_salaries&fiabilite=certifiee)-->1980<!--/-->-<!--chiffre:maximum(data/reference/regimes/taux_cotisation_annuels.csv:annee?regime=msa_salaries&fiabilite=certifiee)-->2026<!--/--> | **certifiée** | DILA, base LEGI, décret n° 50-444 du 20 avril 1950, article 2, puis code rural `D. 741-35`, qui renvoie à `D. 242-4` depuis 2014 |
| Taux de cotisation, salariés agricoles | 1967-1979 | moyenne | la série du régime général tenant lieu, faute d'une version antérieure de l'article 2 |
| Taux de cotisation, cultes, Mayotte, Saint-Pierre-et-Miquelon | depuis 1979 et 1987 | haute | la série du régime général du dépôt, que ces trois régimes portent faute d'un barème propre : la valeur est certifiée, la substitution est une décision de modélisation. Les cultes avaient pourtant le leur de 1979 à 1997, des montants forfaitaires que des arrêtés annuels fixaient (décret n° 79-607, art. 24 et 25), que le modèle ne lit pas |
| Taux de cotisation, complémentaires du privé | Arrco 1962-2018, Agirc 1981-2018, Agirc-Arrco 2019- | moyenne | OpenFisca-France, taux effectifs par tranche, recoupés à chaque exécution. **Ne se certifieront pas** : ces taux sont fixés par accord collectif, l'IPP — source amont d'OpenFisca — laisse lui-même la colonne du *Journal officiel* vide pour chacune de leurs 25 marches, et le JO ne publie que l'avis d'extension, qui renvoie au Bulletin officiel sans écrire le chiffre |
| Retenue pour pension, État, CNRACL, ouvriers de l'État | 1948-2026, une période par taux | moyenne | OpenFisca-France, article L. 61 et barème de la caisse, recoupés à chaque exécution |
| Cotisation vieillesse de base des artisans et commerçants | 1973-2018, moyennes par période | moyenne | OpenFisca-France, décrets d'application de la loi du 3 juillet 1972, recoupés à chaque exécution |
| Taux de cotisation, autres régimes | tous | moyenne / estimée | Comptes de la Sécurité sociale |
| Répartition salarié/employeur, régime général | 1968-2026 | haute | OpenFisca-France, recoupée à chaque exécution |
| Répartition salarié/employeur, autres régimes de salariés | toutes | moyenne / estimée | OpenFisca et textes ; règle 40-60 pour les complémentaires |
| Contribution employeur, État | <!--chiffre:minimum(data/reference/legislation/contribution_employeur_public.csv:annee?regime=fonction_publique_etat&fiabilite=certifiee)-->2006<!--/-->-<!--chiffre:maximum(data/reference/legislation/contribution_employeur_public.csv:annee?regime=fonction_publique_etat&fiabilite=certifiee)-->2026<!--/--> | **certifiée** | Service des retraites de l'État, fiche « Historique des taux de cotisations » |
| Contribution employeur, État (implicite) | 1995-2005 | haute | OpenFisca-France, jaune « pensions » du PLF 2011 — reconstitution dont le producteur refuse les requêtes automatisées |
| Contribution employeur, CNRACL | 1993-2028 | **certifiée** | DILA, base LEGI, décret n° 91-613 du 28 juin 1991, article 5 II |
| Contribution employeur, CNRACL | 1984-1988 | **certifiée** | DILA, base LEGI, décret n° 47-1846 du 19 septembre 1947, article 3 |
| Contribution employeur, CNRACL | 1948-1983, 1989-1992 | haute | OpenFisca-France — la chaîne des versions de l'article 3 est trouée, et la base le démontre |
| Contribution employeur, SNCF (T1 + T2) | 2007-2011 | **certifiée** | DILA, arrêtés annuels du taux T1 (base JORF) et décret n° 2007-1056, article 2 IV (base LEGI) |
| Contribution employeur, SNCF (T1 + T2) | 2012-2018 | haute | OpenFisca-France — le décret cesse de chiffrer T2 après 2011 et le fait évoluer par formule |
| Valeurs d'achat et de service du point, Ircantec | <!--chiffre:minimum(data/reference/regimes/valeurs_point.csv:annee?regime=ircantec&fiabilite=certifiee)-->1971<!--/-->-<!--chiffre:maximum(data/reference/regimes/valeurs_point.csv:annee?regime=ircantec&fiabilite=certifiee)-->2021<!--/--> | **certifiée** | Caisse des dépôts, qui gère le régime |
| Valeurs d'achat et de service du point, Agirc | <!--chiffre:minimum(data/reference/regimes/valeurs_point.csv:annee?regime=agirc&fiabilite=certifiee)-->1947<!--/-->-<!--chiffre:maximum(data/reference/regimes/valeurs_point.csv:annee?regime=agirc&fiabilite=certifiee)-->2018<!--/--> | **certifiée** | Fédération Agirc-Arrco, sa compilation des valeurs de point |
| Valeurs d'achat et de service du point, Arrco | <!--chiffre:minimum(data/reference/regimes/valeurs_point.csv:annee?regime=arrco&fiabilite=certifiee)-->1999<!--/-->-<!--chiffre:maximum(data/reference/regimes/valeurs_point.csv:annee?regime=arrco&fiabilite=certifiee)-->2018<!--/--> | **certifiée** | Fédération Agirc-Arrco, la même compilation |
| Valeurs d'achat et de service du point, UNIRS | <!--chiffre:minimum(data/reference/regimes/valeurs_point.csv:annee?regime=unirs&fiabilite=certifiee)-->1961<!--/-->-<!--chiffre:maximum(data/reference/regimes/valeurs_point.csv:annee?regime=unirs&fiabilite=certifiee)-->1998<!--/--> | **certifiée** | Fédération Agirc-Arrco, la même compilation |
| Valeurs du point, Arrco avant 1999 | 1949-1998 | moyenne | l'UNIRS tenant lieu d'Arrco : la valeur est certifiée, la substitution reste une décision du dépôt |
| Valeurs d'acquisition et de service du point, RAFP | <!--chiffre:minimum(data/reference/regimes/valeurs_point.csv:annee?regime=rafp&fiabilite=certifiee)-->2005<!--/-->-<!--chiffre:maximum(data/reference/regimes/valeurs_point.csv:annee?regime=rafp&fiabilite=certifiee)-->2026<!--/--> | **certifiée** | ERAFP, dont le conseil d'administration les fixe |
| Valeurs d'achat et de service du point, autres | RCI 2013-2023, IGRANTE et IPACTE 1947-2022 | haute | OpenFisca-France-Pension |
| Valeurs du point, complémentaire des avocats | <!--chiffre:minimum(data/reference/regimes/valeurs_point.csv:annee?regime=cnbf_complementaire&fiabilite=certifiee)-->2017<!--/-->-<!--chiffre:maximum(data/reference/regimes/valeurs_point.csv:annee?regime=cnbf_complementaire&fiabilite=certifiee)-->2026<!--/--> | **certifiée** | CNBF, ses barèmes annuels |
| Valeur du point, base des professions libérales | <!--chiffre:minimum(data/reference/regimes/valeurs_point.csv:annee?regime=cnavpl&mesure=valeur_service&fiabilite=certifiee)-->2004<!--/-->-<!--chiffre:maximum(data/reference/regimes/valeurs_point.csv:annee?regime=cnavpl&mesure=valeur_service&fiabilite=certifiee)-->2026<!--/--> | **certifiée** | CNAVPL, ses recueils statistiques |
| Taux des deux tranches, base des professions libérales | <!--chiffre:minimum(data/reference/regimes/valeurs_point.csv:annee?regime=cnavpl&mesure=taux_t1&fiabilite=certifiee)-->2020<!--/-->-<!--chiffre:maximum(data/reference/regimes/valeurs_point.csv:annee?regime=cnavpl&mesure=taux_t1&fiabilite=certifiee)-->2026<!--/--> | **certifiée** | CNAVPL, le tableau des cotisations de ses recueils, exercice par exercice |
| Valeur de service du point, complémentaire agricole | <!--chiffre:minimum(data/reference/regimes/valeurs_point.csv:annee?regime=msa_rco&fiabilite=certifiee)-->2005<!--/-->-<!--chiffre:maximum(data/reference/regimes/valeurs_point.csv:annee?regime=msa_rco&fiabilite=certifiee)-->2025<!--/--> | **certifiée** | DILA, base LEGI, code rural `D. 732-166` |
| Valeur du point, base agricole et valeurs d'achat RCO | — | absentes | hors du code ; voir plus bas |

**Comment la certification fonctionne.** Une valeur n'est `certifiee` que si
elle a été confrontée à un fichier téléchargé depuis le producteur. Le circuit
est le même pour toutes les séries : récupérer, puis confronter.

```bash
python scripts/fetch/insee_bdm.py              # séries longues INSEE
python scripts/fetch/oecd_esperance_vie.py     # espérance de vie à 65 ans
python scripts/fetch/eurostat_mortalite.py     # tables de mortalité par âge
python scripts/fetch/openfisca_plafond.py      # plafond ancien
python scripts/fetch/openfisca_cotisations.py  # taux de cotisation du RG, du public, des non-salariés
python scripts/fetch/openfisca_minimum_contributif.py  # montants du minimum contributif
python scripts/fetch/openfisca_parametres_generation.py  # durée requise, âge d'annulation, par génération
python scripts/fetch/openfisca_points.py       # valeurs du point, depuis 1947
python scripts/fetch/cdc_ircantec.py           # barèmes Ircantec, par son gestionnaire
python scripts/fetch/cnbf_baremes.py           # valeurs du point des avocats
python scripts/fetch/cnavpl_recueils.py        # valeur du point des professions libérales
python scripts/fetch/dila_legi_msa.py          # point de la complémentaire agricole (index LEGI)
python scripts/fetch/dila_legi_minimum_contributif.py  # minimum contributif et plafond (index LEGI)
python scripts/fetch/cnav_minimum_contributif.py  # montants servis entre les ancres, barèmes de la Cnav
python scripts/fetch/dila_legi_parametres_retraite.py   # âges, durées, décotes par génération : lit l'index LEGI, en secondes
python scripts/fetch/openfisca_point_indice.py  # point d'indice et barème du minimum garanti
python scripts/fetch/dila_legi_point_indice.py # point d'indice, dans son décret (index LEGI)
python scripts/fetch/dila_legi_smic.py         # SMIC, dans ses décrets de relèvement (index LEGI)
python scripts/fetch/dila_legi_duree_requise.py # durée requise des générations 1953-1957 (index LEGI)
python scripts/fetch/dila_legi_cnracl.py       # contribution employeur de la CNRACL (index LEGI)
python scripts/fetch/dila_legi_contribution_employeur.py  # part patronale de six régimes spéciaux (index, rapide)
python scripts/fetch/dila_legi_decote_fonction_publique.py  # décote de la fonction publique (index LEGI)
python scripts/fetch/dila_legi_minimum_garanti.py  # barème du minimum garanti (index LEGI)
python scripts/fetch/erafp_valeurs_point.py    # valeurs du point du RAFP, par l'ERAFP
python scripts/fetch/jorf_plafond_securite_sociale.py  # plafond ancien, dans ses décrets (index JORF)
python scripts/fetch/sncf_contribution_employeur.py  # contribution SNCF, dans les deux index
python scripts/fetch/dila_legi_minimum_vieillesse.py  # montants de l'ASPA, seule et en couple, dans le code (index LEGI)
python scripts/fetch/cnav_minimum_vieillesse.py  # ASPA du couple entre les ancres, barèmes de la Cnav
python scripts/fetch/sre_minimum_garanti.py     # référence du minimum garanti, par le service qui la sert
python scripts/fetch/ined_vallin_mesle.py      # quotients de mortalité d'avant 1986
python scripts/fetch/insee_projections_mortalite.py  # espérances de vie projetées, jusqu'en 2125
python scripts/fetch/eurostat_hicp.py          # contrôle croisé de l'inflation

python scripts/verifier_donnees.py             # confronte, sans rien écrire
python scripts/verifier_donnees.py --appliquer # aligne sur la source et certifie
```

`data/brut/` n'est pas versionné : c'est `data/derive/certification.json` qui
garde la trace du dernier recontrôle — quelle source, quel jour, combien de
valeurs, à quel niveau, et une empreinte de la série reconstruite.

**Les hypothèses de projection ne sont pas certifiables par script, et il faut
le dire.** `verifier_donnees.py` confronte des séries à un producteur ; une
hypothèse de long terme n'a pas de producteur, elle a un auteur. Le fichier
`data/reference/macro/hypotheses_projection.yaml` transcrit donc le jeu du COR
— référence <!--chiffre:valeur(data/reference/macro/hypotheses_projection.yaml:scenarios.cor_reference.productivite_reelle*100)-->0,7<!--/--> %, variantes <!--chiffre:valeur(data/reference/macro/hypotheses_projection.yaml:scenarios.cor_productivite_basse.productivite_reelle*100)-->0,4<!--/--> % et <!--chiffre:valeur(data/reference/macro/hypotheses_projection.yaml:scenarios.cor_productivite_haute.productivite_reelle*100)-->1,0<!--/--> % de croissance annuelle de la
productivité — en nommant son millésime, et rien ne garantit qu'il suive le
prochain rapport autrement qu'à la main. Deux réserves s'y ajoutent : le taux
est appliqué dès 2026 quand le COR ne l'atteint qu'en 2040, et l'inflation de
<!--chiffre:valeur(data/reference/macro/hypotheses_projection.yaml:scenarios.cor_reference.inflation*100)-->1,75<!--/--> % est une convention reconduite de ses rapports antérieurs, que les
documents publics de juin 2025 et de juin 2026 ne restatent pas.

**Deux niveaux, deux exigences.** `certifiee` suppose que la source soit le
**producteur** de la donnée : INSEE, Eurostat, OCDE. Une transcription tierce,
même sourcée et reprise automatiquement, plafonne à `haute` — c'est le cas des
années du plafond ancien dont le décret n'a pas été lu, et qui viennent
d'OpenFisca-France. La distinction n'est pas cosmétique : elle dit ce qu'on
saurait vérifier soi-même en remontant d'un cran. Et le plafond montre à quoi
elle sert : sur les trente et une années où les deux chemins existent — la
transcription et le *Journal officiel* —, ils donnent le même chiffre à l'euro
près, ce qui certifie ces trente et une-là et rend les autres un peu moins
incertaines sans les certifier.

## Ce que la certification garantit

**Ce que cela veut dire concrètement.** Les carrières entamées après 1950 —
c'est-à-dire les générations nées à partir de 1930 environ, soit la quasi-totalité
des cas simulés — reposent désormais sur des séries recontrôlées. Les **écarts
entre les trois scénarios** restent plus robustes encore que les niveaux : ils
sont calculés sur les mêmes carrières, avec les mêmes séries, et une erreur
résiduelle se propage dans le même sens aux trois scénarios.
