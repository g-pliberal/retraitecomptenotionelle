# Le message étudié aux sources : ce que chaque électorat gagne, et ce qui ne se promet pas encore

**Reprise, au 7 novembre 2026.** Le chantier 8 est étudié et tranché le
même jour : décisions 31 à 33 de `docs/feuille_de_route_programme.md` (la
faute, le pilier à l'assuré, l'apport pour un premier logement). Reste
l'âge : le propriétaire veut le chiffre avant de choisir. Par quoi
commencer : une session du modèle mesure un âge plancher de 62 ou 64 ans, la
pension étant celle du compte, face aux 65 ans de la proposition. Le gain
des actifs en euros attend la lecture A ou B du chantier 1, le message des
retraités les pertes du chantier 2, et le test des vingt personnes, les deux.

*Le 7 novembre 2026, le propriétaire ouvre le chantier 8 de l'action 186,
« Le message » : « Je veux qu'on attaque ce chantier ». La session relit
chacune des pistes du 6 novembre à sa source, lit dans le modèle ce que vaut
chaque gain promis, et le confronte aux décisions déjà prises. Ce que la note
conclut est une piste, pas une décision : le chantier est tout entier au
propriétaire. Les chiffres portent leur origine : **(modèle)**, le modèle du
dépôt au commit `697d1b7` ; **(dépôt)**, un document du dépôt qui cite sa
source ; **(lu)**, une source ouverte et lue ce jour ; **(relevé)**, un fait
trouvé par recherche dont le texte n'a pas été ouvert, à relire au
chantier 7 avant toute publication.*

## L'essentiel : trois gains se chiffrent, trois ne se promettent pas tels quels

**Les actifs gagnent en salaire net, et sa taille suit le chantier 1.** Aux
taux de la proposition (18 % et 5 % capitalisés), sous le partage tranché le
20 septembre 2026, le gain est positif à tous les salaires : **+39 € par
mois au SMIC, +87 à 1,2 SMIC, +175 à deux SMIC, +417 à cinq SMIC** (modèle).
La décision 29, prise le même jour, rend aux cotisants dès la bascule une
part de ce que la baisse des pensions économise, selon deux lectures que le
chantier 1 refait au modèle (`186/2026-11-07-deux-lectures-et-reprise.md`).
Le gain en euros se chiffre une fois la lecture choisie ; le message
« chaque euro cotisé ouvre des droits » vaut, lui, dès le premier jour.

**Un pilier capitalisé « protégé par la loi » ne l'est pas par une loi.**
Dix-huit des trente pays qui avaient privatisé leurs retraites sont revenus
en arrière ; la Pologne a repris en 2014 la moitié des actifs de ses fonds,
et son Tribunal constitutionnel l'a validé, les fonds étant des « fonds
publics » ; la France elle-même a fait verser à la Cades, de 2011 à 2024,
2,1 Md€ par an du Fonds de réserve pour les retraites. Ce qui protège, c'est
la propriété individuelle de l'épargne, pas une promesse du législateur.

**« L'apport pour un premier logement, comme en Suisse » existe déjà en
France**, pour l'épargne volontaire du PER, mais pas pour ses versements
obligatoires. L'étendre aux cinq points capitalisés, c'est faire ce que fait
la Suisse sur son deuxième pilier obligatoire, au prix d'une retraite plus
faible.

**« La liberté de l'âge » contredit l'âge légal de 65 ans** que la
proposition fixe depuis le 23 septembre 2026. Le compte actuariel la permet ;
la proposition ne la donne pas.

**Le plancher n'est pas un gain de niveau pour les retraités** : la garantie
vieillesse vaut l'ASPA à quelques euros près, et un peu moins pour un couple.
Leurs gains réels sont ailleurs — la garantie individualisée, servie
d'office, et les réversions déjà servies, gardées —, et la reprise de la
garantie sur la succession, que la décision 30 garde, doit se dire avant
qu'un adversaire ne la dise.

**L'injustice ne se voit pas, et cela commande le ton.** Le niveau de vie
des retraités est équivalent à celui de l'ensemble de la population, l'un
des plus élevés des pays que suit le COR ; mais 49 % des Français le croient
moins bon, et les plus modestes le croient plus souvent que les autres.
Désigner une génération serait entendu comme attaquer des gens que l'on
croit pauvres ; montrer le chiffre, et le manque de courage de trente ans,
ne l'est pas.

