# Étape 0, l'inventaire : ce que chaque partie du jaune pensions 2027 apporte au dépôt

Le document : « Rapport sur les pensions de retraite de la fonction publique »,
annexe au projet de loi de finances pour 2027, 250 pages, créé le
12 octobre 2026 par la direction du budget, avec la DGAFP, le Service des
retraites de l'État et la Caisse des dépôts. budget.gouv.fr le sert depuis le
13 octobre, sous « PLF 2027 - Jaunes budgétaires », et refuse le cloud (403,
pare-feu Incapsula) ; à 15 h 21, le dossier du PLF 2027 de l'Assemblée ne le
porte toujours pas. Le propriétaire l'a téléchargé et déposé sur la branche
`jaune-2027` : `34465.pdf`, 11 964 640 octets, SHA-256
`73dd4a66051cd71bdf2c77eb5345a34f99f862330f0f20164c930492be2dbaf5`. Une
session le reprend par `git fetch origin jaune-2027` puis
`git show origin/jaune-2027:34465.pdf > data/brut/34465.pdf`, et en compare
l'empreinte ; `pdftotext -layout` le lit sans perte de chiffres.

Sa matière est le stock de pensionnés au 31 décembre 2025 et le flux des
pensions entrées en paiement en 2025 : la suite, plus récente, de ce que le
dépôt tire du jaune 2026 (`sre_jaune_pensions`). Les numéros de page sont ceux
du PDF.

## Pourquoi l'étape 1 ne pouvait pas se faire aujourd'hui

Le dépôt range un document que le cloud ne télécharge pas de deux façons
(`data/sources.yaml`, champs `blocage`, `miroir` et `rediffusion`) : par un
miroir public, l'Assemblée pour les annexes budgétaires, ou par la release
`documents-apportes` du dépôt, qui ne sert que les documents dont la licence
est lue et permet la rediffusion. Un test l'exige
(`test_tout_refus_visant_un_fichier_a_un_miroir_ou_un_document_publiable`), et
un autre refuse tout document versionné sous `data/brut/`. Le PDF n'entre donc
pas dans l'historique de git. Aujourd'hui, l'Assemblée ne le sert pas encore,
et la licence ne se lit pas depuis le cloud : les mentions légales de
budget.gouv.fr répondent 403, l'archive du web 429 puis un refus, et l'article
L. 322-1 du code des relations entre le public et l'administration
(LEGIARTI000032255220), qui fonde la réutilisation des informations publiques,
répond 403 sur Légifrance. Le jaune 2026 s'était rangé par le miroir de
l'Assemblée, sans release.

## L'éditorial (pages 7 à 15) : la transparence sur le poids des pensions

- Pour la première fois, la part des pensions dans les crédits de chaque
  ministère : figures B et B bis (Éducation nationale, Intérieur), et 3B, page
  24, pour tous. → **site**, étape 8.
- Figures A et A bis (pages 9 et 10) : la rémunération d'un cas type civil et
  d'un militaire, primes comprises, décomposée en cotisations et
  contributions ; pour le militaire, 3 274 € bruts mensuels et 24,60 % de
  primes (moyennes de 2023), 50 % de la rémunération totale en cotisations
  retraite. → la fiche de paie du **site**, étape 8.
- « Une lecture erronée à éviter » (page 13) : le régime des fonctionnaires
  ne serait pas plus avantageux, chiffres de la DREES à l'appui (génération
  1958 : les règles du régime général relèveraient leur pension moyenne de
  1,5 %, 62 % y gagneraient, 32 % y perdraient), un taux de remplacement de
  73,8 % contre 74,8 % au régime général, et 0,94 cotisant par pensionné de
  droit direct contre 1,5. → à mettre en regard de ce que le site montre,
  étape 8.
- Figures C et D : les dépenses publiques comparées à la zone euro. Rien à en
  tirer pour le modèle.

## Partie I (pages 16 à 37) : les finances

- Figures 1 et 2 : la branche vieillesse en 2025 et ses cotisants. →
  contrôle des agrégats de la page Coût, étape 6.
- Figure 3A (page 21) : les recettes du CAS Pensions sous le taux du régime
  général. → action 129 (note du 13 octobre). Son texte écrit 41,5 Md€ de
  subvention d'équilibre, sa figure 43,9.
- Tableaux 4 et 5 (pages 26 à 28) : onze régimes spéciaux, et ce que l'État
  verse à chacun. → `donnees/financement_regimes.py` et l'inventaire des
  régimes, étape 6.
- Figures 6 à 9 : dépenses et recettes des trois régimes depuis 1990, poids
  dans le budget général. → étape 6.
- Tableaux 10 et 11 : les engagements de retraite de l'État, 1 366 Md€ à fin
  2025, et leur sensibilité au taux d'actualisation. → étape 6, si le coût en
  fait un repère.

## Partie II (pages 38 à 86) : les régimes

- Tableau 12 (page 39) : le panorama des régimes des agents publics en 2025,
  les quarante-deux situations d'affiliation. → l'inventaire des régimes
  (`data/reference/regimes/`), étape 3.
- Tableaux 13 et 14 (pages 42 et 44) : taux salariaux et employeurs depuis
  2000 ; le 14 recoupe déjà les séries du modèle (action 129). → étape 3.
- Graphiques 15 et 16 : les polypensionnés, par sexe et par régime. →
  étape 7.
- Graphiques 17 et 18, tableau 19 : le CAS Pensions, ses programmes et son
  solde cumulé. → étape 6.
