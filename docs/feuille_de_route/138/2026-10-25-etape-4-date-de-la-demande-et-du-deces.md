# Étape 4, dix-septième partie : avant juillet 2004, les ressources de la demande, puis celles du décès

**Le 25 octobre 2026, la demande.** Le propriétaire, dans la dixième vague des
sessions : le premier point sans propriétaire du bloc de l'étape, la date de la
demande et celle du décès, avant juillet 2004 ; une présomption nouvelle, si la date
de la demande en demande une, posée et déclarée comme les autres, et son choix dit
au bloc s'il lui revient. Les majorations au maximum viendront dans une session
suivante ; les décrets agricoles de 1976 et 1977, au fac-similé, restent au
propriétaire, et ce que le bloc renvoie au site, au site.

**Ce que dit le droit, lu le jour même** (journal de veille du 25 octobre, « date de
la demande et du décès » ; fiche `reversion`).

- *Les textes.* R. 353-1, en 1985 comme en 1990 : le conjoint qui « ne dispose pas,
  à la date de la demande de pension de réversion, de ressources personnelles
  dépassant le montant annuel du salaire minimum de croissance », et « si les
  conditions de ressources ne sont pas remplies à la date de la demande, elles sont
  appréciées à la date du décès, compte tenu des dispositions en vigueur à cette
  date » ; jusqu'au 30 novembre 1990, « dans les conditions fixées par les articles
  R. 815-25 et suivants » — R. 815-32, les trois mois qui précèdent l'entrée en
  jouissance, sous le quart du plafond, sinon les douze —, puis, par le décret
  n° 90-1061, « les trois mois civils précédant la date de la demande », ou les
  douze. L'article 81 a du décret n° 45-179 le disait en 1981 et 1982, par renvoi au
  décret n° 64-300 du 1er avril 1964.
- *La caisse.* « Quelle que soit la date de décès [...], les ressources doivent être
  appréciées : soit à la date de la demande, soit, si la condition n'est pas remplie
  à cette date, à la date du décès », pour les réversions qui prennent effet après
  le 30 juin 1974 (circulaire n° 31/75, § 21 et 233) ; au décès, le plafond
  « applicable à cette dernière date » (§ 2352). Pour le décret n° 64-300, « les 3
  mois civils précédant la date de la demande si l'entrée en jouissance est fixée au
  1er jour du mois suivant la date de départ de ladite demande », les douze au-delà
  du quart (circulaire n° 42/77, tableau n° 13). L'exposé « Condition de ressources »
  le redit pour toute la période : « Les ressources retenues étaient celles des 3
  mois civils précédant le décès », puis des douze, et « Si les ressources examinées
  à la date de la demande et à la date du décès dépassaient le plafond autorisé, la
  demande était rejetée » ; le survivant refusé peut « formuler une nouvelle
  demande » quand ses revenus diminuent (circulaire n° 46/75, § 233).
- *Avant juillet 1974.* Depuis le 1er mars 1971, les ressources « appréciées à la
  date du décès de l'assuré », sous le SMIC « au 1er janvier de l'année au cours de
  laquelle est survenu le décès » (décret n° 71-123, article 2) ; avant, le conjoint
  « à charge », sous le plafond de l'AVTS diminué de la majoration pour conjoint
  (circulaire n° 31/75, § 2352).
- *La date d'effet.* « Au premier jour du mois suivant celui au cours duquel
  l'assuré est décédé si la demande est déposée dans le délai d'un an suivant le
  décès », sinon au premier jour du mois qui suit sa réception (R. 353-7, depuis le
  1er décembre 1986 ; au lendemain du décès avant).
- *Aucun exemple chiffré* ne fait jouer la demande ni le décès.

**Ce qui est fait.**

