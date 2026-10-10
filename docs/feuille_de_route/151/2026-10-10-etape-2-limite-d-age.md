# Étape 2 : la limite d'âge des fonctionnaires et ses exceptions, texte en main

**Le 10 octobre 2026 : la veille a lu la limite d'âge des fonctionnaires civils et
des militaires, de 1936 à 2026, et chacune des exceptions qui la reculent ou la
lèvent. Huit fiches les portent ; le modèle n'en applique aucune. Ce que le simulateur
fait au-delà de la limite est au propriétaire (étape 3).**

La session a d'abord réparé la suite rouge que l'étape 1 avait laissée : le test de la
confrontation aux estimations officielles attendait le refus d'un départ à 82 ans, que
la saisie accepte désormais ; il le demande à 120 ans (308eafc).

## Ce que dit le droit

- *La limite du sédentaire.* « Le fonctionnaire ne peut être maintenu en fonctions
  au-delà de l'âge limite de l'activité dans l'emploi qu'il occupe, sous réserve des
  exceptions prévues par les dispositions en vigueur » (L. 556-1 du code général de la
  fonction publique, depuis 2022). Les valeurs, par période :
  - de 1936 à 1975, des limites par corps (« échelons ») de 65 à 70 ans pour la
    catégorie A, la sédentaire, et de 55 à 67 ans pour la B, l'active (loi du 18 août
    1936, article 1er), abaissées en 1946 et 1947 et relevées de deux ans en 1953, sans
    passer 70 ans (décret n° 53-711) ;
  - la loi n° 75-1280 ramène 70 ans à 68 et 67 ans à 65, de 1977 à 1980 ;
  - la loi n° 84-834 ramène tout ce qui dépasse 65 ans à 65, en 1985, sauf 68 ans pour
    le vice-président du Conseil d'État et les deux chefs de la Cour des comptes ; les
    territoriaux et les hospitaliers suivent l'État quand leur statut ne fixe rien
    (décret n° 65-773, article 2) ;
  - la loi n° 2010-1330 porte 65 ans à 67 : 65 ans et 4 mois pour les nés au second
    semestre 1951, 65 ans et 9 mois en 1952, 66 ans et 2 mois en 1953, 66 ans et 7 mois
    en 1954, 67 ans à compter de 1955 (article 28 et décret n° 2011-2103) ;
  - le code de 2022 garde 67 ans ; la loi n° 2023-270 y ajoute le maintien jusqu'à
    70 ans.
- *La limite de l'actif.* « Un âge au plus égal » (L. 556-1, 2°), que le statut fixe :
  57 ans pour les surveillants pénitentiaires et les corps d'encadrement et de
  commandement de la police, 60, 61 et 62 ans pour les commissaires et les grades au-dessus,
  59 ans sans report pour les contrôleurs aériens, 62 ans pour les sapeurs-pompiers
  professionnels et les autres emplois actifs (L. 556-8 à L. 556-10, fiche F12395 de
  service-public). La loi de 2010 a relevé chacune de deux ans (article 31).
- *Ce qui se passe à la limite.* La radiation des cadres d'office, le lendemain de
  l'anniversaire ; la pension est due « du jour de la cessation de l'activité » (L. 90
  CPCMR). Les services accomplis au-delà ne comptent que dans les cas prévus par la loi
  (L. 10).
- *Les militaires.* Une limite par grade et par corps, de 47 ans pour un sergent à
  66 ans pour un ingénieur de l'armement (L. 4139-16 du code de la défense), relevée de
  deux ans par la loi de 2010 ; une limite de durée de services pour le militaire sous
  contrat.

## Les exceptions, chacune dans sa fiche

| Exception | Depuis | Ce qu'elle donne | Fiche |
|---|---|---|---|
| Enfant à charge à la limite | 1936 | un an par enfant, trois au plus, de droit | `recul_limite_age_enfants` |
| Parent de trois enfants vivants à 50 ans | 1936 | un an, cumulable avec le précédent pour un enfant invalide | `recul_limite_age_enfants` |
| Enfant mort pour la France | avant 2022 | un an par enfant | `recul_limite_age_enfants` |
| Carrière incomplète | 2004 | jusqu'à la durée du taux maximum, dix trimestres au plus, sous réserve de l'intérêt du service | `prolongation_activite_carriere_incomplete` |
| Fonctionnaire actif | 2010 | jusqu'à la limite des sédentaires, sur sa demande | `prolongation_activite_categorie_active` |
| Sédentaire, sur autorisation | 14 juin 2023 | jusqu'à 70 ans, refus motivé | `maintien_en_fonctions_jusqu_a_70_ans` |
| Le cumul de tout cela | 14 juin 2023 | pas au-delà de 70 ans ; avant, des plafonds par recul jusqu'en 2022 | `plafond_limite_age_fonction_publique` (relation) |
| Corps particuliers | divers | hauts magistrats 68 ans, Conseil d'État, Cour des comptes et magistrats judiciaires maintenus jusqu'à 68 puis 70 ans, professeurs en surnombre, Collège de France à 73 ans, enseignants jusqu'à la fin de l'année scolaire, emplois supérieurs et fonctionnels | `maintiens_en_fonctions_de_certains_corps` |
| Militaires | 2023 | trois ans pour les besoins des forces ; l'officier général sans limite s'il a commandé en chef en temps de guerre ; la Garde républicaine par périodes de deux ans renouvelables | `limite_age_militaires` |

