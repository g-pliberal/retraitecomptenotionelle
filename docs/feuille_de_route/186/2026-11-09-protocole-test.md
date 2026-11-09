# Le test auprès de vingt personnes : le protocole, prêt à lancer

**Reprise, au 9 novembre 2026.** Le protocole est écrit, rien n'est lancé :
une session ne mène pas d'entretien. Au propriétaire, les neuf questions de
la fin (« Ce que le propriétaire tranche »), d'abord la première : lancer
tout de suite une première vague de dix entretiens sur ce qui est tranché,
ou attendre la lecture A ou B et le plafond de baisse par an. Puis le
parti recrute, mène, dépouille sur la grille ; seule la synthèse, des
décomptes sans personne, revient au dépôt, dans une note à elle.

*Le 9 novembre 2026, action 186, chantier 8. Le propriétaire demande le
protocole du test que la note `2026-11-07-message-etude.md` annonçait
(« Tester avant de publier ») : qui l'on voit, ce qu'on montre, ce qu'on
demande, comment on lit les réponses, et ce que chaque résultat ferait
changer, écrit d'avance. Tout ce qui suit est une proposition : le
propriétaire tranche. Les chiffres du programme viennent de
`docs/feuille_de_route_programme.md` et des notes citées ; les règles sur
les données, des pages de la CNIL listées à la fin, lues ce jour.*

## L'essentiel

- **Vingt entretiens, un à un, de vingt minutes**, menés par le parti et
  non par une session : huit retraités dont quatre petites pensions, cinq
  personnes de 45 à 62 ans, sept de moins de 45 ans ; sept abstentionnistes
  au moins ; ni adhérent, ni proche.
- **Trois choses montrées, dans cet ordre** : le message de la décision 90,
  seul sur une carte ; l'accueil du site ; la carrière type la plus proche
  de la personne. La baisse n'est montrée qu'après avoir noté si la personne
  la cherche d'elle-même.
- **Quatre questions tiennent le test** : redire le message avec ses mots ;
  « Pensez-vous y gagner ? », posée trois fois ; « Qu'est-ce qui vous
  choque ? » ; la confiance, notée sur dix avant et après.
- **Ce que chaque résultat change est écrit avant le premier entretien**,
  avec son seuil : on ne lit pas les réponses pour y trouver ce qu'on
  espérait.
- **Rien de nominatif** : ni nom, ni coordonnées, ni enregistrement, des
  tranches plutôt que des valeurs. Le test se mène pourtant comme si le RGPD
  s'appliquait, parce que vingt personnes recrutées de proche en proche se
  reconnaissent à leur profil, et que ce qu'elles disent d'un programme est
  une opinion politique.
- **Il peut partir sans attendre** : le titre, la phrase de dessous et les
  six arguments sont les mêmes sous la lecture A et sous la lecture B. Ce
  qui attend, ce sont les montants en euros.

## Ce que le test cherche, et ce qu'il ne dit pas

Trois questions, celles de l'étude du 7 novembre : ce que la personne a
compris ; si elle pense y gagner ; l'écart entre ce qu'elle croit et ce que
le modèle calcule pour une carrière comme la sienne.

Vingt entretiens ne mesurent rien. Ils trouvent les contresens, pas leur
fréquence dans le pays : la synthèse dira « six retraités sur huit », jamais
un pourcentage, et ne conclura rien d'une seule personne. Les quotas ne
visent pas un échantillon représentatif ; ils font entendre plusieurs fois
chaque électorat du message.

Le contresens à guetter d'abord : un retraité qui lit « Chaque pension vaut
ce qui a été cotisé » et entend « j'ai cotisé toute ma vie, ma pension m'est
due, elle ne bougera pas ». Le titre lui dirait alors le contraire de ce que
le programme lui fait.

## Les vingt profils

### Les quotas

