# 5 ante. Le pilier capitalisé : ce que sa rente suppose

Le compartiment de capitalisation obligatoire du scénario 6 est le seul endroit
du modèle où de l'argent est placé, et il porte donc des incertitudes que le
reste n'a pas. Six, et la première est de loin la plus lourde.

**1. La prime de terme n'est pas retirée des forwards.** Les versements futurs
se placent aux taux forward implicites de la courbe du jour. Sous l'hypothèse
des anticipations pures, le forward est le taux futur attendu ; en pratique, il
le dépasse d'une prime de terme que la littérature situe entre <!--chiffre:illustration()-->0,3<!--/--> et <!--chiffre:illustration()-->1<!--/--> point
sur les maturités longues quand la courbe est ascendante. **Le pilier est donc
flatté**, et d'autant plus que la carrière est longue. L'alternative — retirer
une prime estimée — supposerait davantage et se vérifierait moins ; le choix
est dit plutôt que corrigé. Ordre de grandeur : un demi-point de rendement sur
quarante ans vaut une dizaine de pour cent de capital final.

Depuis septembre 2026, le modèle **sait** la retirer :
`Parametres.prime_terme_trente_ans` décompose le taux observé en une moyenne de
taux courts attendus et une prime proportionnelle à la maturité, calcule les
forwards sur la première et rajoute la seconde à la maturité achetée — de sorte
qu'un placement comptant rend toujours le taux coté du jour. **Le paramètre vaut
zéro, et le site publie à zéro** : la réserve ci-dessus tient donc entière, et
ce qui change est qu'elle est désormais mesurable plutôt que seulement dite. À
0,005 — le milieu de la fourchette — le capital d'une carrière de trente-six ans
partant en 2060 recule de 4,8 %, et la rente de 23 € par mois.

Il ne porte que sur le **pilier**, et c'est une correction : portée sur la
courbe commune, la prime déplaçait aussi le taux auquel la page Coût finance
les déficits, donc le stock de dette de TOUS les systèmes — jusqu'à dix points
de PIB sur le système actuel, qui n'a pas de pilier capitalisé. Le coût de
rouler une dette courte se pose dans les mêmes termes et reste une question
ouverte, mais c'en est une autre, et un réglage du pilier n'est pas l'endroit
d'où la trancher. Un test tient la séparation.

Depuis, il est un **réglage du site** : « Taux futurs du pilier capitalisé »,
à côté de celui des frais, avec trois positions — les taux à terme de la
courbe (défaut), la prime retirée au milieu de la fourchette (<!--chiffre:mesure(constante?de=retraite_notionnelle.config&nom=PRIME_TERME_MILIEU&echelle=100)-->0,50<!--/--> point à
trente ans), la prime retirée au haut (<!--chiffre:mesure(constante?de=retraite_notionnelle.config&nom=PRIME_TERME_HAUTE&echelle=100)-->1<!--/--> point). Une réserve qu'un lecteur peut
chiffrer lui-même cesse d'être une réserve qu'on lui demande de croire, et le
choix de publier sous les anticipations pures redevient ce qu'il est : un
choix, pas un impensé.

Cette réserve en portait une autre, restée invisible tant qu'elle n'était pas
chiffrée : **sous les anticipations pures, l'allocation des maturités n'a
aucune conséquence.** C'est une identité, pas une approximation — découper un
horizon en un trente ans, en trois dix ans ou en quinze deux ans accumule
exactement la même chose, parce que c'est ce que l'arbitrage impose au forward,
et les frais annuels n'y changent rien. L'échelle glissante 2/10/30 que le
pilier pratiquait jusque-là était donc un paramètre libre sans effet ; elle a
été remplacée par l'adossement à l'horizon, qui est la bonne règle pour une
autre raison — l'actif sans risque d'une dette datée est le titre qui tombe ce
jour-là — et dont le changement n'a pas déplacé un centime de capital ni de
rente. Voir `docs/methodologie.md`.

**2. La courbe est celle d'un jour.** Elle est datée, publiée, recontrôlée,
mais elle est un instantané : le 17 septembre 2026 et non un mois plus tôt. Un
déplacement général de la courbe déplace tout le pilier, et rien dans le modèle
ne lisse cette dépendance. C'est assumé — une moyenne de courbes n'est la
courbe de personne — et c'est la raison pour laquelle le fichier de référence
garde les courbes successives : un chiffre publié doit pouvoir être refait tel
qu'il a été publié.

