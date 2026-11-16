# Essai de la note 0009 sur une fiche : l'âge du taux plein

*16 novembre 2026. Essai sur le papier, en lecture seule : rien n'a changé
dans le dépôt (lu à `origin/main`, e0feeb6). Il éprouve sur une seule fiche,
`age_annulation_decote`, les doutes levés le même jour contre la note 0009.
La fiche a été choisie parce que la loi la définit par un renvoi.*

## Ce que l'essai devait dire

1. Une version de fiche sait-elle porter un renvoi, « l'âge prévu à
   l'article L. 161-17-2 augmenté de cinq années » ?
2. Les deux axes, date d'effet et génération, y tiennent-ils ?
3. Que deviennent les renvois des fichiers de régime vers cette fiche ?
4. Quel code faudrait-il relier à la fiche ?
5. Quelles preuves a chaque version ?
6. Un résultat bougerait-il ?

## La fiche aujourd'hui

- Sans versions, `etat: conforme`. Elle lit une table par génération,
  `legislation/age_annulation_decote.csv` (65 ans jusqu'à la mi-1951,
  puis 65 ans et 4 mois… jusqu'à 67 ans dès 1955).
- La table dit elle-même qu'elle est une copie : « Aucun texte ne l'écrit
  génération par génération : ce que le code écrit est une RÈGLE » ; elle
  est « celle des âges d'ouverture, certifiée, décalée de cinq ans et
  plafonnée à 67 », et `verifier_donnees.py` la recalcule à chaque exécution.
- 47 régimes y renvoient, sur 469 périodes (`age_taux_plein_par_generation`).
- Code : `ageTauxPlein` (`moteur/js/droit/ouvrir.js`) et la classe
  `AgesAnnulationDecote` (`moteur/js/regimes.js`) ; côté Python,
  `droit/ouvrir.py` et `scenarios/actuel.py`.
- Trois exemples officiels : `sp_f19666_decote`, `sp_f21552_67_ans_158`,
  `cnav_2026_07_decote_1961`.

## Les versions, au format du dépôt (brouillon)

```yaml
lit:
- l'âge d'ouverture du droit de l'assuré, à sa génération, dans la version
  de `age_legal_par_generation` en vigueur à la date d'effet de sa pension
dates_qui_decident:
- liquidation.date_effet
versions:
- id: age_determine_fixe_par_decret
  textes:
  - {id: LEGIARTI000006742632, article: "L. 351-8, 1°", en_vigueur: 1985-12-21}
  - {id: LEGIARTI000006742633, article: "L. 351-8, 1°", en_vigueur: 2003-08-22}
  - {id: LEGIARTI000006749434, article: "R. 351-27", en_vigueur: 1985-12-21}
  - {id: LEGIARTI000006749435, article: "R. 351-27", en_vigueur: 1993-08-28}
  - {id: LEGIARTI000006749436, article: "R. 351-27", en_vigueur: 2004-02-15}
  - {id: LEGIARTI000020082993, article: "R. 351-27", en_vigueur: 2009-01-01}
  bornes:
    liquidation.date_effet: [1985-12-21, 2011-07-01]   # 1983-1985 : voir plus bas
  contenu:
    parametres: {age: 65}
    droit: >-
      « 1°) les assurés qui atteignent un âge déterminé ; » (L. 351-8, 1° inchangé
      en 2003), que R. 351-27 fixe : « l'âge prévu au 1° de l'article L. 351-8
      est fixé à soixante-cinq ans » (même phrase du 21 décembre 1985 au
      3 juin 2011, d'après la relecture R-L-bis du dépôt)
  exemples: aucun dans le dépôt ; à chercher
- id: age_legal_majore_de_cinq_ans
  textes:
  - {id: LEGIARTI000023030950, article: "L. 351-8, 1°", en_vigueur: 2011-07-01}
  - {id: LEGIARTI000028498855, article: "L. 351-8, 1°", en_vigueur: 2014-01-22}
  nee_de: >-
    loi n° 2010-1330, article 20 ; article 118, II : « Les dispositions de
    l'article 20 sont applicables aux pensions prenant effet à compter du
    1er juillet 2011. »
  bornes:
    liquidation.date_effet: [2011-07-01, 2023-09-01]
  contenu:
    parametres: {majoration_de_l_age_legal: 5}
    droit: >-
      « Les assurés qui atteignent l'âge prévu à l'article L. 161-17-2
      augmenté de cinq années »
  exemples: aucun dans le dépôt ; à chercher (circulaires Cnav de 2011)
- id: age_du_premier_alinea_majore_de_trois_ans
  textes:
  - {id: LEGIARTI000047452736, article: "L. 351-8, 1°", en_vigueur: 2023-09-01}
  - {id: LEGIARTI000051289852, article: "L. 351-8, 1° inchangé", en_vigueur: 2025-02-28}
  bornes:
    liquidation.date_effet: [2023-09-01, null]
  contenu:
    parametres: {majoration_de_l_age_du_premier_alinea: 3}
    droit: >-
      « l'âge prévu au premier alinéa de l'article L. 161-17-2 augmenté de
      trois années » : 64 + 3, soit 67 ans pour toutes les générations
  exemples: [sp_f19666_decote, sp_f21552_67_ans_158, cnav_2026_07_decote_1961]
```

## Ce que l'essai montre

**1. Le renvoi entre dans le format.** Le dépôt le fait déjà pour les IEG :
la fiche `age_reference_decote_ieg` a une version « l'âge minimum
d'ouverture du droit […] majoré de cinq ans », puis une autre « de trois
ans » depuis 2025, par son champ `lit` et un paramètre. L'âge du taux plein
s'écrit de même. La table recopiée disparaît : une copie de moins. Ce qui
était faux, c'est la règle de la note 0009, « chaque version porte sa table
entière » : une version porte ce que dit son texte, une table, une valeur ou
un renvoi avec son paramètre.

**2. Les deux axes tiennent.** La version se choisit à la date d'effet ; la
génération entre par l'âge légal, lu dans sa propre version à la même date.
Pour le droit applicable, la table par génération seule donne déjà les bons
âges : aucun assuré né après la mi-1951 ne pouvait atteindre 65 ans avant
juillet 2011. La différence ne se voit que dans un scénario qui changerait
l'âge légal entre 2011 et 2023 : l'âge du taux plein le suivrait, comme le
veut la loi.

**3. Les renvois des régimes sont du droit, pas des doublons.** 23 des 47
régimes ont d'abord des périodes sans renvoi, à une valeur à eux, et
commencent à renvoyer à des dates qui leur sont propres (recompté le
16 novembre ; quatre autres renvoient dès leur début et ont plus tard des
périodes sans renvoi) : 1983 pour le régime général, la
MSA des salariés, l'Organic et la Cancava ; 2004 pour la CNAVPL et la CNBF ;
2011 pour l'Agirc-Arrco, l'Ircantec et la MSA des non-salariés. C'est la date
où le droit de chaque régime se met à renvoyer à la règle commune. Elle
appartient au régime, pas à la fiche. D'autres gardent leur propre droit :
55 ans à la Banque de France jusqu'en 2007, 60 ans dans la fonction publique
jusqu'en 2003. L'annexe B avait donc raison de garder les renvois, et la
note 0009 tort de les supprimer. Ce qui reste à corriger dans les fichiers
de régime : des dates à l'année, au lieu du jour du texte ; des renvois sans
texte cité ; et 469 valeurs de repli que le moteur ne lit que si la table ne
répond pas. Pour les huit régimes qui basculent en 2011, l'année où la règle
commune change, reste à lire si leur droit a vraiment changé alors, ou si
leur fichier recopie la fiche. (L'essai sur l'âge légal nuance ce point :
certaines dates de bascule sont des coupures de fichier, pas du droit ; voir
`essais-0009.md`.)

**4. Le code se relie, mais pas « une fonction, une fiche ».** `ageTauxPlein`
applique cinq règles : l'âge gardé par qui a ouvert son droit avant une
réforme, les dérogations des emplois classés, les tables propres à un
régime, la règle commune (cette fiche) bornée par l'âge du parent de trois
enfants, et la valeur de la période. Relier chaque fonction à sa fiche ne
marche pas ici : il faut relier chaque branche, ou découper la fonction. Le
minimum avec le parent de trois enfants est une relation entre deux fiches,
que C.2 sait déclarer (`sorte` : plafond, exception). La fonction devra aussi
recevoir la date d'effet, pour choisir la version.

**5. La preuve est inégale.** Les trois exemples officiels valent pour la
troisième version. Les deux premières n'en ont aucun dans le dépôt.

**6. Aucun résultat ne devrait bouger,** ni pour le droit applicable, ni pour
les deux droits contrefactuels du site, qui donnent tous 67 ans dès la
génération 1955. Le Python nomme encore cette fiche, mais plus aucun test
n'exécute de règle Python, hors les deux fichiers de la façade (action 161,
au 16 novembre) : l'étape de code vérifiera qu'elle n'a que le JavaScript à
toucher.