| Critère | Répartition proposée |
|---|---|
| Âge | 18-29 ans : 2 ; 30-44 ans : 5 ; 45-54 ans : 2 ; 55-62 ans : 3 ; 63-70 ans : 4 ; 71-80 ans : 3 ; plus de 80 ans : 1 |
| Situation | en emploi : 11 ; hors de l'emploi sans être retraité : 1 ; retraités : 8 |
| Retraités | petite pension, moins de 1 200 € par mois tous régimes confondus : 4 ; de 1 200 à 2 500 € : 3 ; plus de 2 500 € : 1 ; dont une réversion |
| Carrière | salariés du privé : 13 ; fonction publique et régimes spéciaux : 5 ; indépendants et agriculteurs : 2 |
| Revenu des onze en emploi et de la personne hors de l'emploi | autour du SMIC : 3 ; autour du salaire moyen : 7 ; cadres : 2 |
| Vote au dernier scrutin national | n'a pas voté : 7 au moins ; a voté : 13 au plus |
| Sexe | dix femmes au moins |
| Lieu | pas plus de la moitié dans une même agglomération |

Huit retraités sur vingt, parce que ce sont eux qui perdent, et que le
message leur parle le moins bien ; quatre petites pensions, parce que le fil
du programme est « le parti des cotisants et des petites pensions ». Le
seuil de 1 200 € est une proposition : un peu au-dessus de la garantie de
1 050 € pour une personne seule (décision 65). On ne demande jamais pour qui
la personne a voté.

**Qui l'on écarte.** Les adhérents et les sympathisants connus, qui
connaissent déjà le programme ; la famille et les amis de celui qui mène
l'entretien, qui ménagent leur interlocuteur ; les mineurs et les majeurs
protégés ; les professionnels des retraites. Le recrutement va de proche en
proche, au deuxième degré : l'ami d'un ami, le voisin d'un collègue.

### Les vingt, un à un

La carrière type est l'une des treize de la page `cas-types/`, à la
génération la plus proche (`CAS_TYPES` et `GENERATIONS`, dans
`src/retraite_notionnelle/castypes.py`). Un profil introuvable se remplace
par son voisin de même groupe d'âge, sans défaire les quotas.

| N° | Âge | Situation | Revenu ou pension | Vote | Carrière type montrée |
|---:|---|---|---|---|---|
| 1 | 18-29 | salariée du privé | autour du SMIC | non | Salarié au niveau du SMIC, 2000 |
| 2 | 18-29 | salarié du privé | salaire moyen | oui | Salarié au salaire moyen, 2000 |
| 3 | 30-44 | cadre du privé | cadre | oui | Cadre du privé, 1990 |
| 4 | 30-44 | salariée du privé | salaire moyen | non | Salarié au salaire moyen, 1990 |
| 5 | 30-44 | fonctionnaire, enseignante ou catégorie B | salaire moyen | oui | Fonctionnaire sédentaire (catégorie B), 1990 |
| 6 | 30-44 | artisan ou indépendant | salaire moyen | non | Artisan, 1990 |
| 7 | 30-44 | hors de l'emploi : chômage, parent au foyer | autour du SMIC | non | Carrière interrompue (5 ans hors emploi), 1990 |
| 8 | 45-54 | ouvrier ou employé du privé | autour du SMIC | non | Salarié au niveau du SMIC, 1980 |
| 9 | 45-54 | cadre du privé | cadre | oui | Cadre du privé, 1980 |
| 10 | 55-62 | salariée du privé | salaire moyen | oui | Salarié au salaire moyen, 1970 |
| 11 | 55-62 | hospitalier, cheminot ou agent des IEG | salaire moyen | oui | Fonctionnaire de catégorie active, Agent de conduite SNCF ou Agent des IEG, 1970 |
| 12 | 55-62 | contractuel de la fonction publique | salaire moyen | oui | Agent contractuel de la fonction publique, 1970 |
| 13 | 63-70 | retraitée du privé, carrière hachée | moins de 1 200 € | non | Carrière interrompue (5 ans hors emploi), 1960 |
| 14 | 63-70 | retraité du privé | 1 200 à 2 500 € | oui | Salarié au salaire moyen, 1960 |
| 15 | 63-70 | retraité, ancien cadre | plus de 2 500 € | oui | Cadre du privé, 1960 |
| 16 | 63-70 | retraitée de la fonction publique | 1 200 à 2 500 € | oui | Fonctionnaire sédentaire (catégorie B), 1960 |
| 17 | 71-80 | retraitée du privé, au SMIC toute sa vie | moins de 1 200 € | oui | Salarié au niveau du SMIC, 1950 |
| 18 | 71-80 | ancien agriculteur ou artisan | moins de 1 200 € | non | Chef d'exploitation agricole ou Artisan, 1950 |
| 19 | 71-80 | retraité d'un régime spécial, ou ancien militaire | 1 200 à 2 500 € | oui | Agent de conduite SNCF ou Militaire non officier, 1950 |
| 20 | plus de 80 | veuve, avec une réversion | moins de 1 200 € | oui | Salarié au niveau du SMIC, 1940 |

