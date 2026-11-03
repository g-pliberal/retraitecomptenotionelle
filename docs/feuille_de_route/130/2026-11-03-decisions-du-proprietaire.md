# Les 17 décisions du propriétaire du 3 novembre 2026, et les neuf questions qui attendent sa réponse

File D, vague 6, le 3 novembre 2026 (tête de `main` : 208ac7c, 19 h 42 UTC). Cette
note écrit en un seul lieu les 17 décisions que le propriétaire a prises le
3 novembre 2026, avec l'avis qu'il a approuvé, cité mot pour mot, et ce qui en est
fait. Elle ne change ni règle, ni donnée, ni test, et ne touche pas au bloc
« Reprise » de l'action 130, que la file E seule récrit.

**Ce qui existait.** Aucun registre des décisions du propriétaire. `docs/decisions/`
(0001 à 0006) range des notes d'architecture. Çà et là, une note consigne une
décision à elle seule (`docs/archives/feuille_de_route/150/2026-10-10-decision.md`),
et la feuille de route écrit, par action, « Ce que le propriétaire a tranché ».
Des 17 décisions du 3 novembre, quelques-unes ont une trace éparse, par exemple la 2
(action 185) et la 4 (Mayotte) ; le bloc « Reprise » de l'action 130 en résume l'état
(0f75705, file E). L'orchestration de la vague 5 a relevé, à 19:47:39 : « Vos 17
décisions du 3 novembre ne sont écrites nulle part dans le dépôt. »

**D'où vient le texte.** Ni le message du propriétaire ni les avis ne sont dans le
dépôt : ils sont dans le fil de deux sessions d'orchestration, lu par
`list_events` (outil claude-code-remote). Vague 4 : `session_01FVFLAj3amicrSTwzStJQ8q`
(identifiant interne du fil : `3384e3a4-fd10-5398-8ca1-fe880672068f`). Vague 5 :
`session_01FVFLAjkV9R1z73xEZ5tQ6b`. Les citations sont celles des événements, mot
pour mot ; seuls les gras du message d'origine sont retirés. Les heures sont le
champ `created_at` de l'événement, en UTC. Les identifiants des événements sont
en fin de note, pour qu'on les rouvre. Chaque empreinte de commit a été vérifiée
par `git log -1` sur `origin/main`, et chaque verdict de relecture relu dans la
note de relecture elle-même, non dans le compte rendu qui l'annonçait.

**Ce que cette note n'a pas relu.** Le texte des 15 premiers avis est celui du
résumé de 06:05:50, « Tes 15 questions, avec mon avis ». Les comptes rendus de la
nuit où chaque question est née, avant 06:05, ne sont pas relus ici.

## La réponse du propriétaire

Au fil de la vague 4, le 3 novembre 2026 :

