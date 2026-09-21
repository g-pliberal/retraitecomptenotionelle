# Ce qui a changé de côté

L'inventaire des avantages non contributifs décrit une liste à une date. Ce
document décrit son **déplacement** : ce qui n'était pas contributif et l'est
devenu, ce qui l'était et ne l'est plus, et le versant que le dépôt ne portait
nulle part — ce qui est **versé sans rien ouvrir**.

Quarante et un déplacements datés, de 1991 à 2026, vivent dans
`data/reference/legislation/frontiere_contributive.yaml`. Chacun porte
l'identifiant de la version d'article qui en fait foi, et
`python scripts/frontiere_contributive.py --verifier` rouvre l'index LEGI du
dépôt pour confronter les soixante-quatorze identifiants cités à ce que le dump
contient. Une date écrite sans version opposable serait une mémoire.

## 1. Le mot « contributif » en cache trois, et elles bougent séparément

C'est le résultat qui commande tous les autres. « Non contributif » désigne
trois choses que l'usage confond :

| Face | Ce qu'elle mesure | Qui la porte dans le dépôt |
|---|---|---|
| **droit** | ce que l'assuré ACQUIERT sans avoir cotisé | `avantages_non_contributifs.yaml`, et le modèle le calcule |
| **cotisation** | ce qu'il VERSE sans rien acquérir | personne, jusqu'ici |
| **financement** | QUI PAIE la charge, et si elle reste visible | les séries publiées, d'où viennent 87 % du total chiffré |

Elles ne se déplacent pas ensemble, et une ligne de l'inventaire suffit à le
prouver. Les **indemnités journalières de maternité** :

- le 11 novembre 2010, elles entrent au salaire de base de l'article L. 351-1
  (loi n° 2010-1330, article 98, pour les congés débutant en 2012) — face
  `droit` ;
- le même jour, le FSV en prend la charge au 10° de l'article L. 135-2 — face
  `financement` ;
- le 16 décembre 2020, ce 10° devient « (Abrogé) ». **Et la version de
  L. 351-1 qui les porte est toujours en vigueur.**

Le droit est intact ; sa trace comptable a disparu. Un lecteur qui mesurerait
les avantages non contributifs par les comptes du fonds verrait là une baisse
qui n'existe pas. C'est le risque propre aux lignes `serie_publiee` de
l'inventaire, et la raison pour laquelle une ligne ne doit jamais mélanger deux
périmètres — règle que le § 4 sexies de `avantages_non_contributifs.md` avait
déjà tirée d'une falaise à l'intérieur d'une série.

## 2. La liste existait déjà, et le législateur la tenait lui-même

Le dépôt emploie « non contributif » depuis sa première ligne sans en donner de
source. Elle existe.

> « Il est créé un fonds dont la mission est de prendre en charge les avantages
> d'assurance vieillesse **à caractère non contributif relevant de la
> solidarité nationale, tels qu'ils sont définis par l'article L. 135-2**. »
> — article L. 135-1 du code de la sécurité sociale, loi n° 93-936 du 22 juillet
> 1993, version `LEGIARTI000006740165`.

La définition est **énumérative** : n'est non contributif que ce qu'une liste
énumère. Et cette liste, l'article L. 135-2, a été tenue à jour **trente-sept
fois entre 1994 et 2025**. Chaque version est une photographie datée de la
frontière, prise par celui qui la déplace. C'est l'ossature de ce document :
là où l'inventaire du dépôt a été bâti en partant de ce que le modèle sait
faire, celle-ci a été écrite en partant de ce que le système paie.

Elle ne recouvre pas l'inventaire, et l'écart se lit dans les deux sens. La
liste légale ignore la réversion, les bonifications de service et les départs
anticipés des catégories actives — trois des postes les plus lourds — parce
qu'ils ne donnent lieu à aucun transfert. L'inventaire, lui, ignorait
l'apprentissage et les stages, qui y sont depuis 2014.

## 3. La liste disparaît le 1er janvier 2026

L'article 24 de la **loi n° 2025-199 du 28 février 2025** de financement de la
sécurité sociale abroge le chapitre « Fonds de solidarité vieillesse » et les
articles L. 135-1 à L. 135-5. Son XXII :

> « Les droits et obligations du Fonds de solidarité vieillesse sont dévolus à
> la Caisse nationale d'assurance vieillesse à compter du 1er janvier 2026. »

La liste survit au fonds : le même article crée **L. 222-2-1**, qui la reprend
dans la branche vieillesse et garde l'expression du législateur — « des
avantages non contributifs mentionnés aux 1° à 5° et 7° du présent article ».
Ce qu'il faudra relire, à partir de maintenant, n'est plus L. 135-2.

