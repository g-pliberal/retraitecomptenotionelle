# Relecture de E8 (la majoration pour enfants des sections, et les écarts de R-E8 repris)

File R-E9, le 6 novembre 2026 (action 130, vague 11, sur Opus) : relecture indépendante,
contre les sources, du commit 40d3fbc de la session E8 (`cipav_seconde_tranche`,
`sections_liberales_majoration_enfants`, `tests/test_sections_liberales.py`,
`tests/test_carte.py` ; note `2026-11-06-fiches-communes-des-sections-lues-au-droit.md`).
Ni règle, ni donnée, ni test n'est modifié.

**Méthode.** Les index de la DILA récupérés puis mis à jour (`dila_index.py --recuperer`,
`--mettre-a-jour`) : JORF au 6 novembre 2026 (incrément 20261106-002608), LEGI au 5
novembre (20261105-214938). Chaque texte rouvert par `dila_cherche.py --texte` ; les textes
modificatifs relevés par titre, sans borne (`--limite 500`, jamais atteinte : 138 documents
au titre « agents généraux d'assurance », tous listés) ; les articles que E8 dit repris mot
pour mot, comparés par un script, guillemets ôtés et espaces ramenées. Les montants refaits
en décimal exact. Les essais par `servi_et_refait` (`tests/outils_pont.py`), le portage
servant et le moteur Python refaisant, sous les deux jeux de présomptions : la mère de trois
enfants de E8 (née un 10 mars, `salaire` 2, `debut` 22, `profil` plat, `euros` 2026), aux
douze dates d'effet qui bornent les versions.

## Le verdict

**E8 conforme pour l'essentiel ; l'erreur de la CAVAMAC en 2011 est confirmée.** Toutes les
citations vérifiées sont exactes ; les dates de publication et d'effet, justes ; chaque
montant tombe au centime ; les deux moteurs rendent, sous les deux jeux, ce que la note
écrit ; la carte compte bien 74 fiches et 425 manques (75 et 432 au commit d'avant). Aucun
écart fort ni moyen. Quatre écarts **faibles** (points 7, 10, 13 et 15), sans effet sur un
montant que le modèle sert.

## Les cinq écarts de R-E8, repris par E8

1. **Les six classes de 1979 à 2012.** LEGI porte sept rédactions de l'article 2 du décret
   n° 79-262 (`--num 2 --titre 79-262`) ; les trois d'avant 2013 sont celles que E8 cite :
   LEGIARTI000006767473 (1979-01-01 → 1985-06-21), …006767474 (1985-06-21 → 2012-12-30),
   …026885130 (2012-12-30 → 2013-01-01). Les trois portent « Le régime d'assurance
   vieillesse complémentaire institué par l'article 1er comporte six classes de cotisation :
   Classe 1 portant attribution de quatre points de retraite ; [...] Classe 10 portant
   attribution de quarante points de retraite. » ; celle de 1979, « Le montant des
   cotisations est fixé par décret sur proposition du conseil d'administration de la
   section professionnelle mentionnée à l'article 1er. » ; celle de 1985, « La cotisation
   ainsi fixée peut faire l'objet d'un appel réduit dans les conditions fixées par les
   statuts prévus à l'article 5. » (absente de celle de 1979) ; celle de 2012, « son revenu
   d'activité tel que défini à l'article L. 131-6 du code de la sécurité sociale ».
   **Conforme.**
2. **Le décret n° 2026-239.** Article 2 (JORFARTI000053748625) : « Le présent décret entre
   en vigueur le 1 er juillet 2026. » Annexe (JORFARTI000053748628), 41 843 caractères :
   « (51) La caisse (hors CIPAV) choisit entre la possibilité prévue à l'article R. 642-2 du
   code de la sécurité sociale et des dispositions ad hoc. (52) La caisse (hors CIPAV)
   choisit [...] » ; ni « classe », ni « points », ni « date d'effet », ni « enfant ». Les
   textes du JORF qui citent « 2026-239 » : le décret lui-même, deux arrêtés du 10 juillet
   2026 (JORFARTI000054435943, …054435749) et l'arrêté du 21 septembre 2026
   (JORFARTI000054888263) ; aucun ne le modifie. **Conforme.**
3. **L'enjeu des taux de 2026.** Le plafond : arrêté du 22 décembre 2025, article 1er
   (JORFARTI000053143455), « valeur mensuelle : 4 005 euros », P = 4 005 × 12 = 48 060 €.
   Refait en décimal exact, cotisation du modèle 0,11 × min(R, P) + 0,21 × (min(R, 4 P) −
   P) moins celle de l'hypothèse 0,09 × min(R, P) + 0,22 × (min(R, 4 P) − P), divisée par
   47,40 € ou multipliée par 0,061 :
   - au plafond, 5 286,60 − 4 325,40 = 961,20 € ; 961,20 / 47,40 = 20,2785 points ;
     961,20 × 0,061 = 58,6332, **+58,63 €** ;
   - à trois plafonds, 144 180 € : 25 471,80 − 25 471,80 = 0 ;
   - à quatre plafonds et au-delà (192 240 €, 250 000 €) : 35 564,40 − 36 045,00 =
     −480,60 € ; −10,1392 points ; −29,3166, **−29,32 €** ;
   - à 40 000 € : 800,00 €, 16,8776 points, 48,80 € ; à 150 000 € : 26 694,00 −
     26 752,20 = −58,20 €, −1,2278 point, −3,5502, −3,55 € ;
   - points arrondis à la décimale (0,061 × 47,40 = 2,8914 €) : 92,8 − 75,9 = 16,9,
     48,8647, 48,86 € ; 563,2 − 564,4 = −1,2, −3,4697, −3,47 € ; 111,5 − 91,3 = 20,2,
     58,4063, 58,41 € ; 750,3 − 760,4 = −10,1, −29,2031, −29,20 € ; chaque côté bouge
     d'au plus 0,05 point, l'écart d'au plus 0,1 × 2,8914 = 0,29 € ;
   - les arrondis de E7 : 16,88 × 2,8914 = 48,8068 ; 1,23 × 2,8914 = 3,5564.
   **Conforme**, chaque chiffre de la note et de la fiche.
4. **L'article 2 de l'arrêté du 7 janvier 2025** (JORFARTI000050962836) : « Le présent arrêté
   sera publié au Journal officiel de la République française. » **Conforme.**
5. **E6-bis sur Sonnet** : le commit 8c955fe porte « Co-Authored-By: Claude Sonnet 5.5 ».
   **Conforme.**

## La CAVAMAC : l'erreur de 2011

6. **Les textes, à la lettre.** Arrêté du 23 juin 2011, publié le 29 juin : article 2
   (JORFARTI000024270156), « Les dispositions du présent arrêté entrent en vigueur le 1er
   juillet 2011. » ; article 3 (JORFARTI000024270158), « L'arrêté du 22 décembre 1967
   modifié portant approbation des statuts du régime d'assurance vieillesse complémentaire
   des agents généraux d'assurances est abrogé. » Annexe (JORFARTI000024270173, 29 983
   caractères), article 17 : « les majorations prévues aux articles 18 et 19 des présents
   statuts sont calculées sur la base du compte de droits majoré ou minoré de l'adhérent » ;
   article 18 : « Le nombre des points de retraite acquis dans le présent régime est majoré
   de 10 % au profit de l'adhérent ayant eu au moins trois enfants [...] » ; ni « 2011 », ni
   « 2012 », ni « transitoire », ni « prenant effet » dans l'annexe. Le modèle :
   `cavamac_complementaire.yaml`, période 2004-2011, `avantages_non_contributifs:
   [reversion]` ; période 2012-2018, `[reversion, majoration_enfants]`, et « LES STATUTS DE
   2011, servis à partir de 2012, première année pleine ». **Conforme.**
7. **Les textes modificatifs, tous.** Au titre « agents généraux d'assurance », sans borne,
   138 documents. Depuis 2011 : 28 septembre 2012, décret n° 2013-663, 28 mars 2014, 4 mai
   2016, 20 novembre 2017, 20 octobre 2020, 19 octobre 2021, 4 août 2023, 8 juillet 2025,
   10 juillet 2026 ; dans leurs articles, « enfant » ne paraît qu'au capital décès (2025) et
   au règlement de 2026, et l'« article 18 » de 2016 est celui des statuts généraux (le
   « 15° » est à la partie I, avant « II.-Les statuts du régime d'assurance vieillesse
   complémentaire de la section professionnelle des agents généraux d'assurance sont ainsi
   modifiés »). E8 ne nomme ni le décret de 2013, ni les arrêtés
   de 2020 et 2021 : sans effet. **Avant 2011, l'inventaire de E8 est incomplet — écart
   faible.** La note et la fiche (approximation `[aucune_avant_2000, cipav_depuis_2000]`)
   nomment l'arrêté de 1967 « et ses modifications de 1972, 1975 et 1983 », puis « le décret
   n° 97-1056, les arrêtés du 17 décembre 2007 et du 26 janvier 2011, ces deux derniers pour
   la base et les statuts généraux » ; manquent trois arrêtés qui modifient les statuts du
   régime complémentaire lui-même : du 17 décembre 2001 (JORFARTI000002036105, « sont
   approuvées les modifications apportées aux statuts du régime d'assurance vieillesse
   complémentaire (art. 4) », publié au seul Bulletin officiel n° 2002-04,
   JORFARTI000001070359) ; du 26 décembre 2003 (annexe JORFARTI000001280567, 1 543
   caractères, « Article 3 L'article 3 est complété par deux alinéas [...] ») ; l'autre
   arrêté du 17 décembre 2007, publié le 18 janvier 2008 (annexe JORFARTI000017890649,
   3 032 caractères : articles 1er, 3 et 5). Aucun ne nomme l'enfant ; les décisions du
   comité de gestion de 1969 à 1992 n'ont que leur titre (« plancher », « plafond »,
   « coefficient de référence »). La conclusion tient ; la liste se complète à la reprise.
