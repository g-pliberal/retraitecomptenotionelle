# Correction sur décision du propriétaire : le rendement de la CAFAT et le taux de Wallis-et-Futuna

**Le 2 novembre 2026, le propriétaire a répondu oui : corriger les deux
chiffres d'après les recherches complémentaires du même jour. La CAFAT sert
le rendement que la caisse fixe chaque année, de 12,45 % en 2001 à 9,00 % en
2026, au lieu de 10 % sur toute la période ; Wallis-et-Futuna cotise le taux
de la retraite seule, 11,1 % en 2009 montant à 21 % en 2020, et 9 % avant
2009, un tiers au salarié, au lieu du taux total de la caisse. Des données
seules : aucun code du modèle ne change. La part CRFM des agents mahorais
n'est pas touchée.**

Demande : la file A de la deuxième vague du 2 novembre 2026, ouverte par la
session d'orchestration : « corriger, d'après les recherches de la note
`docs/feuille_de_route/145/2026-11-02-recherches-complementaires.md` : 1. le
rendement de la CAFAT [...] année par année, aussi loin que les sources la
donnent ; 2. le taux de Wallis-et-Futuna : 21 % pour la retraite ». « La part
de pension CRFM des agents mahorais intégrés attend son barème [...] : ne la
touche pas. »

- *Le test d'abord.* `tests/test_caisses_du_pacifique.py` porte les valeurs
  des sources et les confronte à ce que le moteur lit. Six de ses tests ont
  échoué pour la raison attendue — 10 % au lieu de 10,35 % en 2015 et de
  12,45 % en 2001 ; 17,1 % au lieu de 11,1 % en 2009 et de 9 % avant —, puis
  passé avec les données. `test_les_parts_salariales_sont_plausibles`
  (`tests/test_donnees.py`) perd l'exception qu'il faisait à Wallis-et-Futuna,
  que les prestations familiales expliquaient seules.
