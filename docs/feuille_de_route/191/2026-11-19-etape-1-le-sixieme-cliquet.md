# Étape 1 de la note 0009 : le sixième cliquet, l'alarme « loi modifiée »

Le 19 novembre 2026, la seconde session de l'étape 1 pose le sixième cliquet,
que l'amendement du même jour ajoute à la note de décision 0009, avec le délai
de quatorze jours que le propriétaire a choisi. Aucune fiche, aucune règle,
aucun fichier de régime ne change, et aucun résultat ne bouge. L'étape 1 est
finie : les six cliquets et la garde de l'âge du taux plein sont sur `main`.

**Les comptes du jour.** Refaits le 19 novembre par
`docs/decisions/0009/sixieme-cliquet/mesures.py`, sur la liste lue dans
l'index le 16 : ce sont ceux de l'amendement, l'inscription du lundi n'étant
pas repassée. 518 couples d'une fiche et d'une rédaction en vigueur ou à venir
sans réponse, pour 146 fiches : 435 où la fiche cite la rédaction sans l'avoir
coupée en version, 83 où elle n'en dit rien. 136 couples d'une fiche et d'une
réforme : 40 ont leur version à la date, 96 sont à classer.

**Deux couples vérifiés à la main.** `sportifs_haut_niveau` cite R. 351-12 du
code de la sécurité sociale dans la rédaction du 1er septembre 2023
(LEGIARTI000047985880) ; celle du 1er novembre 2026 (LEGIARTI000054425288,
`redactions.csv`, en vigueur, sans date de fin) n'y est pas nommée, alors que
quatre autres fiches la citent. `taux_maximum_fonction_publique` cite
l'article 15 du décret n° 2003-1306 dans la rédaction du 1er août 2026
(LEGIARTI000054590023) ; celle du 14 octobre 2026 (LEGIARTI000054978195,
inscrite le 14 octobre) n'y est pas nommée. Les deux sont comptées parmi les
83, à juste titre.

**Ce qui est posé.**

1. *Les rédactions sans réponse* : `textes.sans_reponse`, fiche par fiche, les
   rédactions en vigueur ou à venir des articles cités auxquelles la fiche n'a
   répondu ni par une version ni par une déclaration sans effet. Elle reprend
   de `non_lues` l'article sans numéro, l'homonyme et la rédaction jamais en
   vigueur, qu'elle écarte ; le rattachement par une autre fiche n'y vaut plus
   réponse. `non_lues` reste, pour `--non-lues`.
2. *L'alarme* : `textes.alarme`, et sur le dépôt
   `test_aucune_loi_modifiee_n_attend_sa_reponse_au_dela_de_quatorze_jours`.
   La pose est datée du 19 novembre (`cliquet.pose_le`, `perimetre.yaml`) :
   une rédaction inscrite après fait échouer la suite le quinzième jour après
   son inscription, si une fiche qui cite son article n'a pas répondu ; le
   message dit la fiche, l'article, la rédaction et les deux réponses.
3. *La dette d'avant la pose*, deux nombres du même fichier :
   `citees_sans_reponse: 435` et `sans_un_mot: 83`. Ils se comptent au jour
   de la pose, non au jour du test : sinon le passage d'une date, le
   1er janvier 2027, où finissent onze rédactions d'articles cités, les
   ferait baisser seul et rougirait `main` sans qu'aucune session y soit
   pour rien.
4. *Les tests de poche*, dans `tests/test_textes.py`, chacun vu rouge : la
   rédaction nouvelle sans réponse ; la version et la déclaration sans effet
   qui répondent ; l'autre fiche qui la rattache, sans effet pour la
   première ; la rédaction nommée à rattacher, dans une lecture ou à relire,
   qui reste sans réponse ; treize jours, la suite passe, quinze, elle
   échoue ; la dette qui ne monte pas et s'abaisse.
5. *La veille* : `carte.a_relire` reçoit `sans_reponse` et
   `scripts/veille_droit.py` le lui donne, à la place des rédactions non
   lues, qu'il contient. Elle montre la fiche qui doit une réponse à une
   rédaction inscrite après la pose, dès l'inscription et avec le jour de
   l'échec, et celle qui ne dit rien d'une rédaction : 51 fiches ce jour, là
   où elle en montrait une. La dette de la migration, les 435, n'en fait pas
   une fiche à relire. `python scripts/textes.py --sans-reponse [fiche]` donne
   le compte par fiche et le détail, avec le mot à mot si l'index est là.
6. *Le tableau de bord* compte les rédactions inscrites depuis la pose qui
   attendent, la première échéance et la dette (`loi_modifiee`).
7. *Les réformes* :
   `test_chaque_reforme_declaree_a_sa_version_ou_dit_ou_elle_est_portee`,
   dans `tests/test_carte.py`, et sa liste,
   `tests/cliquets_du_droit_date/reformes.yaml`. Les 96 couples y sont tous
   `a_faire` : la session n'a lu aucun des textes, et le brief ne permet de
   classer `portee` ou `sans_version` que ce qui est lu. Le commentaire de
   chacun dit ce que la fiche a : 49 sont dans une fiche sans version, 17 ont
   une version qui commence la même année un autre jour, 30 aucune cette
   année-là. Le cliquet est à 96.
8. `docs/veille_droit.md` décrit l'alarme, à l'étape 4 de la méthode.

**À savoir.** Le cliquet `citees_sans_reponse` monte quand une session cite
un article de plus dans une fiche sans version : chaque rédaction en vigueur
ou à venir de cet article, que la fiche ne coupe pas, s'y ajoute. Si cela gêne
une session de la zone des données, le dire au propriétaire plutôt que
relever le nombre. L'inscription du lundi suivant, le 23 novembre, sera la
première à compter : ce qu'elle apporte d'un article cité devra avoir sa
réponse le 7 décembre au plus tard. Le workflow du lundi et les hooks n'ont
pas été touchés.

**Ce qui reste, hors de l'étape**, chacun sur l'accord du propriétaire : lire
les 83 rédactions dont les fiches ne disent rien, les plus récentes d'abord
(18 commencent en 2026 ou après) ; classer les 96 réformes ; mettre KALI à
jour le lundi, sans quoi l'alarme n'entend pas les avenants de
l'Agirc-Arrco.

**Ce que l'étape a coûté.** Une session d'environ une heure et demie, un
commit, onze fichiers : `noyau/textes.py`, `noyau/carte.py`,
`scripts/textes.py`, `scripts/veille_droit.py`, `scripts/tableau_de_bord.py`,
`perimetre.yaml`, la liste des réformes, trois fichiers de tests,
`docs/veille_droit.md`, et cette note.