8. **La date d'effet, et la lecture contraire.** Les statuts de 2011, article 20 : « La date
   d'effet de la pension de retraite complémentaire est fixée, au plus tôt, au premier jour
   du trimestre civil qui suit la demande écrite de l'adhérent [...] » (point déjà déclaré,
   non tranché, à `cavamac_minoration_age_seul`). Aux dates d'effet du modèle du 1er août au
   1er décembre 2011, aucune lecture n'échappe aux statuts de 2011 : que la pension parte au
   mois du modèle ou au trimestre civil suivant (1er octobre 2011, 1er janvier 2012), ils
   sont en vigueur, et ceux de 1967 abrogés ; ils majorent. Au 1er juillet 2011, la date du
   cas chiffré, la demande précède forcément le 1er juillet (article 20) ; une lecture qui
   liquiderait aux statuts en vigueur à la demande n'a aucun texte lu pour elle, l'article 3
   abroge les statuts de 1967 au jour même, et son issue dépendrait de ceux-ci, non lus.
   **L'erreur est prouvée : la lecture contraire est intenable**, au 1er juillet comme
   après. Pour la correction, un second cas, hors de toute borne : à 65 ans et 6 mois, au
   1er octobre 2011, le modèle sert 13 442,3420 € sans majoration ; le texte, 0,10 ×
   13 442,3420 = 1 344,2342, **1 344,23 € par an**.
