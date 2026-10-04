# Exécute Destinie 2 (INSEE) sur les cas que `destinie_2.py` décrit.
#
#     Rscript destinie_2.R <dossier des entrées> <dossier des sorties> <variante>
#
# Ce script appartient au dépôt ; Destinie 2 n'y entre pas. Il s'installe à
# part (paquet R `destinie`, https://github.com/InseeFr/Destinie-2, GPL-3.0 ou
# ultérieure, paramètres sous ODbL et DbCL), et ce script n'en appelle que les
# fonctions exportées et les jeux de données livrés avec lui. Seules les
# sorties entrent au dépôt, figées dans `tests/temoins/destinie_2.json`.
#
# Les entrées sont les tables qu'attend `destinieSim` — ech, emp, fam,
# union_base, union —, écrites en CSV par `destinie_2.py`, et `options.json`.
# La population n'est pas simulée : pas de `destinieDemographie`, ni de
# transitions sur le marché du travail, ni d'imputation de salaires. Les
# carrières, les naissances, les unions et les décès sont ceux que le script
# Python écrit, et `destinieSim` ne fait que liquider les droits directs, puis
# les réversions et le minimum vieillesse.
#
# La variante dit ce que l'on neutralise, une option de Destinie à la fois
# (`options.json`) : « base » rien ; « sans_majoration » les majorations de
# pension pour trois enfants (NoBonif). Chaque variante tourne dans son propre
# processus : les tables de sortie de Destinie sont des objets statiques du
# code C++, qu'un second appel dans la même session retrouverait.

suppressPackageStartupMessages({
  library(destinie)
  library(dplyr)
})

arguments <- commandArgs(trailingOnly = TRUE)
if (length(arguments) != 3) {
  stop("usage : Rscript destinie_2.R <entrees> <sorties> <variante>")
}
entrees <- arguments[1]
sorties <- arguments[2]
variante <- arguments[3]
dir.create(sorties, showWarnings = FALSE, recursive = TRUE)

reglages <- jsonlite::fromJSON(file.path(entrees, "options.json"))
an_max <- as.integer(reglages$AN_MAX)

lire <- function(nom) {
  read.csv(file.path(entrees, paste0(nom, ".csv")), stringsAsFactors = FALSE)
}

sim <- new.env()
options_destinie <- list(
  anLeg = as.integer(reglages$anLeg),
  AN_MAX = an_max,
  comp = as.integer(reglages$comp),
  pas1 = 3 / 12, pas2 = 1,
  NoRegUniqAgircArrco = FALSE,
  SecondLiq = FALSE
)
neutralisees <- reglages$variantes[[variante]]
if (is.null(neutralisees)) stop("variante inconnue : ", variante)
for (option in neutralisees) options_destinie[[option]] <- TRUE
sim$options <- options_destinie

# Les paramètres économiques et sociaux : les hypothèses du COR que le paquet
# livre (la feuille ParamSociaux de l'année), prolongées par ses règles
# d'indexation, qui dépendent de la législation choisie.
suppressMessages(import_scenario_eco_cor(
  sim, date_fin_simulation = an_max,
  scenario_productivite = reglages$scenario_productivite,
  scenario_chomage = reglages$scenario_chomage
))

# La démographie n'est pas simulée, mais `destinieSim` lit les tables de
# mortalité et les équations de santé : celles du scénario central, livrées
# avec le paquet. `import_scenario_demo_insee` échouerait : le classeur
# `ciblesDemographie_FE_dev.xls` de `Param_demo_2022` n'est pas publié.
data("fec_Cent_vie_Cent_mig_Cent", package = "destinie", envir = environment())
for (nom in ls(fec_Cent_vie_Cent_mig_Cent)) {
  assign(nom, get(nom, envir = fec_Cent_vie_Cent_mig_Cent), envir = sim)
}
data("eq_struct", package = "destinie", envir = environment())
for (nom in ls(eq_struct)) {
  if (!exists(nom, envir = sim, inherits = FALSE)) {
    assign(nom, get(nom, envir = eq_struct), envir = sim)
  }
}
sim$FinEtudeMoy <- xlsx::read.xlsx(
  system.file("extdata", "PARAM_etude.xls", package = "destinie", mustWork = TRUE),
  sheetName = "TABLEFINDET0", startRow = 2
)
# Le code C++ veut un facteur, dans cet ordre ; R 4 lit des chaînes.
sim$EqSante$NomVar <- factor(
  as.character(sim$EqSante$NomVar),
  levels = c("INCID_0_F", "INCID_0_H", "INCID_1_F", "INCID_1_H",
             "MORT_F", "MORT_H", "PREVAL_F", "PREVAL_H")
)

entiers <- function(table, numeriques = character(0)) {
  for (colonne in names(table)) {
    if (!(colonne %in% numeriques)) table[[colonne]] <- as.integer(table[[colonne]])
    else table[[colonne]] <- as.numeric(table[[colonne]])
  }
  table
}
sim$ech <- entiers(lire("ech"), c("taux_prim", "k"))
sim$emp <- entiers(lire("emp"), c("salaire"))
sim$fam <- entiers(lire("fam"))
sim$union_base <- entiers(lire("union_base"))
sim$union <- entiers(lire("union"))

destinieSim(sim)

write.csv(as.data.frame(sim$liquidations), file.path(sorties, "liquidations.csv"), row.names = FALSE)
write.csv(as.data.frame(sim$retraites), file.path(sorties, "retraites.csv"), row.names = FALSE)

# Les paramètres que Destinie a lus, aux années des cas : ce qui explique un
# écart de montant sans qu'il faille relancer R.
colonnes <- intersect(reglages$parametres, names(sim$macro))
macro <- as.data.frame(sim$macro)
write.csv(macro[macro$annee %in% reglages$annees_parametres, c("annee", colonnes)],
          file.path(sorties, "parametres.csv"), row.names = FALSE)

versions <- list(
  R = paste(R.version$major, R.version$minor, sep = "."),
  destinie = as.character(packageVersion("destinie")),
  Rcpp = as.character(packageVersion("Rcpp")),
  dplyr = as.character(packageVersion("dplyr")),
  xlsx = as.character(packageVersion("xlsx")),
  readxl = as.character(packageVersion("readxl")),
  plateforme = R.version$platform
)
writeLines(jsonlite::toJSON(versions, auto_unbox = TRUE, pretty = TRUE),
           file.path(sorties, "versions.json"))
