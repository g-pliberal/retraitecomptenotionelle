# L'étape 4 : Simuler, la même chose en moins de mots

**La demande.** Vague du 23 octobre 2026, seconde salve : la session de suivi
« Qu'est-ce qu'il reste à faire ? » lance, sur la demande du propriétaire
(« Fait ça », en réponse à l'offre d'une session par chantier qu'une session
peut mener seule), l'étape 4 de l'action 173, maintenant que l'étape 3,
l'accueil, est poussée : « Simuler, moins de mots sans perdre une idée ».

**Ce qui se lit sans déplier.** Le budget de lecture de Simuler
(`BUDGETS_DE_LECTURE`, `tests/test_web.py`) passe de 1 500 à 1 020 mots. Il
vaut pour le formulaire, qui n'en montre que 149 depuis que les options de ses
menus ne comptent plus, et pour la page de résultats
(`test_la_page_de_resultats_replie_son_detail`), qui en montrait 1 091 : vu
rouge à 1 091, elle en montre 1 015. Partent « servi 1 ans plus tard que les
trois autres », que « pas à 64 ans mais à 65 ans » venait de dire, faute
d'accord comprise ; « si vous ne les placez pas, vous gardez le salaire net
plein, et la rente baisse », que la carte du système 4 dit en chiffres — tant
« sans rien ajouter », et tant « de plus si vous placez les cinq points
rendus » ; « le brut de chaque mois, base et complémentaire », que les colonnes
de l'estimation officielle portent ; l'annonce du détail, de vingt-six mots à
quatorze. La borne des résultats de `test_le_simulateur_tient_en_peu_de_mots`
descend de 1 700 à 1 300 (1 286 lus).

**Ce qui se lit en dépliant.** `BUDGETS_DEPLIES` prend Simuler à son adresse :
les résultats de la simulation témoin, formulaire compris, sans menus ni
bulles, et sans le JSON, qu'on copie et ne lit pas. 7 092 mots, vu rouge pour
6 850 ; 6 832 après. Les cinq points volontaires — ce qu'ils sont, qu'on les
place ou qu'on les garde, qu'ils font cotiser 28 % comme aujourd'hui — se
disaient cinq fois : une fois ouverts, sous « Et pendant que vous cotisez »,
une fois dans la méthode de la fiche de paie ; la note de l'épargne à votre nom
ne garde que ce qu'ils ajoutent au compte, le pilier ce qu'ils servent de la
rente. La lecture sous la fiche de paie ne redit plus les deux montants du
prélèvement, que sa ligne porte, ni que le coût du travail ne bouge pas, que
la méthode dit en gras juste dessous ; elle écrivait « le salaire brut monte de
-6,03 € » : le sens de chaque écart est désormais dans son verbe. Partent aussi
« C'est le levier que le troisième chiffre applique », que le paragraphe
suivant redit avec sa raison ; la phrase du système 2 sous les trois
hypothèses du COR, que la ligne du tableau donne ; trois introductions qui
redisaient la légende de leur tableau. « Il n'y a que trois façons de la
payer », que le quatrième levier démentait trois lignes plus bas, devient
« de l'une de trois façons ».

**Ce qui se lit ensemble.** À 320 points, les résultats empilaient dix rangées
de deux valeurs courtes, dans des tableaux pliés en fiche — la garantie
vieillesse étape par étape, le pilier, la pension du système 1 : la grille de
8,5 rem n'en laissait tenir qu'une par ligne. Un tableau en fiche à deux
valeurs les tient sur deux colonnes à toute largeur (`moteur/style.css`), une
phrase prenant toujours la ligne entière ; `COTE_A_COTE`
(`tests/test_ecrans.py`) prend le formulaire et les résultats, vu rouge sur
ces dix rangées. La règle vaut pour tout le site : Droits non cotisés,
qu'attendait l'étape 9, n'empile plus rien non plus, et son étape n'aura qu'à
s'ajouter à la liste.

**Laissé tel quel.** Le formulaire : ouvert, ses 149 mots sont des libellés
et des repères, plus un chapeau qui dit ce que la page compare et que tout
reste dans le navigateur ; déplié, ses 918 mots sont ceux de ses champs.
« En bref », qui répond en trois phrases avec les chiffres des cartes : c'est
un résumé voulu, symétrique (action 62). Ce que l'action 172 réserve au
propriétaire ou prend à son compte : la clé de lecture des quatre systèmes,
leurs libellés et leurs descriptions, « systèmes 2 à 6 seulement », le réglage
« Part de la cotisation portée au compte ». Aucun chiffre n'est récrit, aucune
simulation ne bouge.

**Vu en chemin.** La méthode de la fiche de paie d'un salarié du privé dit :
« Ce qu'il ne verse plus en cotisations, il le verse en salaire : le brut
monte, et le net avec lui. » Le partage retenu, deux paragraphes plus bas,
laisse pourtant à l'employeur ce qu'il verse, et le tableau de la simulation
témoin montre le brut baisser de 6 € : la phrase décrit l'hypothèse du coût du
travail fixe en général, non ce que la page calcule. Elle n'est pas une
redite, et l'étape ne l'a pas touchée.
