# Étape 2 : la carrière longue du non-salarié agricole, quatre trimestres à la fin de l'année de l'anniversaire

**Reprise, au 12 novembre 2026.** Rien n'est commencé. Pour partir en carrière
longue, il faut avoir commencé à travailler avant un âge donné. Pour le
non-salarié agricole, le code rural tient cette condition pour remplie avec
quatre trimestres validés à son régime à la fin de l'année de l'anniversaire,
quel que soit le mois de naissance. Le modèle en demande cinq, et quatre pour
le seul né du dernier trimestre. L'écart est antérieur à 2026. À faire, le
test d'abord : lire depuis quand cette voie existe, si la rédaction de 2026
ferme l'autre, et ce qu'applique la MSA ; puis écrire la règle, datée. La
fiche `carriere_longue` reste dite conforme d'ici là, sur décision du
propriétaire.

**La demande, le 12 novembre 2026.** La passe de lecture de l'action 184 a
trouvé des points que le modèle n'applique pas ou qu'elle n'a pas pu vérifier
(note `184/2026-11-12-etape-6-bilan-de-la-passe.md`). La session
d'orchestration les a listés au propriétaire, qui a répondu : « Fait une étape
pour chaque point du modèle ». Celle-ci en est une.

**Ce qui est su.** Le lot de la fonction publique l'a lu
(`184/2026-11-12-etape-6-fonction-publique.md`, « Ce qui change une règle »,
point 2) : article D. 732-40 du code rural (LEGIARTI000053365409, décret n°
2025-1410, pensions prenant effet à compter du 1er janvier 2026). La rédaction
de 2023 offrait déjà cette voie (« soit… soit ») ; celle de 2026 l'écrit « par
dérogation à D. 351-1-3 ». Le modèle : `entreePrecoce`. La fiche
`carriere_longue` tient la rédaction à rattacher.

**La décision sur l'état de la fiche.** Le lot l'a laissée `conforme` malgré
l'écart, qui ne touche qu'un régime et un cas étroit. La session
d'orchestration a jugé ce choix défendable ; le propriétaire, le 12 novembre :
« Pour les décisions à trancher : je choisis tes recommandations ». Elle reste
donc `conforme` jusqu'à cette étape, qui ferme l'écart.

**Ce qu'il y a à faire.**

1. Lire les rédactions de 2005, 2011, 2012, 2023 et 2026 de l'article
   D. 732-40, et dire depuis quand la voie des quatre trimestres existe ; si
   « par dérogation » ferme en 2026 la voie des cinq trimestres ; ce que la
   MSA publie.

2. Le test, vu rouge : un non-salarié agricole né hors du dernier trimestre,
   quatre trimestres à son régime à la fin de l'année de l'anniversaire.

3. La règle, datée de ce que la lecture a établi, dans le modèle et son
   portage ; la fiche.

**Fini quand** la condition d'entrée du non-salarié agricole est celle du
texte à chaque date, et que la fiche cite la rédaction qu'elle applique.

**Les règles de l'étape.** C'est une règle du scénario 1 : la session se mène
sur Fable 5.2, ouvre par `python scripts/veille_droit.py` et suit
`docs/veille_droit.md`. Le test d'abord, sa valeur attendue tirée du texte ou
d'un calcul posé à la main. Le moteur est en chantier dans deux autres
actions, qui le séparent du site et lui font lire les règles dans les fiches
(`python scripts/reprise.py 187`, puis `191`) : lire leurs blocs avant de
toucher au moteur, et ne pas défaire ce qu'elles ont posé. Une seule session à
la fois écrit dans le modèle et son portage.
