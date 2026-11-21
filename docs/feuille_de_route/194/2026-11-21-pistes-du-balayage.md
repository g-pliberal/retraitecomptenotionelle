# Action 194 : trois pistes du balayage expliquées, deux erreurs du moteur

Le 21 novembre 2026, sur Opus 5.5, à la suite de l'étude des outils de
vérification. Aucune règle n'est écrite ni aucun résultat déplacé : la session
rejoue des cas du balayage (`2026-11-21-etape-b-les-filets.md`) sur le moteur
du jour, par le pont, lit les textes dans l'index LEGI et classe chaque groupe.
Les deux corrections restent à faire, chacune par son test d'abord.

## Le complément différentiel des exploitants : voulu par le texte

1 043 baisses, toutes du cas de l'exploitant agricole, aucune de plus de
2,8 millionièmes de la pension. Né en janvier 1959, parti à 64 ans et 3 mois
en avril 2023 : 13 663,72 € par an ; un salaire 20 % plus haut en 1980,
13 663,47 €. Le plafond de toutes les pensions joue (L. 732-63, V ;
D. 732-166-5-1) : 85 % de 1 820 heures au SMIC net agricole de 2023
(8,8323 €), 13 663,57 € par an. Le complément le ramène à ce plafond, puis
se convertit en points arrondis à l'entier le plus proche, la demie comptée
pour un (D. 732-166-6, rédaction de 2015, toujours en vigueur en 2023) : le
total oscille autour du plafond d'au plus un demi-point (0,18 € au point de
0,3642 €). Rejoué : 2 956 points de complément au départ (13 663,72 €, 0,15 €
au-dessus du plafond), 2 908 avec la hausse (13 663,47 €, 0,10 € en
dessous). Tout écart du groupe tient dans un point (2,7 millionièmes à ce
plafond). C'est l'arrondi du texte, non une erreur ; une ligne de
`baisses_legales.yaml` peut l'admettre, bornée à un point de RCO.

Une lecture reste ouverte, sans enjeu : D. 732-166-6 convertit « le montant
déterminé en application des articles D. 732-166-4 et D. 732-166-5 », sans
nommer la réduction du V de L. 732-63. Si la caisse réduisait après la
conversion, le total tomberait pile au plafond. L'écart est de moins de 0,18 €
par an.

## La surcote des régimes spéciaux : une erreur du moteur

Agent des IEG né en février, mars ou avril 1954, parti à 63 ans et 9 mois :
14, 15 et 14 trimestres de surcote. Chacun a pourtant 45 mois de services
après ses soixante ans, soit 15 trimestres entiers. Né en avril 1954 :
42 929,24 € par an, au taux de 88,125 % ; le texte donne 89,0625 %, soit
43 385,93 € (+456,69 €, +1,1 %). Né en février : 42 236,56 € au lieu de
42 685,88 €.

Le texte : les trimestres de la surcote sont ceux « d'assurance, au sens du
III ci-après, cotisés et effectués après le 1er juillet 2008, au-delà de
l'âge », et « sont pris en compte pour ce calcul les trimestres entiers
cotisés » (annexe 3 du statut des IEG, article 10, II) ; les services
sédentaires « sont comptés pour leur durée » (article 2). Le même alinéa est
à la SNCF, à la RATP, à la CRPCEN, à la Comédie-Française et à l'Opéra.

Le moteur (`trimestresDeSurcoteRegimesSpeciaux`, dans
`moteur/js/droit/liquider.js`, par `trimestresDeLaLigneEntre` de
`compter.js`) compte les trimestres de chaque année civile, puis les étale
sur ses mois : l'année du départ ne garde que ses trimestres entiers écoulés
(trois pour onze mois, aucun pour un mois), et la fraction perdue se retranche
de la surcote. Né en février : mars 2014 à novembre 2017, 3,33 + 8 + 3 =
14,33 trimestres ; en mars, 15 ; en avril, 14,67. La correction : compter la
durée des services d'après l'âge au mois, puis ne garder que les trimestres
entiers du total. Elle touche les six régimes de la fonction, et
`coefficientSurcoteRegimesSpeciaux`, qui compte de même les trimestres
d'après 2009. À vérifier en la faisant : la fonction publique, dont la
surcote passe aussi par `trimestresDeLaLigneEntre`.

## Une pension déjà servie, menée dans l'avenir : une erreur du moteur

Non relevée par la note des filets : 34 baisses du contractuel public, une
par génération de 1957 à 1990, parti à 70 ans et 3 mois plutôt qu'à 70 ans,
de 0,55 % à 14,1 % de la pension. Au-delà de la limite d'âge, sa pension de
l'Ircantec est servie depuis le mois qui suit ses soixante-dix ans, et le
moteur la mène au départ déclaré (`menerAuMois`, dans
`moteur/js/revalorisation.js`). Né en janvier 1957 : 9 867,89 € servis en
février 2027, 9 698,17 € « au départ » en mai (−1,7 %), alors que l'Ircantec
ne revalorise qu'en janvier. Né en 1990 : 20 124,14 € en février 2060,
11 156,99 € au départ (−45 %).

La cause, lue dans le moteur : `PensionServie.coefficient` mène une pension
de points par le rapport de la valeur du point à l'échéance à celle du
départ, en s'arrêtant à la dernière valeur publiée (2026 pour l'Ircantec),
puis par la revalorisation générale. Quand le départ est lui-même après cette
dernière valeur, le rapport prend la valeur publiée de 2026 (0,56053 €) sur
la valeur projetée du départ (0,570339 € en 2027) : il fait baisser la
pension, d'autant plus que le départ est loin. Toute pension de points
servie avant un départ ultérieur y passe : départs à des dates différentes
(`droit/departs.js`), retraite progressive (`droit/progressive.js`), seconde
pension (`droit/seconde.js`). La correction : quand le départ suit la
dernière valeur publiée, mener la pension par la seule revalorisation
générale du départ à l'échéance (ou par le rapport des valeurs projetées),
jamais par une valeur antérieure au départ. Son test : la pension de
l'Ircantec servie en février 2027 vaut autant en mai 2027.

## Ce qui reste

- Les deux corrections, chacune une étape, le test d'abord ; elles changent
  des règles du scénario 1, à mener sur Fable 5.2 (`CLAUDE.md`), et les
  témoins : à publier quand `main` est libre.
- La ligne de `baisses_legales.yaml` pour le complément différentiel.
- La première famille (le dernier traitement au 1er février, 2 000 pensions)
  n'est pas lue ici ; elle reste une question de texte.
