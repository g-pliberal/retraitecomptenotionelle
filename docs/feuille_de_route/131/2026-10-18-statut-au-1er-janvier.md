# Le statut de l'exploitant au 1er janvier, qui fixe chacune de ses années

Le reste que les notes de l'année de cessation et des années incomplètes
(`2026-10-17-points-et-revenu-de-l-annee-de-cessation.md`,
`2026-10-18-annees-incompletes-de-l-exploitant.md`) avaient laissé : le moteur
ne lisait la situation du 1er janvier que l'année du départ, dont les lignes de
deux statuts, chef puis collaborateur, se partageaient les douze mois ; une
cessation antérieure gardait ses mois, et le statut pris en cours d'année les
siens.

**La règle, lue.** Code rural, L. 731-10-1 (LEGIARTI000019950453) : les
cotisations « dues par les personnes mentionnées aux articles L. 722-9,
L. 722-10 et L. 722-15 sont fixées pour chaque année civile », la situation du
chef « appréciée au premier jour de l'année civile au titre de laquelle elles
sont dues », et qui cesse en cours d'année les doit « au titre de l'année
civile entière », sans borne à l'année du départ. L. 722-15 y range toutes les
« personnes non salariées occupées dans les exploitations »
(LEGIARTI000006585217), collaborateurs et aides familiaux nommés depuis 2026
(LEGIARTI000051289336) ; R. 731-57 et, de 1985 à 2005, l'article 2 du décret
n° 84-936 disent la même situation au 1er janvier. L'article 3 de ce décret
(LEGIARTI000006767567) laisse au cédant d'une exploitation cédée en cours
d'année demander à son successeur « le remboursement de la fraction de la
cotisation [...] d'assurance vieillesse [...] correspondant à la période
comprise entre la date à laquelle la cession a été effectivement réalisée et le
31 décembre » : le cédant doit l'année, son successeur rien. La pratique : la
MSA de Bourgogne (questions-réponses du webinaire du 23 avril 2026) répond au
conjoint collaborateur affilié chef « à effet en juin 2026 » que « les
premières cotisations 2027 seront calculées » sur l'assiette du nouvel
installé ; la fiche « Statut de conjoint collaborateur » de la MSA
(réglementation au 1er janvier 2009) ne rend proportionnelle à la durée
d'affiliation de l'année que la cotisation ATEXA. Aucune page lue ne chiffre
les points de l'année d'un changement de statut.

**Ce qui est fait.** `Carriere._statuts_au_1er_janvier`
(`statutsAu1erJanvier`) : chaque année que fixe la situation du 1er janvier,
et les statuts qui la cotisent entière. Au régime au 1er janvier (une ligne
agricole l'année d'avant) et sans autre activité cotisée (R. 731-83), l'année
que ses lignes agricoles ne remplissent pas, quelle qu'elle soit, et celle qui
porte deux statuts, se cotisent dans le statut du 1er janvier : celui de
l'année d'avant, ou, quand elle en a eu deux, celui qu'il y a pris. Le statut
pris en cours d'année n'a rien, comme l'installation, que la même table porte
d'un ensemble vide : `statut_pris_apres_le_1er_janvier`
(`statutPrisApresLe1erJanvier`) remplace `installation_agricole`.
`annee_de_cessation_agricole` en devient l'année de la date d'effet ;
`annee_entiere_agricole`, `part_cotisee_ligne`, `trimestres_retenus`,
`trimestres_ecoules` et le revenu moyen de 2026 la lisent comme avant ;
`qualite_agricole` rend le statut du 1er janvier, quelle que soit la ligne en
tête, pour les minima (D. 732-110) et les points de RCO de chef. Avant les
cotisations de 1985, comme quand le statut du 1er janvier ne se lit pas, les
statuts de l'année où l'exploitant cesse s'en partagent les douze mois, comme
le faisait l'année du départ. Trois tests, dans les deux moteurs
(`test_simulateur.py`) : le chef parti le 1er août 2024, collaborateur depuis
avril, a son année de chef, 30 points et 133 de RCO, et rien au collaborateur,
au lieu de trois septièmes et quatre septièmes, 16,43 et 183,29 points ; le
chef qui cesse le 1er juillet 2020 et part en 2024 compte quatre trimestres en
2020, 124 au régime, et 30 points, et non deux, 122 et onze ; la
collaboratrice devenue cheffe le 1er juillet 2015 a son année de
collaboratrice, quatre trimestres, 16 et 66 points, et rien à la cheffe, au
lieu de deux trimestres à chaque ligne, que le plafond de l'année réduisait à
deux en tout (138 au régime, et non 140), et de 19,5 et 133 points. Le test
qui partageait l'année du départ entre ses lignes devient le premier. Les
fiches taux_plein_et_proratisation (deux lectures), retraite_proportionnelle_msa,
assiette_minimale_agricole et pension_non_salaries_agricoles_2026 le disent.

**La classe.** La situation du 1er janvier est celle du seul régime agricole :
le plafond des indépendants se réduit au prorata de leur affiliation
(R. 613-17, que cite la note des années incomplètes), et la classe des barèmes
qui rendent une année à une ligne incomplète a sa note
(`2026-10-18-annees-incompletes-de-l-exploitant.md`).

**Ce qui bouge.** Rien dans les fichiers fabriqués : `regenerer.py --verifier`
tient pour à jour le paquet, ses agrégats et les 883 témoins de simulation,
dont aucune carrière ne cesse avant son départ ni ne change de statut dans
l'année. Les témoins de pages étaient périmés avant ce changement ; il ajoute un
kilo-octet et demi au portage, dont le README ancre le poids. GitHub refait les
fichiers.

**Restes, trouvés en chemin.** L'année du décès, que L. 731-10-1 cotise au
prorata, sauf option du conjoint survivant pour l'année entière : le modèle la
compte entière, comme l'année du départ. Une installation ou un changement de
statut l'année du départ, ou un passage de quelques mois sans ligne agricole
avant ni après, gardent leurs mois : la ligne ne dit pas si elle couvre
janvier. Ce que l'exploitant verse l'année où il cesse, s'installe ou change
de statut, que le compte (`moteur/compte.py`) et les indicateurs de cycle de
vie lisent aux mois.

**Ce qui attend le propriétaire.** La question déjà posée des années cotisées
au prorata (R. 731-83), à laquelle s'ajoute une pièce : la réponse à la
question écrite n° 10883 (JO du 3 février 2026) décrit R. 731-83 comme « un
remboursement partiel des cotisations d'assurance maladie au prorata temporis
des mois restant à courir entre la cessation de l'activité agricole et la fin
de l'année civile », rien des cotisations de vieillesse, qui resteraient dues
pour l'année entière et en porteraient les quatre trimestres et les points ;
le moteur garde à cette année ses mois, comme R. 731-83 l'écrit. À trancher
avec la pratique de la MSA.
