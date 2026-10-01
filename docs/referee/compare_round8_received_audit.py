"""Optional author-side comparison of archived genuine eighth referee outputs.
Run from repository root using the default scientific environment and full Git history.
Writes ignored tmp/round8-received-audit-comparison.json; never overwrites received artifacts.
This is not new referee execution or the default master.
"""
from pathlib import Path
import hashlib
import io
import json
import subprocess
import zipfile
import numpy as np
import pandas as pd

root = Path(__file__).resolve().parents[2]
source = 'aa8667ccde0e00d4c5aa182a89d88b4065a6dda6'
archive_path = root / 'docs/referee/round-8-received-audit/referee_round8_audit_v0.8.0.zip'
separate_summary_path = root / 'docs/referee/round-8-received-audit/summary.json'
dest = root / 'docs/referee/round-8-received-audit'
dest.mkdir(exist_ok=True)
archive_bytes = archive_path.read_bytes()
summary_bytes = separate_summary_path.read_bytes()
digest = lambda data: hashlib.sha256(data).hexdigest()
archive = zipfile.ZipFile(io.BytesIO(archive_bytes))
assert archive.testzip() is None
prefix = 'referee_round8/'
manifest = json.loads(archive.read(prefix + 'audit_file_hashes.json'))
hash_checks = [dict(file=name, expected_sha256=expected,
                    actual_sha256=digest(archive.read(prefix + name)),
                    matches=digest(archive.read(prefix + name)) == expected)
               for name, expected in manifest.items()]
assert all(row['matches'] for row in hash_checks)
assert archive.read(prefix + 'summary.json') == summary_bytes
summary = json.loads(summary_bytes)
assert summary['review_commit'] == '50c96dcea50b5aac25e5beb0912f54ff26e1b47b'
assert summary['scientific_source'] == source

def frozen_bytes(path):
    return subprocess.check_output(['git', 'show', source + ':' + path])
def original_csv(name):
    return pd.read_csv(io.BytesIO(frozen_bytes('output/' + name)))
def audit_csv(name):
    return pd.read_csv(io.BytesIO(archive.read(prefix + name)))

author_draws = original_csv('designed_decision_draws.csv').set_index(['case', 'repetition']).sort_index()
referee_draws = audit_csv('synthetic_draws.csv').set_index(['case', 'repetition']).sort_index()
assert author_draws.index.equals(referee_draws.index)
assert set(author_draws.columns) == set(referee_draws.columns)
draw_errors = {m: float(np.max(np.abs(author_draws[m].to_numpy() - referee_draws[m].to_numpy())))
               for m in sorted(author_draws.columns)}

author_results = pd.concat([original_csv('designed_decisions.csv'), original_csv('designed_decision_benchmarks.csv')]).set_index(['case', 'method']).sort_index()
referee_results = audit_csv('synthetic_results.csv').set_index(['case', 'method']).sort_index()
assert author_results.index.equals(referee_results.index)
result_errors = {k: float(np.max(np.abs(author_results[k].to_numpy() - referee_results[k].to_numpy())))
                 for k in ['mean_actual_regret', 'mc_standard_error']}

def canonical_pairs(frame):
    frame = frame.copy()
    flip = frame.first_method > frame.second_method
    first, second = frame.first_method.copy(), frame.second_method.copy()
    frame.loc[flip, 'first_method'] = second[flip]
    frame.loc[flip, 'second_method'] = first[flip]
    frame.loc[flip, 'mean_regret_difference'] *= -1
    return frame.set_index(['case', 'first_method', 'second_method']).sort_index()
author_pairs = canonical_pairs(original_csv('designed_decision_pairs.csv'))
referee_pairs = canonical_pairs(audit_csv('synthetic_pairs.csv'))
assert author_pairs.index.equals(referee_pairs.index)
pair_errors = {k: float(np.max(np.abs(author_pairs[k].to_numpy() - referee_pairs[k].to_numpy())))
               for k in ['mean_regret_difference', 'paired_mc_standard_error']}

