# generate_comparative_results_table PRD

## Description
Create a markdown table comparing CLIFF, naive fine‑tuning, and prompt‑only baselines across all metrics.


## Implementation Plan

### 1. Load the JSON summary produced by the parent node `compute_accuracy_and_forgetting_metrics` (field `summary_json`) and deserialize it into a native Python dictionary.

| Category | Details |
| --- | --- |
| **Reason** | Deserialization is required to access individual numeric fields (mean accuracies, forgetting values, per‑material lists) for further processing. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use `json.loads()`; add error handling for malformed JSON; raise a clear exception if required keys are missing. |

### 2. Extract the ordered list of model identifiers from the parent output field `models` and map them to the canonical display names required for the table (e.g., replace "CLIFF" → "CLIFF", "NaiveFineTuning" → "Naive Fine‑Tuning", "PromptBaseline" → "Prompt‑Only").

| Category | Details |
| --- | --- |
| **Reason** | The downstream consumer expects human‑readable model names, not internal identifiers. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Create a static mapping dictionary; apply it with a list comprehension; validate that all three expected models are present. |

### 3. Collect overall accuracies: read `cliff_mean_accuracy`, `naive_fine_tuning_mean_accuracy`, and `prompt_baseline_mean_accuracy` from the deserialized dict and assemble them into the list `overall_accuracies` ordered according to `model_names`.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the `overall_accuracies` output aligns with the row order of the markdown table. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Map each model name to its corresponding mean field; cast to `float` with rounding to 4 decimal places for readability. |

### 4. Collect average forgetting values: read `cliff_forgetting`, `naive_fine_tuning_forgetting`, and `prompt_baseline_forgetting` and assemble them into `average_forgettings` in the same order as `model_names`.

| Category | Details |
| --- | --- |
| **Reason** | Forgetting is a key comparative metric; consistent ordering is essential for downstream analysis. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Same approach as the previous bullet; ensure values are non‑negative; if a value is missing, insert `None` and later replace with "N/A" in the markdown. |

### 5. Extract per‑material accuracy lists (`cliff_per_material_accuracy`, `naive_fine_tuning_per_material_accuracy`, `prompt_baseline_per_material_accuracy`) and the global `materials` list; truncate each per‑material list to at most three entries (as required by the prompt).

| Category | Details |
| --- | --- |
| **Reason** | The markdown table column must list up to three material accuracies; truncation prevents overflow and keeps the table readable. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Slice each list with `[:3]`; keep the same ordering of materials as provided; if fewer than three materials exist, fill missing slots with `"-"` placeholders. |

### 6. Flatten the truncated per‑material accuracies into a single list `per_material_accuracies` ordered by model then by material.

| Category | Details |
| --- | --- |
| **Reason** | Matches the output schema definition and allows downstream nodes to index accuracies without needing nested structures. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Iterate over the three model‑specific lists and extend a master list; ensure each entry is a `float` rounded to 2‑3 decimal places. |

### 7. Construct the markdown table string:
```
| Model | Overall Accuracy | Avg. Forgetting | Material‑1 | Material‑2 | Material‑3 |
|-------|------------------|----------------|-----------|-----------|-----------|
| CLIFF | 0.92 | 0.03 | 0.94 | 0.91 | 0.92 |
| Naive Fine‑Tuning | 0.85 | 0.15 | 0.88 | 0.83 | 0.84 |
| Prompt‑Only | 0.88 | 0.10 | 0.90 | 0.86 | 0.88 |
```
Populate each cell using the previously assembled lists, inserting "-" where a material slot is empty.

| Category | Details |
| --- | --- |
| **Reason** | A well‑formatted markdown table is the primary deliverable for human readers and for inclusion in the final report. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use Python string templating (e.g., f‑strings or `str.format`); loop over `model_names` to generate rows; ensure proper escaping of pipe characters; validate that each row has exactly six columns. |

### 8. Validate the final outputs:
- `markdown_table` must be a non‑empty string containing at least three rows (header + separator + data rows).
- `model_names`, `overall_accuracies`, and `average_forgettings` must each have length 3.
- `per_material_accuracies` length must be ≤ 9 (3 models × 3 materials).
If any validation fails, raise an informative exception.

| Category | Details |
| --- | --- |
| **Reason** | Early detection of mismatched data prevents downstream failures and ensures contract compliance. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Implement a helper `assert` block; log the mismatched dimensions; include a fallback that inserts placeholder values rather than crashing for production robustness. |

### 9. Return a dictionary matching the declared `output_structure` with keys: `markdown_table`, `model_names`, `overall_accuracies`, `average_forgettings`, `per_material_accuracies`.

| Category | Details |
| --- | --- |
| **Reason** | Conforms to the typed node contract; downstream nodes (`write_summary_report`) will consume these fields directly. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Create a plain Python dict; ensure each value adheres to its PrimitiveType (e.g., cast lists to `list`, floats to `float`). |

### 10. Add logging statements at DEBUG level before and after each major transformation (loading JSON, extracting metrics, building table) to aid troubleshooting and reproducibility.

| Category | Details |
| --- | --- |
| **Reason** | Transparent logs simplify debugging in complex DAG executions and satisfy audit requirements. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use Python `logging` module; include node name in log messages; optionally expose a `verbose` flag. |
