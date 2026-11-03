# Le site : la page dépliée sous son budget, et l'assurance maladie demandée quand elle compte

**Le 3 novembre 2026, ce qui est fait.** La file du site, dans la troisième
vague : d'abord la suite complète, rouge sur e042a12, puis la question de
l'assurance maladie du micro-entrepreneur, que l'étape 6 laissait « à
reprendre ». Deux commits, chacun son test vu rouge d'abord.

1. *La suite réparée* (`fa5c936`). `test_une_page_depliee_tient_son_budget`
   rougissait sur la page témoin du simulateur, 7 375 mots pour 7 362 : les
   treize du libellé et de l'exemple des « Années outre-mer » (étape 7). La
   question de l'étape 6 n'y paraît pas, la carrière témoin étant salariée.
   Trois redites ôtées en rendent vingt, et le budget ne bouge pas : la page en
   porte 7 355. L'aide brève du revenu, « en euros bruts par mois », redisait
   le brut et le mois de son libellé, « Revenu d'activité brut mensuel » : elle
   dit « en euros ». La note de l'épargne disait les points volontaires « pas
   prélevés », ce que le haut de la section dit (« pas une retenue ») et que la
   phrase en gras du partage redit. L'estimation officielle finissait sur « Ce
   que vous recopiez reste dans votre navigateur », ce que le chapeau dit pour
   toute la saisie. Le commentaire du budget, dans `tests/test_web.py`, le
   consigne.
2. *L'assurance maladie, demandée quand la réponse compte* (`1c1c0c7`). La
   réponse « hors du RSI » ne change que les seuils de chiffre d'affaires de
   2014 et de 2015, au seul métier du micro-entrepreneur, et à la condition
   qu'il saisisse son chiffre d'affaires (`maladie_hors_rsi`, que `parcours`
   ne pose qu'avec l'activité). Le menu ne paraît donc plus qu'au chiffre
   d'affaires d'une activité que la grille hors de la maladie du RSI
   distingue, lue au paquet (`seuils_micro_hors_maladie_rsi`) : la vente et
   les services en 2014 et en 2015, le libéral en 2014 seulement, le libéral
   de 2015 gardant la compensation ; et quand une période de
   micro-entrepreneur couvre l'une de ces années. Il paraît aussi quand la
   réponse est déjà dite, pour qu'on la défasse. Ni le revenu déjà abattu, ni
   la Cipav, ni l'activité d'après le départ ne le font paraître
   (`horsDuRsiEnJeu`, `pages.js`). Vu rouge :
   `test_l_assurance_maladie_ne_se_demande_que_si_la_reponse_compte`
   (`tests/test_web_saisie.py`), onze cas, dont six rouges avant le code.
   Des deux voies que l'étape 6 laissait, la première : le plancher de la
   saisie, un dixième du salaire moyen, vaut pour tous les statuts, et
   l'abaisser changerait la saisie de chacun pour quelques jeunes
   micro-entrepreneurs, que le profil de carrière met déjà à la portée des
   seuils.

**Mesuré.** Le paquet, les témoins et les pages refaits comme GitHub les
refait : aucun rendu de page ne change du fait de la seconde retouche, les
deux micro-entrepreneurs des témoins couvrant 2015 au chiffre d'affaires.
`python -m pytest -m rapide`, `-m site`, `tests/test_web.py` et
`tests/test_web_saisie.py` au vert.

**Vu en chemin, non corrigé.**

- Le robot ne recommite pas les fichiers fabriqués quand la suite rougit : le
  paquet, les témoins et les pages de `main` dataient, ce matin, de la
  dernière suite verte. Sans les refaire, trois tests de `tests/test_web.py`
  rougissent en local (`test_le_paquet_est_a_jour` et les deux concordances
  du portage) ; refaits, une vingtaine de témoins de simulation bougent, du
  fait d'autres files (la Nouvelle-Calédonie, Wallis-et-Futuna, Mayotte).
  La prochaine fabrique verte les recommitera.
- Le relevé de carrière ne porte pas l'assurance maladie : seul le métier
  saisi la lit, comme l'étape 6 l'a voulu.

**Ce qui reste.** Rien de la file du site dans l'action 177. Au bloc
« Reprise » de l'action 177, que la file D tient : ôter l'étape 7 et
l'assurance maladie de ce qui reste à la session du site.

**L'étape est faite.**