1. **09:20:30**, le propriétaire écrit (l'événement porte `client_platform:
   android`) : « Je veux que tu lances dans de nouvelles sessions
   la prochaine série de travail / Cependant, fait extrêmement attention. Il ne faut
   aucune erreur. La crédibilité du parti est en jeu. Il faut toujours vérifier avec
   un document source à la clé et ne jamais faire confiance à ta propre mémoire. Il
   faudra que l'on puisse justifier avec preuve à l'écrit tout notre système quand
   on nous le demandera plus tard » (le saut de ligne du message d'origine est
   marqué ici par la barre oblique).
2. **09:21:16**, l'orchestration répond : « Avant de lancer quoi que ce soit, j'ai
   besoin d'une seule précision : tu ne m'as pas encore répondu sur les 17
   questions, et une bonne partie de la suite en dépend. »
3. **09:21:20**, elle pose la question (`AskUserQuestion`, intitulée « 17
   questions ») : « Pour la prochaine série de travail, est-ce que j'applique mes
   avis sur les 17 questions en attente (par exemple corriger la pension des
   officiers de marine, la complémentaire des artisans, les cultes, l'Agirc-Arrco, et
   faire la durée des échelons des fonctionnaires) ? » Trois réponses sont offertes :
   « Oui, applique tes avis (Recommandé) », « Seulement les vérifications »,
   « Question par question ».
4. **09:22:35**, le propriétaire répond : « Oui, applique tes avis (Recommandé) ».
   L'événement porte `permission_decision` : `accept`, source `user_temporary`.

**Ce que cette réponse couvre.**

- Un seul « oui » pour les 17 avis, non une réponse par question. Les avis qu'il
  approuve sont ceux que l'orchestration lui avait écrits : les 15 premiers à
  06:05:50, le 16e à 06:18:01, le 17e à 07:03:11, repris à 08:25:31.
- La réponse choisie disait, dans sa description : « Je lance les corrections
  approuvées. Chacune cite son texte officiel (article, version, date, lien) relu
  pendant la session, jamais de mémoire, et chacune est relue ensuite par une
  seconde session indépendante qui revérifie la source. Ce qui attend (questions
  3, 11, 12) reste en attente. » Les décisions 3, 11 et 12 sont donc des décisions
  d'attendre.
- L'heure : les notes d'état de l'orchestration datent la demande de « 09 h 25
  UTC ». L'événement porte 09:20:30 ; 09:25:16 est l'heure du premier lancement de
  session qui a suivi. Cette note garde l'heure de l'événement.

## Les 17 décisions

Pour chacune : l'avis approuvé, cité ; où elle en est. « Relue » dit ce que la note de
relecture écrit de son verdict.

### 1. Les officiers de marine (R. 11, 3°)

- **Avis** (06:05:50) : « Corriger la pension des officiers de marine d'après la loi ? Oui »
- **Où elle en est : faite, mais le chiffre annoncé n'existait pas.** La file M1 a écrit
  l'abattement de R. 11, 3° (e5dd612 ; `130/2026-11-03-abattement-des-marins.md`).
  Elle a lu que « l'indice 100 » est l'indice brut 100 (décret n° 85-1148, art. 7), non
  l'indice majoré que la nuit avait supposé sans source. L'orchestration le rend à
  10:35:58 : « L'erreur annoncée cette nuit n'existait pas, et aucun chiffre du
  modèle ne change. » La nuit avait annoncé une pension surestimée « de 2 à 19 % ».
- **Une limite, relevée par la relecture** (R-M1, 11:32:33) : pour 1985 à 2007, « aucun
  marin n'a atteint le plafond » n'est « pas prouvé, seulement très probable », car les
  salaires d'avant 2008 sont estimés trop bas (−14,5 % en 1995, d'après un montant
  réel). Déclarée par M1-bis (8cf8615), bornée au premier semestre de 1995 par M1-ter
  (a66e323), le choix de 1994 déclaré par M1-quater (aa6721d).
- **Relue** : R-M1 (4dc0195, 5957549), point décisif « conforme » ; R-M1-bis (aa35999),
  citations « conformes mot pour mot », cinq écarts, repris par M1-ter ; R-M1-ter
  (265b237), « conforme sur l'essentiel ».
- **Reste** : les questions 2 et 3 ci-dessous.

### 2. L'action 145 close, l'action 185 ouverte

- **Avis** (06:05:50) : « Fermer l'action 145 et ouvrir une action pour les petits écarts d'octobre ? Oui »
- **Où elle en est : faite.** c0e5036 : l'action 145 est close, aux archives avec ses
  notes (16:32:44 : « aucun texte ne s'est perdu dans le rangement »). L'action 185
  (`docs/feuille_de_route.md`, « Les écarts que l'action 145 a lus sans les calculer »,
  `à faire`) inscrit 24 écarts tels que leur note les dit, avec la trace du barème de
  la CRFM, « dont la part attend l'arrêté de 1977 ». Aucun n'est tranché : chacun se
  relit à sa source avant d'être corrigé.

### 3. Le départ anticipé des régimes spéciaux, daté au premier mois permis

- **Avis** (06:05:50) : « Régimes spéciaux : compter un départ anticipé à partir du premier mois permis ? Oui, plus tard »
- **Où elle en est : à faire, plus tard.** Une des trois décisions que la réponse du
  09:22:35 laisse « en attente ». Aucun commit ni aucune session n'y est rattaché
  dans ce que cette note a relu.

### 4. Mayotte en 2026

- **Avis** (06:05:50) : « Mayotte 2026 : suivre la caisse (250 €) plutôt que le décret (150 €) ? Non »
- **Où elle en est : faite, notée.** Le modèle garde le décret, 150 €. La note
  `177/2026-11-03-etape-9-assiette-du-rco-ecrite.md` (4209a8a) l'écrit : « Une
  autre décision du propriétaire, le 3 novembre 2026 », et garde les 250 € du barème
  de la caisse comme écart déclaré (`ECARTS_COTISATIONS_VALIDANTES_MAYOTTE`, fiche
  `mayotte_pension_de_base`). Rien d'autre à faire.

### 5. La durée de chaque échelon des fonctionnaires, avant le reste

- **Avis** (06:05:50) : « Fonctionnaires : faire d'abord la durée de chaque échelon ? Oui. Quatre sessions l'ont demandé. »
- **Où elle en est : faite.** B2 (04cbe34) : 14 345 durées, chacune avec sa référence
  d'article. B2-bis (fa24baa à 260182e) : 777 tableaux, 14 506 lignes. B2-ter (ddde684
  à 54983bd) : le tableau du décret n° 83-1260, art. 34, rétabli, la coquille du LEGI
  (1980 pour 1990) prouvée par le JORF.
- **Relue** : R-B2 (b121b49), 32 lignes sur 32 conformes pour la valeur, avec un écart
  moyen ; R-B2-bis (3dd70c4), 32 sur 32 ; R-B2-ter (a5557f9), six points « conformes ».
- **Reste** : 97 versions de tableaux, dans 54 articles, que le lecteur ne reconnaît
  pas : comptées et listées, non lues (question 9) ; relier les durées aux grilles de
  salaire, suite de la file B. Aucun chiffre de pension ne bouge : ces durées ne
  servent pas encore au calcul.

### 6. L'index de la DILA, élargi pour deux articles agricoles

- **Avis** (06:05:50) : « Élargir la copie des textes de loi pour lire deux articles agricoles ? Oui »
- **Où elle en est : faite, sauf D. 732-76.** File B : 0a64139 (le filtre de l'index garde
  les durées d'échelon et D. 732-76/77), ed8f3fa (la note de l'index élargi et
  reconstruit). File K : 7621be3 et 5835f0d, la majoration des points de chef de 1952
  à 1972 aux pensions de juillet 1986 à 2025 ; les trois exemples types gagnent 47 €,
  48 € et 106 € par an. K-bis (ddb8824, a7f4519) reprend cinq écarts faibles, de
  rédaction ou de déclaration, sans calcul qui change.
- **Relue** : R-K (babeae2), « conforme », cinq écarts faibles ; R-K-bis (2654317),
  « conforme », deux écarts faibles.
- **Reste** : D. 732-76 (question 5) ; la cotisation de 1952, une demi-année que le
  modèle prélève en entier, que le compte rendu de K-bis (15:33:40) dit non corrigée,
  à traiter à part.

### 7. Le RCO des artisans

- **Avis** (06:05:50) : « Corriger le calcul de la complémentaire des artisans de 1979 à 2008 ? Oui »
- **Où elle en est : faite.** M2 (f716130, f63fec0, 93906ff, 1aa23ce, 4209a8a, 5cda81f) :
  le RCO des artisans de 1979 à 2008 et le NRCO des commerçants de 2004 à 2008 se
  calculent sur le revenu de l'avant-dernière année ; les deux premières années de
  l'artisan au forfait ; la cotisation de 0,10 % de 1985 à 1996 sans points. Effet :
  de −0,1 à −2,3 % (11:29:51). M2-bis (cc55cdd, 06e2e9a) : le conjoint collaborateur à
  l'option, de 2007 à 2012, un exemple type à −0,19 %. M2-ter (15b4b1f).
- **Relue** : R-M2 (c79277d), règle « conforme », quatre écarts mineurs ; R-M2-bis
  (b5cbc57), « conforme », trois écarts faibles de documentation, repris par M2-ter.
  La relecture a aussi établi que les marges élargies du test du COR (9 % et 12 %)
  sont « justifiées » : tout le déplacement vient de la correction (12:10:45).

### 8. Les pensions de 2023 et 2024 de la page Coût

- **Avis** (06:05:50) : « Ajouter les pensions de 2023 et 2024 à la page Coût ? Oui »
- **Où elle en est : faite.** File A : 0521e59, 127aa4a, a78366a ; le test réparé,
  bf1c50b ; trois retouches, c35ffe7. La page affiche 6,9 % au lieu de 6,8 % (19:47:39).
- **Relue** : R-A (214c777), « conforme sur tous les points décisifs », deux écarts faibles.

### 9. L'Ircantec, deux erreurs d'avant 1983

- **Avis** (06:05:50) : « Ircantec : corriger deux erreurs d'avant 1983 ? Oui, sans urgence »
- **Où elle en est : à faire.** File M3, après l'Agirc-Arrco, sans urgence. Les commits
  du 3 novembre sur l'Ircantec (9d3e2de, 72f40e7) la lisent au droit ; aucun ne la
  corrige. Le bloc « Reprise » de l'action 130 la dit : « Décidée, l'Ircantec d'avant
  1983 viendra par la file M3. » Voir la question 1.

### 10. Les années outre-mer, repliées dans les options

- **Avis** (06:05:50) : « Garder le champ « Années outre-mer » replié dans les options ? Oui »
- **Où elle en est : on garde, rien à faire.**

### 11. La grille du coût

- **Avis** (06:05:50) : « Corriger tout de suite le calcul du coût, sans attendre la nouvelle population ? Non, attendre »
- **Où elle en est : en attente**, de la population de l'étape 14 de l'action 138 (file I).
  Y attendent les trois erreurs du coût que la note `178/2026-11-03-etape-5-regles.md`
  dit rester : « le recours à la garantie compté en têtes, la complétude de la grille au
  lieu de la proratisation, les nouveaux retraités de 2024 à 28 % de trop ». Une des
  trois décisions que la réponse du 09:22:35 laisse « en attente ».

### 12. Les artisans, en attendant une source

- **Avis** (06:05:50) : « Attendre une source sur les anciens artisans avant de toucher aux départs des hommes ? Oui »
- **Où elle en est : en attente** d'une source sur leur carrière. L'état de
  l'orchestration (vague 4) la dit « à inscrire par I », la file I de l'action 138.
  Une des trois décisions « en attente ».

### 13. La base de cotisation des cultes

- **Avis** (06:05:50) : « Cultes : corriger la base de cotisation des ministres du culte ? Oui, sans urgence »
- **Où elle en est : faite.** M5 (2af6a11, e4d9994, cd8db07) : la base suit le SMIC de
  chaque mois, dans les deux moteurs ; les 21 relèvements du SMIC lus au Journal
  officiel. Quinze pensions types montent, de 0,11 € à 4,08 € par mois (16:59:40).
  M5-bis (3954dfe) : six retouches, sans calcul qui change.
- **Relue** : R-M5 (5b33e12), « conforme sur chaque point décisif », six écarts faibles.
- **Reste** : la garantie de rémunération de 2002 au 30 juin 2005 n'est pas codée
  (question 7).

### 14. Le taux plein à 65 ans des parents de trois enfants

- **Avis** (06:05:50) : « Calculer le taux plein à 65 ans des parents de trois enfants nés de 1951 à 1955 ? Oui »
- **Où elle en est : faite au régime général, aux salariés agricoles, aux artisans et
  commerçants, et à l'Agirc-Arrco ; le reste à faire.** M4 (ee8e6ac, 213318b). La
  relecture R-M4 (db2457d) les juge « conformes » mais trouve un écart grave, la fiche
  disant que l'Agirc-Arrco garde la décote, et un écart moyen ; M4-bis (e5e8d34)
  corrige la fiche, relue « conforme » (`175/2026-11-03-relecture-correction-taux-plein-parents.md`).
  Agirc-Arrco : M3 (16663e5), de +5 % à +9 % de leur complémentaire (18:33:11).
- **Relue** : R-M3b (54baa1b), « la règle est conforme ; un écart moyen, six faibles ».
  L'écart moyen touche la majoration pour enfants de la réversion depuis 2019 : le modèle
  y applique encore la baisse pour départ anticipé dans un cas (19:47:39). Sa correction
  (M3-bis) n'est pas publiée à 208ac7c.
- **Reste, écrit dans la fiche, non calculé** (12:26:04) : les fonctionnaires, la CAVIMAC
  et les points d'avant 1973, la RCI. L'Ircantec : question 1. Pour un parent parti avant
  65 ans, aucun texte ne dit à partir de quel âge l'Agirc-Arrco compte sa baisse :
  question 8.

### 15. L'Agirc-Arrco, la majoration pour enfants avant le coefficient

- **Avis** (06:05:50) : « Agirc-Arrco : appliquer la majoration pour enfants avant la baisse pour départ anticipé ? Oui, sans urgence »
- **Où elle en est : faite.** M3 (488c30a, 2d15a5b) : la majoration se calcule avant la
  baisse, à l'Arrco de 2012 à 2018, partout depuis 2019 ; 3 cas témoins sur 930 montent,
  d'au plus 94 € par an (+0,31 %) (17:05:52). Avant 2012, aucun texte ne tranche : calcul
  inchangé, déclaré (question 8).
- **Relue** : R-M3 (ee67f54), « conforme » ; écarts tous faibles.

### 16. Le récupérateur de la Cnav pendant l'import de nuit

- **Avis** (06:18:01) : « faut-il que notre outil refuse tout seul, en le signalant, de relire le site de la Cnav pendant sa mise à jour de nuit ? Ce serait une petite protection, avec son test. Son avis et le mien : oui. Cela évitera la fausse alerte de cette nuit. » Repris à 08:25:31 : « Pour les deux, mon avis est oui. »
- **Où elle en est : faite.** H (f0772d0, f6d3a95) : `cnav_legislation.py` refuse de relire
  la base pendant son import de nuit, et le dit. Réglage de script, sans effet sur un
  chiffre, vérifié par l'orchestration (16:18:07), sans relecture indépendante.

### 17. La part de départs avec décote des générations nées depuis 1960

- **Avis** (07:03:11) : « faut-il revoir la part de départs avec décote que le modèle prête à tous les retraités nés après 1960 ? Ce chiffre, 13 % des hommes, ne vient que des salariés du privé. Son avis et le mien : oui, dans une session à part. » Repris à 08:25:31 : « Pour les deux, mon avis est oui. »
- **Où elle en est : à faire.** File I, action 138, étape 14.

## Questions posées au propriétaire, sans réponse au 3 novembre

Les neuf questions se numérotent de 1 à 9 dans les messages au propriétaire. Aucune
n'est décidée : le dernier message lu de la vague 5 (19:47:39) dit « Neuf questions
vous attendent ». Les notes d'état de la vague 4 ont numéroté les premières 18, 19 et
suivantes ; c'est la même suite. L'avis qui suit chaque question est celui de
l'orchestration, que le propriétaire n'a ni approuvé ni refusé.

1. **L'Ircantec et les parents de trois enfants** (10:29:27). « Nouvelle question
   (oui ou non) : l'Ircantec, la retraite complémentaire des contractuels du public,
   dispense aussi ces parents de décote, mais le modèle les pénalise encore. Faut-il
   l'ajouter à la correction de l'Ircantec déjà prévue ? Mon avis : oui, le texte est
   clair. » Reposée à 12:16:01 : « On l'ajoute au travail sur les complémentaires ?
   Mon avis : oui. »
2. **Les décrets des marins de 1968 à 1985** (10:35:58). « Sa question (oui ou non) :
   faut-il aller lire les décrets de 1968 à 1985, que l'on ne trouve que dans le
   Journal officiel papier, pour couvrir aussi ces années ? Son avis et le mien : non.
   Le plafond était alors bien au-dessus de tous les salaires des marins, donc l'effet
   serait nul. » À 12:16:01 : « Les lire ne changerait aucun chiffre. Mon avis : non. »
3. **Les barèmes des marins d'avant 2008** (11:32:33). « Nouvelle question (oui ou
   non) : faut-il chercher les vrais barèmes de salaires des marins d'avant 2008 et
   corriger le modèle ? Cela pourrait changer la pension des marins aux carrières
   anciennes. Mon avis : oui, si les textes sont lisibles. Sinon, on le signale comme
   limite. » Précisée à 12:25:05 : « Faut-il faire lire les vrais barèmes de 1985 à
   2007 dans le Journal officiel papier, c'est-à-dire ses pages scannées ? Mon avis :
   oui si le parti doit chiffrer les pensions des marins d'avant 2008, sinon cela peut
   attendre. » À 15:23:15, le montant de l'arrêté du 30 juin 1995 « ne figure qu'au
   Journal officiel imprimé » : « C'est votre question 3. »
4. **La surcote des générations nées après 1953** (12:18:01, sous « Une nouvelle
   question (rien ne bloque aujourd'hui) »). « Le bonus des personnes nées après 1953.
   L'enquête de la DREES ne voit pas ces générations. Propose-t-on de leur donner la part qu'on observe chez les nouveaux
   retraités de la Cnav en 2024, soit 19 %, comme on l'a déjà fait pour la décote ?
   Mon avis : oui, mais seulement une fois ajoutées les personnes qui partent après
   67 ans, que le modèle oublie aujourd'hui. » La relecture R-I a corrigé le motif
   (15:01:51) : les départs après 67 ans n'expliquent qu'une part de l'écart de 8 points
   (11 % au modèle, 19 % à la Cnav) ; R-I-bis (19:01:42) les chiffre entre 1,7 et
   2,6 points. Dernier avis (19:47:39) : « oui, mais seulement après avoir compris les
   6 points d'écart encore inexpliqués ».
5. **Le deuxième bonus agricole, D. 732-76** (13:11:55, sous « Nouvelle question 5 : un
   autre bonus agricole »). « On a découvert un deuxième bonus de 17 % pour les
   exploitants agricoles, fixé par un décret de 1981 qui n'existe qu'en version papier
   scannée. Aucun texte lu ne dit s'il s'ajoute au premier, et le
   modèle ne l'applique pas : certains anciens exploitants sont donc peut-être
   sous-estimés. Mon avis : faire lire ce décret au Journal officiel du 20 août 1981.
   S'il ne dit pas si les deux bonus s'ajoutent, écrire à la MSA, la caisse des
   agriculteurs. » (Les puces du message d'origine sont retirées.) La relecture R-K lit D. 732-76 : « majoré de 17 % lorsque [...] au
   moins égal à seize », concordance « Décret 81-790 1981-08-18 art. 2 »
   (`131/2026-11-03-relecture-majoration-de-1986-a-2025.md`).
6. **L'index de la DILA sur GitHub** (15:42:22). « Les tests qui relisent les textes
   officiels ont besoin de cet index. Sur GitHub, l'index n'est pas téléchargé, donc
   ces tests y sont sautés : seules nos sessions les font tourner. Faut-il modifier la
   suite de GitHub pour qu'elle le télécharge ? C'est une protection du dépôt : rien
   ne s'y change sans votre accord. Mon avis : non pour l'instant. Il vaut mieux que
   chaque test garde ses propres chiffres, tirés du texte, comme M1-quater le fait pour
   les marins ; GitHub repère alors une erreur même sans l'index. »
7. **Les cultes, de 2002 à juin 2005** (16:59:40). « De 2002 à juin 2005, une garantie
   de rémunération s'applique aux ministres des cultes. Aucun texte lu ne dit comment
   elle entre dans leur base de cotisation : soit elle la relève jusqu'à son montant
   (au plus +11 %), soit elle s'y ajoute en entier. Le modèle n'en tient pas compte
   pour l'instant, et la fiche le dit. Mon avis : écrire à la CAVIMAC, la caisse des
   cultes, pour connaître sa pratique. L'effet ne porte que sur trois ans et demi de
   carrière. »
8. **L'Agirc-Arrco, une lettre** (17:05:52, complétée à 18:33:11). « Faut-il écrire à
   l'Agirc-Arrco pour savoir comment elle calculait cette majoration avant 2012 ? Mon
   avis : oui, dans une même lettre que celle à la caisse des cultes (question 7). »
   Complétée à 18:33:11 : « Pour un parent parti avant 65 ans, aucun texte ne dit à
   partir de quel âge l'Agirc-Arrco compte sa baisse de pension. Le modèle lui sert 91 %
   de sa pension à 64 ans ; ce serait 96 % si la baisse se comptait à partir de 65 ans.
   Je propose de le demander à la caisse dans la même lettre que le reste de la
   question 8. »
9. **Les tableaux de durées d'échelon que le LEGI abîme** (17:15:01). « Faut-il lire à
   la main, au Journal officiel, les tableaux que la base officielle abîme ou ne
   livre pas (notamment la protection judiciaire de la jeunesse depuis 2021) ? Mon
   avis : oui, mais plus tard, quand on reliera ces durées aux grilles de salaire. Et
   seulement pour les métiers que le simulateur propose. Pour l'instant, aucun calcul
   n'en dépend. »

À 19:47:39, l'orchestration dit : « Questions 5, 7 et 8 : faut-il écrire à la MSA, à la
CAVIMAC et à l'Agirc-Arrco ? Mon avis est oui pour les trois. »

**Deux questions que le propriétaire n'a plus à trancher.** Les marges élargies du test
du COR (« Nouvelle question », 11:29:51) : la relecture les a jugées « justifiées »
(12:10:45), comme l'avis le posait. Le doute sur la date « 1980 » du décret n° 83-1260
(15:57:56) : R-B2-bis « a aussi réglé la question de B2-bis sans avoir besoin de vous »
(16:25:11), par le décret publié au Journal officiel du 3 août 1990.

## Ce que la vérification de cette note a relevé

- L'heure de la demande : 09:20:30 à l'événement, 09:25 dans les notes d'état.
- La décision 1 a été prise sur un chiffre que la lecture du texte a invalidé : ce qui
  est fait est la règle, écrite ; aucun chiffre ne bouge, mais l'absence d'effet de 1985
  à 2007 est « très probable », non prouvée (décision 1, questions 2 et 3).
- Les formules abrégées des notes d'état (« garder le décret (150 €) », « à inscrire
  par I ») ne remplacent pas le texte des avis : fait foi le texte cité plus haut.
- La décision 14 n'est pas close : la correction de la réversion de l'Agirc-Arrco et
  la suite pour les fonctionnaires, la CAVIMAC, les points d'avant 1973 et la RCI sont
  à publier.
- Je n'ai trouvé de relecture indépendante ni pour la décision 2 ni pour la 16, qui ne
  changent aucun chiffre ; l'orchestration a vérifié la 2 (rangement sans perte) et la
  16 elle-même.

## Les événements cités

Fil de la vague 4 (`session_01FVFLAj3amicrSTwzStJQ8q`) :

| Heure (UTC) | Événement |
|---|---|
| 06:05:50 | `3541789b-a4a2-4ef9-9431-c5d8bec41a0e` : « Tes 15 questions, avec mon avis » |
| 06:18:01 | `1e9683eb-06f7-485c-8bfb-dd11b1a55bc4` : la 16e |
| 07:03:11 | `f3bd1041-e204-4365-afd9-e404657abfcc` : la 17e |
| 08:25:31 | `879591cb-96f0-4dc0-b174-cfea8fda0f79` : « Pour les deux, mon avis est oui » |
| 09:20:30 | `9e4b6f62-272f-4493-b5fe-fb8740dde6e0` : le message du propriétaire |
| 09:21:16 | `99874cce-08c7-42f4-8d11-d6652a3f3731` : la précision demandée |
| 09:21:20 | `19953f7b-954b-4577-8294-3d06da2222c8` : la question à trois réponses |
| 09:22:35 | `5b805c65-a78a-4897-82f5-c2edd55caa58` : « Oui, applique tes avis (Recommandé) » |
| 10:29:27 | `2259d81f-1615-4551-b129-541f8079be4c` : question 1 |
| 10:35:58 | `a54889b9-6a0b-4aa8-8b1e-af113a5e816b` : question 2 |
| 11:32:33 | `fad92345-d4c1-4760-8fe7-e70feb9b1b1b` : question 3 |
| 12:16:01 | `f6edbccc-28da-4b1b-89cb-b6061d15753e` : les questions 1 à 3 reposées |
| 12:18:01 | `ee65904f-5db1-4036-bbf0-3e0348d33f21` : question 4 |
| 12:25:05 | `fe5186d5-7dcc-4ed9-93b9-f6b045cf780e` : question 3 précisée |
| 13:11:55 | `810c30c4-ff3e-4f2c-941f-aa986024e9b5` : question 5 |
| 14:35:16 | `7ba1dd53-9774-4bb1-aeff-7fafbec2036c` : passage de la main, « Vos 5 questions » |

Fil de la vague 5 (`session_01FVFLAjkV9R1z73xEZ5tQ6b`) :

| Heure (UTC) | Événement |
|---|---|
| 15:01:51 | `041d23fe-1d46-4cc2-9ca6-2c24264b33c7` : R-I corrige le motif de la question 4 |
| 15:42:22 | `26afb0cc-c3fb-487f-adc1-abbb6cf892cf` : question 6 |
| 16:59:40 | `ce0f5474-91d0-4ca8-9d96-5116050c3e58` : question 7 |
| 17:05:52 | `4f3fbe0e-b5c9-474f-b44a-f1f563f1536b` : question 8 |
| 17:15:01 | `17c0066f-a3c7-45cb-9328-3ecf4caf5948` : question 9 |
| 18:33:11 | `e19a335c-8516-4747-b4a7-d85f2853cf83` : question 8 complétée |
| 19:47:39 | `4ec08917-14e6-448b-97d8-2a457566126e` : « Neuf questions vous attendent » |
