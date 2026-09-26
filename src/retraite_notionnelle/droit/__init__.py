"""Le droit applicable, en étapes (docs/architecture.md, § 7.2 et 7.3).

Le scénario 1 quitte ``scenarios/actuel.py`` pour ce paquet, une étape par
module, et ``moteur/js/droit/`` le suit fonction pour fonction. Pour une
demande, quatre étapes construisent le RELEVÉ DES DROITS qu'elle fait
valoir :

* :mod:`.preparer` — préparer la chronologie : la compléter par les
  présomptions ;
* :mod:`.coordonner` — coordonner les affiliations : rétablir l'agent parti
  de la fonction publique sans droit à pension, router chaque ligne vers les
  régimes qui la reçoivent, puis réunir en groupes les régimes que le droit
  fait liquider ensemble ;
* :mod:`.compter` — compter les durées : assurance, services, cotisés, et les
  trimestres des enfants, dans le régime que la priorité entre régimes
  désigne ;
* :mod:`.acquerir` — acquérir les droits : points, cotisations, durée qu'un
  régime plafonne, points attribués sans cotisation.

Chaque étape écrit une donnée que décrit son schéma, dans
``data/reference/etapes/`` ; :mod:`.releve` les enchaîne, et en tire les
lignes du relevé (contrat C.5).

Puis la LIQUIDATION (§ 7.3) : :func:`.liquidation.liquider`, une fonction
pure de la demande, de l'état et du contexte, fait l'acquisition et trois
étapes de plus :

* :mod:`.ouvrir` — ouvrir le droit : âge légal, catégories actives,
  militaires, carrière longue ; durée requise et taux plein ;
* :mod:`.liquider` — liquider chaque régime : annuités, points, forfait ou
  capital ; décote, surcote, abattement, proratisation ;
* :mod:`.completer` — compléter tous régimes : les deux minima, la surcote
  parentale, la majoration pour enfants.

Entre les deux dernières, elle mesure par des liquidations d'essai ce
qu'apportent les trimestres des enfants, l'AVPF et les points gratuits.
L'ASPA vient après, de l'étape « foyer et net » (:mod:`.foyer`), qui regarde
toutes les ressources. :mod:`.commun` porte ce que les étapes partagent.

Les étapes lisent la chronologie par sa vue, la carrière, et les tables du
scénario 1 par le moteur qui les tient — ``moteur``, un
:class:`~retraite_notionnelle.scenarios.actuel.ScenarioActuel`. Les fiches et
leurs versions les remplaceront (phase 6).
"""
