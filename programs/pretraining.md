# autoresearch pretraining program

This is the original training-focused autoresearch loop preserved for legacy use.

## Setup

To set up a new experiment, work with the user to:

1. **Agree on a run tag**: propose a tag based on today's date (e.g. `mar5`). The branch `autoresearch/<tag>` must not already exist.
2. **Create the branch**: `git checkout -b autoresearch/<tag>` from current master.
3. **Read the in-scope files**:
   - `README.md`
   - `prepare.py`
   - `train.py`
4. **Verify data exists**: check that `~/.cache/autoresearch/` contains data shards and a tokenizer. If not, tell the human to run `uv run prepare.py`.
5. **Initialize results.tsv**: create `results.tsv` with only the header row.
6. **Confirm and go**: once setup looks good, kick off the baseline.

## Experimentation

Each experiment runs on a single GPU. The training script runs for a fixed 5-minute wall-clock budget:

```bash
uv run train.py
```

**What you can do**

- Modify `train.py`.

**What you cannot do**

- Modify `prepare.py`.
- Install new packages or change dependencies.
- Change the evaluation harness in `prepare.py`.

The goal is to minimize `val_bpb`.

## Logging

Log every completed experiment to `results.tsv` using tab separation:

```text
commit	val_bpb	memory_gb	status	description
```

Use `status` values `keep`, `discard`, or `crash`.

## Loop

1. Inspect the current branch and commit.
2. Modify `train.py` with one experimental idea.
3. Commit the change.
4. Run `uv run train.py > run.log 2>&1`.
5. Read `val_bpb` and `peak_vram_mb` from `run.log`.
6. If the run crashed, inspect the tail of the log and decide whether the idea is salvageable.
7. Record the result in `results.tsv`.
8. Keep the commit only if `val_bpb` improved.
9. Otherwise revert and try a new idea.

Do not stop after one experiment unless the human interrupts you.
