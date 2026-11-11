# Étape 6 : la passe de lecture des rédactions en vigueur ou à venir, zone par zone

**Reprise, au 11 novembre 2026.** Rien n'est commencé, et l'étape attend la
fin de l'étape 4, qui change la liste des rédactions. Le propriétaire a dit
oui, le 11 novembre, à des sessions dédiées, zone par zone, pour lire les
rédactions en vigueur ou à venir que les fiches n'ont pas lues : ce jour-là,
92 rédactions sur 56 fiches. Chaque session prend un lot de fiches, lit
`python scripts/textes.py --non-lues <fiche>`, et donne à chaque rédaction
son statut dans la fiche, en commençant par celles qui ont pris effet depuis
décembre 2025. Elle se mène sur Fable 5.2, comme toute lecture du scénario 1.
Les lots, la règle du cliquet et ce qu'on fait d'une rédaction qui change une
règle sont ci-dessous. Chaque lot tient sa note, et son bloc s'il s'arrête en
chemin.

**La demande, le 11 novembre 2026.** La session qui a mesuré les outils (note
`2026-11-11-sorties-et-temps-des-outils.md`) a demandé au propriétaire :
« Faire lire les 92 rédactions en vigueur par des sessions dédiées, zone par
zone ? Je recommande oui, en commençant par celles qui ont pris effet depuis
décembre 2025. » Sa réponse : « oui pour les deux », l'autre question étant
celle de l'étape 4.

**Pourquoi.** Une fiche peut appliquer une rédaction que LEGI a remplacée,
sans que rien le dise. La décision du 3 novembre confiait cette lecture aux
sessions de chaque zone, au fil de la veille : en huit jours, on est passé de
57 fiches et 94 rédactions à 56 et 92.

**Les lots, au 11 novembre**, avant l'inscription de l'étape 4, qui en
ajoutera : à refaire le jour où l'étape s'ouvre, par
`python scripts/textes.py --non-lues`. Une fiche va au lot du texte qui porte
le plus de ses rédactions en vigueur ou à venir, pour que deux sessions
n'écrivent jamais dans la même fiche. Une rédaction que deux fiches n'ont pas
lue se compte deux fois : 110 lectures pour 92 rédactions.

| Lot | Fiches | Lectures | Dont depuis décembre 2025 |
|---|---|---|---|
| Le code de la sécurité sociale | 23 | 50 | 17 |
| La fonction publique | 8 | 16 | 11 |
| Les non-salariés agricoles | 7 | 19 | 14 |
| Les autres régimes | 18 | 25 | 10 |

- *Le code de la sécurité sociale* : `taux_plein_a_soixante_cinq_ans` (7),
  `micro_social_abattement` (6), `reversion` (6),
  `cnavpl_allocation_avant_2004` (4), `minimum_vieillesse` (3),
  `assiette_rco_independants`, `conjoint_collaborateur_independants`,
  `cumul_emploi_retraite_et_retraite_progressive`, `minimum_contributif`,
  `stages_formation_professionnelle`, `trimestres_avant_1972` (2 chacune),
  `assiette_minimale_independants`, `avpf`, `cnavpl_valeur_service`,
  `compagnie_generale_eaux_transfert_1991`, `conge_supplementaire_naissance`,
  `cultes_fractions_de_pension`, `exoneration_independants_outre_mer`,
  `majoration_forfaitaire_reversion`, `retraite_progressive`,
  `revenu_annuel_moyen_independants`, `salaire_annuel_moyen`,
  `sportifs_haut_niveau` (1 chacune).
- *La fonction publique* : `carriere_longue` (5),
  `categorie_active_duree_requise` (3),
  `cumul_emploi_retraite_fonction_publique` (2),
  `duree_requise_carriere_longue_fonction_publique` (2),
  `bonification_cinquieme_militaires`, `militaires_duree_requise`,
  `retraite_pour_invalidite_fonction_publique`, `reversion_fonction_publique`
  (1 chacune).
- *Les non-salariés agricoles* : `majoration_retraite_proportionnelle` (5),
  `retraite_proportionnelle_msa` (5), `pension_majoree_reference` (3),
  `pension_non_salaries_agricoles_2026` (3), `assiette_minimale_agricole`,
  `complement_differentiel_rco`, `cotisation_vieillesse_agricole_avant_2003`
  (1 chacune).
- *Les autres régimes* : `saint_pierre_et_miquelon_pension_de_base` (4),
  `prime_speciale_sujetion_aides_soignants` (3),
  `retraite_anticipee_handicap` (3), et quinze fiches d'une rédaction :
  `abattement_rci`, `asv_autres_professions_de_sante`,
  `categorie_active_super_active`, `decote_avant_1983`,
  `depart_anticipe_parents_trois_enfants`, `limite_age_opera`,
  `limite_age_ouvriers_etat`, `mayotte_pension_de_base`,
  `organic_conjoints_de_commercants`, `points_avant_1973_independants`,
  `raap_classe_speciale`, `regies_ferroviaires_pensions_en_extinction`,
  `reversion_rci`, `surcote_par_age_seul`,
  `taux_plein_anciens_combattants_prisonniers`.

**Ce que fait la session d'un lot.**

1. Elle ouvre comme toute session du scénario 1 : `docs/veille_droit.md`,
   `python scripts/veille_droit.py`, l'index LEGI récupéré et mis à jour.
2. Pour chaque fiche de son lot, `python scripts/textes.py --non-lues
   <fiche>` montre les rédactions en vigueur ou à venir et leur mot à mot.
   Elle lit chacune, les plus récentes d'abord, et lui donne son statut dans
   la fiche (`docs/architecture.md`, § 6.6 ; `docs/veille_droit.md`,
   étape 4) : citée par la version de la fiche qui l'applique ; sans effet
   (`textes_sans_effet`), le mot à mot pour preuve — une rédaction « (texte
   inchangé) » se déclare d'une ligne ; à rattacher (`textes_a_rattacher`),
   quand elle change le droit sans que la fiche soit encore coupée ; à relire
   (`textes_a_relire`), quand son effet reste à lire. Le mot à mot de l'index
   est bruité quand une note d'application naît ou disparaît : lire alors les
   deux versions (`dila_cherche.py legi --num <article> --le <date>`).
3. *Une rédaction qui change ce que le modèle calcule* ne se porte pas au
   modèle dans cette passe, qui lit et classe : la fiche le dit (son état,
   `sources.a_relire`), la note du lot la range sous « Ce qui change une
   règle », avec l'article, la date d'effet et ce qui change, et le
   propriétaire décide de l'étape qui l'écrira. C'est la proposition de la
   session du 11 novembre, faute d'autre consigne ; il peut en décider
   autrement.
4. *Le cliquet.* `perimetre.yaml` tient le compte exact des rédactions sans
   statut : après ses fiches, la session l'abaisse au nombre que
   `python scripts/textes.py` imprime. Deux lots qui poussent le même jour se
   heurtent sur cette ligne : rattraper `main`, puis refaire le compte, sans
   garder l'un des deux nombres.
5. Elle met à jour `sources.lu_le` et `sources.prochaine_relecture` des
   fiches relues, écrit sa note, `<date>-etape-6-<lot>.md`, et son entrée du
   journal de veille.

**Fini quand** : `python scripts/veille_droit.py` ne compte plus de fiche à
relire pour une rédaction non lue, ou chaque reste est nommé dans la note
d'un lot ; ce que la lecture a trouvé qui change une règle est porté à la
connaissance du propriétaire, en une liste.
