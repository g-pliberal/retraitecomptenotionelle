# Version du 7 octobre 2026 : les limites par partie

`docs/limites.md` pesait 314 190 octets en 3 518 lignes, et 406 des 974
commits des trente jours précédents y écrivaient à la main, une fois écartés
ceux qui n'y récrivent que des chiffres ancrés : aucun document hors de la
feuille de route et du README ne se retouche aussi souvent. Il tient
désormais en quatorze parties, une par section, sous `docs/limites/`, chacune
nommée du numéro sous lequel on la cite (`5-ter-trajectoire.md` pour le
« § 5 ter »). `docs/limites.md` garde son titre, son introduction et le
sommaire, de sorte que les renvois du dépôt et du site mènent toujours
quelque part, sans qu'aucun ait été récrit. Les titres remontent d'un niveau,
rien d'autre ne change : `scripts/conservation.py --depuis HEAD` retrouve
chaque paragraphe. Chaque partie a son régime dans `zones.yaml`, avec les
procès-verbaux qu'elle porte, et `tests/test_prose.py` tient le sommaire et
les parties ensemble (action 135, étape 5 du contexte, à la demande du
propriétaire).
