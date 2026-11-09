# « Plein de petites baisses », chiffrées pour un retraité : la somme ne compense pas la baisse de la pension

*Le 9 novembre 2026, action 186, chantier 8. La décision 89 dit : « on
compte faire plein de petites baisses. Au total, on aura une vraie grosse
baisse pour tout le monde. Y compris pour les retraités », et demande de
chiffrer avant de le dire. Cette note recense ce que le programme, tel
qu'il est décidé, baisse et hausse ; elle en fait la somme pour quatre
retraités types, propriétaires puis locataires, et la met face à la baisse
de leur pension. La pension vient du modèle tel qu'il est, au commit
`1c32439`, sans qu'une ligne en change ; les taxes et les factures sont
posées à côté, sur des chiffres publiés. Les deux scripts sont restés dans
le brouillon de la session. La note propose ; le propriétaire tranche.*

## L'essentiel

**Une seule baisse décidée atteint un retraité : la CTA.** Elle lui rend
environ 23 € par an sur l'électricité, et de 49 à 58 € de plus s'il se
chauffe au gaz (calcul). Toutes les autres baisses du programme vont aux
actifs et à leurs employeurs.

**Le propriétaire paie plus qu'aujourd'hui.** La taxe sur la valeur du
terrain à 2 %, sans abattement, lui coûte environ 600 € par an pour
100 000 € de logement ; la taxe foncière qu'elle remplace, environ 385 €
(calcul). L'écart est de 170 à 270 € par an et par 100 000 €.

**Face à la baisse de la pension, la somme ne pèse rien.** Pour une personne
seule, par an (modèle, puis calcul) :

| Pension brute aujourd'hui, par mois | 1 100 € | 1 600 € | 2 500 € | 4 000 € |
|---|---:|---:|---:|---:|
| Pension brute sous la proposition | 1 050 € | 1 183 € | 1 758 € | 3 018 € |
| Baisse de la pension nette, par an | −600 € | −3 586 € | −6 704 € | −7 720 € |
| Locataire : somme des baisses décidées | +23 € | +23 € | +23 € | +23 € |
| Locataire : part de la baisse compensée | 4 % | 0,6 % | 0,3 % | 0,3 % |
| Propriétaire : somme des baisses et des hausses | −693 € | −358 € | −569 € | −928 € |
| Propriétaire : baisse de la pension et somme | −1 293 € | −3 943 € | −7 273 € | −8 648 € |

Le propriétaire perd donc deux fois, et le locataire retrouve moins d'un
centième de ce qu'il perd, sauf au plancher.

**Les lectures A et B ne changent rien pour un retraité.** La pension déjà
servie ne dépend pas du taux de cotisation : le modèle rend la même, à
l'euro près, sous 18 %, sous A et sous B (modèle). Les deux lectures ne
départagent que les actifs.

**La somme compense la baisse pour ceux dont la pension ne baisse pas, et
pour eux seuls** : les retraités sous le plancher de la garantie, 27 % des
retraités (dépôt), et parmi eux les seuls locataires, soit 8 à 19 % des
retraités (calcul, fourchette large). Au-dessus du plancher, pour aucun.

**Ce que la note propose** : ne pas dire « une moindre baisse » aux
retraités tant qu'aucune baisse décidée ne les atteint ; dire ce qui est
vrai et que le modèle montre — la pension nette baisse moins que la brute,
et personne ne tombe sous le plancher. Si le propriétaire veut que la
phrase devienne vraie, trois leviers sont chiffrés à part.

*Lire les chiffres.* **(publié)** : lu à sa source, citée en fin de note.
**(dépôt)** : pris dans une note, une décision ou une donnée du dépôt.
**(modèle)** : sorti du modèle au commit `1c32439`, paramètres changés en
mémoire ; c'est une sorte de (dépôt). **(calcul)** : calculé ici, le calcul
posé. **(hypothèse)** : la valeur du logement de chaque retraité type, que
rien de publié ne donne par niveau de pension ; c'est la seule. Les
montants sont en euros de 2026, par an sauf mention.

## Ce que le programme baisse, et ce qu'il hausse

Sont décidées les mesures numérotées de `docs/feuille_de_route_programme.md`.

