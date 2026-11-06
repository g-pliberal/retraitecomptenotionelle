# Les corrections de la relecture R-E7 : la CARMF lue au droit, redite

**La demande.** Le 6 novembre 2026, la session d'orchestration confie à la file E (tâche
E6-bis) les écarts que la relecture R-E7 (`130/2026-11-06-relecture-r-e7.md`, commit dcdb75f)
a trouvés dans le travail de E6 (`130/2026-11-06-carte-des-fiches-carmf-lue-au-droit.md`,
commit c19d9ca) : une fiche à compléter d'un texte non cité, cinq écarts faibles. R-E7 juge
E6 conforme pour l'essentiel. Chaque texte est relu ici, dans l'index de la DILA (JORF à
jour du 3 novembre 2026, LEGI du 2 novembre), non repris de la relecture. Aucune règle du
modèle ne change. La note de E6 est un récit et reste telle quelle : ses valeurs corrigées
sont ici, et un renvoi daté la clôt.

## Ce qui est fait

- **Le test d'abord** (`tests/test_sections_sante.py`), cinq tests neufs, vus rouges de leur
  raison (la fiche ne cite pas le texte, ne dit pas 2,96 €) avant toute retouche d'une
  fiche, puis verts : `test_la_fiche_de_la_carmf_cite_l_article_12_ter_de_l_asv`,
  `test_le_rectificatif_du_8_aout_2026_est_lu_et_sans_effet`,
  `test_l_age_legal_des_nes_en_1964_est_celui_de_l_161_17_2` (qui joue aussi le modèle
  dans les deux moteurs), `test_l_ajustement_de_l_avant_derniere_annee_se_chiffre_a_la_main`,
  `test_la_fiche_de_l_ajustement_cite_l_arrete_du_7_janvier_2025`. Les phrases attendues y sont
  copiées de l'index, non de la fiche.
- **Les citations vérifiées par un script** : chaque phrase écrite dans les fiches, guillemets
  ôtés et espaces ramenées, se retrouve dans le texte de l'index qu'elle nomme (onze phrases) ;
  une phrase altérée exprès (« article 16 » pour « article 15 ») y échoue.
- Les fiches `carmf_asv_minoration_enfants` et `asv_medecins_ajustement` changent, ainsi que
  le paquet (`moteur/donnees.json`, règle 4).

## Point 1 (moyen) : l'article 12 ter des statuts de l'ASV

R-E7 écrivait que l'arrêté du 1er décembre 2016 abroge l'article 12 ter. La lecture va un
peu plus loin : l'arrêté du 28 septembre 2011, que la fiche citait déjà, nomme ce même
article, et c'est la phrase que la fiche coupait.

- **Arrêté du 28 septembre 2011, annexe** (JORFARTI000024612007), statuts de l'ASV :
  « Article 12 A l'article 12, les mots : « ou de 60 ans » sont remplacés par les mots : « ou
  de l'âge prévu à l'article L. 161-17-2 du code de la sécurité sociale ». Article 12 ter Au
  premier alinéa de l'article 12 ter, les mots : « dès l'âge de 60 ans » sont remplacés par
  les mots : « dès l'âge prévu à l'article L. 161-17-2 du code de la sécurité sociale » ».
  À la complémentaire, le même arrêté récrit les deux mêmes membres de phrase, à l'article
  15 : « 1. Au premier alinéa du 1, les mots : « ou de 60 ans » [...] 2. Au cinquième alinéa
  du 1, les mots : « dès l'âge de 60 ans » ».
- **Arrêté du 1er décembre 2016, annexe** (JORFARTI000033538061), statuts de l'ASV : « 4°
  L'article 12 ter est abrogé ; 5° L'article 15 est ainsi modifié : a. Au dernier alinéa, les
  mots : « au titre de l'article 12 ter » sont remplacés par les mots : « avant le 1er
  janvier 2017 » ; b. Après le dernier alinéa, il est inséré un nouvel alinéa ainsi rédigé :
  « Lorsque le coefficient de majoration dont a bénéficié le médecin ayant liquidé ses droits
  à partir du 1er janvier 2017 en vertu du deuxième alinéa du 1° de l'article 12 est
  inférieur à 15 %, ce coefficient est porté à 15 % pour le calcul de la pension de
  réversion. » ». L'article 15 est celui de la réversion : l'article 15 bis dit « Le taux de
  réversion est identique à celui retenu à l'article 15 pour le conjoint survivant ».