**3. Les frais sont ceux du marché, et leur baisse est une hypothèse.** Le
pilier supporte quatre frais, aux vraies moyennes du marché du PER individuel
en 2025, lues sur le rapport de l'OPEF (tableau T7) et sur celui du CCSF de
2021 : <!--chiffre:mesure(parametre?nom=frais_versement_capitalisation)-->1,09<!--/--> % sur versement et <!--chiffre:mesure(parametre?nom=frais_gestion_capitalisation)-->0,76<!--/--> % par an sur encours, moyennes pondérées
par les primes et par l'encours ; <!--chiffre:mesure(parametre?nom=frais_arrerages_capitalisation)-->0,99<!--/--> % sur arrérages, moyenne sur les vingt
assureurs déclarants et non sur les seuls neuf qui facturent (<!--chiffre:illustration()-->2,20<!--/--> %) ; et
<!--chiffre:mesure(parametre?nom=frais_encours_rente_capitalisation)-->0,52<!--/--> % par an sur la réserve de la rente, que l'OPEF ne mesure pas et que le
CCSF relevait sur 22 contrats sur 34, de <!--chiffre:illustration()-->0,60<!--/--> à <!--chiffre:illustration()-->1<!--/--> % par an, estimé au milieu
de la fourchette sur la part des contrats qui facturent. Ce dernier frais pèse
plus que les arrérages au diviseur du modèle. Trois choses que
ces sources disent sur ce que les moyennes sont :

- Le frais sur versement du PER (<!--chiffre:mesure(parametre?nom=frais_versement_capitalisation)-->1,09<!--/--> %) est le double de celui de
  l'assurance-vie (<!--chiffre:illustration()-->0,55<!--/--> %) et six fois celui du contrat de capitalisation
  (<!--chiffre:illustration()-->0,19<!--/--> %), pour les mêmes assureurs et les mêmes fonds en euros. L'OPEF
  l'explique par des frais fixes qui pèsent sur des primes petites. Une
  cotisation prélevée sur chaque paie n'a pas cette structure de coût.
- La moyenne des frais sur arrérages publiée est **non pondérée** et ne porte
  que sur les 9 organismes, sur 20, qui les facturent : onze assureurs sur
  vingt ne prélèvent rien sur la rente. Le <!--chiffre:illustration()-->2,20<!--/--> % est la moyenne de ceux qui
  facturent, le <!--chiffre:mesure(parametre?nom=frais_arrerages_capitalisation)-->0,99<!--/--> % celle du marché, et la médiane est nulle.
- Le frais de gestion du fonds en euros est le poste qui compte, parce qu'il
  s'applique chaque année à tout l'encours, et c'est celui qu'un régime
  obligatoire fait le plus baisser : la prime de pension suédoise, seul pilier
  obligatoire capitalisé adossé à un compte notionnel, coûte <!--chiffre:illustration()-->0,11<!--/--> % des
  encours en frais de fonds après remise et <!--chiffre:illustration()-->0,024<!--/--> % d'administration ; le
  Fonds de réserve pour les retraites, <!--chiffre:illustration()-->0,41<!--/--> % toutes charges comprises, dont
  <!--chiffre:illustration()-->8,6<!--/--> points de base de coûts fixes, en gérant des actions ; l'ERAFP
  provisionne « au moins <!--chiffre:illustration()-->0,2<!--/--> % des encours ». Aucun ne prélève sur les
  versements ni sur les arrérages.

**Ce que ces moyennes sont, et ce qu'on sait des médianes.** Les frais sur
versement et de gestion de l'OPEF sont des moyennes **pondérées** de tout le
marché remis à l'ACPR, par les primes pour le premier, par l'encours moyen pour
le second : un euro versé ou placé y pèse un euro, ce sont les vraies moyennes
de ce qui est payé. Aucune source publique ne donne de médiane pour ces deux
postes ; la seule autre mesure du même marché est le rapport du CCSF de
juillet 2021, sur 34 PER assurance et leurs tarifs affichés, en moyennes
arithmétiques non pondérées. Ce que l'on a, le 20 septembre 2026 :

| Poste | OPEF 2025, marché | Sur tous les déclarants | Médiane | CCSF 2021, 34 contrats affichés |
|---|---|---|---|---|
| Versement | 1,09 %, pondéré par les primes | idem | non publiée | maximum affiché 3,18 % en moyenne, 0 à 5 %, courtiers en ligne à 0 |
| Gestion, fonds en euros | 0,76 %, pondéré par l'encours | idem | non publiée, entre 0,75 et 0,90 % à en juger par la dispersion | 0,87 % en moyenne, 0,60 à 1 % hors un fonds à 2 %, 0,66 à 0,93 % par catégorie |
| Arrérages | 2,20 %, non pondéré, 9 facturants sur 20 | 0,99 % | nulle, onze déclarants sur vingt à zéro | 1,18 % zéros compris sur 30 contrats, 0 à 3 %, onze à zéro, 0,60 % (banques) à 2,30 % (mutuelles) |
| Réserve de rente | non mesuré | non mesuré | non publiée | 22 contrats sur 34 facturent, de 0,60 à 1 % par an |

