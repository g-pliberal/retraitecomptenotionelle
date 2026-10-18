# Étape 5, dixième partie : l'année de revenus de l'imposition de la majoration pour enfants, et la limite de son exonération

**La demande.** Le point 4 de « Ce qui reste » de
`2026-10-18-etape-5-prime-pour-l-emploi-des-non-salaries.md` : l'année de
revenus dont l'impôt prend la majoration pour enfants, au texte de la loi de
finances pour 2014. Ni les décisions du propriétaire (l'effet retour dans le
solde, les trois sur le bénéfice), ni l'impôt au site, ni les règles d'avant
1981.

**Où les textes se lisent.** Légifrance refuse `curl`, et l'index JORF de la
DILA n'a de la loi n° 2013-1278 du 29 décembre 2013 que sa notice
(JORFTEXT000028399511, JO du 30 décembre 2013). Son texte se lit au site de
l'Assemblée nationale, au texte adopté en lecture définitive (TA n° 267,
19 décembre 2013), et la décision n° 2013-685 DC à celui du Conseil
constitutionnel. L'index LEGI a les cinquante rédactions de l'article 81 du
code général des impôts parues de 1950 à 2013, et celles de 2014. La
doctrine : l'actualité ACTU-2014-00067 du 5 mars 2014, par le jeu de données
« bofip-vigueur » de data.economie.gouv.fr ; au BOFiP, le BOI-RSA-PENS-20-10
du 12 septembre 2012 et du 5 mars 2014, le BOI-RSA-PENS-10-10-10-20 et le
BOI-RSA-BASE-30-30 du 12 septembre 2012 ; aux archives du BOFiP
(bofip-archives.impots.gouv.fr), la documentation de base 5 F 1222 du
10 février 1999.

**Ce que disent les textes.**

- *L'exonération.* « les majorations de retraite ou de pension pour charges
  de famille » sont affranchies de l'impôt par les cinquante rédactions de
  l'article 81, de celle du 30 avril 1950 (2°, LEGIARTI000048121406) à celle
  du 7 juin 2013 (2° ter, LEGIARTI000027518339) ; la rédaction du 1er janvier
  2014 porte « 2° ter (Abrogé) » (LEGIARTI000028416932).
- *L'abrogation et son année.* « Le 2° ter de l'article 81 du même code est
  abrogé » (art. 5) ; « Sous réserve de dispositions contraires, la présente
  loi s'applique : 1° À l'impôt sur le revenu dû au titre de 2013 et des années
  suivantes » (art. 1er, II), et l'article 5 n'en dispose pas autrement. La
  décision n° 2013-685 DC censure des parties des articles 11, 19, 27, 76, 92
  et 121, et les articles 12, 13, 96, 97, 100, 106 et 112 à 116 : ni le 1er ni
  le 5. L'administration : la loi « a supprimé l'exonération [...] à compter
  de l'imposition des revenus de l'année 2013 » (ACTU-2014-00067) ; « les
  majorations de retraite ou de pension pour charges de famille perçues à
  compter du 1er janvier 2013 sont imposables » (BOI-RSA-PENS-20-10-20140305,
  § 1). Le dépôt l'imposait à toute époque.
- *Ce qu'elle couvre.* Les majorations du régime général, des marins, de la
  fonction publique, et « des majorations de retraite ayant un objet similaire
  servies dans le cadre d'un régime complémentaire légalement obligatoire » ;
  « aussi bien aux majorations allouées en considération d'enfants à charge
  que lorsque les attributaires ont élevé au moins trois enfants » (DB 5 F
  1222, n° 2 et 3). La majoration pour conjoint à charge s'impose : de la
  pension et de ses avantages accessoires, seules la « bonification accordée
  aux assurés sociaux pour charges de famille » et la majoration pour tierce
  personne échappent à l'impôt (BOI-RSA-PENS-10-10-10-20-20120912, § 70).
- *Sa limite.* « le montant exonéré des majorations pour enfant à charge,
  augmenté, le cas échéant, des majorations pour avoir eu ou élevé au moins
  trois enfants, ne peut excéder, pour un même bénéficiaire, 10 % du montant
  de la pension pour les trois premiers enfants et 5 % par enfant au-delà du
  troisième. En outre, le montant de la pension augmentée des majorations ne
  peut excéder le montant du revenu d'activité du bénéficiaire ayant servi à
  la liquidation de ladite pension. Toute somme excédant l'une ou l'autre de
  ces limites est imposable » (DB 5 F 1222, n° 4 ; mot pour mot au
  BOI-RSA-PENS-20-10-20120912, § 30).
- *La CSG.* Sa part déductible « n'est en revanche pas déductible du revenu
  imposable lorsqu'elle est afférente à des revenus exonérés d'impôt sur le
  revenu mais également de cotisations de sécurité sociale », dont « les
  majorations de retraite ou de pension pour charges de famille »
  (BOI-RSA-BASE-30-30-20120912, § 80 et 90).

**Ce qui est fait.**

