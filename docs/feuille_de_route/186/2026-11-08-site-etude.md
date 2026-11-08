# Le site face au programme : ce qu'il dément, ce que montrera la version publique, et le rendement

**Reprise, au 8 novembre 2026.** Le chantier 9 est étudié, rien n'est
retouché. Le site dément le programme sur onze sujets, dans une trentaine
de phrases, dont cinq seulement sont déclarées démenties au catalogue (« 1. ») ;
l'architecture du 6 novembre tient pour la version publique sans simulateur,
réordonnée (« 2. ») ; le rendement a quatre façons de se montrer (« 3. »).
Au propriétaire : les cinq questions de la fin. Puis une session du site,
quand celle de la réversion aura quitté les pages, fait ce qui ne dépend de
rien (« 4. ») ; le reste suit A ou B et les portages du modèle.

*Le 7 novembre 2026, le propriétaire demande d'attaquer le chantier 9 de
l'action 186, « Le site et le simulateur » (« Attaque le chantier 9 »). La
session lit les pages telles qu'elles sont sur `origin/main` (commit
`b2a5715`, le texte des neuf pages fabriquées), les confronte aux décisions 1
à 87 de `docs/feuille_de_route_programme.md` et au catalogue
`data/reference/site/affirmations.yaml`, et refait au modèle le rendement des
cotisations. C'est une étude : « l'étude précède tout changement du modèle ou
du site ». Aucune page n'est touchée ; deux autres sessions travaillent au
même moment sur le moteur (action 187) et sur la réversion au scénario 6.
Les chiffres portent leur origine : **(site)**, une page fabriquée ;
**(modèle)**, `scripts/cycle_de_vie.py` à ce commit.*

*Une précaution de vocabulaire, que le site impose. Les pages numérotent
quatre systèmes : 1, le droit actuel ; 2, le compte notionnel sur la part
salariale ; 3, le compte notionnel sur les deux parts ; 4, la proposition. Le
modèle et la feuille de route du programme en numérotent six : le système 3
du site est le scénario 4 du modèle, le système 4 du site est le scénario 6.
Cette note dit « système » pour le site et « scénario » pour le modèle.*

## L'essentiel

**Le site dément le programme sur onze sujets, mais sur aucun des quatre
chiffres du chantier 7.**
« La moitié du déficit public », le « TRI négatif », le PEE et « proche du
défaut » ne sont sur aucune page : ils étaient dans le programme écrit, pas
sur le site (décisions 82 à 85). La page Pourquoi changer dit déjà ce que la
décision 84 retient, un rendement en baisse et non négatif. Ce que le site
dément, ce sont les décisions des chantiers 1 à 6 : la réversion, la garantie
d'office, les complémentaires caisse par caisse, la TVA gardée, l'indexation
du stock, l'apport pour un premier logement, les droits des accidents de la
vie ; vingt-six décisions en tout, et un douzième sujet, les intérêts de la
créance de la garantie, est une question. Cinq phrases sont déclarées
`contredite` au catalogue, toutes sur la réversion ; les autres sont
`verifiee` contre le modèle, qui n'a pas encore reçu la décision, ou hors du
catalogue, faute d'être en gras. La LVT et l'argent aux parents
d'aujourd'hui n'y paraissent pas.

**L'architecture du 6 novembre tient, et la décision 34 la rend plus
nécessaire.** Sans simulateur, le lecteur ne peut plus vérifier sur sa
carrière : la version publique doit lui répondre d'avance, par des cas types
et par « Les questions qui fâchent ». L'accueil s'ouvre aujourd'hui sur le
formulaire du simulateur, et les quatre cartes à partager y renvoient toutes.