**Mais un mot a sauté, et il coûte cher.** Le 2° de L. 135-2 visait la prise en
compte des périodes assimilées « par **le régime général**, le régime des
salariés agricoles, … ». Le 2° de L. 222-2-1 vise « le régime des salariés
agricoles, le régime des non-salariés agricoles, le régime d'assurance
vieillesse des professions libérales et la Caisse nationale des barreaux
français ». Le régime général n'y est plus — non qu'il ait perdu quoi que ce
soit, mais parce qu'il a absorbé le fonds et ne se rembourse pas à lui-même.

Conséquence directe, et c'est une dette à inscrire : **à compter de 2026, le
coût des périodes assimilées du régime général cesse d'être un transfert publié
pour devenir une charge interne.** C'est le plus gros contingent de la ligne la
plus lourde que le modèle calcule. La série `periodes_assimilees` de
l'inventaire a désormais une date de péremption.

## 4. Le versant que le dépôt ne portait pas : cotiser sans rien acquérir

Un compte notionnel ne sert que ce qui a été cotisé. La question symétrique —
que cotise-t-on sans que rien ne soit servi ? — n'était posée nulle part, et
elle a deux réponses datées, lues dans le même article.

| Date | Ce que L. 241-3 ajoute | Version |
|---|---|---|
| 20 janvier 1991 | « des cotisations **à la charge des employeurs** et assises sur la totalité des rémunérations ou gains » | `LEGIARTI000006741899` |
| 22 août 2003 | la même phrase devient « à la charge des employeurs **et des salariés** » | `LEGIARTI000006741901` |

Le salaire au-delà du plafond ne peut entrer ni au salaire annuel moyen, ni
dans aucun droit. Ces cotisations n'achètent donc rien, par construction. Elles
sont non contributives au même titre qu'un trimestre gratuit, en sens inverse :
le lien entre le versement et le droit est rompu, du côté du versement.

**Et cela change la lecture des scénarios de ce dépôt.** `config.py` le dit
déjà en toutes lettres — « le compte notionnel porte ce qui a été PRÉLEVÉ, taux
d'appel compris » — et `taux_cotisation_annuels.csv` sépare `taux_plafonne` de
`taux_deplafonne`. Les scénarios notionnels rendent donc **contributif ce que le
droit actuel stérilise**. Une partie de l'écart qu'ils mesurent entre le système
actuel et un compte notionnel ne vient pas d'avantages gratuits en plus : elle
vient de cotisations rendues à leur cotisant. Ce n'était nommé nulle part.

### Le renversement de 2023, et la seule pension purement contributive du droit français

L'article **L. 161-22-1-1**, créé le 1er septembre 2023 par la loi n° 2023-270,
fait l'inverse : les cotisations du retraité qui reprend une activité, jusque-là
à fonds perdus, « se constituent de nouveaux droits à pension ». C'est la seule
bascule de ce fichier dans ce sens-là.

Deux phrases du même article méritent d'être lues pour elles-mêmes :

> « Seules sont retenues les périodes d'assurance ayant donné lieu à cotisations
> à la charge de l'assuré, à l'exclusion des périodes correspondant à des
> versements [rachats] […] Aucune majoration, aucun supplément ni aucun
> accessoire ne peut être octroyé au titre de cette nouvelle pension. »

C'est, en droit positif, **la définition d'une pension purement contributive** —
exactement l'objet que les scénarios 2 à 5 construisent par le calcul. Le
législateur l'a écrite pour une pension et une seule. Le champ n'est pas le
même et ce n'est donc pas une validation du modèle ; c'est le seul point du
droit français où la question que ce dépôt pose reçoit une réponse rédigée.

## 5. Ce que la chronologie montre, et qu'aucune liste ne montrait

`python scripts/frontiere_contributive.py --chronologie` range les vingt-quatre
bascules dans l'ordre du temps, faces mêlées. Deux asymétries en sortent.

**Du côté des droits, tout dépend du code que l'on lit — et c'est le résultat
le plus net de ce document.**

| | Ouvertures | Fermetures |
|---|---|---|
| Code de la sécurité sociale (privé) | **5** | 1 |
| Code des pensions civiles et militaires | 4 | **6** |
| Régimes spéciaux (SNCF, RATP) | 3 | 3 |

Dans le privé, **la frontière ne recule jamais**, et l'unique « fermeture » n'en
est pas une : c'est la seconde pension du cumul emploi-retraite, un objet neuf,
non un droit gratuit retiré à qui l'avait. Les cinq ouvertures sont l'entrée des
indemnités journalières au salaire de base (2010), les sportifs de haut niveau
(2011), les stages de formation professionnelle (2014), les travaux d'utilité
collective (2023) et le congé supplémentaire de naissance (2025). La liste des
périodes assimilées s'allonge par la fin, et aucun de ces ajouts n'a jamais été
repris.