- **Arrêté du 30 novembre 2016, annexe** (JORFARTI000033521562), statuts de la
  complémentaire : « 4° L'article 41 est ainsi modifié : a) Au deuxième alinéa, les mots :
  « demandé la liquidation de ses droits par anticipation au titre de l'article 15 » sont
  remplacés par les mots : « liquidé ses droits par anticipation avant le 1er janvier 2017 au
  titre de l'article 15 » ». Les deux arrêtés de 2016 entrent en vigueur le 1er janvier 2017
  (leur article 2 : « Le présent arrêté entre en vigueur au 1er janvier 2017 ») ; celui de
  2011, publié le 30 septembre, sans date écrite, le lendemain.

Cités dans la fiche, à leur place : la version d'avant 2017 (la phrase de 2011, qui ne s'arrête
plus à l'article 12), la version de 2017 (les deux textes de 2016, au 4° et au 5°, a ; l'article
41), l'approximation d'avant 2017, la liste « à relire ».

**Ce que le texte change au point non tranché, et de quel côté il penche.** Le texte n'a plus
seulement « l'article 12 de l'ASV, récrit des mêmes mots que l'article 15 » : il montre à l'ASV
un second article, le 12 ter, dont le premier alinéa porte « dès l'âge de 60 ans », les mots mêmes
que le cinquième alinéa du 1 de l'article 15 de la complémentaire. Et la réversion de l'ASV
singularise les droits liquidés « au titre de l'article 12 ter » comme celle de la
complémentaire singularise ceux liquidés « par anticipation au titre de l'article 15 ». Le
texte penche donc vers la seconde lecture (un coefficient à l'ASV), pour deux raisons : l'ASV
avait un article à elle pour une liquidation dès 60 ans, que sa réversion visait ; la seule
décote du régime de base, la lecture du modèle, expliquerait mal un tel article. **Il ne la
prouve pas, et la lecture du modèle n'est pas intenable** : le texte de l'article 12 ter et celui
du dernier alinéa de l'article 15 ne sont nulle part dans l'index (la recherche de la phrase «
article 12 ter » dans l'index JORF ne retrouve, pour la CARMF, que ces deux arrêtés) ; « dès l'âge
de 60 ans » dit un âge, non un coefficient ; rien ne dit si l'article 12 ter visait tout médecin
ou une catégorie (l'article 12 de 2017 donne à l'inapte et à l'ancien combattant un coefficient
de 13 %) ; et rien ne donne la valeur du coefficient, ni qu'elle soit celle de la
complémentaire. Le calcul des deux lectures, posé par E6 et relu par R-E7, ne bouge pas : 0 €
si le modèle a raison ; 776,66 € par an de moins si l'ASV porte le 0,95 à 64 ans (né le 10
mars 1949, parti à 64 ans le 1er avril 2013 ; 15 533,26 × 0,95 = 14 756,60 ; 15 533,26 −
14 756,60 = 776,66). **Au propriétaire** : la question 22 des statuts d'avant 2017 (Bulletin
officiel ou CARMF) vise aussi l'article 12 ter de l'ASV et le dernier alinéa de son article 15.

## Point 2 (faible) : le rectificatif du 8 août 2026

JORFARTI000054642802, publié le 8 août 2026 : « Rectificatif au Journal officiel n° 165 du 17
juillet 2026, texte n° 11 : Dans l'annexe, au lieu de lire : « Article 6 « Chapitre 2 « Médecins
en cumul activité/retraite « Le conseil d'administration détermine, chaque année, la valeur du
point de retraite. », lire : « Article 6 « Le conseil d'administration détermine, chaque année,
la valeur du point de retraite. « Chapitre 2 « Médecins en cumul activité/retraite » ». Il ne
déplace qu'un intitulé de chapitre, l'article 6 (la valeur du point) gardant son texte : ni
l'âge, ni la majoration, ni l'article 24 ne changent. E6 se trompait de dire que l'index n'en
a que le titre. La fiche le passe en `textes_sans_effet`, ôte « n'est pas lu » de l'erreur de
2026 et le rectificatif de ses « à relire » ; la question au propriétaire tombe.

## Point 3 (faible) : l'âge légal des nés en 1964