## Ce que les textes ont appris

*Lus sur Légifrance le 16 novembre, à la demande du propriétaire : l'index
LEGI du dépôt ne se télécharge pas depuis cet environnement (release privée),
et l'accès direct à Légifrance y est bloqué ; un lecteur web a lu les pages
datées des articles.*

- **Les trois versions sont des renvois ; aucune n'est une table.** La
  première renvoie de la loi au décret : L. 351-8 dit « un âge déterminé »,
  et c'est R. 351-27 qui le fixe à soixante-cinq ans. La deuxième renvoie à
  l'âge de L. 161-17-2, augmenté de cinq ans ; la troisième à l'âge de son
  premier alinéa, augmenté de trois. La table par génération du dépôt n'est
  écrite dans aucun texte.
- **Les bornes se lisent dans la disposition d'application, pas dans les
  dates de LEGI.** R. 351-27 perd ses soixante-cinq ans le 3 juin 2011
  (décret n° 2011-620), L. 351-8 change le 1er juillet, et l'article 118, II,
  de la loi fixe le 1er juillet 2011 pour les pensions. L'écart de juin est
  sans effet parce qu'une pension prend effet le premier jour d'un mois : la
  version doit le dire.
- **Un trou dans le partage, que la table cachait.** Le régime général
  renvoie à la fiche dès 1983, mais l'index du dépôt n'a aucun texte avant le
  21 décembre 1985 : l'ancien code n'y est pas. Pour les pensions de 1983 à
  1985, il faut lire l'ordonnance de 1982 et l'ancien code, ou écrire une
  version `supposée`. Le dépôt le savait déjà pour l'ASV des directeurs de
  laboratoire.
