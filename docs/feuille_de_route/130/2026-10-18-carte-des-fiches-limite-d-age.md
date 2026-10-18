# La carte des fiches : les quinze fiches de la limite d'âge, mûries

Session 130 de la vague du 18 octobre 2026, sans le propriétaire. Un des restes
de l'action qui ne dépendent pas de lui : « Faire mûrir la carte »
(`docs/etat.md`, § 3), où 832 champs obligatoires manquaient à 126 fiches. Le
lot pris est celui des quinze fiches que lit `droit/limite_age.py`
(`limite_age.FICHES`), loin des domaines des autres sessions de la vague :
l'action 151, qui les a fait naître, est au repos, ce qui lui reste revenant au
propriétaire ou à des textes illisibles d'ici. Il ne leur manquait que leur
`code`, aux quinze, et leurs `approximations`, aux onze approchées. Aucun
fichier du modèle, des pages ni des témoins ne bouge ; le paquet du site, qui ne
garde des fiches que leurs versions (`versions.preparer`), non plus.

## Ce qui est fait

- **Le test d'abord**, le dernier de `tests/test_limite_age.py` : les quinze
  fiches ne manquent d'aucun champ que le contrat C.2 exige ; chaque
  approximation touche des versions que sa fiche porte ; le code de chacune
  nomme, dans chaque moteur, des fonctions qui sont dans les fichiers qu'il
  nomme (« fichier : fonction, Classe.méthode ; … »), les paramètres que ses
  versions portent, tous et rien d'autre, et des tests qui existent. Vu rouge
  sur les quinze, vert après.
- **Le code des quinze** : les fonctions de `droit/limite_age.py` et de son
  jumeau `moteur/js/droit/limite_age.js` qui lisent chaque fiche — la limite
  (`_limite`, `limiteDe`, et leurs morceaux), les exceptions qu'une version
  ouvre, les reculs pour enfants, les deux prolongations et le maintien, le
  plafond de 2023, la prorogation du statut de la Banque de France, les
  services de l'agent des IEG avant 2008 —, et, pour les fiches de limite, le
  chemin par lequel la radiation devient la date de la pension : `FichesDatees`,
  `departs_et_demandes`, `ScenarioActuel.calculer` et `Echeancier.parcourir`,
  dans les deux moteurs ; les paramètres de leurs versions ; les tests de la
  limite d'âge, ses témoins de simulation et leur rejeu en JavaScript
  (`tests/js/moteur.test.js`).
- **Les approximations des onze approchées**, transcrites de ce que chacune
  disait déjà dans son effet (« Approchée : … »), ses présomptions et les
  hypothèses de ses versions supposées, chacune rattachée aux versions qu'elle
  touche : le corps du fonctionnaire et le grade du militaire, que la saisie ne
  porte pas ; l'enfant invalide, handicapé ou mort pour la France ; la durée
  comptée sans les bonifications, et l'intérêt du service présumé ; la
  disposition d'avant 2010 du décret n° 48-1907, non lue ; la durée d'assurance
  du contractuel, comptée par les années cotisées, et la limite de chaque
  administration avant 2011, présumée la plus haute ; les limites que les
  régimes spéciaux et les ouvriers de l'État opposaient avant les textes lus,
  de 1962 à 2012 selon le régime, non lues ou supposées ; les catégories que la
  saisie ne distingue pas. Une seule a un effet mesuré, celle
  du décret de 1948 — de 4 à 24 % de la pension des actifs nés de 1925 à 1945
  partis à 64 ans —, que l'effet de la fiche de la limite écrivait déjà ; les
  autres sont « non mesuré », comme les fiches le disaient.

La carte passe de 126 fiches à mûrir à 111, et de 832 manques à 806 : `code`
manque à 61 fiches au lieu de 76, `approximations` à 29 au lieu de 40. Le
tableau de bord se refait sur GitHub.

L'inscription des rédactions du LEGI parues depuis le 15 octobre, que la vague
demandait aussi, était déjà faite au matin du 18 : 122 rédactions inscrites ce
jour-là, sur l'index à jour de l'incrément du 17 octobre au soir
(`data/reference/textes/inscription.yaml`). L'étape ne l'a pas refaite.

## Ce que l'étape laisse

- Le champ `code` n'est contrôlé que pour ces quinze fiches. Le même test,
  étendu à toutes celles qui en ont un, tiendrait la carte à jour quand une
  fonction est renommée ou retirée, ce que fait l'action 161 : sur la tête de
  `main`, les seuls chemins de fichiers Python et JavaScript qui ne se
  retrouvent pas tels quels sont ceux de deux fiches qui les abrègent (`pension_proratisee`,
  `totalisation_des_periodes_etrangeres` : « moteur/js/droit/etranger.js,
  compter.js… ») ; les noms de fonctions des autres fiches ne sont pas vérifiés.
  À faire après la vague, puisque la session 161 retire des fonctions.
- `code` n'est pas parmi les champs documentaires de `memoire.py`
  (`CHAMPS_DOCUMENTAIRES`) : aucun calcul ne le lit, mais l'écrire change
  l'empreinte de la fiche et refait sa mémoire. Une retouche du code, hors de
  cette étape.
- Restent à mûrir 111 fiches : les 107 que la phase 2 a tirées du registre de
  veille, à qui manquent leurs versions, leur domaine, leurs régimes, ce
  qu'elles lisent et écrivent et leurs dates qui décident, et qui demandent la
  lecture du droit (`docs/veille_droit.md`) ; et quatre presque mûres :
  `asv_autres_professions_de_sante` (code et approximations, née de
  l'action 138), `cultes_retraite_complementaire_taux_specifiques` (code et
  versions), `minimum_pension_ieg` (code, d'une règle `manquante`) et
  `rafp_majoration_capital` (étape).
- Les points ouverts des phases 2 à 8 restent tels que la feuille de route les
  dit, sous « Ce qui reste ouvert » de chaque phase. Relevés pour cette étape,
  ceux qui ne dépendent pas du propriétaire : le journal de veille encore dans
  `veille.yaml`, sans liste des situations des fiches service-public et des
  circulaires (phase 2) ; les présomptions qu'une simulation emploie, que le
  site ne montre pas (phase 3) ; le relevé, que le site ne montre pas (phase 4) ;
  les événements de l'échéancier qui attendent encore leurs domaines
  (phase 5) ; les paramètres des périodes, encore dans les fichiers de
  régimes (phase 6) ; trois fiches qui mêlent la cotisation et le droit,
  `restitution.py` sans fiche (phase 7) ; les libellés de la saisie encore en
  Python, la liste des systèmes montrés dans le texte du site (phase 8). Celui
  de la phase 6, « Une fiche dit la valeur qu'elle pose, pas encore sa
  fonction », avance avec cette étape : quinze fiches nomment désormais la
  leur.

## Ce qui attend le propriétaire

Rien de neuf : la décision de la proposition du sixième domaine, et celle sur
la retraite progressive, le cumul et la seconde pension, README muet.
