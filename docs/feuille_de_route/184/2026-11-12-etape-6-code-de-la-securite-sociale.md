# Étape 6, lot du code de la sécurité sociale : cinquante rédactions lues

Le lot est fini le 12 novembre 2026. Ses vingt-quatre fiches n'ont plus de
rédaction en vigueur ou à venir sans statut : cinquante rédactions, pour
cinquante-cinq lectures, cinq étant citées par deux ou trois fiches. Six sont
citées par la version de fiche qui les applique, trente-neuf sont déclarées
sans effet, le mot à mot pour preuve, cinq sont à rattacher. Le cliquet de
`perimetre.yaml` passe de 9 258 à 9 236. Aucune rédaction du lot ne change ce
que le modèle calcule aujourd'hui ; quatre points relevés en chemin attendent
une décision, plus bas. Ni `src/` ni `moteur/` ne sont touchés.

La consigne est celle de la note de l'étape,
`2026-11-11-etape-6-passe-de-lecture.md`, et le lot celui que la session
d'orchestration a refait après l'inscription de l'étape 4.

## Ce qui a été lu

L'index LEGI du dépôt, à jour au 11 novembre 2026, par
`python scripts/textes.py --non-lues <fiche>`, puis, pour chaque rédaction, son
texte entier et celui de la précédente (`dila_cherche.py legi --num <article>
--le <date>`). Le décret n° 2025-1409 du 30 décembre 2025, dont l'article 2
écrit cinq des rédactions du lot, a été lu en entier dans l'index du Journal
officiel (JORFARTI000053227542), avec son II, qui dit à quelles pensions
chaque retouche s'applique. Chaque passage cité entre guillemets dans une fiche
a été recherché dans la rédaction qu'il cite ; ceux qui n'y sont pas sont les
mots que la rédaction ôte, repris de la précédente.

## Fiche par fiche

| Fiche | Rédaction | Statut |
|---|---|---|
| `taux_plein_a_soixante_cinq_ans` | R. 351-7, 1er janvier 2026 | citée par la version `loi_du_28_fevrier_2025` |
| | règlement du RCI, article 12, 1er janvier 2027 | à rattacher |
| | R. 351-6 (2026), L. 13 du code des pensions (2025), R. 382-57 (2025), R. 653-2, L. 381-1 et L. 351-12 (2023), loi n° 86-33, article 41 (2023) | sans effet |
| `micro_social_abattement` | D. 131-6-1 (2026), D. 621-1 et D. 621-2 (2024), D. 133-4 (2023), D. 612-4 et D. 612-5 (2021), arrêté du 9 février 2012, article 3 | sans effet |
| `reversion` | R. 353-13, 1er janvier 2026 | citée par la version `minimum_2026` |
| | R. 815-25, 13 janvier 2007 | à rattacher |
| | R. 815-32 (2025), D. 355-1 (2020), R. 815-41 (2014), R. 815-40 (2007) | sans effet |
| `cnavpl_allocation_avant_2004` | R. 643-7, 1er septembre 2023 | citée par la version `pension_en_points` |
| | R. 643-6, 5 mars 2023 | à rattacher |
| | L. 643-2 (2018), R. 643-9 (2004) | sans effet |
| `minimum_vieillesse` | L. 815-4, 1er janvier 2006 | à rattacher |
| | L. 815-2 et L. 815-8, 1er janvier 2026 | sans effet |
| `assiette_rco_independants` | décret n° 2012-443, article 4 (2022), D. 635-2 et D. 635-4 (2020) | sans effet |
| `conjoint_collaborateur_independants` | D. 742-26 et D. 742-28 (2020) | sans effet |
| `cumul_emploi_retraite_et_retraite_progressive` | D. 161-2-8 et D. 161-2-9 (2023), texte inchangé | sans effet |
| `minimum_contributif` | R. 351-25 (2026), décret n° 73-937, article 7 (2001) | sans effet |
| `stages_formation_professionnelle` | code du travail, L. 6342-3, 1er août 2020 | citée par la version `cinquante_jours_depuis_2015` |
| | L. 351-3, 1er novembre 2026 | sans effet |
| `conge_supplementaire_naissance` | L. 351-3, 1er novembre 2026 | citée par la version `cinquante_huit_jours` |
| `sportifs_haut_niveau` | L. 351-3, 1er novembre 2026 | sans effet |
| `trimestres_avant_1972` | D. 757-2 (2004), ordonnance n° 45-2250, article 32 (1954) | sans effet |
| `assiette_minimale_independants` | L. 613-9 (2022) | sans effet |
| `avpf` | L. 381-1, 1er septembre 2023 | citée par la version `l_un_ou_l_autre_parent` |
| `cnavpl_valeur_service` | R. 643-11 (2004) | sans effet |
| `compagnie_generale_eaux_transfert_1991` | R. 711-1 (2023) | sans effet |
| `cultes_fractions_de_pension` | R. 351-6 (2026) | sans effet |
| `exoneration_independants_outre_mer` | D. 756-7 (2017) | sans effet |
| `majoration_forfaitaire_reversion` | D. 173-21-1 (2026) | sans effet |
| `retraite_progressive` | R. 351-39 (2026) | sans effet |
| `revenu_annuel_moyen_independants`, `salaire_annuel_moyen` | R. 173-3-2, 1er août 2026 | à rattacher |
| `un_statut_par_annee` | R. 711-24 (2017) | sans effet |

