# Étape 5 : la page dit la limite d'âge et l'exception présumée

**Le 16 octobre 2026 : quand le départ saisi passe la limite d'âge de l'emploi, la
note des départs du simulateur dit la limite, chaque recul de droit, chaque
exception présumée demandée et accordée, l'âge où l'emploi prend fin, dans les
mots de son statut, et que ce qui suit peut se déclarer comme un métier de plus.**

## Ce que fait la page

- **`limiteDAgePassee`** (`moteur/js/pages.js`) lit `radiation(moteur, carriere)`
  (`droit/limite_age.js`) sur la carrière saisie, dès qu'un départ porte le motif
  `limite_d_age` et que la radiation est forcée. Elle écrit, dans la note des
  départs, après leur liste : « La limite d'âge de votre emploi est de 67 ans. » ;
  les reculs de droit (« La loi la recule de droit : le recul d'un an du parent de
  trois enfants, à 68 ans. ») ; les exceptions présumées, à la suite, chacune à
  l'âge où elle mène (« Nous présumons que vous avez demandé et obtenu la
  prolongation pour carrière incomplète jusqu'à 59 ans et 6 mois, puis la
  prolongation de l'actif jusqu'à la limite des sédentaires, 67 ans, autant que
  votre départ le demande. ») ; puis la fin de l'emploi selon la fiche
  (`FIN_A_LA_LIMITE`) : « la loi vous radie des cadres à 70 ans » pour le
  fonctionnaire et le militaire, « votre contrat prend fin à 70 ans » pour le
  contractuel, « vous êtes mis à la retraite à 67 ans » pour l'ouvrier de l'État,
  l'agent de la SNCF et de la RATP. Le militaire lit que sa limite est la plus
  haute de sa catégorie, son grade n'étant pas saisi.
- **Le titre d'un départ unique** à la limite : « Votre pension ne commence pas à
  votre départ. Votre emploi a une limite d'âge, et votre départ la passe. »
- **Les motifs** se disent sans « cadres », que le contractuel n'a pas :
  `POURQUOI_CE_DEPART`, « à la limite d'âge de votre emploi » ;
  `POURQUOI_PAS_A_CETTE_DATE`, « votre emploi prend fin à sa limite d'âge, et sa
  pension part de ce jour ».
- **Contrôlé** : `test_la_page_dit_la_limite_d_age_et_ses_exceptions_presumees`
  (`tests/test_web_saisie.py`), le fonctionnaire parent de trois enfants, le
  policier, l'officier, le contractuel, le cheminot né en 1960, et le départ
  avant la limite, muet ; deux témoins de page neufs,
  `simuler_limite_d_age_policier` et `simuler_limite_d_age_contractuel`. Aucune
  autre page ne change de ce fait ; aucune phrase en gras neuve.

## Un constat

Le paquet `moteur/donnees.json` de `main` (sources c7d2af5) ne portait pas encore
les trois fiches de l'étape 4 : le site ne radiait ni le contractuel, ni l'ouvrier,
ni le cheminot avant régénération. GitHub le refait à l'envoi ; les témoins de
simulation de l'étape 4 attendaient de même.

## Ce qui reste

- Au modèle et au propriétaire, ce que le bloc « Reprise » de l'action dit.
- La page ne dit pas encore la limite d'un départ qui la frôle sans la passer, ni
  la radiation dans les comptes notionnels, que le propriétaire n'a pas décidée.
