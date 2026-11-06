# Relecture de E6 : la CARMF lue au droit

File R-E7, le 6 novembre 2026 : relecture indépendante, contre les sources, du commit c19d9ca
de la session E6 (la CARMF lue au droit : `carmf_asv_minoration_enfants`,
`asv_medecins_ajustement` ; note `2026-11-06-carte-des-fiches-carmf-lue-au-droit.md`). Ni
règle, ni donnée, ni test n'est modifié.

**Méthode.** Les index de la DILA récupérés puis mis à jour (`dila_index.py --recuperer`,
`--mettre-a-jour` : JORF au 6 novembre 2026, dernier incrément 20261106-002608 ; LEGI au 5
novembre). La liste des textes, par requêtes directes sur la base de l'index, sans borne ni
limite : « médecins » au titre avec « statuts », « règlement », « vieillesse », « retraite »,
« prestations », « allocation » ou « CARMF » (213 titres, les autres professions ôtées) ;
« CARMF » ou « section professionnelle » au titre sans « médecins » ; « section professionnelle
des médecins » au corps (limite 500). Chaque arrêté de 2014 à 2026 fouillé, article par
article, aux mots « article 15 », « article 12 », « date d'effet », « trimestre civil »,
« jouissance », « cet âge », « 62 ans », « majoration », « enfants ». Chaque citation des deux
fiches, découpée à ses « [...] », guillemets ôtés et espaces ramenées, cherchée par un script
écrit pour cette relecture dans le texte de l'index qu'elle nomme (un mot altéré exprès y
échoue). LEGI lu par `dila_cherche.py --num` et `--le`, et les versions des décrets n° 72-968
et 2011-1644 relevées dans la base. Chaque cas de la note rejoué par `servi_et_refait`
(`tests/outils_pont.py` : le portage servi, le moteur Python refait au bit près), sur la
requête du formulaire, puis sous `PRESOMPTIONS_DECALEES=1` ; chaque montant refait au centime,
en décimal, à partir des montants servis non arrondis.

## Le verdict

**Conforme pour l'essentiel.** Les vingt-neuf citations et motifs sont exacts mot pour mot ;
les dates de publication et d'effet sont justes ; les versions sont fidèles au texte ; chaque
coefficient et chaque montant est celui des deux moteurs, présomptions décalées ou non, et
chaque calcul tombe juste au centime ; l'erreur de la date d'effet de 2026 est prouvée, et la
lecture contraire est intenable ; aucun texte modificatif n'est manqué. Un écart **moyen** :
un texte qui pèse sur le non-tranché de l'ASV d'avant 2017 n'est pas cité (point 5). Cinq
écarts **faibles** : le rectificatif du 8 août 2026 est bien dans l'index, et ne change rien
(point 3) ; l'âge légal de la génération 1964 n'est plus celui de D. 161-2-1-9 (point 4) ; la
lecture du modèle, de janvier à mars 2017, est la plus faible des deux (point 6) ; les
0,2482 point de l'ajustement mêlent deux écarts (point 7) ; l'arrêté du 7 janvier 2025 n'est
pas cité dans la fiche de l'ajustement (point 8).

## Point par point

1. **Les textes modificatifs : conforme.** La liste sans borne donne, de 2007 à 2026, les
   mêmes arrêtés que la note : 2007 (deux), 2008, 2009, 2010 (9 août ; 10 décembre, publié en
   2011), 2011, 2012 (l'invalidité-décès), 2014, 2016 (trois), 2017 (trois), 2018 (deux),
   2020, 2021, 2024 (deux), 2025, 2026 (10 juillet, son rectificatif, 21 septembre). Aucun
   arrêté sur la CARMF ne se titre sans « médecins ». Le décret n° 2026-239 (statuts-types des
   sections) n'a ni date d'effet, ni majoration. Aucun arrêté de 2017 à 2026 ne touche à la
   majoration des articles 15 et 12, ni aux enfants, ni à une date d'effet du médecin, hors
   ce que la fiche dit (2024 : « A compter du 1er janvier 2017 » supprimé, et l'inapte).
   L'article 3 du décret n° 2011-1644 n'a qu'une rédaction dans LEGI (LEGIARTI000024853554,
   depuis le 1er janvier 2012) ; l'article 2, quatre (2012, 30 décembre 2012, 5 septembre 2016,
   14 novembre 2025), comme la fiche.

