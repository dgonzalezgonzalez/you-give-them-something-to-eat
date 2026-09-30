"""Block linearization for assignment-weighted ratio means.

Exploratory second-referee repair. Conditional exchangeability within released
blocks/counts and independence across blocks are assumptions, not recovered
randomization code. This module alone does not establish finite-sample coverage.
"""
import numpy as np


def hajek_block(sample, values, assignment, arms):
    """Preserve all cross-arm score dependence within assignment blocks.

    Ratios use the same positive weights as the earlier village estimator.
    Aggregation occurs before covariance estimation. B/(B-1) corrects a
    common block covariance, not six separate arm covariances. Fixed-block
    expected-score heterogeneity gives an asymptotic positive-semidefinite
    excess covariance under the stated independent-block design assumptions.
    """
    blocks=sorted(sample.block.unique())
    block_index={b:i for i,b in enumerate(blocks)}
    B=len(blocks)
    if B<2:
        raise ValueError('At least two independent assignment blocks required')
    values=np.asarray(values,dtype=float)
    means=np.zeros(len(arms))
    influence=np.zeros((B,len(arms)))
    denominators=np.zeros(len(arms))
    for a_index,arm in enumerate(arms):
        keep=(sample.arm==arm).to_numpy()&np.isfinite(values)
        selected=sample.loc[keep]
        if selected.empty:
            raise ValueError(f'No observed support for {arm}')
        probabilities=selected.block.map(assignment[arm]).to_numpy(dtype=float)
        if not np.all((probabilities>0)&(probabilities<=1)):
            raise ValueError('Invalid conditional assignment probability')
        weights=selected.samp_wgt.to_numpy(dtype=float)/probabilities
        denominators[a_index]=weights.sum()
        means[a_index]=np.average(values[keep],weights=weights)
        scores=weights*(values[keep]-means[a_index])/denominators[a_index]
        index=selected.block.map(block_index).to_numpy(dtype=int)
        np.add.at(influence[:,a_index],index,scores)
    assert np.allclose(influence.sum(axis=0),0.,atol=1e-12)
    influence*=np.sqrt(B/(B-1))
    return means,influence,{'blocks':blocks,'denominators':denominators.tolist(),
                             'correction':B/(B-1),
                             'scope':'Independent-block ratio linearization; asymptotic conservative covariance under stated assumptions, not exact finite-sample inference'}


def referee_counterexample(blocks=22):
    """Exact 90-assignment enumeration of the referee's ten-village block."""
    outcome=np.array([4.]*5+[6.]*5)
    draws=np.array([(outcome[i],outcome[j]) for i in range(10) for j in range(10) if i!=j])
    covariance=np.cov(draws,rowvar=False,bias=True)/blocks
    c=np.array([1.,-1.])
    true_variance=float(c@covariance@c)
    independent_variance=float(np.trace(covariance))
    assert np.isclose(covariance[0,1],-1/(9*blocks))
    assert np.isclose(true_variance,20/(9*blocks))
    assert np.isclose(independent_variance/true_variance,.9)
    return {'blocks':blocks,'assignments_per_block':len(draws),
            'true_difference_variance':true_variance,
            'expected_independent_arm_estimate':independent_variance,
            'independent_to_true_ratio':independent_variance/true_variance,
            'expected_block_covariance_estimate':covariance.tolist(),
            'expected_block_difference_variance':true_variance}


def bounded_hajek_outer(sample, values, assignment, arms, baseline_frame,
                        value_range, *, alpha=.05, multiplicity=1):
    """Finite conditional-assignment outer intervals by bounded sampling.

    Condition on fixed baseline weights and exchangeable quota assignment.
    For each arm, within-block sampling without replacement is bounded by
    the with-replacement exponential moment. Blocks are independent. An
    observed-outcome ratio targets the weighted potential-observation ratio;
    complete endpoint ratios target all fixed weighted baseline observations.
    This does not itself establish representativeness for unsampled households.
    """
    low,high=map(float,value_range)
    if not low<high or not 0<alpha<1 or multiplicity<1:
        raise ValueError('Invalid support, probability, or multiplicity')
    frame=baseline_frame.groupby(['block','vid']).samp_wgt.sum().reset_index()
    block_size=frame.groupby('block').vid.size()
    maximum_weight=frame.groupby('block').samp_wgt.max()
    values=np.asarray(values,dtype=float)
    means=[];lower=[];upper=[];proxies=[];denominators=[]
    for arm in arms:
        proxy=0.
        for block,size in block_size.items():
            probability=float(assignment[arm][block]);quota=probability*size
            if not np.isclose(quota,round(quota)) or quota<1:
                raise ValueError('Finite calculation requires positive integer conditional quotas')
            proxy+=round(quota)*(maximum_weight.loc[block]/probability)**2
        keep=(sample.arm==arm).to_numpy()&np.isfinite(values)
        selected=sample.loc[keep]
        weights=selected.samp_wgt.to_numpy()/selected.block.map(assignment[arm]).to_numpy()
        denominator=float(weights.sum());denominators.append(denominator);proxies.append(float(proxy))
        if not denominator:
            means.append(float('nan'));lower.append(low);upper.append(high)
            continue
        observed=values[keep]
        if np.any((observed<low-1e-12)|(observed>high+1e-12)):
            raise ValueError('Observed transformation outside declared support')
        mean=float(np.average(observed,weights=weights))
        radius=(high-low)*np.sqrt(.5*proxy*np.log(2*multiplicity/alpha))/denominator
        means.append(mean);lower.append(max(low,mean-radius));upper.append(min(high,mean+radius))
    return np.array(means),np.array(lower),np.array(upper),{
        'alpha':alpha,'primitive_family_size':multiplicity,
        'variance_proxy_by_arm':dict(zip(arms,proxies)),
        'realized_denominator_by_arm':dict(zip(arms,denominators)),
        'scope':'Finite conditional exchangeable-assignment bound for fixed weighted baseline sample; sampling-frame transport needs additional assumptions'}
