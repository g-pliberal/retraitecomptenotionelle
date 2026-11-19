# Évaluation indépendante de la note de décision 0009

*Copie, au 18 novembre 2026, de l'évaluation remise au propriétaire, menée
sans lire l'évaluation précédente. Elle fonde le rectificatif du 19 novembre
2026 de la note. Les scripts de ses contrôles sont dans le dossier
`evaluation-du-18-novembre/`, à côté de ce fichier (`LISEZ-MOI.md`).*

## Verdict

**La note 0009 est la bonne décision. Je recommande de la poursuivre, après un
second rectificatif.** Son diagnostic est exact, les affirmations de droit que
j'ai relues tiennent toutes dans LEGI, et aucune des solutions qu'elle écarte
ne fait mieux. Rien de ce que j'ai trouvé ne la renverse.

Deux réserves portent sur son exécution, pas sur sa direction :

1. **Elle décide le principe, pas la forme exécutable.** Elle ne dit ni qui
   écrit la table d'une version, ni où un renvoi se résout. Le récupérateur de
   LEGI fait déjà les deux, et la note ne le nomme pas.
2. **Son étape 4 n'est pas un rangement.** Dater au jour les renvois des
   régimes corrige le modèle, donc déplace des résultats, sur plus de deux
   cents dates et non dix. La note promet pourtant qu'« aucun résultat chiffré
   ne bouge ».

Cinq points plus petits demandent chacun une phrase dans la note. Le plus
concret : une fois l'âge du taux plein écrit en renvois, le droit
contrefactuel au 31 août 2023 rendrait 65 ans au lieu de 67 si sa couche ne
gardait que l'âge légal.

Au 18 novembre, ni les cliquets ni l'étape de l'âge légal ne sont commencés
dans le dépôt. Tout cela se corrige donc avant leur premier commit.

## Ce que j'ai vérifié, et comment

Les affirmations de la note tiennent presque toutes : je les ai contrôlées une
à une, sans m'appuyer sur ses essais. J'ai relu la note en entier,
rectificatif compris, recompté ses chiffres par des scripts sur les fichiers
du dépôt, et relu ses textes dans l'index LEGI de la DILA, à jour au 16
novembre 2026. Je n'ai modifié aucun fichier du dépôt.

| Affirmation de la note | Contrôle | Résultat |
| --- | --- | --- |
| 562 valeurs de repli pour l'âge légal, 469 pour l'âge du taux plein | recompte des 873 périodes des 80 régimes | exact |
| 96 renvois aux deux fiches d'âge, dont 51 dès le début du régime ; 23 régimes sur 47 ont d'abord une valeur à eux | même recompte | exact |
| 2 570 renvois vers 50 fiches | même recompte | 2 573 aujourd'hui, 50 fiches |
| 65 fiches sur 267 confrontées à un exemple | lecture des fiches | exact |
| L. 161-17-2 : la loi de 2025 écrit l'âge des nés à compter du 1er septembre 1961 et renvoie les autres à sa « rédaction antérieure », pour les pensions à compter du 1er septembre 2026 | LEGIARTI000053280889 | exact, mot pour mot |
| D. 161-2-1-9 n'a pas été réécrit et dit encore 63 ans pour 1964 | LEGIARTI000047634502 | exact |
| R. 351-27 fixe 65 ans jusqu'en juin 2011 ; L. 351-8, 1° : l'âge légal « augmenté de cinq années », puis celui du « premier alinéa » « augmenté de trois années » | LEGIARTI000020082993, LEGIARTI000028498855 et LEGIARTI000047452736 | exact |
| D. 351-1-1 a six rédactions, D. 351-1-4 cinq | index LEGI | exact |
| La porte de 2023 de la carrière longue vaut 60 ans et 6 mois pour 1964 | texte et `carriere_longue.csv` | exact |
| Pour l'âge légal, la recherche du premier départ rend la date de la table d'aujourd'hui | force brute : les 19 358 jours de naissance de 1923 à 1975, cinq versions choisies à la date d'effet, contre la table fusionnée | 0 écart, 0 droit ouvert puis refermé |
| 130 fiches sur 267 citées dans le code | recompte | 114 dans `moteur/js`, 124 avec le Python et les scripts |
| 271 versions d'avant 1985, dont 100 supposées | note du dépôt du 17 novembre | 312, dont 122 |