- `cycle_de_vie.py` : `majoration_exoneree` exonère la majoration jusqu'aux
  revenus de 2012 (`PREMIERE_ANNEE_MAJORATION_IMPOSABLE`), sous la limite de
  10 % de la pension sans elle, plus 5 % par enfant au-delà du troisième
  (`TAUX_EXONERE_TROIS_ENFANTS`, `TAUX_EXONERE_PAR_ENFANT_AU_DELA`) ;
  `parts_exonerees` en fait, pour chaque système, la part exonérée du niveau
  de chaque année, de la majoration que `faire_vivre` mène : celle du scénario
  1, que les systèmes prospectifs gardent à qui est parti avant leur bascule,
  à la part de la bascule ensuite ; rien aux systèmes rétroactifs, qui ne
  servent pas de majoration. Le flux la porte (`Flux.exoneree`) ; l'impôt de
  chaque année et le taux de remplacement après impôt au départ déclarent la
  pension sans elle, la part imposable de l'année ne portant que sur le reste,
  comme la CSG qui se déduit.
- Le portage : `cycle-de-vie.js`, de même (`majorationExoneree`,
  `partsExonerees`).
- Les tests : `test_la_majoration_pour_enfants_s_exonere_jusqu_aux_revenus_de_2012`,
  la règle posée à la main sur la DB ;
  `test_jusqu_aux_revenus_de_2012_le_foyer_ne_declare_pas_la_majoration`, un
  père de trois enfants né en 1946, parti en 2008 : de 2008 à 2012, sa pension
  déclarée perd sa majoration, en 2013 et en 2020 elle la garde ; le système
  prospectif l'exonère de même, le rétroactif non ; son taux de remplacement
  après impôt l'exonère ; vus rouges avant le code. La grille du portage : le
  salarié né en 1948, parti en 2010, a trois enfants, rouge avant le
  JavaScript ; son contrôle a un objet, sa pension déclarée de 2013 dépassant
  de plus de 5 % celle de 2012.
- La veille : l'index LEGI mis à jour au 17 octobre, et `textes.py
  --inscrire`, qui inscrit dix-huit rédactions de l'article L. 731-15 du code
  rural et du décret n° 2008-1072, à examiner.

**Ce que montrent les mesures** (barème projeté sur les prix, convention après
impôt).

- Un père de trois enfants né en 1946, non cadre, au salaire moyen, parti à
  62 ans en 2008 : son impôt de 2010 passe de 1 387 à 1 147 €, celui de 2012
  de 1 342 à 1 093 € ; celui de 2013 ne change pas (1 363 €). Rendement réel
  de 2,202 à 2,214 %, taux d'annuité de 40,40 à 40,51 %, remplacement après
  impôt au départ de 76,7 à 77,7 %.
- Une fonctionnaire de l'État née en 1946, trois enfants, partie en 2008 :
  impôt de 2010 de 3 815 à 2 961 € ; rendement de 3,873 à 3,902 % ;
  remplacement de 103,2 à 106,1 %.
- Une cadre née en 1950, quatre enfants, à 1,5 fois le salaire moyen, partie
  en 2012 : impôt de 2012 de 3 432 à 2 685 € ; rendement de 2,153 à 2,157 % ;
  remplacement de 62,0 à 63,3 %.
- La limite ne mord sur aucun d'eux : leur majoration fait 9,6 % de la
  pension sans elle (trois enfants, au régime général et à l'Arrco), 10,6 %
  (quatre enfants, sous une limite de 15 %), 10 % à la fonction publique. Elle
  mord quand la majoration pour enfants à charge de l'Agirc-Arrco, 5 % par
  enfant, passe celle des enfants nés ou élevés d'un parent dont trois enfants
  sont encore à charge.
- La page Coût n'en dépend pas : l'impôt de son effet retour porte sur la
  distribution de l'EIR, ramenée à la pension de droit direct sans les
  majorations pour enfants (`donnees/distribution.py`), et le cycle de vie
  n'y entre pas.

**Ce qui reste** de l'étape, dans l'ordre :

1. *L'effet retour dans le solde* : au propriétaire.
2. *Les trois décisions sur le bénéfice* : au propriétaire.
3. *L'impôt au site*, et l'affichage de l'effet retour : à la session des
   pages.
4. *Les règles d'avant 1981 sans texte lu.*
5. *Ce que la prime ne prend pas* (point 6 de la note de la prime pour
   l'emploi des non-salariés).
6. *La limite de l'exonération avant 1999*, que le modèle tient de la DB de
   1999, la plus ancienne lue : ses rédactions antérieures, si les archives
   du BOFiP les ont. Et la seconde limite, la pension majorée bornée au
   revenu d'activité qui l'a liquidée, que le modèle ne tient que dans la
   fonction publique, par l'article L. 18 : ailleurs, aucun texte lu ne dit
   ce qu'est ce revenu pour une pension de points. Léger : ni l'une ni
   l'autre ne mord sur un cas de la grille.