- **L'exception des parents de trois enfants** vient de l'article 20, III,
  de la même loi, que R. 351-27 cite depuis 2011. La fiche
  `taux_plein_a_soixante_cinq_ans` la porte déjà en versions, lues à la date
  d'effet ; le lien entre les deux fiches reste un minimum dans le code.

## Ce qui reste ouvert

- La version de 1983 à 1985 : l'article 9 de l'ordonnance n° 82-270
  (LEGIARTI000006275868, lu le 16 novembre) la fait entrer en vigueur le
  1er avril 1983, et dès le 1er juillet 1982 pour deux publics : certains
  assurés de 63 ans justifiant de 150 trimestres, et les demandeurs d'emploi
  de 60 ans inscrits au 1er février 1982, avec 40 trimestres. Son article 1er,
  qui définit le taux plein, n'est pas sur Légifrance : il se lit au Journal
  officiel. La disposition d'application du décret n° 2011-620 n'importe pas
  (voir plus haut « Les bornes se lisent dans la disposition d'application » :
  aucune pension ne prend effet entre le 3 juin et le 1er juillet 2011).
- Les huit régimes qui basculent en 2011 : leur valeur propre, 65 ans, est
  celle de la règle commune jusqu'aux nés de juillet 1951, qui ont 65 ans en
  juillet 2016 ; leur date ne change aucun résultat, qu'elle soit du droit ou
  une copie (relu le 16 novembre, voir la note 0009).
- La question ouverte de `ages_regimes.csv` pour les générations 1958 à 1961
  de certains régimes d'outre-mer : « augmenté de cinq ans » de leur propre
  âge, ou 64 + 3 ? Elle relève de ces régimes, pas de cette fiche.

## Ce que l'essai change à la note 0009

- **Tient :** les deux axes ; le droit daté d'une règle commune dans les
  versions de sa fiche ; la fin des tables recopiées.
- **Tombe :** la table entière dans chaque version (une version porte ce que
  dit son texte) ; la fin des renvois des régimes (ils sont le droit de
  chaque régime) ; « chaque fonction nomme sa fiche » (c'est la branche, ou
  la relation).
- **Ce travail est celui de l'action 191**, qui convertit déjà les fiches
  domaine par domaine (la retraite progressive est faite). L'essai en est
  une étape possible, dans le domaine des âges.

## L'étape de code, si elle est décidée

Une session neuve, sur Fable 5.2 puisqu'elle écrit une règle du scénario 1,
comme une étape de l'action 191 : retrouver dans l'index LEGI les textes lus
ici sur Légifrance ; trancher la version de 1983 à 1985, par l'ordonnance de
1982 et l'ancien code, ou en la marquant `supposée` ; écrire d'abord les
tests (les trois versions, à quelques générations et dates tirées des textes
et des exemples) ; faire lire les versions au moteur ; retirer la table
recopiée ; témoins identiques ; une étape, poussée sur `main` selon les
règles du dépôt.

Les essais suivants (`essais-0009.md`) proposent de commencer par l'âge
légal, que cette fiche lit dans sa version à la date d'effet.
