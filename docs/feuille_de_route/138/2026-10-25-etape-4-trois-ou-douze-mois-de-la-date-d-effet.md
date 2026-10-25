# Étape 4, quinzième partie : les trois ou douze mois de la date d'effet, et le décès qui commence la période de référence

**Le 25 octobre 2026, la demande.** Le propriétaire, dans la huitième vague des
sessions : le premier point sans propriétaire du bloc de l'étape, les trois ou
douze mois de la date d'effet (R. 353-1). Les majorations de 1972 à 1982
comparées au plancher viendront dans une session suivante ; les décrets agricoles
de 1976 et 1977, au fac-similé, restent au propriétaire, et ce que le bloc
renvoie au site, au site.

**Ce que dit le droit, lu le jour même** (journal de veille du 25 octobre, « trois
ou douze mois de la date d'effet » ; fiche `reversion`).

- *Le texte.* Depuis le 25 août 2004 : « Les ressources à prendre en compte lors
  de la demande sont celles afférentes aux trois mois civils précédant la date
  d'effet de la pension de réversion. Lorsqu'elles excèdent le quart du plafond
  [...], il leur est substitué celles afférentes aux douze mois civils précédant
  cette date, qui sont alors comparées au montant annuel de ce plafond » (R. 353-1,
  de la rédaction LEGIARTI000006749453 à celle du 8 juillet 2019). De 1990 à 2004,
  les trois ou douze mois « précédant la date de la demande » ; en 1985 comme en
  1990, la condition non remplie à la demande s'apprécie « à la date du décès,
  compte tenu des dispositions en vigueur à cette date ».
- *La caisse.* L'exposé « Condition de ressources » et la circulaire Cnav
  n° 2005/17 (§ 143, § 146) le redisent, avec la tolérance de la lettre
  ministérielle du 29 mars 1965 : quand la date d'effet est le mois qui suit le
  dépôt de la demande, les trois ou douze mois qui précèdent la demande. Quand la
  situation familiale change dans la période, les ressources d'après le changement
  y sont transposées, et le décès de l'assuré en est un (lettre de la Cnav du 18
  avril 2007) : « on retient les ressources perçues par le seul conjoint survivant
  à compter du 12/02 », dix-neuf jours transposés sur quatre-vingt-dix (circulaire
  RSI n° 2007/061, annexe 3, § 7, exemple 1, en attribution). Le droit propre qui
  commence le jour de la date d'effet n'y est pas, « non pris en compte à la date
  d'effet de la PR », et compte à la révision du mois qui suit ; le régime général,
  quand il instruit après la date d'effet, « calcule différents dépassements
  jusqu'à stabilisation des ressources » (même annexe, questions, exemple 3).
- *Aucun exemple chiffré* ne fait jouer les douze mois, ni des ressources qui
  varient dans la période d'une attribution.

**Ce qui est fait.**

- *Le modèle* (`droit/reversion.py`, et son jumeau) : la date d'effet d'après
  juillet 2004 retient les ressources des mois que la version dit
  (`periodes_de_reference: [3, 12]`, `_ressources_a_la_date_d_effet`) : celles
  des trois mois civils qui la précèdent, comptées comme à une révision — les
  revenus d'activité et l'apport du nouveau conjoint tels que perçus, les
  retraites du survivant pour ce qu'elles servent, ou entières au régime général
  avant le 1er juillet 2010 —, et, quand avec les réversions des autres régimes de
  base elles excèdent le plafond rapporté à l'année, celles des douze. La période,
  de la date d'effet comme d'une révision, commence au dernier changement de
  situation familiale qu'elle porte, le décès compris (`_ressources_de_la_periode`,
  qui succède à `_ressources_des_trois_mois`). Un changement du jour de la date
  d'effet, la retraite du survivant comprise, révise la réversion le mois qui suit ;
  celui que la période de la date d'effet compte tel que perçu, le premier mois dont
  les trois mois ne portent plus que ce qui le suit, quand cela change quelque
  chose : la lecture des révisions du 24 octobre, étendue à la date d'effet, comme
  le régime général qui « calcule différents dépassements jusqu'à stabilisation ».
  Avant juillet 2004 (`periodes_de_reference: null`), la date d'effet compare
  encore ses ressources du jour, sur l'année. Chaque ligne dit les mois de sa
  période (`periode_de_reference` : 3, 12, ou 0), que le paquet porte.
- *Le paquet* refait sur les agrégats de `main`, pour que le portage lise les
  périodes dès l'envoi ; les témoins, laissés à GitHub.
- *Les tests*, posés à la main depuis le texte et vus rouges : la veuve de 2006
  dont l'activité cesse quinze jours après le décès, sa réversion réduite sur les
  vingt et un jours qui le suivent, puis entière le 1er février 2007 ; la veuve de
  2010 dont le salaire quadruple deux mois avant ses cinquante-cinq ans, entière sur
  les douze mois, suspendue le 1er août sur les trois ; la veuve de 2015 retraitée
  le jour où sa réversion part, entière à sa date d'effet, réduite à sa dernière
  révision. Les deux moteurs confrontés sur ces trois saisies, au niveau
  `complet`. L'exemple 1 de la circulaire RSI entre au témoin des exemples
  officiels (`rsi_2007_061_transposition_depuis_le_deces`), transposé en 2008 :
  en février 2005, l'abattement de cinquante-cinq ans aurait touché la survivante,
  que l'exemple n'abat pas ; à salaire constant, il passait déjà.
- *La fiche* `reversion` : ses lectures, l'écart des révisions récrit, les
  périodes de chaque version, l'historique ; les rédactions de R. 353-1 de 2010 et
  de 2017, lues, à rattacher — le cliquet des textes descend à 9 518 ; la page des
  limites.

**Les mesures.** Aucune réversion ne bouge, sur les 907 témoins de simulation, ni
aucun rendu de page : seul s'y ajoute le champ de la période, trois mois sur
vingt-neuf lignes, douze sur une — la survivante de 86 000 € de ressources, que
les douze mois laissent sans réversion, comme l'année.

**Ce qui reste.**

1. *Avant juillet 2004* : les ressources à la date de la demande, sur ses trois ou
   douze mois depuis le 30 novembre 1990, puis, la condition non remplie, à la date
   du décès, aux dispositions de ce jour (R. 353-1, rédactions de 1985 et de
   1990) ; le modèle compare celles de la date d'effet, sur l'année.
2. La date de la demande, que le modèle ne connaît pas, et la tolérance qui prend
   ses mois quand la date d'effet est le mois qui suit le dépôt ; les réversions
   des autres régimes de base, comptées pour ce qu'elles servent le jour de
   l'examen ; la période de la complémentaire des indépendants, que sa fiche
   `reversion_rci` ne dit pas ; les rédactions de R. 353-1 de 2010 et de 2017 à
   rattacher aux versions qu'elles touchent.
3. *Au site* : la phrase de la carte qui dirait la période des ressources retenues
   (`periode_de_reference`).
