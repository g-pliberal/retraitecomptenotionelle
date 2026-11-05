# Étape 4, thème « Carrière : cotisations-salaires » : les exposés et leurs références

**Le 3 novembre 2026, ce qui est fait.**

- *La lecture* : les 65 exposés du thème, relus par l'API à la version que le registre
  date — 43 « Cotisations par activité », 6 « Insertion professionnelle », 4
  « Affiliation au régime général et relevé de carrière », 4 « Annulation de
  cotisations », 3 « Reversement de cotisations », 2 « Volontariat et service civique »,
  et « Taux des cotisations », « Travail dissimulé », « Validation des périodes de
  cotisations » —, chacun confronté aux fiches et aux limites qui portent ses règles :
  la validation des trimestres, avant et depuis 1972 ; l'apprentissage ; l'AVPF et
  l'assurance vieillesse des aidants ; le service civique et le volontariat associatif ;
  les stages de la formation professionnelle ; le rétablissement des agents partis sans
  droit ; le cumul d'activités ; les assiettes forfaitaires ; les cultes, que lit la file
  E ; les indépendants, que lit la file D.
- *Le tableau, confronté aux séries* : le salaire qui valide un trimestre au salarié,
  période par période — 1 800 anciens francs de 1946 à 1948, le trimestre de l'allocation
  aux vieux travailleurs salariés jusqu'en 1971, 200 heures de Smic, puis 150 depuis 2014
  —, par `test_le_salaire_qui_valide_un_trimestre_est_celui_de_la_caisse`
  (`tests/test_cnav_exposes.py`). Tout concorde.
- *Aucun écart corrigé, quatre déclarés*, un par commit :
  - l'activité accessoire de l'agent d'un régime spécial — fonctionnaire, militaire,
    agent de la SNCF, de la RATP, des IEG… — qui, jusqu'au 18 juillet 2015, n'ouvrait
    aucun droit au régime général : D. 171-2 et D. 171-4, rédactions de 1985 lues dans
    l'index LEGI, « n'ont droit qu'aux prestations prévues par le régime auquel ils sont
    affiliés au titre de leur activité principale ». Le modèle ouvre le régime général à
    toute activité cumulée. La correction attend que la ligne d'une carrière sache
    qu'elle est cumulée, ce que l'étape qui coordonne les affiliations ne lit pas
    aujourd'hui : à la session du modèle, les deux moteurs ensemble (fiche
    `un_statut_par_annee`, approximation neuve) ;
  - l'AVPF du père : la caisse ne l'affilie que depuis le 1er juillet 1979, et jusqu'à
    1984 seulement s'il a la charge d'un handicapé ; le décret n° 73-88 ne nomme les pères
    qu'en août 1985, L. 381-1 l'un ou l'autre parent à sa codification. Le modèle sert
    l'AVPF à toute période d'éducation déclarée depuis 1972. Les lois de 1979 et
    n° 85-17, que l'index n'a qu'en notice, sont à lire avant la correction (fiche `avpf`,
    à relire) ;
  - la validation, par un régime spécial, des services de non-titulaire de l'agent
    titularisé tardivement, qui annule les cotisations du régime général (D. 173-13,
    D. 173-19) ;
  - l'affiliation au régime général, depuis 1992, de l'élu local qui a cessé son activité
    pour son mandat, quelles que soient ses indemnités, et l'option sous le seuil depuis
    septembre 2023 (ces deux-là dans `docs/limites/3-systeme-actuel.md`).
- *Les assiettes forfaitaires* : la limite qui les déclare porte désormais une vingtaine
  d'activités que les exposés décrivent sans barème — le président-directeur général et
  le gérant de société avant 1963, l'écrivain, le déménageur, le chauffeur de taxi, le
  cadet de golf, l'énoiseur, les recenseurs et les enquêteurs, la presse, les musées, le
  sport, les associations de jeunesse, la junior-entreprise, le travailleur handicapé,
  l'artiste-auteur, le détenu, le travailleur payé en nature, le stagiaire, le travail
  dissimulé, l'abattement du VRP et du journaliste —, et date le taux réduit du
  journaliste de 1964, celui des médecins à temps partiel de 1961.