2. **L'erreur de la date d'effet depuis le 18 juillet 2026 : conforme, la lecture contraire
   intenable.** L'article 24 du règlement est au titre V, « DISPOSITIONS COMMUNES AUX
   ALLOCATIONS DU MÉDECIN ET DU CONJOINT SURVIVANT » (JORFARTI000054435859) : il vaut pour le
   médecin. Ses deux branches tombent au premier jour d'un trimestre civil : « La date d'effet
   de l'allocation est fixée au premier jour du trimestre civil qui suit la réalisation de
   toutes les conditions d'ouverture des droits, sans pouvoir être antérieure à la date de la
   demande et à condition que le formulaire de demande de retraite délivré par la Caisse soit
   reçu dans les douze mois suivant la date d'effet. Si cette dernière condition n'est pas
   remplie, la date d'effet est fixée au premier jour du trimestre civil qui suit la réception
   par la CARMF du formulaire. » Aucune lecture n'y loge le premier du mois. La cessation est
   une condition (article 2, « 3° Cesser l'exercice de la médecine non salariée ») : parti à
   63 ans le 10 mai 2027, le médecin a sa pension le 1er juillet 2027, comme la note le dit.
   Les montants servis sont ceux de la note, dans les deux moteurs et sous la variable
   (14 056,14 ; 14 026,06 ; 15 850,88 ; 15 938,12) ; refaits : 14 056,14 / 12 = 1 171,35 ;
   2 × 14 026,06 / 12 = 2 337,68 ; 14 026,06 / 1,05 × 1,0625 = 14 193,04, 166,98 € par an ;
   à l'ASV, 1 320,91, 2 656,35, 16 127,86 et 189,74 €. Les trimestres : 4 des deux côtés
   (du 1er juillet 2026) dans le premier cas ; 5 au texte (du 1er avril 2026 au 1er juillet
   2027) et 4 au modèle dans le second. Le règlement de l'ASV (annexe III) ne date pas la
   pension du médecin : l'article 7 n'étend que les règles des conjoints, l'article 9 ne fixe
   que « l'entrée en jouissance » après une dette ; le non-tranché de l'ASV est fondé.

3. **Le rectificatif du 8 août 2026 : écart faible, sans effet.** La note et la fiche disent
   que l'index n'en a que le titre ; il a son article, JORFARTI000054642802 : « Dans l'annexe,
   au lieu de lire : « Article 6 « Chapitre 2 « Médecins en cumul activité/retraite « Le
   conseil d'administration détermine, chaque année, la valeur du point de retraite. », lire :
   « Article 6 « Le conseil d'administration détermine, chaque année, la valeur du point de
   retraite. « Chapitre 2 « Médecins en cumul activité/retraite » ». Il ne déplace qu'un
   intitulé de chapitre : ni l'âge, ni la majoration, ni l'article 24 ne changent. La question
   au propriétaire tombe ; la fiche peut le passer en `textes_sans_effet`.

4. **L'âge légal de la génération 1964 : écart faible, sans effet sur les montants.** La note
   et la fiche écrivent « parti à 63 ans (D. 161-2-1-9, 10°) ». Pour les pensions prenant effet
   depuis le 1er septembre 2026, L. 161-17-2, dans sa rédaction de la loi n° 2025-1403
   (LEGIARTI000053280889, « Conformément au VI de l'article 105 [...] s'appliquent aux pensions
   prenant effet à compter du 1 er septembre 2026 »), fixe « 3° Soixante-deux ans et neuf mois,
   pour les assurés nés entre le 1 er janvier 1963 et le 31 mars 1965 » ; D. 161-2-1-9, 10°
   (« Soixante-trois ans pour les assurés nés en 1964 », LEGIARTI000047634502) ne le dit plus.
   Les cas tiennent : 63 ans passe l'âge légal, la majoration court de 62 ans, et la cessation
   à 63 ans fait la date d'effet. La référence est à reprendre. Ce que le modèle sert d'âge
   légal à la génération 1964 n'est pas l'objet de cette relecture.

5. **L'ASV avant 2017 : écart moyen, un texte non cité.** Les chiffres sont justes (le modèle
   sert 15 533,26 € sans coefficient ; × 0,95 = 14 756,60 ; 776,66 € par an), et le point
   reste non tranché. Mais l'arrêté du 1er décembre 2016 montre des statuts de l'ASV d'avant
   2017 plus que les mots de 2011 (JORFARTI000033538061) : « 4° L'article 12 ter est abrogé ;
   5° L'article 15 est ainsi modifié : a. Au dernier alinéa, les mots : « au titre de l'article
   12 ter » sont remplacés par les mots : « avant le 1er janvier 2017 » ». À la complémentaire,
   l'arrêté du 30 novembre 2016 fait de même (JORFARTI000033521562) : « les mots : « demandé la
   liquidation de ses droits par anticipation au titre de l'article 15 » sont remplacés par
   les mots : « liquidé ses droits par anticipation avant le 1er janvier 2017 au titre de
   l'article 15 » ». L'ASV avait donc, avant 2017, un article 12 ter que sa réversion citait,
   vraisemblablement une liquidation par anticipation : la seconde lecture, un coefficient à
   l'ASV, en sort renforcée, sans que le texte en donne la valeur. À citer dans la fiche, et à
   nommer dans la question au propriétaire (l'article 12 ter des statuts de l'ASV).