Les carrières types n'ont pas de réversion : au profil 20, on dit de vive
voix que les réversions déjà servies sont gardées (décision 16), et l'on
note ce qu'elle en fait. Une profession libérale née vers 1940, la seule des
treize dont la pension monte aux générations déjà parties (+ 19 %,
décision 90), peut remplacer le profil 15 si elle se trouve : on y verrait
comment se reçoit « certaines pensions montent ».

## Ce qu'on leur montre

Trois supports, imprimés, pour ne dépendre ni d'un réseau ni d'un écran ; le
téléphone de celui qui mène, si la personne préfère lire le site.

1. **Le message**, seul sur une carte, sans logo ni couleur de parti :
   « Chaque pension vaut ce qui a été cotisé. » et, dessous, « Une égalité
   de traitement pour tous et une protection pour les plus fragiles. »
   (décision 90, telle que l'accueil la porte depuis l'étape 2 de
   l'action 189).
2. **L'accueil du site**, tel qu'il est en ligne le jour de l'entretien : le
   titre, la phrase, les six arguments. La date de l'impression se note en
   tête de la grille, puisque le site bouge.
3. **La carrière type proche**, à la page `cas-types/` : la pension du droit
   en vigueur et celle de la proposition, pour la carrière et la génération
   du tableau. Entre les deux, la réponse du site à « Ma retraite va-t-elle
   baisser ? », où la décision 90 a placé la baisse, « un clic plus loin ».

**Ce qu'on ne montre pas.** Le simulateur : la décision 34 le réserve aux
adhérents, et la personne y saisirait sa propre carrière, une donnée
personnelle de plus. La page Coût, qui s'adresse à un autre lecteur.

**L'avertissement, lu avant la carrière type.** « Ces chiffres sont ceux
d'une carrière type, pas les vôtres. Le site ne suit pas encore toutes les
décisions du programme : le calendrier de la baisse n'est pas arrêté. » La
décision 90 le dit de la grille ; sans cette phrase, le test ferait croire
à un retraité un chiffre que le programme n'a pas arrêté.

## Le déroulé, en vingt minutes

Un entretien à la fois, chez la personne ou dans un lieu calme. Celui qui
mène n'est pas, si possible, celui qui a écrit le texte : on ménage un
auteur, et un auteur défend son texte. Il n'explique rien, ne corrige rien
et ne défend rien avant la dernière minute ; il note les mots de la
personne, pas les siens. Deux entretiens d'essai, d'abord, pour tenir les
vingt minutes.

| Minutes | Ce qui se passe |
|---|---|
| 0 à 2 | L'accueil : qui mène le test et pour quel parti, à quoi il sert, ce qui est noté et ce qui ne l'est pas. La notice est lue et remise, la personne coche ses deux cases (voir « Le consentement et les données »). |
| 2 à 4 | Le profil, en tranches, cinq cases. Puis, avant d'avoir rien montré : « Sur 10, quelle confiance avez-vous dans le système de retraite d'aujourd'hui ? » |
| 4 à 7 | La carte du message, lue en silence. Questions 1 et 2. |
| 7 à 12 | L'accueil, deux minutes de lecture libre ; on note où le regard s'arrête, ce qui est lu à voix haute. La page retirée, questions 3 à 6. Puis la réponse « Ma retraite va-t-elle baisser ? », si la personne ne l'a pas demandée avant. |
| 12 à 17 | La carrière type. Question 7 avant de la montrer, l'avertissement, puis questions 8 à 10. |
| 17 à 19 | La confiance : questions 11 à 14. |
| 19 à 20 | La clôture : on répond enfin aux questions de la personne, on lui redit que les chiffres vus sont ceux d'une carrière type, on lui remet le coupon qui porte le numéro de sa grille, pour un retrait. |

## Les questions

Dans cet ordre, mot pour mot ; une relance au plus, « C'est-à-dire ? ».

Sur le message :
1. « Avec vos mots, qu'est-ce que cette phrase veut dire ? » Puis : « Et la
   seconde ? »
2. « Pensez-vous y gagner ? » — y gagner, y perdre, ni l'un ni l'autre, ne
   sait pas — « Pourquoi ? »

Sur l'accueil, la page retirée :
3. « Qu'est-ce que vous retenez ? »
4. « Qu'est-ce qui vous choque ? »
5. « Quelle question vous posez-vous, que la page ne règle pas ? » On note
   si la baisse des pensions vient d'elle-même, et à quelle minute.
6. « Pensez-vous y gagner ? », une deuxième fois.

Après la réponse « Ma retraite va-t-elle baisser ? » : « Vous vous y
attendiez ? » On note le mot qui vient : normal, honnête, caché, trompé.

Sur la carrière type :
7. Avant de la montrer : « Pour quelqu'un qui a eu cette carrière, à votre
   avis, la pension monte, baisse, ou ne change pas ? De combien, à peu
   près ? »
8. Après : « Est-ce ce que vous attendiez ? »
9. « Pensez-vous y gagner ? », une troisième fois. « Et vos enfants, ou vos
   parents ? »
10. « Qu'est-ce qui vous choque, maintenant ? »

Sur la confiance :
11. « Sur 10, croyez-vous que cela se fera comme c'est écrit ? Qu'est-ce
    qui vous ferait monter d'un point ? »
12. « Qui, à votre avis, peut proposer cela ? »
13. « Si vous en parliez ce soir à quelqu'un, que lui diriez-vous ? » C'est
    la seconde reformulation, celle qui circule.
14. Aux seuls retraités, si le propriétaire la garde (question 6 de la
    fin) : « Si votre pension baissait, mais que ce que vous payez baissait
    aussi — des factures, des impôts —, l'accepteriez-vous ? » Sans aucun
    chiffre : la somme de ces baisses n'est pas calculée (décision 89).

## La grille d'analyse

Une feuille par entretien, remplie dans l'heure par celui qui a noté, puis
un tableau de vingt lignes. Les codes :

| Code | Ce qu'il note | Valeurs |
|---|---|---|
| C | La compréhension du message (question 1) | 2 : elle redit que la pension dépend de ce que chacun a cotisé, à la même règle pour tous ; 1 : une idée vague, « c'est plus juste » ; 0 : un contresens |
| C0 | Le contresens, s'il y en a un | a : « ma pension m'est due, elle ne bougera pas » ; b : « tout le monde aura la même pension » ; c : « on me rend mes cotisations » ou la capitalisation seule ; d : « c'est contre les fonctionnaires », ou un régime ; e : autre, mot pour mot |
| G1, G2, G3 | Le gain qu'elle croit (questions 2, 6 et 9) | gagne, perd, neutre, ne sait pas |
| M | Ce que le site calcule pour la carrière type montrée | monte ou baisse, en % |
| E | L'écart entre G3 et M, et entre la question 7 et M | accord ; illusion : elle croit gagner, la carrière perd ; crainte : l'inverse ; l'ampleur sous-estimée ou surestimée |
| B | La baisse | vient d'elle-même, avant l'accueil, à l'accueil, ou jamais ; reçue comme normale, honnête, négociable (« si c'est progressif »), rejetée, ou cachée (« on ne me l'avait pas dit ») |
| S | Ce qui choque (questions 4 et 10) | le mot exact, puis le thème : la baisse des pensions en cours ; les 65 ans ; l'avance reprise sur la succession ; les 5 % placés ; la fin des régimes spéciaux ; « cheminot », pris pour une cible ; la faute d'une génération ; autre |
| F0, F1 | La confiance, sur 10 | dans le système d'aujourd'hui ; dans la proposition (question 11), et sa raison |
| R | La phrase qu'elle redirait (question 13) | mot pour mot |
| V | Les mots qui arrêtent | « égalité de traitement », « cotisé », « compte », « placés », autre |
| A | L'acceptation d'une moindre baisse (question 14) | oui, non, « ça dépend de combien » |

La synthèse se lit par électorat — moins de 45 ans, 45 à 62 ans, retraités,
petites pensions — et par vote, en décomptes. Deux personnes codent chacune
de leur côté les questions 1 et 4, et comparent : un code qu'elles ne
donnent pas pareil est une définition à resserrer.

## D'avance, ce que chaque résultat ferait changer

Les seuils sont des propositions, à arrêter avant le premier entretien. Une
personne seule ne change rien ; un motif, trois personnes d'un même
électorat, oui.

| Ce que le test trouve | Seuil proposé | Ce qui change |
|---|---|---|
| Le message est compris (C = 2) | 14 sur 20, et la moitié de chaque électorat | Rien : le titre reste. |
| Le message n'est pas compris | moins de 10 sur 20 | Le titre se récrit ; le contresens dominant dit dans quel sens. Retour au propriétaire : c'est sa décision 90. |
| Des retraités lisent « ma pension m'est due » (C0 = a) | 3 retraités sur 8 | Le titre trompe ceux qui perdent : la baisse remonte à l'accueil, sous le titre, ce qui rouvre « un clic plus loin » (décision 90). |
| « Égalité de traitement » se lit « la même pension pour tous » (C0 = b), ou arrête (V) | 5 sur 20 | La phrase de dessous se récrit ; les mots sont au propriétaire. |
| Les actifs ne voient pas ce qu'ils gagnent (G3) | moins de 6 des 12 non-retraités | L'accueil ouvre sur le salaire net, en euros par mois : le choix entre A et B devient pressant. |
| On croit gagner là où la carrière type perd (E = illusion) | 5 sur 20 | Le message promet trop : la pension plus basse se dit à l'accueil, pas seulement à la question. |
| La baisse, découverte, est reçue comme cachée (B) | 4 retraités sur 8, ou 6 sur 20 | La baisse se dit à l'accueil. Reçue comme honnête par autant : la décision 90 est confirmée. |
| Personne ne cherche la baisse (B = jamais) | 12 sur 20 | La question « Ma retraite va-t-elle baisser ? » monte sur l'accueil, visible sans la chercher. |
| Un même thème choque (S) | 5 sur 20, dits sans y être aidés | Le site lui donne une réponse à lui, ou la phrase change. |
| L'avance reprise sur la succession choque les petites pensions | 3 sur 4 | La décision 30 ne bouge pas ; sa formulation se retravaille et se reteste à la seconde vague. |
| « Cheminot ou salarié du privé » est pris pour une attaque | 3 sur 20, ou 2 des 5 du public | L'exemple du sixième argument change. |
| La confiance baisse après la carrière type (F1 sous F0) | la médiane perd 2 points | La grille des carrières types fait du tort telle qu'elle est montrée : sa présentation passe au chantier 9. |
| On ne croit pas que cela se fera (F1) | médiane de 3 ou moins | « Une règle fixée une fois pour toutes » ne suffit pas : il lui faut une preuve, que la question 11 aura nommée. |
| Les retraités n'acceptent pas la moindre baisse (A) | moins de 3 sur 8 | La décision 89 ne s'écrit pas au site. « Ça dépend de combien », en majorité : la chiffrer d'abord. |
| La phrase redite (R) n'est pas le message | 10 sur 20 redisent autre chose, la même | Cette phrase-là est le message que les gens portent : la proposer au propriétaire. |

## Le consentement et les données

### La règle : ne pas recueillir

Ce qui n'est pas noté ne se protège pas. La grille ne porte ni nom, ni
prénom, ni téléphone, ni adresse, ni commune, ni employeur, ni métier
précis, ni âge exact, ni montant exact. Aucun enregistrement, aucune photo :
la CNIL range les « enregistrements sonores de voix » parmi les données
personnelles. Une liste de mentions interdites, lue par celui qui note avant
chaque entretien, comme la CNIL le recommande aux équipes de campagne : la
santé, la religion, l'origine, le syndicat, le parti pour lequel on a voté,
le nom de quiconque. Si la personne en parle, cela ne s'écrit pas.

### Pourquoi on applique quand même le RGPD

Trois raisons de ne pas se dire « c'est anonyme, donc hors du RGPD » :

- **Vingt personnes se reconnaissent à leur profil.** La CNIL rappelle que
  l'identification peut se faire « à partir du croisement d'un ensemble de
  données », et demande « de ne jamais considérer des jeux de données brutes
  comme anonymes ». Celui qui a recruté une retraitée de 71 à 80 ans,
  ancienne agricultrice, la retrouve dans le tableau. Des trois critères de
  l'anonymat, le premier manque : « il ne doit pas être possible d'isoler un
  individu dans le jeu de données ».
- **Un numéro ne suffit pas.** Une base où le nom est remplacé par un numéro
  « est considérée comme pseudonymisée et non comme anonymisée », et des
  données pseudonymisées restent soumises au RGPD.
- **Ce qui est noté est une opinion politique** : avoir voté ou non, et ce
  que l'on pense du programme d'un parti. L'article 9 du RGPD en interdit le
  traitement, sauf exception. Celle des partis ne vaut que pour leurs
  membres, anciens membres et les personnes en « contacts réguliers » avec
  eux : les vingt n'en sont pas. Reste le « consentement explicite »
  (article 9, paragraphe 2, a).

Les grilles sont donc des données personnelles sensibles tant qu'elles
existent ; la synthèse, des décomptes par électorat, ne l'est plus.

### Le consentement, sans signature

La CNIL veut un consentement « libre, spécifique, éclairé et univoque »,
donné par « une déclaration ou tout autre acte positif clairs », et, pour
des données sensibles, explicite ; le responsable doit pouvoir « démontrer à
tout moment que la personne a bien consenti ». Pour s'en assurer, elle
suggère une déclaration écrite et signée : ce serait la seule pièce
nominative du test. La piste, appuyée sur l'article 11 du RGPD — le
responsable « n'est pas tenu de conserver, d'obtenir ou de traiter des
informations supplémentaires » pour identifier quelqu'un à seule fin de
respecter le règlement — : la personne coche elle-même, sur sa grille
numérotée, deux cases que rien ne précoche, sans nom ni signature.

> ☐ J'ai entendu et reçu la notice. J'accepte de participer à cet
> entretien, et que mes réponses soient notées sans mon nom.
>
> ☐ J'accepte que soient notés le fait que j'ai voté ou non, et ce que je
> pense de ce texte, qui est le programme d'un parti politique.

Sans la seconde case, l'entretien n'a pas lieu : c'est tout son objet.
Chaque question reste facultative. Aucune rémunération, pour que le
consentement ne s'achète pas. Cette piste est à faire relire (question 8 de
la fin) : une case sans nom prouve moins qu'une signature.

