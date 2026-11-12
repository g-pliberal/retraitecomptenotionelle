# Étape 5 : le cumul d'une pension militaire et d'un emploi, pour les pensions prises à compter de 2027

**Reprise, au 12 novembre 2026.** Rien n'est commencé. Pour une première
pension de base prise à compter du 1er janvier 2027, la loi laisse la pension
militaire se cumuler entièrement avec un emploi privé ; elle ne la plafonne
que devant un employeur public, avec des exceptions. Le modèle applique à
toute pension de la fonction publique les mêmes trois régimes selon l'âge,
sans regarder si elle est militaire : le militaire parti tôt et salarié du
privé y perd une pension que le droit lui laisse. Cela a été lu dans le code,
non rejoué. À faire, le test d'abord : lire l'article L. 86 du code des
pensions et les articles du code de la sécurité sociale qu'il met en jeu,
rejouer le cas, puis écrire la règle.

**La demande, le 12 novembre 2026.** La passe de lecture de l'action 184 a
trouvé des points que le modèle n'applique pas ou qu'elle n'a pas pu vérifier
(note `184/2026-11-12-etape-6-bilan-de-la-passe.md`). La session
d'orchestration les a listés au propriétaire, qui a répondu : « Fait une étape
pour chaque point du modèle ». Celle-ci en est une.

**Ce qui est su.** Le lot de la fonction publique l'a lu
(`184/2026-11-12-etape-6-fonction-publique.md`, « Ce qui change une règle »,
point 1) : article L. 86 du code des pensions (LEGIARTI000053279638, loi n°
2025-1403, article 102) ; articles L. 161-22, III, C, 1°, et L. 161-22-1-2, 4°
et 5°, du code de la sécurité sociale. Le plafond devant un employeur public :
le tiers de la pension et la moitié du minimum garanti, sauf non-officier de
moins de vingt-cinq ans de services, limite d'âge atteinte, invalidité. Le
portage : `regle2027`, dans `moteur/js/droit/cumul.js`. La fiche
`cumul_emploi_retraite_fonction_publique` tient la rédaction à rattacher.

**Ce qu'il y a à faire.**

1. Lire les trois articles, et le sort de la pension d'invalidité, civile ou
   militaire, que le 5° laisse cumuler entièrement.

2. Rejouer le cas : un militaire parti avant l'âge légal en 2027, salarié du
   privé. Le test, vu rouge, valeur tirée du texte.

3. La règle, dans le modèle et son portage ; ce que la saisie sait du
   caractère militaire de la pension et de l'employeur, à dire s'il manque.

4. La fiche.

**Fini quand** la pension militaire suit, en 2027, le cumul que le texte lui
donne, ou que ce qui manque à la saisie pour le dire est une limite écrite.

**Les règles de l'étape.** C'est une règle du scénario 1 : la session se mène
sur Fable 5.2, ouvre par `python scripts/veille_droit.py` et suit
`docs/veille_droit.md`. Le test d'abord, sa valeur attendue tirée du texte ou
d'un calcul posé à la main. Le moteur est en chantier dans deux autres
actions, qui le séparent du site et lui font lire les règles dans les fiches
(`python scripts/reprise.py 187`, puis `191`) : lire leurs blocs avant de
toucher au moteur, et ne pas défaire ce qu'elles ont posé. Une seule session à
la fois écrit dans le modèle et son portage.
