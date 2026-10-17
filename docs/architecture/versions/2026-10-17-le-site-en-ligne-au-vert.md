# Version du 17 octobre 2026 : le site en ligne au vert

Le site ne part plus en ligne à chaque envoi sur `main`, mais d'une suite
verte seulement (§ 10, action 163). GitHub Pages publiait `main` à chaque
poussée : celle d'une session, que la suite complète n'avait pas encore
passée, comme celle du robot qui écrit le verdict, rouge compris, et sans les
fichiers fabriqués, qu'il ne commite que sur une suite verte. Du 6 au
17 octobre 2026, `main` a reçu 25 verdicts rouges pour 143 verts.

Désormais `scripts/publier_fabrique.sh` dit `en_ligne=oui` quand il pousse le
verdict d'une suite verte sur `main`, et `tests.yml` déploie alors sur GitHub
Pages, par GitHub Actions, l'arbre de ce commit (`git archive HEAD`), et lui
seul : ni un envoi de session, ni le répertoire de travail de la course et ses
caches. La documentation de GitHub dit qu'une poussée du jeton du workflow ne
déclenche pas de construction de Pages, quand les déploiements du 17 octobre
montrent le contraire : la mise en ligne ne repose donc pas sur ce
comportement, ni sur une branche que le robot avancerait, mais sur un job,
`en_ligne`, qui déploie lui-même. Une garde des présomptions rouge ne retient
pas le site, pas plus que les fichiers fabriqués : la suite est verte.

Elle demande un réglage que seul le propriétaire peut faire : Settings →
Pages → Source « GitHub Actions ». Tant qu'il n'est pas fait, Pages publie
encore chaque envoi, et la course ne déploie rien ni ne rougit. Revenir en
arrière, c'est rétablir `main`, que la course verte suivante remet en ligne.