### La notice, lue puis remise

Courte, en mots simples, dite par celui qui mène et laissée sur papier : la
CNIL demande une information « concise, transparente, compréhensible et
aisément accessible ». Elle porte ce que la CNIL liste « dans tous les
cas » :

> **Qui.** [Nom du parti], [adresse, courriel], teste un texte sur les
> retraites avant de le publier.
> **Pourquoi.** Savoir si ce texte se comprend. Rien d'autre : ni
> démarchage, ni fichier, ni nouveau contact.
> **Sur quelle base.** Votre accord, que vous pouvez retirer.
> **Ce qui est noté.** Une tranche d'âge, votre situation, une tranche de
> revenu, si vous avez voté, et vos réponses. Ni votre nom, ni vos
> coordonnées ; rien n'est enregistré. Vous pouvez ne pas répondre à une
> question, ou arrêter.
> **Qui le lit.** Les deux personnes qui dépouillent. Ce qui sort du test
> est un décompte, où personne ne se reconnaît.
> **Combien de temps.** Votre feuille est détruite trente jours au plus
> après le dernier entretien.
> **Vos droits.** Jusque-là, avec le numéro de ce coupon, vous pouvez voir
> votre feuille, la faire corriger ou la faire détruire, en écrivant à
> [courriel]. Ensuite, plus rien ne permet de vous retrouver. Vous pouvez
> saisir la CNIL (cnil.fr).