**La baisse des frais, et ce qu'elle suppose.** Le modèle fait baisser chaque
poste par paliers (`Parametres.frais_*_paliers`), parce que c'est ainsi que
les frais ont bougé partout où une épargne retraite obligatoire a mis les
gérants sous plafond ou en concurrence, et les sources de chaque marche sont
des jeux `controle` du manifeste :

| Marché | Mécanisme | Ce qui s'est passé |
|---|---|---|
| Royaume-Uni | plafond de 0,75 % sur les fonds par défaut, avril 2015 | 0,48 % en moyenne en 2020 sur les régimes concernés, 0,29 % dans les régimes fiduciaires ; les régimes hors plafond passent de 0,79 % à 0,53 % |
| Chili | adjudication des nouveaux entrants tous les deux ans, depuis 2010 | commission du gagnant : 1,14 %, 0,77 %, 0,47 %, 0,41 %, puis 0,69 % en 2018, 0,58 %, 0,49 %, 0,46 % en 2025 ; 1,36 % avant ; un gagnant a remonté de 0,47 à 1,16 % une fois libre |
| Suède | remise imposée aux gérants de la prime de pension, plafonds en 2015 et 2021 | frais moyen net de 0,31 % en 2013, 0,21 % en 2020, 0,13 % en 2022, 0,11 % en 2026 ; 0,45 % sans la remise |
| États-Unis | concurrence seule | fonds actions, pondérés par les encours : 1,04 % en 1996, 0,40 % en 2025, 3,3 % de baisse par an ; plans 401(k) : 0,76 % en 2000, 0,26 % en 2024 |
| Australie | produit par défaut MySuper, 2014 ; test de performance, 2021 | frais MySuper de 1,05 % à 1,00 % en 2023, « la plus forte baisse depuis 2014 » ; plus lent que les autres |
| France | concurrence des courtiers en ligne, transfert des PER | frais sur versement, mesuré sur les primes de l'année : PER 1,20 % → 1,09 %, assurance-vie 0,75 % → 0,55 % en deux ans ; frais de gestion, mesuré sur tout l'encours : 0,73, 0,77, 0,76 % |

