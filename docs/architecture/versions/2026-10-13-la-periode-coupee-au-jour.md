# Version du 13 octobre 2026 : la période coupée au jour

Une période d'un fichier de régime peut borner au jour les pensions qu'elle
liquide (§ 4.6, action 131). Ses années bornaient l'acquisition et la
liquidation ensemble, et le moteur servait à toute l'année la règle d'un texte
entré en vigueur en avril ou en septembre : les versions datées des fiches,
lues au jour depuis le domaine des enfants, ne couvraient que les paramètres
d'une fiche, non les champs d'une période, ni les interrupteurs que le
chargeur y résout une fois pour toutes. Le champ facultatif `date_effet` de la
période porte désormais, comme les bornes d'une version (§ 4.1), les dates
d'effet [début, fin) qu'elle liquide ; absent, ce sont ses années, et les
témoins n'ont pas bougé. La liquidation choisit la période à la date d'effet
de la pension (`periode_de_liquidation`, dans les deux moteurs), l'acquisition
garde l'année, et les morceaux que la datation des taux découpe dans une
période s'en partagent les dates. Le chargeur refuse une borne qui n'est pas
un jour, ou qui tombe à plus d'un an des années de la période. Trois textes
s'en servent : l'ordonnance du 26 mars 1982 au 1er avril 1983, au régime
général et chez les salariés agricoles, deux arrêtés de la CAVEC, au
5 septembre 2018 et au 7 juillet 2025, et celui du RACL, au 16 mai 2025.
