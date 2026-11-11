---
paths:
  - "docs/feuille_de_route.md"
  - "docs/feuille_de_route/**"
  - "docs/architecture.md"
  - "docs/architecture/**"
  - "docs/limites.md"
  - "docs/limites/**"
  - "data/reference/legislation/journal_de_veille/**"
---

# Règle de la documentation : ce qu'une étape écrit, et où

Claude Code charge cette règle à la première lecture ou écriture d'un fichier
de la feuille de route, de ses notes, de l'architecture, des limites ou du
journal de veille, en plus de `CLAUDE.md`, qui dit où vont la note et l'entrée
du journal, et ce que tient un message de commit. Les régimes de la prose et
la conservation : `prose.md`.

- **La documentation, au plus court** : une note de feuille de route par
  étape, au commit qui la clôt, et non une par sous-partie, dans un fichier à
  elle : `docs/feuille_de_route/<action>/<AAAA-MM-JJ>-<sujet>.md`
  (`148/2026-10-06-etape-2.md`), qui s'ouvre sur son titre ; les notes écrites
  avant le 6 octobre 2026 restent dans la feuille de route. Une session qui
  s'arrête en cours d'étape dit seulement où, dans le bloc « Reprise ». Une
  version de l'architecture par domaine, à sa clôture, ou par décision hors
  domaine, dans un fichier à elle :
  `docs/architecture/versions/<AAAA-MM-JJ>-<sujet>.md`, qui s'ouvre sur
  « # Version du <date> : <sujet> » (action 149). Elle ne porte pas de numéro,
  que deux sessions prendraient ensemble, et se cite par sa date et son
  sujet ; ni l'en-tête du document ni sa liste, close à la 5.37, ne se
  touchent. Les fiches et les limites (`docs/limites/`, une partie par
  fichier) une fois, à la fin de l'étape, sauf ce qu'un test exige plus tôt.
  Le journal de veille garde sa règle.
- **Le bloc « Reprise »**, que récrit la session qui avance l'action
  (`CLAUDE.md`, « Économiser le contexte »), s'écrit pour un lecteur
  intelligent mais sans contexte — la session neuve, qui n'a vu ni les
  fichiers ni le raisonnement de celle qui l'écrit — et se comprend seul :
  l'essentiel dans les premières phrases ; des phrases entières et courtes,
  une idée chacune, en mots ordinaires ; aucun terme ni sigle forgé pendant le
  travail, nom d'étape ou empreinte de commit : dire ce que la chose est. Ce
  qui ne tient pas va dans la note, non dans une phrase plus dense. C'est le
  seul paragraphe d'une action qui se récrit. Quand les étapes d'une action se
  mènent en parallèle, son bloc le dit, et aucune session ne le récrit plus :
  chaque étape inachevée tient le sien, sous le titre de sa note, et l'ôte en
  finissant.
- **Une action qui se clôt** passe, telle quelle, à la fin de
  `docs/archives/feuille_de_route.md`, et le dossier de ses notes sous
  `docs/archives/feuille_de_route/`.