Les deux dernières lignes sont des écarts de comptage, sans effet sur la
décision. Les scripts de ces contrôles sont dans le dossier
`evaluation-du-18-novembre/`.

## Ce qui tient

La direction est juste, pour six raisons que j'ai retrouvées dans le dépôt.

- **Le diagnostic est exact.** Le droit daté d'une même règle s'écrit bien à
  plusieurs endroits. `dureeRequise` (`moteur/js/droit/ouvrir.js`) en est la
  meilleure preuve : une dizaine de branches, où les dates d'effet de 2003,
  2009, 2023 et 2026 sont écrites dans le code.
- **Les deux axes sont nécessaires.** La porte de 2023 de la carrière longue
  se lit contre l'âge légal de 2023, pas contre la table fusionnée. La preuve
  de la note est juste.
- **Le mécanisme existe.** 197 fiches sur 267 ont déjà des versions, et le
  moteur en lit 80 par elles. La note fait rentrer dans la règle commune les
  règles qui y échappent : l'âge légal, la durée requise, l'âge du taux plein.
- **Les renvois des régimes restent.** Contre son brouillon, la note a raison
  de les garder : chacun est le droit de son régime à sa date.
- **Aucune solution écartée ne fait mieux.** Un seul de ses arguments est
  faible, sans changer la conclusion (voir « Erreurs de fait »).
- **La lecture qu'elle impose a déjà payé.** Lire chaque texte à sa
  disposition d'application a trouvé en deux jours l'erreur de la surcote de
  2004 à 2006 et cinq dates de régime fausses sur dix. C'est le meilleur
  argument pour la poursuivre.

Ses garde-fous sont les bons pour toucher l'étalon : cinq cliquets, deux
preuves par version reprise, les témoins comme alarme.

## Réserve 1 : la forme exécutable n'est pas décidée

**La note dit ce qu'une version porte, mais pas sous quelle forme le moteur la
lit, ni qui l'écrit.** Son rectificatif renvoie la question au début de
l'étape 2. C'est le choix qui engage le plus, et il est laissé à la session
qui code.

Ce que montre le dépôt :

- Le contrat de la fiche laisse `contenu` libre. Le renvoi que la note cite en
  exemple (`age_reference_decote_ieg`) est une phrase et un paramètre, qu'un
  code propre interprète.
- La table de l'âge légal n'est pas saisie. Le récupérateur
  `dila_legi_parametres_retraite.py` la lit dans LEGI, rédaction par
  rédaction, et elle est `certifiee`. Les deux copies d'avant réforme sont
  lues à la main, au niveau `haute`.
- Ce récupérateur fait déjà ce que la note demande. Il lit la date
  d'application en tête de chaque rédaction (`date_effet`). Il résout le
  renvoi de 2023 de la carrière longue contre l'âge légal de la date d'effet.
  Il ne lui reste qu'à ne plus fusionner (`_par_version`).
- `carriere_longue.csv` est déjà une table à deux axes : cinq dates d'effet,
  80 portes par génération. C'est l'exemple que la note cite elle-même.
- Trois fiches dépassent 100 000 octets, quand le dépôt interdit de lire en
  entier un fichier de plus de 50 000.

Deux risques si rien n'est écrit. Une session peut recopier à la main, dans la
fiche, des tables que le récupérateur lit aujourd'hui dans LEGI : la
certification reculerait. Et un renvoi résolu chez le lecteur échoue chez le
lecteur : sur un site statique, « arrête le calcul » veut dire une page qui ne
répond plus.

Ce que je recommande :

1. **La table d'une version reste lue dans LEGI par le récupérateur**, dans un
   fichier indexé par version, comme la carrière longue. La fiche déclare la
   version (bornes, texte, statut, renvoi) et désigne ses lignes. Les deux
   copies y gagnent le niveau `certifiee`.
