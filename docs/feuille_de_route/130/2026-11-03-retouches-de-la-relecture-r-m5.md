# Les retouches de la relecture R-M5 : la lecture de 1998 déclarée, la borne de 11 % estimée

File M5-bis, le 3 novembre 2026. La relecture R-M5
(`2026-11-03-relecture-base-des-cultes-au-smic-du-mois.md`) juge conforme la base
des cultes au SMIC de chaque mois et relève six écarts faibles, de preuve et
d'écriture. Chacun est relu ici au texte, dans les index LEGI (à jour au
2 novembre 2026) et JORF (à jour au 3 novembre 2026) de la DILA, récupérés, et
dans les PDF téléchargés ce jour. Aucun calcul ne change, aucune valeur
attendue ; `construire_donnees.py` ne change rien au paquet.

## Les six écarts

1. **La rédaction de 1998 ne dit pas « en vigueur ».** R. 721-29 et R. 721-30,
   du 21 juin 1998 au 26 février 2004 (LEGIARTI000006752924, 6752925, 6752064,
   6752065) : « est égale, par mois, à 169 fois le montant du salaire minimum de
   croissance ». La fiche `cultes_salaire_annuel_moyen` déclare désormais, dans
   les `conditions` de la version `cent_soixante_neuf_heures`, que suivre le
   SMIC de chaque mois sous cette rédaction est une lecture du modèle, avec le
   texte mot pour mot, ce qui la justifie (la base est « par mois » ; les textes
   du temps qui veulent un SMIC fixe nomment sa date : « celui en vigueur au
   1er janvier de l'année civile considérée », D. 742-3, décret n° 2002-784,
   JORFARTI000001824475 ; « par mois, à 169 fois le salaire horaire minimum de
   croissance en vigueur au 1er juillet de l'année civile précédente »,
   R. 742-14, décret n° 2002-1253, JORFARTI000002446426), et ce qui manque :
   aucun document de la caisse d'avant 2008. L'approximation ne prête plus
   « en vigueur » qu'à la rédaction de 2004 et à R. 382-89 et R. 382-90, et la
   partie 4 des limites le dit.
2. **L'arrêté du 29 novembre 2011.** La date est à l'article 1er, « est majoré
   de 2,1 % pour prendre effet au 1er décembre 2011 » (JORFARTI000024874230) ;
   le montant à l'article 2, « s'établira, à compter de cette date, à 9,19 € de
   l'heure » (JORFARTI000024874233). L'en-tête de
   `macro/smic_horaire_releves.csv`, la fiche et le commentaire de
   `tests/test_cultes_smic_du_mois.py` citent les deux.
3. **Pas de décret au 1er janvier 2025.** Les décrets « portant relèvement du
   salaire minimum de croissance » de l'index JORF, de 2017 à 2025 : n° 2017-1719,
   2018-1173, 2019-1387, 2020-1598, 2021-1741, 2022-1608, 2023-1216, puis
   n° 2024-951 (au 1er novembre 2024) et n° 2025-1228 (au 1er janvier 2026),
   rien entre les deux ; une recherche de « salaire minimum » dans les titres de
   2025 ne donne que le décret n° 2025-1228, un arrêté de nomination du groupe
   d'experts et un arrêté sur les journalistes. Janvier 2025 garde les 11,88 €
   du 1er novembre 2024. La fiche écrit « les décrets du 1er janvier de 2018 à
   2024 et de 2026 », et dit 2025.
4. **La circulaire de la CAVIMAC n° 2025/01.** Le PDF de cavimac.fr, trois
   pages, a une couche de texte (`pdftotext`), et non une image. Page 1, le
   résumé : « Cotisations et contributions sociales applicables à compter du
   1er novembre 2024 (échéance au 15 décembre 2024) » ; le corps : « les
   assiettes forfaitaires [...] sont modifiées à compter de l'échéance du
   15 décembre 2024 ». Page 2, le tableau : « Cotisations sociales mensuelles
   applicables à compter du 1er janvier 2025 », 1 802 € pour la vieillesse comme
   pour la « RCO » — le barème de 2025, que le SMIC ne change pas au
   1er janvier 2025 (point 3). La circulaire n° 2024/01, relue, date l'échéance
   du 15 d'un mois du mois précédent : « applicables à compter du 10/15 février
   2024 -au titre du mois de janvier 2024- ». Le relèvement de l'assiette est
   bien de novembre 2024. La fiche relève l'en-tête et corrige « image ».
