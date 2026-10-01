"""Field affine tests: average all observed orders, with no hidden ordering."""
from decimal import Decimal,ROUND_FLOOR
import numpy as np
from quota_arithmetic import I,dot,calc
from empbern_quota import averaged_block_logs

def affine_rows(full,lo,hi,zz,arm,lam,weights):
    total=sum((I(x) for x in full.samp_wgt),I(0));C=[];intercepts=[];receipts=[]
    selected=full[full.arm==arm]
    for score_index,z in enumerate(zz):
        intercept={-1:Decimal(0),1:Decimal(0)};blocks=[]
        for block,part in selected.groupby('block'):
            lower=[];upper=[]
            for vid,village in part.groupby('vid'):
                index=village.index.to_numpy()
                lower.append(dot(village.samp_wgt,z[lo[index].astype(int)]))
                upper.append(dot(village.samp_wgt,z[hi[index].astype(int)]))
            logs,detail=averaged_block_logs(weights[int(block)],len(lower),lam,lower,upper)
            for sign in [-1,1]:intercept[sign]=calc(ROUND_FLOOR,lambda:intercept[sign]+logs[sign])
            blocks.append({'block':int(block),'log_intercepts_lower':{str(sign):str(logs[sign]) for sign in [-1,1]},**detail})
        plus=[(-I(lam)*total*I(value)).lower_float() if value else 0. for value in z]
        minus=[(I(lam)*total*I(value)).lower_float() if value else 0. for value in z]
        C.extend([plus,minus]);intercepts.extend([I(intercept[1]).lower_float(),I(intercept[-1]).lower_float()])
        receipts.append({'score_index':score_index,'blocks':blocks})
    return np.array(C),np.array(intercepts),receipts
