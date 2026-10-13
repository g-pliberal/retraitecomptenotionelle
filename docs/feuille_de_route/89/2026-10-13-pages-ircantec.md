# Les pages de l'Ircantec : quatre exemples, la table de la durée confirmée, et les droits que le modèle ne sert pas

**Le 13 octobre 2026 : les vingt lignes de l'Ircantec, réservées puis
dépouillées.** Le lot `a_explorer` suivant dans l'ordre du bloc « Reprise » :
les pages du site de la caisse et de sa base documentaire, réservées par un
commit seul (7d8bba4) avant d'ouvrir une source, lues avec leurs sous-pages
— les enfants, la maladie, les élus, la réversion, les cotisations des
élus. Treize lignes sont épuisées, six explorées, ce qui leur reste nommé ;
la vingtième attend le propriétaire.

- *Quatre exemples au témoin* (`tests/temoins/exemples_officiels.yaml`,
  section de l'Ircantec). La page des conditions de départ en publie deux.
  Né le 1er avril 1965, parti à 63 ans avec 157 trimestres sur 171 : 85,50 %,
  par la durée, plus avantageuse que l'âge (0,83). La fiche
  `coefficient_anticipation_ircantec` disait cette seconde table de l'article
  16 invérifiable, « faute d'un exemple chiffré de la caisse, qu'elle ne
  publie pas » : elle en publie un, et le modèle le rend. Né en décembre
  1964, parti à 61 ans et 9 mois, avant l'âge légal : 76,25 %, à l'âge seul.
  Celui-là entre en écart connu : le modèle présume la complémentaire
  demandée avec le régime de base, l'ouvre un an plus tard, à l'âge légal,
  et lui donne 0,90 par la durée. C'est l'approximation que la fiche
  `liquidation_regime_par_regime` déclarait « non mesurée » ; elle l'est.
  Les deux autres sont des points : 494 pour 47 500 € en 2024, 458 et 298
  par tranche pour 50 000 € en 2019 (base documentaire). Le modèle les rend
  au point. L'oracle a appris pour eux deux choses : une source qui arrondit
  au point (`arrondi: point`), et un total seul, quand elle ne publie que lui
  (`tests/test_oracle.py`).
- *Ce qui concorde, et n'apprend rien de plus.* Le salaire de référence de
  2013 à 2026, les taux d'appel et théoriques des deux tranches, part de
  l'agent et part de l'employeur, de 2014 à 2026, la valeur du point de 2011
  à 2026 avec ses dates d'effet : tout est déjà dans
  `regimes/valeurs_point.csv` et la fiche du régime. Le plafond de l'annexe
  4-1, de 1962 à 2024 : ses soixante-trois années tombent sur la série du
  dépôt. La surcote, à ses deux taux, calculés à part : le IV de l'article 16
  que le modèle applique. L'âge du taux plein par génération, de 65 ans à 67
  ans dès 1955. La réversion et le versement unique sous 300 points, au
  salaire de référence de l'année qui précède. Le cumul plafonné, où
  l'Ircantec verse sa pension entière, ce que le modèle fait.
- *Ce que le modèle ne sert pas* (`docs/limites/ecarts-au-droit-positif.md`,
  « Les droits de l'Ircantec que le modèle ne sert pas »). Les points
  gratuits des arrêts de travail, de la maternité, de la paternité et du
  congé supplémentaire de naissance (depuis le 1er juillet 2026), dès trente
  jours d'indemnités ; de l'invalidité des deux tiers ; du service national
  et la bonification parentale, à la moyenne annuelle des points ; du
  chômage non cotisé, sur le SMIC. La validation des services d'avant 1973.
  La pension demandée avant le régime de base, dès 57 ans. La seconde
  pension de l'activité reprise depuis le 1er septembre 2024, sans
  majoration — deux liquidations au plus depuis le 1er août 2026. Les taux
  propres des PU-PH et MCU-PH, sans tranche. Et la date de chaque mandat
  d'élu, de 1973 à 2002, que le statut `elu_local` ne distingue pas : dite
  dans la fiche `elus_locaux_ircantec`, et l'inventaire refait.
- *Les pages de la caisse qui ne s'accordent pas entre elles.* La page
  « Départ à la retraite à taux plein à partir de l'âge légal » en est
  restée aux tableaux de 2023, sans la suspension : 63 ans et 171 trimestres
  pour 1964, quand la page des conditions de départ dit 62 ans et 9 mois et
  170. Les tableaux de minoration, republiés en juillet 2025, ne corrigent
  qu'une coquille (« 66 ans et 3 mois » pour 0,97) et attendent la loi de
  financement pour 2026. La page des retraites anticipées imprime « 60 ans
  et 3 6 mois » pour la carrière longue des nés en 1964. Et l'arrondi des
  points : la base documentaire arrondit au plus proche (457,71 donne 458),
  la page des élus tronque mandat par mandat (250,55 donne 250) — son
  exemple de deux mandats n'est pas transcrit.
- *La vingtième ligne est un simulateur.* Le « Guide des prélèvements
  sociaux » n'est pas un barème : un formulaire anonyme en plusieurs pages,
  qui ne montre les seuils de la CSG qu'après la saisie du revenu fiscal de
  référence. Sa nature est corrigée, et la ligne reste `a_explorer` : aucune
  saisie sans un lot approuvé par le propriétaire.
- *Fichiers.* `data/sources_a_explorer.yaml` ; le témoin et l'oracle ; les
  fiches `coefficient_anticipation_ircantec`, `liquidation_regime_par_regime`,
  `ircantec_valeurs_point`, `ircantec_majoration_enfants`,
  `reversion_ircantec`, `versement_unique_ircantec`, `seconde_pension` et
  `cumul_emploi_retraite_et_retraite_progressive` ;
  `regimes/elus_locaux_ircantec.yaml` et l'inventaire ; les limites.
- *Les pages du site.* Rien à écrire dans `pages.js` ni dans `index.html`,
  que tient une autre session : la date des mandats d'élus passe au paquet
  (`moteur/donnees.json`) quand GitHub relance `construire_donnees.py`, et
  le reste ne touche que le témoin, les fiches et les limites.
- *Reste.* Certifier 2022 à 2026, que le dépôt porte au niveau `haute` : un
  récupérateur des pages « Les paramètres utilisés par l'Ircantec » et
  « Valeur du point », en tableaux HTML, plus simple que le PDF de l'annexe
  8-1. Le lot de saisies du guide des prélèvements, si le propriétaire
  l'approuve. Et le lot suivant du bloc : la Cnav et service-public.
