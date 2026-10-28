# Étape 3, vingt-cinquième partie : la phrase des poids de la page Coût, chaque caisse divisée par les têtes de ses cas types

**La demande.** Vague du 28 octobre 2026, une session par tâche qui se mène
sans le propriétaire, celle-ci seule sur les pages : le dernier point du site
du bloc de l'étape, « la phrase des poids », le point 3 de « Ce qui reste » de
la note du poids du militaire (24 octobre). La phrase seule : la table des
poids et sa phrase du partage, que l'inapte et l'ex-invalide démentent,
restent au propriétaire (bloc de la note « naissances et migrations dans les
pages »), comme l'officier. Aucune règle du scénario 1 n'est en cause : ni
veille du droit, ni entrée au journal.

**La phrase.** Le dépliant « Ce que chaque carrière type pèse dans ces
chiffres » (`coutDetailPoids`) disait, au-dessus de la table : « dans les
dépenses, un cas type pèse les retraités de sa caisse (combien ont eu cette
carrière-là), publiés par la DREES, puis calés d'un même coefficient chaque
année… ». Depuis le 24 octobre, chaque caisse se divise par les têtes que la
pyramide donne à ses cas types (`castypes.poids_effectifs`), et la colonne
« Retraités en 2024 » montre des parts de départs. Ce n'est pas la phrase du
partage, sous la table (« Une caisse réclamée par plusieurs cas types se
partage également entre eux »), que la session n'a pas touchée. Elle dit
désormais : « Celle du cas type est sociologique. Dans les dépenses, il pèse sa
part des départs : les retraités de sa caisse, publiés par la DREES, divisés
par les têtes que la pyramide donne aux cas types de la caisse, puis calés d'un
même coefficient chaque année pour que chaque groupe de régimes pèse dans la
masse la part que le COR donne à sa dépense en 2025. Dans les recettes, il pèse
ses cotisants, publiés et projetés par le COR. » Elle perd « et elle se lit des
deux côtés du bilan », que ses deux phrases disent, et la glose « combien ont
eu cette carrière-là » : Coût tout déplié comptait 33 243 mots pour un budget
de 33 250 (`BUDGETS_DEPLIES`), il en compte 33 244.

**Le test** (`test_web.py`) :
`test_la_page_cout_dit_que_chaque_caisse_se_divise_par_les_tetes_de_ses_cas_types`,
vu rouge pour la raison attendue — le modèle refuse de peser des retraités
sans les têtes de leurs cas types (`cout._ponderation`), la page ne le disait
pas —, puis vert ; il refuse aussi l'ancienne formule.

**Ce que ça déplace.** Les cinq rendus de Coût de `tests/temoins/pages.json`
(`cout`, `cout_cascade_horizon`, `cout_cascade_hors_liste`,
`cout_flux_horizon`, `cout_solde_vise`) et `cout/index.html`, de cette phrase
seule ; ni le paquet, ni un témoin de simulation, ni le catalogue des
affirmations, sa phrase en gras, « Deux pondérations se composent. », restant
la même.

**Trouvé en chemin.**

- *La phrase du bord*, sous la table : « Hors de la fenêtre que la DREES
  publie (2004 à 2024), la répartition du bord est reconduite ». Au-delà de
  2024, les caisses de la fonction publique et celles qui se ferment suivent
  la croissance que le COR donne à leurs retraités
  (`EffectifsRetraites.CAISSES_PROJETEES`, action 147, étapes 9 et 13). Un
  texte de la table, au propriétaire avec elle.
- *Les fabriqués de `main` sont périmés* par les commits du modèle et des
  données de la vague : le paquet (`test_le_paquet_est_a_jour`) et les témoins
  de simulation, dont 19 sur 909 bougent, de −0,01 à +0,04 %. Tombent aussi,
  sans cette retouche comme avec, sept confrontations du portage au Python dans
  `-m rapide` (`test_pont.py`, `test_coupures_au_mois.py`, `test_simulateur.py`,
  `test_cycle_de_vie_script.py`) et la date de vérification que promet la page
  Méthode et sources (`test_web_revues.py`) ; avec, le portage sur des
  carrières tirées au hasard (`test_web.py`), que rien de cette retouche ne
  lit. GitHub refait les fabriqués avant la suite complète ; la session n'a
  commité que les rendus de pages qu'elle déplace.

**Ce qui reste**, de cette partie ; le reste de l'étape est dans son bloc.

1. *Au propriétaire, avec la table des poids* : son en-tête « Retraités en
   2024 », qui porte des parts de départs, que la phrase dit désormais ; sa
   phrase du partage ; la phrase du bord, ci-dessus.
