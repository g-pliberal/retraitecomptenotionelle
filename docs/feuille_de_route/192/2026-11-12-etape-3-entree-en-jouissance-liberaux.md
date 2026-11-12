# Étape 3 : la date d'effet de la pension de base des libéraux, au trimestre civil

**Reprise, au 12 novembre 2026.** Rien n'est commencé, et rien n'est établi :
c'est d'abord une vérification. Le code de la sécurité sociale fait partir la
pension de base des professions libérales du premier jour du trimestre civil
qui suit la demande ; depuis le 5 mars 2023, du premier jour du mois pour la
seule Cipav. Aucune fiche ne le dit pour la pension en points, servie depuis
2004, et personne n'a regardé ce que fait le moteur. À faire : lire l'article
R. 643-6 et ses rédactions, regarder ce que le moteur date, et, s'il y a un
écart, l'écrire, le test d'abord. L'enjeu est d'au plus deux mois de pension.
S'il n'y a pas d'écart, la fiche le dit et l'étape se clôt.

**La demande, le 12 novembre 2026.** La passe de lecture de l'action 184 a
trouvé des points que le modèle n'applique pas ou qu'elle n'a pas pu vérifier
(note `184/2026-11-12-etape-6-bilan-de-la-passe.md`). La session
d'orchestration les a listés au propriétaire, qui a répondu : « Fait une étape
pour chaque point du modèle ». Celle-ci en est une.

**Ce qui est su.** Le lot du code de la sécurité sociale l'a relevé
(`184/2026-11-12-etape-6-code-de-la-securite-sociale.md`, « Ce qui change une
règle », point 1) : article R. 643-6 (LEGIARTI000047265890, en vigueur), règle
depuis 2004, dérogation pour la Cipav depuis le 5 mars 2023. La fiche
`cnavpl_allocation_avant_2004` ne déclare l'écart qu'avant 2004, où le modèle
date au mois.

**Ce qu'il y a à faire.**

1. Lire R. 643-6 dans ses rédactions, et ce que les sections publient de la
   date d'effet.

2. Regarder ce que le moteur fait de la date d'effet d'une pension de base
   libérale liquidée après 2004, par un cas joué.

3. S'il y a un écart : le test, vu rouge, puis la règle, la Cipav à part
   depuis mars 2023 ; sinon, la fiche le dit.

**Fini quand** la fiche dit la règle de date d'effet et que le moteur
l'applique, ou que la limite est dite.

**Les règles de l'étape.** C'est une règle du scénario 1 : la session se mène
sur Fable 5.2, ouvre par `python scripts/veille_droit.py` et suit
`docs/veille_droit.md`. Le test d'abord, sa valeur attendue tirée du texte ou
d'un calcul posé à la main. Le moteur est en chantier dans deux autres
actions, qui le séparent du site et lui font lire les règles dans les fiches
(`python scripts/reprise.py 187`, puis `191`) : lire leurs blocs avant de
toucher au moteur, et ne pas défaire ce qu'elles ont posé. Une seule session à
la fois écrit dans le modèle et son portage.
