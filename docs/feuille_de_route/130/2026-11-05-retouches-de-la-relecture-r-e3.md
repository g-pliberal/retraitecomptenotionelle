# Retouches de la relecture R-E3 : la CAVOM, deux non-tranchés déclarés et huit écarts faibles (file E2)

Le 5 novembre 2026, action 130. La relecture R-E3 (ace82ea,
`2026-11-05-relecture-de-e-cavom.md`) du travail de la file E (ee71f57,
`2026-11-05-carte-des-fiches-cavom-lue-au-droit.md`) juge la CAVOM lue au droit conforme
pour l'essentiel et relève dix écarts faibles, (a) à (i) et le bloc « Reprise ». Cette note
les reprend un à un. Ni règle, ni donnée, ni valeur servie ne change : les fiches
`cavom_ages_minoration` et `cavom_assiette_2016`, les notes du fichier
`regimes/cavom_complementaire.yaml` et une docstring de `tests/test_sections_liberales.py`.
Textes rouverts dans les index du dépôt (`dila_index.py --recuperer` : JORF à jour du
3 novembre 2026, LEGI du 2 novembre), par `dila_cherche.py --texte`. Cas rejoués par
`servi_et_refait` (`tests/outils_pont.py`), dans les deux moteurs, aucun écart entre eux :
la requête de E, `officier_ministeriel`, entrée à 25 ans, deux salaires moyens.

## Les deux non-tranchés, déclarés dans la fiche

- **(a) L'âge de l'inapte né avant 1959, de 2016 à 2024.** L'article 14, I, 1°, des statuts
  de 2016 sert l'inapte sans coefficient « À partir de 62 ans » ; l'article 23 dit que,
  « Pour les générations antérieures, les âges d'ouverture des droits à retraite et de
  bénéfice du taux plein évoluent selon le tableau », 60 ans jusqu'à la génération 1955. Le
  texte ne dit pas si l'inapte est servi sans coefficient dès cet âge. Essai : né le 10 mars
  1955, inapte, liquidé le 1er avril 2016 à 61 ans ; 65 − 61 = 4 années, 1 − 4 × 0,05 =
  0,80 ; le modèle sert 0,80, 12 830,11 € par an. Si l'âge suit la table, le texte sert 1 :
  12 830,11 / 0,80 = 16 037,64 €, soit 3 207,53 € de plus par an ; s'il reste 62 ans, 0,80.
  Déclaré dans une approximation neuve, et dans les `conditions` de `statuts_de_2016`, qui
  disaient « dès 62 ans » pour tous.
- **(b) L'âge qui compte pour le coefficient.** Depuis 2025, « 5 % par année manquante entre
  l'âge auquel est demandée la liquidation de la retraite, qui ne peut être inférieur à l'âge
  fixé au 1°, et l'âge prévu au 2° » : l'âge de la demande, ou l'âge auquel l'affilié demande
  que sa retraite soit liquidée, celui de l'effet ; en 2016, « si la retraite est attribuée
  lorsque l'affilié est âgé de », la décision ou l'effet. Le modèle compte l'âge à la date
  d'effet. Essai : né le 10 février 1960, parti à 65 ans ; le modèle sert la CAVOM dès le
  1er mars 2025, 67 − 65 = 2 années, 0,90, 20 317,08 € par an. Au texte, une demande du
  15 janvier 2025, à 64 ans, 11 mois et 5 jours, prend effet au plus tôt le 1er avril 2025,
  premier jour du trimestre civil qui suit, à 65 ans, 1 mois et 22 jours. À l'âge de l'effet,
  1 an, 10 mois et 9 jours manquent : deux années, 0,90. À l'âge de la demande, 2 ans et
  26 jours : trois années si l'année entamée compte entière, comme le modèle la compte,
  0,85 ; deux sinon, 0,90. L'écart possible : 20 317,08 / 0,90 × 0,05 = 1 128,73 € par an.

## La condition de l'erreur (3), complétée

- **(c)** La fiche disait la pension servie un ou deux mois trop tôt « quand l'âge tombe au
  premier ou au deuxième mois d'un trimestre civil ». Elle oubliait l'assuré né le 1er d'un
  mois, que le modèle sert dès le jour de son anniversaire (`date_effet_mois_suivant`). La
  condition générale : deux mois de trop quand le modèle fait prendre effet la pension au
  deuxième mois d'un trimestre civil, un mois au troisième, aucun au premier. Essais, nés en
  1959, à 62 ans : le 1er mai, servi dès mai 2021, 13 546,16 € par an, le texte au
  1er juillet : 13 546,16 × 2 / 12 = 2 257,69 € ; le 1er mars, dès mars, 13 529,99 € par an,
  le texte au 1er avril : 13 529,99 / 12 = 1 127,50 € ; le 1er avril, dès avril, comme le
  texte. Le mois de l'effet se lit à `mois_liquidation` du résultat.

## Les cinq imprécisions de lecture

