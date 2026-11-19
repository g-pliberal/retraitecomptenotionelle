# Le sixième cliquet de la note 0009 : l'alarme « loi modifiée »

Le 19 novembre 2026, le propriétaire demande que le dépôt fasse mieux que les
autres modèles, et choisit d'ajouter à la note de décision 0009, avant sa
première étape, un sixième cliquet. L'amendement est écrit à la fin de la
note ; le script de ses comptes et leur sortie du jour sont sous
`docs/decisions/0009/sixieme-cliquet/`. Aucun test, aucune fiche, aucune règle
ne change : le document d'architecture suit, par sa version du 19 novembre
2026 (§ 6.6).

**Ce que la vérification a trouvé.** La moitié de l'alarme existait depuis
l'action 184 : l'inscription du lundi, et la ligne de la veille pour une
rédaction non lue. Deux trous restaient. Rien n'échouait. Et une rédaction
qu'une fiche avait rattachée ne se montrait plus aux autres fiches du même
article : la veille montrait une fiche, quand 83 couples d'une fiche et d'une
rédaction en vigueur ou à venir étaient sans un mot de la fiche, 48 rédactions
pour 51 fiches. 435 autres couples sont la dette connue : la fiche cite la
rédaction sans l'avoir coupée en version.

**Ce que l'amendement décide.**

1. Chaque fiche répond pour elle-même à toute rédaction en vigueur ou à venir
   d'un article qu'elle cite : par une de ses versions, ou par une
   déclaration « sans effet ».
2. Une rédaction apportée par l'index après la pose du cliquet fait échouer
   la suite quatorze jours après son inscription, si une fiche qui cite son
   article n'a pas répondu. Le propriétaire a choisi ce délai plutôt qu'un
   échec immédiat : l'inscription du lundi est commitée par GitHub, et `main`
   aurait rougi sans qu'aucune session y soit pour rien.
3. Les rédactions d'avant la pose font une dette, en deux nombres qui ne
   peuvent que baisser.
4. Une fiche qui déclare une réforme a une version qui commence à sa date,
   ou une liste dit où la réforme est portée. Sur 136 couples, 40 ont cette
   version ; l'égalité des dates ne suffit pas, une réforme pouvant
   s'appliquer plus tard dans un régime.

**L'étape 1 se mène en deux sessions.** La première pose les cinq cliquets et
la garde de l'âge du taux plein, comme le second rectificatif le dit. La
seconde pose le sixième : deux tests, deux fonctions de la carte
(`noyau/textes.py`, `noyau/carte.py`), deux nombres dans
`data/reference/textes/perimetre.yaml` et une liste. Elle refait les comptes
le jour même, la liste bougeant chaque lundi, et met à jour
`docs/veille_droit.md`, qui décrit encore la veille d'avant. Elle ne touche
ni au workflow du lundi ni aux hooks.

**Ce qui attend le propriétaire.** Le « reprends » de l'étape 1. Puis, hors
de l'étape, la lecture des 83 rédactions dont les fiches ne disent rien, 18
d'entre elles commençant en 2026 ou après : une à deux sessions, chaque
réponse étant une lecture du droit. La mise à jour de KALI le lundi, sans
laquelle l'alarme n'entend pas les avenants de l'Agirc-Arrco.

**Ce que tenir l'alarme coûtera.** Les articles cités ont 191 rédactions qui
commencent en 2026, dont 104 au 1er janvier et 37 au 1er juillet : autant de
réponses à écrire par an, le plus souvent « sans effet ».
