import json
import os
import sys

import numpy as np
from statsmodels.stats.multitest import multipletests

"""
p_values correction using multiple hypothesis correction using fdr_bh method

We chose to use the fdr_bh method

Main question: Did nature select entanglement to be enriched near functional sites? 
Sub-main queston: Did nature select entanglement to be enriched near specfic functional type? 

Package Implementation: 
https://www.statsmodels.org/dev/generated/statsmodels.stats.multitest.multipletests.html

"""

def main_question_correction():

    enrichment_pval = []
    depletion_pval = []
    two_tailed_pvals = []
    genes = []

    Enrichement, Depletion, Neither = 0, 0, 0

    ALPHA = 0.05

    for pval_files in os.listdir("DATA/yeast_mc_pvals_stochastic_full"):

        uni, _, _ = pval_files.split("-")

        with open(f"DATA/yeast_mc_pvals_stochastic_full/{pval_files}") as reader:
            js_file = json.load(reader)

        enrichment_pval.append(js_file[uni]["Enrichment"])
        depletion_pval.append(js_file[uni]["Depletion"])
        two_tailed_pvals.append(js_file[uni]["two-tailed"])
        genes.append(uni)
    
    _, correct_pvalues, _, _ = multipletests(two_tailed_pvals, alpha=ALPHA, method="fdr_bh")

    for index, q_value in enumerate(correct_pvalues):

        if q_value <= ALPHA:

            if enrichment_pval[index] <= ALPHA:

                Enrichement += 1
                print("Full", "Enrichment: ", genes[index])

            elif depletion_pval[index] <= ALPHA:

                Depletion += 1
                print("Full", "Depletion: ", genes[index])
    
        else: 
            Neither += 1
            print("Full", "Neither: ", genes[index])

    return Enrichement, Depletion, Neither

def sub_main_correction():

    all_individual_sites = {}

    ALPHA = 0.05

    for func_type in os.listdir("DATA/individual_p_vals/"):

        enrichment_pval = []
        depletion_pval = []
        two_tailed_pvalues = []
        genes = []

        Enrichement, Depletion, Neither = 0, 0, 0

        all_individual_sites[func_type] = {}
        all_individual_sites[func_type]["Enrichment"] = 0
        all_individual_sites[func_type]["Depletion"] = 0
        all_individual_sites[func_type]["Neither"] = 0

        for pval_files in os.listdir(f"DATA/individual_p_vals/{func_type}"):

            uni = pval_files.split("-")[0]

            with open(f"DATA/individual_p_vals/{func_type}/{pval_files}") as reader:
                js_file = json.load(reader)

            enrichment_pval.append(js_file[uni]["Enrichment"])
            depletion_pval.append(js_file[uni]["Depletion"])
            two_tailed_pvalues.append(js_file[uni]["two-tailed"])
            genes.append(uni)

        _, correct_pvalues, _, _ = multipletests(two_tailed_pvalues, alpha=ALPHA, method="fdr_bh")

        for index, q_value in enumerate(correct_pvalues):

            if q_value <= ALPHA:

                if enrichment_pval[index] <= ALPHA:

                    Enrichement += 1
                    print(func_type, "Enrichment: ", genes[index])

                elif depletion_pval[index] <= ALPHA:

                    Depletion += 1
                    print(func_type, "Depletion: ", genes[index])
        
            else: 
                Neither += 1
                print(func_type, "Neither: ", genes[index])
            
        all_individual_sites[func_type]["Enrichment"] = Enrichement
        all_individual_sites[func_type]["Depletion"] = Depletion
        all_individual_sites[func_type]["Neither"] = Neither

    return all_individual_sites
    
if __name__ == "__main__":

    Enrichment, Depletion, Neither = main_question_correction()
    
    all_individual_sites = sub_main_correction()

    frequency_table = np.empty((8, 4))
    rows = []
    cols = ["Enrichment", "Depletion", "Neither", "Total"]
    
    for i, func_type in enumerate(all_individual_sites):

        rows.append(func_type)

        indiv_e = all_individual_sites[func_type]["Enrichment"]
        indiv_d = all_individual_sites[func_type]["Depletion"]
        indiv_n = all_individual_sites[func_type]["Neither"]

        frequency_table[i, 0] = indiv_e
        frequency_table[i, 1] = indiv_d
        frequency_table[i, 2] = indiv_n
        frequency_table[i, 3] = indiv_e + indiv_d + indiv_n

    rows.append("Full")

    frequency_table[i + 1, 0] = Enrichment
    frequency_table[i + 1, 1] = Depletion
    frequency_table[i + 1, 2] = Neither
    frequency_table[i + 1, 3] = Enrichment + Depletion + Neither

    import matplotlib.pyplot as plt

    fig, (ax0) = plt.subplots(nrows=1, ncols=1, figsize=(13,4.3))

    table = ax0.table(cellText=frequency_table, cellLoc="center", rowLabels=rows, colLabels=cols, loc="center")
    ax0.set_title(label="Frequency Table for Yeast Non-Covalent Lassos (corrected at 0.05) without Knots",  y = 0.8)
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    ax0.title.set_size(12)
    ax0.axis("off")

    fig.tight_layout(pad=1.2)
    plt.savefig("final_yeast_corrected", bbox_inches = "tight")


