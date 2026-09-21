# Ce qui a changé de côté

L'inventaire des avantages non contributifs décrit une liste à une date. Ce
document décrit son **déplacement** : ce qui n'était pas contributif et l'est
devenu, ce qui l'était et ne l'est plus, et le versant que le dépôt ne portait
nulle part — ce qui est **versé sans rien ouvrir**.

Vingt-quatre déplacements datés, de 1991 à 2026, vivent dans
`data/reference/legislation/frontiere_contributive.yaml`. Chacun porte
l'identifiant de la version d'article qui en fait foi, et
`python scripts/frontiere_contributive.py --verifier` rouvre l'index LEGI du
dépôt pour confronter les quarante identifiants cités à ce que le dump
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

**Du côté des droits, la frontière ne recule pas.** Cinq ouvertures contre une
fermeture, et la fermeture n'en est pas une : c'est la seconde pension du cumul
emploi-retraite, un objet neuf, et non un droit gratuit retiré à qui l'avait.
Les cinq ouvertures sont l'entrée des indemnités journalières au salaire de base
(2010), les sportifs de haut niveau (2011), les stages de formation
professionnelle (2014), les travaux d'utilité collective (2023) et le congé
supplémentaire de naissance (2025). **La liste des périodes assimilées s'allonge
par la fin, et aucun de ces ajouts n'a jamais été repris.**

**Du côté du financement, la visibilité se referme, et c'est récent.** Dix
charges ont été isolées chez un payeur nommé, dont neuf avant 2015 ; cinq ont
été refondues dans les comptes des régimes, et quatre de ces cinq sont
postérieures à 2016 — le minimum contributif (2016), les indemnités
journalières (2020), le fonds lui-même et le régime général (2026). Le
mouvement des trente premières années a rendu la dépense lisible ; celui des
dix dernières la rend progressivement opaque.

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
3. **Les bascules de la fonction publique manquent.** Ce document lit le code
   de la sécurité sociale ; la bonification pour enfants du code des pensions,
   restreinte aux enfants nés avant 2004 et conditionnée à une interruption
   d'activité, est un déplacement de frontière de la même nature et n'y est pas.
4. **La liste légale doit être confrontée à l'inventaire, poste par poste.** Le
   § 2 dit que les deux ne se recouvrent pas ; personne n'a encore fait le
   tableau des deux côtés, et c'est le moyen le plus court de trouver ce qui
   manque encore aux quarante-deux dispositifs.


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

---

Voir aussi : `docs/avantages_non_contributifs.md` pour l'inventaire et son
chiffrage, `docs/veille_droit.md` pour l'obligation de lecture des sources,
`docs/limites.md` pour les écarts au droit positif.