## Les actifs : le salaire net, un compte, un pilier, un logement

### Le salaire net, en euros par mois

Le gain que le modèle calcule pour un salarié du privé non cadre en 2026, à
coût du travail constant (l'incidence que l'action 38 a retenue), avec le
taux unique de 18 % et les 5 % capitalisés, partagés comme le programme l'a
tranché le 20 septembre 2026 — l'employeur garde ses 16,67 points, l'assuré
passe de 11,31 à 6,33 (`tests/test_remuneration.py`) :

| Salaire brut | 1 SMIC | 1,2 SMIC | 1,5 SMIC | 2 SMIC | 3 SMIC | 5 SMIC |
|---|---|---|---|---|---|---|
| Gain net, € par mois | +39 | +87 | +121 | +175 | +269 | +417 |
| À brut inchangé, € par mois | +91 | +109 | +136 | +182 | +262 | +406 |

(modèle, `remuneration.py` par les aides de `tests/test_remuneration.py`,
SMIC annuel de 2026 : 21 876 €.)

Trois choses à dire avec ces chiffres. *Un*, ils valent aux taux de la
proposition ; le gain du message sera celui de la lecture du chantier 1 que
le propriétaire retiendra, à chiffrer par la même fiche de paie du modèle.
Et sur un compte notionnel, la cotisation d'aujourd'hui est la pension de
demain : un point rendu au salaire est un point de moins crédité au compte,
et le message doit dire les deux. *Deux*, le gain est faible au SMIC
parce que la réduction générale y efface déjà toute la part patronale :
l'action 38 l'avait trouvé négatif (−38 € par mois) avant le partage du
20 septembre, qui l'a rendu positif partout. *Trois*, les cinq points
capitalisés ne sont pas dans le gain, et ils ne sont pas perdus : ils vont à
un compte au nom de l'assuré.

Un autre gain, d'une autre nature, ne dépend d'aucune lecture : la
cotisation vieillesse déplafonnée, 17,9 Md€ en 2025, n'ouvre aujourd'hui
aucun droit (dépôt, `docs/musee_des_horreurs.md`) ; sur un compte notionnel,
tout euro versé est crédité. Le message « chaque euro cotisé est à vous »
vaut dès le premier jour ; le gain en euros par mois, une fois la lecture
du chantier 1 choisie.

### Un compte à leur nom