**Le rendement de la proposition est plus faible que celui du droit actuel,
et presque entièrement parce que le droit actuel promet ce que ses
cotisations ne paient pas.** Pour le salarié moyen né en 2000 : 1,3 % réel
au droit actuel, 0,2 % pour la proposition, et 0,3 % pour les mêmes
cotisations que le droit actuel, rendues par la règle d'une répartition à
taux constant (le système 3 du site) **(modèle)**. Mais sous les conventions
du COR, le rendement réel de la proposition devient négatif pour le salarié
moyen né à partir de 1990 (−0,1 %) et pour le cadre (−0,3 % pour celui né en
2000) : le « TRI négatif » que la décision 84 retire au droit actuel, un
adversaire pourra l'opposer à la proposition. Le simulateur montre déjà ces
rendements, sans les expliquer.

## 1. Ce que les pages disent contre le programme

Une ligne par décision ; l'extrait est le texte de la page **(site)** ; la
dernière colonne dit qui le corrige, et quand.

| Décision | Ce que dit le site | Catalogue | Corrigé par, et quand |
|---|---|---|---|
| 16 (réversions servies gardées) ; 17 à 24 (rente sur deux têtes, par défaut pour les mariés) | Accueil : « Notre système ne sert aucune réversion » ; « Et si je meurs ? » : « notre système ne sert pas de pension de réversion » ; Coût : la marche « Réversion supprimée », −43,6 Md€, de la cascade ; « Seul le système actuel sert la pension de réversion. » | `contredite`, action 186 : cinq entrées | La session de la réversion, étape 2 (le stock gardé, la cascade d'abord), puis 5 (la rente) ; `…-reversion-scenario-6-plan.md` |
| 22 (le conjoint d'un actif mort touche la moitié de son compte converti) | Accueil, tableau terme à terme, « Décès avant la retraite » : « vos cotisations restent au système » | absent | Même plan, étape 6 |
| 20 (la garantie servie d'office) | Accueil : « Elle se demande, comme l'ASPA, et se refuse » ; « Le programme retient qu'un ayant droit sur deux la réclame » — et le coût de la garantie suit ce taux de recours | absent | Même plan, étape 3 |
| 30 (la reprise sur la succession, à hauteur de ce que la garantie a avancé, « pas sur autre chose ») | Accueil : la garantie est « une créance de l'État, qui porte intérêt au taux auquel il emprunte » | absent | Au propriétaire : les intérêts sont-ils « autre chose » ? |
| 33 (les cinq points obligatoires ouverts à l'apport pour un premier logement) | Accueil, la part capitalisée : « Ni achat de résidence principale, ni sortie anticipée : l'argent n'en sort qu'en rente viagère, ou par l'héritage, pour les 5 % obligatoires comme pour les 5 % que vous ajoutez. » | absent | Texte seul, sans le modèle ; le plafond reste ouvert (chantier 8) |
| 3 et 87 (la baisse par cinquièmes, entière en 2030) | Accueil, la bascule : « Chaque carrière est recalculée depuis sa première cotisation, y compris celles dont la pension est déjà liquidée » ; la page Coût baisse d'un coup | absent | Le modèle, puis le site ; la décision 87 le note déjà |
| 41, 73 et 74 (les pensions servies suivent les prix moins la hausse du nombre de retraités par cotisant ; une prime de 2,15 % mise en réserve) | Accueil : « Elle reste ensuite revalorisée sur les prix » ; les points de blocage : « l'indexation sur les prix est conservée » | absent | Le modèle d'abord : la règle de la prime n'y est pas écrite (chantier 5) |
| 37, 40, 48, 70 et 72 (les complémentaires intégrées caisse par caisse, à l'épuisement de leurs réserves ; 25,83 % pour le salarié du privé jusqu'à l'intégration de l'Agirc-Arrco ; le RAFP et trois caisses à part) | Accueil : « Demain, le même taux pour tout le monde » ; « la cotisation retraite passe de 28 % du salaire brut, employeur compris, à 23 % » ; la bascule : « Les régimes fusionnent en un seul », « Toute cotisation postérieure à la bascule est prélevée à 18 % » ; « un seul régime […] même taux pour tous » ; Partager : « de cotisation retraite, pour tout le monde » ; Pourquoi changer : « ramène le prélèvement de 28 % à 18 % » | `verifiee` : `accueil.meme_taux` | Le modèle, étape 2 des complémentaires (le moteur d'une carrière), puis le site |
| 79 et 47 (la part de TVA des retraites gardée ; la compensation de l'Agirc-Arrco aussi) | Accueil : « Les impôts que nous supprimons : 32 Md € rendus aux salaires » ; « Nous cessons donc de les affecter à la retraite. » ; Coût : « Ce que la proposition n'encaisse plus, elle ne le garde pas. » | `verifiee` : `accueil.impots_non_affectes` | Le modèle (la part de la Cnav reste à chiffrer), puis le site ; le partage suit aussi A ou B |
| 80 (la LVT à 2 %, un point aux retraites) | Nulle part | — | Le modèle ne la porte pas (« hors du modèle ») |
| 7, 57, 58, 61 et 78 (les droits des accidents de la vie gardés ; l'AVPF, la MDA d'enfant handicapé, la majoration forfaitaire de réversion gardées ; la garantie dès l'invalidité) | Accueil : « Trimestres et points disparaissent, et avec eux les droits qu'aucune cotisation n'a payés : trimestres gratuits, majorations, minimums. » ; « Payés par l'impôt, dès 65 ans » (aussi sur Partager) ; « La garantie vieillesse, elle, n'est versée qu'à partir de 65 ans. » ; Méthode : la proposition « remet un plancher, et un seul » aux suppressions, « ni AVPF […] ni périodes assimilées » | `verifiee` : `accueil.garantie_montants` | La répartition des 45 dispositifs (chantier 3, ouverte), puis le modèle |
| 62 et 69 (la Banque de France garde son plancher tant que durent ses réserves) | Accueil : la garantie « remplace le jour de la bascule les quatre d'aujourd'hui » | absent | Le modèle ; un détail |
| 29 (la baisse des pensions va pour moitié au déficit, lecture A ou B) | Accueil : « 18 % + 5 % » ; « Le solde de la proposition est de −1,4 point par an en moyenne contre −1,1 pour le système actuel » ; la dette de 2070, « 103 % du PIB contre 66 % » ; « son déficit moyen dépasse celui du système actuel » ; les baisses médianes de 26, 14 et 28 % ; Coût : « Ce qu'elle encaisserait 18 % » ; Carrières types : le coefficient de la proposition « au plus bas 0,79 en 2026 » | `verifiee` ou absent | Le choix de A ou B, puis le modèle, puis le site |
| 50 et 51 (la moitié de ce que coûtaient les droits familiaux aux parents d'aujourd'hui, en argent) | Nulle part ; la cascade de Coût porte l'économie au solde | — | L'étude de la prestation (décision 51) |

Trois phrases ne démentent pas une décision, mais ce que le modèle mesure :
- *« Le rendement est le même pour tous »* (accueil,
  `accueil.rendement_meme_pour_tous`) : son contrôle vérifie que le taux de
  revalorisation d'une année ne dépend pas de la carrière, ce qui est vrai ;
  le rendement d'une vie entière, lui, va de −0,1 % à 0,5 % réel entre les
  treize carrières types nées en 2000 (« 3. »). C'est quatre fois moins
  d'écart qu'au droit actuel, mais pas « le même ».
- *« 100 % de ce que vous avez cotisé vous revient »* (accueil,
  `accueil.vous_revient`) : le capital entier est bien converti en pension ;
  mais en euros constants, le cadre et le libéral nés à partir de 1980
  reçoivent leur mise ou un peu moins (de 0,0 à −0,2 % réel ; −0,3 % pour le
  cadre né en 2000 sous les conventions du COR).
- *« règle l'écart chaque année par un coefficient d'équilibre »* (Pourquoi
  changer) et ses sœurs : déjà `contredite` sous l'action 11, et à relire
  avec la décision 41, qui fait porter l'effort démographique par
  l'indexation des pensions servies.

Ce que le site dit déjà comme le programme : l'âge de 65 ans (décision 68) ;
la garantie de 1 050 € seul et 800 € en couple (65) ; le compte capitalisé
qui appartient à l'assuré (32) ; rien sur l'héritage (5), la reprise sur la
succession de la seule garantie (30, hors les intérêts) ; la MDA et la
majoration de 10 % retirées (52 à 54) ; le rendement en baisse (84).

**Ce que le catalogue ne voit pas.** Il juge une phrase contre le modèle. Une
décision que le modèle porte déjà fait tomber le contrôle de la phrase
qu'elle dément : quand le modèle gardera la part de TVA, le contrôle de
`accueil.impots_non_affectes` échouera, et la phrase devra changer. Mais deux
décisions n'entreront jamais au modèle, l'apport pour un logement (33) et
les intérêts de la créance (30), et les phrases absentes du catalogue ne
tombent avec aucun contrôle : elles ne changeront que si quelqu'un les
relit. Cette table en tient la liste.

## 2. L'architecture des pistes, pour la version publique

**Ce que le site est aujourd'hui** **(site)**. Neuf pages : l'accueil
(« Notre programme pour les retraites »), Simuler, Coût, Pourquoi changer,
Partager, Le saviez-vous ?, et, sous « Pour vérifier », Carrières types,
Droits non cotisés, Méthode et sources. L'accueil s'ouvre sur le formulaire
du simulateur (« Et vous, ça donne combien ? ») ; Coût et Droits non cotisés
finissent sur « Et pour vous ? », qui y renvoie ; les quatre cartes de
Partager et son texte prêt à coller pointent vers `#simulateur`, et l'une est
« L'appel au simulateur ». Le mot « simulateur » paraît soixante-quatre fois
dans le texte des neuf pages. Retirer le simulateur, c'est donc récrire
l'accueil et Partager, et recoudre une dizaine de renvois.

**Les pistes, une à une.**

1. *Le rendement d'un euro cotisé, en tête.* À garder, mais par cas types,
   non par carrière : sans simulateur, le lecteur cherche la carrière qui lui
   ressemble. Le modèle le donne déjà pour treize carrières et sept
   générations (`cycle_de_vie.py`) ; il montre deux injustices à la fois,
   entre générations (3,3 % réel pour le salarié moyen né en 1940, 1,3 % pour
   celui né en 2000) et entre statuts (en 2000, de −0,1 % pour le
   fonctionnaire de catégorie B à 2,3 % pour l'exploitant agricole). C'est le
   fil du parti des cotisants. Mais un tableau des rendements appelle la
   colonne de la proposition, et c'est la question de la partie 3. Le
   tableau se fabrique en Python et se lit au paquet, comme tout chiffre
   d'une page qui agrège (`moteur/CLAUDE.md`).
2. *Les trois portes d'entrée.* À garder, comme trois sections de l'accueil
   plutôt que trois pages : chacune a son adresse (un mot derrière le `#`),
   et les questions de l'accueil les contiennent déjà (« Ma retraite va-t-elle
   baisser ? », « Je suis déjà à la retraite », « À quel âge pourrai-je
   partir ? », « Qu'est-ce qui change sur ma fiche de paie ? »). *Je
   travaille* : le salaire net, le compte à son nom, les cinq points et le
   premier logement — le salaire net suit A ou B. *Je pars bientôt* :
   65 ans, les droits recalculés, pas de transition (décision 63), la
   garantie. *Je suis retraité* : la baisse par cinquièmes, son plancher, la
   réversion gardée, la garantie d'office, la reprise, l'indexation — tout
   suit le chantier 2 et les portages du modèle. Chaque porte finit sur la
   carrière type la plus proche, dans Le miroir.
3. *La page Coût dans l'ordre du chantier 1.* Nécessaire : c'est la page
   qui dit aujourd'hui que la proposition creuse la dette (103 % du PIB en
   2070 contre 66 %), et l'accueil le répète dans ses points de blocage.
   L'ordre : le déficit du droit actuel ; la baisse des pensions (118 Md€ en
   2026 sur la base de la page) ; son partage entre le déficit et les
   cotisants ; les recettes gardées et neuves (TVA, LVT) ; le solde et la
   dette. Rien ne s'en écrit avant A ou B.
4. *« Comment on paie la transition ».* Plutôt la fin de la page Coût
   qu'une page de plus : c'est là que les décisions 29, 30, 38, 47, 50, 79 et
   80 se rejoignent, et la version publique perd déjà Simuler. Attend A ou B
   et la LVT au modèle.
5. *« Les questions qui fâchent ».* Une page à part, et la plus utile à une
   version sans simulateur : le lecteur ne peut plus vérifier lui-même, il
   faut répondre d'avance. Pourquoi changer porte déjà des objections, mais
   au diagnostic ; celles-ci portent sur la proposition. Les questions se
   savent dès maintenant : ma pension baisse de combien ; mon rendement
   est-il plus faible (« 3. ») ; ma veuve ; la maison de mes parents (la
   reprise, décisions 30 et 66) ; les mères (52 à 54, et l'argent aux parents
   d'aujourd'hui, 50) ; 65 ans (68) ; l'Agirc-Arrco (43 et 48) ; la
   Constitution et la CEDH (6) ; et si l'emploi baisse (46, 73 à 76). Les
   chiffres des réponses suivent A ou B.
6. *« Le miroir ».* À faire : les systèmes 2 et 3, qui montrent ce que la
   carrière aurait donné si le compte avait toujours existé, sur la seule
   part contributive (décision 28), quittent Coût et Simuler pour une page à
   eux, qui reprend Carrières types. Ne dépend d'aucun chantier, mais déplace
   des blocs de `pages.js` : après la session de la réversion.

**La version publique, proposée** : l'accueil (le rendement d'un euro cotisé,
les cinq promesses de la décision 45, les trois portes) ; Coût, dans l'ordre
du chantier 1, qui finit sur la transition ; Les questions qui fâchent ;
Pourquoi changer ; et sous « Pour vérifier », Le miroir, Droits non cotisés,
Le saviez-vous ?, Méthode et sources ; Partager, ses cartes recousues. Neuf
pages, comme aujourd'hui, Simuler en moins, Les questions qui fâchent et Le
miroir en plus, Carrières types fondue dans Le miroir. Les réglages de la
page Coût font tourner le moteur dans le navigateur : la version publique
peut les garder, ou se figer sur ses réglages par défaut, sans moteur du
tout. La seconde est plus simple et suit la décision 34 ; elle est au
propriétaire.

## 3. Comment montrer le rendement

**Les chiffres** **(modèle)**, `python scripts/cycle_de_vie.py --indicateurs
rendement_reel,rendement_smpt`, conventions du dépôt : flux bruts, déflatés
des prix, survie de la génération ; toutes les cotisations, et pour la
proposition les deux parts de son pilier, dont la rente entre dans ce qui est
reçu ; ni l'ASPA ni la garantie, que l'impôt paie.

| Rendement interne réel, par an | Né en 1940 | 1970 | 2000 |
|---|---:|---:|---:|
| Salarié moyen, droit actuel (système 1) | 3,3 % | 1,3 % | 1,3 % |
| Salarié moyen, mêmes cotisations, règle d'une répartition à taux constant (système 3 ; scénario 4) | 1,2 % | 0,5 % | 0,3 % |
| Salarié moyen, proposition (système 4 ; scénario 6) | 1,2 % | 0,4 % | 0,2 % |
| Cadre, droit actuel | 2,6 % | 0,5 % | 0,5 % |
| Cadre, proposition | 0,7 % | 0,1 % | −0,0 % |
| Au SMIC, droit actuel | 3,6 % | 1,4 % | 1,4 % |
| Au SMIC, proposition | 1,9 % | 0,9 % | 0,5 % |

Entre les treize carrières types nées en 2000, le droit actuel va de −0,1 %
à 2,3 %, la proposition de −0,1 % à 0,5 % ; nées en 1940, de −0,3 % à 7,6 %,
et de 0,7 % à 2,1 %. Rapporté au salaire moyen plutôt qu'aux prix, le
salarié moyen né en 2000 rend 0,6 % au droit actuel et −0,5 % à la
proposition ; sous les conventions du COR (`--cor`), −0,8 % contre 0,4 %,
et en réel −0,1 % contre 1,1 %. Le calcul de la note du chantier 7
(0,2 % contre 1,3 %) se retrouve.

**D'où vient l'écart.** Le système 3 crédite exactement les cotisations que
le droit actuel prélève, à la règle d'un compte notionnel : il rend 0,3 %.
Un point des 1,1 qui séparent le droit actuel de la proposition tient donc à
ce que le droit actuel sert au-delà de ce que ses cotisations paient à taux
constant — l'impôt affecté aujourd'hui, le déficit que le COR projette
demain (2,4 points de PIB en 2070). Le dixième qui reste tient aux choix
propres de la proposition (son taux, son pilier, ses 65 ans), que l'étude n'a
pas séparés. Et la règle du compte fixe le niveau : le compte suit la masse
salariale jusqu'au départ, puis la pension suit les prix, avec un diviseur
qui n'anticipe aucune croissance ; sous les hypothèses du COR, cela fait
quelques dixièmes de point par an sur une vie.

**Ce que le lecteur voit déjà.** Le simulateur imprime ces rendements, sous
la convention de l'OCDE, pour sa carrière et chaque âge de départ : « Le
rendement réel de vos cotisations, par an », quatre colonnes, la proposition
sous le droit actuel, et pour toute explication une bulle sur la façon de les
compter. Le problème n'est pas à venir, il est en ligne.

**Quatre façons de le montrer.**
- **A. Trois colonnes : promis, payé, proposé.** À côté du droit actuel, ce
  que ses propres cotisations rapporteraient à la règle d'une répartition à
  taux constant (le système 3, déjà calculé), puis la proposition. La phrase :
  « Le système actuel vous promet 1,3 % par an ; ses cotisations en paient
  0,3 % ; le reste viendra de vos impôts ou de vos enfants. Nous vous servons
  0,2 %, payés. » Honnête, déjà chiffrée, une étiquette et une phrase au
  simulateur. Sa faiblesse : « payé » repose sur la convention du site, et
  un adversaire répondra que l'État paiera ; la réponse est que l'État, ce
  sont les mêmes contribuables.
- **B. L'écart plutôt que le niveau.** En tête, l'injustice que la
  proposition réduit : entre générations, et entre statuts (2,4 points
  d'écart entre les carrières nées en 2000 au droit actuel, 0,6 à la
  proposition) ; les niveaux publiés à la page Méthode avec leur convention,
  comme la décision 84 le promet. C'est le fil du parti des cotisants. Sa
  faiblesse : quelqu'un mettra les niveaux côte à côte, et un tableau qui ne
  les montre pas semblera les cacher.
- **C. Compter l'impôt dans la mise.** Ajouter aux cotisations de chaque
  génération sa part des impôts affectés et du déficit qu'elle remboursera :
  un rendement « tout compris ». Le plus juste en principe ; mais c'est une
  comptabilité des générations que le modèle ne tient pas, des semaines de
  travail, et des conventions qui se discutent. Plus tard, si jamais.
- **D. Ne plus le montrer.** Retirer le tableau du simulateur. Le code et
  les conventions sont publics, la décision 84 promet de publier la
  convention, et les adversaires feront le calcul : le retrait se verrait.
  La décision 34 règle d'ailleurs la question pour la version publique, qui
  n'a pas de chiffre personnel ; il ne reste que les cas types.

**La piste.** B en tête — l'accueil, le rendement d'un euro cotisé, les
écarts —, et A partout où les niveaux se comparent : le simulateur des
adhérents, « Les questions qui fâchent », la page Méthode. La convention
dite, en réel, et pourquoi : rapportés au salaire moyen, comme le fait le
COR, tous les rendements baissent et celui de la proposition passe sous zéro
pour toutes les carrières nées à partir de 1990, et presque toutes dès 1980. Le programme doit le dire
avant un adversaire, dans « Les questions qui fâchent ». Les phrases « le
rendement est le même pour tous » et « 100 % de ce que vous avez cotisé vous
revient » se récrivent avec leur condition (« 1. »).

## 4. Ce qui se fait tout de suite, et ce qui attend

**Tout de suite, sur l'accord du propriétaire,** dans une session du site,
une fois que celle de la réversion aura quitté les pages (`git log
origin/main -- moteur/js/pages.js` le dit), en une passe :
- la phrase de l'apport pour un logement (décision 33), et celle des
  intérêts de la créance si le propriétaire tranche contre eux (30) ;
- l'option de rendement choisie, au tableau du simulateur, et les deux
  phrases de l'accueil, avec leur condition ;
- hors des pages, dans une session du modèle : le tableau des rendements par
  génération et par carrière, fabriqué en Python pour le paquet ;
- hors des pages, dans une note : la liste des « questions qui fâchent »,
  avec leurs sources, les chiffres laissés en blanc où ils attendent A ou B.

**Après les chantiers 1 à 6 et les portages du modèle** :
- A ou B : le taux, le solde et la dette, le gain des actifs, les baisses
  médianes — l'accueil, Coût, Carrières types, Partager ;
- le chantier 2 et la décision 87 : la baisse par cinquièmes, la porte des
  retraités ;
- les complémentaires au moteur (décisions 37 à 48, 70 à 72) : le taux de
  25,83 % jusqu'à l'intégration de l'Agirc-Arrco, la fin de « un seul
  régime » à la bascule ;
- l'indexation du stock (41, 73 à 77), la TVA gardée (79), la LVT (80),
  l'argent aux parents (50 et 51), les droits gardés (57, 58, 61) et la
  garantie dès l'invalidité (78), la répartition des 45 dispositifs
  (chantier 3) ;
- la réversion, étapes 2 à 6 de son plan, déjà engagée.
La page Coût dans l'ordre du chantier 1, la transition, les trois portes et
les réponses des questions qui fâchent attendent ces chiffres : une seule
refonte, quand ils seront là, plutôt qu'une retouche par décision, que chaque
passe paierait en témoins.

**Après l'action 187.** La version publique n'en a pas besoin, si elle se
fige sur ses réglages par défaut : ce sont les mêmes pages, Simuler en
moins, que `construire_pages.py` fabriquerait à part. Le simulateur des
adhérents, si : où il vit, et comment on y entre. Un site statique ne
restreint l'accès à personne, et une adresse non publiée ne protège rien ;
il faut un espace des adhérents du parti qui serve le moteur, un déploiement
à part derrière un contrôle d'accès, ou le moteur diffusé tel quel. C'est
l'étape 6 de l'action 187, et la question déjà posée au propriétaire le
7 novembre.

## Au propriétaire

1. **Le rendement** : A, B, C ou D — la note propose B en tête et A pour les
   comparaisons, la convention réelle dite, et le rendement négatif sous les
   conventions du COR annoncé dans « Les questions qui fâchent ».
2. **La version publique** : la liste des neuf pages (« 2. ») ; les trois
   portes en sections de l'accueil ; la transition à la fin de Coût ; Coût
   figée sur ses réglages par défaut, sans moteur dans le navigateur.
3. **La créance de la garantie** : porte-t-elle intérêt, ou ne reprend-elle
   que ce qu'elle a versé (décision 30) ?
4. **Les deux phrases de l'accueil** : « le rendement est le même pour tous »
   et « 100 % de ce que vous avez cotisé vous revient », vraies de la règle,
   à quelques dixièmes près fausses du rendement d'une vie : les nuancer, ou
   les retirer ?
5. **Le calendrier des pages** : une petite passe tout de suite (l'apport
   pour un logement, le rendement), ou tout en une refonte après A ou B ?
