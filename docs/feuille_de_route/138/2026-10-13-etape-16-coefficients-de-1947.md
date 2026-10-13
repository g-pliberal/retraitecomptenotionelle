# Étape 16, suite : les coefficients de l'Agirc d'avant 1955, lus dans la convention de 1947 ; l'Arrco d'avant 1965 attend le Journal officiel de 1962

**Reprise, au 13 octobre 2026.** Fait : le texte de 1947, lu à l'image de son
original, et la table de l'Agirc d'avant 1955 qu'il fixe, anticipation et
ajournement, dans les deux moteurs. Reste l'Arrco d'avant 1965 : lire l'accord
du 8 décembre 1961 au Journal officiel du 31 mars 1962, où l'arrêté d'agrément
du 27 mars 1962 le publie en annexe (JORFTEXT000000435809), fac-similé que
Légifrance ne sert qu'au navigateur — au propriétaire, depuis son poste —, et
le règlement de l'UNIRS de 1957 ; puis, si les âges de chaque ligne y sont, la
table de 1957 à 1964, en Python puis en JavaScript, comme celle de 1947. À la
fin de l'étape, la ligne des coefficients de `docs/limites/parametres.md`.
Détail : plus bas, « Ce qui reste ».

**Le 13 octobre 2026, la demande.** « Action 138, étape 16 : son reste, les
coefficients de l'Agirc d'avant 1955 et de l'Arrco d'avant 1965 ; trouve
d'abord les textes de 1947 et de 1961. » Le dépôt servait à toute date la
table des accords, 0,78 à soixante ans, sans aucun ajournement, et sa fiche
disait n'avoir lu ni l'un ni l'autre texte.

- *Le texte de 1947.* La convention n'est ni au Journal officiel ni dans
  KALI ; l'index JORF n'a que la notice de l'arrêté d'agrément du 31 mars 1947.
  Son texte d'origine, annexes comprises, est publié par dcalin.fr, un site
  d'éducation spécialisée qui reproduit « la version originale intégrale »
  des textes de la Libération : une copie numérisée de vingt-six pages et une
  transcription. Lu à l'image, annexe I, article 6 : liquidation « au plus
  tôt, à l'âge de 55 ans », « La retraite normale est liquidée à l'âge de 65
  ans », puis les points « affecté[s] des coefficients d'anticipation ou
  d'ajournement ci-après » — 0,40 à 55 ans, 0,47, 0,54, 0,61, 0,66, 0,72 à
  60 ans, 0,76, 0,81, 0,87, 0,93 à 64 ans ; 1,05 à 66 ans, 1,10, 1,15, 1,20,
  « 70 ans et au delà 1,25 ». La transcription a ses coquilles ailleurs
  (« 1er janvier 1956 » pour 1936), pas dans ces nombres. La colonne
  « 1947-1955 » du document n° 13 du COR (28 janvier 2009, p. 15) les donne
  aussi ; l'IPP y met ceux de l'Arrco de 1957 et 1,05 dès soixante-cinq ans :
  l'écart E5 du registre est tranché, l'IPP a tort.
- *Le texte de 1961.* L'accord a été agréé par l'arrêté du 27 mars 1962,
  « ACCORD PUBLIE EN ANNEXE », au Journal officiel du 31 mars 1962 : l'index
  n'en a que la notice. Légifrance et NATLEX refusent la session, Gallica lui
  oppose une page de contrôle, et le PDF de la caisse est la version
  consolidée de 2018, dont l'annexe A date de 1999. L'accord du 15 mai 1957
  qui crée l'UNIRS n'est pas au Journal officiel. Le COR et l'IPP donnent à
  l'UNIRS, de 1957 à 1965, 0,75 à soixante ans … 0,95 à soixante-quatre, et un
  ajournement de 1,05 à 1,25 qu'ils écrivent dès l'âge normal — le décalage
  d'un an que le texte de 1947 dément à l'Agirc. Sans le texte, le dépôt
  n'écrit pas cette table.