Dans la fonction publique, l'inverse : **six fermetures contre quatre
ouvertures**, et les trois plus lourdes tombent le même jour. Le § 9 les
détaille. C'est une dissymétrie qu'aucune des deux listes ne montre seule, et
elle ne se voit qu'en lisant les deux codes avec la même grille.

Les régimes spéciaux, eux, sont à l'équilibre, et d'une façon qui leur est
propre : ils se sont fermés d'un coup, en 2008, aux entrants d'après, puis n'ont
plus fait que s'élargir pour ceux qui restaient. Le § 11 le raconte.

**Du côté du financement, la visibilité se referme, et c'est récent.** Dix
charges ont été isolées chez un payeur nommé, dont neuf avant 2015 ; six ont
été refondues dans les comptes des régimes, et cinq de ces six sont
postérieures à 2016 : le minimum contributif (2016), les indemnités
journalières (2020), le fonds lui-même, le régime général et la réduction pour
l'Afrique du Nord (2026). Le mouvement des trente premières années a rendu la
dépense lisible ; celui des dix dernières la rend progressivement opaque.

Un mot sur la façon de compter, parce qu'elle décide du résultat. Une bascule
est rangée sur la face que **la version citée prouve**, et non sur celle que son
sujet suggère. La validation des trimestres d'apprentissage est un droit
gratuit ; l'article lu, lui, ne dit que qui le paie, et la ligne est donc rangée
en `financement`. Le droit est à l'article L. 6243-3 du code du travail, que ce
document n'a pas lu. C'est plus sévère, et c'est la seule règle qui empêche un
inventaire de lectures de redevenir un inventaire de souvenirs.

### Un droit qui change quarante ans après coup

Le 9° de l'article L. 351-3, entré le 1er septembre 2023, valide « les périodes
de stage dont les cotisations sociales ont été prises en charge par l'État et
ayant pour finalité l'insertion dans l'emploi […] ainsi que celles mentionnées
à l'article 3 de la loi n° 79-575 du 10 juillet 1979 et à l'article L. 980-9 du
code du travail, dans sa rédaction antérieure ». Ce sont les **TUC** et les
stages assimilés des années 1980.

Des périodes qui ne validaient rien en sont devenues validantes,
**rétroactivement**, quarante ans plus tard. Le modèle date ses règles par
l'année de la période : il ne sait pas rejouer une validation décidée après
coup, et c'est une limite d'un genre que `docs/limites.md` ne portait pas — non
pas une règle mal appliquée, mais une règle dont la date d'effet n'est pas celle
qu'un modèle historique suppose.

## 6. Trois corrections que ces lectures apportent à l'inventaire

**La pénibilité a un payeur, et il est nommé dans la loi.** L'inventaire range
`incapacite_permanente_penibilite` en `absent` et lui donne pour raison
qu'aucun poste ne l'isole. Or L. 241-3 porte, depuis le 11 novembre 2010, une
contribution de la branche accidents du travail « couvrant les dépenses
supplémentaires engendrées par les départs en retraite à l'âge fixé en
application de l'article L. 351-1-4 ». Ce qui manque n'est pas la charge :
c'est sa publication.

**L'invisibilité de l'allocation veuvage s'explique.** L'inventaire dit qu'un
poste fourre-tout l'absorbe. La raison est plus profonde : c'est le seul droit
dérivé qui ait jamais eu **sa propre cotisation** — 0,10 % à la charge du seul
salarié, sur la totalité des rémunérations, article D. 242-5, dont l'unique
version court de 1985 au 25 août 2004. Elle a disparu avec la loi du 21 août
2003, qui a fondu « les charges de l'assurance vieillesse et de l'assurance
veuvage » dans les cotisations vieillesse. Un droit cesse d'être mesurable le
jour où il cesse d'avoir un payeur nommé.

**Le minimum contributif a été déclaré non contributif par le législateur, puis
ne l'a plus été.** Entré dans la liste du FSV le 22 décembre 2010 — « une
partie, fixée par la loi de financement de la sécurité sociale, des sommes
correspondant au service […] de la majoration mentionnée à l'article
L. 351-10 » —, porté à « au moins 50 % » en 2016, il en sort le 25 décembre de
la même année. C'est le seul cas de ce document où le modèle sait **mieux** que
les comptes : la cascade continue d'isoler son montant quand la série publiée
s'arrête.

## 7. Ce qui reste à faire

1. **Le versant `cotisation` est chiffré — voir le § 8**, qui a corrigé au
   passage une erreur écrite ici : ce qui manquait n'était PAS la distribution
   des salaires au-dessus du plafond. La cotisation déplafonnée porte sur la
   totalité de la rémunération, et sa masse est un produit de deux séries
   publiées. Reste à chiffrer la part sans droits de l'Agirc-Arrco, qui n'est
   connue qu'en proportion.