5. **La borne de 11 %.** L'article 32, I, de la loi n° 2000-37
   (JORFARTI000001248766) fixe la garantie au « produit du salaire minimum de
   croissance en vigueur à la date de la réduction par le nombre d'heures
   correspondant à la durée collective qui leur était applicable, dans la limite
   de cent soixante-neuf heures », puis « revalorisé au 1er juillet en fonction
   de l'évolution de l'indice des prix à la consommation [...] et de la moitié de
   l'augmentation du pouvoir d'achat du salaire mensuel de base ouvrier ». Il ne
   la borne pas au SMIC du mois de cent soixante-neuf heures. Les 11 % sont un
   calcul, 2 028 / 1 820 − 1 = 11,4 %, sous l'hypothèse que la garantie la plus
   élevée ne passe jamais ce SMIC : une estimation, que la fiche (version
   `garantie_mensuelle_de_remuneration`, son approximation et l'`effet`) et la
   docstring de `test_la_garantie_de_remuneration_reste_sous_cent_soixante_neuf_heures`
   écrivent comme telle. L'`effet` rappelle l'autre lecture, la garantie ajoutée
   entière, près de moitié moins. Aucun montant de la garantie n'est dans le
   dépôt pour vérifier l'hypothèse.
6. **Les forfaits agricoles.** Les décrets n° 90-498 (JORFARTI000001735045) et
   n° 94-690 (JORFARTI000002131575) disent bien « le montant du salaire minimum
   de croissance en vigueur au 1er janvier de l'année considérée ». Le décret
   n° 2001-584, IV (JORFARTI000001260750), dit autrement : « le salaire minimum
   de croissance à prendre en considération est celui en vigueur au 1er janvier
   de l'année au titre de laquelle les cotisations sont dues ». Même sens ; la
   conclusion de M5 tient. La citation n'est que dans la note de M5, un récit :
   elle est corrigée ici, avec un renvoi daté au bout de cette note.

## Le guide de 2008, en appui

Actes 6, « La rémunération des ministres du culte » (© 1995-2008), téléchargé
et lu : « sur la base forfaitaire du SMIC arrondie à l'euro près : 1 309 € à
compter du 1er mai 2008 », la même base pour l'« Assurance vieillesse CAVIMAC »
et la « Retraite complémentaire » ; « SMIC horaire au 1er mai 2008 : 8,63
euros ». 8,63 × 151,67 = 1 308,91 : la base suit le relèvement de mai. La fiche
le cite dans ses `lectures`, de seconde main et d'après 2004.

## L'acte de l'Arrco qui fixe l'assiette des cultes

Cherché parmi les accords que le dépôt certifie (`sources.yaml`,
`agirc_arrco_accords_contributions_equilibre`), téléchargés et lus : il n'y
est pas. L'accord du 17 novembre 2017 ne nomme pas les cultes ; son article 30
assied les cotisations sur les éléments de L. 242-1 et, « Par dérogation, dans
certaines situations visées au présent Accord ou dans son annexe A (inactivité
totale ou partielle, salariés travaillant à l'étranger, apprentis…) », sur
« une assiette forfaitaire, fictive ou particulière ». Le recueil des accords
de 1993 à 2015 ne les nomme pas non plus. La circulaire 2019-1-DRJ, fiche 3,
que cite `regimes/arrco_cultes.yaml`, n'a pas sa copie dans le dépôt. La fiche
`cultes_retraite_complementaire` le dit dans `sources.a_relire`. L'assiette
reste lue dans les circulaires de la CAVIMAC et le guide de 2008.

## Les tests

`python -m pytest -m rapide` : 4 316 verts, 6 sautés.
`tests/test_cultes.py`, `test_cultes_au_droit.py`, `test_cultes_smic_du_mois.py`
et `test_carte.py` : 36 verts. Seuls des commentaires et une docstring
changent dans les tests.
