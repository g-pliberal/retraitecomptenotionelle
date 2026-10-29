# Étape 9, suite de la huitième partie : la limite 5 ante ter (2), à jour de l'étape

**La demande.** Vague du 28 octobre 2026 : une session par tâche, que le
propriétaire ne suit pas pas à pas ; une autre session de la vague tient les
pages de l'étape. Le point « la limite 5 ante ter (2), en fin d'étape » du bloc
« Reprise » de la huitième partie : écrire, dans
`docs/limites/5-ante-ter-net-et-brut.md`, ce que l'étape a fait et ce qu'elle
laisse, à jour des notes du 25 au 29 octobre, en reprenant les approximations
de la fiche `maintien_affiliation_crpcen_ieg`, comme le suggérait la note
« retour à la CRPCEN et aux IEG ». L'étape n'est pas close : le plafond de
2027, les dates de pension d'un retour au site et les points au propriétaire
restent ouverts, et la limite les dit tels quels, sans les trancher.

**Ce que disent les textes.** Rien de neuf à lire : la limite reprend ce que
les notes de l'étape ont lu du 13 au 29 octobre, et les fiches et les
commentaires des données qui le portent (`prelevements_remuneration.yaml`,
`maladie_des_pensions.py`, `affiliations.yaml`).

**Ce qui est fait.**

- *La réserve 2*, récrite. Elle disait non lus les régimes spéciaux, la
  fonction publique et les indépendants. Elle dit désormais les trois
  cotisations qui courent encore — 1 % des complémentaires de salariés,
  0,70 % de la pension de la SNCF sous un plafond que le dépôt calcule faute
  de valeur publiée, 0,50 % de celle des mines —, ce qu'elles épargnent et la
  tranche de CSG qu'elles suivent ; les régimes dont la maladie n'est pas lue ;
  l'histoire des prélèvements, ses séries, ses quatre conventions et ce que
  les textes ne disent pas ; ce qui reste hors du calcul, la CAMIEG et le
  non-résident ; le régime d'une pension selon l'entrée dans le statut, avec
  les quatre approximations de la fiche ; les quatre points au propriétaire.
- *« Et un mot sur la saisie »* : chaque ligne remonte par la fiche de sa
  dernière année, avec les deux approximations de `Saisie.retours` (note du
  29 octobre).
- *La prose* : régime `etat` (`zones.yaml`), sans exception à déclarer, aucun
  paragraphe n'y racontant. Chaque chiffre est ancré : sur
  `prelevements_remuneration.yaml` (les taux, le plafond et son année), sur
  `affiliations.yaml` (les dix ans du maintien, en lettres), et, pour les
  5 128 € de 2010, sur `test_le_plafond_de_la_sncf_est_celui_du_texte_revalorise`.
  Quand la ligne de la SNCF passera à 2027, le plafond et son année suivront
  d'eux-mêmes (`verifier_prose.py --corriger`). Le contrôle ne relève rien
  dans la partie ; `conservation.py` ne perd rien de la référence, et
  `--depuis HEAD` ne nomme que les deux paragraphes d'état récrits.

**Trouvé en chemin.**

- *La majoration pour trois enfants de la réversion du régime général paie
  encore, au non-résident, la cotisation de la base* (note « réversion de la
  SNCF » du 18 octobre, « Trouvé en chemin »). Le point est tombé des listes
  après la note du 18 octobre sur le minimum de la réversion, sans note qui le
  dise fait, et il ne l'est pas : `reverse` (`pages.js`, vers la ligne 6410)
  n'ôte de l'assiette que la majoration du défunt (`ligne.majoration`, nulle
  au régime général), quand la ligne du régime général porte la sienne dans
  son montant (`majoration_trois_enfants`, `reversion.js`, vers la ligne
  2030) ; aucun test ne tient le cas. La limite le dit, et le bloc « Reprise »
  le rend aux restes : à une session des pages, avec son test.
- *La fiche `cotisation_maladie_pensions_complementaires`* dit encore, dans sa
  troisième approximation et ses relectures, non lus les taux des
  non-résidents et ce que les régimes spéciaux et la fonction publique
  prélèvent : vrai le 4 octobre, plus depuis le 16. Avec les fiches de
  l'étape, à sa fin.

**Ce que montrent les mesures.** Rien ne bouge : la session n'écrit que de la
prose. En local, six tests échouent, dont aucun ne tient à la partie : trois
de parité des deux moteurs, au RAFP (`test_pont.py`, `test_coupures_au_mois.py`,
la surcote parentale de `test_simulateur.py`), et trois de péremption
(`test_prose.py` : des chiffres ancrés du README et de quatre autres documents,
le tableau de bord, le chiffrage du PLF). Ils lisent les fichiers fabriqués du
clone, que GitHub refait à chaque envoi et qu'aucun de ses commits n'a refaits
depuis la suite rouge du 28 octobre (`7c7a055`) ; la course 1111 était verte
sur `75942d8`.

**Ce qui reste**, une session par point : le plafond de 2027, à la
revalorisation du 1er janvier (note du 28 octobre) ; au site, les dates de
pension d'un retour, que la session des pages pousse ce jour (`ca623ed`, sa
note à venir), et la majoration de la réversion du régime général au
non-résident (« Trouvé en chemin ») ; les fiches de l'étape, à sa fin. Au
propriétaire, sans changement : la CAMIEG, l'écrêtement du minimum de la SNCF,
l'ASPA de l'article 23, les textes au fac-similé. La session qui règle l'un de
ces points récrit sa phrase de la limite.