Près de la moitié des « sans effet » tiennent à une seule cause : le numéro
d'article que la fiche cite pour une règle ancienne porte aujourd'hui autre
chose. D. 612-4 fixait le taux de la maladie en 2017 et règle depuis la
comptabilité de l'Acoss ; R. 643-9 donnait l'âge des anciens prisonniers de
guerre et règle depuis la procédure d'inaptitude. La liste suit le numéro, non
la règle : ces rédactions reviendront à chaque renumérotation.

## Ce qui change une règle

Rien, dans ce lot, ne change ce que le modèle calcule. Les rédactions qui
changent le droit touchent des règles que le modèle porte déjà, ou qu'il
déclare ne pas servir.

- **R. 173-3-2, 1er août 2026** (décret n° 2026-699, pensions prenant effet à
  compter du 1er septembre 2026) : vingt-quatre ou vingt-trois meilleures
  années pour les parents. Le moteur l'applique déjà, artisans et commerçants
  compris (`nombreDAnneesRetenues`), et la règle a sa fiche,
  `sam_parents_24_23`. Cette fiche-là, hors du lot, ne cite pas la rédaction
  par son identifiant (LEGIARTI000054589934) : à y rattacher.
- **R. 351-7 et R. 353-13, 1er janvier 2026** (décret n° 2025-1409) : le
  premier nomme le 6° de L. 351-8 pour la majoration de durée, le second écarte
  les nouveaux droits du cumul emploi-retraite de la dernière révision de la
  majoration de réversion. Le modèle ne sert ni le taux plein à soixante-cinq
  ans de l'aidant et du parent d'un enfant handicapé, ni la révision de la
  majoration : deux approximations déjà déclarées.
- **R. 351-6, 1er janvier 2026** : la ligne des assurés nés en 1947 sort de
  l'article, et R. 351-39 la leur garde, puisqu'ils ont plus de
  soixante-quinze ans. Rien ne change pour personne.

Quatre points, que la lecture a trouvés sans pouvoir les trancher, vont au
propriétaire.

1. **La date d'effet de la pension de base des libéraux.** R. 643-6
   (LEGIARTI000047265890, en vigueur) la fixe « au premier jour du trimestre
   civil qui suit la demande », et au mois pour la seule Cipav depuis le 5 mars
   2023. La fiche `cnavpl_allocation_avant_2004` ne déclare l'écart que pour
   l'allocation d'avant 2004, où le modèle date l'effet au mois. Aucune fiche
   ne le dit pour la pension en points, depuis 2004 : à vérifier dans le
   moteur, puis à écrire. L'enjeu est d'au plus deux mois de pension.