6. **L'âge légal de janvier à mars 2017 : conforme aux chiffres, lecture du modèle faible.**
   1952 : 60 ans et 9 mois (D. 161-2-1-9, 3°, dans ses rédactions du 31 décembre 2011 et du 1er septembre 2023), le 10
   décembre 2012 ; du 1er janvier 2013 au 1er janvier 2017, 16 trimestres, 1,20 ; le modèle,
   11, 1,1375 (servi dans les deux moteurs : 12 364,01 et 15 894,81) ; refaits : 13 043,35 et
   16 768,15, soit 679,34 + 873,34 = 1 552,68 € par an. Mais la lecture qui sauve le modèle
   suppose que la date de la liquidation, non la date d'effet, choisisse la rédaction : la
   fiche elle-même choisit ses versions par `liquidation.date_effet`, et l'arrêté du 22 mars
   2017, sans date, n'entre en vigueur que le 30 mars, sans effet rétroactif écrit. « Ces
   coefficients sont déterminés définitivement lors de la liquidation des droits » dit qu'ils
   ne se revoient pas, non quelle rédaction les fixe. Le propriétaire peut le tenir pour une
   erreur probable ; le classement reste le sien.

7. **L'ajustement : conforme, un chiffre à préciser (faible).** 18 × 1 600 / 5 751 = 5,0078,
   5,01 ; 18 × 1 680 / 5 751 = 5,2582 ; le forfait de 5 751 € et la valeur de 11,82 € sont
   sourcés (`asv_conventionnes.yaml`, la CARMF au registre le 4 octobre 2026 ; décret
   n° 2011-1644, article 4, LEGIARTI000052567955). Mais 0,2482 = 5,2582 − 5,01 mêle les deux
   écarts déclarés, l'assiette et l'arrondi : l'assiette seule fait 18 × 80 / 5 751 = 0,2504
   point, 0,2504 × 11,82 = 2,96 €, et non 2,93 €. L'arrondi seul : au plus 0,06 €, juste.

