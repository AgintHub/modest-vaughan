# compute_accuracy_and_forgetting_metrics PRD

## Description
Aggregate performance numbers for CLIFF, naive fine‑tuning, and prompt‑only baselines, computing both accuracy and forgetting.


## Implementation Plan

### 1. Define a deterministic file‑naming convention for each model’s test‑result artefact (e.g., `results/<model_id>/test_metrics.json`) and store the path in a constant dictionary for lookup.

| Category | Details |
| --- | --- |
| **Reason** | A uniform naming scheme eliminates ambiguity when loading data from disparate training pipelines and enables reproducible aggregation. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use a Python dict: `RESULT_PATHS = {'CLIFF': 'results/CLIFF/test_metrics.json', 'NaiveFineTuning': 'results/NaiveFineTuning/test_metrics.json', 'PromptBaseline': 'results/PromptBaseline/test_metrics.json'}`. Validate existence with `os.path.exists` and raise a clear error if missing. |

### 2. Load per‑material test accuracies from each JSON file; each file must contain a mapping `material_name -> top1_accuracy` and a list `ordered_materials` that reflects the chronological learning order.

| Category | Details |
| --- | --- |
| **Reason** | Both the per‑material accuracy and the order of learning are required to compute forgetting correctly. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement a helper `load_metrics(path)` that returns `(ordered_materials, acc_dict)`. Use `json.load` and assert that all expected materials from `split_datasets.material_names` are present. |

### 3. Validate that the material order is identical across all three models; if not, re‑order each model’s accuracy list to match the canonical order from `split_datasets.material_names`.

| Category | Details |
| --- | --- |
| **Reason** | Consistent ordering guarantees that per‑material lists line up when constructing the final output structure. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Iterate over the canonical material list and build ordered accuracy lists: `cliff_acc = [cliff_dict[m] for m in canonical]` etc. Log a warning if any model is missing a material and insert `None` (later handled as `nan`). |

### 4. Compute mean accuracy for each model by averaging over the ordered per‑material accuracies, ignoring `nan` entries.

| Category | Details |
| --- | --- |
| **Reason** | Mean accuracy is a primary evaluation metric required by downstream nodes. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use `np.nanmean(np.array(acc_list, dtype=float))` from NumPy for robust handling of missing values. |

### 5. Implement the forgetting calculation: for a given model, iterate over the learning sequence; for each material *i* compute the drop `acc_i_before - acc_i_after` where `acc_i_before` is the accuracy recorded immediately after material *i* was first learned, and `acc_i_after` is the accuracy after the final material has been learned. Average these drops across all *i* to obtain the forgetting metric.

| Category | Details |
| --- | --- |
| **Reason** | Forgetting measures catastrophic loss of knowledge; the definition matches that of `evaluate_cliff_performance` and ensures comparability across baselines. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Assume each model’s JSON contains a list `cumulative_accuracies` where entry *k* is the accuracy on material *k* after training up to material *k*. Compute `drops = [cum_acc[i] - final_acc[i] for i in range(num_materials-1)]` and take the mean. If `cumulative_accuracies` is absent, fallback to the simple definition `mean(initial_accuracy - final_accuracy)`. |

### 6. Assemble the final output dictionary with keys matching the declared `output_structure` (models, materials, per‑material lists, means, forgettings). Convert the entire dict to a JSON string with `json.dumps(..., indent=2, sort_keys=True)` and store under `summary_json`.

| Category | Details |
| --- | --- |
| **Reason** | Downstream nodes expect a single JSON‑formatted string; sorting keys improves readability and deterministic output for testing. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | ```python
output = {
    "models": ["CLIFF", "NaiveFineTuning", "PromptBaseline"],
    "materials": canonical,
    "cliff_per_material_accuracy": cliff_acc,
    "naive_fine_tuning_per_material_accuracy": naive_acc,
    "prompt_baseline_per_material_accuracy": prompt_acc,
    "cliff_mean_accuracy": cliff_mean,
    "naive_fine_tuning_mean_accuracy": naive_mean,
    "prompt_baseline_mean_accuracy": prompt_mean,
    "cliff_forgetting": cliff_forget,
    "naive_fine_tuning_forgetting": naive_forget,
    "prompt_baseline_forgetting": prompt_forget,
    "summary_json": json.dumps(...)
}
``` |

### 7. Add robust error handling: wrap each I/O operation in try/except blocks, log missing files, malformed JSON, or mismatched material sets, and raise a custom `MetricsAggregationError` with a clear message.

| Category | Details |
| --- | --- |
| **Reason** | Early failure detection simplifies debugging of upstream pipelines and prevents silent propagation of incorrect metrics. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Create a small utility module `utils.py` with `load_json(path)` and `assert_materials_match(list1, list2)` functions. Use Python's `logging` module at INFO level for normal operation and ERROR level for failures. |

### 8. Write unit tests covering: (a) correct loading and ordering, (b) mean calculation with NaNs, (c) forgetting computation on a synthetic cumulative‑accuracy series, and (d) JSON output schema compliance.

| Category | Details |
| --- | --- |
| **Reason** | Automated testing guarantees that future changes to parent nodes or data formats do not break this aggregation step. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Use `pytest` with fixtures that generate temporary result JSON files. Validate that `compute_accuracy_and_forgetting_metrics()` returns a dict whose fields match the `output_structure` types. |

### 9. Document the function in a docstring that mirrors the node’s prompt, includes parameter descriptions (`result_paths`), return type (`dict`), and an example of the produced `summary_json`.

| Category | Details |
| --- | --- |
| **Reason** | Clear documentation aids downstream developers and ensures the function can be called programmatically without re‑reading the prompt. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Follow Google Python style guide for docstrings. |