2. **Les biens du survivant dans les ressources de la réversion.** R. 815-25
   (LEGIARTI000006753705, depuis le 13 janvier 2007), auquel R. 353-1 renvoie,
   compte les biens pour 3 % de leur valeur vénale. La fiche `reversion` ne le
   dit pas, et la saisie prend les ressources telles qu'on les déclare. Ce
   n'est pas un calcul à changer, mais ce que la saisie devrait dire.
3. **L'abattement du RCI au 1er janvier 2027.** L'article 12 du règlement
   (LEGIARTI000054908824) plafonne le coefficient d'abattement de qui est en
   retraite progressive, « au taux prévu à la deuxième ligne du tableau de
   l'annexe 2 », et compte l'âge du taux plein « au sens du 1° ou, du 1° bis ou
   du 6° de l'article L. 351-8 ». C'est la règle de la fiche `abattement_rci` :
   le lot « les autres régimes » l'a lue et la porte dans sa propre liste
   (`2026-11-12-etape-6-autres-regimes.md`). Elle est ici à rattacher, pour le
   seul renvoi au 1° bis et au 6°.
4. **La rente d'accident du travail dans les périodes assimilées.** L. 351-3,
   1°, depuis le 1er novembre 2026 (loi n° 2025-199, article 90), la compte
   « pour une incapacité permanente professionnelle », pour les victimes dont
   l'état est consolidé à compter de cette date. Aucune fiche ne lit le 1° pour
   la rente ; les trois fiches qui citent l'article lisent ses 7°, 8° et 9° et
   le congé supplémentaire de naissance, que la rédaction ne touche pas.

## Ce que la passe a montré de l'outil

Le statut d'une rédaction est commun à toutes les fiches, et le plus établi
l'emporte (`noyau/textes.py`, `statuts`). Une rédaction qu'une fiche déclare
sans effet sort donc de la liste `--non-lues` de toutes les autres, même si
elle y change le droit. Deux rédactions du lot étaient partagées avec un autre
lot : L. 13 du code des pensions (LEGIARTI000053280906), que le lot de la
fonction publique a lue dans ses quatre fiches avant que celui-ci la déclare
sans effet sur `taux_plein_a_soixante_cinq_ans` ; l'article 12 du règlement du
RCI, mis à rattacher, ce qui ne le retire de la liste de personne. Trois
rédactions sont sans effet sur une fiche du lot et à rattacher dans une autre
fiche, qui les nomme déjà : L. 613-9 (`micro_social_abattement`), R. 351-39
(`trimestres_avant_1972`), R. 711-1 (`un_statut_par_annee`). Leur statut
commun est désormais « sans effet », et la fiche qui doit les rattacher le
garde écrit dans ses `textes_a_rattacher` ou ses lectures.

## Ce qui reste

- `sources.lu_le` des vingt-quatre fiches est au 12 novembre 2026. Leur
  `prochaine_relecture` n'a pas bougé : chacune tient à une échéance que la
  fiche nomme, que cette passe ne lève pas.
- R. 653-2, pour les avocats, renvoie encore aux III et IV de l'article 20 de
  la loi n° 2010-1330, abrogés pour les pensions prenant effet à compter du
  1er janvier 2026 : le décret n° 2025-1409 ne l'a pas retouché. À relire à la
  prochaine rédaction.
- R. 351-37 a une rédaction du 1er novembre 2026, vue en passant, qu'aucune
  fiche du lot ne cite.
- Les rédactions passées des mêmes articles ne sont pas lues : 149 pour
  `taux_plein_a_soixante_cinq_ans`, 75 pour `micro_social_abattement`, 75 pour
  `reversion`. Ce n'est pas l'objet de l'étape.
- Le bloc « Reprise » de la note de l'étape reste à la session
  d'orchestration, qui suit les quatre lots.
