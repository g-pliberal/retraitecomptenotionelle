# Le sixième domaine, étape 1 : les fiches lues à la source

Session de nuit du 16 octobre 2026, sans le propriétaire. L'étape 1 du gabarit
(`2026-10-14-sixieme-domaine-mesure.md`) : lire à la source les périodes
assimilées qui manquent au modèle, l'apprentissage d'abord. Aucun fichier du
modèle, du site ni des témoins ne bouge.

## Ce qui est fait

L'index LEGI est à jour au 15 octobre 2026, et `textes.py --inscrire` a porté
à la liste de contrôle 266 rédactions parues depuis (commit à part). Quatre
fiches naissent dans `data/reference/regles/`, toutes `pas_encore_modelisee`,
domaine `periodes_assimilees`, étape `compter_les_durees` :

- **`apprentissage`** — trois versions par la date de la période : l'assiette
  forfaitaire d'avant 2014 ; depuis 2014, la durée du contrat garantie
  (L. 6243-3, D. 373-3 et D. 373-4), les trimestres complémentaires comptant
  pour le taux et le prorata, non pour la durée cotisée ; depuis 2022, le
  versement du payeur forfaitisé, le droit inchangé. Lue dans la circulaire
  Cnav 2016-41, qui porte quatre exemples.
- **`stages_formation_professionnelle`** — le 8° de L. 351-3 (tous les stages
  depuis 2015) et le 9° (les TUC et quatre stages d'insertion de 1977 à 1992,
  pour les pensions prenant effet depuis le 1er septembre 2023) : cinquante
  jours de stage dans l'année valent un trimestre assimilé, en plus de
  l'assiette forfaitaire. Lue dans la circulaire Cnav 2024-18, qui porte
  quatre exemples.
- **`sportifs_haut_niveau`** — depuis 2012, quatre-vingt-dix jours
  d'inscription valent un trimestre, sous conditions d'âge et de ressources,
  seize trimestres au plus, trente-deux depuis le 1er septembre 2023.
- **`conge_supplementaire_naissance`** — cinquante-huit jours indemnisés
  valent un trimestre, depuis le 1er juillet 2026.

L'inventaire des avantages non contributifs renvoie à ces fiches ; le cliquet
des textes passe de 9 768 à 9 762.

## Ce que la lecture apprend pour les étapes suivantes

- Deux règles de décompte, et non une : l'apprentissage complète, année par
  année, jusqu'à la durée du contrat (un fait « contrat », avec ses dates) ;
  les stages, les sportifs et le congé comptent des jours dans l'année (un
  fait « période », avec ses dates et sa sorte). L'étape 2 donne à
  `periode_assimilee` un motif par sorte, et à l'apprentissage, qui est un
  emploi salarié, un attribut sur la ligne d'emploi plutôt qu'une période à
  part.
- Les trimestres complémentaires de l'apprenti et les trimestres assimilés des
  stages ne sont pas cotisés : ils n'ouvrent pas la carrière longue
  (D. 351-1-2 ne les nomme pas).
- Les exemples publiés à rejouer à l'étape 4 : les quatre de la circulaire
  2016-41, dont le troisième porte une date de fin fautive (« 14 février 2015 »
  pour un contrat compté sur quinze mois) ; les quatre de la 2024-18.

## Ce qui reste de l'étape

Les `a_relire` des fiches : une circulaire Cnav sur l'apprentissage
postérieure au décret de 2022, qui a retiré de D. 373-4 le II disant la portée
des trimestres ; l'arrêté du 5 juin 1979 ; les décrets n° 2015-1240 et du
financement des stages d'avant 2015 ; une circulaire sur les sportifs ; le
décret n° 2026-425 pour les congés du premier semestre 2026 ; la MSA pour les
apprentis agricoles. Rien n'en dépend pour ouvrir l'étape 2.

## Ce qui attend le propriétaire

Rien de neuf : la décision de la proposition, à l'étape 7.
