# L'accès depuis un poste : le PDF de la DREES, sa licence et ses classeurs

**Le 2 novembre 2026, ce qui est fait**, depuis le poste du propriétaire, où
le site de la DREES répond, par une requête simple sous l'en-tête des
récupérateurs du dépôt (`retraite-notionnelle/0.1 (recherche publique)`),
rien de maquillé. Toute session lit désormais le panorama et ses classeurs.

1. *Le PDF.* La page mène à l'ouvrage par deux liens : le bouton « Ouvrage »
   de son en-tête (`…Édition 2026_0.pdf`) et l'onglet « Ouvrage »
   (`…Édition 2026.pdf`, le `document` du manifeste). L'un et l'autre rendent
   9 983 866 octets, à l'empreinte de la copie de l'UNSA (`9eb36a06…`) : le
   miroir est le fichier de la DREES, octet pour octet, et le relevé de
   l'étape 1 vaut pour lui sans rien refaire.
2. *La licence.* Les mentions légales du site (mises à jour le 2 juin 2026),
   rubrique « II. Conditions générales d'utilisation » : ses publications et
   bases de données « sont des œuvres originales dont l’Administration
   concède des droits de reproduction et de diffusion », aux conditions de
   l'article D. 323-2-1 du code des relations entre le public et
   l'administration ; ses marques et logos ne sont pas librement
   réutilisables. Au pied de chaque page : « Sauf mention contraire, tous les
   contenus de ce site sont sous licence etalab-2.0. » Ni le PDF ni aucun
   classeur ne porte de mention contraire (ni « © », ni « droits réservés »,
   ni « reproduction », ni licence). Les deux jeux du manifeste déclarent
   `rediffusion: libre`, la clause citée, où et quand elle a été lue, et la
   mention que la licence exige : la source et la date de mise en ligne.
3. *Les classeurs.* L'onglet « Données » de la page en sert trente-six : un
   par fiche, un pour la vue d'ensemble, un pour l'annexe 2 (sources et
   méthodes), 1,85 Mo en tout, tous mis en ligne le 14 octobre 2026. Aucun ne
   porte de macro (les `.bin` sont des réglages d'impression) ni de logo :
   les seules images, dans trois classeurs, sont des pictogrammes de quelques
   pixels, une flèche, un trait. Leur étiquette de confidentialité est
   « C1 - Standard ».
4. *L'archive.* `drees_panorama_retraites_2026_classeurs.zip` les réunit tels
   quels, octet pour octet, sous des noms simples (`fiche_NN.xlsx`,
   `vue_d_ensemble.xlsx`, `annexe_02.xlsx`) : rangés par nom, stockés sans
   compression, datés du 14 octobre 2026 à minuit, de sorte que deux passes
   rendent la même archive, 1 858 599 octets (`ec7503f8…`). Elle est sur la
   release `documents-apportes`, déposée par `gh release upload`, avec sa
   ligne au corps de la release, écrite par `_citer` pour que `--mentions` la
   trouve conforme ; GitHub lui calcule la même empreinte. Le manifeste la
   déclare (`blocage: refus`, `fichier_local`, `miroir`, `sha256`,
   `rediffusion`), et son champ `contenu` dit de chaque classeur son adresse
   à la DREES et l'empreinte de ce qu'elle sert. Un jeu pour l'archive plutôt
   qu'un par classeur : trente-six jeux auraient répété trente-six fois la
   même licence, et le workflow mensuel aurait demandé chaque mois trente-six
   fichiers à un site qui refuse le cloud. Sans `document`, faute d'adresse à
   la DREES pour l'archive, ce workflow ne la retélécharge pas.
5. *La vérification.* `data/brut/` sans l'archive, `recuperer(jeux)` sur les
   deux jeux du panorama l'a rapportée de la release, sans jeton, à son
   empreinte, et ses trente-six membres portent celles de `contenu` ; le PDF
   de la DREES, déposé dans `data/brut/` sous le nom du miroir, y est « déjà
   là, conforme ». `tests/test_drees_panorama.py` exige ces déclarations :
   l'adresse du PDF à la DREES et sa licence, l'archive sur la release, un
   classeur par fiche du relevé et les deux autres, chacun à son adresse et à
   son empreinte, celles de la fiche 1 écrites en entier.

**Ce que les classeurs portent de personnel.** Trente-cinq nomment dans leurs
métadonnées l'agent de la DREES qui les a modifiés en dernier, et vingt-neuf
leur auteur — un nom, un identifiant de connexion, une fois une adresse
électronique professionnelle. Neuf portent des liens externes vers les
classeurs de travail d'où viennent leurs graphiques : serveurs du ministère,
identifiants de connexion de cinq agents dans sept d'entre eux, et, dans
trois, le nom d'une personne au dossier des archives d'anciens agents. La
licence le prévoit : un document qui contient des données à caractère
personnel se réutilise librement « à condition de respecter le cadre légal
relatif à la protection des données à caractère personnel ». Trois voies ont
été soumises au propriétaire : publier des copies dont ces métadonnées et ces
chemins seraient effacés, publier tels quels, garder les classeurs sur le
poste. Il a choisi de les publier tels quels, comme la DREES les sert, par le
raisonnement du rapport de la Cour sur les successions, qui nomme ses
magistrats : rien n'en est extrait, et l'asset se retire si la DREES le
demande. Ni ces noms ni ces chemins ne sont recopiés dans le dépôt : ils ne
sont que dans les classeurs de l'archive.

**Comment lire un classeur**, depuis toute session :
`python scripts/fetch/source_locale.py --recuperer`, ou `recuperer(jeux)` sur
le seul jeu des classeurs, puis
`zipfile.ZipFile("data/brut/drees_panorama_retraites_2026_classeurs.zip")`,
dont `read("fiche_15.xlsx")` rend le classeur de la fiche 15, à vérifier à
l'empreinte que `contenu` lui donne. Une édition corrigée par la DREES se
relève depuis un poste, classeur par classeur, contre `contenu` ; l'archive
se refait alors par la même recette, et se redépose.

**Ce qui reste.** Les étapes 2 à 7 de l'action, une session chacune. La 6,
les séries des graphiques que le PDF ne chiffre pas, n'attend plus personne ;
la 3 peut lire les classeurs des fiches 12 et 21 sans passer par le portail.
