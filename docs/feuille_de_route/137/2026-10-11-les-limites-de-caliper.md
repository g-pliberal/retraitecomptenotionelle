# Les limites de CALIPER, lues sur le site de la DREES et confrontées à `docs/limites/`

**Le 11 octobre 2026, au soir : depuis le poste du propriétaire, le site de la
DREES répond, et la confrontation que la reprise gardait est faite.**

- *La demande.* Le propriétaire, dans une session de bureau : « fais le
  point 5, le site de la DREES » — le site que le réseau de sortie du cloud
  refuse depuis le matin, et ce que la reprise de l'action en attendait, la
  liste des simplifications de CALIPER confrontée à `docs/limites/`.
- *L'accès.* Depuis le poste, `curl` reçoit la page CALIPER (200), la page du
  document de travail et son PDF, le DT 111 (Lermechin, Duc et Burricand,
  novembre 2011, `dt111.pdf`). Le Dossier solidarité et santé n° 37 (Duc et
  Lermechin, mars 2013), que le registre des modèles n'avait lu que par un
  miroir, a changé d'adresse — l'ancienne rend 404 — et se lit sous
  `/publications/dossiers-solidarite-et-sante-1998-2016/` (`dss37.pdf`). La
  page dit toujours que l'outil « a été réécrit en R », son code étant celui
  de `calcul_pension`.
- *Il n'y a pas de liste de « simplifications ».* Les deux documents disent
  ce que l'outil ne fait pas dans une section, « Développements et limites
  de l'outil », et dans leur encadré 1, sur la qualité des données de l'EIR et
  de l'EIC. C'est cette liste qui est confrontée, limite par limite :

  | Limite de CALIPER (DT 111, 2011 ; Dossier n° 37, 2013) | Ce qu'en fait le dépôt |
  |---|---|
  | Des droits individuels seulement : ni réversion ni minimum vieillesse, qui demandent le ménage | Les calcule, en règles approchées : `reversion`, `minimum_vieillesse` (l'ASPA du ménage) |
  | Dix régimes, la SNCF ensuite ; les libérales et les non-salariés agricoles « en cours » en 2013 ; une part des retraités de 1938 tout entière hors champ | Tous les régimes à l'inventaire, calculés ou déclarés (`4-regimes-incomplets.md`), libérales et exploitants compris |
  | L'écrêtement du minimum contributif sur la pension tous régimes, depuis 2012, mal estimé faute de tous les régimes | Servi, pensions étrangères déclarées comprises (`ecarts-au-droit-positif.md`) |
  | Les points de la tranche C de l'Agirc confondus avec ceux de la tranche B dans l'EIR 2004, leur abattement propre ignoré | Suivis de l'acquisition à la liquidation depuis le 28 septembre 2026 (`coefficients_anticipation_agirc_arrco`) |
  | Les artisans et les commerçants : le salaire annuel moyen sur les seuls salaires d'après 1973 | Le régime en points d'avant l'alignement de 1973, ses points conservés et convertis (`cancava`, `organic`) |
  | Les versements forfaitaires uniques, absents de l'EIR 2004 | Servis, en règle approchée (`versement_forfaitaire_unique`) |
  | La catégorie active ou sédentaire, les trimestres de surcote et les trimestres cotisés, absents des données | Saisis ou tirés de la carrière : le dépôt part d'une carrière, non d'un échantillon |
  | Des périodes régularisées tard, le plus souvent à la liquidation : chômage non indemnisé, service militaire, étranger | Même limite pour un relevé déposé avant le départ : déclarée ce jour, `5-hors-du-modele.md` |
  | Une règle mise en œuvre par les caisses après sa date officielle : le minimum contributif majoré de 2004 | Même limite, le modèle servant la date légale : déclarée ce jour, `5-hors-du-modele.md` |
  | Des subtilités très complexes, pour une part infime des retraités, non codées | Écrites une à une (`ecarts-au-droit-positif.md`) |
  | Une réforme ne se simule que sur une carrière complète, d'où PROMESS | Le site prolonge la carrière jusqu'au départ (`prolonger_releve`) ; la page Coût part de ses grilles |

  Le dépôt lève presque toutes les limites qui tiennent à l'outil. Celles
  qui tiennent aux données des échantillons ne le concernent pas, sauf une,
  qui revient par le relevé que l'assuré dépose.
- *Ce qui change.* Deux limites partagées, que rien ne disait, sont écrites
  dans `docs/limites/5-hors-du-modele.md` : le relevé souvent complété à la
  liquidation seulement, à la suite des quatre choses que le document ne
  donne pas ; la règle servie à sa date légale quand une caisse l'a mise en
  œuvre plus tard, au reste du périmètre. Le registre des sources passe
  `drees_caliper` à `epuise`, l'accès restant `refus` pour le cloud ; le
  registre des modèles corrige l'adresse du Dossier n° 37 et date sa
  lecture. Aucun résultat ne bouge.
- *Ce qui reste.* Le site ne dit pas à qui dépose son relevé qu'il peut
  manquer des périodes régularisées au départ : une phrase pour la session
  du site. De CALIPER, rien d'autre : sa validation sur les pensions réelles
  de l'EIR 2004 reste au chantier 138.14, au CASD.
