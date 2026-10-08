# Version du 8 octobre 2026 : un document tenu par son test

La prose a un quatrième régime, `tenu` : le document dit ce qui est vrai
aujourd'hui, mais aucune sonde ne sait le recalculer — ce qu'une page du site
affiche —, et c'est le test que `zones.yaml` lui nomme (`test`) qui le
confronte à ce qu'il décrit (annexe B). Ni ancré ni gelé, il n'a que ce test :
`scripts/verifier_prose.py` refuse un test absent, qui ne soit pas un
`tests/test_*.py`, ou qui ne nomme pas le document, et `scripts/conservation.py`
gèle alors le document comme un récit (§ 12) ; une archive le reste, quoi que
`zones.yaml` en dise. Le parcours de présentation est le premier : déclaré
`recit`, il était gelé par la conservation quand `tests/test_parcours.py`
l'obligeait à suivre les pages, et la suite, rougie par chaque chiffre qui
bougeait sur une page, ne reverdissait qu'en acceptant des pertes. La
référence de la conservation, refigée sans perte, a quitté ses 66 paragraphes,
et aucun autre (action 135, à la demande du propriétaire).