Le coupon, détaché de la grille, ne porte que son numéro : le retrait est
ainsi « aussi simple » que l'accord (article 7, paragraphe 3), sans que le
parti sache qui a quel numéro. Les feuilles détruites, les droits d'accès
ne peuvent plus s'exercer, ce que la notice dit d'avance (article 11,
paragraphe 2).

### Le recrutement, à part

Le prénom et le téléphone qui servent à fixer le rendez-vous sont des
données personnelles, les seules nominatives. Elles restent chez celui qui
recrute, jamais sur la grille ni à côté de son numéro, s'effacent le jour de
l'entretien, et n'entrent dans aucun fichier du parti. La CNIL recommande de
n'utiliser qu'une fois les coordonnées d'un contact occasionnel ; ici, pas
même pour inviter à adhérer, sauf si la personne le demande.

### Ce que le parti tient

- **Le responsable du traitement** est le parti, ou la personne qui
  organise le test s'il n'a pas la personnalité morale : à écrire dans la
  notice.
- **Le registre.** La dérogation des organismes de moins de 250 salariés ne
  couvre pas « les traitements qui portent sur des données sensibles » : une
  fiche, donc — le responsable, la finalité, les personnes (vingt
  volontaires), les données (les tranches, le vote, les réponses), les
  destinataires (deux personnes), aucun transfert hors de l'Union, la
  destruction à trente jours, les mesures de sécurité.
