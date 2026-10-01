# Small public input byte views

Each text part is at most 12,001 bytes. Reassembly instructions and original/part SHA256 values are in manifest.json. This can support readers whose interfaces cannot retrieve large CSVs. All source observations were already public in data/input under CC BY 4.0.

Verify: `python code/public_review_bytes.py --verify`. Reconstruct into a separate destination: `python code/public_review_bytes.py --reconstruct-to tmp/reassembled-inputs`. The script never replaces data/input. These inspection views are outside the default numerical master and do not prove independent replication.