8. **L'arrêté du 7 janvier 2025 : écart faible, à citer.** Lu par E6 (il est dans la liste des
   lectures de la fiche des âges), il n'est pas dans `asv_medecins_ajustement`, qu'il touche
   peut-être (JORFARTI000050962838, IV, statuts de l'ASV) : « 3° Au premier alinéa de
   l'article 8, les mots : « l'année » sont remplacés par les mots : « l'avant dernière année »
   ». Le contenu de l'article 8 n'est pas publié. S'il porte l'assiette de la cotisation
   d'ajustement, les statuts disaient « l'année » jusqu'à l'arrêté, et le décret « la deuxième
   année précédant » : le décret prime, et l'approximation déclarée demeure ; aucun chiffre ne
   change. Son 4° (« Au deuxième alinéa de l'article 15, le mot : « 60 » est remplacé par le
   mot : « soixante-deux » ») touche l'article de la réversion : sans effet.

9. **Les versions de 2017 et 2026 et le test : conformes.** Les arrêtés du 30 novembre (JO du
   4 décembre) et du 1er décembre 2016 (JO du 6) entrent en vigueur au 1er janvier 2017 ; celui
   du 22 mars 2017, publié le 29, le 30 ; le règlement du 10 juillet 2026, publié le 17, le 18 ;
   le décret n° 2026-418, le 1er juillet 2026 (article 30). Les trois cas du test refaits à la
   main : 8 × 1,25 % = 10 % (né en mars 1955, parti à 64 ans) ; 12 × 1,25 % = 15 % (né en mars
   1952, parti à 65 ans et un mois) ; 12 × 1,25 % + 20 × 0,75 % = 30 % (né en mars 1950,
   parti à 71 ans). Né le 10 mars 1949 parti à 64 ans, la complémentaire à 0,95 dans les deux
   moteurs.

10. **Les tests.** `tests/test_sections_sante.py` : 50 réussis, sous la variable aussi.
    `-m rapide` : 11 rouges, tous de `test_pages_en_dossier` (les faux rouges connus), sous la
    variable aussi ; un premier passage, lancé pendant la mise à jour de l'index LEGI, rougit
    24 cas de `test_marins.py`, verts relancés seuls (78), avec ou sans la variable.

## Ce que la relecture laisse

- **À la file E**, dans `carmf_asv_minoration_enfants` : passer le rectificatif du 8 août 2026
  en texte sans effet et ôter sa question ; reprendre la référence de l'âge légal de 1964
  (L. 161-17-2, 3°, et non D. 161-2-1-9, 10°) ; citer l'abrogation de l'article 12 ter des
  statuts de l'ASV et l'article 41 de la complémentaire. Dans `asv_medecins_ajustement` :
  dire que 0,2482 point mêle l'assiette et l'arrondi (l'assiette seule, 0,2504 point,
  2,96 €) ; citer l'arrêté du 7 janvier 2025 (IV, 3°).
- **Au propriétaire** : l'erreur de 2026 confirmée ; le non-tranché de janvier à mars 2017,
  dont la lecture du modèle est la plus faible ; l'article 12 ter de l'ASV, à demander avec
  les statuts d'avant 2017 au Bulletin officiel.
- **Candidat, hors de la tâche** : l'annexe de l'arrêté du 9 août 2010 (JORFARTI000022758875)
  a une première partie, les statuts du régime de base de la CARMF, que la fiche ne nomme pas :
  « L'entrée en jouissance de la pension de retraite est fixée au premier jour du trimestre
  civil qui suit la demande de l'intéressé » (article 7). Sans effet sur ces deux fiches (la
  partie de la complémentaire n'a aucune date d'effet du médecin) ; à confronter à la date
  d'effet que le modèle donne au régime de base des libéraux.
