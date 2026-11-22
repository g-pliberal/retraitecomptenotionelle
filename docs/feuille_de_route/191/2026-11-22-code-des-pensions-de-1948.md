# Les pensions de l'État de 1948 à 1964, liquidées au code de 1948

Le 22 novembre 2026, sur Opus 5.5, relu sous Opus, Fable 5.2 étant
indisponible jusqu'au 25 novembre. La loi n° 48-1450 du 20 septembre 1948,
transcrite le même jour du fac-similé du Journal officiel
(`data/reference/textes/apportes/`), régit les pensions de l'État dont la date
d'effet tombe du 21 septembre 1948 au 30 novembre 1964. Le modèle les
liquidait comme le code de 1964 : tous les services entiers, sans condition de
durée, la majoration pour enfants sans plafond. Corrigé au texte, sans
demander, selon la règle du propriétaire.

**Ce qui change**, dans les versions `loi_du_20_septembre_1948` de deux fiches :

| Fiche | Le texte |
|---|---|
| decompte_des_services_fonction_publique | services sédentaires aux cinq sixièmes, et services actifs aussi dans les trente premières années de qui a droit après trente ans (art. 16, I) ; décompte final au semestre (art. 16, II) ; sans trente ans de services, vingt-cinq en catégorie B, la pension est proportionnelle, vingt-cinq annuités au plus (art. 6 ; art. 16, IV) ; les bonifications ne réduisent la durée que d'un cinquième (art. 8, III) |
| majoration_enfants_plafond_fonction_publique | la pension majorée ne dépasse pas les émoluments de base, et la pension proportionnelle n'est pas majorée (art. 18, V) ; la version du code de 1964 part désormais du 1er décembre 1964, non du 1er janvier |

Le moteur : `servicesDuCodeDe1948` (`moteur/js/droit/compter.js`), que
`liquiderChaqueRegime` lit, et la pension proportionnelle que l'étape qui
complète ne majore pas. Tests : `tests/test_pensions_de_l_etat_de_1948.py`,
quatorze cas posés à la main depuis le texte.

**Exemple.** Un fonctionnaire sédentaire né en janvier 1903, trente-deux ans
et demi de services de juillet 1930 à 1962, parti en janvier 1963 : 130
trimestres liquidables avant, 65 % du traitement ; 108 au texte, 54 %.

**Trois lectures**, d'où la fiabilité estimée de la version : la catégorie B
est la carrière qui ouvre la dérogation de l'âge ; « compléter » les premières
années se lit en durée, non dans l'ordre des années ; la bonification pour
enfants suit la catégorie de l'agent.

**Reste**, pour des étapes suivantes : l'âge des mères abaissé d'un an par
enfant (art. 7, 3°) ; la pension proportionnelle des mères à quinze ans de
services et sa jouissance (art. 6, III, 4°, et 24) ; l'agent de la catégorie B
sans vingt-cinq ans, que le modèle laisse partir à cinquante-cinq ans ; le
minimum vital, son abattement et son minimum (art. 17, II, 18, II et IV), dont
la série manque ; l'invalidité (art. 25 à 27) ; les maxima portés à quarante
annuités (art. 16, III et IV) ; les anciens combattants (art. 6, II) ; les
services d'avant 1930, que le catalogue des régimes ne compte pas. La période
1964 de `fonction_publique_etat.yaml` part du 1er janvier, quand le code de
1964 ne vaut qu'au 1er décembre : à régler à la migration des fichiers de
régime. Les limites d'âge de 1936 attendent la lecture des lois de 1946 à 1948.
