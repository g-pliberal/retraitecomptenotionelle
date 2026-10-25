# L'étape 7 : Partager et Le saviez-vous ?, la même chose en moins de mots

**La demande.** Lot du 24 octobre 2026, quatrième vague : le propriétaire
demande une session par tâche, menée sans lui, dix en même temps ; celle-ci,
seule du lot sur les pages, mène l'étape 7 de l'action 173 : « Partager et Le
saviez-vous ?, moins de mots sans perdre une idée ».

**Ce qui se lit sans déplier.** Le budget de lecture de Partager
(`BUDGETS_DE_LECTURE`, `tests/test_web.py`) passe de 400 à 340 mots : vu rouge
pour 372, la page en montre 331. Sous le texte prêt à coller, une note disait
que le bouton de chaque carte met « ce message » dans le presse-papiers ; il y
met celui de sa carte, qu'il compose de son chiffre, de sa phrase et de son
détail (`texteDeLaCarte`, `index.html`) : la note fausse s'en va, et le
chapeau de l'affiche dit déjà que chaque image part avec son message.
L'encadré « Et depuis les pages du site » redisait le filigrane que ce chapeau
décrit, et dit « filigrane compris » ; le chapeau perd « et non dans un coin »,
que « le recadrer revient à recadrer la carte » explique. Sur la carte du taux,
« comme aujourd'hui » redisait les 28 % de la ligne d'au-dessus.

Celui de Le saviez-vous ? passe de 700 à 640 mots : vu rouge pour 673, la page
en montre 636. Le chapeau de l'affiche disait « une carte par règle, avec le
texte officiel qui la fonde », que le titre dit en trois mots (« textes à
l'appui ») ; il ne garde que la date de lecture et le bouton. Celui de « Un
même deuil, trois règles » énumérait ce que ses trois cartes disent, le taux,
l'âge, ce qui fait perdre la réversion ; celui de « Cotiser sans acquérir de
droits » redisait son titre en dix-huit mots, il le redit en treize. La carte
« Trois taux » dit en seize mots ce qu'elle disait en vingt-deux ; celle de
l'équilibre technique disait deux fois « tout le salaire » (« de tout le
salaire, dès le premier euro ») et garde le premier euro. Les extraits que le
catalogue des affirmations suit sur ces deux cartes restent : le catalogue ne
change pas.

**Ce qui se lit en dépliant.** `BUDGETS_DEPLIES` prend les deux pages, à leur
adresse. Partager ne replie rien : sa ligne vaut son budget de lecture, et dira
si un dépliant y naît pour porter ce que la page a ôté. Le saviez-vous ? :
1 229 mots, vu rouge pour 1 190 ; 1 182 après. Sous « Ce que dit le texte », le
RAFP redisait qu'il se verse en rente à partir du seuil, que sa carte dit, et
les TUC « près de quarante ans après », que disent le 2023 et les « années
1980 » de la leur. Aucune règle ne change de sens, aucun lien ne bouge, aucune
simulation non plus : seuls les témoins des deux pages changent.

**Ce qui se lit ensemble.** `COTE_A_COTE` (`tests/test_ecrans.py`) prend les
deux pages : vert d'emblée, aucune n'ayant de tableau.

**Ce qui ne se voyait pas, trouvé en chemin.** À 1 024 points, la tablette en
largeur, la grille des cartes, qui demandait 32 rem par colonne, les rangeait
une par ligne, sur 944 points : un chiffre de 110 pixels, une carte par écran,
Partager sur 4 015 pixels et Le saviez-vous ? sur 10 959, deux fois plus qu'au
bureau ; le titre d'un thème, qui comble au large la case voisine de la
première carte, restait seul sur sa ligne. Deux cartes de front, dans l'image
réduite, auraient porté leur détail à neuf pixels.
`test_les_cartes_a_publier_vont_deux_par_ligne_et_se_lisent`, que mesure
`tests/js/ecrans.mjs`, exige deux cartes de front dès 1 024 points, et jamais
une phrase ou un détail sous douze pixels : vu rouge à 1 024 sur les cinq
grilles des deux pages, puis, la colonne passée à 28 rem, à 9,1 pixels. Les
tailles de lecture, que le téléphone prenait sous 34 rem d'écran, sont
désormais celles de toute carte de 32 rem ou moins, par une requête sur son
cadre (`@container`, `moteur/style.css`) : celles du téléphone, et les deux de
front d'une tablette. Le bureau garde l'aperçu au format de l'image, sur
519 pixels, le détail à 12,1 ; la composition retrouve le 16/9 à toutes les
largeurs, la classe `en-image` ayant quitté la requête du téléphone. À
1 024 points, Partager tient en 2 174 pixels, Le saviez-vous ? en 5 355.

**Ce que le propriétaire peut vouloir trancher.** À 1 024 points, l'aperçu
d'une carte n'a plus la forme de l'image, mais celle qu'il a sur un téléphone ;
l'image publiée, elle, ne change pas.

**Laissé tel quel.** Les chiffres des cartes et les textes qu'elles citent ;
le texte prêt à coller, qui est un message ; le surtitre « Le saviez-vous ? »
de chaque carte, que l'image emporte ; ce que dit le texte quand il énonce la
règle que la carte illustre — le semestre des marins, le plafond —, parce que
c'est ce que vient lire qui doute ; les intitulés des dépliants.