2. **La date de péremption de 2026 doit être inscrite.** Tant que les comptes
   de la protection sociale publient encore leurs sous-postes, rien ne bouge ;
   le jour où le régime général cesse d'apparaître comme bénéficiaire d'un
   transfert, la ligne `periodes_assimilees` change de nature. Il faut le voir
   venir plutôt que le constater.
3. **Les bascules de la fonction publique et des régimes spéciaux sont lues —
   § 9 et § 11.** Dix dans L. 12, L. 12 bis et L. 24 ; six dans les deux
   décrets du 30 juin 2008. Restent les autres caisses à règlement propre —
   IEG, Banque de France, Opéra, Comédie-Française —, dont aucune n'a encore
   été ouverte.
4. **La liste légale a été confrontée à l'inventaire — voir le § 10 —, et les
   deux dettes qu'elle a rapportées sont comblées.** L'apprentissage et la
   réduction pour l'Afrique du Nord ont leur ligne, leur base légale lue et
   leur raison écrite. Ni l'une ni l'autre n'est chiffrée, et aucune ne le sera
   par le modèle : la grille n'a ni apprenti ni ancien d'Afrique du Nord, et
   aucun poste publié ne les isole.


## 8. Combien : 17,9 milliards, et la correction d'une erreur écrite plus haut

Le § 7 posait que le versant `cotisation` était daté mais non chiffré, et
donnait pour obstacle la distribution des salaires au-dessus du plafond.
**C'était faux, et l'erreur valait un facteur dix.**

L'article D. 242-4 et la lettre même de L. 241-3 le disent : la cotisation
déplafonnée est assise sur **la totalité de la rémunération, dès le premier
euro** — et non sur la seule fraction supra-plafond. Elle n'ouvre aucun droit
pour autant, le salaire annuel de base étant borné au plafond par R. 351-29 et
les trimestres à quatre par an par R. 351-9. Aucune distribution n'est donc
nécessaire : la masse est le produit d'un taux par une assiette, et les deux
sont publiés.

### L'assiette, chez celui qui la recouvre

Elle ne pouvait pas venir des comptes nationaux, qui couvrent toute l'économie,
fonction publique comprise — laquelle ne relève pas de L. 241-3. L'Urssaf
publie la bonne, et sa note méthodologique la **définit** : « la masse salariale
correspond à l'assiette déplafonnée des cotisations sociales », champ secteur
privé, régime général, France entière, depuis 1997, série labellisée par
l'Autorité de la statistique publique. `scripts/fetch/urssaf_masse_salariale.py`
la récupère, et `data/reference/macro/masse_salariale_privee.csv` en porte
vingt-neuf années certifiées.

L'écart entre les deux séries n'est pas une nuance : 726 Md€ en 2024 chez
l'Urssaf contre environ 1 050 Md€ aux comptes nationaux. Les confondre
gonflerait la masse de 45 % sans que rien ne change d'allure, et un test du
dépôt tient désormais cet écart pour cette raison précise.

### Le résultat

`python scripts/frontiere_contributive.py --chiffrer` :

| Année | Assiette déplafonnée | Taux | Prélevé sans droits | dont salarié |
|---|---|---|---|---|
| 1997 | 305,9 Md€ | 1,60 % | **4,9 Md€** | 0,0 |
| 2005 | 418,3 Md€ | 1,70 % | **7,1 Md€** | 0,4 |
| 2015 | 526,4 Md€ | 2,10 % | **11,1 Md€** | 1,6 |
| 2023 | 703,0 Md€ | 2,30 % | **16,2 Md€** | 2,8 |
| 2025 | 740,0 Md€ | 2,42 % | **17,9 Md€** | 3,0 |

**17,9 milliards d'euros en 2025**, dont 3,0 à la charge du salarié. Le taux a
été relevé deux fois depuis 2023 — 2,42 % au 1er janvier 2024, 2,51 % au
1er janvier 2026 —, si bien que la série continuera de monter plus vite que
l'assiette.

### Un recoupement que rien n'avait préparé

La part salariale de ce prélèvement est **nulle jusqu'en 2004** et positive à
partir de 2005, dans une table certifiée construite depuis les décrets
d'application. Or la bascule du § 4 est datée du 22 août 2003, par la version de
L. 241-3 qui ajoute « et des salariés ». Les deux dates ne se contredisent pas :
**la loi autorise, le décret exécute**, et deux chemins indépendants — le texte
d'un côté, les taux appliqués de l'autre — se rejoignent à dix-huit mois près.
Le dépôt garde les deux, et un test tient l'écart, qui disparaîtrait sans bruit
si quelqu'un alignait l'une sur l'autre.

### La complémentaire : connue en proportion, pas en masse

La fiche réglementaire de l'Agirc-Arrco est explicite, et c'est le producteur
de la règle qui parle : « **Seule cette cotisation est génératrice de droits** »
— celle calculée au taux de calcul des points — et les deux contributions
d'équilibre de l'article 37 de l'ANI sont « **non génératrices de droits** ».

