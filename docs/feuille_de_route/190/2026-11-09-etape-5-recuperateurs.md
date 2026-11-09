# Étape 5 : les machines à états implicites des récupérateurs

**Le 9 novembre 2026, ce qui est fait.** Les récupérateurs de
`scripts/fetch/` sont relus pour ce qui garde un état sans le nommer : par
`Grep` d'abord — les boucles d'essais et les pauses, les fichiers partiels,
les caches sous `data/brut/` et en mémoire, les variables qu'un lecteur
remet ou non à nul —, puis la seule fenêtre utile de chaque candidat. Rien
n'est téléchargé ni relancé. Vingt-trois machines, numérotées à part de
l'inventaire de l'étape 1 : presque toutes saines, et la plupart gardées par
un contrôle qui refuse ce qu'il ne reconnaît pas. Deux défauts sont
reproduits, puis corrigés : l'index de la DILA se disait construit sur un
dump tronqué (1), et le cache des rapports à la CCSS servait le rapport de
printemps quand celui d'automne avait paru (8). Le reste se déclare. Les
numéros de ligne sont ceux du commit 0d03aaf, avant les deux corrections.

Les trois scripts en R n'ont pas de machine : `trajectoire.R` garde le cache
du paquet dans un dossier temporaire propre à chaque session de R
(48-52), qui ne survit pas à l'exécution ; `destinie_2.R` et `ines.R`
enchaînent leurs étapes sans état. `lecture_pdf.mjs` lit l'entrée, répond et
s'arrête (31 lignes). La sonde des sources (`sonder_sources.py:110-136`)
ne garde qu'une pause entre deux adresses.

## Les téléchargements

