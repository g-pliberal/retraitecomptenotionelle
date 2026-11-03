# Étape 2, cinquième partie : la CAFAT, la CPS de Polynésie, Wallis-et-Futuna et les fonctionnaires de Nouvelle-Calédonie, lus et mis en fiche

**Le 16 octobre 2026 : quatre fiches de règles, `approchee`, pour cinq régimes
du Pacifique qui n'avaient que la fiche générique de liquidation —
`cafat_pension_de_base`, `cps_polynesie_pension_des_salaries` (les deux
tranches), `wallis_et_futuna_pension_des_salaries` et
`clr_nouvelle_caledonie_pension_des_fonctionnaires`. Aucun moteur, aucun
chiffre ne bouge. Trois lignes d'inventaire sont corrigées.**

Demande : la vague bis du 16 octobre, session 12, « action 145, étape 2. La
CAFAT, la CPS de Polynésie, Wallis-et-Futuna et les fonctionnaires du
Pacifique, lus à la source et mis en fiche, documentés sans être calculés ;
puis, si l'étape le permet, les trois hors champ ».

- *Où sont les textes.* Lois du pays et délibérations, hors de l'index de la
  DILA. La Nouvelle-Calédonie les publie consolidés sur Juridoc, joignable :
  la fiche de la CAFAT et celle de la caisse locale de retraites citent
  l'article. LexPol, la base polynésienne, et le site de l'administration
  supérieure de Wallis-et-Futuna, qui publie son Journal officiel, refusent
  la connexion depuis le conteneur ; le site de la CPS de Polynésie est une
  application sans texte. Pour ces deux territoires, la fiche lit des sources
  officielles de second rang : le CLEISS, le site de la CPSWF, le rapport 2021
  de l'IEOM. Les textes juridiques de Juridoc portent « droits réservés de
  reproduction » : les fiches les citent, le dépôt ne les garde pas.
- *Ce que le modèle ne fait pas*, et que les fiches nomment :
  1. **CAFAT.** La valeur de référence est publiée chaque mois par la fiche
     des paramètres de la caisse (2 845,44 F CFP en 2026, pour un point de
     256,09 F CFP, gelé depuis avril 2023) : le rendement descend de 10,3 %
     en 2016 à 9,0 % en 2026, quand le dépôt l'estime à 10 % ; la pension
     simulée est trop haute de 11 % en 2026. L'anticipation, dix trimestres à
     1,5 % d'abattement, ou sans abattement à 59,5 ans avec 37 années en
     2026, jusqu'à dix-huit trimestres pour 39 années, n'est pas portée ; ni
     le plafond du territoire, ni le minimum par années de cotisation. Le
     chômage cotise à la CAFAT et y vaut des points (Lp. 100-7) : l'inventaire
     le disait non lu.
  2. **CPS de Polynésie.** Le salaire de référence est la moyenne des 180
     meilleurs mois des 240 derniers, non des dix meilleures années ; ni les
     abattements, ni la pension réduite dès 57 ans, ni la majoration de 1,84 %
     par année au-delà de la durée ne sont portés. La tranche B, 2 % du salaire
     par année pour 17,43 % de cotisation, rend 11,5 % : le dépôt a juste.
  3. **Wallis-et-Futuna.** La cotisation de retraite est de 21 % depuis 2020,
     11,1 % en 2009 (IEOM) ; la fiche de régime prend le taux total de la
     caisse, six points de plus : la cotisation simulée est trop haute de 54 %
     en 2009, de 29 % depuis 2020. La délibération n° 25/AT/2015 porte la
     durée du taux plein à 35 ans et ouvre l'anticipation dès 55 ans, à 7 %
     d'abattement par année, sans abattement à 57 ans avec 35 années ; sa
     date d'effet n'est pas lue, la fiche la suppose au 1er janvier 2016.
  4. **Fonctionnaires de Nouvelle-Calédonie.** L'abattement est par tranches
     d'âge, 10, 16, 24, 35 et 40 %, réduit pour 35 et 40 années de services,
     non 2,5 % par trimestre ; toutes les pensions sont minorées de 8 % en
     2026 et 2027 ; l'âge se réduit pour les services calédoniens d'avant
     2014, jusqu'à 55 ans ; la retenue et la contribution portent sur le
     traitement majoré de 73 %, et la cotisation simulée est trop basse
     d'environ 42 %.
  Au propriétaire de dire si ces écarts rejoignent ceux des notes du 13, du
  14 et du 16 octobre ; la CAFAT (rendement) et Wallis-et-Futuna (taux) se
  corrigeraient d'une donnée chacune.
- *Les tests.* `test_donnees.py`, `test_carte.py`, `test_contrats.py`,
  `test_textes.py` et `test_regle_de_chacun.py` passent. `inventaire.yaml` et
  `docs/regimes.md` sont refaits par leurs scripts. Les échecs de
  `test_prose.py` (poids des pages, tableau de bord, chiffrage) tiennent aux
  fichiers fabriqués, que GitHub refait.
- *Ce qui devrait s'écrire dans les pages* : rien en dur ; la page Données lit
  les lignes d'inventaire corrigées.
- *Ce qui reste de l'étape 2.* Les trois hors champ : la CRFM de Mayotte, les
  élus du Pacifique, les régies ferroviaires d'outre-mer ; puis les limites de
  l'étape (`docs/limites/4-regimes-incomplets.md`), une fois, à sa fin. À lire
  quand les sites répondront : LexPol pour la Polynésie (délibérations
  n° 87-11 AT et n° 95-180 AT, loi du pays n° 2019-6), le Journal officiel de
  Wallis-et-Futuna (délibérations n° 20 bis/AT/2009 et n° 25/AT/2015, statut
  de la CPSWF) ; et sur Juridoc, la délibération n° 300 de 1961 et les
  rédactions du code calédonien d'avant 2025.
