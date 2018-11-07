# Clinicaltrials.gov analytics
Includes cheminformatics and medical terms text mining.

---

### About AACT:
* [AACT-CTTI](https://aact.ctti-clinicaltrials.org/) database from Duke.
* CTTI = Clinical Trials Transformation Initiative
* AACT = Aggregate Analysis of ClinicalTrials.gov
* According to website (July 2018), data is refreshed monthly.
* Identify drugs by intervention ID, since may be multiple drugs per trial (NCT\_ID).

### References:
* <http://clinicaltrials.gov>
* <https://aact.ctti-clinicaltrials.org/>
* [AACT Data Dictionary](https://aact.ctti-clinicaltrials.org/data_dictionary), which references <https://prsinfo.clinicaltrials.gov/definitions.html>.
* [The Database for Aggregate Analysis of ClinicalTrials.gov (AACT) and Subsequent Regrouping by Clinical Specialty](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0033677), Tasneem et al., March 16, * 2012https://doi.org/10.1371/journal.pone.0033677.
* [How to avoid common problems when using ClinicalTrials.gov in research: 10 issues to consider](https://www.bmj.com/content/361/bmj.k1452), Tse et al., BMJ 2018; 361 doi: https://doi.org/10.1136/bmj.k1452 (Published 25 May 2018.
* See also: <https://www.ctti-clinicaltrials.org/briefing-room/publications>

### About NextMove LeadMine:
* Text mining performed with [NextMove LeadMine](http://nextmovesoftware.com).

### Purpose:
* Associate drugs with diseases/phenotypes.
* Associate protein targets with diseases/phenotypes.
* Associate drugs with protein targets.

### Tables of interest:
* **studies**
* **keywords**
* **brief\_summaries**
* **detailed\_descriptions**
* **conditions**
* **browse\_conditions**           (NCT-MeSH links)
* **interventions**
* **browse\_interventions**        (NCT-MeSH links)
* **intervention\_other\_names**    (synonyms)
* **study\_references**            (including type results\_reference)

### Overall workflow:
* `Go\_ct\_GetData.sh` - Fetch selected data from AACT db.
* `Go\_xref\_drugs.sh` - PubChem and ChEMBL IDs via APIs.
* `Go\_BuildDicts.sh` - Build NextMove LeadMine dicts for MeSH etc. NER.
* `Go\_NER.sh` - LeadMine NER.
* `Go\_NER\_pubmed.sh` - LeadMine NER, selected referenced PMIDs.
* `leadmine\_utils.sh` - Runs LeadMine API custom app on TSVs.
* Results analyzed for associations via R codes.

### Association semantics:
* **keywords**, **conditions** and **summaries**: reported terms and free text which may be text mined for other intended associations.
* **studies**, **descriptions** and **conditions** text mined for MeSH disease/phenotype terms.  These free text fields may indicate both the intended and other conditions, symptoms and phenotypic traits, which may be non-obvious from the study design.
