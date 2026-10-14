# Étape 19, les revalorisations servies : le scénario 1 sert son droit, et non les prix

**Le 14 octobre 2026. La masse du scénario 1 de la page Coût servait, jusqu'au
dernier barème, des pensions indexées sur les prix ; elle sert désormais ce que
le droit a servi, régime par régime. Le passé se rapproche des comptes (2009 de
−16,4 à −13,9 %, 2023 de +2,5 à −0,7 %), et l'horizon s'en écarte d'autant
(dérive de 2070 de 1,008 à 1,033) : la correction démasque le défaut de la
pension par tête, que l'étape 18 situait déjà dans l'avenir.**

- *Ce qui est fait.* `RevalorisationServie.coefficient_historique`
  (`revalorisation.py`) : ce que vaut en une année, en euros constants, un euro
  de pension d'un régime liquidé une année antérieure, sous les trois règles de
  `PensionServie` lues à l'année — les coefficients de la Cnav (L. 161-23-1),
  pour tout ce qui n'a pas de texte à soi, régimes spéciaux compris ; la
  péréquation au point d'indice jusqu'en 2003, les décrets de 2004 à 2008, puis
  la Cnav, pour l'État, la CNRACL et les ouvriers de l'État ; la valeur de
  service des régimes en points, le long des fusions et des changements
  d'échelle. Chacune à la moyenne des douze mois de l'année, déflatée des prix,
  jusqu'à son dernier barème, un au-delà. Le RAFP, hors répartition, garde un.
  `coefficient_servi` (`cout.py`) le compose avec la valeur de service convenue
  de l'Agirc-Arrco ; la masse du scénario 1, ses masses par régime,
  l'engagement et la distribution de `grille_large.py` le lisent.
  `coefficient_historique` (`cout.py`, sans la convention) sert aux réformes
  prospectives, scénario 6 compris quand on l'y range : qui est parti avant la
  bascule y garde la pension du scénario 1, sous son droit jusqu'à elle — le
  stock reste toute la masse du scénario 1 sur les années publiées. Le cycle de
  vie, qui mène le passé pension par pension (`faire_vivre`), garde
  `coefficient_actuel` : rien ne change à son portage (138.9).
- *Mesuré*, sous les réglages des tests, Python 3.11 :

  | | 1990 | 2000 | 2004 | 2009 | 2015 | 2020 | 2023 | dérive 2050 | dérive 2070 |
  |---|---|---|---|---|---|---|---|---|---|
  | avant | −24,3 | −14,4 | −11,7 | −16,4 | −9,5 | −3,8 | +2,5 | 0,986 | 1,008 |
  | après | −18,0 | −11,0 | −9,5 | −13,9 | −6,8 | −3,0 | −0,7 | 1,008 | 1,033 |

  En 2009, −6,1 % de têtes (inchangé), −8,3 % de pension par tête (−11,0 %
  avant). À l'horizon, contre le COR : la pension relative de l'ensemble passe
  de +2,4 à +4,8 % ; la FPE de +5,2 à +8,0 %, la CNRACL à +3,4 %,
  l'Agirc-Arrco à +22,2 % ; la dépense de la FPE à +23,1 %, de la CNRACL à
  +13,7 %. Le coût par défaut : le solde moyen de la proposition de −0,9 à −1,0
  point de PIB, sa dette de 2070 de 62 à 69 % ; l'engagement du système actuel
  en 2021 de 481 à 490 % du PIB. La seconde lecture de la dérive alourdit
  désormais la dette de la proposition de sept points, au lieu de l'alléger.
- *Les cliquets relevés*, chacun avec son histoire dans `tests/test_cout.py` :
  la reconstitution abaissée de 17 à 14 %, la pension par tête de 12 à 10 % ;
  la pension relative relevée de 3 à 5 % ; la dérive de l'horizon tolérée
  jusqu'à 1,04 ; les groupes (FPE 8 %, CNRACL 4 %, Agirc-Arrco 23 %, dépenses
  FPE 24 %, CNRACL 14 %, régimes spéciaux abaissé à 34 %) ; le contrôle
  `cout.vigilance_cor`, de trois à quatre points. Un test neuf,
  `test_le_scenario_1_sert_les_revalorisations_de_son_droit`. L'accueil
  (`MESURES_BLOCAGES`, `pages.js`) cite le solde et la dette nouveaux : deux
  valeurs, sur le territoire de la session du site, faute de quoi la suite
  rougissait.
- *Deux conventions, déclarées* (limite 5 ter) : la tranche de 2020 du milieu,
  0,8 %, les masses ne connaissant pas le montant de chaque retraité ; les
  majorations forfaitaires de 1972 à 1982, qui ne visent que certaines pensions
  d'avant 1975, absentes. Le paragraphe de la limite 5 bis sur le stock de
  la fonction publique au jaune, récit du 14 octobre, dit encore que la page
  indexe le scénario 1 sur les prix : vrai à sa date, il ne se récrit pas, et
  ses écarts au jaune n'ont pas été remesurés.
- *Pour la session du site.* La page Coût dit de la seconde lecture qu'elle
  « l'alourdit en 2070, l'allège avant » (`pages.js`, vers la ligne 9419) :
  la dérive ne passe plus sous un qu'en 2027, et la phrase est à reprendre.
  La limite 5 ter le dit déjà.
- *Ce qui reste.* L'horizon d'abord : la pension par tête du modèle croît plus
  vite que celle du COR, et ce qui la masquait est levé — la FPE et
  l'Agirc-Arrco en font le gros. Puis, au passé, les départs anticipés pour
  carrière longue de 2004 à 2008 (action 152) et les pensions des générations
  anciennes. La pension relative à 3 % et le passé à quelques pour cent sont
  loin : l'action ne se clôt pas.
- *Au propriétaire.* Le coût de la proposition monte (dette de 2070 à 69 %) :
  le droit servi est moins généreux que les prix, la masse du scénario 1 de
  2024 qui fait l'ancrage l'est donc aussi, et le coût du COR est rapporté à
  une masse plus basse. Rien à trancher, sinon s'il faut clore l'action 147
  sur un écart déclaré plutôt qu'à sa cible, pour ouvrir 138.5 et 138.7.