- **(d) L'arrêté du 28 août 2020.** Le G a deux points. Le 2° change les mots du renvoi de
  l'inaptitude. Le 1° insère, à la condition de cessation, « , sous réserve des dérogations
  prévues à l'article 15, », et le H récrit l'article 15, « Cumul activité-retraite ». La
  fiche le dit, sous la citation et dans l'approximation de la cessation, que le modèle ne
  porte pas, pas plus que le cumul.
- **(e) L'arrêté du 21 décembre 2016.** Le motif omettait son 18°, « Les articles 18, 20, 21
  et 22 sont abrogés », qui n'en donne pas la rédaction, et son 19°, qui fait de l'âge de la
  réversion (article 24, « Réversibilité » depuis le 9° de 2015) celui « prévu à l'article 14
  des présents statuts ». Ni l'un ni l'autre ne touche l'article 14 ou l'article 23.
- **(f) La référence « article 1er, II ».** La dérogation des quatre à sept plafonds est au
  II de l'article 3 du décret n° 2015-1875 (JORFARTI000031740735) ; la note de LEGI à
  l'article 2 du décret n° 79-265 (LEGIARTI000038427708) écrit « Conformément à l'article 1
  II ». Corrigée aux lignes 110, 172, 195 et 218 de `regimes/cavom_complementaire.yaml`, en
  « article 3, II ». `moteur/donnees.json`, qui en porte les notes, se refait à GitHub.
- **(g) Le décret n° 2026-418.** Son article 22 (JORFARTI000054153714) insère trois alinéas
  à l'article 2, I, et « b) Le III est abrogé ». La fiche cite désormais l'article 2 en
  entier (LEGIARTI000054168585), avec la note de LEGI sur l'article 30, l'article 22, et
  L. 131-6-2 (LEGIARTI000048683699), dont le deuxième alinéa fait calculer la cotisation à
  titre provisionnel sur l'avant-dernière année et le troisième la régularise sur l'année.
  L'index aplatit les alinéas : le quatrième, « Par dérogation au deuxième alinéa », celui du
  revenu estimé que l'article 2 nomme, situe les autres. Le III, « un nombre de point égal à
  son montant divisé par le prix d'achat du point », passe à l'article 4-2, « arrêté à la
  deuxième décimale par excès ». Trois approximations neuves : les deux lectures du minimum
  des « deux premières années d'activité » (aussi ces années, ou l'assiette forfaitaire des
  cotisations provisionnelles), sans effet sur la cotisation définitive, que le premier
  alinéa borne à 19 % du plafond dans l'une et l'autre ; la cotisation provisionnelle et sa
  régularisation, non modélisées, sans effet sur la cotisation définitive ; l'arrondi des
  points, que le modèle, qui sert cotisations × rendement, ne fait pas : moins d'un centième
  de point par cotisation, 0,01 × 3,3745 = 0,03 € de pension par an au plus, à la valeur de
  service de 2026 que porte le fichier du régime.
- **(h) Le taux de 2019.** L'article 2 du décret n° 2018-1033 est remplacé par l'article 1er
  du décret n° 2019-1484 (JORFARTI000039684598, publié le 29 décembre 2019), au même taux,
  « «-taux de cotisation : 12,50 % ; » ; la fiche cite les deux rédactions.

## La docstring et le bloc

- **(i)** La docstring de `test_chaque_pension_minoree_porte_les_ages_et_le_taux_de_sa_version`
  cite désormais les textes de la CAVOM : articles 14 et 23 en 2016, l'article 14 récrit en
  2025, l'article 1er, I, du règlement de 2026.
- **Le bloc « Reprise »**, récrit au commit de cette note : R-N2 y est dit conforme pour la
  règle, avec l'écart grave du test du site, rouge depuis ddc92fc et réparé par N-bis
  (0ba2aea) ; de la CRPNPAC, le refus avant cinquante ans et l'anticipation d'avant 2012
  reviennent, avec les vingt annuités ; la ligne des retouches de R-E, R-M3-ter, R-L-ter et
  R-D-bis (7e44534) aussi.

## Ce que l'étape laisse

- **Au propriétaire, inchangé** : les trois erreurs de la CAVOM que la note de E déclare (de
  2016 à 2024, l'inapte minoré, jusqu'à 25 points ; depuis 2025, l'inapte non ouvert à
  62 ans ; la pension au mois et non au trimestre civil, un ou deux mois de trop, ce que (c)
  précise). S'y ajoutent deux non-tranchés, (a) et (b), qu'un exemple de la caisse
  trancherait, et l'arrondi des points de 2026, d'un centime au plus.
- **La caisse suivante n'est pas lue** : cette session s'arrête après les retouches, la
  règle « une session, une étape » et le contexte déjà long le demandant. La suivante,
  dans l'ordre du bloc, est la CARPIMKO : `carpimko_ages_2015` et `carpimko_assiette_2026`,
  sept manques chacune.
- Le contenu des articles 18, 20, 21 et 22 des statuts, abrogés en 2016, est au seul
  Bulletin officiel.