| Mesure | Décision | Qui en profite, ou qui paie | Atteint un retraité |
|---|---|---|---|
| **Baisses** | | | |
| CTA supprimée, sur l'électricité et le gaz | 88 | tout consommateur | oui |
| Taxe foncière supprimée, la LVT la remplace | 9, 80 | les propriétaires | oui, s'il possède |
| CEG et CET supprimées | 36 | salariés et employeurs du privé | non |
| Cotisation de retraite à 18 % après l'intégration | 40, 48 | les actifs | non |
| Taux cotisé de la lecture A ou B | 29 | les actifs : +66 € (A) ou +263 € (B) par mois au salaire moyen (dépôt) | non |
| Taxe sur les salaires et forfait social supprimés, 17,8 Md€ en 2025 (dépôt) | partage du 20 septembre | les employeurs | non |
| CSG d'activité baissée de 1,12 point en 2025 (dépôt) | partage du 20 septembre | les salariés | non |
| **Hausses** | | | |
| LVT à 2 %, sans abattement, en quelques mois | 80, 81 | les propriétaires | oui, s'il possède |
| Prime de 2,15 % retenue sur les pensions servies, rendue en route si elle ne sert pas | 73 à 75 | les retraités | oui |
| Reprise de la garantie sur la succession, dès le premier euro | 30, 66 | les héritiers de qui touche la garantie | oui, plus tard |
| Revalorisation diminuée de la hausse du nombre de retraités par cotisant | 41 | les retraités | oui, après 2026 |
| **Ni l'un ni l'autre** | | | |
| TVA gardée à 20 % | 79 | — | rien ne change |
| Droits sur les alcools retirés à la complémentaire agricole | 67 | la taxe demeure | rien ne change |

Trois remarques sur ce tableau.

- **Les impôts que la retraite n'encaisse plus ne sont pas rendus aux
  retraités.** Le partage du 20 septembre en rend la moitié aux salaires,
  l'autre à la dette (`restitution.py`). La CSG prélevée sur les pensions,
  dont 2,94 points vont aujourd'hui à la retraite (dépôt, article L. 131-8,
  3° e, du code de la sécurité sociale), continue d'être prélevée.
- **Deux baisses ne sont pas des décisions, mais la suite de la baisse de la
  pension** : la CSG, la CRDS et la CASA, puis l'impôt sur le revenu,
  baissent avec elle. Le modèle les compte (`EffetRetour._preleve`) ; la
  note les met du côté de la pension, qui se lit en net.
- **La baisse des pensions elle-même** (décisions 2, 3, 52 à 56) n'est pas
  dans ce tableau : c'est l'autre plateau de la balance.

## La baisse de la pension, au modèle

### Les quatre retraités types

Ce sont quatre anciens salariés du privé nés en 1950, qui ont 76 ans en
2026, sans enfant, à la carrière des cas types « salaire moyen » et
« cadre » de la grille du site. Seul le niveau de salaire est cherché, pour
que le droit en vigueur leur serve en 2026 la pension brute de droit direct
voulue. Le modèle donne ce qu'il leur sert sous la proposition
(`pension_aujourd_hui`, scénario 6). Par mois (modèle) :

| | 1 100 € | 1 600 € | 2 500 € | 4 000 € |
|---|---:|---:|---:|---:|
| Statut | non-cadre | non-cadre | non-cadre | cadre |
| Niveau de salaire, en part du salaire moyen | 0,32 | 0,74 | 1,39 | 2,33 |
| Départ | 2011 | 2011 | 2011 | 2013 |
| Régime général | 920 € | 1 184 € | 1 609 € | 1 633 € |
| Agirc-Arrco | 180 € | 416 € | 891 € | 2 367 € |
| Sous la proposition : pension du compte | 594,65 € | 1 182,79 € | 1 758,06 € | 3 017,69 € |
| Garantie vieillesse, personne seule | 455,35 € | 0 | 0 | 0 |
| Total sous la proposition, personne seule | 1 050,00 € | 1 182,79 € | 1 758,06 € | 3 017,69 € |
| Écart brut | −4,5 % | −26,1 % | −29,7 % | −24,6 % |

