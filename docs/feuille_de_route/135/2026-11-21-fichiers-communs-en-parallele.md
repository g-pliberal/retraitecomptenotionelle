# Les fichiers communs en parallèle : témoins par entrée, cliquets additifs, paquet refait

**Le 21 novembre 2026, la demande.** Les chantiers du jour passaient un par
un sur `main`. Le propriétaire a demandé si les « fichiers communs » étaient
trop gros. L'étude (`/mnt/project-files/architecture/fichiers-communs/`, et
le rapport « Les fichiers communs : taille, croisements, découpage ») a
relevé les 87 publications des sessions du 18 au 21 novembre. Ce n'est pas la
taille qui sérialise.

**Ce que l'historique a montré.**

- *Les témoins sont rangés au bon grain*, une entrée par cas. Deux
  publications successives touchaient les mêmes cas pour 1 paire sur 14 de
  `simulations.json` (12 Mo, 937 cas), 2 sur 16 de `sorties.json`, 4 sur 19
  de `droit.json`, toutes dans un même chantier. Mais `-merge` gardait le
  témoin de main, et la correction de la session s'y perdait.
- *Les cliquets s'écrivent un nombre par ligne.* `redactions_sans_statut`
  (`perimetre.yaml`, 8 Ko) a été abaissé cinq fois par cinq chantiers : deux
  baisses du même compteur sont un conflit garanti, dont la bonne valeur
  n'est écrite d'aucun côté.
- *Le paquet* (`moteur/donnees.json`, 6,1 Mo) porte des agrégats sur toute
  la population : 19 paires sur 29 y partagent une clé. Le découper ne
  servirait à rien. `pousser.sh` refusait tout conflit dessus.

**Ce qui est fait**, avec l'accord du propriétaire (« Vas-y », puis « on
passe à 10 minutes » et « je suis ta recommandation »), relu sous Fable :

- Le pilote `cles` (`scripts/fusionner.py`) fusionne `simulations`,
  `sorties`, `droit`, `servis` et `valeurs` entrée par entrée. Une entrée
  changée des deux côtés reste un conflit, et le refus dit de refaire les
  témoins. `pages.json` garde `-merge`.
- Le pilote `compteurs` additionne les baisses des deux côtés, sur les seules
  lignes faites d'un nom et d'un seul nombre. Une hausse, un identifiant, une
  date restent un conflit. Le filet recompte : le test des rédactions et
  celui de l'alarme des quatorze jours y entrent. Le propriétaire avait
  d'abord approuvé un cliquet à sens unique resserré par le robot ; la
  relecture a montré qu'une hausse pouvait s'y cacher derrière une baisse pas
  encore resserrée, et il a retenu la forme additive.
- `pousser.sh` garde le paquet de main au rebasage, puis le refait des
  sources réunies dans le dernier commit de la session. Une marque,
  `.git/paquet-a-refaire`, retient tout envoi tant qu'il ne l'est pas. Refait
  sans mémoire des calculs, il a tenu 2 min 48 s : le hook de fin de tour
  passe de 120 à 600 secondes.

**Ce qui reste.** Les commits rejoués avant le dernier gardent le paquet de
main. Deux chantiers sur un même cas ou un même régime se croisent toujours,
et c'est voulu. La règle 2 du projet (un seul chantier à la fois sur les
fichiers communs) n'est pas touchée : le propriétaire veut voir le résultat
avant de l'assouplir. À relever sur une semaine d'envois : combien de refus
le rebasage évite, combien il en garde.
