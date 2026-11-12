# Étape 7 : les articles qu'aucune fiche ne cite, lus et confrontés au modèle

**Reprise, au 12 novembre 2026.** Rien n'est commencé. La passe de lecture ne
lisait que les articles que les fiches citent déjà. Elle a croisé des
rédactions récentes qu'aucune fiche ne suit, et que personne n'a confrontées
au modèle : trois droits ajoutés en 2026 à la pension des ouvriers de l'État,
la rente d'accident du travail dans la durée d'assurance au 1er novembre 2026,
un article du code de la sécurité sociale refait à la même date, un renvoi
mort dans le régime des avocats. À faire : lire chacune, dire si le modèle
sert ce qu'elle règle, et la rattacher à une fiche. Cette étape lit et classe,
sans écrire de règle : ce qui change un calcul est listé pour le propriétaire.
Elle peut se mener pendant qu'une autre session écrit dans le modèle.

**La demande, le 12 novembre 2026.** La passe de lecture de l'action 184 a
trouvé des points que le modèle n'applique pas ou qu'elle n'a pas pu vérifier
(note `184/2026-11-12-etape-6-bilan-de-la-passe.md`). La session
d'orchestration les a listés au propriétaire, qui a répondu : « Fait une étape
pour chaque point du modèle ». Celle-ci en est une.

**Ce qui est su**, des notes des lots (`184/2026-11-12-etape-6-…`).

- Décret n° 2004-1056, ouvriers de l'État, article 12 : trois rédactions de
  2026 — la majoration des sapeurs-pompiers volontaires (8°, pensions à
  compter du 1er juillet 2026), un trimestre de bonification par enfant né
  depuis 2004 pour l'ouvrière (2° bis, décret n° 2026-699, à compter du 1er
  septembre 2026), la majoration des élus locaux (9°, à compter du 1er janvier
  2027). Lot des autres régimes, « Vu en passant ».

- Même décret, article 7, fiche `limite_age_ouvriers_etat` : du 1er septembre
  2023 au 2 janvier 2025, les services faits après la limite d'âge au titre du
  maintien ou de la prolongation comptaient-ils ? Lot des autres régimes,
  « Une question ouverte ».

- Article L. 351-3, 1°, du code de la sécurité sociale (LEGIARTI000051288449,
  1er novembre 2026, loi n° 2025-199, article 90) : la rente d'accident du
  travail « pour une incapacité permanente professionnelle ». Aucune fiche ne
  lit le 1°.

- Article R. 351-37, rédaction du 1er novembre 2026, qu'aucune fiche ne cite.

- Article R. 653-2, avocats : il renvoie aux III et IV de l'article 20 de la
  loi n° 2010-1330, abrogés pour les pensions de 2026.

- La fiche `sam_parents_24_23` ne cite pas l'article R. 173-3-2 par son
  identifiant (LEGIARTI000054589934), que le moteur applique déjà.

**Ce qu'il y a à faire.** Pour chaque point : lire la rédaction dans l'index
(`dila_cherche.py legi --num <article> --le <date>`), dire si le modèle sert
ce qu'elle règle, et lui donner sa place — citée par la fiche qui la porte, ou
une fiche nouvelle si la règle n'en a pas. Ce qui change un calcul ne se porte
pas au modèle ici : la fiche le déclare, la note le liste, et le propriétaire
décide de l'étape qui l'écrira. Cette étape se mène sur Fable 5.2, comme toute
lecture du scénario 1, et suit `docs/veille_droit.md`.

**Fini quand** chaque point de la liste a sa fiche et son statut, et que ce
qui change un calcul est porté au propriétaire en une liste.