- *Les sources, relues avant d'écrire.* La chambre territoriale des comptes
  (p. 62, 63 et l'annexe 7, p. 102), l'avis n° 12/2008 du conseil économique
  et social (p. 4), la Cour des comptes (S2022-2223, p. 32 et 33) et le
  rapport 2004 de l'IEOM (p. 64 et 65), téléchargés hors du dépôt : les
  citations de la note s'y retrouvent mot pour mot. Deux détails de plus. Les
  valeurs de service de l'annexe sont, en 2017 et 2018, la moyenne de l'année
  des valeurs du point que la caisse fixe au 1er avril et que ses fiches
  publient (239,28 = ¼ × 238,26 + ¾ × 239,62 ; 241,87 = ¼ × 239,62 + ¾ ×
  242,62) : le rendement de ces deux années en sort plus bas de 0,01 et 0,03
  point ; le dépôt garde l'annexe, que la décision cite, et un test le
  mesure. Le rapport écrit 9,95 % pour un départ de 2019, où l'annexe donne
  9,97 %.
- *La CAFAT.* Le moteur sert le rendement de l'année de la liquidation aux
  cotisations de toute la carrière revalorisées sur les prix (`droit/liquider`,
  dans les deux moteurs) : la série s'écrit donc par année de départ, dans
  `regimes/rendements_points.csv`, qui se saisit à la main. De 2015 à 2021,
  la valeur de service divisée par la valeur de référence de l'annexe ; de
  2022 à 2026, celles des fiches des paramètres ; 9,00 % reconduit au-delà
  (`haute`). 2001, 2007 et 2008 : 12,45 %, 10,98 % et 10,35 %, ceux du conseil,
  que la chambre contredit (`moyenne`). Calculs du dépôt, dits et `estimee` :
  la ligne droite de 2002 à 2006, la « politique de baisse progressive » que
  le conseil décrit ; 10,35 % de 2009 à 2014, la valeur de 2008 que la
  chambre donne encore en 2015 ; la valeur de 2001 prolongée jusqu'en 1958.
  Le prix d'achat de chaque année, que la note proposait de verser à
  `valeurs_point.csv`, n'y entre pas : ce fichier s'écrit par
  `verifier_donnees.py`, sous un contrôle à créer, et la série n'est lue que
  depuis 2015. L'écart qui en reste est mesuré dans la fiche : pour un départ
  de 2026, la revalorisation sur les prix s'écarte de celle de la valeur de
  référence de −2,2 % (cotisations de 2021) à +1,4 % (2015).
- *Wallis-et-Futuna.* Chaque période porte le total de la caisse moins les six
  points de prestations familiales, tous à l'employeur : 11,1 % en 2009, 0,9
  point de plus chaque 1er janvier, 21 % depuis 2020 ; la part du salarié,
  inchangée, en fait un tiers (0,3333). Avant 2009, les 9 % de la caisse
  locale (6 % et 3 %), lus pour 2004 et 2008 et prolongés jusqu'en 1975.
  Restent lus et non portés, faute d'une décision qui les couvre : le barème
  de la caisse locale (3,2 % par année des quatre derniers salaires, 65 % au
  plus, à 55 ans) et sa création en 1977, qui changerait l'étiquette du statut
  sur le site (« depuis 1975 »).
- *Ce qui bouge.* Au scénario 1, la pension CAFAT : un dixième de moins pour
  un départ depuis 2026, 3,5 % de plus de 2008 à 2015, un quart de plus avant
  2001. À Wallis-et-Futuna, la pension, en annuités, ne bouge pas ; le compte
  notionnel, qui ne reçoit par défaut que la part du salarié, non plus depuis
  2009, et reçoit 3 % au lieu de 3,70 % avant ; sous la part totale, de 22 % à
  47 % de moins. Le paquet et les témoins refaits en local, puis rendus à
  GitHub, qui les refait : 15 des 915 témoins de simulation bougent. Au
  scénario 1, huit calédoniens, de −7,57 % (née en 1975, partie en 2039 :
  la CAFAT baisse d'un dixième, l'Agirc-Arrco ne bouge pas) à +24,50 %
  (génération 1925, partie en 1989, la CAFAT seule) ; aux scénarios
  notionnels, les sept de Wallis-et-Futuna baissent, de −1,78 % à −18,94 % au
  scénario 2, jusqu'à −47,37 % aux scénarios 4 et 6. Une page change, la
  méthode, qui cite l'inventaire.
- *Les fichiers.* `regimes/rendements_points.csv` ;
  `regimes/cafat_nouvelle_caledonie.yaml` et `regimes/wallis_et_futuna.yaml`
  (notes, `manque`, sources de l'inventaire), d'où `inventaire.yaml` et
  `docs/regimes.md`, refaits ; `legislation/reformes.yaml` (le libellé de
  `wallis_2009`) ; les fiches `cafat_pension_de_base` et
  `wallis_et_futuna_pension_des_salaries` ; `docs/limites/4-regimes-incomplets.md` ;
  la description de la page des taux de la caisse dans
  `scripts/fetch/sites_institutionnels.py`.
- *Les tests.* `tests/test_caisses_du_pacifique.py`, `test_donnees.py`,
  `test_carte.py`, `test_services_passes.py`, les confrontations légères, les
  deux tests de la feuille de route et celui du journal de veille passent,
  avec la suite rapide.
- *Hors de la file A.* Rien à changer dans les fichiers des autres files.

## Ce qui reste, et la clôture

- *Rien du ressort de l'action*, qui documente sans calculer : ses trois
  étapes, les recherches et la correction décidée sont faites.
- *Hors d'elle, au propriétaire* : les écarts que les notes du 13, du 14 et
  du 16 octobre lui laissent — des changements du modèle, dont elles
  demandent s'ils ouvrent une action —, auxquels s'ajoutent, lus et non
  portés, le barème et la création en 1977 de la caisse locale de
  Wallis-et-Futuna et le taux d'avant avril 2009 de la CAFAT ; la part CRFM
  attend l'arrêté de 1977.
- *La clôture.* L'action peut se clore dès que le propriétaire aura dit si
  ces écarts ouvrent une action nouvelle (avis : oui, une action qui les
  porte au modèle, et clore celle-ci) ; la session ne la clôt pas.
