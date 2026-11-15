# Essai : proposer par le code les bornes d'application d'une version d'article

**La demande, le 15 novembre 2026.** Le propriétaire, méfiant envers « ce
genre de solution magique », veut un essai avant tout outil : un code
peut-il retrouver à quelles pensions s'applique chaque version d'un article
(date d'effet, génération), qu'une session lit aujourd'hui à la main ?
Rien n'entre dans le code de production ; le prototype, jetable, est resté
hors du dépôt.

**Le lien entre une version et la loi qui l'a écrite.** Il existe dans les
fichiers de la DILA : chaque article de LEGI porte des balises `<LIEN
typelien="MODIFIE" …>` qui nomment le texte modificateur (vérifié par le
lecteur de LEGI de Legilibre, `legi.py`, qui les range dans une table
`liens`). Mais l'index du dépôt ne les garde pas (note
`2026-11-03-etape-1.md`), et la DILA n'est pas joignable depuis une session
web : le lien n'a pas pu être essayé sur des données réelles. Le prototype le
remplace par une recherche dans le JORF.

**Ce que l'essai a trouvé d'abord.** La NOTA que la DILA place en tête d'une
version, et que l'index garde, écrit souvent déjà la borne : « Conformément
au VI de l'article 105 de la loi n° 2025-1403 du 30 décembre 2025, ces
dispositions […] s'appliquent aux pensions prenant effet à compter du
1er septembre 2026. » Le prototype lit donc la NOTA d'abord, en écartant une
NOTA périmée (héritée d'une version plus ancienne), puis, à défaut, cherche
dans le JORF le texte qui modifie l'article et ses phrases d'application.

**Le résultat, sur 43 versions du code de la sécurité sociale.**

| Échantillon | Versions | Justes | Fausses | Manquées |
|---|---|---|---|---|
| Connu, qui a servi à régler le prototype (L. 161-17-2, L. 161-17-3, D. 161-2-1-9, D. 351-1-1) | 17 | 13 | 2 | 2 |
| De contrôle, non vu avant (L. 351-1-1, L. 351-10, D. 351-1-2, L. 161-22-1-5, L. 351-1-3) | 26 | 12 | 4 | 10 |

Par chemin, les deux échantillons ensemble :

- **Par la NOTA** : 22 versions, 21 justes. La seule fausse (L. 351-1-1 au
  31 décembre 2025) tient à une NOTA qui dit « ladite loi » sans en redire le
  numéro, que le prototype ne savait pas lire.
- **Par le JORF** : 21 versions, 4 justes, 5 fausses, 12 manquées ou
  signalées « à lire ». Les fausses prennent la phrase d'application d'un
  autre article du même texte (« Les dispositions de l'article 2 du présent
  décret entrent en vigueur au 1er janvier 2012 », quand c'est l'article 1er
  qui modifie D. 161-2-1-9). Les manquées sont surtout les versions anciennes.

**Où il y a une NOTA.** Sur les 750 versions des articles de retraite du code
(L. 161-17, D. 161-2, L. et D. 351, R. 351, L. et D. 173), une phrase
d'application se lit en tête de 126 sur 195 depuis 2020, 33 sur 249 de 2010
à 2019, 3 sur 306 avant 2010.

**Ce qu'aucun outil version par version ne voit.** La suspension de 2025 a
changé l'âge légal sans écrire de nouvelle version de D. 161-2-1-9 : la loi
déroge au décret, qui reste en l'état. Une borne qui dépend d'un autre texte
reste une lecture humaine.

**Le temps.** Le prototype rend les 43 propositions en une seconde.
Une borne lue à la main demande de trois à cinq minutes ; vérifier une
proposition de NOTA, une trentaine de secondes. Le gain est réel sur les
versions récentes, nul sur les anciennes, et l'outil `dila_cherche.py --le`
imprime déjà ces phrases pour une date donnée.

**La conclusion.** Lire les bornes dans la loi modificatrice ne vaut pas la
peine : moins d'une proposition sur cinq est juste, et les fausses ont
l'air aussi sûres que les justes. Lire la NOTA, en revanche, est fiable (21 sur
22) et simple : une table, version par version, de la phrase d'application
que la DILA a déjà écrite, ou « pas de NOTA : à lire ». C'est une aide à la
lecture, pas une source : la phrase reste à confirmer, et les versions sans
NOTA restent à lire. La décision de la construire revient au propriétaire.
