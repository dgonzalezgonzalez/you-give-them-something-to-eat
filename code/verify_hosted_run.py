"""Cold full-master execution on a separately provisioned hosted runner.

This is author-initiated continuous integration, not independent scientific
replication or a journal data-editor certification. Runtime metadata, PNG byte
identity and PDF byte/text identity across TeX distributions are not asserted.
The generated PDF and all actual cold-run outputs are retained as artifacts.
"""
from pathlib import Path
import hashlib,json,os,platform,shutil,subprocess,sys
import pandas as pd
import pymupdf
from decimal import Decimal,ROUND_CEILING

root=Path(__file__).resolve().parents[1]
dest=root/'tmp/hosted-cold'
dest.mkdir(parents=True,exist_ok=False)
for folder in ['code','data/input']:
    shutil.copytree(root/folder,dest/folder,ignore=shutil.ignore_patterns('__pycache__'))
(dest/'paper').mkdir()
for file in ['run.py','requirements.txt','paper/paper.tex']:
    shutil.copy2(root/file,dest/file)
checks={};execution_error=None
try:
    subprocess.run([sys.executable,str(dest/'run.py'),'--pdf'],check=True,cwd=dest)
    for file in sorted((root/'output').glob('*.csv')):
        if file.name=='stata-validation.csv':continue
        a=pd.read_csv(file);b=pd.read_csv(dest/'output'/file.name)
        if file.name=='designed_decisions.csv':
            # Baseline floating scale search can vary by a few ulps across
            # libm/BLAS platforms. Its maximum realized rational-rounding
            # diagnostic is small and sensitive to those candidates. Each
            # draw still checks its exact decision certificate. Compare this
            # one diagnostic at a declared conservative display resolution,
            # and require the analytic universal rounding ceiling separately.
            column='maximum_rational_policy_rounding_bound'
            denominator=json.loads((root/'output/designed-decisions.json').read_text())['decision_probability_denominator']
            ceiling=Decimal(1)/Decimal(2*denominator)
            def rounding_values(frame):
                return [Decimal.from_float(float(x)) for x in frame[column]]
            av,bv=rounding_values(a),rounding_values(b)
            checks['designed_rounding_universal_ceiling']=all(x.is_finite() and 0<=x<=ceiling for x in av+bv)
            checks['designed_rounding_upward_1e-9_display']=len(av)==len(bv) and all(x.quantize(Decimal('1e-9'),rounding=ROUND_CEILING)==y.quantize(Decimal('1e-9'),rounding=ROUND_CEILING) for x,y in zip(av,bv))
            a=a.drop(columns=column);b=b.drop(columns=column)
        pd.testing.assert_frame_equal(a,b,check_exact=False,rtol=1e-10,atol=1e-12)
        checks['output/'+file.name]=True
    for file in sorted((root/'output/tables').glob('*.tex')):
        relative=file.relative_to(root)
        checks[relative.as_posix()]=file.read_text(encoding='utf8')==(dest/relative).read_text(encoding='utf8')
    for relative in ['output/policies.json','output/numbers.json','output/revision-numbers.json','output/decision-numbers.json','output/distribution-numbers.json','output/quota-comparison-numbers.json','output/community-numbers.json','paper/results.tex','paper/revision-results.tex','paper/decision-results.tex','paper/distribution-results.tex','paper/quota-comparison-results.tex','paper/community-results.tex','docs/output-map.csv']:
        checks[relative]=(root/relative).read_text(encoding='utf8')==(dest/relative).read_text(encoding='utf8')
    for leaf in ['quota-enclosure-validation.json','quota-dp-validation.json','empbern-quota-validation.json','designed-decision-validation.json','regional-minimax-validation.json','quota-allocation-validation.json','community-validation.json']:
        actual=json.loads((dest/'output'/leaf).read_text())
        checks['cold_'+leaf]=actual['all_passed'] and bool(actual['checks']) and all(actual['checks'].values())
    baseline=json.loads((root/'output/quota-loss-bound.json').read_text())
    cold=json.loads((dest/'output/quota-loss-bound.json').read_text())
    checks['quota_event_and_outward_constants']=all(baseline[key]==cold[key] for key in ['event_terms','event_cap','transformations','models'])
    community=json.loads((root/'output/community-decision.json').read_text())
    cold_community=json.loads((dest/'output/community-decision.json').read_text())
    checks['community_fixed_events_and_menus']=all(community[key]==cold_community[key] for key in ['family_size','alpha','quota_mean_test_family','quota_mean_test_cap','input_hashes','baseline_eligible_weight_share_exact','menus'])
    def community_display(row):
        from fractions import Fraction
        from decimal import localcontext,ROUND_FLOOR
        with localcontext() as ctx:
            ctx.prec=100
            f=Fraction(row['exact_regional_lower']);lower=(Decimal(f.numerator)/Decimal(f.denominator)).quantize(Decimal('.001'),rounding=ROUND_FLOOR)
            f=Fraction(row['exact_proposal_upper']);upper=(Decimal(f.numerator)/Decimal(f.denominator)).quantize(Decimal('.001'),rounding=ROUND_CEILING)
        return lower,upper
    checks['community_regional_outward_displays']=len(community['decisions'])==len(cold_community['decisions'])==12 and all(
        (a['method'],a['cost_convention'],a['population'],a['theta_interval'])==(b['method'],b['cost_convention'],b['population'],b['theta_interval']) and community_display(a)==community_display(b)
        for a,b in zip(community['decisions'],cold_community['decisions']))
    checks['quota_display_bounds']=all(a['reported_conservative_loss_upper']==b['reported_conservative_loss_upper'] and b['conditional_loss_upper']<=float(a['reported_conservative_loss_upper']) for a,b in zip(baseline['scenarios'],cold['scenarios']))
    actual=json.loads((dest/'output/quota-benchmark-validation.json').read_text())
    checks['cold_classical_moment_validation']=actual['all_passed'] and actual['passed']==actual['checks'] and actual['independent_moment_inequalities']>0
    actual=json.loads((dest/'output/quota-benchmark-receipt-validation.json').read_text())
    checks['cold_benchmark_receipt_validation']=actual['all_passed'] and bool(actual['checks']) and all(actual['checks'].values())
    baseline_bench=json.loads((root/'output/quota-benchmarks.json').read_text())
    cold_bench=json.loads((dest/'output/quota-benchmarks.json').read_text())
    checks['benchmark_upper_display_thresholds']=all(
        a['moment_method']==b['moment_method'] and a['event']==b['event'] and a['bin_floors']==b['bin_floors'] and a['objective']==b['objective'] and
        b['fixed_proposal_loss_upper']<=float(Decimal.from_float(a['fixed_proposal_loss_upper']).quantize(Decimal('.001'),rounding=ROUND_CEILING))
        for a,b in zip(baseline_bench['rows'],cold_bench['rows'])) and len(baseline_bench['rows'])==len(cold_bench['rows'])
    with pymupdf.open(dest/'paper/paper.pdf') as pdf:
        pages=len(pdf)
        pdf_text='\n'.join(page.get_text() for page in pdf)
    checks['compiled_pdf_title']='You give them something to eat:' in pdf_text
    checks['compiled_pdf_author']='Diego' in pdf_text and 'Gonz' in pdf_text
