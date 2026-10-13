# La carte du dépôt, en schémas

Le propriétaire ne s'y retrouvait plus : beaucoup de documents, dix-huit
actions ouvertes, et rien qui montre d'un coup d'œil comment les pièces
s'emboîtent. Il a demandé, le 13 octobre 2026, une vue d'ensemble visuelle,
sur le dépôt, qui lui serve à suivre l'avancement, mais hors du site.

Ce qui est fait :

- `docs/carte_du_depot.md` : quatre schémas Mermaid, que GitHub dessine. D'où
  viennent les chiffres ; une visite sur le site ; les six scénarios, avec le
  tableau des couches de chaque univers et les deux façons de calculer une
  pension ; d'une session à la mise en ligne. Puis où suivre l'avancement, où
  lire quoi, et le vocabulaire du dépôt.
- Le régime `etat` dans `zones.yaml` : ses chiffres sont ancrés. Les listes
  vivantes (les actions en cours, les comptes des fiches) n'y sont pas
  recopiées : la carte renvoie au tableau de bord, qui les fabrique.
- `tests/test_carte_du_depot.py`, dans la suite rapide : les chemins que la
  carte cite existent ; ses pages sont celles de `TITRES` ; chaque scénario y
  porte les couches de son univers, dans l'ordre où elles se posent ; et rien
  de ce que charge le navigateur ne nomme la carte.
- Le README la nomme dans son arborescence.

Pourquoi du Markdown, et non la page HTML d'abord dessinée pour le
propriétaire : GitHub Pages sert la racine du dépôt telle quelle, et une page
HTML sous `docs/` serait devenue une page du site. Un fichier Markdown n'y est
servi qu'en texte brut, comme les autres documents, et GitHub en dessine les
schémas. La page interactive reste une vue de session, datée, hors du dépôt.

Ce que le test ne voit pas : un schéma qui vieillit sans qu'aucun chemin,
aucune page ni aucune couche ne change, une étape de calcul ou un hook de
plus. La session qui change l'architecture relit la carte.
