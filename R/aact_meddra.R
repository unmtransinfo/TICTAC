#!/usr/bin/env Rscript
#############################################################################
### CTTI = Clinical Trials Transformation Initiative
### AACT = Aggregate Analysis of ClinicalTrials.gov
### According to website (July 2018), data is refreshed monthly.
### https://aact.ctti-clinicaltrials.org/
#############################################################################
### See also: https://github.com/ctti-clinicaltrials/aact
#############################################################################
### descriptions_MedDRA_hlt_leadmine.tsv from Go_NER.sh
### descriptions_MedDRA_llt_leadmine.tsv from Go_NER.sh
#############################################################################
library(readr)
library(dplyr, quietly = T)
library(plotly, quietly = T)


###
# Corpus = Descriptions
# MedDRA HLT/LLT NER:
###
#HLT (high-level terms):
desc_hlt_leadmine <- read_delim("data/descriptions_MedDRA_hlt_leadmine.tsv", "\t")
desc_hlt_leadmine <- dplyr::rename(desc_hlt_leadmine, nct_id = DocName)
ner <- desc_hlt_leadmine %>% group_by(PossiblyCorrectedText) %>% summarise(n = n())
ner <- ner[order(-ner$n),]
#
writeLines(sprintf("===\nTop MedDRA HLT counts:"))
writeLines(sprintf("%3d. %28s: %6d", 1:50, ner$PossiblyCorrectedText[1:25], ner$n[1:25]))
#
###
#LLT (low-level terms):
desc_llt_leadmine <- read_delim("data/descriptions_MedDRA_llt_leadmine.tsv", "\t")
desc_llt_leadmine <- dplyr::rename(desc_llt_leadmine, nct_id = DocName)
ner <- desc_llt_leadmine %>% group_by(PossiblyCorrectedText) %>% summarise(n = n())
ner <- ner[order(-ner$n),]
#
writeLines(sprintf("===\nTop MedDRA LLT counts:"))
writeLines(sprintf("%3d. %28s: %6d", 1:50, ner$PossiblyCorrectedText[1:25], ner$n[1:25]))
