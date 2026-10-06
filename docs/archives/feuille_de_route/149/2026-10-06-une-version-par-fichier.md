# Action 149 : une version de l'architecture par fichier

**Le 6 octobre 2026 : chaque version de l'architecture a son fichier, sans
numéro, et l'en-tête du document n'en nomme plus aucune.**

- *La mesure.* 62 commits de `main` touchent `docs/architecture.md`, du
  25 septembre au 6 octobre ; 34 touchent sa liste « Les versions » ou sa
  ligne d'en-tête, et tous pour y ajouter une version (de 5.1 à 5.37, le
  premier en posant quatre). Chaque couple de ces commits successifs est
  rejoué comme s'il avait été mené en parallèle depuis la même base : la
  seconde modification reportée sur l'état d'avant la première, puis les deux
  fusionnées (`git merge-file`, à l'histogramme, comme les fusions de git).
  Les 33 couples entrent en conflit : chaque version s'ajoute au même point,
  en tête de la liste, et 22 couples récrivent aussi tous deux l'en-tête ;
  tous auraient pris le même numéro. L'étape 3 de l'action 148 en comptait
  20 sur 34, sans garder sa méthode : reportée sur la base de la première,
  une seconde version ajoutée en tête bute toujours. L'historique ne montre
  aucune course : aucun de ces commits n'a été écrit avant que le précédent
  soit publié (date d'auteur contre date de commit ; un rebasage, lui, ne
  laisse pas de trace), et les versions se suivent, depuis le 1er octobre, à
  1,6 à 67 heures d'intervalle. Ce que le changement évite est un conflit à
  venir, maintenant que les sessions vont en parallèle, plus qu'un conflit
  déjà payé : l'avis réservé de la demande tenait pour le passé.
- *Ce que le rangement évite.* Rejoués de même, la liste hors du document et
  l'en-tête sans numéro : 19 des 33 conflits disparaissent ; les 14 autres
  tiennent au corps du document, que deux étapes successives d'un même
  domaine récrivent au même endroit : le tableau du périmètre (§ 2), dont
  chaque étape récrit la ligne de son domaine, dans 8 couples ; le chemin des
  domaines (§ 11) dans 4 ; l'annexe B dans un ; et le premier couple, qui
  crée le fichier. De la prose écrite à la main, hors de l'action. Depuis le
  1er octobre, 5 sur 6. Sur les 61
  couples successifs de tous les commits du fichier, 30 conflits avant, 16
  après. La liste seule rangée, l'en-tête gardant son numéro, en laisserait
  24 sur 33 : l'en-tête en porte dix à lui seul.
- *Le choix.* Un fichier par version,
  `docs/architecture/versions/<AAAA-MM-JJ>-<sujet>.md`, qui s'ouvre sur
  « # Version du <date> : <sujet> » ; sans numéro ; et l'en-tête du document
  n'en nomme aucune, renvoyant au dossier. Une version se cite par sa date et
  son sujet, que deux sessions ne prennent pas ensemble ; le tri des noms
  donne l'ordre. Des numéros que personne n'attribue à la main ne se donnent
  sans doublon qu'à l'arrivée sur `main`, dans l'ordre des envois — par
  `pousser.sh` au rebasage, ou par GitHub après : la session ne connaîtrait
  pas le sien en écrivant sa note, ou le verrait changer sous elle. Un rang
  tiré du tri des noms changerait dès qu'une version datée de la veille
  arriverait après une version du jour : un numéro publié bougerait. L'en-tête
  en chiffre ancré, que le pilote « ancres » règle seul, n'aurait réglé que
  le conflit de l'en-tête, pas le doublon du numéro, et une ancre tient une
  quantité, quand 5.4 précède 5.37. Le § 13.3 refusait déjà ce compteur à la
  carte : « Aucun compteur n'est partagé ».
- *Les premières restent où elles sont.* Les versions 5.1 à 5.37 gardent leur
  numéro et leur place, en bas du document, telles qu'elles ont été écrites,
  comme les notes d'avant l'action 148 restent dans la feuille de route : rien
  ne bouge, rien ne peut se perdre, et la quinzaine de renvois de la feuille
  de route et des notes (« l'architecture passe en version 5.34 ») trouve son
  entrée où elle a toujours été. Les ranger un fichier chacune aurait coupé
  deux paragraphes gelés qui en portent plusieurs (5.14 et 5.15 ; 5.5 à 5.1).
  Un paragraphe neuf, en tête de leur liste, dit où vont les suivantes.
- *Ce qui change.* `docs/architecture.md` : l'en-tête, le § 9.3 (la règle),
  le § 13.3 (« Ce document porte un numéro de version » devient faux), une
  ligne de l'annexe B, et ce paragraphe en tête de « Les versions » ; la
  première version rangée, `2026-10-06-une-version-par-fichier.md`.
  `scripts/conservation.py` gèle le dossier dès qu'un fichier y naît
  (`VERSIONS`, dans `TOUT_GELES` avec les décisions et les archives), sans
  déclaration dans `zones.yaml`, que chaque version récrirait au même
  endroit ; `zones.yaml` le dit en commentaire. `CLAUDE.md`, « La
  documentation, au plus court ». Aucun script ni test ne lisait la liste ou
  l'en-tête (`grep -rn "Les versions\|Version 5\."`), sinon le contrôle de
  la prose et la conservation, par la déclaration de `zones.yaml`, qui ne
  change pas.
- *La preuve.* `test_les_versions_de_l_architecture_se_rangent_une_par_fichier`
  (`test_prose.py`) : le nom de chaque fichier, son titre et la date qu'il
  porte, aucun numéro, un en-tête qui ne nomme aucune version, une liste
  numérotée qui va de 5.1 à 5.37 et pas au-delà. Cinq mutations jouées contre
  lui — l'en-tête numéroté, une 5.38 dans la liste, un nom en majuscule, un
  titre numéroté, la date d'un titre fausse — sont toutes refusées.
  `test_une_version_de_l_architecture_est_gelee_des_son_fichier_ecrit`
  (`test_conservation.py`), sur un dépôt miniature : la version est gelée
  sans déclaration, une note ne l'est pas. `conservation.py --depuis HEAD`
  ne voit que cinq paragraphes changés, tous d'état, et c'est voulu :
  l'en-tête, le § 9.3, le § 13.3, le tableau de l'annexe B et le paragraphe
  de `CLAUDE.md` qui porte la règle. La référence refigée gèle la première
  version.
- *Hors de l'action.* Les 14 conflits qui restent sur le corps du document,
  de la prose écrite à la main, dont le tableau du périmètre (§ 2), où
  chaque étape récrit la ligne de son domaine, porte plus de la moitié.

- *L'action close.* Elle tient en cette étape, et passe, telle quelle, à la
  fin de l'archive, ce dossier avec elle, au commit qui suit celui de
  l'étape. `conservation.py --depuis HEAD` n'y voit que deux paragraphes
  changés, et c'est voulu : son titre, dont l'état passe à `fait`, et son
  bloc « Reprise », retiré comme aux clôtures des actions 141 et 148 ; une
  ligne « Ce que ça a déplacé » s'y ajoute. La référence refigée gèle ses
  paragraphes et ceux de cette note.
