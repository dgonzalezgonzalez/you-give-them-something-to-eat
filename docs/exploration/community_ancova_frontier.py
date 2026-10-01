"""Alternative fitted frontier from exploratory observed-panel ANCOVA contrasts.

Within each stratum, the common control level cancels from policy rankings.
These curves have different estimands from the assignment-weighted ratios.
No missingness robustness or uncertainty interval for switches is asserted.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from community_cost_frontier import frontier,ARMS

ROOT=Path(__file__).resolve().parents[2]

def main():
    destination=ROOT/'docs/exploration'
    rows=pd.read_csv(destination/'community-ancova-pilot.csv')
    vertices=json.loads((ROOT/'output/policies.json').read_text())['vertices']
    policies={'Gikuriro':{'Gikuriro':1.},**vertices}
    large_share=vertices['Control+Large']['Large'];results=[]
    for baseline in [False,True]:
        means={}
        for g in [0,1]:
            contrasts=rows[(rows.eligible==g)&(rows.baseline_control==baseline)].set_index('policy').estimate
            gikuriro=float(contrasts['Control'])
            effects={'Control':0.,'Gikuriro':gikuriro,**{a:gikuriro-float(contrasts[a]) for a in ['Lower','Middle','Upper']},'Large':(gikuriro-float(contrasts['Control+Large']))/large_share}
            means[g]=np.array([effects[a] for a in ARMS])
        segments,_,_=frontier(policies,means)
        results.append({'baseline_diet_control':baseline,'frontier':segments})
    output={'scope':'Exploratory observed-panel ANCOVA point rankings with original eligible cost menu. Within-stratum policy contrasts cancel the common control level. Baseline/block WLS and village-CR1 inference are distinct from assignment-weighted ratio estimands and finite protection. Eligibility is baseline-defined; identified follow-up diets still select this sample. Theta is stipulated total welfare weight, not measured preferences. Switches have sampling and specification uncertainty; no full-target ranking, new externality or general-interest importance is established.','specifications':results}
    (destination/'community-ancova-frontier.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(output,indent=2))

if __name__=='__main__':main()