- **L'analyse d'impact.** Elle est obligatoire quand un traitement remplit
  « au moins deux des neuf critères » européens. Deux peuvent se lire ici :
  des données sensibles, et des « personnes âgées » parmi les personnes
  vulnérables. Vingt volontaires, sans fichier, des feuilles détruites en un
  mois : le risque est faible, mais la question se pose à la lettre. La
  piste : une page qui dit pourquoi le risque n'est pas élevé, jointe à la
  fiche de registre, relue par un juriste ou le délégué du parti.
- **La sécurité.** Les grilles dans une enveloppe fermée, chez une seule
  personne ; pas de photo ; le tableau des vingt lignes sur papier, ou dans
  un fichier local, jamais dans un service en ligne.
- **Le dépôt et les sessions.** Ni les grilles ni le tableau des vingt
  lignes n'entrent au dépôt, ni dans une session : seule la synthèse — des
  décomptes par électorat, et des phrases citées sans rien qui désigne leur
  auteur.

Ce qui précède lit les pages de la CNIL ; ce n'est pas un avis de juriste.
Aucune des pages lues ne traite d'une enquête qu'un parti mène auprès de
personnes qui ne sont ni ses membres ni ses contacts : le guide de la
communication politique parle de prospection, non de test.

## Ce que le test attend encore, et comment le lancer quand même