confidence_rows = author_results[author_results.index.get_level_values('method').isin(summary['published_draw_spotcheck']['methods'] + ['harmonic_martingale', 'weight_sensitive_product', 'weight_sensitive_hybrid'])]
certificate_error = float(np.max(np.abs(confidence_rows.mean_certified_loss_upper.to_numpy() - referee_results.loc[confidence_rows.index, 'mean_certificate'].to_numpy())))
count_fields = [('certificates_at_most_010', 'count_le_010'),
                ('joint_mean_interval_coverage_count', 'coverage'),
                ('empty_region_fallback_count', 'fallbacks')]
count_mismatches = {a: int(np.sum(confidence_rows[a].to_numpy() != referee_results.loc[confidence_rows.index, b].to_numpy())) for a,b in count_fields}

receipt = {
    'status': 'actual_completed_eighth_audit_download_received_and_compared',
    'original_download_receipt': 'docs/referee/round-8-received-audit/receipt.json',
    'destination_chat_id': '6abd01e3-4184-83ed-9ff0-e9475053b958',
    'original_review_turn_id': 'ada88880-abe0-43d6-bbbe-46962582b1e4',
    'review_ref': 'v0.8.0', 'scientific_source': source,
    'recommendation': 'Reject at unchanged leading general-interest standard',
    'new_review': False, 'acceptance': False,
    'zip_path': 'docs/referee/round-8-received-audit/referee_round8_audit_v0.8.0.zip',
    'zip_actual_bytes': len(archive_bytes), 'zip_actual_sha256': digest(archive_bytes),
    'separate_summary_path': 'docs/referee/round-8-received-audit/summary.json',
    'separate_summary_actual_bytes': len(summary_bytes), 'separate_summary_actual_sha256': digest(summary_bytes),
    'summary_exact_named_archive_member_byte_equal': True,
    'archive_crc_check': True, 'archive_members': len(archive.namelist()),
    'supplied_manifest_checks': hash_checks,
    'supplied_manifest_checks_passed': len(hash_checks),
    'retrieval_scope': 'Downloaded by the original completed report’s browser controls. Browser event observation timed out, but exact expected Windows files were created at the click times and actually hashed/read. No local upload, private endpoint, alternate request or new review was used.',
    'retrieval_diagnostic_correction': 'An initial endswith(summary.json) test returned false because it matched both summary.json and synthetic_summary.json. Exact named member comparison passes. A viewer-only text reconstruction remained incomplete and was not used as the received artifact.',
    'author_archive_comparison': {
        'executed_by': 'Author-side Python 3.12 environment, comparing downloaded referee outputs to frozen eighth Git blobs; not new independent referee execution.',
        'draw_rows': len(author_draws), 'methods': len(author_draws.columns),
        'draw_values_compared': int(author_draws.size), 'maximum_draw_errors_by_method': draw_errors,
        'result_rows': len(author_results), 'result_errors': result_errors,
        'pair_rows': len(author_pairs), 'pair_errors': pair_errors,
        'pair_orientation': 'Canonical alphabetical method order; mean sign reversed when swapping methods, paired SE unchanged.',
        'confidence_rows': len(confidence_rows), 'maximum_mean_certificate_difference': certificate_error,
        'count_mismatches': count_mismatches,
        'frozen_canonical_costs_byte_equal': archive.read(prefix + 'costs.csv') == frozen_bytes('data/input/costs.csv'),
        'referee_programs_rerun_by_author': False,
    },
    'independent_referee_scope': summary['scope'],
    'original_referee_effect_pairs_checked': len(summary['effect_pairs_checked']),
    'original_referee_paired_draw_checks': 32,
    'original_referee_not_executed': summary['not_executed'],
    'exclusions': ['No completed supplemental eighth field report received.', 'No ninth assessment delivered.', 'No independent full field/master/Stata/PDF replication inferred.', 'Archive self-manifest matching is not third-party signed authenticity or scientific validation.', 'No simulated acceptance, real journal decision or DOI deposition.'],
}


(root / 'tmp/round8-received-audit-comparison.json').write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
print(json.dumps({k:v for k,v in receipt.items() if k in ['zip_actual_bytes','zip_actual_sha256','separate_summary_actual_sha256','supplied_manifest_checks_passed','author_archive_comparison']}))