9. **Le chiffre.** Essai du 6 novembre 2026, née le 10 mars 1946 (l'âge se compte du 1er
   avril, `calendrier.origine_des_ages` : 65 ans et 3 mois au 1er juillet 2011), dans les
   deux moteurs, sous les deux jeux : 13 323,3108 € de CAVAMAC, majoration 0 ; 0,10 ×
   13 323,3108 = 1 332,3311, **1 332,33 € : juste**. Aux 1er juin, 1er juillet, 1er août,
   1er octobre et 1er décembre 2011 (65 ans et 2, 3, 4, 6 et 8 mois) : 13 283,63,
   13 323,31, 13 362,99, 13 442,34, 13 521,70 €, majoration 0 ; au 1er janvier 2012,
   1 382,6362 = 0,10 × 13 826,3624, 1 382,64 €. **Conforme.**
10. **Les 5 % par enfant handicapé — écart faible.** L'article 19 des statuts de 2011 est
    cité exactement, et 0,05 × 13 323,31 = 666,17 € est juste. Mais l'article 8 du
    règlement de 2026 (JORFARTI000054436046) ne le reprend pas mot pour mot, comme la note
    le dit (« l'article 8 le 19 ») : il écrit « en application » pour « en vertu », et
    ajoute, après la prestation de compensation, « soit à l'allocation aux adultes
    handicapés prévue à l'article L. 821-1 du code de la sécurité sociale ». Depuis le
    18 juillet 2026, le manque couvre aussi l'enfant qui ouvre droit à l'AAH ; la fiche ne
    le dit pas. L'article 7 reprend l'article 18 mot pour mot (comparé par script) :
    conforme.
11. **Les statuts de 1967, au fac-similé.** Titres seuls dans l'index (JORFTEXT000000660274,
    …000283882, …000831972, …000494188) ; celui de 1975 porte « (MODIFICATION DES ART. 4,
    5, 8 & 8 BIS, 10, 14, 15, 17 & 18 DES STATUTS DE LA CAISSE). » Manque bien déclaré.
    **Conforme.**

