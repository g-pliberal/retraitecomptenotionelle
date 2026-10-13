# Étape 4, première partie : le stock et le flux de 2025 certifiés, les trois cas types statutaires confrontés aux départs de leur groupe

**Reprise, au 13 octobre 2026.** Fait : le stock de pensions au 31 décembre
2025 (A-1) et le flux de 2025 (B-1 en entier, B-3, B-3 bis, B-4, B-5), lus case
par case et certifiés (`caracteristiques_fonction_publique.csv`) ; les trois
cas types statutaires, partis en 2025, face aux départs de leur groupe, leurs
écarts déclarés (`tests/test_flux_fonction_publique.py`) ; le registre des
modèles à jour. Reste, dans cet ordre : le tableau B-22, les bonifications du
flux, qui corrige la case fausse du tableau 50 ; les séries du flux (B-14) et
les tableaux 60 à 108, pour confronter les cas types année par année ; le stock
face à la page Coût, pesé comme elle ; les limites. Commencer par B-22, avec un
gabarit du lecteur. Détail : cette note.

Le document est celui de l'étape 1 (`sre_jaune_pensions_2027`), tiré de la
branche `jaune-2027` dans `data/brut/`, son empreinte vérifiée. Les pages
citées sont celles qu'il imprime.

## Où les référents vont

Le plan de l'étape les rangeait dans `referents.yaml`. Ce registre est celui des
autres modèles, et le jaune n'en est pas un : ses chiffres sont l'observé, les
pensions que le Service des retraites de l'État, la CNRACL et le FSPOEIE ont
effectivement servies. Ils sont donc une série certifiée de
`data/reference/macro/`, comme les caractéristiques des retraités que l'EIR de
la DREES publie (`caracteristiques_retraites.csv`), hors de l'empreinte du
modèle, qu'ils jugent sans le régler (`memoire.HORS_DU_MODELE`). Le registre
dit, aux modèles qui les attendaient, qu'ils sont là (plus bas).

## La lecture, case par case

Les tableaux du flux ont des cases vides : pas de total de l'État sur la
plupart des lignes du B-1, pas de militaires sur celles de la surcote ni des
carrières longues, pas de décote pour les départs pour invalidité. Une case vide
ne laisse rien dans le texte d'une ligne : « Part des pensions avec surcote » a
six nombres pour huit colonnes, et rien ne dit lesquels manquent. Le lecteur PDF
du dépôt rend désormais chaque ligne en fragments, chacun à son abscisse
(`lecture_pdf.fragments_par_page`) ; `sre_jaune_pensions.py` place les colonnes
sur la première ligne du tableau (« Ensemble des départs », « Effectif »), range
chaque case à la colonne la plus proche, et reconnaît chaque ligne à son
intitulé, dans l'ordre que dit le gabarit du tableau — le jaune pose certains
intitulés au-dessus de leurs cases, d'autres en dessous, d'autres de part et
d'autre. Trois pièges du document : l'insécable des milliers posée à quatorze
points et demi de ses chiffres au tableau A-1 ; le tiret qui est tantôt un
signe moins, collé à ses chiffres, tantôt une case sans objet, seul dans sa
case, au B-3 bis ; les montants sans séparateur des milliers au B-5.

Les tableaux se recoupent, et la lecture le vérifie : les sexes font l'effectif
au A-1, cent pour cent au flux ; le total de l'État fait ses civils et ses
militaires, celui de la CNRACL la territoriale et l'hospitalière ; les motifs de
départ du B-3 et du B-3 bis font l'ensemble du B-1 ; les catégories des civils
partis pour ancienneté au B-4, leur colonne du B-3. Tout recoupe, et les départs
du B-1 sont ceux que `bonifications_jaune.csv` tenait déjà.

## Ce qui est certifié

`caracteristiques_fonction_publique.csv`, clé (tableau, population, champ,
indicateur) : le stock au 31 décembre 2025, droit direct et droit dérivé (A-1) ;
le flux de 2025, par régime (B-1), par motif de départ (B-3 pour l'État, B-3 bis
pour la CNRACL), par catégorie pour les départs pour ancienneté et, pour les
militaires, par armée et par grade (B-4, B-5). Vingt-quatre caractéristiques
par colonne du flux : âges de radiation et de première mise en paiement,
services, bonifications, durée tous régimes, décote et surcote (part, perte ou
gain, taux, coût), taux de liquidation avec et sans elles, part au taux plein et
au taux de 80 %, indice, part au minimum garanti, majoration pour enfants,
pension avec et sans accessoires. `verifier_donnees.py` les certifie ; le
manifeste les range sous `sre_jaune_pensions_2027`.

Quelques repères. Le stock de droit direct : 1 656 399 pensions civiles de
l'État, mises en paiement à 59,3 ans, 2 386 € par mois ; 408 750 militaires, à
44,1 ans, 1 832 € ; 1 470 309 à la CNRACL, à 58,9 ans, 1 481 €. Le flux :
47 104 civils, 10 691 militaires, 69 650 agents de la CNRACL.

