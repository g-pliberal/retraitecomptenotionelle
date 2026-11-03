# La forme des liens de la base : l'état passager de son import de nuit

**Ce qui a été vérifié, le 3 novembre 2026, avec l'en-tête des récupérateurs du dépôt**
(`cnav_api.ENTETES`, rien d'autre). De 5 h 44 à 5 h 46 UTC, les sept collections de
l'API, puis trois fois `/expose` et `/liste`, servis à l'identique : l'import de la nuit
(exposés à 5 h 00 min 13 s, listes à 5 h 00 min 24 s), et, dans les exposés, 7 379 liens
vers des références, 870 vers des barèmes ou des listes, 619 vers des exposés et 420 vers
des fenêtres, sous les routes du site (`#/…?file_leaf_ref=`, `#/infosupp/`), et 1 619 PDF
sous `/Pdf/`. Les références et les fenêtres demandées une à une, et les dernières
circulaires, de même ; à 6 h 08, encore. Six liens seulement suivent les chemins du site
SharePoint, anciens — leurs exposés sont datés de 2023 à septembre 2026 — et sans objet de
la base : cinq vers un dossier, `RefReg/textes`, sans fichier, un vers une page de
`N_I_GDLC_Campus_Bar` que la base ne sert pas. Le récupérateur, inchangé, relu sur cette
base de 5 h 47 à 5 h 57, a refait le registre à l'octet près — 9 541 objets, les 21 liens
morts et les 78 objets nommés sans être servis de l'étape 1 —, et
`python scripts/veille_droit.py` n'y voit « rien de neuf depuis le registre ».

**Ce que l'étape 4 avait vu.** Sa base, téléchargée à 5 h 01 min 40 s par le même en-tête
— une minute après l'import des exposés et des listes, quand les avis de mise à jour
portaient encore celui de la veille, du 2 novembre à 5 h 02 —, liait par les chemins du
site SharePoint. Son relevé de 5 h 03, sur les exposés : 7 374 liens vers
`/sites/N_GDLC_Campus_Ref/SitePages/`, 1 619 vers `/sites/N_GDLC_Campus_Ref/RefReg/textes/`,
862 vers `/sites/N_GDLC_Campus_Bar/SitePages/`, 619 vers `/sites/N_GDLC_Campus/SitePages/`,
420 vers `/sites/N_GDLC_Campus_Com/SitePages/` : les comptes de 5 h 44, à quelques liens
près, sous l'autre forme. Ainsi, tels que servis :
`/sites/N_GDLC_Campus_Ref/SitePages/CR_CN_6096_28061996.aspx`,
`/sites/N_GDLC_Campus_Ref/RefReg/textes/circulaire_cnav_2016_41_17102016.pdf`,
`/sites/N_GDLC_Campus_Bar/SitePages/aspa_ressource_exclue_list.aspx`,
`/sites/N_GDLC_Campus_Com/SitePages/ex_polygamie.aspx`. Le même import, les mêmes dates de
modification : la base sert d'abord ce que l'import apporte du site SharePoint, puis le
récrit dans ses routes, entre 5 h 03 et 5 h 44. Rien ne dit si elle passe chaque nuit par
cet état.

**Pourquoi rien n'a été porté au récupérateur.** Cet état diffère de la base relue par
plus que ses liens : des formes que le relevé ne montre que par leur début
(`/Pages/textes/D_IM_201100…`, cinq ; `/Bareme/Articles/…`, six ;
`/sites/N_GDLC_Campus_Bar/oldBareme/…`, deux documents joints ; une adresse de
`cnavts.sharepoint.com`) ; les barèmes, les fenêtres et les références, que l'étape 4 n'a
pas demandés dans cet état ; les avis, pas encore réimportés. Lire ces liens ne rendrait
pas sûre une lecture faite pendant l'import : le récupérateur y lirait une base à moitié
importée. Le site ayant changé, ce moment-là, plus que ses liens, l'étape s'arrête ici,
comme le voulait sa consigne.

**La question au propriétaire.** Le récupérateur doit-il refuser, en le disant, de relire
une base qui lie encore par les chemins du site SharePoint — son import de nuit en cours —,
et laisser le registre tel qu'il est ? Avis : oui ; quelques lignes, et un test sur un lien
de 5 h 01. Sinon, la règle suffit : ne pas relancer `cnav_legislation.py` entre 5 h et
6 h UTC.

**Au passage.** L'API sert à 258 exposés un champ `voirAussi`, que le dépôt ne nomme
nulle part : une liste de liens « voir aussi » — à 5 h 01, des adresses de
`cnavts.sharepoint.com` —, vers des exposés seulement, dont 452 que leur contenu ne lie
pas. Un exposé tenant son thème du menu, le registre n'en perd rien. Aucun fichier de
code, de test ni du registre n'a changé, et aucune autre file n'a été touchée. La mise en
garde du bloc de l'étape 4, dans la note du thème « Carrière : cotisations-salaires », est
à récrire par la session qui reprendra l'étape.
