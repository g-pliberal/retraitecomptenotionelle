# Étape 9, les quatre restes de la surcote parentale : le minimum garanti et les libéraux corrigés, la circulaire et le trimestre daté déclarés

**La demande.** La vague du 23 octobre 2026 : la session de suivi « Qu'est-ce
qu'il reste à faire ? » lance, sur la demande du propriétaire (« Fait ça »),
douze sessions en parallèle, une étape chacune. Celle-ci reprend, dans l'ordre
de leur poids, les quatre restes que la note du 18 octobre
(`2026-10-18-l14-v.md`, « Ce qui reste ») laisse dans la fiche
`surcote_parentale`, et qui relèvent de la carte plus que du jaune : la
circulaire Cnav et un exemple du régime général ; le minimum garanti, que le
moteur surcotait de la parentale quand il efface la surcote de L. 14, III ; la
CNAVPL, dont l'étape qui complète composait encore les deux coefficients ; le
trimestre d'enfant, que la CNRACL date et que le moteur ne date pas. Ce qui ne
se lit pas d'ici se déclare. Scénario 1, sur Opus, après
`python scripts/veille_droit.py` ; l'index LEGI mis à jour au 22 octobre 2026.

## Ce que les textes et les caisses disent

- **Le minimum garanti se compare à la pension normale.** L. 17 du code des
  pensions (LEGIARTI000048697797) dit seulement que « le montant de la pension
  ne peut être inférieur » au minimum ; L. 14, IV, majore la pension « dans
  les mêmes conditions que celles prévues au III ». Le service des retraites
  de l'État (« Le minimum garanti », lu le 23 octobre) : « Le montant normal
  de votre pension est donc comparé à celui du minimum garanti. Dans tous les
  cas, c'est le montant le plus favorable qui vous est payé ». Les pages de la
  CNRACL sur le minimum garanti ne parlent pas de la surcote.
- **Les libéraux ont la règle du régime général.** L. 643-3, I
  (LEGIARTI000047453031, puis LEGIARTI000053280388 pour les pensions de
  septembre 2026 et après) sert la surcote parentale « dans les mêmes
  conditions que celles prévues à la première phrase du quatrième alinéa du
  présent I », la surcote, que R. 643-8 (LEGIARTI000047985850) fixe à 0,75 %
  par trimestre accompli avant le 1er septembre 2023 et à 1,25 % depuis.
- **Le régime général n'a toujours ni circulaire ni exemple.** La recherche de
  la base documentaire de la Cnav (son API, `search/custom`) ne trouve
  « surcote parentale », « 351-1-2-1 » ni « surcote au titre des enfants »
  dans aucune référence ; son exposé « Surcote », modifié le 6 janvier 2026,
  n'en parle pas, ni le paragraphe « L'incidence sur la surcote » des
  circulaires 2023/19, 2024/25 et 2026/7 ; la page « Être parent » de
  l'Assurance retraite donne les conditions et le taux, sans exemple ; la
  fiche F19643 de service-public (vérifiée le 1er janvier 2026) ne chiffre que
  la surcote ordinaire.
- **La CNRACL date le trimestre d'enfant** : la surcote au titre des enfants
  ne court que « sous réserve que l'assuré justifie à partir de cette date »
  d'un trimestre d'enfant et de la durée, et l'assuré « n'est pas tenu de
  remplir les conditions à l'âge anticipé ». Son exemple 3, une majoration
  pour enfant handicapé acquise à 62 ans et 6 mois, est né en 1964 : la
  suspension de 2026 a ramené l'âge légal de cette génération sous 63 ans, et
  il ne se rejoue plus.

## Ce qui a changé

- **Le minimum garanti** (`droit/completer.py`, `droit/completer.js`) : les
  trimestres de surcote parentale de chaque pension se comptent avant les
  minima (`trimestres_de_surcote_parentale`), et le minimum garanti se compare
  à la pension qui porte les deux surcotes ; quand il l'emporte, il les efface
  l'une et l'autre, et le détail de la pension dit le montant normal (« 13,963.82
  € avec la surcote parentale, porté au minimum garanti »). Le module servait
  1,05 fois le minimum : 925 euros par an de trop pour une agente de la CNRACL
  née en 1969, partie en 2033 à 30 % du salaire moyen. Entre les deux — sous le
  minimum avec la seule surcote de L. 14, III, au-dessus avec les deux —, la
  pension normale, que le minimum ne relève plus. La correction vaut pour
  l'État, la CNRACL et le FSPOEIE, les trois régimes du code des pensions.
- **Les libéraux** (`droit/liquider.py`, `droit/liquider.js`) : la liquidation
  passe à l'étape qui complète le coefficient de surcote de chaque régime en
  points qu'il majore (`surcotes_des_points`, hors du schéma, comme les
  coefficients d'anticipation), et la surcote parentale de la CNAVPL se
  calcule sur la pension d'avant lui : 1,15 au lieu de 1,10 × 1,05 pour huit
  trimestres de surcote et quatre d'enfants.
- **Le test d'abord**, dans `tests/test_simulateur.py` : l'agente de la CNRACL
  à 30 % et à 40 % du salaire moyen, le minimum seul puis la pension normale ;
  la libérale partie à 66 ans ; la confrontation des deux moteurs, sept
  carrières au lieu de quatre. `test_le_minimum_garanti_efface_la_surcote`,
  dans `test_plafond_majoration_enfants.py`, perd la fin de son nom, devenue
  fausse.
- **La fiche** `surcote_parentale` reste `transcrite`, lue le 23 octobre ;
  `docs/methodologie.md` dit le minimum garanti et les libéraux.

Ce que les corrections déplacent : aucun des 889 témoins de simulation ni des
79 rendus de page ; aucune page du site n'en dit rien de faux, et rien n'est dû
à une session des pages.

## Ce qui reste

- **La circulaire Cnav**, quand elle paraîtra ; la fiche dit où on a cherché.
- **Le trimestre d'enfant daté**, déclaré plutôt que codé : tous les trimestres
  d'enfants du modèle naissent avec l'enfant et vont à la mère ; seule une
  majoration acquise tard — l'enfant handicapé (L. 351-4-1, L. 12 ter), que le
  modèle ne porte pas, ou l'adoption, que la chronologie ne connaît pas
  (fiche `majoration_duree_assurance_enfants`) — ferait jouer la date. D'ici
  là, seule une naissance déclarée dans l'année qui précède l'âge légal de la
  mère, que la saisie accepte, s'en écarte.
- **La même classe d'erreur, ailleurs** : la pension que le plancher de la
  retraite progressive relève porte ensuite la surcote parentale, calculée sur
  le montant relevé ; lire si la caisse la calcule sur la pension d'avant le
  plancher, comme D. 351-2-1 le veut du minimum contributif (inscrit à la
  fiche `surcote_parentale`).
- Ce qui reste de l'action attend le propriétaire : la DREES refaite par le
  modèle (étape 8), l'indexation du stock du scénario 1 (étape 4), les cas
  types de l'étape 5, et sa clôture.
