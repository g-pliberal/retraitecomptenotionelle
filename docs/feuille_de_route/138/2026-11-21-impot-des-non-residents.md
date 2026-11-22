# L'impôt du retraité qui réside hors de France : la convention fiscale et l'article 197 A

**La demande.** Le propriétaire, le 21 novembre 2026 : les étrangers et les
Français de l'étranger, peu traités. L'état des lieux classe au premier rang
l'impôt du retraité résidant hors de France — environ 1,1 million de retraités
du régime général (Cnav, fin 2024) —, que le calcul après impôt imposait au
barème du résident quel que soit son État. Le propriétaire a choisi, le même
jour, de montrer l'impôt français seul, l'impôt de l'État de résidence étant
hors du modèle.

**Les textes lus.** Les conventions fiscales des six États où vivent le plus
de retraités, dans leur version consolidée d'impots.gouv.fr : Algérie
(articles 18 et 19), Belgique (12 et 10), Espagne (18 et 19), Maroc (17 et
18 bis), Portugal (19 et 20), Tunisie (25, 26 et 22), et l'Italie (18, 2,
qui laisse à la France la pension de sécurité sociale). L'article 197 A du
code général des impôts, rédaction applicable aux revenus depuis 2018, et
l'article 182 A en vigueur, lus dans l'index LEGI.

**Ce qui a été fait.**

1. `CONVENTIONS_FISCALES_DES_PENSIONS` (`moteur/js/cycle-de-vie.js`) dit, pour
   chacun des six États, qui impose la pension privée et la pension publique,
   et depuis quelle année entière de revenus ; `partsExonerees` retire de
   l'impôt français ce que la convention réserve à l'État de résidence. La
   part publique est celle des régimes de la famille `fonction_publique` et du
   RAFP, que sert un établissement public pour des services rendus à l'État.
   Un salarié du privé né en 1958, parti en 2022 au salaire moyen, au Maroc :
   l'impôt français de 2026 sur sa pension passe de 910 € à 0 €, son taux de
   remplacement après impôt de 71,5 % à 74,4 %.
2. Retouches de la relecture. Le RAFP compté pour public : part publique de
   45 % à 50 % dans l'essai à 900 € d'État, 100 € de RAFP et 1 000 € de régime
   général, sans effet aux réglages du site, qui isolent le RAFP de la
   répartition. La Tunisie : l'article 26 renvoie la pension publique à
   l'article 22, qui la laisse à la France ; le calcul ne change pas. Depuis
   les revenus de 2018, ce que la France impose l'est sans la réduction sous
   condition de revenus ni la décote, que l'article 197 A n'ouvre pas au
   non-résident : un fonctionnaire de l'État né en 1955, parti en 2016 à huit
   dixièmes du salaire moyen, au Portugal, paie 709 € d'impôt français en
   2026 au lieu de 117 €, et 952 € en 2019 au lieu de 366 €. La retenue à la
   source de l'article 182 A s'impute sur l'impôt de l'article 197 A (V) : elle
   ne change pas l'impôt de l'année.

Test : `tests/js/impot-non-resident.test.js`, cinq essais, chacun vu rouge
avant son code. Aucune des 937 simulations témoins ne bouge ; la page
`simuler_non_resident` voit son taux de remplacement après impôt du
scénario 1 passer de 73,2 % à 77,1 %.

**Ce qui reste.** La nationalité, que le modèle ne connaît pas ; l'Italie et
l'Agirc-Arrco, point de doctrine à vérifier dans le BOFiP (série
BOI-INT-CVB-ITA) ; les autres États et les conventions antérieures ; le
non-résident d'avant 2018 ; le taux minimum de l'article 197 A ;
l'abattement des personnes âgées et la CSG déductible du non-résident. Voir
`docs/limites/5-ante-ter-net-et-brut.md`.
