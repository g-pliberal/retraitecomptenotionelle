# Étape 5 : la veille de la base

**Le 3 novembre 2026, ce qui est fait.**

- *La veille*, `scripts/fetch/cnav_veille.py`, que `python scripts/veille_droit.py`
  imprime entre ses sources et le rappel du journal : elle compare la base au
  registre, sans l'écrire. Elle demande, d'un appel chacune, les collections
  que l'API date — barèmes, exposés, les trois des fenêtres d'information, les
  avis de mise à jour — et les listes, qu'elle ne date pas ; les dernières
  circulaires (`/reference/dernieresCirculaires/`, les quinze dernières de la
  Cnav que la base met en avant) ; la recherche, à l'année de la veille et à
  la précédente. Elle dit, par genre, ce que le registre ne porte pas ; ce dont
  la date a changé depuis son sort, avec le script ou le renvoi qui le lit, et
  la date du sort et celle du jour ; ce dont la date a changé quand il attend
  encore d'être lu ; ce que la base ne sert plus. Puis les circulaires et les
  références que le registre ne porte pas, ou sans titre, le geste qui les
  inscrit, et ce que le registre garde à lire. Une quinzaine de mégaoctets, en
  treize secondes ; hors réseau, deux secondes, les dernières circulaires se
  demandant d'abord, deux fois au plus ; `--sans-cnav` s'en passe. La
  procédure, `docs/veille_droit.md`, le dit.
- *Le récupérateur*, `scripts/fetch/cnav_legislation.py`, part aussi des
  dernières circulaires et de la recherche des deux dernières années : une
  circulaire que rien ne lie encore entre au registre par une lecture
  ordinaire, sans attendre la recherche entière.
- *Relire ce qui a changé depuis son sort* : la session qui le relit écrit au
  registre le sort et la date de la version lue, que la veille lui donne ; le
  récupérateur la garde ensuite. Ce qui attend encore d'être lu prend la date
  du jour à chaque lecture.
- *Les tests*, sept de plus dans `tests/test_cnav_legislation.py` : la
  comparaison, les références nouvelles, ce que la veille demande à la base et
  dans quel ordre, ce que la veille du droit en imprime, la base qui ne répond
  pas ou d'une forme nouvelle, les racines récentes du récupérateur ; et la
  ligne
  `cnav_legislation_portail` du vivier, qui doit passer `epuise` le jour où le
  registre n'a plus rien à lire : la session qui lira le dernier objet le verra
  rougir.

**Ce que la veille a trouvé, le 3 novembre 2026**, contre le registre des
étapes 1 à 3 : la circulaire Cnav 2026/34 du 30 octobre, « Droit de
rectification des informations ayant une incidence sur le montant des indus »,
que rien ne lie — ni barème, ni exposé, ni avis : seules les dernières
circulaires et la recherche de 2026 la servent — ; et un exposé à lire,
« Sommes payées à tort »
(`paiement_prescription_recouvrement_precription_somme_payee_tort_ex.aspx`),
redaté le 29 octobre, qui cite désormais la circulaire 2022/24 et non plus la
2022/11. Aucun barème, aucune liste, aucune fenêtre ni aucun avis neuf, changé
depuis son sort ou parti. Le récupérateur, relancé avec la recherche entière —
1 792 requêtes, aucune sans réponse, aucune référence que rien ne lie hors de
la circulaire —, a inscrit la circulaire à lire, sans thème, pour l'étape 6 ;
redaté l'exposé ; déplacé de la circulaire 2022/11 à la 2022/24 le thème
« Paiement » qu'il leur donne ; rien d'autre. Relancée, la veille ne voit plus
rien de neuf. Le registre porte 9 541 objets, dont 8 543 à lire.

**Ce que la veille ne voit pas.** Les documents joints, que le site sert un
par un hors de l'API, et sans `HEAD` : six cents requêtes, que le
récupérateur fait à chaque lecture et dont il dit ce qui a changé. Une liste,
que l'API ne date pas — sa `date_import` est, pour toutes, celle de l'import
de la nuit — : la veille n'en voit que l'arrivée et le départ. Une référence,
que l'API ne date pas non plus : une circulaire refondue sous son nom ne se
voit pas. Un texte ancien que la base ajouterait : la recherche des deux
dernières années ne le sert pas, la recherche entière, `--chercher`, si.

**Ce qui reste.** L'étape est faite. Les étapes 4 et 6 vident le registre ; le
jour où il n'a plus rien à lire, la ligne du vivier passe `epuise`, et
l'action se clôt. Aucun fichier d'une autre file n'a été touché :
`scripts/veille_droit.py` et `docs/veille_droit.md`, qu'aucune file ne tient,
ne gagnent que la section de la Cnav ; du vivier partagé,
`data/sources_a_explorer.yaml`, seule la ligne `cnav_legislation_portail` a
changé.
