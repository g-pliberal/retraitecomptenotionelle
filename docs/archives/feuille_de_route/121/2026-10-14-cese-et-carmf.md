# Le CESE au taux de son mandat, la CARMF d'avant 2000 présumée : l'action se clôt

**Le 14 octobre 2026, le moteur liquide chaque annuité de la caisse du CESE au
pourcentage de la période de son année, et non plus à celui de l'année de
liquidation ; la durée de la CARMF d'avant 2000, dont les statuts restent
introuvables, se déclare présumée.** Le registre `A_RELIRE` du test de la
règle de chacun est vide : l'action 121 se clôt.

## Le CESE : un interrupteur, deux moteurs

L'article 17 du règlement de la caisse fixe le pourcentage par annuité selon
la date du MANDAT : 2,11 % jusqu'au 31 août 2004, 2,02 % jusqu'au
30 septembre 2010, puis 1,95, 1,90, 1,85 et 1,82 % depuis le 28 octobre 2013.
La fiche de régime l'écrivait en durée requise par année civile (75 % sur 142,
149, 154, 158, 162 et 165 trimestres), et le moteur prenait celle de l'année
de liquidation pour toutes les annuités.

Un interrupteur de période, `annuites_au_taux_de_leur_annee`, renvoie à la
fiche `cese_pension_des_membres`, qui le déclare (`code.interrupteurs`) ; les
quatorze périodes de `regimes/cese_membres.yaml` le posent. Quand il est vrai,
`liquider_chaque_regime` remplace le numérateur de la proratisation par les
trimestres de chaque période pesés de la durée de la liquidation sur la durée
requise de leur période (`annuites_au_taux_de_leur_annee`, dans
`droit/liquider.py` ; `annuitesAuTauxDeLeurAnnee`, dans `droit/liquider.js`),
arrondis au centième de la même façon des deux côtés ; le maximum des trois
quarts borne la somme. Une annuité de 2000 liquidée en 2030 pèse 165/142
trimestres : 2,11 % de l'assiette, et non 1,82 %. Le chargeur, le schéma et le
paquet portent le champ (`construire_donnees.py` ne l'écrit que vrai).

Les témoins : rien ne bouge au scénario 1, dont les témoins du CESE font
quarante ans de mandat et touchent le maximum ; les trois témoins des
scénarios 3 et 5 dont les droits acquis se convertissent à la bascule montent
de 3 à 8 %. Le portage les retrouve.

Le test de la règle de chacun ne compare plus la durée d'une période qui porte
l'interrupteur : elle n'y est que le dénominateur, et la pension ne dépend plus
de l'année du départ. Un test nouveau
(`test_l_annuite_du_cese_garde_le_taux_de_son_mandat`) le vérifie sur vingt ans
de mandat, liquidés sur 142 ou sur 165 trimestres.

Restent approchées, et déclarées dans la fiche : les coupures à l'année civile
(septembre à décembre 2004 à 2,11 % au lieu de 2,02 %, novembre et décembre de
2010 à 2013 au pourcentage de l'année), le pourcentage lu par une durée en
trimestres entiers (0,4 % d'écart au plus), et l'allocation viagère des
mandats courts d'après 2015, comptée double.

## La CARMF d'avant 2000 : présumée

Statuts d'avant 2000 cherchés : LEGI et JORF n'en portent que des résumés
d'arrêtés ; le site de la CARMF ne publie que l'état consolidé ; deux
recherches sur le web n'ont rien rendu. La borne de 2000 n'est pas la date
d'un texte, mais celle d'une période (« Cet article n'est lu que dans l'état
consolidé des statuts, sans date d'origine : la fiche le sert à partir de
2000 ») : la déclarer à l'année d'effet aurait menti. Un troisième registre,
`PRESUMES`, la reçoit, avec ce qu'on a cherché. Un indice, que la fiche ne
suit pas encore : la chronologie de la CARMF date de 1979 la retraite à
soixante ans « avec un coefficient d'abattement », une minoration par l'âge
qui vaudrait dès cette date, et non la décote du régime de base que la fiche
lit avant 2000.

## Ce qui reste, et à qui

- **L'archivage de l'action** : à une session d'entretien.
- **Au dossier des décisions** : 172 trimestres présumés à la Banque de France
  pour les nés de 1966 à 1972 ; la table de l'Opéra de 2019 prêtée au ballet ;
  la CARMF d'avant 2000, minoration par l'âge dès 1979, ou la présomption
  d'aujourd'hui ; le CESE, si le Conseil peut donner ses règlements de 1958 et
  de 2015.
- **À une session du site** : la phrase de la page Méthode sur la durée de
  l'Opéra et de la Banque de France, lue à la date où l'assuré réunit les
  conditions.
- **Lectures déclarées, sans chantier** : l'ancien régime de la Banque de
  France, avant 2007 ; ce que l'Opéra applique au ballet et aux chœurs depuis
  juillet 2019 ; l'âge de la CARPIMKO avant 2016.
