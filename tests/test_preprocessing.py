import json
from pathlib import Path

import nbformat
import numpy as np
import pytest


ROOT = Path(__file__).parents[1]
NOTEBOOKS = sorted((ROOT / "dnn-hmm").glob("*.ipynb"))


def notebook_source(path):
    notebook = nbformat.read(path, as_version=4)
    return "\n\n".join(cell.source for cell in notebook.cells if cell.cell_type == "code")


def definitions(path, names):
    namespace = {"np": np}
    notebook = nbformat.read(path, as_version=4)
    for cell in notebook.cells:
        if cell.cell_type != "code":
            continue
        if any(f"class {name}" in cell.source or f"def {name}" in cell.source for name in names):
            exec(compile(cell.source, str(path), "exec"), namespace)
    return [namespace[name] for name in names]


def test_notebooks_are_self_contained_and_compile():
    assert len(NOTEBOOKS) == 10
    assert not (ROOT / "src").exists()
    for path in NOTEBOOKS:
        notebook = nbformat.read(path, as_version=4)
        assert notebook.metadata["implementation"] == "self-contained"
        source = notebook_source(path)
        assert "wakeword_data" not in source
        assert 'root / "src"' not in source
        for index, cell in enumerate(notebook.cells):
            if cell.cell_type == "code":
                compile(cell.source, f"{path.name}:cell-{index}", "exec")


def test_saved_notebook_execution_has_no_errors():
    for path in NOTEBOOKS:
        notebook = nbformat.read(path, as_version=4)
        code_cells = [cell for cell in notebook.cells if cell.cell_type == "code" and cell.source.strip()]
        assert all(cell.execution_count is not None for cell in code_cells)
        errors = [output for cell in code_cells for output in cell.outputs if output.output_type == "error"]
        assert not errors


@pytest.fixture
def cfg():
    return json.loads((ROOT / "configs/preprocessing.json").read_text())


@pytest.mark.parametrize("chunk_size", [1, 157, 400, 1024])
def test_notebook_streaming_features_match_batch(cfg, chunk_size):
    LogMel, StreamingLogMel = definitions(NOTEBOOKS[6], ["LogMel", "StreamingLogMel"])
    signal = np.random.default_rng(1).normal(0, .1, 17219).astype(np.float32)
    extractor = LogMel(cfg)
    stream = StreamingLogMel(extractor)
    actual = np.concatenate([stream.push(signal[i:i+chunk_size])
                             for i in range(0, len(signal), chunk_size)])
    np.testing.assert_allclose(actual, extractor(signal), atol=1e-5, rtol=1e-6)
    assert len(stream.pending) < cfg["window_samples"]


def test_saved_split_and_augmentation_contracts(cfg):
    run = ROOT / "data/processed" / cfg["run_name"]
    originals = [json.loads(line) for line in (run / "05_standardized.jsonl").read_text().splitlines()]
    final = [json.loads(line) for line in (run / "09_final_manifest.jsonl").read_text().splitlines()]
    for field in ("speaker_id", "pcm_sha256"):
        groups = {split:{r[field] for r in originals if r["split"] == split}
                  for split in ("train", "validation", "test")}
        assert not groups["train"] & groups["validation"]
        assert not groups["train"] & groups["test"]
        assert not groups["validation"] & groups["test"]
    assert all(row["split"] == "train" for row in final if row["is_augmented"])


def test_saved_quality_report_passes(cfg):
    path = ROOT / "reports/preprocessing" / cfg["run_name"] / "qa.json"
    qa = json.loads(path.read_text())
    assert qa["preprocessing_pass"]
    assert all(qa["checks"].values())
    assert not qa["phonetic_hmm_training_ready"]
    assert not qa["production_evaluation_ready"]


def test_bootstrap_alignment_contract(cfg):
    run = ROOT / "data/processed" / cfg["run_name"]
    report = ROOT / "reports/preprocessing" / cfg["run_name"] / "bootstrap_alignment_qa.json"
    qa = json.loads(report.read_text())
    assert qa["bootstrap_alignment_pass"]
    assert all(qa["checks"].values())
    assert qa["label_status"] == "bootstrap_pseudo_label_not_human_verified"
    topology = json.loads((run / "10_alignments/hmm_topology.json").read_text())
    transition = np.asarray(topology["transition_probability"])
    mask = np.asarray(topology["allowed_transition_mask"], dtype=bool)
    np.testing.assert_allclose(transition.sum(axis=1), 1)
    assert np.all(transition[~mask] == 0)
