# Le pilote, les erreurs tues : la différence relevée le 24 octobre n'atteint aucun lecteur, et rien n'est corrigé

**La pertinence, d'abord.** La différence existe toujours, sur `origin/main`
du 12 novembre 2026 (3944fdc) : aucun commit ne l'a traitée depuis le
24 octobre. Elle n'a pas d'effet atteignable, et le silence qu'elle élargit
est voulu, écrit et testé. Cette session n'a donc touché ni au code ni aux
tests ; elle laisse une proposition au propriétaire, sur un silence voisin.

**Où elle est.** Non dans `pilote.js`, que la demande nommait, mais dans
`contexte.js` : `departsDeLEstimation` (ligne 369) rend une liste vide à toute
erreur qui n'est ni `TypeError`, ni `ReferenceError`, ni `RangeError`, ni
`SyntaxError`. `pilote.js` porte la même garde dans `sansRefus` (ligne 225),
qui répond « rien ne s'ouvre » à un départ refusé pendant la descente vers la
carrière longue ; `balayageDeLEstimation` et le contrôle du relevé la portent
aussi. Le Python retiré (be67006^, `contexte.py`, ligne 338) n'attrapait que
`(ErreurSaisie, ValueError)`.

**Ce qu'elle tait de plus que le Python.** Le portage lève trois classes :
`ErreurSaisie` (174 fois), `Error` (213 fois), `DonneeInsuffisante` (2 fois).
Les deux premières sont le refus de la saisie et, pour l'essentiel, celui du
modèle, que le Python taisait aussi. Restent, tus ici seulement :
- `DonneeInsuffisante`. Elle ne se lève que si la fiabilité exigée dépasse
  « estimée », le plus bas des quatre niveaux (`_verifierFiabilite`,
  `Serie.valeur`). La saisie ne porte pas ce réglage : le lecteur ne peut pas
  l'atteindre.
- les `Error` qui ne sont pas un refus — une clé absente du paquet, un
  invariant. Le portage n'a pas de classe qui les distingue d'un refus du
  modèle.

**Ce qui se produit réellement.** Mesuré, par une sonde passagère dans les
deux gardes, retirée ensuite, sur 22 552 saisies : les 932 requêtes des témoins de simulations sous les trois états du
droit ; les mêmes à huit âges de départ, de 56 à 70 ans ; une grille des
74 statuts, sept générations de 1958 à 2004, trois âges de début, six âges
de départ, avec un second métier, puis trois enfants et du chômage. Toutes
les erreurs tues sont des `ErreurSaisie`. Aucune `Error` nue, aucune
`DonneeInsuffisante`, aucune faute de programme. Une mesure n'est pas une
preuve : elle dit qu'aucune carrière connue du dépôt n'atteint la différence.

**Ce que le lecteur verrait.** Tue, l'erreur ôte le bloc « Mon estimation
retraite », sans un mot ; le reste des résultats s'affiche, juste. Dans
`sansRefus`, elle arrêterait la descente et daterait le premier départ trop
tard : le seul cas où le silence donnerait un chiffre faux, que la mesure ne
rencontre pas. Remontée, comme en Python, elle serait pire : `rendre`
(`pages.js`, ligne 441) remplacerait tous les résultats par « Saisie
refusée », pour une carrière que le modèle calcule à l'âge demandé.

**Le silence est voulu.** Quatre endroits le disent : la documentation de
`departsDeLEstimation` (« vide […] quand la saisie ou le modèle refusent la
carrière à l'un des âges ») et son commentaire (« le bloc se tait plutôt que
de chiffrer une autre carrière ») ; `fauteDeProgramme` (`pages.js`,
ligne 615), la règle de tout le site, qui tient pour prévues `ErreurSaisie`,
`DonneeInsuffisante`, `KeyError` et `ValueError`, et ne laisse remonter que
les quatre classes ci-dessus ; `test_sans_depart_a_choisir_le_bloc_se_tait`
(`tests/test_estimation_du_site.py`), qui veut la page « sans le bloc ni un
refus ».

**Pourquoi rien n'est corrigé.** Resserrer la garde au seul refus
demanderait une classe pour les refus du modèle, sur 213 `throw` de modules
hors du périmètre, pour un cas que personne n'atteint ; et le test qui le
dirait ne pourrait s'écrire qu'avec une erreur fabriquée, non avec une
carrière.

**Ce que la mesure a montré à côté, pour le propriétaire.** Le silence
commun aux deux langages, lui, s'atteint. Dans 275 des saisies sondées, la
page calcule et le bloc manque, parce que la saisie refuse la carrière à l'un
des âges de l'estimation :
- un métier, une ligne de relevé, une activité après le départ ou une
  retraite progressive que la date du départ au plus tôt contredit — le
  métier qui commence à 64 ans et demi d'un départ demandé à 67 ans, que le
  test nomme ;
- un âge hors de la fourchette de la saisie : l'aide-soignante née en 1968,
  mère de trois enfants, entrée à 16 ans, qui demande un départ à 67 ans. Le
  droit date son premier départ à 30 ans et 10 mois, en 1999, et la saisie
  n'accepte un départ qu'à partir de 40 ans. Ce départ, d'une année passée,
  serait omis de toute façon, comme le taux plein, à 55 ans et demi, en 2023 ;
  son refus emporte le taux plein automatique, à 62 ans, en 2030, que le
  modèle chiffre.

Le lecteur ne sait pas pourquoi le bloc manque. Une phrase à sa place le
dirait, par exemple : « Mon estimation retraite ne se chiffre pas pour cette
carrière : au départ le plus tôt, *le message de la saisie* ». Elle change
ce que le site affiche, dans `pages.js`, et les témoins de pages : elle n'est
pas écrite, et sa forme revient au propriétaire. Ces 275 cas sont connus
ici par leurs départs vides et par le message tu ; la page n'a été rendue
pour aucun.

**Ce qui reste.**
1. Au propriétaire : dire ou non au lecteur pourquoi l'estimation manque, et
   avec quels mots ; puis, à une session du site, le second cas ci-dessus, où
   un départ chiffrable se perd avec celui que la saisie refuse.
2. Si le portage reçoit un jour une classe pour les refus du modèle, les
   quatre gardes s'y resserrent ensemble.
