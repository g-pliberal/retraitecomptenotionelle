# La mémoire des calculs indexée sur le seul modèle

**Le 10 octobre 2026, la mesure.** La mémoire des calculs (`memoire.py`) se
gardait sous l'empreinte de tout ce que git voit sous `src/`, `data/` et
`scripts/`. En trente jours, 826 commits de `main` l'ont changée, et chacun
suffisait à faire refaire toute la mémoire au passage suivant : cinq minutes
de suite le 28 septembre, et jusqu'au quart d'heure de la recherche d'âges. Ce que lisent vraiment les
calculs gardés se relève dans un processus neuf, sans mémoire, en notant
chaque fichier ouvert, sur deux simulations par statut, le coût agrégé et les
avantages : 343 fichiers, tous sous `regimes/`, `regles/`, `legislation/`,
`macro/`, `couches/`, `univers/`, `mortalite/`, `vocabulaire/` et
`contrats/`, plus les lois de mortalité calibrées de `data/derive/` ; 82
modules de `src/`. Ni la veille, ni les registres de sources, ni la prose, ni
le catalogue du site, ni les textes, ni l'outillage du site et des tests.

- *L'empreinte du modèle.* `memoire.SOURCES` ne compte plus que `src/` et
  `data/`, hors de `HORS_DU_MODELE` : le journal de veille et `veille.yaml`,
  `prose/`, `site/`, `textes/`, `referents.yaml`, `sources.yaml`,
  `sources_a_explorer.yaml`, `web/`, `fabrique.py`, `pytest_parallele.py`,
  et les `CLAUDE.md`.
- *Le code d'un calcul écrit hors du modèle.* Huit scripts gardent des
  calculs, et des tests : `test_cout.py` et les confrontations des deux
  moteurs. Leur clé porte désormais leur fichier, et ceux qu'il importe ou
  nomme à côté de lui ou dans `scripts/`, de proche en proche
  (`_code_hors_du_modele`) : `cout_age_depart.py` emporte `age_depart_csp.py`
  et `age_conjoncturel.py`, `chiffrage_plf.py` `proposition_prospective.py`.
  Une retouche de `scripts/` ne refait plus que les calculs des scripts
  qu'elle touche. Le calcul de `test_cout.py`, l'ancienne convention des
  cotisants, ne se gardait que sous l'empreinte des sources, qui ne lit pas
  `tests/` : une retouche de son code n'aurait rien refait. Un fichier
  retouché depuis le chargement du modèle se calcule sans mémoire, comme
  `_code_retouche` le veut pour les sources ; `moitie_python` passe par là.
- *Le garde-fou.* `scripts/lectures_du_modele.py` refait le relevé, et
  `test_aucun_calcul_garde_ne_lit_ce_que_l_empreinte_ignore`
  (`test_outillage.py`) exige que rien n'y soit hors du modèle. Le relevé
  prend 50 s et se garde sous l'empreinte du modèle : il ne se refait que
  quand celui-ci bouge, et GitHub, sans mémoire, le refait à chaque passage.
  Il ne couvre pas les calculs des scripts, qui reposent sur les mêmes
  chargeurs et ne nomment aucun des fichiers exclus.

**Mesuré.** Des 161 commits de `main` qui ont changé l'empreinte depuis le
1er octobre, 36 (22 %) ne la changeraient plus ; les 125 autres touchent le
modèle lui-même, dont 104 son code. Sur deux scripts lourds et les trois
confrontations : 91 s la mémoire vide, 11 s ensuite ; 11 s encore après une
retouche de `scripts/consommation.py` et de `data/sources.yaml`, quand
l'ancienne empreinte aurait tout refait ; 48 s après une retouche de
`solde_fusion.py`, dont seuls les calculs se refont.

**Ce qui reste.** Les fiches de règles : le modèle en lit 93 sur 208, et
elles changent dans 82 des 125 commits, seules dans 13, souvent pour leur
seule documentation — la date de lecture, l'état —, qu'une empreinte de leurs
seuls champs lus laisserait de côté. Et `actions/cache` sur GitHub, qui y
garderait la mémoire d'un passage à l'autre, mais ôterait à la suite son
passage sans mémoire : au propriétaire de le décider.