L. 161-17-2 du code de la sécurité sociale, dans la rédaction de la loi n° 2025-1403 du 30
décembre 2025 (LEGIARTI000053280889, en vigueur le 31 décembre 2025) : « Conformément au VI de
l'article 105 de la loi n° 2025-1403 du 30 décembre 2025, ces dispositions, dans leur
rédaction résultant de l'article précité, s'appliquent aux pensions prenant effet à compter du
1 er septembre 2026. » ; « Cet âge est fixé à : [...] 3° Soixante-deux ans et neuf mois, pour
les assurés nés entre le 1 er janvier 1963 et le 31 mars 1965 ». La pension des cas posés prend
effet le 1er juillet 2027, après le 1er septembre 2026 : cette rédaction vaut, la dernière que
l'index porte (au 2 novembre 2026 ; un texte plus récent n'y serait pas). D. 161-2-1-9, 10°,
dans sa rédaction du 1er septembre 2023 (LEGIARTI000047634502) disait « Soixante-trois ans
pour les assurés nés en 1964 » ; ce n'est plus l'âge des pensions d'après le 1er septembre 2026.
E6 écrivait « parti à 63 ans (D. 161-2-1-9, 10°) ». La fiche cite L. 161-17-2 ; son ancienne
lecture de D. 161-2-1-9 garde la ligne de 1952 (3°), qui tient pour 2017.

**Vérifié : sans effet sur les montants.** À la main, né le 10 mai 1964 : 62 ans le 10 mai 2026,
le trimestre civil suivant commence le 1er juillet 2026 ; 62 ans et 9 mois le 10 février 2027 ;
la cessation à 63 ans (10 mai 2027) est la dernière condition, la pension prend effet le 1er
juillet 2027 (article 24) ; 4 trimestres (du 1er juillet 2026 au 1er juillet 2027), 1,05. Né le
10 mars 1964 : 62 ans le 10 mars 2026, trimestre civil suivant le 1er avril 2026 ; 62 ans et 9
mois le 10 décembre 2026 ; cessation à 63 ans et un mois (10 avril 2027), pension au 1er juillet
2027 ; 5 trimestres, 1,0625. Que l'âge légal soit de 63 ans (10 mars 2027) ou de 62 ans et 9 mois
(10 décembre 2026), il est dépassé avant la cessation : ni la date d'effet ni les trimestres ne
changent. Joués dans les deux moteurs (`servi_et_refait`, la requête du formulaire), les quatre
montants de la note de E6 sont retrouvés : 14 056,14 € et 15 850,88 € (premier cas), 14 026,06 €
et 15 938,12 € (second). Le modèle n'attend pas 63 ans : il ouvre les nés en 1964 à 62,75 ans
(`liquidation_ouverte` vrai, `motif_ouverture` « age_legal »), non à 62,5 ans ; le test le tient.

## Point 4 (faible) : la lecture du modèle, de janvier à mars 2017, est la plus faible

Les chiffres de E6 tiennent (né le 10 mars 1952 : 60 ans et 9 mois le 10 décembre 2012,
D. 161-2-1-9, 3°, « Soixante ans et neuf mois pour les assurés nés en 1952 », rédaction du 31
décembre 2011 en vigueur au 1er janvier 2017 ; 16 trimestres du 1er janvier 2013 au 1er janvier
2017, 20 %, 1,20 ; le modèle, 11 trimestres, 1,1375 ; 679,34 + 873,34 = 1 552,68 € par an).
Mais la lecture du modèle suppose que la date de la **liquidation**, non celle de l'**effet**,
choisisse la rédaction des statuts. La fiche choisit ses versions par `liquidation.date_effet`
(`dates_qui_decident`) ; l'arrêté du 22 mars 2017 (JORFARTI000034298518 à 521, publié le 29
mars) ne dit aucune date : l'article 1er approuve les modifications, l'article 2 charge le
directeur de la sécurité sociale de l'exécuter, et rien n'y écrit un effet rétroactif ; il
entre en vigueur le lendemain de sa publication, le 30 mars 2017. Et « Ces coefficients sont
déterminés définitivement lors de la liquidation des droits » dit que les coefficients ne se
revoient pas, non quelle rédaction les fixe. La lecture du modèle reste possible (une
liquidation faite après le 29 mars pour une pension du 1er janvier) : le point reste non
tranché. La fiche le dit.

## Point 5 (faible) : l'ajustement de l'ASV, 0,2504 point et 2,96 €