2. **Les renvois se contrôlent à la fabrication, d'une fiche à l'autre.** Pour
   chaque renvoi, sur toute l'étendue des bornes de sa version, la fiche lue a
   une version et une seule, et aucune chaîne ne boucle. Le contrôle
   d'aujourd'hui (`noyau/partage.py`) ne regarde qu'une fiche à la fois.
   L'arrêt au calcul ne reste que comme ceinture.
3. **Les deux scripts de certification entrent dans l'étape 2** :
   `dila_legi_parametres_retraite.py` et `verifier_donnees.py`. Ni la note ni
   le brief ne les nomment.
4. **L'étape 2 se coupe en trois sessions**, chacune laissant les résultats
   identiques :
    - les versions deviennent la source, et la table fusionnée comme les deux
      copies sont fabriquées depuis elles, valeurs identiques, sans toucher au
      moteur ;
    - le moteur lit l'âge légal par ses versions, avec la recherche du premier
      départ ;
    - les deux droits contrefactuels deviennent des couches.
5. **La fin de l'étape 2 est un point d'arrêt** : on y mesure ce qu'elle a
   coûté avant d'engager l'étape 3. La note n'a ni estimation ni règle
   d'arrêt.

Le brief du 17 novembre donne tout cela à une seule session, sur dix fichiers
du moteur. Une migration arrêtée à mi-chemin est le cas que l'architecture
nomme le pire (§ 11), et la première de ces trois sessions suit sa règle : ce
qui passe dans une fiche devient une vue fabriquée dans le même commit.

## Réserve 2 : l'étape 4 déplace des résultats, et n'est pas mesurée

**Dater au jour les renvois et les périodes des régimes corrige le modèle,
donc déplace des résultats.** La note écrit pourtant qu'« aucun résultat
chiffré ne bouge », en fait le critère de fin de chaque étape, et la ligne 6
du chemin de l'architecture dit encore « inchangés ».

Ce que j'ai mesuré dans les 80 fichiers de régime :

- La note ne compte que les renvois aux deux fiches d'âge : 45 dates de
  bascule, dont dix « peuvent changer un résultat ». Tous renvois confondus,
  je compte 216 changements de renvoi après la première période d'un régime :
  173 débuts, 41 fins et 2 changements de cible. 180 tombent sur une frontière
  coupée à l'année.
- Les périodes ont 793 frontières. 38 périodes sur 873 sont datées au jour,
  les autres sont coupées à l'année.
- Les dix premières dates, relues au texte le 17 novembre, donnent cinq justes
  et cinq fausses. Trois étaient déjà déclarées « coupées à l'année ». Une
  cache une erreur de règle : la décote de la Banque de France n'est pas celle
  de la fonction publique.
- Les dates d'application anciennes ne se lisent presque jamais dans LEGI. Sur
  les 750 rédactions des articles de retraite du code, une phrase
  d'application figure en tête de 3 sur 306 avant 2010, contre 126 sur 195
  depuis 2020 (essai du 15 novembre).
- Retirer la valeur de repli n'est pas toujours neutre. Celle de l'âge légal
  ne sert plus, la table commençant à la génération 1900. Celle de l'âge du
  taux plein répond encore avant la génération 1930.

L'étape 4 est donc le gros du travail de la note, et le gros de son bénéfice
pour le scénario 1. C'est un audit du droit daté des régimes, pas une
restructuration.

Ce que je recommande :

1. **Écrire que l'étape 4 a deux sortes de commits.** Ceux qui ne déplacent
   rien : le texte cité, un repli mort retiré, une date au jour sans effet. Et
   les corrections, chacune avec son test tiré du texte et l'accord du
   propriétaire. Le rectificatif pose déjà cette règle pour la surcote ; elle
   vaut pour toute l'étape.
2. **Corriger la ligne 6 du chemin** et le critère de fin de l'étape 4 :
   « aucun résultat n'a bougé » ne vaut que pour la première sorte.
3. **Compter avant de commencer** : les 216 changements par renvoi, et ceux
   dont le texte n'est pas dans l'index.
4. **Ordonner par poids dans les résultats** : les régimes les plus peuplés et
   les périodes récentes d'abord, avec un budget.
5. **Ne pas faire attendre les corrections derrière la restructuration.** Le
   moteur sait déjà dater une période au jour (`date_effet`,
   `periodeDeLiquidation`). Les dates déjà relues peuvent se corriger
   maintenant, en parallèle des étapes 1 à 3, comme la surcote le 17 novembre.