- *La présomption.* Le modèle ne connaît pas la date de la demande : il la présume
  le mois qui précède la date d'effet, celui du décès, ou celui où le survivant
  atteint l'âge requis (`reversion_demandee_le_mois_avant_sa_date_d_effet`, au
  vocabulaire et au § 5.6 de l'architecture) — la seule valeur qui garde la date
  d'effet que donne `reversion_demandee_dans_l_annee` sous R. 353-7, et celle que
  le tableau de 1977 et la tolérance de la caisse supposent. Les mois de la demande
  sont alors ceux du décès quand il tombe le même mois.
- *La fiche* dit de chaque version les moments de ses ressources
  (`ressources_examinees`) : la date d'effet depuis juillet 2004, la demande puis
  le décès de juillet 1974 à juin 2004, le décès seul avant ; les versions d'avant
  2004 disent leurs mois (`periodes_de_reference: [3, 12]`). Leurs conditions, leurs
  hypothèses et leurs textes sont récrits : l'article 81 a, R. 815-25, R. 815-32,
  R. 353-7 et l'article 83 rattachés — le cliquet des textes descend à 9 514 — ; la
  référence du décret n° 71-123 et de la circulaire n° 31/75 ; deux lectures ; un
  écart pour la période d'avant 2004 ; l'historique ; la page des limites.
- *Le modèle* (`droit/reversion.py`, et son jumeau) : `_ressources_a_la_date_d_effet`
  examine les moments de la version l'un après l'autre, chacun sur ses trois ou
  douze mois civils, comptés comme à une révision (`_ressources_de_la_periode`) ; le
  décès, aux paramètres de la version du décès ; la demande, au mois que donne
  `_mois_de_la_demande`. Les ressources d'avant juillet 2004 restent personnelles,
  sans ses retraites, que la limite de cumul compte. Chaque ligne dit le moment qui
  a décidé (`ressources_examinees_au` : `date_d_effet`, `demande` ou `deces`, le
  dernier examiné quand aucun ne remplit la condition), que le paquet porte.
- *Les tests*, posés à la main depuis les textes et vus rouges : la veuve de 1996,
  sans activité au décès, qui en prend une ensuite, refusée à sa demande de juin
  2000, ouverte par les mois du décès ; la même, dont le salaire sextuple deux mois
  avant sa demande, ouverte par les douze mois de la demande, quand ceux de sa date
  d'effet la lui auraient fermée ; la veuve de 1972 qui travaille jusqu'à la veille
  de sa date d'effet, refusée au décès. Les deux moteurs confrontés sur ces trois
  saisies, au niveau `complet`.

**Les mesures.** Aucune réversion ne bouge, sur les 907 témoins de simulation, ni
aucun rendu de page : aucun survivant d'avant juillet 2004 n'y a de revenus
d'activité. Les sept réversions d'avant 2004 disent désormais trois mois, et non
zéro ; le champ du moment s'ajoute à trente-sept lignes — la date d'effet à trente,
la demande à six, le décès à la survivante de 1971.

**Ce qui reste.**

1. *Au propriétaire, le choix de la date de la demande* : la présomption la place
   le mois qui précède la date d'effet. Une demande plus tardive dans l'année, que
   la caisse servirait de la même date d'effet (R. 353-7), examinerait d'autres
   mois : la survivante qui cesse son activité le mois du décès, que la date
   d'effet ouvrait avant cette partie, voit sa réversion refusée quand ses salaires
   des mois qui précèdent passent le plafond, ce qu'une demande trois mois plus
   tard lui aurait évité.
2. La nouvelle demande du survivant refusé, quand ses ressources baissent
   (circulaire n° 46/75, § 233) ; avant le 1er mars 1971, le conjoint à charge ; le
   SMIC de la demande quand elle suit l'année du décès (§ 2351) ; la date d'entrée
   en jouissance au lendemain du décès avant le 1er décembre 1986 ; depuis juillet
   2004, la tolérance qui prend les mois de la demande (circulaire n° 2005/17,
   § 143).
3. *Au site* : la phrase de la carte qui dirait le moment des ressources retenues
   (`ressources_examinees_au`), avec leur période (`periode_de_reference`).