**La lecture A ou B de la décision 29.** Elle fixe le taux cotisé, donc le
gain des actifs en euros et leur pension. Pour le salarié au salaire moyen
né en 1990, au chiffrage du 8 novembre : + 186 € nets par mois aux 18 % du
programme, + 66 € sous A, + 263 € sous B ; une pension de 1 531 €, 1 697 €
ou 1 425 € en 2055, face aux 2 859 € du droit en vigueur. Le sens ne dépend
pas de la lecture ; le montant, si. Tant qu'elle n'est pas choisie, aucun
gain en euros ne se montre.

**Le plafond de baisse par an (chantier 2).** La baisse se fait en cinq ans
au plus (décision 3), par cinquièmes pour les complémentaires que l'État
règle (décision 87) ; le plafond par an reste au propriétaire, et le site
la montre encore d'un coup. Les retraités perdent la même chose sous les
trois lectures : pour eux, ce n'est pas A ou B qui manque, c'est ce qu'ils
perdent la première année. Manquent aussi qui perd, et combien, par tranche
de pension ; combien de retraités voient leur pension monter (décision 90) ;
la somme des petites baisses de la décision 89.

**Ce qui est tranché suffit à une première vague.** Le titre, la phrase de
dessous et les six arguments sont arrêtés, et ne citent aucun montant que A
ou B déplacerait. La compréhension, le gain que l'on croit, ce qui choque
et la confiance se testent dès maintenant. D'où deux vagues de dix :

- **La première, tout de suite**, sur les profils impairs du tableau, qui
  gardent quatre retraités dont deux petites pensions : la carte, l'accueil,
  la réponse « Ma retraite va-t-elle baisser ? » et la carrière type telle
  que le site la montre, avec l'avertissement. Elle dit si le message se
  comprend et si la baisse, placée un clic plus loin, est reçue comme
  honnête ou comme cachée.
- **La seconde, après A ou B et le plafond**, sur les profils pairs : la
  même grille, le gain des actifs en euros et la perte d'un retraité la
  première année en plus. Le texte corrigé après la première vague s'y
  reteste ; les deux vagues se comparent, puisque la grille est la même.

L'autre voie, les vingt d'un coup une fois tout tranché, teste un texte
complet, mais ne laisse rien corriger entre deux lectures et fait attendre
le chantier 9. Si la première vague montre que les actifs ne voient pas
leur gain, elle aura dit, en plus, que le choix entre A et B presse.