- *Les sorts*, sous la convention de la note du premier thème : 65 exposés (55 `limite`,
  10 `hors_modele` — le relevé de carrière, la dispense des impatriés, les cotisations
  versées à tort, les transferts avec les institutions européennes et les organisations
  internationales, les régimes spéciaux supprimés, l'accueillant familial, les congés
  payés, le coopérant), 9 fenêtres (8 définitions du lexique, `hors_modele` ; la liste des
  régimes spéciaux qui valident le chômage, `limite`), 237 références (210 `limite`,
  27 `hors_modele`, et 8 déjà rangées dont les renvois s'étendent), 15 avis. La liste des
  pays de l'Espace économique européen reste `a_lire`, avec les règlements européens ; les
  deux exposés « Mayotte - Législation > Carrière > Cotisations-salaires », avec le thème
  Mayotte. Du premier thème restent marqués, à lire avec le leur, ce que son bloc
  « Reprise », passé ici, comptait : 78 listes d'accords et 2 des règlements européens
  (accords internationaux), 57 listes de périodes de guerre (Carrière, périodes
  assimilées), et les 92 références qu'elles seules lient.

**Ce que la lecture a trouvé, sans écart.** Le service civique et le volontariat
associatif, l'apprentissage depuis 2014, le rétablissement des agents partis sans droit et
l'assiette de l'AVPF sont ce que leurs fiches disent servir, ou déclarent ne pas servir. La
surcotisation du salarié à temps partiel, sur le salaire d'un temps plein (L. 241-3-1),
est déjà dehors (`docs/limites/ecarts-au-droit-positif.md`). Les exposés de la junior
entreprise et de l'artiste du spectacle occasionnel annoncent des mises à jour qui attendent
leurs instructions (loi n° 2022-1616, article 14 ; arrêté du 26 février 2020) : la veille
les dira.

**La forme des liens de la base, changée le 3 novembre 2026 à 5 h.** Les exposés et les
listes, réimportés ce matin-là, lient désormais par les chemins du site SharePoint de la
caisse : `/sites/N_GDLC_Campus/SitePages/<exposé>`, `/sites/N_GDLC_Campus_Bar/SitePages/`
pour un barème ou une liste, `/sites/N_GDLC_Campus_Com/SitePages/` pour une fenêtre,
`/sites/N_GDLC_Campus_Ref/SitePages/` et `/sites/N_GDLC_Campus_Ref/RefReg/textes/` pour une
référence. `cnav_legislation.liens` ne lit que les routes du site (`#/expose?…`) et `/Pdf/` :
sur la base du jour, il ne trouve aucun lien aux 65 exposés du thème, et une relecture du
registre perdrait les thèmes des listes, des fenêtres et des références, et les références
neuves. Cette session a lu les liens par un relevé à elle, où chaque chemin désigne un objet
du registre, sans toucher au récupérateur. Le porter, le test d'abord
(`test_les_liens_d_un_contenu_disent_ce_qu_ils_visent`), revient à la file du registre ;
les dates de modification, elles, n'ont pas bougé, et la veille ne voit rien.

**Pour la file D**, sans y toucher : les deux exposés « Travailleurs indépendants » et
« Affiliation des travailleurs indépendants », renvoyés à ses fiches, sont à confronter
par elle — l'assiette unique des cotisations dues depuis 2025 (abattement de 26 %, borné),
la cotisation minimale qui valide trois trimestres à qui est affilié 90 jours, l'Acre du
micro-entrepreneur ramenée de moitié au quart pour les créations du 1er juillet 2026. Et,
dans l'exposé « Validation des périodes de cotisations », le trimestre de l'indépendant
compté en cotisations, non en revenu : les cotisations versées divisées par la
cotisation minimale — 150 heures de Smic au taux plafonné du 1er janvier, « arrondi
comptable à l'euro » —, arrondies à l'entier inférieur, que la fiche
`cotisation_vieillesse_independants` ne dit pas. Aucune règle n'a été changée.

**À la session du modèle**, les deux moteurs ensemble : l'activité accessoire d'avant le
19 juillet 2015 et l'AVPF du père, ci-dessus, avec ce que la note du premier thème lui
laisse. Aucun fichier d'une autre file n'a été changé ; les fiches des cultes, de la file
E, ne sont que nommées par le registre.