## Cinq points à préciser

Aucun ne remet la décision en cause ; chacun se règle par une phrase dans la
note et un test.

**1. Une couche doit garder une réforme, pas une fiche.** Aujourd'hui, les
deux droits contrefactuels ne changent que trois règles : l'âge légal, la
durée requise et la carrière longue (`_sousLeDroit`). L'âge du taux plein
reste une table par génération, qui donne 67 ans sous les trois états du
droit. L'étape 3 la remplace par les renvois du texte : l'âge légal plus cinq
ans jusqu'en 2023, puis l'âge du premier alinéa plus trois ans. Si la couche
du 31 août 2023 ne garde que l'âge légal de 2011, la version de 2023 lira 62 +
3 = 65 ans.

Le fichier qui définit ces deux droits (`test_droits_contrefactuels.py`) ne
contrôle pas l'âge du taux plein ; je n'ai pas cherché si un autre test le
couvre par ricochet. Je recommande d'écrire ce test d'abord, et de définir
qu'un univers qui écarte une réforme garde la version précédente de chaque
fiche que cette réforme a réécrite, la liste se calculant depuis les textes
que citent les versions. « Prolonger » n'est d'ailleurs aucune des six
opérations de couche d'aujourd'hui, et ces deux droits vivent dans le code
(`DROITS_CONTREFACTUELS`), pas dans un univers.

**2. La recherche du premier départ vaut aussi pour la carrière longue.** Pour
l'âge légal, elle ne change rien : c'est le résultat de la force brute. Pour
les portes de la carrière longue, elle compte. Le moteur lit la porte dans le
texte de la date déclarée (`CarriereLongue.portes`), et le décret de 2026
abaisse d'un trimestre les portes des générations 1966 à 1970.

J'ai refait l'essai sur la table du dépôt, hors du moteur et la durée supposée
acquise. À la bascule du 1er septembre 2026, 1 856 dates de naissance sur 2
617 partent plus tôt par la recherche que par l'âge du texte de la date
déclarée. À celle de 2023, l'écart va dans l'autre sens. Je n'ai pas vérifié
ce que le moteur rend dans ces cas, qui supposent un départ déclaré avant la
bascule.

La note doit dire que la recherche couvre toute règle qui ouvre un droit, et à
quelle date se comptent alors les durées : aujourd'hui, au départ déclaré. À
l'étape 3, « aucun résultat ne bouge » peut donc tomber pour une bonne raison.
Le moteur a déjà une recherche de ce genre pour les périodes de régime
(fonction ouvertureDe) : il s'agit de l'étendre aux versions des fiches. Elle
peut ne s'arrêter qu'aux dates où une version change ; la force brute mois par
mois, que décrit le rectificatif, sert alors d'oracle au test.

**3. Le cinquième cliquet n'a pas de dénominateur.** Il vise « les chiffres de
la loi dans le code des règles, nommés un à un par l'étape qui pose les
cliquets ». Une liste choisie à la main ne garde que ce qu'elle nomme. Le
moteur déclare 745 constantes nommées, dont 131 portent une année ou une date,
et 77 dans le seul code des règles (mon recompte). Je recommande un relevé
mécanique : un test relève toute constante datée, et une liste qui ne peut que
raccourcir dit pour chacune si elle est du droit à migrer.

**4. Un renvoi a une cible précise et une opération d'une liste fermée.** L.
351-8 ne lit pas l'âge légal de l'assuré : il lit l'âge du premier alinéa de
L. 161-17-2, soit 64 ans pour tous. Le renvoi doit donc nommer une valeur de
la version lue, pas la fiche entière. L'essai de la note le sait, sa décision
ne l'écrit pas. Pour l'opération, les quatre essais n'en demandent que deux :
ajouter une durée, en retrancher une. Tout le reste devrait passer par une
fonction nommée, sinon le format devient un langage.

