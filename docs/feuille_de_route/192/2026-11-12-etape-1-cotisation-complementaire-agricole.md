# Étape 1 : la cotisation de retraite complémentaire du chef d'exploitation agricole, depuis 2026

**Reprise, au 12 novembre 2026.** Rien n'est commencé. Depuis le 1er janvier
2026, la cotisation de retraite complémentaire du chef d'exploitation agricole
a deux parts : 4 % comme avant, et une seconde, de 1 % à 3 % selon le revenu
rapporté au plafond de la sécurité sociale. Les points se tirent de la
cotisation payée, donc la seconde part en achète. Le modèle garde 4 % et 133
points. À faire, le test d'abord : lire les articles D. 732-165 et D. 732-155
du code rural et le barème de la MSA, poser un cas à la main, puis écrire la
règle dans le modèle et son portage, et mettre la fiche à jour. Restent à lire
avant d'écrire : l'arrondi des points et l'année incomplète.

**La demande, le 12 novembre 2026.** La passe de lecture de l'action 184 a
trouvé des points que le modèle n'applique pas ou qu'elle n'a pas pu vérifier
(note `184/2026-11-12-etape-6-bilan-de-la-passe.md`). La session
d'orchestration les a listés au propriétaire, qui a répondu : « Fait une étape
pour chaque point du modèle ». Celle-ci en est une.

**Ce qui est su.** Le lot des non-salariés agricoles l'a lu
(`184/2026-11-12-etape-6-non-salaries-agricoles.md`, « Ce qui change une règle
») : article D. 732-165, I, du code rural, rédaction du décret n° 2024-688 du
5 juillet 2024 (LEGIARTI000049904700), cotisations des périodes courant depuis
le 1er janvier 2026 ; article D. 732-155 pour les points, P = C / [(1 820 SMIC
× 4 %) / 133]. Posé à la main par ce lot, à revérifier : à un plafond de
revenu en 2026 (48 060 €), 2 787,48 € de cotisation et non 1 922,40 €, environ
424 points et non 292. Collaborateur et aide familial inchangés. La fiche
`assiette_minimale_agricole` le déclare (`textes_a_rattacher`,
`sources.a_relire`).

**Ce qu'il y a à faire.**

1. Relire les deux articles dans l'index, et le barème 2026 de la MSA ; lever
   l'arrondi des points et le cas de l'année incomplète, ou dire ce qui reste
   ouvert.

2. Le test, vu rouge : la cotisation et les points d'un chef d'exploitation en
   2026, à deux niveaux de revenu au moins, valeurs posées à la main.

3. La règle, dans le modèle et son portage, datée du 1er janvier 2026 ; les
   années d'avant ne bougent pas.

4. La fiche, ses versions et ses sources ; la limite, s'il en reste une.

**Fini quand** le scénario 1 sert les points de 2026 que le texte donne, que
la cotisation versée au compte des scénarios rétroactifs suit, et que la fiche
ne déclare plus cet écart.

**Les règles de l'étape.** C'est une règle du scénario 1 : la session se mène
sur Fable 5.2, ouvre par `python scripts/veille_droit.py` et suit
`docs/veille_droit.md`. Le test d'abord, sa valeur attendue tirée du texte ou
d'un calcul posé à la main. Le moteur est en chantier dans deux autres
actions, qui le séparent du site et lui font lire les règles dans les fiches
(`python scripts/reprise.py 187`, puis `191`) : lire leurs blocs avant de
toucher au moteur, et ne pas défaire ce qu'elles ont posé. Une seule session à
la fois écrit dans le modèle et son portage.