## Les trois cas types face au flux de 2025

`scripts/flux_fonction_publique.py` fait partir chaque cas type statutaire en
2025 — la génération que le droit, appliqué à sa carrière, fait partir cette
année-là — et met en regard ce que le modèle lui sert et ce que le jaune publie
des départs de son groupe : les civils de l'État partis pour ancienneté en
catégorie sédentaire (B-4), les agents de la CNRACL partis pour ancienneté en
catégorie active (B-5), les militaires partis pour ancienneté (B-3). Le taux est
la pension rapportée au traitement qui la liquide ; l'indice, ce traitement
ramené par la valeur du point de 2025. L'écart du modèle au jaune :

| cas type | âge | durée tous régimes | taux | indice | pension |
|---|---|---|---|---|---|
| sédentaire de l'État, 1961 | 64,0 pour 64,4 | 168 pour 174,5 | 75,0 % pour 66,8 % | 749 pour 735 | 2 766 € pour 2 399 € |
| actif de la CNRACL, 1968 | 57,75 pour 61,0 | 143 pour 180,7 | 49,7 % pour 60,5 % | 616 pour 508 | 1 506 € pour 1 578 € |
| militaire, 1977 | 48,5 pour 49,2 | 130 pour 154,5 | 59,1 % pour 66,3 % | 635 pour 605 | 1 846 € pour 1 943 € |

- *Le sédentaire* part à l'âge du flux et à son indice, mais au taux plein, sur
  une carrière entière dans le seul régime de l'État : le civil réel n'y a que
  138,1 trimestres de services sur 174,5 tous régimes. Sa pension est 15 % trop
  haute, et c'est lui qui porte toute la fonction publique d'État de la page.
- *L'actif de la CNRACL* part trois ans et quart trop tôt, à l'âge
  d'ouverture, avec une décote que 7,8 % seulement des actifs prennent, sur un
  traitement un cinquième trop haut : deux erreurs qui se compensent, à 4,6 %
  près sur la pension. L'action 152 l'avait lu sur le jaune 2026 et gardé le cas
  type (sa note de l'étape 2) ; le flux de 2025 le confirme.
- *Le militaire* part à l'âge du flux, à un indice 5 % trop haut, mais sans les
  bénéfices de campagne ni les bonifications du service aérien : 130 trimestres
  liquidables pour 149,5 (110,9 de services et 38,6 de bonifications). Sa
  pension est 5 % trop basse.

Les quinze écarts sont déclarés, chacun dans sa fourchette : une mesure qui en
sort fait échouer la suite, qu'elle s'améliore ou se dégrade, et qui la déplace
dit pourquoi. Le recalage des cas types est l'étape 5, qui part de ce tableau ;
aucune ligne du modèle ne change ici.

## Le registre des modèles

- *Oscar* (SRE) : son moteur a été « testé avec succès sur le flux de
  liquidation réel 2018 », et le dépôt ne l'était sur aucun flux. Il l'est
  désormais sur les agrégats publiés du flux de 2025, pour ses trois cas types
  statutaires ; la validation pension par pension reste au chantier 138.14.
- *Canopée* (CNRACL) : le flux de 2025 confirme son point — 36,8 % des départs
  de l'hospitalière en catégorie active, 4,7 % de la territoriale ; les actifs
  mis en paiement à 61,0 ans, les sédentaires à 64,0 —, contre un cas type
  parti à cinquante-sept ans et neuf mois (chantier 138.3).
- *Pablo* (SRE) : l'effet de la réforme de 2023 sur le régime de l'État se lit
  désormais dans l'édition 2027 (p. 186), qui reprend les chiffres de 2026 puis
  décrit, sans la chiffrer, la suspension de la réforme que décide la loi de
  financement de la sécurité sociale pour 2026.

## Ce qui reste, pour la seconde partie

- **Le tableau B-22**, les bonifications du flux de 2025 par population : il
  établit l'année du tableau 50 et corrige sa case fausse (la bonification pour
  enfant des civils, 44,0 % et non 4,0 %). Il va à `bonifications_jaune.csv`,
  par un gabarit du lecteur.
- **Les séries du flux** : pension, indice et taux de liquidation de 2016 à 2025
  (B-14), âges par motif depuis 2004 (tableaux 101 et 102), taux et pension à la
  liquidation (107 et 108), pension moyenne du stock et du flux depuis 2000 (75
  à 78) : de quoi mesurer les cas types année par année, et non en 2025 seul.
- **Le stock** (A-1 à A-6, A-8, B-20, B-21) face à la page Coût : la pension
  moyenne de chaque caisse, ses retraités pesés comme la page les pèse, ce que
  l'action 152 mesurait à la main sur 2020.
- **Les limites** (`docs/limites/5-bis-cout-agrege.md`), une fois l'étape close.