- Tableaux 20 et 21 (page 57) : démographie et finances de la CNRACL. →
  étape 6.
- Tableau 22B (page 66) : les paramètres du RAFP au 1er janvier, de 2005 à
  2026. → `regimes/rafp.yaml` et les fiches `rafp_*`, étape 3.
- Tableau 23 : le programme 742, les ouvriers d'État. → étape 6.
- Tableau 24 (page 79) : les taux de cotisation réels de l'Ircantec depuis
  1992 ; graphique 27, tableaux 28 à 30 : ses nouveaux retraités et son stock.
  → `regimes/ircantec.yaml`, étape 3 ; les pensions moyennes, étape 4.

## Partie III (pages 87 à 143) : les règles

Exemple officiel, que le texte tel que la caisse l'applique domine ; chaque
point se confronte aux fiches de la carte, à l'étape 9, ou aux séries, à
l'étape 3.

- Tableau 31 et figure 32 : les textes jusqu'en 1983, les réformes jusqu'en
  2023.
- Tableaux 33 et 34 : la durée requise par génération. →
  `duree_requise_fonction_publique.csv`.
- Tableaux 35 et 36 : le taux de la retenue de 2010 à 2020.
- Figure 37 : les départs des parents de trois enfants, de 2010 à 2025.
- Tableau 38 : la décote par régime et par génération. →
  `decote_fonction_publique.csv`.
- Tableaux 39A et 39B : les carrières longues ; figure 40 : les rachats
  d'années d'études.
- Tableau 41 et figure 42 : âge, durée et calcul de la pension d'un sédentaire.
- Tableaux 43 à 47, figure 44 : le minimum garanti, ses conditions, sa
  formule, ses montants, ses bénéficiaires. → `minimum_garanti.csv`,
  `minimum_garanti_montants.csv`.
- Tableaux 48 et 49 : la bonification de dépaysement et les bénéfices de
  campagne par territoire ; tableau 50 : bénéficiaires et gain moyen des
  bonifications. → `bonifications_jaune.csv`, étape 2.
- Tableaux 51 à 53 : la majoration pour trois enfants.
- Tableau 54 et figure 55 : l'indemnité temporaire de retraite et son plafond.
- Tableau 56 : le cumul emploi-retraite.
- Tableau 57 (page 138) : âges d'ouverture et limites d'âge des emplois de la
  catégorie active. → `categorie_active.csv`.
- Tableau 58, figure 59 : les départs anticipés (flux 2023) et l'invalidité.
- La réversion (pages 133 à 135).

## Partie IV (pages 144 à 166) : les pensions

Des référents du modèle, à l'étape 4 : effectifs de pensionnés depuis 1990
(tableau 60, figures 61 à 65), départs et âges de 2024 et 2025 (tableaux 66 à
69, dont la comparaison public-privé), motifs de départ (tableau 70,
graphiques 71 et 72), pension moyenne du stock et du flux depuis 2000
(graphique 74, tableaux 75 à 78), durée validée du flux 2025 (tableau 79), le
minimum garanti dans le flux 2025 (tableaux 80 à 85), la décristallisation
(tableau 86).

## Partie V (pages 167 à 196) : les perspectives

- Graphiques 87 à 91 : la pyramide des âges des agents fin 2024, la part des
  cinquante ans ou plus. → étape 7.
- Tableaux 94 à 97 : durée de référence, services et bonifications par sexe
  et par motif de départ, caractéristiques des nouvelles pensions militaires.
  → les cas types, étape 5.
- Graphique 98, tableaux 101 à 108 : durée d'assurance tous régimes, âges par
  motif, surcote et décote, taux de liquidation, pension à la liquidation. →
  étape 4.
- Tableau 109 : ce que les réformes ont rapporté aux régimes de l'État ;
  tableau 110 : la revalorisation des pensions. →
  `revalorisation_pensions_fonction_publique.csv`, étape 3.
- Tableaux 113 et 115, figure 114 : les ratios démographiques ; tableau 116 :
  le solde technique de la CNRACL ; le rapport du COR de juin 2026. →
  étape 6.

## Partie VI (pages 197 à 250) : l'annexe statistique

- **A-1 à A-8**, le stock au 31 décembre 2025 : effectifs, âges, pensions
  moyennes de 2011 à 2025, part portée au minimum garanti depuis 2005,
  bonifications (A-7), déciles de pension (A-8). → étapes 2 et 4.
- **B-1 à B-22**, le flux de 2025 : caractéristiques (B-1), par sexe, par
  motif, par âge (B-6 à B-9), par administration et catégorie (B-10), la
  réversion (B-11), les entrées de 2011 à 2025 (B-12), les décès de
  pensionnés (B-13), pension, indice et taux de liquidation de 2011 à 2025
  (B-14), pensions par catégorie et par grade (B-16 à B-19), déciles (B-20),
  minimum garanti (B-21), bonifications (B-22). → étapes 2, 4, 5 et 7.
- **C-1 à C-9**, les départs anticipés hors invalidité de 2015 à 2025, par
  motif, âge, catégorie et durée, pour chaque versant. → étape 7.
- **D-1 à D-5**, les finances et la démographie de 2025 : dépenses et
  recettes, taux, programme 741, compte de résultat de la CNRACL, effectifs de
  cotisants et de pensionnés. → étapes 3 et 6, et `donnees/cotisants.py`.
- **E**, le glossaire. → `data/reference/vocabulaire/`, s'il y manque un
  terme.