**5. Sans exemple officiel, une version n'a qu'une preuve.** La note demande
deux preuves, ou « aucun trouvé ». Or les exemples couvrent surtout les
dernières versions, et le rectificatif le dit lui-même : un cas calculé à la
main éprouve le code contre la lecture, pas la lecture contre le texte.
L'erreur de la surcote passait tous les tests, et c'est une relecture qui l'a
trouvée. Je recommande, pour les versions sans exemple qui pèsent dans les
résultats, une seconde lecture du texte par une session qui n'a pas vu la
première.

## Erreurs de fait relevées

J'en relève cinq, dont aucune ne touche le droit ni la direction.

| Ce que dit la note | Ce que je trouve | Portée |
| --- | --- | --- |
| Étape 2 : « la fin des deux copies et de `TableRecouverte` » | `_sousLeDroit` pose aussi `TableRecouverte` sur la durée requise, qui ne migre qu'à l'étape 3 | à corriger dans le brief de l'âge légal |
| « Tout en tables datées : une table n'a qu'une date qui décide » | `carriere_longue.csv` en a deux, la date d'effet et la génération | l'argument est faible, la conclusion tient |
| Le corps de la note garde trois phrases que son rectificatif dit fausses : le champ `code` en prose, legiretraite, la surcote de 2004 à 2006 | la note est gelée, son corps ne se récrit pas | faible : les briefs exigent déjà de lire le rectificatif, et devront exiger aussi le second |
| 130 fiches sur 267 citées dans le code | 114 dans `moteur/js`, 124 avec le Python et les scripts | nulle |
| 271 versions d'avant 1985, dont 100 supposées | 312, dont 122, selon le recompte du dépôt du 17 novembre | nulle |

## Amendements recommandés

Dix amendements, rangés par l'étape qu'ils doivent précéder. Ils tiennent dans
un second rectificatif à la fin de la note, qui est gelée, avec la ligne 6 du
chemin dans `docs/architecture.md` et les briefs du 17 novembre repris.

**Avant la session des cliquets**

1. Définir le cinquième cliquet par un relevé mécanique des constantes datées,
   avec une liste qui ne peut que raccourcir.

**Avant la session de l'âge légal**

2. Écrire que la table d'une version reste lue dans LEGI par le récupérateur,
   dans un fichier indexé par version, que la fiche désigne.
3. Écrire que les renvois se contrôlent à la fabrication, d'une fiche à
   l'autre, et qu'un renvoi nomme une valeur précise de la version lue.
4. Mettre les deux scripts de certification dans le périmètre de l'étape.
5. Couper l'étape en trois sessions, et faire de sa fin un point d'arrêt où le
   coût se mesure. Corriger au passage « la fin de `TableRecouverte` ».
6. Écrire d'abord le test de l'âge du taux plein sous les trois états du
   droit, et dire qu'une couche garde une réforme.

**Avant l'étape 3**

7. Étendre la recherche du premier départ aux portes de la carrière longue, et
   dire à quelle date se comptent les durées.

**Avant l'étape 4**

8. Écrire que l'étape déplace des résultats, séparer ses deux sortes de
   commits, corriger la ligne 6 du chemin, compter les 216 changements de
   renvoi et les ordonner par poids dans les résultats.

**Sans attendre**

9. Décider des corrections proposées le 17 novembre (Banque de France,
   Cavimac, artisans et commerçants d'avant 1973). Elles n'ont pas besoin
   d'attendre la restructuration.

**À chaque version reprise**

10. Demander une seconde lecture indépendante du texte pour les versions sans
    exemple officiel qui pèsent dans les résultats.

## Ce que je n'ai pas examiné

Ce verdict a cinq limites.

- **L'évaluation précédente.** Je ne l'ai pas lue, comme demandé. Le
  rectificatif du 16 novembre fait partie de la note, je l'ai donc lu : il
  rapporte un « avis extérieur ». Si c'est cette évaluation, trois de ses
  constats me sont parvenus par là.
- **Les régimes en points, la réversion et les régimes spéciaux.** La note dit
  ne pas les avoir essayés ; je ne l'ai pas fait non plus.
- **Le moteur sur la carrière longue.** L'écart du point 2 est établi sur la
  table du dépôt, pas sur le moteur.
- **Le droit d'avant 1985.** L'index de la DILA ne le porte pas.
- **Le coût en sessions.** Je donne des comptes, pas un devis.