La grille du site, relancée de même sur ses 38 cases déjà parties, redonne
la médiane publiée : −27,9 % (modèle ; « 28 % » sur l'accueil).

### Du brut au net, par an

Le modèle compte ce que paie une personne seule qui n'a que sa pension : la
CSG, la CRDS et la CASA de sa tranche, puis l'impôt sur le revenu, au barème
de 2026. Les taux sont ceux du dépôt
(`prelevements_remuneration.yaml`) : exonéré jusqu'à 13 048 € de revenu
fiscal pour une part ; 4,3 % jusqu'à 17 057 € ; 7,4 % jusqu'à 26 472 € ;
9,1 % au-delà. Le revenu fiscal est la pension moins l'abattement de 10 %.

| Personne seule, par an | 1 100 € | 1 600 € | 2 500 € | 4 000 € |
|---|---:|---:|---:|---:|
| Pension brute aujourd'hui (12 mois) | 13 200 | 19 200 | 30 000 | 48 000 |
| Pension brute sous la proposition | 12 600 | 14 193 | 21 097 | 36 212 |
| **Baisse brute** (calcul) | **−600** | **−5 007** | **−8 903** | **−11 788** |
| Revenu fiscal, avant puis après | 11 880 ; 11 340 | 17 280 ; 12 774 | 27 000 ; 18 987 | 43 561 ; 32 591 |
| Taux de CSG, CRDS et CASA, avant puis après | 0 ; 0 | 7,4 % ; 0 | 9,1 % ; 7,4 % | 9,1 % ; 9,1 % |
| CSG, CRDS et CASA, avant puis après (modèle) | 0 ; 0 | 1 421 ; 0 | 2 730 ; 1 561 | 4 368 ; 3 295 |
| Impôt sur le revenu, avant puis après (modèle) | 0 ; 0 | 0 ; 0 | 1 030 ; 0 | 5 179 ; 2 184 |
| Prélèvements en moins (calcul) | 0 | +1 421 | +2 199 | +4 068 |
| **Baisse nette** (calcul) | **−600** | **−3 586** | **−6 704** | **−7 720** |
| En part de la pension nette | −4,5 % | −20,2 % | −25,6 % | −20,1 % |

Le calcul, sur la pension de 2 500 € : la baisse brute est
12 × (1 758,06 − 2 500) = −8 903 € ; les prélèvements sociaux passent de
9,1 % × 30 000 = 2 730 € à 7,4 % × 21 097 = 1 561 €, soit 1 169 € de
moins ; l'impôt passe de 1 030 € à 0 ; la baisse nette est
−8 903 + 1 169 + 1 030 = −6 704 €. La pension de 1 600 € sort de la CSG :
son revenu fiscal tombe à 12 774 €, sous le seuil de 13 048 €.

### À deux, la pension de 1 100 € perd bien plus

La garantie est de 1 050 € pour une personne seule et de 800 € par personne
à deux (décision 65). Le retraité à 1 100 € garde 1 050 € s'il vit seul,
et tombe à 800 € s'il vit en couple : −3 600 € bruts par an, −3 032 € nets
si son conjoint a la même pension (modèle, `situation_foyer` à « couple »).
Les trois autres pensions sont au-dessus des deux planchers ; à deux, leur
baisse nette est de −4 196 €, −6 491 € et −7 388 € par personne (modèle,
deux pensions égales).

### Sous la lecture A et sous la lecture B : la même baisse

Les lectures de la décision 29 fixent le taux cotisé et crédité aux
comptes : 21,2 % sous A, 15,9 % sous B, avec la part de TVA et la LVT
(dépôt, note `2026-11-07-deux-lectures-au-modele.md`). Le modèle, relancé
à 18 %, 21,2 %, 15,9 %, 25,3 % et 20,8 %, rend aux quatre retraités la même
pension au centime : 1 050,00 €, 1 182,79 €, 1 758,06 € et 3 017,69 €
(modèle). Un retraité ne cotise plus : son compte est fait de ce qu'il a
cotisé avant 2026.

| | Lecture A | Lecture B |
|---|---:|---:|
| Baisse nette de la pension, de 1 100 € à 4 000 € | −600 à −7 720 € | les mêmes |
| Somme des baisses décidées, locataire | +23 € | +23 € |
| Somme des baisses et des hausses, propriétaire | −358 à −928 € | les mêmes |
| Salarié né en 1990 au salaire moyen, net par mois (dépôt) | +66 € | +263 € |
| Solde de la caisse en 2026, points de PIB (dépôt) | +0,7 | −1,5 |

La « vraie grosse baisse » existe donc, mais pour les actifs, et sa taille
est celle de la lecture choisie. Ce qui distingue A pour un retraité est
indirect : la caisse y est en excédent dès 2026, ce qui laisse de quoi
payer une baisse qui l'atteindrait, si le propriétaire en décidait une.

## Les baisses et les hausses, pour chaque retraité

### La CTA : 23 € par an, jusqu'à 81 € au gaz

- *Électricité.* La baisse du 1er février 2026, de 21,93 % à 15 %, rend
  10,58 € par an TTC à un client moyen au tarif réglementé (publié, CRE,
  dans la note `2026-11-09-cta.md`). Elle retire
  (21,93 − 15) / 21,93 = 31,6 % du prélèvement ; il en reste
  10,58 × 15 / 6,93 = **22,90 € par an TTC** (calcul), que la décision 88
  supprime. Un comparateur donne 9 à 52 € selon la puissance souscrite, et
  18 € pour 6 kVA (publié, Selectra, montants indicatifs).
- *Gaz.* La CTA vaut 20,80 % de la part fixe du tarif de distribution, plus
  4,71 % de 83,21 % de cette part (publié, Selectra ; le coefficient de
  72,71 % que la note du 9 novembre relevait a été ramené à 83,21 % par un
  arrêté du 26 juin 2026). Pour un abonnement de chauffage de 196,68 € par
  an au 1er juillet 2026 (publié, source secondaire) :
  196,68 × (0,2080 + 0,0471 × 0,8321) = **48,62 € hors taxes**, soit
  58,34 € TTC (calcul). Selectra donne le même 48,62 €, qu'il dit TTC, et
  14,21 € pour la seule cuisson. La note retient 49 à 58 €.

Un retraité tout électrique gagne donc 23 € par an, un retraité chauffé au
gaz 72 à 81 € (calcul). C'est la réponse au premier point de « Ce qui
reste » de la note du 9 novembre sur la CTA ; le rendement total reste à
lire au rapport de la CNIEG.

### La taxe foncière contre la LVT, pour 100 000 € de logement

- *Ce que vaut le terrain.* Fin 2025, les ménages possèdent 4 190 Md€ de
  terrains bâtis et 4 812 Md€ de bâti (publié, Insee, dans la note
  `2026-11-07-recettes-tva-lvt.md`) : le terrain fait
  4 190 / 9 002 = 46,5 % de la valeur d'un logement.
- *Ce que la taxe fait au prix.* La note du 7 novembre pose
  P₁ = P₀ × y / (y − τ₀ + t), avec τ₀ = 0,32 % et t = 2 % (dépôt). Au
  rendement central y = 3 %, le prix du terrain est multiplié par
  0,03 / 0,0468 = 0,641 ; par 0,598 à y = 2,5 % ; par 0,704 à y = 4 %
  (calcul).
- *La LVT.* 2 % × 46,5 % × 0,641 = **0,597 % de la valeur d'aujourd'hui du
  logement**, soit 597 € par 100 000 € ; 557 € à 656 € selon le rendement
  (calcul).
- *La taxe foncière.* Les particuliers ont payé 34,69 Md€ de taxe foncière
  sur le bâti en 2025, à 31,06 millions, soit 1 117 € en moyenne (publié,
  DGFiP). Rapportés à leurs 9 002 Md€ d'immobilier : **0,385 %**, soit
  385 € par 100 000 € (calcul). L'Insee donne 0,34 % en moyenne, plus de
  0,5 % pour les moins bien dotés et 0,22 % pour le centile le mieux doté
  (dépôt, note du 7 novembre).
- *L'écart.* 597 − 385 = **+211 € par an et par 100 000 €** au rendement
  central, +171 € à +270 € selon le rendement (calcul). En moyenne, un
  particulier propriétaire paierait
  4 190 Md€ × 2 % × 0,641 / 31,06 millions = 1 730 €, contre 1 117 €
  (calcul).

La part du terrain n'est pas la même partout : elle est plus forte dans les
grandes villes, plus faible à la campagne. Un retraité rural paierait moins
que ce calcul, un retraité parisien plus.

**Les exonérations d'aujourd'hui pèsent sur le plus modeste.** La taxe
foncière de l'habitation principale est supprimée aux plus de 75 ans dont
le revenu fiscal ne dépasse pas 12 793 € pour une part (publié,
service-public.fr, taxe de 2026 sur les revenus de 2025) ; les 65 à 75 ans
sous le même seuil ont 100 € de moins ; la taxe est plafonnée à 50 % des
revenus sous 30 083 € pour une part (publié, LégiFiscal). Le retraité à
1 100 €, seul, 76 ans, a 11 880 € de revenu fiscal : il ne paie pas de taxe
foncière aujourd'hui. La LVT de la décision 80 est chiffrée « sans
abattement » ; l'abattement et le plafonnement « restent ouverts ». Telle
qu'elle est décidée, elle lui fait payer une taxe qu'il ne paie pas.

### La somme, pour un locataire et pour un propriétaire

La valeur du logement de chaque retraité type est une hypothèse. Son
repère : les ménages retraités possèdent 216 000 € d'immobilier en moyenne
(publié, COR, enquête de 2021), et 70,2 % des ménages de 65 ans ou plus
sont propriétaires de leur logement (publié, Insee), soit de l'ordre de
216 000 / 0,702 = 308 000 € par ménage propriétaire, tous biens confondus
(calcul). Les deux lignes « par 100 000 € » plus haut permettent de refaire
le compte pour une autre valeur.

| Personne seule, par an, rendement de 3 % | 1 100 € | 1 600 € | 2 500 € | 4 000 € |
|---|---:|---:|---:|---:|
| **Locataire** | | | | |
| CTA de l'électricité supprimée (calcul) | +23 | +23 | +23 | +23 |
| Somme, locataire | +23 | +23 | +23 | +23 |
| Somme, s'il se chauffe au gaz | +72 à +81 | +72 à +81 | +72 à +81 | +72 à +81 |
| **Propriétaire** | | | | |
| Valeur du logement (hypothèse) | 120 000 | 180 000 | 280 000 | 450 000 |
| CTA de l'électricité supprimée | +23 | +23 | +23 | +23 |
| Taxe foncière supprimée, 0,385 % (calcul) | 0, exonéré | +694 | +1 079 | +1 734 |
| LVT, 0,597 % (calcul) | −716 | −1 074 | −1 671 | −2 685 |
| Somme, propriétaire | −693 | −358 | −569 | −928 |
| Somme, aux rendements de 2,5 % et de 4 % | −645 à −764 | −286 à −463 | −457 à −734 | −748 à −1 193 |

Sans son exonération, le retraité à 1 100 € paierait 462 € de taxe
foncière, et sa somme serait de −231 € (calcul).

### Face à la baisse de la pension

| Personne seule, par an | 1 100 € | 1 600 € | 2 500 € | 4 000 € |
|---|---:|---:|---:|---:|
| Baisse nette de la pension (A comme B) | −600 | −3 586 | −6 704 | −7 720 |
| **Locataire** : somme | +23 | +23 | +23 | +23 |
| Reste perdu | −577 | −3 563 | −6 682 | −7 697 |
| Part compensée, tout électrique | 3,8 % | 0,6 % | 0,3 % | 0,3 % |
| Part compensée, chauffé au gaz | 13,5 % | 2,3 % | 1,2 % | 1,1 % |
| **Propriétaire** : somme | −693 | −358 | −569 | −928 |
| Reste perdu | −1 293 | −3 943 | −7 273 | −8 648 |
| Part compensée | aucune : la somme s'ajoute à la perte | de même | de même | de même |

Par mois, le locataire retrouve 2 € quand il en perd 50, 299, 559 ou 643.

### Trois charges décidées de plus, que ce tableau ne compte pas

- **La prime de 2,15 %** (décisions 73 et 74) est retenue sur les pensions
  servies dès la bascule ; le modèle ne la porte pas à la pension d'un cas
  type. Sur la pension brute d'après la baisse : 2,15 % × 14 193 = 305 € ;
  × 21 097 = 454 € ; × 36 212 = 779 € par an (calcul). Elle est rendue en
  route si la réserve ne sert pas (décision 75). À elle seule, elle fait
  treize fois la CTA de l'électricité pour la pension de 1 600 €.
- **La reprise sur la succession** (décisions 30 et 66). Le retraité à
  1 100 € ne touche pas l'ASPA aujourd'hui : rien n'est repris sur sa
  succession. Sous la proposition, sa pension du compte est de 594,65 € ;
  la garantie lui avance 455,35 € par mois, 5 464 € par an (modèle), repris
  avec intérêts sur ce qu'il laisse. S'il est propriétaire, c'est sur son
  logement. Sa pension ne baisse que de 50 € par mois, mais 455 € en
  deviennent une avance.
- **L'indexation** (décision 41) : chaque année après 2026, la
  revalorisation perd la hausse du nombre de retraités par cotisant. La
  note `2026-11-07-indexation-scenario-6.md` la chiffre ; elle ne joue pas
  l'année de la bascule.

## Pour quelle part des retraités la somme compense la baisse

**Au-dessus du plancher, pour aucun.** La somme vaut au mieux 81 € par an,
pour un locataire chauffé au gaz. Elle ne compense qu'une baisse de pension
de moins de 7 € par mois. Sur les 38 cases déjà parties de la grille du
site, 34 perdent plus de 200 € nets par an, et la perte médiane est de
5 864 € (modèle). Les quatre qui ne perdent pas sont celles dont la pension
ne baisse pas : les deux libéraux, nés en 1940 et en 1950, et les deux
exploitants agricoles nés en 1940 et en 1950, que la garantie porte de
1 044 € à 1 050 €.

**Sous le plancher, la pension ne baisse pas, et la somme compense par
construction pour les locataires.** La distribution des pensions brutes de
droit direct des retraités qui vivent en France (dépôt, EIR 2020 de la
DREES, portée aux prix de 2026 par le coefficient du modèle, 1,1751) en
place 19,4 % sous 800 € et 29,7 % sous 1 050 € (calcul). La garantie,
servie d'office (décision 20), les porte à 800 € à deux et à 1 050 €
seuls : leur total ne baisse pas, et monte pour qui n'a pas l'ASPA
aujourd'hui. Au mélange des personnes seules et des couples que donne le
recensement, **26,9 % des retraités de 65 ans et plus ont une pension
propre sous leur plancher**, 3 995 000 personnes (dépôt, note
`2026-11-09-pensions-qui-montent.md`, écrite le même jour, qui fait ce
compte et en dit les réserves).

Parmi eux, seuls les locataires y gagnent : la CTA. Les propriétaires
paient la LVT, sauf abattement. Le dépôt n'a pas la part des locataires par
niveau de pension. Si elle est celle de tous les ménages de 65 ans ou plus,
100 − 70,2 = 29,8 % (publié, Insee), 26,9 % × 29,8 % = 8 % des retraités ;
si elle est celle du quart des ménages aux revenus les plus bas, tous âges
confondus, 100 − 28,5 = 71,5 % (publié, Insee), 26,9 % × 71,5 % = 19 %
(calcul). **La somme compense donc la baisse pour 8 à 19 % des retraités,
tous sous le plancher, et pour aucun des 73 % qui sont au-dessus.**

Trois réserves. Une partie de ces retraités touche déjà l'ASPA, à 6 € du
plancher : leur total ne bouge pas. Ce qui
ne baisse pas est le total versé : la pension du compte, elle, baisse, et
la garantie qui la complète est une avance reprise sur la succession. Et
une pension de droit direct basse n'est pas un foyer pauvre : beaucoup sont
des conjoints, que la garantie individualisée sert quel que soit le revenu
de l'autre.

## À part : ce qui n'est pas décidé, ou que le modèle ne fait pas encore

- **L'abattement de la résidence principale, le plafonnement au revenu et
  le sort des exonérations de la taxe foncière** (ouverts, décision 80).
  Pour qu'un propriétaire moyen ne paie pas plus qu'aujourd'hui sur son
  logement, il faudrait abattre 1 − 385 / 597 = 35 % de la valeur de son
  terrain (calcul). Reconduire l'exonération des plus de 75 ans modestes
  ramènerait la somme du retraité à 1 100 € de −693 € à +23 €. Ce que ces
  mesures retirent au point de LVT des retraites (36 à 43 Md€) n'est pas
  chiffré : il y faut la valeur du terrain des résidences principales.
- **Rendre aux retraités la CSG de leurs pensions qui va à la retraite**,
  2,94 points. Rien ne le décide. Sur la pension d'après la baisse : rien
  pour les pensions de 1 100 € et de 1 600 €, qui ne paient plus de CSG ;
  2,94 % × 21 097 = 620 € pour celle de 2 500 € ; 2,94 % × 36 212 = 1 065 €
  pour celle de 4 000 € (calcul). La mesure irait aux pensions hautes, et
  elle prend sur la moitié rendue aux salaires ou sur celle de la dette.
- **L'Agirc-Arrco garde ses pensions jusqu'à son intégration, en 2032**
  (décision 43, décidée ; le modèle baisse tout d'un coup). Jusque-là, seule
  la pension du régime général baisse. Le modèle ne dit pas de combien : le
  compte ne sépare pas les deux. Si elle baissait du même taux que le
  total, la baisse brute serait de −3 706 €, −5 730 € et −4 814 € par an
  pour les pensions de 1 600 €, 2 500 € et 4 000 €, au lieu de −5 007 €,
  −8 903 € et −11 788 € (calcul, pour l'ordre de grandeur seulement).
- **La baisse par cinquièmes** est décidée pour les complémentaires que
  l'État règle (décision 87) ; pour le régime général, c'est encore une
  piste du chantier 2. Elle diviserait par cinq la perte de la première
  année, sans rien changer à celle de la cinquième.
- **Le prix du logement** baisse de 14 à 19 % (dépôt) : 30 000 € pour un
  logement de 180 000 € au rendement central (calcul). C'est du patrimoine,
  non une dépense de l'année, et l'acheteur de demain y gagne.
- **Les droits familiaux.** Les quatre types n'ont pas d'enfant. Un parent
  de trois enfants perd en plus sa majoration de 10 % (décision 54).
- **Ce que le modèle ne compte pas** : la cotisation maladie de 1 % sur les
  pensions complémentaires, la taxe d'enlèvement des ordures ménagères, qui
  n'est pas la taxe foncière et que rien ne supprime, et tout autre revenu
  que la pension.
- **L'idée que les retraités acceptent une baisse si ce qu'ils paient
  baisse aussi** reste à éprouver sur des lecteurs (note du 9 novembre sur
  la CTA).

## La méthode, et ses limites

- **La pension** : le jumeau Python du modèle, `Simulateur.simuler` puis
  `revalorisation.pension_aujourd_hui`, scénario `notionnel_liberal`, sous
  les réglages de référence ; `situation_foyer` passé à « couple » et
  `taux_cotisation_liberal` aux taux des lectures, en mémoire. Le niveau de
  salaire de chaque type est trouvé par dichotomie sur la pension du droit
  en vigueur de 2026.
- **Le net** : les fonctions du modèle qui servent à
  `EffetRetour._preleve` (tranche de CSG, part déductible, impôt de 2026),
  appliquées à une personne seule qui n'a que sa pension, puis à deux
  pensions égales.
- **La bascule d'un coup** : le modèle baisse toute la pension en 2026,
  complémentaire comprise. Les chiffres sont ceux de la baisse entière.
- **Quatre carrières ne sont pas les retraités.** À pension égale, la
  baisse change du simple au double selon le régime : sur la grille, une
  pension de 2 100 à 2 300 € baisse de 24 % pour l'artisan né en 1960, de
  29 % pour le salarié au salaire moyen né en 1950, et de 47 à 50 % pour
  l'agent de conduite de la SNCF (modèle). Les quatre types sont des
  salariés du privé, les plus nombreux.
- **La LVT** suit les hypothèses L1 à L5 de la note du 7 novembre :
  capitalisation complète et immédiate, aucun abattement.

## Sources

- Le dépôt : `docs/feuille_de_route_programme.md` (décisions 29, 41, 43,
  65, 73 à 75, 79 à 81, 88, 89) ; les notes `2026-11-09-cta.md`,
  `2026-11-07-recettes-tva-lvt.md`, `2026-11-07-deux-lectures-au-modele.md`
  et `2026-11-09-pensions-qui-montent.md` ;
  `src/retraite_notionnelle/restitution.py` ;
  `data/reference/legislation/prelevements_remuneration.yaml` ;
  `data/reference/macro/distribution_pensions.csv`.
- DGFiP Statistiques n° 46, mai 2026, « En 2025, la taxe foncière progresse
  de 2,4 % », tableaux 1 et 2 :
  https://www.impots.gouv.fr/dgfip-statistiques-en-2025-la-taxe-fonciere-progresse-de-24
- Service-public.fr, fiche F59, exonérations de taxe foncière des personnes
  âgées : https://www.service-public.gouv.fr/particuliers/vosdroits/F59 ;
  LégiFiscal, plafonds de 2026 :
  https://www.legifiscal.fr/actualites-fiscales/4551-exoneration-degrevement-taxe-fonciere-2026-publication-plafonds-revenus.html
- COR, séance du 5 février 2026, document n° 6, patrimoine des retraités :
  https://www.cor-retraites.fr/sites/default/files/2026-02/Doc_06_Patrimoine_SGCOR.pdf
- Insee, « Détention de la résidence principale », *Les revenus et le
  patrimoine des ménages*, édition 2024 :
  https://www.insee.fr/fr/statistiques/7941429
- Selectra, la CTA, page mise à jour le 19 août 2026, et l'arrêté du
  26 juin 2026 : https://selectra.info/energie/taxes/cta ;
  https://selectra.info/energie/actualites/marche/baisse-cta-gaz-annulee-juillet-2026
- À relire au texte : l'arrêté du 26 juin 2026 sur le coefficient de la CTA
  du gaz ; l'abonnement de distribution du gaz au 1er juillet 2026, à la
  délibération de la CRE ; les articles 1390 à 1391 B ter du code général
  des impôts.

## Ce que le propriétaire tranche

1. **Le message de la décision 89.** Tel que le programme est décidé, « une
   moindre baisse » n'est vraie pour aucun retraité au-dessus du plancher :
   23 € par an face à 3 600 à 7 700 €, et une hausse pour le propriétaire.
   La note propose de ne pas l'écrire au site, et de dire à la place ce que
   le modèle montre : la pension nette baisse moins que la brute, de 20 à
   26 % quand la brute baisse de 25 à 30 % ; personne ne tombe sous
   1 050 € seul ou 800 € à deux ; plus d'un quart des retraités sont sous
   ce plancher, et leur total ne baisse pas. Le garder, ou le
   remplacer ainsi.
2. **Si la phrase doit devenir vraie, par quoi.** Aucune baisse décidée
   n'atteint les retraités, hors la CTA. Les leviers chiffrés à part : un
   abattement de la LVT sur la résidence principale (35 % du terrain pour
   la neutralité moyenne) ; la reconduction des exonérations des retraités
   modestes ; les 2,94 points de CSG des pensions, qui ne rendraient rien
   aux pensions de 1 100 € et de 1 600 €, que la baisse sort de la CSG.
   Chacun coûte au point de LVT des
   retraites ou au partage du 20 septembre : en décider un, plusieurs, ou
   aucun.
3. **La LVT du retraité modeste.** Sans abattement ni exonération, le
   propriétaire de 76 ans à 1 100 € paie 716 € de LVT là où il ne paie pas
   de taxe foncière. Reconduire ou non, dans la LVT, l'exonération des plus
   de 75 ans modestes, le dégrèvement des 65 à 75 ans et le plafonnement à
   50 % du revenu, que le Conseil constitutionnel exige sous une forme ou
   une autre (note du 7 novembre).
4. **A ou B.** Le choix ne change rien pour un retraité. Seul A laisse à la
   caisse un excédent dès 2026 (+0,7 point de PIB), qui pourrait payer une
   baisse à leur intention.
5. **Dire la prime de 2,15 % avec la baisse**, ou à part : elle retire 305
   à 779 € par an à trois des quatre retraités, plus de dix fois ce que la
   CTA leur rend.
6. **Dire la reprise sur la succession avec le plancher.** Le retraité à
   1 100 € garde 1 050 €, mais 455 € par mois deviennent une avance reprise
   sur son logement. Le chantier 8 demandait déjà de le dire avant qu'un
   adversaire ne le dise.
7. **Faire chercher la part des locataires parmi les retraités sous le
   plancher**, que le dépôt n'a pas : elle seule resserre la fourchette de
   8 à 19 %. La note `2026-11-09-pensions-qui-montent.md` compte déjà ces
   retraités, 26,9 %, pour la décision 90.