## La CAVEC

12. **L'arrêté du 4 juillet 2025**, publié le 6 juillet : article 2 (JORFARTI000051849614),
    « Le présent arrêté sera publié au Journal officiel de la République française. », en
    vigueur le 7 ; annexe (JORFARTI000051849616), II, 10° : « Il est ajouté un article 20
    ainsi rédigé : « Art. 20. - Bonification de la pension pour enfants. « Le montant de la
    première pension personnelle et de la pension de réversion relatives au régime
    d'assurance vieillesse complémentaire des assurés ayant eu au moins trois enfants est
    majoré de 10 % dans les conditions fixées par les articles L. 643-1-1 et L. 351-12 du
    code de la sécurité sociale. » ; L. 643-1-1 existe (LEGI : quatre rédactions depuis le 28
    décembre 2009 ; en 2025, LEGIARTI000047453363, du 1er septembre 2023). Le règlement de 2026, article 1.3.1 (JORFARTI000054435943), le reprend,
    « cotisants » pour « assurés ». Avant : l'arrêté du 22 février 2008 récrit un à un les
    articles 3.1 à 3.20 du régime complémentaire, et son article 3.12 dit « Le montant de la
    retraite est égal au nombre de points acquis par l'intéressé multiplié par la valeur du
    point fixée annuellement par le conseil d'administration. » ; celui du 20 août 2018
    remplace les statuts entiers (« sont remplacés par les dispositions suivantes ») ; ni
    l'un, ni celui de 2012 n'a de « bonification » : `enfant OR enfants OR bonification`,
    au titre de la CAVEC et sans borne, ne rend que 2008, 2012, 2018, 2025 et 2026, et
    « bonification » n'est qu'aux deux derniers. Essais :
    32 178,71 € sans majoration au 1er juillet 2025 ; 3 246,2072 = 0,10 × 32 462,0722,
    3 246,21 €, au 1er août 2025. **Conforme.** Non dit, sans effet : le second alinéa de
    l'article 20 ouvre la majoration aux enfants adoptés en adoption plénière « sans que les
    conditions d'éducation prévues au deuxième alinéa de l'article L. 342-4 du même code ne
    soient remplies » ; le modèle compte déjà tous les enfants.
13. **La réversion de la CAVEC — écart faible, de rangement.** Le candidat de E8 est au
    texte (« et de la pension de réversion », article 20 puis 1.3.1). Mais le modèle ne sert
    aucune réversion de la CAVEC : `cavec_minoration_age_seul.yaml` le déclare déjà (« Le
    modèle ne sert aucune réversion de la CAVEC [...] motif `non_portee` »). La majoration de
    10 % de la réversion depuis le 7 juillet 2025 n'est pas un candidat à part : elle se
    joint à cet écart déclaré, et la réversion, quand elle sera servie, la portera.

## La Cipav