La Suède envoie chaque année, depuis 1999, l'« enveloppe orange » : le solde
du compte de chacun. Environ 90 % des Suédois la connaissent, 75 % de
ceux-là disent en lire une partie, mais la connaissance du système n'a pas
progressé après son introduction (Larsson, Paulsson, Sundén et Takayama,
2011, et une étude de 2020 qui ne trouve qu'un petit effet ; relevé, d'après
[Journal of Pension Economics and Finance, 2020](https://doi.org/10.1017/S1474747220000232)
et [INAPP, 2019](https://oa.inapp.gov.it/bitstreams/a8bb1dfc-58c8-441a-9369-e199d81f5073/download)).
Le compte à son nom est un argument de liberté, pas une pédagogie : il ne
s'explique pas tout seul, et le site doit le faire. En France, le relevé de
situation individuelle existe déjà ; ce qui est neuf, c'est un solde en
euros qui vaut une pension.

### Un pilier capitalisé « protégé par la loi »

Le dépôt a déjà lu ces précédents (`docs/risque_de_defaut.md`, « La reprise
des fonds capitalisés ») :
- sur trente pays qui avaient privatisé entre 1981 et 2014, **dix-huit ont
  fait marche arrière**, dont l'Argentine en 2008 (environ 25,5 milliards de
  dollars, 9,5 % du PIB), la Hongrie en 2010, la Pologne en 2011 et 2014
  (OIT, *Reversing Pension Privatizations*, 2018 ; dépôt, lu) ;
- **la Pologne a transféré en 2014 51,5 % des actifs de ses fonds**, toutes
  leurs obligations d'État (Naczyk et Domonkos, *Governance*, 2016 ; dépôt,
  lu). La piste du 6 novembre disait « la moitié », à vérifier : c'est
  vérifié ;
- son **Tribunal constitutionnel l'a validé le 4 novembre 2015** (K 1/14) :
  les fonds sont des « fonds publics » (dépôt, résumé) ;
- « plus le niveau de dette publique et l'exposition des fonds aux
  obligations domestiques sont élevés, plus l'incitation et la capacité
  technique à nationaliser sont grandes » (Naczyk et Domonkos ; dépôt, lu).

Le précédent français manquait au dépôt. **Le Fonds de réserve pour les
retraites**, créé en 1999 pour amortir le surcoût des retraites après 2020 et
doté de 28 Md€ jusqu'en 2010, verse depuis la réforme de 2010 **2,1 Md€ par
an à la Cades, jusqu'en 2024** (lu, [COR, séance du 11 juillet 2018,
document 4319](https://www.cor-retraites.fr/sites/default/files/2019-06/doc-4319.pdf)) :
une réserve des retraites, votée pour elles, mise au remboursement de la
dette sociale.

D'où la piste : **une loi ne protège pas d'une loi suivante ; la propriété,
davantage.** Un fonds public, même cantonné, se reprend par un vote ; une
épargne inscrite au nom de chacun, dans un contrat qui lui appartient, est un
bien que protègent l'article 17 de la Déclaration de 1789 et l'article 1 du
Protocole n° 1 de la CEDH. Et un pilier qui ne se place pas d'abord en dette
française tente moins l'État qui la doit. La promesse se tient par la
conception du pilier, pas par sa protection légale. Ce que la proposition
fait aujourd'hui des cinq points — un compte au nom de l'assuré, qui se
transmet (action 38), aux frais moyens du PER individuel
(`docs/limites/5-ante-capitalisation.md`) — va dans ce sens ; la forme
juridique du compte n'est écrite nulle part.

### L'épargne retraite comme apport pour un premier logement

- **En Suisse**, l'encouragement à la propriété du logement permet de
  retirer son avoir du deuxième pilier, le pilier obligatoire, pour acheter
  son logement : 20 000 francs au moins, jusqu'à trois ans avant l'âge de la
  retraite ; les prestations de vieillesse et de risque baissent d'autant
  (relevé, ordonnance OEPL, art. 5, et [OFAS](https://sozialversicherungen.admin.ch/fr/d/6946/download)).
  Combien de Suisses s'en servent, la recherche ne l'a pas trouvé.
- **En France, le PER le permet déjà** : l'acquisition de la résidence
  principale est l'un des six cas de sortie anticipée de l'article L. 224-4
  du code monétaire et financier, pour les versements volontaires et
  l'épargne salariale, pas pour les versements obligatoires (relevé, texte
  non ouvert ; [Allianz](https://www.allianz.fr/assurance-particulier/epargne-retraite/retraite/conseils-pratiques/deblocage-per.html),
  [Groupama](https://manouvellevie.groupama.fr/se-preparer/completer-retraite-solutions-epargne-retraite/deblocage-per)).
  Le motif n'est pas réservé au premier achat.

Annoncer « l'épargne retraite comme apport, comme en Suisse » serait donc
annoncer, pour l'essentiel, ce qui existe : un adversaire le relèverait. Ce
que le programme ajouterait, c'est de l'ouvrir aux **cinq points
obligatoires** — c'est le choix suisse —, ce qui sert le logement des jeunes,
l'un des deux vrais problèmes du diagnostic, au prix d'une pension
capitalisée plus faible pour qui s'en sert. Une question au propriétaire.

## Les 45-62 ans : les droits acquis, et l'âge

*Les droits acquis* : la décision 2 n'épargne que les droits cotisés ; le
compte notionnel rétroactif les crédite tous (scénario 4). Le message tient,
à une condition : que le compte de chacun soit calculable et montré, ce que
le simulateur fait déjà.

*La liberté de l'âge* : la proposition fixe **un âge légal de départ de
65 ans** à compter de 2026 (dépôt, `README.md`, « Enfin, un âge légal de
départ de 65 ans ») ; il a fait passer le solde moyen 2026-2070 de la
variante rétroactive de −1,39 à −0,87 point de PIB, le 23 septembre 2026
(dépôt, `docs/chiffrage_plf.md`). Promettre « la liberté de l'âge » à côté de
65 ans serait une contradiction qu'un adversaire verrait le premier jour.

Le modèle de la liberté de l'âge est la Suède : la pension de revenu se
prend au plus tôt trois ans avant l'« âge cible », soit à 64 ans en 2026, cet
âge étant de 67 ans, et en partie (un quart, la moitié, les trois quarts) ;
la garantie se touche à l'âge cible (relevé, Pensionsmyndigheten,
[« Att ta ut pension », 2026](https://www.pensionsmyndigheten.se/content/dam/pensionsmyndigheten/blanketter---broschyrer---faktablad/broschyrer-och-faktablad/faktablad/2025/PM-7624-Att-ta-ut-pension-26-01.pdf)).
Un compte actuariel rend l'âge neutre pour le régime : partir tôt donne une
pension plus faible, sans coût pour les autres. L'âge plancher n'y protège
que deux choses : le budget pendant la transition, et l'assuré contre une
pension trop faible, qui tomberait à la garantie. Le choix est entre deux
messages cohérents : « 65 ans, comme nos voisins » ou « partez quand vous
voulez à partir de 64 ou 62 ans, votre pension est celle de votre compte » —
pas les deux.

## Les retraités : le plancher, la garantie, la réversion

*Le plancher* : la garantie vieillesse vaut **1 050 € par mois pour une
personne seule, 1 600 € pour un couple** (dépôt, `docs/methodologie.md`,
scénario 6) ; l'ASPA vaut **1 043,59 € et 1 620,18 €** en 2026 (dépôt,
`data/sources.yaml`, `service_public_aspa`, certifié). Le plancher n'est pas
un gain de niveau : 6 € de plus pour une personne seule, 20 € de moins pour
un couple d'allocataires.

*Les gains réels* sont trois :
- **l'individualisation** : un couple de 300 € et 1 500 € ne touche rien de
  l'ASPA, qui compte le foyer, et 500 € par mois de la garantie (dépôt,
  `docs/methodologie.md`) — un gain pour le conjoint de petite pension, à
  montrer ;
- **la garantie servie d'office** (décision 20) : le dépôt suppose, d'après
  la DREES, que la moitié seulement des ayants droit réclament l'ASPA
  (`taux_recours_garantie`) ; la servir sans demande double, à peu près, ceux
  qui la touchent ;
- **les réversions déjà servies, gardées jusqu'à extinction** (décision 16) :
  4,4 millions de survivants, dont 886 000 n'ont pas d'autre pension
  (`186/2026-11-07-reversion-etude-et-couts.md`).

*Ce qui les menace* : le scénario 6 reprend la garantie **sur la succession
dès le premier euro, avec intérêts**, quand l'ASPA n'est reprise qu'au-delà
d'un seuil d'actif net (dépôt, `docs/methodologie.md`). Le propriétaire l'a
gardée le même jour (décision 30) : c'est le remboursement d'une avance, sur
la seule valeur de l'aide, pas un impôt sur l'héritage. La règle est
tranchée ; reste la façon de la dire, parce qu'un adversaire dira « la
garantie servie d'office, que vos enfants rembourseront sur la maison », et
qu'un retraité modeste propriétaire de son logement l'entendra ainsi. Le
message doit le dire avant lui, dans les termes de la décision : une avance,
qui ne reprend que ce qu'elle a versé, jamais plus que la succession, et
jamais rien de la poche des héritiers ; et il ne peut pas taire qu'elle est,
sur ce point, plus dure que l'ASPA.

*Ce qui manque* : qui perd, et combien, chez les retraités d'aujourd'hui (le
chantier 2). Le chantier 2 le dit déjà : « si la retraitée médiane perd
lourdement, ne pas prétendre le contraire ». Le message des retraités ne
s'écrit pas avant.

## La responsabilité : une génération, ou trente ans sans courage

Le COR, le 5 février 2026 : le niveau de vie des retraités « est équivalent à
celui de l'ensemble de la population, ce qui en fait l'un des plus élevés
parmi les pays suivis par le COR. Ce constat est en décalage avec les
opinions : 49 % des enquêtés évaluent le niveau de vie moyen des retraités
comme étant moins bon que celui de l'ensemble de la population, contre
seulement 20 % qui l'évaluent comme meilleur » (lu, [COR, dossier en bref du
5 février 2026, p. 1](https://www.cor-retraites.fr/sites/default/files/2026-02/Dossier%20en%20bref_05.02.2026.pdf)).
Le document de travail qui l'étaye ajoute deux faits (lu, [COR, document
n° 5](https://www.cor-retraites.fr/sites/default/files/2026-02/Doc_05_Opinions%20sur%20niveau%20vie_SGCOR.pdf),
d'après le baromètre d'opinion de la DREES 2024) :
- les personnes des deux premiers quintiles de niveau de vie croient plus
  souvent que les autres les retraités moins bien lotis : chacun « projette
  sa situation sur celle des autres » ;
- 54 % des non-retraités pensent que leur niveau de vie à la retraite sera
  inférieur à celui de l'ensemble de la population.

Trois conséquences pour le message, qui confirment la piste du 6 novembre :
1. **L'injustice que décrit le diagnostic est réelle et invisible** : c'est
   un argument pour la montrer chiffrée, à la source du COR, pas pour
   l'affirmer.
2. **Accuser le baby-boom serait entendu comme accuser des pauvres**, et
   d'abord par l'électorat modeste que le fil vise, qui croit les retraités
   plus pauvres qu'ils ne sont, et dont ce sont les parents.
3. **Le manque de courage politique** — les mots du propriétaire — désigne
   des décisions, pas des personnes : « on a toujours fait payer les
   cotisants sans toucher aux droits passés ». Il s'appuie sur des faits du
   dépôt (les 17,9 Md€ cotisés sans droits ; le Fonds de réserve détourné) et
   laisse aux retraités modestes leur place dans le fil.

Et les jeunes partagent le pessimisme : 54 % s'attendent à être moins bien
lotis à la retraite. Le compte à leur nom répond à cette crainte-là.

## Tester avant de publier

La piste : une vingtaine de personnes réelles, retraités compris, deux
questions — qu'ont-elles compris, pensent-elles y gagner. Ce qui conditionne
le test :
- **le matériel** : une page ou un tract par électorat, avec ses chiffres ;
  ceux des actifs attendent le chantier 1, ceux des retraités le chantier 2 ;
- **la méthode** : des entretiens un à un plutôt qu'un groupe, où les
  premiers avis entraînent les suivants ; la personne reformule d'abord ce
  qu'elle a lu, puis dit si elle y gagne, et l'on note l'écart entre ce
  qu'elle croit et ce que le modèle calcule pour elle ;
- **qui le mène** : le propriétaire ou le parti, pas une session ; une
  session peut préparer le matériel et la grille.

## Ce que le propriétaire tranche

1. **La responsabilité** : le manque de courage politique de trente ans (la
   piste), la génération du baby-boom, ou les deux.
2. **L'âge** : garder 65 ans et ne pas promettre la liberté de l'âge, ou
   ouvrir un départ libre plus tôt, la pension étant celle du compte.
3. **Le pilier capitalisé** : un compte qui appartient à l'assuré (la piste),
   ou un fonds public cantonné par la loi.
4. **Le logement** : ouvrir les cinq points obligatoires à l'apport, comme en
   Suisse, ou laisser le pilier à la retraite, le PER volontaire le
   permettant déjà.
Deux autres suivent les chantiers 1 et 2 :

5. **Le gain des actifs**, en euros par mois, se chiffre sous la lecture A ou
   B de la décision 29, quand le propriétaire l'aura choisie.
6. **Le message des retraités** attend qui perd, et combien (chantier 2) ; la
   reprise sur la succession, tranchée (décision 30), s'y dit comme une
   avance remboursée sur la seule valeur de l'aide.

Le test des vingt personnes attend les deux.

## Ce que le propriétaire a tranché, le même jour

Aux quatre questions, posées une à une avec leurs options :
- *La faute* : « Les deux, nuancé » — le manque de courage politique de
  trente ans d'abord ; le poids électoral du baby-boom comme explication,
  jamais comme accusation (décision 31).
- *Le pilier* : « Un compte à l'assuré » — un contrat à son nom, comme un
  PER, protégé comme un bien (décision 32).
- *Le logement* : « Oui, premier logement seul » — les cinq points
  obligatoires s'ouvrent à l'apport pour le premier achat de la résidence
  principale ; le plafond reste à fixer (décision 33).
- *L'âge* : « Chiffrer avant de choisir » — une session du modèle mesure ce
  que coûterait un âge plancher de 62 ou 64 ans, la pension étant celle du
  compte actuariel, face aux 65 ans de la proposition ; le propriétaire
  tranche ensuite.
