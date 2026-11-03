# Le refus de relire la base pendant son import de nuit

**La décision.** Le 3 novembre 2026, le propriétaire a répondu oui à la question de la note
`2026-11-03-forme-des-liens.md` (« La question au propriétaire », lignes 44 à 48) :
`scripts/fetch/cnav_legislation.py` refuse, en le disant, de relire une base qui lie encore
par les chemins du site SharePoint de la caisse — son import de nuit en cours —, et laisse
le registre tel qu'il est. Cette note relaie la réponse ; l'étape de la forme des liens est
finie, et son bloc « Reprise » ôté de sa note.

**Ce qui signale l'import.** Cinq familles de chemins, que l'étape 4 a relevées dans les
exposés de la base téléchargée le 3 novembre à 5 h 01 (note de la forme des liens, « Ce que
l'étape 4 avait vu », lignes 18 à 29 ; note de l'étape 4, lignes 85 à 89), par centaines
ou milliers de liens et avec leurs exemples : une page sous `SitePages/` de
`/sites/N_GDLC_Campus` (exposés, 619 liens), `/sites/N_GDLC_Campus_Bar` (barèmes et listes,
862), `/sites/N_GDLC_Campus_Com` (fenêtres, 420) ou `/sites/N_GDLC_Campus_Ref` (références,
7 374), et un fichier sous `/sites/N_GDLC_Campus_Ref/RefReg/textes/` (PDF, 1 619). Un seul
lien de ces familles suffit au refus : la base les récrit dans ses routes entre 5 h 03 et
5 h 44 (même note, lignes 30 et 31), et une base à moitié récrite en garde quelques-uns ;
un seuil serait inventé.

**Ce qui ne le signale pas.** Les six chemins anciens que la base ordinaire sert aussi (même
note, « Ce qui a été vérifié », lignes 10 à 13), relevés de nouveau le 3 novembre à 16 h 00
UTC dans les contenus des 633 exposés, 324 listes et 397 barèmes, avec l'en-tête des
récupérateurs : cinq fois le dossier
`/%3af%3a/r/sites/N_GDLC_Campus_Ref/RefReg/textes?csf=1&web=1&e=7VduC2`, sans fichier, et une
fois `/sites/N_I_GDLC_Campus_Bar/SitePages/Ressources-exclues-pour-la-retraite-de-r%c3%a9version.aspx`,
d'un autre site ; s'y ajoute un lien vers `www.info-retraite.fr/portail-info/sites/…`, hors
de la caisse. Ni les formes que le relevé de 5 h 01 ne montre que par leur début (même note,
lignes 35 à 38) : `/Pages/textes/D_IM_201100…`, `/Bareme/Articles/…`,
`/sites/N_GDLC_Campus_Bar/oldBareme/…`, une adresse de `cnavts.sharepoint.com`. Un motif
sur elles devinerait ce qui les suit ; une à six chacune, elles allaient avec les cinq
familles, qui suffisent. À 16 h, aucune des quatre n'était dans les contenus des trois
collections. Le champ `voirAussi` (même note, lignes 50 à 53) n'est pas lu : rien ne dit sa
forme hors de l'import.

**Le code.** `_IMPORT`, `liens_de_l_import` et quelques lignes de `main` : les liens des
contenus des barèmes, des exposés et des listes, les trois premières collections lues, avant
toute autre requête et toute écriture. Pris en faute, le script dit sur la sortie d'erreur
combien de liens suivent ces chemins, en nomme jusqu'à douze, dit l'import de nuit en cours,
que la lecture s'arrête là, que rien n'est écrit et que le registre reste tel quel, et de
relancer plus tard, hors de 5 h–6 h UTC ; il sort sur le code 1. Un lien égaré d'une de ces familles dans la base
ordinaire le ferait refuser de même : le message le nomme, à relire avant de toucher au
motif.

**Les tests**, dans `tests/test_cnav_legislation.py`, sans réseau, sur des réponses figées :
`test_une_base_en_plein_import_de_nuit_ne_se_relit_pas`, sur un lien de chaque famille —
les quatre exemples de la note de la forme des liens, lignes 26 à 29, et la forme de
l'exposé de l'étape 4, ligne 87, sur un exposé du registre —, vu rouge (le récupérateur
poursuivait sa lecture), puis vert ; `test_une_base_qui_lie_par_les_routes_du_site_se_relit`,
sur les routes du site, `#/infosupp/`, `/Pdf/` et les deux chemins anciens tels que servis à
16 h, qui ne le font pas refuser.

**Sur la vraie base**, hors de l'import : le récupérateur, avec son refus, relu de 16 h 05
à 16 h 13 UTC le 3 novembre, n'a pas refusé, est sorti sur le code 0, et a refait le
registre à l'octet près (`git status` n'y voit rien) : 9 541 objets, les 21 liens morts et
les 78 objets nommés sans être servis, comme la note de la forme des liens.

**Au passage.** La mise en garde du bloc « Reprise » de l'étape 4 (note du thème « Carrière :
cotisations-salaires ») ne tient plus depuis la note de la forme des liens ; elle reste à
récrire par la session qui reprendra l'étape, qui tient ce bloc. La veille
(`scripts/fetch/cnav_veille.py`, que `scripts/veille_droit.py` imprime) lit les mêmes
collections sans ce refus, et n'écrit rien : elle compare au registre des noms et des dates,
et l'import n'a pas changé les dates (note de la forme des liens, lignes 29 et 30) ; le
3 novembre au matin, elle n'a rien vu (note de l'étape 4, ligne 96).