Le militaire n'a pas le recul pour enfants, que la loi de 1936 réserve aux
« fonctionnaires et employés civils ». Le plafond de 70 ans vaut-il pour un cumul de
reculs et de prolongations sans le maintien ? L. 556-1 parle du « bénéfice cumulé de ce
maintien » ; service-public l'écrit de tout cumul. La fiche de la relation laisse la
question ouverte.

## Ce que le modèle fait, mesuré

Il n'applique aucune limite d'âge : un fonctionnaire se simule en activité, traitement,
services et surcote compris, jusqu'au départ saisi. Au scénario 1, brut par mois en
euros constants, pour une carrière entière commencée à 22 ans :

| Statut, génération | 67 ans | 70 ans | 90 ans | 119 ans |
|---|---|---|---|---|
| Sédentaire de l'État, 1960 | 3 871 € | 4 461 € | 9 015 € | 17 895 € |
| Sédentaire de l'État, 1990 | 4 499 € | 5 219 € | 10 775 € | 18 987 € |
| Policier, 1990 | 4 499 € | 5 219 € | 10 775 € | 19 279 € |

Le droit ne garde le sédentaire né en 1990 que jusqu'à 70 ans, le policier que jusqu'à
57 ans, 67 avec la prolongation de L. 556-7.

## La proposition au propriétaire

Ce que le simulateur fait d'un départ saisi au-delà de ce que le droit permet :

1. **Refuser la saisie** au-delà de l'âge le plus tardif que le statut permet (70 ans
   pour un sédentaire depuis 2023). Simple, mais il interdit de simuler celui qui
   continue de travailler après sa radiation, ce que le propriétaire veut pouvoir faire.
2. **Radier des cadres à la limite**, et c'est la proposition : la carrière de
   fonctionnaire s'arrête à la limite reculée et prolongée par les exceptions qui
   s'appliquent ; la pension de fonctionnaire part de ce jour-là ; ce qui suit, jusqu'au
   départ saisi, n'est plus du service, mais peut être un métier de plus, que le
   simulateur sait déjà décrire (salarié, contractuel, indépendant), et dont les pensions
   partent au départ saisi. La page le dit : « la loi vous radie des cadres à 70 ans ».
3. **Pour les exceptions**, la proposition est de les appliquer autant que le départ
   saisi le demande et que le droit le permet : de droit, les reculs pour enfants, que la
   saisie connaît par les naissances ; présumées demandées et accordées, la prolongation
   pour carrière incomplète, celle de l'actif et le maintien jusqu'à 70 ans, puisque
   celui qui saisit un départ à 70 ans dit les avoir obtenues ; la page nomme
   l'exception qu'elle présume. Les corps particuliers restent hors du modèle tant que la
   saisie ne porte pas le corps.

Deux questions accessoires, au même moment : quelle limite opposer au militaire, dont le
simulateur ne connaît ni le grade ni le corps (la plus haute de sa catégorie, présumée
favorable ?) ; et les agents contractuels, les ouvriers de l'État et les régimes spéciaux
(IEG, SNCF, RATP, Banque de France), qui ont leur propre limite, à 67 ans le plus
souvent, et que le modèle n'applique pas davantage : à la même étape, ou à une suivante ?

## Ce qui reste

- L'étape 3 : la décision du propriétaire, puis la limite et chaque exception
  modélisées, en Python puis en JavaScript, avec leurs témoins.
- À lire encore : les lois du 15 février 1946 et du 8 août 1947, le décret n° 48-1907,
  la rédaction de 1936 de l'article 1er de la loi du 18 août 1936 et celle d'avant 1986
  de son article 4 ; la limite des territoriaux avant 1985 ; les limites des corps actifs
  avant 2010 ; les tableaux de L. 4139-16 de 2007 à 2023, que l'index ne reproduit pas.
- Les deux règles que l'étape 1 signalait, laissées à une étape à elles parce qu'elles
  touchent d'autres régimes : la majoration de différé de la CARMF complémentaire avant
  2017 (le différé suppose-t-il la cessation d'activité, que l'article 15 des statuts
  exigeait en 2011 ?) ; et le régime général d'une carrière née en 1900, dont la pension
  au taux acquis au 31 mars 1983 tombe de 2003 à 2004 (le maximum des pensions perd-il
  en 2004 le coefficient de ce taux, que la Cnav lui applique ?).