1. **L'index de la DILA** — `dila_index.py:315-329`, `342-429`, `572-646`.
   Le fichier en cache : absent, partiel (`.partiel`, que `curl -C -`
   reprend, et qu'un 404 efface), entier — et alors plus jamais redemandé,
   ce qui vaut pour une archive nommée par son horodatage, qui ne change
   pas. Puis la base, dont l'état est sa table `meta` : construite depuis le
   dump global (`dump`, `dernier_increment`), mise à jour incrément par
   incrément — `meta` puis `commit` à chacun ; un incrément interrompu se
   rejoue sans dommage, puisqu'il efface avant de réinsérer —, publiée.
   *Défaut, reproduit et corrigé.* `verser_archive` lisait le dump par
   `tar -xzO` sans regarder le code de sortie de `tar`, ses erreurs jetées :
   un dump tronqué se versait jusqu'à la coupure, et `construire` écrivait
   ensuite le dump et son horodatage, comme pour un index complet — la même
   famille que l'index construit vide sous Windows, que le commentaire de
   350-358 raconte. `tar` en échec lève désormais une erreur, et
   `construire` efface l'index à moitié versé
   (`test_construire_refuse_un_dump_tronque_sans_laisser_d_index`, vu rouge
   sur « 1 documents lus, 1 gardés »).
   *Déclaré.* `publier` laisse `<base>.sqlite.gz` dans le cache, que
   `recuperer` prendrait ensuite pour l'index publié, au lieu du plus récent,
   et dont il écraserait l'index local : sans effet sur `index-dila.yml`,
   qui part d'une machine neuve, mais un poste qui publie puis récupère se
   ferait reculer. La base tourne sans journal (`journal_mode=OFF`, 243) :
   un arrêt brutal en pleine mise à jour peut l'abîmer, et la reconstruire
   répare. Un dump sans horodatage dans son nom (`--archive`) laisse
   `dernier_increment` vide : `--mettre-a-jour` appliquerait alors tous les
   incréments du répertoire, sans dommage tant que la DILA n'y garde que
   ceux d'après son dernier dump global.
2. **Les grilles du CISIRH** — `cisirh_grilles.py:290-305`. Trente essais,
   dix secondes entre deux ; le fichier `.part` se réécrit en entier à
   chaque essai, et ne remplace l'archive qu'après `testzip`. Sain.
3. **Le COR** — `cor_comptes_retraite.py:222-254`. Quatre essais, la pause
   doublée de deux à huit secondes ; une erreur HTTP ne se redemande pas ;
   les classeurs se gardent le temps d'une exécution (`_CLASSEURS`), et un
   échec n'y entre pas. Sain.
4. **La Cnav** — `cnav_legislation.py:607-702`. Une route se redemande
   quatre fois, la pause doublée, une erreur 500 comprise (`_obtenir`) ;
   une référence ou une fenêtre deux fois, une recherche trois, puis
   « rien » ; un document en UTF-8, puis en latin-1. « Rien » vaut
   « absent » : une page qu'un échec passager laisse vide est retirée
   (`sans_les_pages_declarees_absentes`, 342-354) et passe aux disparus.
   *Déclaré.* Le registre (`inscrire`, 564-589) garde toute ligne dont le
   sort n'est plus `a_lire` : un échec passager ne coûte qu'une ligne encore
   à lire, que la lecture suivante remet.
5. **Epicycle** — `epicycle_bareme.py:425-433`. Trente essais, cinq secondes
   entre deux, puis l'empreinte SHA-1 que la notice publie. Sain.
6. **L'INSEE, par Melodi** — `insee_melodi.py:46-72`. Les pages de mille
   observations se suivent jusqu'à une page courte ou vide.
   *Déclaré.* À la cinquantième page pleine (`pages_max`), la boucle
   s'arrête sans le dire, et le JSON s'écrit tronqué ; aucun jeu lu
   aujourd'hui n'en approche, faute de quoi il faudrait le dire à l'écran.
7. **Le dump du JORF des cotisations libérales** —
   `jorf_cotisations_liberales.py:144-153`, `276-286`. Sans `--dump` ni
   index, l'archive se retélécharge entière, à chaque fois, dans un fichier
   que rien ne relit ensuite ; une coupure fait échouer la lecture en
   flux (`tarfile`). Sain, et hors d'usage : l'index de la DILA en tient
   lieu, et ses dumps ne se retéléchargent pas.

*Déclaré, pour 2 à 5.* Une réponse coupée avant la fin qu'elle annonce lève
`http.client.IncompleteRead`, qui n'hérite ni d'`OSError` ni d'`URLError` :
aucune de ces boucles ne la redemande, et la première coupure arrête le
récupérateur — bruyamment, sans valeur fausse. Le COR dit pourtant couper
« au milieu d'un classeur » ; si l'arrêt se voit, c'est l'exception à
ajouter aux quatre.

## Les mémoires

8. **Les rapports à la CCSS** — `ccss_transferts_retraite.py:178-212`, que
   reprennent `ccss_regimes.py:626` et `ccss_impots_retraite.py:152`. La
   page désigne un rapport par année, d'automne de préférence, à défaut de
   printemps ; le PDF se garde dans `data/brut/ccss_rapports/`.
   *Défaut, reproduit et corrigé.* Le cache se rangeait par année seule : le
   rapport de printemps gardé, celui d'automne paru ensuite ne se
   téléchargeait jamais, et la provenance écrite (`lus`, 383) disait
   l'automne d'un chiffre lu au printemps. Le fichier porte désormais
   l'année et le nom du rapport
   (`test_le_rapport_d_automne_ne_se_lit_pas_dans_celui_de_printemps`, vu
   rouge sur les octets du printemps).
   *Déclaré.* L'écriture n'est pas atomique, et un fichier de plus de
   100 000 octets se relit sans autre contrôle : un PDF coupé à l'écriture
   se relirait tel quel. Un rapport qu'on ne peut lire laisse ses années au
   rapport suivant, ce que la provenance dit.
9. **Les sources locales** — `source_locale.py:204-235`. Le fichier
   demandé, puis `data/brut/`, puis le miroir, puis le site ; ce qui est lu
   porte l'empreinte du manifeste quand il la donne, et le chemin lu
   s'écrit au journal. Sain : sans empreinte, un fichier local ne se périme
   pas, et le journal le dit.
10. **Les mémoires d'une exécution** — `lecture_pdf.py:35`,
    `drees_eacr.py:171` : des `lru_cache` dont la clé est le contenu même
    du document ; `cor_comptes_retraite.py:247`, par adresse. Rien ne
    survit au processus. Sains.
11. **Le registre de la Cnav** — `cnav_legislation.py:121`, `564-589`, et
    `cnav_veille.py:152-189`. Explicite : un vocabulaire fermé, `SORTS`, que
    `tests/test_cnav_legislation.py:691` impose à chaque ligne. Sain.

## Les lecteurs

12. **La section de la CNAV dans un rapport à la CCSS** —
    `ccss_impots_retraite.py:106-135`. Deux registres, comme le relevé lu
    (machine 14 de l'inventaire) : `colonnes`, le dernier en-tête d'années,
    et `dans_la_section`, qu'ouvre le titre de la CNAV et que ferment son
    total ou un en-tête de tableau. La première valeur trouvée l'emporte.
    *Déclaré.* Une section coupée par un saut de page dont l'en-tête se
    répète perdrait sa suite ; aucun test ne couvre ce lecteur.
13. **Le minimum vieillesse par régime** —
    `drees_panorama_classeurs.py:420-445`. `regime` n'est jamais remis à
    nul : une ligne d'un régime que la table ne connaît pas ne l'ouvre pas,
    et ses lignes « Métropole » et « DROM » écraseraient celles du régime
    précédent.
    *Déclaré.* Seul le total, exigé, garde le lecteur, et son test ne
    nomme que des régimes connus.
14. **Les pensions des indépendants** —
    `insee_revenus_independants.py:245-285`. Le même registre, que rien ne
    remet à nul ; mais les femmes et les hommes doivent faire l'effectif de
    leur régime, et les trois régimes celui de leur ensemble. Sain, gardé.
15. **Les figures du COR** — `cor_comptes_retraite.py:296-325`, où
    l'intitulé se reporte d'une ligne à la suivante, `640-672` et `676-700` ;
    `cor_leviers.py:80-111`, dont le levier courant se remet à nul après son
    niveau d'équilibre ; `cor_pouvoir_achat_retraite.py:52-70` ;
    `cor_regimes.py:155-178`, dont le bloc suit le dernier en-tête d'années.
    Sains : chaque lecteur refuse la ligne muette, la série inconnue ou le
    levier manquant.
16. **Le projet annuel de performances** — `pap_plf_2026.py:265-300`,
    `327-347`. Le régime s'ouvre au numéro de son action et se ferme au
    suivant, ou après sa ligne de crédits. Sain.
17. **La DG Trésor** — `dgtresor_trajectoires_smic.py:128-180`. Le tableau
    et son bloc, remis à nul sur « Source : » ; un bloc inattendu, ou un
    compte de valeurs faux, est refusé. Sain.
18. **L'Ageing Report** — `ageing_report.py:155-181`. La section et ses
    rangs se remettent sur chaque en-tête 2022-2023 ; une ligne cherchée et
    absente est refusée. Sain.
19. **Le panorama de la DREES** — `drees_panorama.py:138-175`. La fiche se
    reporte de page en page, la page imprimée aussi, plus un ; un encadré
    n'attend sa source que jusqu'à la figure suivante. Sain.
20. **Le jaune des pensions** — `sre_jaune_pensions.py:258-290`. Les
    bénéficiaires lus attendent leur bonification, et se remettent à nul
    après la durée moyenne, qui va à la dernière bonification lue ; le
    nombre de bonifications et les effectifs sont contrôlés.
    `sre_jaune_referents.py:108-135`, `410-425` : les mots d'une case, puis
    les lignes qu'un gabarit attend, dans l'ordre. Sains.
21. **Les tableaux de LEGI** — `dila_legi_durees.py:442-567`,
    `dila_legi_reclassements.py:738-795`, `dila_legi_grilles.py:400-445`.
    Des analyseurs à jetons écrits à la main : la ligne courante, le
    groupe, l'en-tête, le texte libre, la coupure. Chacun finit par un
    contrôle (`_remplir`, `_controler`, `_Refus`) qui refuse le tableau
    plutôt que de le lire faux. Sains, gardés.
22. **Les montants qui changent** — `dila_legi_parametres_retraite.py:356-365`,
    `dila_legi_minimum_contributif.py:250-269`,
    `dila_legi_taux_cotisation.py:605-622`,
    `ipp_points_independants.py:170-185`, `epicycle_bareme.py:284-301`. Une
    valeur précédente, sur des versions triées par date : un montant redit
    n'ouvre pas de période. Sains.
23. **Les lignes d'un PDF** — `lecture_pdf.py:95-115`. Un fragment rejoint
    la ligne courante s'il est sur la même page, dans la même bande, à la
    tolérance près du fragment précédent. Sain.
