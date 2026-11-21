# Action 194 : la durée des régimes spéciaux et des fonctionnaires, comptée au jour

*Le 21 novembre 2026, sept corrections écrites par une session, relues une à
une par une autre sous Opus (Fable indisponible ce soir-là ; le propriétaire
l'a voulu ainsi), publiées ensemble. Elles reprennent ce que laissait
`2026-11-21-surcote-des-regimes-speciaux-au-mois.md` : la décote et la durée
d'assurance de ces régimes comptées par trimestres civils.*

## Les sept corrections

| | Le texte | Le moteur faisait | Il fait |
|---|---|---|---|
| 1 | SNCF, décret n° 2008-639, article 12 : la fraction de 45 jours et plus du « décompte final des trimestres liquidables » compte pour un trimestre ; de même à la RATP (article 23), aux IEG (annexe 3, article 9), à la CRPCEN (article 85), à l'Opéra (article 14), à la Comédie-Française (article 12) et à la Banque de France (annexe, article 31, II) | arrondir chaque année civile | additionner les services, puis arrondir une fois ; fiche neuve `decompte_des_services_regimes_speciaux` |
| 2 | les décrets de juin 2008 valent pour les pensions qui prennent effet à compter du 1er juillet 2008 ; la surcote de 2008 arrondit « à l'entier supérieur » (SNCF, article 13, II) | la réforme au 1er janvier 2009 | une date d'effet coupe 2008 |
| 3 | SNCF, article 13, I, 2° (CRPCEN et Comédie-Française de même) : la borne de la décote retranche les trimestres d'après l'ouverture, « arrondi à l'entier supérieur » | les compter par années civiles | les compter au mois |
| 4 | SNCF, article 7, IV, 3° : le temps partiel compte pour sa quotité dans la pension ; article 13, III : à temps plein dans la durée d'assurance | le liquider à temps plein | sa quotité, sauf à la CRPCEN, dont le texte ne la réduit pas |
| 5 | L. 14, I : la durée d'assurance des fonctionnaires se compte au jour ; les régimes spéciaux « totalise[nt] la durée des services » (SNCF, article 13, III) | annoncer les trimestres civils | annoncer les trimestres entiers d'une durée au jour |
| 6 | L. 14, III : la surcote compte les trimestres « entiers » au-delà de la durée requise | compter l'excédent par années civiles | les trimestres entiers d'une durée au jour |
| 7 | L. 14, III : la surcote court de la date où la durée requise est atteinte | dater cette date à l'année civile | la dater au mois |

Exemples : un agent de la SNCF né le 1er février 1975, entré à 30 ans, parti
à 62 ans et 9 mois, a 394 mois de services : 131 trimestres au lieu de 130,
32 161,66 euros au lieu de 31 916,15 (patch 1). Une fonctionnaire née le
1er janvier 1964, entrée le 1er septembre 1984, atteint 510 mois le 1er mars
2027 ; partie le 1er juin, elle a un trimestre de surcote : 75,9375 % au lieu
de 75 % (patch 7 ; à la CNRACL, 35 781,52 à 36 228,79 euros).

Deux témoins de simulation sur 937 bougent, au patch 1 seulement :
`banque_de_france_emploi_classe` (+0,87 %) et
`crpcen_generation_1957_apres_soixante_ans` (+0,64 %). Trois exemples publiés
(Monsieur A de la CNIEG, Jean et Yves de la CRPCEN) reçoivent leur carrière
exacte dans `tests/temoins/exemples_officiels.yaml`, que le test des
trimestres publiés tient.

## Ce qui reste

- **Une présomption** (patch 4) : l'agent à temps partiel n'a pas payé la
  retenue qui le ferait compter à temps plein (RATP, article 18 ; IEG,
  annexe 3, article 11 ; Banque de France, annexe, article 11 ; Opéra,
  article 11 ; Comédie-Française, article 13 bis). La saisie ne le demande
  pas ; la fiche le dit, et vider `services_a_quotite` la renverse.
- **La version d'avant le 1er avril 2007** de la fiche neuve est supposée :
  rien n'y est lu.
- **Une limite vue à la relecture** (patch 7) : la date de la durée requise
  ne lit que l'activité principale de l'année, et prend toute année
  incomplète autre que celle du départ pour une année d'entrée qui finit en
  décembre. Une année coupée en son milieu où la durée est atteinte daterait
  la surcote un peu tard : moins que le droit, jamais plus. Non vérifié sur
  un cas, le relevé refusant deux lignes pour une même année.