| Tranche | Acquisitif | Versé | Sans droits | Versé au-dessus du plafond | Sans droits |
|---|---|---|---|---|---|
| Tranche 1 | 6,20 % | 10,02 % | **38,1 %** | 10,37 % | **40,2 %** |
| Tranche 2 | 17,00 % | 24,29 % | **30,0 %** | 24,64 % | **31,0 %** |

**Près de deux euros sur cinq versés à la complémentaire sur la tranche 1
n'achètent aucun point** — le pourcentage d'appel de 127 % (article 36 de l'ANI)
et la contribution d'équilibre général. C'est trois fois plus, en proportion,
que la part sans contrepartie du régime de base. Le secrétariat général du COR
note que « ce mécanisme est peu connu des cotisants ».

Ce n'est pas une masse, et ce ne peut pas l'être ici : il faudrait la répartition
de l'assiette entre les deux tranches, que le dépôt n'a pas. Le rapport, lui,
est exact — il ne met en jeu que des taux publiés.

### Le mécanisme a changé de signe

Le pourcentage d'appel n'a pas toujours prélevé. Instauré en 1952 à l'Agirc, il
était **inférieur à 100 %** — 78 % en 1952, 95 % en 1965 — pour éviter de
constituer des réserves inutiles : le cotisant versait moins que le taux
contractuel et acquérait les points du taux entier. Il joue en sa faveur
jusqu'en 1978, atteint 125 % en 1992 à l'Arrco et en 1995 à l'Agirc, et 127 %
à la fusion. **Le même instrument a fait les deux.**

### Ce que ce total n'est pas

Un **plancher**, et il faut le dire avec le chiffre. Il ne porte que le régime
général : la complémentaire n'y entre qu'en proportion, et la fonction publique
pas du tout — le taux du compte d'affectation spéciale des pensions, 82,28 %
pour les civils au 1er janvier 2026 après deux relèvements de quatre points, est
fixé par décret pour **équilibrer** un compte, non pour acquérir un droit ; la
Commission des comptes de la sécurité sociale le nomme d'ailleurs « contribution
d'équilibre ».

Et il ne se soustrait de rien. Les 17,9 milliards ne viennent pas en déduction
des avantages non contributifs de l'inventaire : ce sont deux grandeurs de sens
opposé, sur deux faces différentes, et les compenser l'une par l'autre n'aurait
aucun sens — l'une dit ce que le système donne sans qu'on ait payé, l'autre ce
qu'on paie sans rien recevoir. Elles ne se rencontrent pas dans la même poche.

### Ce qui manque encore

Aucune **masse** de cotisation sans droits n'est publiée par les producteurs,
ni au régime général ni à l'Agirc-Arrco : ils publient les taux et le mécanisme.
Les 17,9 milliards sont donc un calcul du dépôt à partir de deux séries
publiées, et non un chiffre repris. Le seul montant qu'un régime publie
lui-même sur ce terrain est celui d'Agirc-Arrco — 27,6 Md€ de prestations
servies « au titre de la solidarité » en 2024, près de 30 % de ses pensions —,
mais il est de l'autre côté de la frontière, et il vient d'un communiqué, sans
décomposition ni compte audité.


## 9. La fonction publique : le seul endroit où la frontière a reculé

Dix bascules, lues dans trois articles du code des pensions — L. 12 pour les
bonifications, L. 12 bis pour la majoration de durée d'assurance, L. 24 pour
l'âge de liquidation. La recherche documentaire sur le web n'avait rien produit
sur ce terrain ; l'index LEGI du dépôt porte les versions, et la même méthode
que pour L. 135-2 y suffit.

### 2004 : l'année par enfant devient une année méritée

Le b de L. 12 disait « Bonification accordée **aux femmes fonctionnaires** pour
chacun de leurs enfants ». Il dit désormais « **les fonctionnaires et
militaires** bénéficient d'une bonification fixée à un an […] **à condition
qu'ils aient interrompu leur activité** », et seulement pour les enfants « nés
antérieurement au 1<sup>er</sup> janvier 2004 ».

Trois mouvements dans une seule version : le droit s'ouvre aux pères, se
referme sur une condition d'interruption, et s'éteint pour les naissances à
venir. Un an de services gratuits devient un an payé par une interruption de
carrière — c'est-à-dire par un coût réel supporté par le bénéficiaire. C'est,
de tout ce document, la seule fois qu'un avantage non contributif devient
**contributif au sens fort** : non pas cotisé, mais acquis contre quelque chose.

Le même jour, L. 12 bis crée le régime de remplacement : deux trimestres de
majoration de durée d'assurance, pour les enfants nés à compter de 2004, aux
femmes ayant accouché après leur recrutement. Quatre trimestres de moins qu'une
année, et un droit rendu à son caractère féminin après que le b venait de
l'ouvrir aux deux parents.

> **La différence entre les deux cases n'est pas de taille, elle est de
> nature.** Une bonification s'ajoute aux **services** et entre donc dans la
> liquidation ; une majoration de durée d'assurance ne compte que pour la
> durée, c'est-à-dire pour la décote et le prorata. Le même trimestre ne vaut
> pas la même chose selon la case où il tombe — et c'est exactement ce que la
> réforme de 2025 va déplacer.

### 2011 : trois fermetures le même jour

La loi du 9 novembre 2010 referme, dans les mêmes versions, trois droits
distincts :

- **le départ anticipé des parents de trois enfants disparaît**. L'expression
  « trois enfants » quitte l'article L. 24 à cette date et n'y est jamais
  revenue. C'est la seule extinction franche de tout ce fichier : non une
  restriction, une disparition ;
- **la catégorie active exige dix-sept ans de services actifs au lieu de
  quinze** — condition que la rédaction en vigueur reprend telle quelle ;
- **la bonification du cinquième des militaires exige dix-sept ans de services
  au lieu de quinze**. C'est la bonification la plus massive du système :
  99,3 % des pensions militaires liquidées en 2010 la portaient.

La même version ouvre pourtant d'un mot : la condition du b passe de
« interrompu » à « interrompu **ou réduit** » leur activité, ce qui étend le
droit à qui est passé à temps partiel sans jamais s'arrêter.

**Le départ des parents de trois enfants n'est dans aucune liste du dépôt.** Il
a vécu trente ans, il comptait parmi les avantages les plus connus de la
fonction publique, et l'inventaire des quarante-deux dispositifs ne le porte ni
sous un code ni sous une raison écrite. C'est un manque, signalé ici faute de
pouvoir le chiffrer.

### 2023 : un plafond et une libération, dans la même version

La réforme de 2023 ajoute à L. 12 une phrase qui n'existait pas — « Les
bonifications acquises […] pour services accomplis dans différents emplois
classés dans la catégorie active et la bonification prévue au i peuvent se
cumuler, **dans la limite de vingt trimestres** » — et en **supprime** une
autre, celle qui rabotait le cinquième des militaires d'une annuité par année
servie au-delà de cinquante-neuf ans.

Une fermeture et une ouverture dans la même version, en sens contraires. Une
réforme n'a pas de sens unique, et un inventaire qui ne noterait que les
fermetures mentirait autant qu'un autre qui ne noterait que les ouvertures.

### 2026 : un trimestre change de case, et la veille du dépôt avait raison de demander

Le registre de veille du dépôt portait depuis des mois une ligne `a_verifier` :
le décret n° 2026-699 crée « une bonification d'un trimestre pour chacun de
leurs enfants nés depuis le 1<sup>er</sup> janvier 2004 » aux femmes
fonctionnaires — **est-ce un ajout aux deux trimestres de L. 12 bis ?**

**Non, et le texte le dit lui-même.** La loi du 30 décembre 2025 insère un b ter
à L. 12 pour cette bonification d'un trimestre, et réécrit L. 12 bis le même
jour : les deux trimestres de majoration demeurent, « **dont l'un est pris en
compte au titre de la bonification prévue au b ter de l'article L. 12** ».

Le total ne bouge pas. Ce qui bouge est la **case** : un des deux trimestres
passe de la durée d'assurance aux services, où il entre dans la liquidation au
lieu de ne compter que pour la durée. Le même accouchement vaut davantage,
sans qu'aucune cotisation l'ait payé. C'est pourquoi ce document le compte deux
fois, en sens opposés — une ouverture à L. 12, une fermeture à L. 12 bis — :
les deux lignes décrivent le même geste vu des deux côtés, et ne s'additionnent
pas. Applicable aux pensions prenant effet à compter du 1<sup>er</sup> septembre
2026, et étendu à la CNRACL et au FSPOEIE à la même date par décret en Conseil
d'État — c'est le décret que la veille signalait.

### Ce que le modèle en fait, et ce qu'il n'en fait pas

Une seule de ces dix bascules est vraiment rejouée : le passage de la
bonification d'un an à la majoration de deux trimestres en 2004, que
`majoration_duree_assurance.csv` porte et que le moteur applique par date de
naissance. Pour le reste :

- **la condition d'interruption n'est pas opposée** — la grille de cas types ne
  porte pas d'interruption pour enfant, si bien que le modèle accorde la
  bonification là où le droit la refuserait. C'est un écart au droit positif, du
  côté généreux ;
- **la condition de dix-sept ans de services actifs n'est pas opposée** non
  plus : le moteur sert la catégorie active par la fiche du régime et une table
  d'âges. `veille.yaml` porte déjà cette lacune, à l'état `manque` ;
- **les bonifications de services ne sont pas servies du tout**, si bien que le
  plafond de vingt trimestres de 2023 n'a rien à plafonner.

### Une bascule qui n'en est pas une, et qu'il faut dire quand même

La réforme de 2023 a réécrit le départ de la catégorie active en termes
**relatifs** : non plus « cinquante-sept ans », mais « un âge anticipé égal à
l'âge mentionné au premier alinéa de l'article L. 161-17-2 du code de la
sécurité sociale **diminué de cinq années** », dix pour les services
super-actifs. L'âge absolu monte donc avec l'âge légal — mais **l'avantage, lui,
est intact** : cinq ans avant tout le monde, hier comme aujourd'hui.

Ce n'est donc ni une ouverture ni une fermeture, et ce fichier ne la compte pas.
Elle mérite pourtant d'être écrite : c'est le seul endroit où le droit a pris
soin de **protéger** un avantage non contributif contre une réforme qui
déplaçait tout le reste.


## 10. Ce que le législateur compte, et ce que le dépôt comptait

Le § 7 réclamait la confrontation de l'inventaire à la liste légale, poste par
poste, comme « le moyen le plus court de trouver ce qui manque encore aux
quarante-deux dispositifs ». Elle est faite, sur les huit postes de
l'article L. 222-2-1, et elle a rapporté **deux dettes**.

| Poste | Ce qu'il finance | Dans l'inventaire |
|---|---|---|
| 1° | Minimum vieillesse | `minimum_vieillesse` |
| 2° | Périodes assimilées, chômage, activité partielle | `periodes_assimilees` |
| 3° | *Abrogé* — réduction de durée pour l'Afrique du Nord (L. 351-7-1) | `reduction_duree_afrique_du_nord` |
| 4° | Points de complémentaire des préretraites et de l'ASS | `points_gratuits_complementaires` |
| 5° | Volontariat du service national | `service_national` |
| 6° | Mayotte | extension territoriale |
| 7° | Validation des trimestres d'apprentissage (L. 6243-3 code du travail) | `apprentissage` |
| 8° | Saint-Pierre-et-Miquelon | extension territoriale |

**L'apprentissage manquait, et il ne pouvait pas manquer autrement.** Son droit
n'est pas dans le code de la sécurité sociale mais dans celui du travail. Les
trois listes internes dont l'inventaire est né — les champs de
`Neutralisations`, les codes des fiches de régime, les lignes de la cascade —
décrivent toutes ce que le MODÈLE sait faire ; aucune ne pouvait aller chercher
un article de L. 6243-3. C'est le même défaut que le § 4 sexies avait relevé en
trouvant trois dispositifs dans la nomenclature des comptes : **partir de ce
qu'on calcule ne mène jamais à ce que le système verse.**

**Les deux dettes sont comblées**, et la seconde n'était pas ce qu'on croyait.
Le 3° parlait de « réductions de la durée d'assurance ou de périodes reconnues
équivalentes, définies à l'article L. 351-7-1 » ; l'article, lu, vise les
**services militaires actifs accomplis en Afrique du Nord**, et leur ouvre une
réduction de la durée requise pour le taux plein. Ce n'est ni un trimestre
gratuit ni un âge abaissé : c'est la cible qui recule, ce qui revient au même
pour l'assuré et ne se lit sur aucune ligne de sa pension.

**Et il démontre une troisième fois la thèse du § 1.** Le poste qui le finançait
est abrogé au 1<sup>er</sup> janvier 2026 ; la version de L. 351-7-1 en vigueur
depuis 2017 n'a pas bougé. Après les indemnités journalières de maternité (2020)
et le minimum contributif (2016), c'est le troisième droit qui survit à son
financement. Trois fois, la même illusion serait possible : lire la fin d'un
transfert comme la fin d'un droit.

L'inventaire compte désormais **quarante-cinq dispositifs**.

### Le poste qu'on n'attendait pas : la branche paie une complémentaire

Le 4° renvoie à l'article 49 de la loi de modernisation sociale de 2002, dont
le texte est explicite : la branche verse chaque année **aux organismes de
l'article L. 921-4** — c'est-à-dire à l'Agirc-Arrco — les cotisations dues au
titre des périodes de préretraite du Fonds national pour l'emploi, de
préretraite progressive, d'allocation de solidarité spécifique et d'allocation
équivalent retraite.

L'inventaire rattachait les points gratuits de complémentaire aux seuls accords
Agirc-Arrco. Une partie d'entre eux est payée par la branche vieillesse, sous
un article de loi, depuis 1999 pour les plus anciens. Le dispositif était dans
l'inventaire ; son payeur n'y était pas.

### La liste des périodes financées n'est pas celle des périodes validées

C'est la trouvaille la plus utile de la confrontation, et elle se lit dans un
seul mot du 2°. L'article L. 351-3 valide neuf catégories de périodes ; le
poste qui les finance n'en vise que **trois** — les 1°, 3° et 8° —, plus les
allocations de chômage et d'activité partielle.

Restent donc à la charge des régimes, sans transfert ni payeur nommé : les
périodes de guerre (5°), la détention provisoire (6°), **les sportifs de haut
niveau (7°) et les travaux d'utilité collective (9°)** — c'est-à-dire, très
exactement, les deux droits les plus récemment ouverts, ceux que le § 5 relevait
comme les derniers ajouts à une liste qui ne se referme jamais.

**Un droit gratuit sans payeur nommé est un droit qu'aucune série ne
chiffrera.** Le § 6 disait déjà cela de l'allocation veuvage, qui avait eu sa
cotisation et l'a perdue. On le voit ici à l'endroit : le législateur ouvre un
droit, et choisit de ne pas le financer à part. Les deux mouvements de ce
document — l'ouverture des droits et la refonte des financements — ne sont pas
seulement simultanés, ils se répondent.


## 11. Les régimes spéciaux : fermés une fois, élargis depuis

Les bonifications de service de la SNCF et de la RATP ne sont pas dans le code
de la sécurité sociale ni dans celui des pensions : elles vivent dans deux
décrets jumeaux du 30 juin 2008, l'un par régime, que l'index du dépôt porte
avec toutes leurs versions.

**Elles se ferment le jour même où elles sont réécrites.** La rédaction
initiale de l'article 9 du décret SNCF réserve la bonification de conduite —
un trimestre par année au-delà de la troisième, vingt au plus — aux
« personnels dont l'admission au cadre permanent de la SNCF a été prononcée
**avant le 1<sup>er</sup> janvier 2009** ». L'article 20 du décret RATP fait de
même pour le cinquième du tableau B. Le droit demeure entier pour qui l'avait ;
il n'existe plus pour personne d'autre.

Il n'y a pas de version antérieure à citer : ces décrets remplacent des
règlements de caisse que l'index ne porte pas sous ces numéros d'article. La
fermeture se lit donc dans le texte qui l'institue, non dans l'écart entre deux
versions — c'est le seul cas de ce fichier où il en va ainsi, et la ligne le
dit.

**Puis elles ne font plus que s'élargir**, trois fois en dix-huit ans, et pour
ceux-là seuls qui restaient :

| Date | Ce qui s'ouvre | Texte |
|---|---|---|
| 3 décembre 2020 | les périodes d'**activité partielle** comptent comme du service | décret n° 2020-1489 |
| 1<sup>er</sup> janvier 2025 | la RATP étend le tableau B aux « emplois **équivalents** » | décret n° 2023-690 |
| 7 août 2026 | le **congé de mobilité** compte lui aussi, à la SNCF | décret n° 2026-738 |

La première mérite qu'on s'y arrête. Le décret du 1<sup>er</sup> décembre 2020
ajoute que les périodes d'indemnité d'activité partielle « sont prises en compte
pour le calcul de ces bonifications », à compter du 1<sup>er</sup> mars 2020.
Un mois de chômage partiel vaut donc un mois de conduite, pour un droit qui n'a
jamais été cotisé. **La crise sanitaire a élargi un avantage non contributif
sans que personne ne l'ait décidé comme tel**, et rien dans le décret ne le
présente ainsi.

La dernière est le déplacement le plus **récent** que ce document porte, toutes
faces confondues — et il va, comme presque tous ceux du côté des droits, dans le
sens de l'élargissement.

**Une seule fermeture leur est venue d'ailleurs.** Au 1<sup>er</sup> janvier
2017, la même phrase entre dans les deux décrets : les bonifications ne sont
prises en compte « que dès lors que la pension rémunère au moins quinze années
de services effectifs ». C'est la condition que le code des pensions avait reçue
six ans plus tôt, en 2011, pour ses propres bonifications. Les réformes de la
fonction publique et celles des régimes spéciaux ne sont pas simultanées, mais
elles se suivent — et le décalage est ici de six ans exactement.

**Le modèle n'en sert aucune.** L'inventaire range
`bonifications_regimes_speciaux` en `absent`, et le § 4 sexies de
`docs/avantages_non_contributifs.md` a déjà relevé pourquoi : les fiches de la
SNCF et de la RATP déclarent le code `bonifications` depuis toujours, mais le
moteur le lit comme la bonification pour enfants de la fonction publique.
Aucune de ces six bascules ne change donc un euro calculé. Elles disent
seulement, avec des dates, ce que le modèle ne fait pas.

---

Voir aussi : `docs/avantages_non_contributifs.md` pour l'inventaire et son
chiffrage, `docs/veille_droit.md` pour l'obligation de lecture des sources,
`docs/limites.md` pour les écarts au droit positif.