14. **Les textes.** Décret n° 99-913, article 6 (LEGIARTI000006780306, en vigueur le 1er
    janvier 2000), cité exactement. Décret n° 79-262, article 5-2 (LEGIARTI000054168515) :
    « Conformément à l'article 30 du décret n° 2026-418 du 29 mai 2026, ces dispositions,
    dans leur rédaction issue dudit décret, entrent en vigueur le 1er juillet 2026. I. - Le
    montant de la pension est égal au produit du nombre de points acquis diminué, le cas
    échéant, du coefficient de réduction par la valeur de service du point. Il est majoré de
    10 % au profit du demandeur ayant eu au moins trois enfants. [...] » ; décret n°
    2026-418, article 20 (JORFARTI000054153655, qui écrit l'article 5-2) et article 30
    (JORFARTI000054153813, « Le présent décret entre en vigueur le 1 er juillet 2026. »).
    Essais : 4 033,95 € sans majoration au 1er décembre 1999 ; 418,1477 = 0,10 ×
    4 181,4774, 418,15 €, au 1er janvier 2000 ; 2 102,7421 = 0,10 × 21 027,4208,
    2 102,74 €, au 1er juillet 2026 ; au 1er juin 2026, 2 096,08 €, la version de 2000.
    **Conforme.**
15. **Le point non tranché d'avant 2000, et le test qui le fige — écart faible.** Les deux
    lectures sont bien citées et chiffrées : 0 € ou 0,10 × 4 033,9509 = 403,3951, 403,40 €.
    La seconde a du poids — le décret du 21 octobre 1999 renvoie à des conditions
    « prévues par les statuts de ce régime », et n'en réserve que les droits d'après 2000
    aux anciens géomètres —, mais rien ne dit quand la bonification est née : non tranché,
    à bon droit. L'écart est dans `tests/test_sections_liberales.py` :
    `MAJORATIONS_AUX_DATES_QUI_COMPTENT` s'annonce « La majoration de chaque cas, au texte :
    10 % de la pension, ou rien », et deux de ses sept cas tiennent la valeur du modèle, non
    celle du texte : la CAVAMAC au 1er juillet 2011, 0,0 où le texte dit 0,10 (le
    commentaire du cas le dit), et la Cipav au 1er décembre 1999, 0,0, une seule des deux
    lectures (son commentaire ne le dit pas). La règle du dépôt veut la valeur de la source.
    À la correction de la CAVAMAC, le premier cas passe à 0,10 ; le second se déclare.

## Les tests et la carte

16. **`test_chaque_version_de_la_majoration_pour_enfants_des_sections_est_portee`** : les
    bornes des cinq versions sont celles des textes (2000-01-01, 2011-07-01, 2025-07-07,
    2026-07-01) ; les six dates omises sont celles du point 8 ; 51 × 12 × 3 − 6 = 1 830
    dates vues. **Conforme.**
17. **`test_la_majoration_pour_enfants_des_sections_aux_dates_qui_comptent_dans_les_deux_moteurs`** :
    ses sept cas, rejoués (point 9, 12, 14), tombent juste ; voir le point 15 pour deux de
    ses valeurs attendues.
18. **La carte.** `carte.manques()` : 74 fiches, 425 manques ; au commit 40d3fbc^, 75 et
    432, dont 7 à `sections_liberales_majoration_enfants`. La fiche entre dans
    `LUES_AU_DROIT` sans manque. **Conforme.**

`test_sections_liberales.py`, `test_carte.py`, `test_textes.py` : 91 verts ; sous
`PRESOMPTIONS_DECALEES=1`, 90 et un sauté.

## Ce qui reste

- **À une file E-bis** : la liste des textes de la CAVAMAC d'avant 2011 (point 7) ; l'AAH
  de l'article 8 du règlement de 2026 (point 10) ; la réversion de la CAVEC jointe à son
  écart déclaré (point 13) ; l'en-tête et le cas de la Cipav de 1999 du test (point 15).
- **À la correction de la CAVAMAC** : l'erreur confirmée ; le cas du 1er octobre 2011,
  1 344,23 €, à côté de celui du 1er juillet, 1 332,33 €.
