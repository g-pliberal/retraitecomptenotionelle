# Le diaporama des adhérents passe à trente diapositives : sommaire, indexation, chiffres macro, calendrier

*Le 10 novembre 2026, action 186, chantier 8. Le propriétaire, en relisant le
diaporama du 9 novembre : « J'aime beaucoup la présentation PowerPoint mais
j'ai l'impression qu'il manque des détails. […] Je ne crois pas avoir vu la
méthode d'indexation. » Puis, au fil de l'échange : un sommaire, un
calendrier, les schémas de flux et les parts de PIB avant et après, des
comparaisons internationales, les tables de mortalité, « compte notionnel à
valeur actuarielle au moins une fois », et, pour les impôts, « Presque tout
baisse, une taxe monte » avec la liste.*

## Ce qui est fait

`docs/presentation_adherents_novembre_2026.pptx` garde son nom et passe de
vingt à trente diapositives, en six chapitres dont le numéro est rappelé en
haut de chacune. Dix sont nouvelles :

- **le sommaire** ;
- **où va l'argent aujourd'hui** : le schéma des flux du système actuel en
  2026, repris de la page Coût ;
- **la France et ses voisins** : la dépense de pensions de onze pays en part
  du PIB, en 2024 ;
- **un exemple, du compte à la pension** : la revalorisation avant le départ,
  la division par les années que donnent les tables de mortalité, la
  revalorisation après ;
- **la revalorisation** : le compte sur la masse des salaires, la pension
  nouvelle sur la masse des salaires moins la hausse du nombre de retraités
  par cotisant, la pension d'aujourd'hui sur les prix moins cette hausse
  (décisions 10 et 41), le plancher en euros et son rattrapage (44, 46, 49),
  la réserve de 1 % (73, 107) ;
- **cinq pays ont déjà des comptes notionnels** ;
- **où irait l'argent avec la réforme** : le schéma de la proposition en 2026 ;
- **la part des retraites dans le PIB, avant et après**, de 2026 à 2070 ;
- **presque tout baisse, une taxe monte** : sept prélèvements baissés ou
  supprimés (décisions 36, 48, 88, 103, 104), la taxe sur les terrains qui
  monte (80), les cotisations chômage et maladie avec elle (99) ;
- **le calendrier** : le jour de la réforme, les cinq premières années, vers
  2032, vers 2053, au-delà.

Six anciennes sont retouchées. Le principe dit la masse des salaires, les
tables de mortalité et le nom savant ; son exemple, qui ne faisait que
diviser, a sa diapositive. « Un réglage publié chaque année » devient « une
règle de revalorisation, connue d'avance », dans le tableau et dans les
notes. Les pensions actuelles portent la réserve de 1 %. Le financement et
« ce qui reste à préciser » ne disent plus qu'aucun chiffre n'existe : la
page Coût compte la TVA et la taxe sur les terrains depuis le 9 novembre au
soir. La date du titre passe au 10 novembre.

`docs/parcours_presentation.md` décrit le fichier tel qu'il est. La décision
107 (la prime à 1 %) est au registre du programme depuis le commit `086653b`.

## D'où viennent les chiffres

- **Les flux et les parts de PIB** : la page Coût du site, servie en local et
  lue dans un navigateur le 10 novembre 2026. 423 Md € versés en 2026, 14,1 %
  du PIB, 15,3 % en 2070 ; la proposition, 308 Md € et 10,3 % en 2026, 8,1 %
  en 2070, des recettes à 9,8 %, l'équilibre en 2053 ; la garantie, 36 Md € en
  2026 et 29 en 2070.
- **L'Europe** : Eurostat, table `tps00103`, mise à jour le 26 octobre 2026,
  année 2024, plusieurs valeurs provisoires. Italie 15,85, Autriche 15,38,
  France 14,98, Espagne 13,19, Union 12,57, Allemagne 11,67, Pologne 11,61,
  Pays-Bas 11,25, Suède 10,72, Norvège 9,85, Lettonie 8,93. Son périmètre,
  invalidité comprise, est plus large que celui du COR : les notes le disent.
  La phrase de la page Risque, « le deuxième montant de l'OCDE, derrière
  l'Italie », n'a pas de source au dépôt, et l'Autriche passe devant la
  France dans cette table en 2024 : elle est à revoir.
- **Les tables de mortalité** : le modèle, à ses réglages par défaut. 22,72
  années à 65 ans pour un départ en 2026, 21,13 à 67 ans en 2028
  (`esperance_residuelle`), table de génération, unisexe.
- **Les cinq pays** : l'OCDE (*Panorama des pensions*) pour la liste et les
  dates ; l'étude du 7 novembre pour la règle de chacun. Les 2,5 points
  d'épargne obligatoire de la Suède, dits dans une note du présentateur, ne
  sont pas au dépôt.
- **Les impôts** : les décisions, et la note
  `2026-11-09-petites-baisses-retraites.md` pour les 600 € et 385 € par
  100 000 € de logement.

L'exemple chiffré est en chiffres ronds : 2,5 % de hausse de la masse des
salaires et 0,5 % de hausse du nombre de retraités par cotisant sont des
hypothèses, dites comme telles.

## Ce qu'il ne dit pas, à dessein

- **« Tout le monde paiera moins »** : le propriétaire l'avait demandé, puis
  a choisi « Presque tout baisse, une taxe monte ». Les notes disent pourquoi
  la première phrase est fausse pour un propriétaire et pour un retraité.
- **Aucun chiffre de perte de pouvoir d'achat** : les 96 % et les 17 % de
  l'étude du 7 novembre sont posés à côté du modèle, qui en a corrigé une
  hypothèse depuis.
- **Aucun chiffre de dette**, ni de gain de salaire net en euros.

## Ce qui n'a pas été vérifié, et ce qui reste

- Aucun calcul du modèle n'a été relancé, hors les deux espérances de vie.
- La page Coût applique la baisse des pensions en une fois dès 2026, quand
  les décisions l'étalent sur cinq ans et laissent ses pensions à
  l'Agirc-Arrco jusqu'à son intégration : les 16 Md € qui manquent en 2026
  sont donc un minimum. La diapositive et sa note le disent.
- Le fichier est binaire, aucun test ne le relit. Il a été monté à partir du
  fichier du 9 novembre par un script (python-pptx) resté dans le brouillon
  de la session, que le dépôt n'a pas en dépendance ; il se retouche dans
  PowerPoint.
- Le rendu a été relu dans LibreOffice, non dans PowerPoint.

## Au propriétaire

1. Relire les notes des diapositives 6 (l'Italie, qui a des comptes
   notionnels et dépense le plus), 9 (la revalorisation) et 24 (les impôts).
2. La réserve de 1 % : ce qu'elle devient si elle ne sert pas reste ouvert
   (note `2026-11-08-reserve-personnelle.md`) ; le diaporama le dit.
3. Le pouvoir d'achat des pensions sous la règle de revalorisation : le
   chiffrer au modèle, ou continuer de le dire sans chiffre.