Trois leçons, et le modèle les tient. **La baisse va par à-coups**, une
décision puis un plateau, d'où des paliers plutôt qu'une pente : le frais de
gestion suit le rythme américain, le seul observé sur trente ans, par marches
de dix ans (<!--chiffre:mesure(parametre?nom=frais_gestion_capitalisation)-->0,76<!--/-->, <!--chiffre:mesure(parametre?nom=frais_gestion_paliers.0.1)-->0,54<!--/-->, <!--chiffre:mesure(parametre?nom=frais_gestion_paliers.1.1)-->0,39<!--/-->, <!--chiffre:mesure(parametre?nom=frais_gestion_paliers.2.1)-->0,28<!--/-->, <!--chiffre:mesure(parametre?nom=frais_gestion_paliers.3.1)-->0,20<!--/--> % en 2066, le plancher de l'ERAFP) ;
le frais sur versement rejoint l'assurance-vie de 2025 en 2031, le contrat de
capitalisation en 2036, zéro en 2046 ; le frais sur arrérages, dont la médiane
est déjà nulle, s'éteint en 2046 ; le frais sur la réserve suit le rythme de
la gestion. **Elle porte sur les nouveaux dépôts, et un peu sur le stock** :
un frais de gestion est contractuel, l'OPEF le montre en deux ans, et les
lignes de l'échelle portent le tarif de leur cohorte, qui ne referme chaque
année que <!--chiffre:mesure(parametre?nom=convergence_frais_stock&echelle=100)-->10<!--/--> % de son écart avec le tarif du jour, la moitié en sept ans,
entre le contrat privé qu'on ne renégocie pas (0) et le plafond qui touche
tout le stock d'un coup (1), comme au Royaume-Uni et en Suède. **Elle n'est
pas acquise** : le Chili a vu la commission d'une caisse remonter de <!--chiffre:illustration()-->0,47<!--/--> % à
<!--chiffre:illustration()-->1,16<!--/--> % dès qu'elle a cessé d'être adjudicataire, et le modèle ne fait jamais
remonter un frais. Les paliers sont une hypothèse, datée et sourcée, pas une
mesure ; leurs années et leurs niveaux se changent en un endroit.

**Ce que chaque hypothèse déplace.** Rente mensuelle du pilier, les deux
cotisations réunies, pour un non-cadre né en 2004 qui cotise de 22 à 64 ans,
donc toute sa carrière après la bascule (le 20 septembre 2026, courbe du 17,
diviseur par niveau de vie) :

| Réglage | Rente | Écart |
|---|---|---|
| retenu : moyennes 2025 du marché, paliers, convergence 0,10 | 1 800 € | référence |
| PER 2025 tel que vendu, figé, sans frais de réserve, l'ancien réglage : 1,09 / 0,76 / 2,20 | 1 665 € | − 8 % |
| moyennes 2025 du marché figées, aucune baisse | 1 553 € | − 14 % |
| paliers, mais le stock garde son tarif, convergence 0 | 1 750 € | − 3 % |
| paliers, et tout le stock suit, convergence 1 | 1 832 € | + 2 % |
| retenu, sans frais sur la réserve de rente | 1 839 € | + 2 % |
| aucun frais | 2 035 € | + 13 % |

Pour un assuré né en 1985, qui liquide en 2049, les paliers ne sont encore
qu'à moitié parcourus : les moyennes figées lui coûtent 7 %, et le frais sur
la réserve, encore à 0,27 %, 4 %. Pour un assuré né en 1970, qui liquide en
2034, aucun palier n'est atteint, et le nouveau réglage sert 7 % de moins que
l'ancien, parce que le frais sur la réserve de rente (8 %) pèse plus que la
baisse des arrérages ne rend. Sur le total servi par le scénario 6, dont le
pilier pèse au plus deux cinquièmes, chaque hypothèse déplace donc de un à six
points. Le sens de chacune est connu, la taille est encadrée, et le choix
reste celui du paramètre.

**4. Aucun risque n'est simulé.** Le pilier est sans risque par construction,
et c'est un choix de proposition autant que de modèle : un régime obligatoire
qui promet une rente ne peut pas la gager sur des actions. Mais le modèle ne
dit rien de ce qu'un panachage aurait donné, ni de la volatilité qu'il aurait
fallu accepter pour cela. Il ne dit rien non plus du risque de crédit : la
courbe retenue est celle des souverains les mieux notés, pas celle de la dette
française, qui rendait <!--chiffre:illustration()-->51<!--/--> points de base de plus au dix ans
le jour de la courbe.

**5. Aucune fiscalité.** Les versements au PER sont déductibles du revenu
imposable, la rente est imposable à la sortie, et le capital transmis au décès
relève d'un régime successoral propre. Tous les montants du dépôt sont bruts,
et l'avantage fiscal à l'entrée — qui est une part réelle du rendement d'un PER
pour un contribuable imposé — n'est pas compté. Il joue en sens inverse des
points 1 et 2 : il minore la rente affichée.

**6. La garantie vieillesse compte la rente capitalisée, et la prend pour ce
qu'elle est.** Le programme a tranché le 19 septembre 2026 : une allocation
différentielle regarde toutes les ressources de retraite, la rente du pilier
comprise, volontaire comme obligatoire. Ce paragraphe a dit l'inverse jusqu'au
23 septembre 2026, bien après que le code l'eut réglé. Reste la manière de la
compter entre le départ et l'ouverture, puis année après année : la rente est
NOMINALE et constante, et les prix seuls la déprécient. La garantie la
revalorisait jusqu'à la même date comme la pension notionnelle, sur la masse
salariale, quand le compte des flux du pilier la servait nominale : deux
conventions pour la même rente, et un complément sous-estimé d'autant. La
rente prise nominale, et la règle du stock appliquée à la pension, ajoutaient
le jour du changement <!--chiffre:illustration()-->0,9<!--/--> milliard de 2026 à la garantie de 2070 et
<!--chiffre:illustration()-->33<!--/--> au cumul de 2026 à 2070.

Une dernière chose, qui n'est pas une limite mais une convention à connaître :
**l'espérance de capital transmis n'est pas conditionnée à la survie**. Elle se
lit de l'ouverture du pilier, et se rapporte donc à quelqu'un qui peut mourir
avant son départ, quand la rente affichée, elle, suppose qu'il l'atteint. Les
deux chiffres décrivent deux futurs, et leur somme n'a pas de sens.
