# Note de décision 0004 — une adresse par page

*Proposée le 26 octobre 2026 par la session de l'action 174, à valider par le
propriétaire. L'analyse complète, et ce qu'il fallait modifier, est dans
`docs/feuille_de_route/174/2026-10-26-proposition-des-adresses.md`.*

*Validée le 26 octobre 2026 par le propriétaire, telle quelle : « 1. Oui ».
Le pré-rendu des pages se commite dans le dépôt, que la copie du parti recopie
tel quel ; l'adresse que les moteurs de recherche retiennent est celle de la
copie, sous `partiliberalfrancais.fr/retraite/`.*

## Le problème

Le serveur ne reçoit jamais ce qui suit `#` dans une adresse. Pour lui, les
neuf pages du site n'en faisaient qu'une, `index.html`, qui choisissait la
sienne une fois ses scripts chargés et le moteur prêt. Il ne pouvait donc
servir à aucune son propre contenu — ni son titre, ni sa description, ni le
texte qu'on lit avant le moteur. Or c'est ce contenu tout fait, affiché sans
attendre le moteur, qui porte la note de Performance de Lighthouse à 100 : 98 à
100 sur des pages figées, contre 59 à 60 en mobile sur le site en ligne.

## La décision

**La page dans le chemin, le lecteur derrière le `#`.**

- L'accueil reste la racine du site. Chaque autre page est un dossier de son
  nom, qui porte son `index.html` : `simuler/`, `cout/`, `risque/`,
  `partager/`, `saviez-vous/`, `cas-types/`, `avantages/`, `methode/`. Tout
  serveur statique le sert sans réglage, et redirige `cout` vers `cout/` :
  c'est la seule forme qui ne demande rien au serveur de la copie du parti.
- Ce qui appartient au lecteur — sa carrière, ses réglages — reste derrière le
  `#`, que le navigateur ne transmet à aucun serveur : `cout/#indexation=prix`,
  `simuler/#naissance=1965-03-01&sexe=H`. La promesse « rien n'est envoyé à un
  serveur » tient comme avant. Un mot sans `=` y désigne une section de la
  page : `methode/#sources`.
- **Les anciennes adresses restent valides, toutes.** Une ancienne adresse a
  la forme `#/cout?indexation=prix`, et le serveur y sert l'accueil, quoi que
  porte la suite : c'est le routeur qui la lit, la remplace sans l'empiler par
  la nouvelle (`cout/#indexation=prix`) et charge la page. Les deux pages
  fondues le 23 septembre 2026 gardent leur sens : `#/trajectoire` mène aux
  résultats du simulateur, cumul ouvert, et `#/donnees` à la partie Sources de
  la page Méthode.
- Les liens que les pages écrivent sont relatifs à leur page (`../cout/`) :
  le site vit à deux adresses, GitHub Pages et la copie du parti, sans en
  connaître aucune.
- Les huit pages en dossier sont fabriquées depuis `index.html` par
  `scripts/construire_pages.py`, commitées, jamais retouchées à la main.

| Page | Avant | Désormais |
|---|---|---|
| Programme | `…/` | `…/`, inchangée |
| Simuler | `…/#/simuler` | `…/simuler/` |
| Une simulation | `…/#/simuler?naissance=…` | `…/simuler/#naissance=…` |
| Les autres pages | `…/#/cout`, `#/risque`, `#/partager`, `#/saviez-vous`, `#/cas-types`, `#/avantages`, `#/methode` | `…/cout/`, `…/risque/`, `…/partager/`, `…/saviez-vous/`, `…/cas-types/`, `…/avantages/`, `…/methode/` |
| Une page sous d'autres réglages | `…/#/cout?indexation=prix` | `…/cout/#indexation=prix` |

## Ce que cela change pour le lecteur

Passer d'une page à l'autre charge une page, au lieu de changer l'ancre : le
moteur se réinitialise à chaque page (mesuré le 26 octobre 2026 : 0,7 à 1,0 s
pour une page de contenu, 2,4 s pour des résultats, sur un poste de bureau sans
bridage). Le pré-rendu, étape suivante de l'action, ramène les pages de contenu
à l'affichage immédiat ; les résultats, et une page vue sous d'autres réglages,
attendent encore le moteur. Un lien vers la page où l'on est ne recharge rien.

## Ce que cette décision ne tranche pas

Les résultats d'une simulation, dont la note de Performance reste sous 100
tant que le moteur calcule avant d'afficher : décision 3 de l'action 174, au
propriétaire.

## Les retouches de l'hôte

La copie du site du parti retouche `index.html` (`plf-theme.css`, le bandeau
`plf-back-link`) : avec une page par dossier, il faudrait les refaire dans
chacune. Le document d'intégration lui recommande de les abandonner depuis le
17 septembre 2026 ; ce sera le moment, et la classe `plf-embedded` de son
cadre doit être posée à chaque chargement du cadre. À régler avec lui à sa
prochaine copie.
