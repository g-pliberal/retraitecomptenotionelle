# Étape 12, dixième partie : le RCI et la cotisation minimale de l'indépendant en cumul

**Le 19 octobre 2026, la demande.** Deuxième salve de la vague B du 19 octobre,
session 13 : le point « à lire, le RCI et la cotisation minimale de
l'indépendant en cumul » du bloc de l'étape, le 2 de « Ce qui reste » de
`…-nouvelle-pension-de-l-independant.md` ; règle du scénario 1, en Python puis
en JavaScript.

**Ce que dit le droit** (journal de veille,
`2026-10-19-action-138-etape-12-rci-et-cotisation-minimale.yaml`).

- *Le RCI.* Jusqu'au 25 juin 2024, « les cotisations versées au régime
  d'assurance vieillesse complémentaire obligatoire par un retraité de ce
  régime afférentes à des périodes postérieures à la date d'arrêt du compte ne
  sont pas productives de droits » (règlement du RCI, article 4) ; depuis,
  « Sous réserve des dispositions du deuxième alinéa de l'article 27 ». Les
  alinéas 2 à 5 de l'article 27, que l'arrêté du 19 juin 2024 écrit,
  « entrent en vigueur le 1er janvier 2025 » (son article 2) : en cumul
  intégral (L. 634-6, alinéas 3 à 6), « l'assuré se constitue de nouveaux
  droits à pension au titre du présent régime » ; une seule seconde pension,
  « calculée, liquidée et servie dans les conditions applicables à la pension
  de vieillesse du présent régime », demandée « en même temps que celle du
  régime de base ». En 2027 (arrêté du 21 septembre 2026), au cumul entier du
  3° du A du III de L. 161-22.
- *La cotisation minimale.* « Pour les assurés en activité », 450 SMIC
  horaires « à compter des cotisations annuelles dues au titre de l'année
  2023 », passé quatre-vingt-dix jours d'affiliation (D. 633-2) : rien n'en
  dispense le pensionné, ni là ni ailleurs dans l'index LEGI. La Cnav : « Une
  cotisation minimale de retraite de base permet aux travailleurs
  indépendants de valider 3 trimestres de retraite par an » ; ceux de la
  nouvelle pension « sont validés dans les conditions de droit commun », et
  son revenu annuel moyen « correspond aux cotisations versées » (R. 634-1 ;
  R. 351-29, I, B, par D. 634-3).
- *La caisse.* Ni instruction ni exemple de la seconde pension du RCI ;
  l'Urssaf et la Sécurité sociale des indépendants refusent le réseau de la
  session.

**Ce qui est fait.**

- *Les deux moteurs* : `_revenus` (`revenus`, `seconde.js`) donne à la
  nouvelle pension de base le revenu cotisé, l'assiette minimale de l'artisan
  et du commerçant comprise ; `_seconde_retraite_rci` (`secondeRetraiteRci`)
  achète les points du RCI des mois de cumul intégral depuis 2025 — au taux de
  chaque tranche sur le revenu déclaré, ou par la part complémentaire du
  forfait du micro-entrepreneur —, au prix de l'année, et les sert sans
  coefficient, à la date de la nouvelle pension de base.
- *Tests* : quatre dans `test_emploi_retraite.py`, posés à la main
  (450 × 11,65 € et 450 × 11,88 € ; 8,1 % / 21,532 €, au point de 1,335 € ;
  12,3 % × 16,5 % du forfait), et leur jumeau dans `moteur.test.js`, vus
  rouges ; un témoin, `seconde_pension_artisane_au_minimum_2026`.
- Fiche `seconde_pension` : D. 633-2 et six rédactions des articles 4 et 27
  du règlement dans les versions, deux contenus, deux approximations de plus,
  les lectures.

**Mesuré.** Python et JavaScript au bit près sur cinq cas et sur le témoin
nouveau. Un témoin bouge, `seconde_pension_commercant_2025` : 61 € de RCI
s'ajoutent à ses 631 €, 45,7 points de ses sept mois de 2025. L'artisane qui
déclare 5 % du salaire moyen en 2024 et 2025 : six trimestres et 97 € au lieu
de deux et 13 € ; 7,8 points de RCI, 10,55 €. Le micro-entrepreneur vendeur :
39,5 points, 52,67 €. Rien avant 2025 : le commerçant parti de son cumul en
juillet 2024 n'a que sa pension de base.

**Trouvé en chemin.**

- *Le RCI en cumul plafonné.* L'article 27 soumet la pension du RCI aux
  règles de cumul de la base : « suspendu pour la même durée » jusqu'en 2024,
  « la section 3 du chapitre 4 du titre III du livre VI » depuis, L. 161-22 et
  L. 634-6-1 en 2027 ; la Cnav : « Les règles du cumul emploi-retraite du
  régime de base des travailleurs indépendants s'appliquent au régime
  complémentaire ». Le modèle le sert entier (fiche
  `cumul_emploi_retraite_et_retraite_progressive`, qui l'avait « à lire »).
- *Le versement forfaitaire unique du RCI* : sous quarante points, ou quand la
  base en a fait un (articles 39 et 40) ; le modèle ne le fait à aucune
  pension du RCI.
- *La classe* : les secondes retraites des autres complémentaires —
  l'Ircantec depuis le 1er septembre 2024, la RCO, les sections libérales — ne
  sont ni calculées ni nommées, `non_calcules` ne portant que les bases.

**Pour les pages**, que leur session tient. `droitsDuCumul` (`pages.js`)
tient pour nouvelle pension de base toute pension qui n'est pas de
l'Agirc-Arrco : la seconde retraite du RCI s'y lit « une nouvelle pension de
61 € par an […] — 0 trimestres, au taux plein — ». Elle se dit comme celle de
l'Agirc-Arrco : « une seconde retraite complémentaire du RCI de 61 € par an,
sur 46 points ». Aucun témoin de page ne la montre.

**Ce qui reste.**

1. Au RCI, une session chacun : le cumul plafonné (article 27), dans
   `cumul.py` et son jumeau ; le versement forfaitaire unique (articles 39 et
   40), aux deux pensions.
2. La phrase des pages, ci-dessus : la session des pages.
3. À lire : les secondes retraites de l'Ircantec, de la RCO et des sections
   libérales.
4. Déclarés, légers : deux assiettes minimales l'année du départ, de part et
   d'autre ; le pensionné au RSA ou à la prime d'activité, que la saisie du
   cumul ne dit pas, sans dispense.
5. À la fin de l'étape : les limites (`ecarts-au-droit-positif.md`) et
   l'architecture diront la seconde retraite du RCI et l'assiette minimale.
6. Les restes du bloc : la veille du projet de loi de financement pour 2027 ;
   au propriétaire, la part de base de l'ordre de D. 133-4 de 2016 à 2019.