## Ce que le propriétaire tranche

1. **Quand lancer** : une première vague de dix dès maintenant, sur ce qui
   est tranché, puis dix après A ou B et le plafond (la piste) ; ou les
   vingt d'un coup, une fois les deux tranchés.
2. **Les quotas** : huit retraités sur vingt dont quatre petites pensions,
   sept abstentionnistes au moins, cinq personnes du public (la piste) ; le
   seuil de la petite pension, 1 200 € par mois.
3. **Qui mène et qui recrute** : le propriétaire, des membres du parti, ou
   quelqu'un d'extérieur au texte (la piste, pour mener) ; l'écart des
   adhérents et des proches.
4. **Nommer le parti dès l'accueil** : oui (la piste), le consentement
   éclairé le demande, au prix d'un biais chez ceux qui en ont une idée ;
   la carte du message reste sans logo.
5. **Montrer aux retraités la baisse que le site affiche aujourd'hui**, avec
   l'avertissement (la piste), ou ne leur montrer la carrière type qu'à la
   seconde vague, le calendrier arrêté.
6. **La question 14**, la moindre baisse de la décision 89 : la poser sans
   chiffre (la piste), ou l'ôter tant que la somme n'est pas calculée.
7. **Les seuils** du tableau « ce que chaque résultat ferait changer », et
   d'abord celui-ci : accepter d'avance que trois retraités sur huit lisant
   « ma pension m'est due », ou quatre se disant trompés, rouvrent « la
   baisse un clic plus loin » de la décision 90.
8. **Les données** : le consentement par deux cases sans signature (la
   piste) ou un formulaire signé, gardé à part ; la destruction à trente
   jours ; le nom du responsable du traitement ; et une relecture de cette
   partie par un juriste ou le délégué à la protection des données du parti
   avant le premier entretien, analyse d'impact comprise.
9. **Aucune rémunération** (la piste), ou un dédommagement égal pour tous.

## Sources

Pages de la CNIL, lues le 9 novembre 2026 ; les citations sont de courts
extraits.

- « L'anonymisation de données personnelles », 19 mai 2020 :
  https://www.cnil.fr/fr/technologies/lanonymisation-de-donnees-personnelles
- « Identifier les données personnelles », 27 janvier 2020 :
  https://www.cnil.fr/fr/identifier-les-donnees-personnelles
- « Conformité RGPD : comment recueillir le consentement des personnes ? »,
  3 août 2018 : https://www.cnil.fr/fr/les-bases-legales/consentement
- « Conformité RGPD : information des personnes et transparence »,
  29 juillet 2019 :
  https://www.cnil.fr/fr/conformite-rgpd-information-des-personnes-et-transparence
- Le RGPD, chapitre II (articles 5, 7, 9 et 11) et chapitre III
  (articles 12 et 13) :
  https://www.cnil.fr/fr/reglement-europeen-protection-donnees/chapitre2 et
  https://www.cnil.fr/fr/reglement-europeen-protection-donnees/chapitre3
- « Les fichiers de communication politique », 21 octobre 2025 :
  https://www.cnil.fr/fr/les-fichiers-de-communication-politique
- « Communication politique : protéger les données des électeurs », guide,
  novembre 2025 :
  https://www.cnil.fr/sites/default/files/2025-11/guide_communication_politique.pdf
- « Le registre des activités de traitement », 13 avril 2018 :
  https://www.cnil.fr/fr/RGPD-le-registre-des-activites-de-traitement
- « Ce qu'il faut savoir sur l'analyse d'impact relative à la protection
  des données (AIPD) », 18 octobre 2017 :
  https://www.cnil.fr/fr/ce-quil-faut-savoir-sur-lanalyse-dimpact-relative-la-protection-des-donnees-aipd
- « Les durées de conservation des données », 2 avril 2026 :
  https://www.cnil.fr/fr/les-durees-de-conservation-des-donnees
- « Recherche scientifique (hors santé) : enjeux et avantages de
  l'anonymisation et de la pseudonymisation », 13 janvier 2022 :
  https://www.cnil.fr/fr/recherche-scientifique-hors-sante-enjeux-et-avantages-de-lanonymisation-et-de-la-pseudonymisation