Exercice 2026, taux de 4 % (décret n° 2011-1644, article 2, rédaction du décret n° 2025-1076
: « 4 % à compter de l'exercice 2026 »), forfait total 3 × 1 917 = 5 751 € (`asv_conventionnes.yaml`,
la CARMF au registre le 4 octobre 2026), valeur de service 11,82 € (article 4, II, 3° : « 3°
S'agissant des points liquidés à compter du 1er janvier 2017 : [...] 11,82 euros à compter de
l'exercice 2025 », relu dans LEGIARTI000052567955). Revenu de 40 000 € en 2024 (le décret :
« la deuxième année précédant ») et de 42 000 € en 2026 (le modèle : l'exercice même).

- Le décret : 18 × (4 % × 40 000) / 5 751 = 18 × 1 600 / 5 751 = 28 800 / 5 751 = 5,0078 points,
  5,01 arrondis au centième (article 3).
- Le modèle : 18 × (4 % × 42 000) / 5 751 = 18 × 1 680 / 5 751 = 30 240 / 5 751 = 5,2582 points.
- **L'assiette seule** : 5,2582 − 5,0078 = 18 × 80 / 5 751 = 1 440 / 5 751 = **0,2504 point** ;
  0,2504 × 11,82 = 2,9597, **2,96 €** de pension annuelle par exercice.
- Les 0,2482 de E6 : 5,2582 − 5,01 = 0,2482, soit 0,2504 − 0,0022 ; ce 0,0022 est l'arrondi du
  décret (5,01 − 5,0078 = 0,0022), que la deuxième approximation compte à part. 0,2482 × 11,82
  = 2,93 € : le 2,93 mêlait les deux. L'arrondi seul : 0,0022 × 11,82 = 0,03 € dans ce cas ; au
  plus 0,005 × 11,82 = 0,06 €, comme E6 le disait.

La fiche écrit 0,2504 et 2,96 €, et le 0,0022 de l'arrondi.

## Point 6 (faible) : l'arrêté du 7 janvier 2025

JORFARTI000050962838 (publié le 10 janvier 2025 ; l'article 2 charge de l'exécution et de la
publication, sans date : en vigueur le 11 janvier), annexe, IV, « les statuts du régime des
prestations complémentaires de vieillesse de la caisse autonome de retraite des médecins de
France » (l'ASV) : « 3° Au premier alinéa de l'article 8, les mots : « l'année » sont remplacés
par les mots : « l'avant dernière année » ; 4° Au deuxième alinéa de l'article 15, le mot : «
60 » est remplacé par le mot : « soixante-deux » ». Le contenu de l'article 8 n'est pas publié.
S'il porte l'assiette de la cotisation d'ajustement, les statuts disaient « l'année » jusqu'à
l'arrêté, « l'avant dernière année » depuis ; le décret dit « la deuxième année précédant »
depuis 2012 et prime sur les statuts : l'approximation de l'assiette demeure, aucun chiffre
ne change. Le 4° touche l'article 15 des statuts de l'ASV (la réversion), non l'ajustement.
La fiche de l'ajustement le cite, dans l'approximation de l'assiette et dans ses lectures.

## Ce que la tâche laisse

- **Au propriétaire** : l'article 12 ter de l'ASV s'ajoute à la question 22 (point 1). Les erreurs
  et non-tranchés de E6 restent ceux de son compte rendu : la date d'effet au trimestre civil
  (erreur de la CARMF, comme la CAVOM, la CARPIMKO et la CAVP), l'âge légal de janvier à mars 2017
  (le plus faible des deux, point 4), l'ASV d'avant 2017 (le texte penche, point 1), la date
  d'effet avant 2026 et celle de l'ASV.
- **Le bloc « Reprise » de l'action 130** n'est pas récrit : aucun chiffre qu'il porte ne change
  (il ne porte ni 2,93 ni 0,2482).
- **Candidat, hors de la tâche** : l'arrêté du 30 novembre 2016 (JORFARTI000033521562) ajoute, à
  l'article 27 des statuts de la complémentaire (2°), « Pour les retraites liquidées avant le 1er
  janvier 2017, le nombre de points est affecté d'un coefficient compensant l'évolution de la
  valeur du point entre 2016 et 2017 », et à l'article 31 (3°), celui du médecin qui bénéficie
  de l'allocation d'invalidité, « Le nombre de points calculé lors de la liquidation de la
  retraite est affecté du coefficient suivant : « 1,13 s'il est né en 1953 ; « 1,11 s'il est né
  en 1954 ; « 1,09 s'il est né à partir du 1er janvier 1955 ». Aucune fiche ni aucun code du
  dépôt ne les porte (recherche des mots de l'article 27 dans `data`, `docs`, `tests`, `src` :
  rien) ; E6 et R-E7 ne les nomment pas. Ils touchent les pensions liquidées avant 2017 et les
  médecins invalides : à lire et à classer par la file E.

*Cette note corrige, sans la récrire, celle de E6 ; un renvoi daté la clôt.*
