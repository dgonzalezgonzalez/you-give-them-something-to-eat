version 19
clear all
set more off
capture log close
log using "output/stata-validation.log", text replace
import delimited "data/input/households.csv", clear varnames(1) case(preserve)
preserve
keep if round==1 & eligible==1
keep hhid dietarydiversity
rename dietarydiversity baseline_diet
tempfile base
save `base'
restore
keep if round==2 & eligible==1 & sample_panel==1
merge 1:1 hhid using `base', keep(master match) nogen
gen baseline_missing=missing(baseline_diet)
drop if missing(dietarydiversity)
recast double baseline_diet
bysort block: egen double sum_diet=total(baseline_diet*samp_wgt)
bysort block: egen double sum_weight=total(samp_wgt*(!missing(baseline_diet)))
replace baseline_diet=sum_diet/sum_weight if baseline_missing
reg dietarydiversity treat_GK treat_GD_lower treat_GD_mid treat_GD_upper treat_GD_huge baseline_diet baseline_missing i.block [aw=samp_wgt], vce(cluster vid)
file open result using "output/stata-validation.csv", write replace
file write result "arm,estimate,se" _n
foreach a in GK GD_lower GD_mid GD_upper GD_huge {
    file write result "`a'," %21.15g (_b[treat_`a']) "," %21.15g (_se[treat_`a']) _n
}
file close result
log close