- *Ce qui change.* Un interrupteur nouveau, `bareme_anticipation`
  (`_schema.yaml`, `regimes.py`, le paquet), et une fiche,
  `coefficients_anticipation_agirc_1947`, à laquelle renvoient les trois
  périodes de l'Agirc de 1947 à 1954 : l'anticipation par année d'âge révolue
  (`liquider.coefficient_convention_1947`, et son jumeau), l'ajournement par
  la majoration par âge seul de ces périodes, 1,25 % par trimestre au pas de
  quatre, de soixante-cinq à soixante-dix ans — 5 % par année révolue, ligne
  pour ligne la table du texte. Le passage à la table des accords est supposé
  au 1er janvier 1955, comme l'IPP : l'avenant qui le fait n'est pas
  identifié (réforme `agirc_ajournement_1955` au calendrier). Le registre
  sépare le point de l'IPP : l'Agirc reprise, l'Arrco à reprendre.
- *Ce que ça déplace.* Le cadre né en 1888, parti à soixante ans en 1948,
  prend 0,72 au lieu de 0,78 ; à soixante-deux ans en 1950, 0,81 au lieu de
  0,88 ; celui de 1882, parti à soixante-sept ans en 1949, 1,10 au lieu de 1 ;
  à soixante-dix ans en 1952, 1,25. Aucun témoin de simulation, le simulateur
  commençant aux nés de 1900, et aucun chiffre du chiffrage ; aux agrégats de
  la page Coût, les cadres des générations 1880 à 1890 : le cumul passé du
  système notionnel rétroactif gagne 24 millions d'euros sur 2 891 milliards,
  les coûts de 1959 à 1992 au plus 0,05 %, les avantages au plus 0,07 %, et
  rien après 1992. Deux chiffres ancrés du README suivent : le poids du site
  et le nombre de réformes au calendrier, que GitHub refait.
- *Les pages.* Rien à y écrire : aucune ne décrit ces coefficients, et la
  formule de la pension, qui les affiche, vient du moteur.
- *Nés de la lecture*, dans la fiche, à d'autres étapes : l'article 7, dix
  années de cotisation au moins, faute de quoi l'article 9 rembourse les
  cotisations ; l'article 10, un versement unique quand l'allocation
  trimestrielle est « inférieure à vingt fois le salaire horaire de
  référence », quand la fiche `versement_unique_agirc_arrco` n'en lit aucun
  avant 2004 ; l'article 12, la veuve à soixante ans après quinze années de
  services, dès cinquante avec la même table décalée de cinq ans ;
  l'article 22, les cadres sortis d'activité avant le 1er avril 1947 ; l'âge
  d'ouverture de soixante ans des périodes de l'Agirc, quand la convention
  dit cinquante-cinq, sans effet sur le calcul.
- *La veille.* Le serveur de la DILA sert de nouveau ses incréments : celui du
  12 octobre est appliqué, et ni L. 161-17-2 ni L. 161-17-3 n'ont de version
  postérieure au 31 décembre 2025.

**Ce qui reste.** L'Arrco d'avant 1965 : le fac-similé du Journal officiel du
31 mars 1962, à télécharger sur Légifrance depuis le poste du propriétaire,
comme les quatre textes de l'étape 17, puis le règlement de l'UNIRS ; si le
texte de 1961 renvoie aux règlements des caisses, c'est celui de l'UNIRS qui
fait la table, et le texte qui la change en 1965, que l'IPP date du
1er janvier. L'Agirc : l'avenant de 1954 ou de 1955 qui supprime
l'ajournement, que les arrêtés d'extension du 13 janvier 1955 et du 28 mars
1956 visent peut-être, au fac-similé lui aussi. Et, à la fin de l'étape, la
ligne « Coefficients d'anticipation Agirc-Arrco » des limites.
