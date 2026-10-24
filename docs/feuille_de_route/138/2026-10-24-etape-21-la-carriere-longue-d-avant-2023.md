# Étape 21 : la carrière longue d'avant 2023, au texte de chaque décret — chaque porte aux générations que sa rédaction nomme, et la durée d'assurance majorée de huit trimestres

**Reprise, au 24 octobre 2026.** Fait : les deux erreurs, corrigées dans la
table, certifiée au texte (la dernière génération de chaque porte, la durée
d'assurance majorée), dans les deux moteurs, les fiches et le registre. Reste
un point, que la lecture des décrets a trouvé : D. 16-1, la rédaction par
génération de l'État, vaut au 1er janvier 2011 (décret n° 2010-1748, sans
date d'application), quand la table ne l'applique qu'au 1er juillet 2011 ;
lire comment le SRE l'appliquait, puis la dater pour l'État seul (fiche
`duree_requise_carriere_longue_fonction_publique`, à relire). Détail : cette
note.

**Le 24 octobre 2026, la demande.** Le propriétaire, dans la quatrième vague
des sessions du jour : l'étape 21, que la confrontation de Nos Retraites
(action 137, note du 24 octobre) venait d'ouvrir. Deux erreurs du moteur :
`CarriereLongue._portes` retenait pour chaque porte la ligne de la plus haute
génération qui ne dépassait pas celle de l'assuré, et l'étendait ainsi à
toutes les générations suivantes ; et la durée d'assurance majorée de huit
trimestres, que les rédactions d'avant novembre 2012 exigeaient, n'était pas
vérifiée. Le test d'abord, chaque décret lu à sa rédaction.

**Ce que dit le droit, lu le jour même** (journal de veille du 24 octobre,
« action 138, étape 21 » ; fiches `carriere_longue` et
`duree_requise_carriere_longue_fonction_publique`).

- *Les portes.* La rédaction du 2 juillet 2012 de D. 351-1-1
  (LEGIARTI000026139949, pensions de novembre 2012 à août 2023) ouvre
  soixante ans à qui a débuté avant vingt ans (I), et ses portes plus
  précoces bloc par bloc (II) : « A.-Pour les assurés nés en 1952 », 59 ans
  et 4 mois avant dix-sept ans ; « B.-Pour les assurés nés en 1953 », 56 ans
  avec huit trimestres de plus, 58 ans et 4 mois avec quatre, 59 ans et 8
  mois avant dix-sept ans ; de 1954 à 1956, les deux portes des débuts avant
  seize ans ; en 1957, 57 ans avec huit trimestres de plus et 59 ans et 8
  mois sans ; de 1958 à 1960, la seule porte des huit trimestres de plus,
  « à compter du 1er janvier 1960 » à 58 ans. La rédaction de 2010
  (LEGIARTI000023397567) a la même forme, en onze blocs, de « nés avant le 1er
  juillet 1951 » à « nés à compter du 1er janvier 1960 ». La circulaire Cnav
  n° 2012-60 le lit de même : « avant 16 ans ou 17 ans selon son année de
  naissance et l'âge de départ fixé [pour] sa génération » (point 211).
- *La durée d'assurance.* Le chapeau des rédactions de 2003
  (LEGIARTI000006736521) et de 2010 n'ouvre le dispositif qu'aux assurés qui
  justifient, tous régimes, « d'une durée minimale d'assurance ou de périodes
  reconnues équivalentes au moins égale à la limite fixée en application du
  deuxième alinéa de l'article L. 351-1 majorée de huit trimestres » ; la
  Cnav y compte « tous les trimestres retenus pour déterminer le taux de la
  pension » (circulaire n° 2003-46, point 111), et le décret de 2012 « supprime
  par ailleurs la condition de durée d'assurance totale pour tous les âges de
  départ » (circulaire n° 2012-60, point 2).
- *Les autres régimes* auxquels le modèle ouvre la même table ont les mêmes
  portes et la même durée majorée : les artisans et les commerçants (décret
  n° 73-937, article 3 bis), les non-salariés agricoles (décret n° 55-753,
  article 28 ter, puis D. 732-40, « dans les conditions prévues » à D. 351-1-1),
  les fonctionnaires (L. 25 bis du code des pensions, « au moins égale à 168
  trimestres » de 2005 à 2008, puis la durée de l'année des soixante ans
  majorée de huit trimestres ; D. 16-1, dont les blocs des nés de 1952 à 1960
  sont ceux du régime général).
- *Aucun exemple chiffré publié* de l'une ou l'autre règle : ni la circulaire
  n° 2003-46, ni la n° 2012-60, dont les exemples ne portent que sur les
  périodes réputées cotisées. Les tests posent leurs cas à la main, depuis le
  texte.

**Ce qui est fait.**

- *La donnée et sa certification.* `carriere_longue.csv` porte deux colonnes
  de plus : `generation_fin`, la première génération que la ligne ne vise
  plus (« nés en 1953 » : 1954 ; « nés avant le 1er juillet 1951 » : 1951,5 ;
  2100 sans fin), et `trimestres_assurance_supplementaires`, les huit
  trimestres d'assurance des lignes de 2004 et de 2011, vide depuis 2012. Le
  récupérateur (`dila_legi_parametres_retraite.py`) les lit : la fin de chaque
  bloc dans son en-tête, celle d'une adaptation du II à l'adaptation suivante,
  la durée d'assurance dans le chapeau ; la certification
  (`verifier_donnees.py`) les met dans la clé de chaque porte. Les
  quatre-vingts portes, relues au texte, identiques.
- *Les deux moteurs* (`CarriereLongue`, `scenarios/actuel.py`, et son jumeau
  de `regimes.js`) : une ligne ne couvre que les générations de
  `generation` à `generation_fin` exclue, et parmi celles qui couvrent
  l'assuré, la plus haute génération l'emporte — l'adaptation du II sur la
  règle générale ; `age_de_depart` et `age_propose` lisent la durée
  d'assurance, que les trois appelants passent : celle que le taux lit, au
  relevé (`ouvrir`), et, pour dater un départ sans relevé
  (`age_carriere_longue`, `departs.py`), les trimestres de la carrière, ceux
  des enfants et les étrangers (`duree_d_assurance`, la lecture
  d'`age_taux_plein_droit`). Le paquet passe à la version 32.
- *Les tests*, vus rouges pour la raison attendue
  (`tests/test_verification.py`, `tests/test_simulateur.py`,
  `tests/test_droits_contrefactuels.py`) : le récupérateur sur les trois
  formes de rédaction ; dans les deux moteurs, le né de janvier 1955 entré à
  seize ans, qui ne part qu'à 60 ans, celui de juin 1953, à 59 ans et 8
  mois ; le né de 1957 entré avant seize ans, sept trimestres au-delà de la
  durée requise, refusé à 59 ans et 4 mois et ouvert à 59 ans et 8 mois ;
  celui de 1958 à la durée nue, refusé à 59 ans et 8 mois ; le né de mars
  1950, 164 trimestres cotisés et 164 d'assurance à 59 ans, en avril 2009,
  refusé, et ouvert quand ses deux années sans rien sont au chômage
  indemnisé ; au droit du 31 août 2023, le né de 1966 entré à seize ans
  part à 60 ans. Le test de la durée fixe des fonctionnaires d'avant 2009
  (`tests/test_oracle_carriere_longue_fonction_publique.py`) attendait la
  porte ouverte à 160 trimestres cotisés et 160 d'assurance, contre les 168
  de L. 25 bis : son fonctionnaire a désormais trois années validées sans
  cotisation, pour l'éducation d'un enfant, et le cas de 160 d'assurance est
  refusé. Les cas du moteur disent le jour de naissance, le 15 : la garde
  des présomptions de GitHub, qui les rejouait nés le 1er, une pension prise
  un mois plus tôt, les avait fait tomber après l'envoi.
- *Les fiches* `carriere_longue` et `duree_requise_carriere_longue_fonction_publique`
  (lectures, effet, une question à relire), les limites (`parametres.md`,
  `1-certification.md`), le registre (`nosretraites_cas_types`, 138.21 :
  repris), et le cliquet des textes, abaissé des sept rédactions qui y prennent
  un statut.

**Ce que la correction déplace**, régénération faite (`regenerer.py`, puis
`resumer_temoins.py`). Aucune pension des 902 témoins de simulation, ni le
coût agrégé, ni ses variantes (`agregats.json` inchangé). Un témoin bouge,
`etranger_portugal_carriere_longue` : né en mai 1958, entré au Portugal à
quinze ans et dix mois, il n'a que trois trimestres à la fin de l'année de
ses seize ans ; la porte des débuts avant dix-sept ans des nés de 1953 lui
ouvrait 59 ans et 8 mois, le texte lui ouvre 60 ans, l'âge où il part : son
âge d'ouverture opposable passe de 59,67 à 60, sa pension ne bouge pas. La
page Méthode date du jour la certification de la table ; le tableau de bord
compte un point repris de plus, et sept rédactions sans statut de moins.

**Ce qui reste.** La date de la rédaction par génération de l'État (bloc
« Reprise »). Au propriétaire, rien à trancher. Aux pages, rien : le site lit
le paquet, que GitHub refait.

*Fichiers.* `data/reference/legislation/carriere_longue.csv`,
`data/derive/certification.json`, `scripts/fetch/dila_legi_parametres_retraite.py`,
`scripts/verifier_donnees.py`, `scripts/construire_donnees.py`,
`src/retraite_notionnelle/scenarios/actuel.py`, `droit/ouvrir.py`,
`droit/departs.py`, `moteur/js/regimes.js`, `droit/ouvrir.js`,
`droit/departs.js`, `contexte.js`, les quatre fichiers de tests, les deux
fiches, les deux limites, `referents.yaml`, `sources_a_explorer.yaml`,
`perimetre.yaml`, cette note et l'entrée du journal de veille.
