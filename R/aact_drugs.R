#!/usr/bin/env Rscript
#############################################################################
### CTTI = Clinical Trials Transformation Initiative
### AACT = Aggregate Analysis of ClinicalTrials.gov
### According to website (July 2018), data is refreshed monthly.
### https://aact.ctti-clinicaltrials.org/
#############################################################################
### See also: https://github.com/ctti-clinicaltrials/aact
#############################################################################
### drugs.csv from intervention_drug_list.sql
### drugs_leadmine.tsv from Go_NER.sh
### descriptions_MedDRA_hlt_leadmine.tsv from Go_NER.sh
### descriptions_MedDRA_llt_leadmine.tsv from Go_NER.sh
#############################################################################
### interventions.nct_id is the study ID.  interventions.id not unique
### for interventions.name.
#############################################################################
library(readr)
library(dplyr, quietly = T)
library(plotly, quietly = T)
library(rcdk, quietly = T)
library(png, quietly = T)


drugs <- read_delim("data/drugs.tsv", "\t", skip=1, col_names=c("id", "nct_id", "name"), col_types = "dcc")
drugs <- drugs[order(drugs$name),]

n_names <- length(unique(drugs$name))
writeLines(sprintf("Total drug trials: %d ; Unique drug names: %d", nrow(drugs), n_names))

drugs_leadmine <- read_delim("data/drugs_leadmine.tsv",  "\t", escape_double=F, trim_ws=T)
drugs_leadmine <- dplyr::rename(drugs_leadmine, nct_id = DocName, smiles = ResolvedForm)
n_smi <- length(unique(drugs_leadmine$smiles))
writeLines(sprintf("Unique drug smiles: %d", n_smi))
#
drugs_smi <- drugs_leadmine[!is.na(drugs_leadmine$smiles),c("smiles","OriginalText")]
drugs_smi <- unique(drugs_smi)
drugs_smi <- rename(drugs_smi, name = "OriginalText")
drugs_smi <- drugs_smi[order(drugs_smi$name),]
drugs_smi <- group_by(drugs_smi, smiles) %>% summarise(names = paste(name, collapse="; "))
drugs_smi <- drugs_smi[order(nchar(drugs_smi$smiles)),]
write_delim(drugs_smi, "data/drugs_smi.smi", "\t", col_names=F)
drugs_smi_sample <- sample_n(drugs_smi, 120)

mols <- parse.smiles(drugs_smi_sample$smiles)
#view.table is fragile.
#view.table(mols, drugs_smi_sample, cellx=100, celly=60)

#molimg <- view.molecule.2d(mols)
h <- 400
w <- 400
molimg <- view.image.2d(mols[[1]], get.depictor(width=w, height=h))
#
plot(c(0, w), c(0, h), asp=1.0, type="n", xlab="", ylab="", pty="m", xaxt="n", yaxt="n")
rasterImage(molimg, 0, 0, w, h)
writePNG(molimg, target = "data/molimg.png",
         text=c(source=R.version.string), metadata=sessionInfo())
#
###
#
ner <- drugs_leadmine[!is.na(drugs_leadmine$smiles),] %>% group_by(nct_id) %>% summarise(n = n())
writeLines(sprintf("Leadmine results by drug trial: %.1f%% (%d/%d)", 
                   100*nrow(ner)/length(unique(drugs$nct_id)),
                   nrow(ner), length(unique(drugs$nct_id))))
#
ner <- drugs_leadmine[!is.na(drugs_leadmine$smiles),] %>% group_by(OriginalText) %>% summarise(n = n())
writeLines(sprintf("Leadmine results by drug name: %.1f%% (%d/%d)", 
                   100*nrow(ner)/length(unique(drugs$name)),
                   nrow(ner), length(unique(drugs$name))))
#
###
# Maybe not interesting.  Many non-structures expected.
#resolution_fails <- unique(drugs_leadmine[is.na(drugs_leadmine$smiles),c("EntityText","smiles")])
#write.table(resolution_fails, file="data/leadmine_resolution_fails.tsv", sep="\t", row.names=F, quote=T, qmethod="double")
###


###
# MedDRA HLT/LLT NER:
###
desc_hlt_leadmine <- read_delim("data/descriptions_MedDRA_hlt_leadmine.tsv", "\t")
desc_hlt_leadmine <- dplyr::rename(desc_hlt_leadmine, nct_id = DocName)
ner <- desc_hlt_leadmine %>% group_by(PossiblyCorrectedText) %>% summarise(n = n())
ner <- ner[order(-ner$n),]
#
#Top MedDRA HLT counts:
writeLines(sprintf("===\nTop MedDRA HLT counts:"))
writeLines(sprintf("%3d. %28s: %6d", 1:25, ner$PossiblyCorrectedText[1:25], ner$n[1:25]))
#
desc_llt_leadmine <- read_delim("data/descriptions_MedDRA_llt_leadmine.tsv", "\t")
desc_llt_leadmine <- dplyr::rename(desc_llt_leadmine, nct_id = DocName)
ner <- desc_llt_leadmine %>% group_by(PossiblyCorrectedText) %>% summarise(n = n())
ner <- ner[order(-ner$n),]
#
#Top MedDRA LLT counts:
writeLines(sprintf("===\nTop MedDRA LLT counts:"))
writeLines(sprintf("%3d. %28s: %6d", 1:25, ner$PossiblyCorrectedText[1:25], ner$n[1:25]))