except Exception as error:
    execution_error=f'{type(error).__name__}: {error}'
    pages=None
master_path=dest/'output/master_run.json'
receipt={'scope':'Author-initiated full public microdata-to-manuscript run in a new GitHub-hosted Ubuntu environment; not an independent scientific replicator or journal certification.',
         'source_commit':os.environ.get('GITHUB_SHA') or subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
         'workflow_run_url':f"https://github.com/{os.environ.get('GITHUB_REPOSITORY','')}/actions/runs/{os.environ.get('GITHUB_RUN_ID','')}" if os.environ.get('GITHUB_RUN_ID') else None,
         'python':platform.python_version(),'platform':platform.platform(),
         'requirements_lock_sha256':hashlib.sha256((root/'requirements-lock.txt').read_bytes()).hexdigest(),
         'checks':checks,'all_passed':execution_error is None and bool(checks) and all(checks.values()),
         'execution_error':execution_error,'pdf_pages':pages,
         'master':json.loads(master_path.read_text()) if master_path.exists() else None,
         'comparison_scope':'CSV rtol=1e-10/atol=1e-12, except the maximum realized rational-policy rounding diagnostic: both platforms must satisfy the analytic 1/(2*denominator) ceiling and have identical upward 1e-9 displays. Per-draw exact decision certificates remain mandatory. Exact generated table/macro/definition text; exact quota event/model constants, cold interval and dual validation, equal outward display thresholds with actual upper bounds below them; successful cold PDF compilation with title/author. Solver tangent candidates, runtime metadata, PNG/PDF bytes and cross-platform PDF-text identity are excluded.'}
(root/'output').mkdir(exist_ok=True)
source_delivery_error=None
if receipt['all_passed']:
    try:
        # Transport the unchanged public ninth freeze through the EXISTING
        # artifact upload path. This is separate from the 130 scientific
        # comparisons above; it changes no scientific input or computation.
        subprocess.run([sys.executable,str(root/'docs/referee/build_public_frozen_bundle.py')],cwd=root,check=True)
        bundle_dir=root/'tmp/public-review-v0.9.0'
        bundle_manifest=json.loads((bundle_dir/'manifest.json').read_text(encoding='utf8'))
        shutil.copy2(bundle_dir/'source.zip',dest/'output/public-frozen-source-v0.9.0.zip')
        shutil.copy2(bundle_dir/'manifest.json',dest/'output/public-frozen-source-v0.9.0.json')
        receipt['public_frozen_source_delivery']={
            'status':'packaged','scope':'Separate delivery of already-public frozen v0.9.0, not another scientific comparison or new referee execution.',
            'manifest':bundle_manifest,'artifact_inner_zip':'output/public-frozen-source-v0.9.0.zip'}
    except Exception as error:
        source_delivery_error=f'{type(error).__name__}: {error}'
        receipt['public_frozen_source_delivery']={'status':'failed','error':source_delivery_error}
(root/'output/hosted-run.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
print(json.dumps(receipt,indent=2))
if not receipt['all_passed']:raise RuntimeError('Hosted reproduction failed; preserve the actual receipt and logs.')
if source_delivery_error:raise RuntimeError('Scientific comparisons passed but public frozen-source delivery failed; preserve the actual receipt and logs.')
