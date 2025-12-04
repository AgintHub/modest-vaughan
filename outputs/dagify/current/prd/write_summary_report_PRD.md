# write_summary_report PRD

## Description
Compose a concise report summarizing methodology, experiments, results, and key conclusions about CLIFF.


## Implementation Plan

### 1. Load the markdown table output (`markdown_table`) from the `generate_comparative_results_table` node and store it as a raw string for later insertion into the Results section.

| Category | Details |
| --- | --- |
| **Reason** | The comparative table is the core quantitative evidence for CLIFF's superiority and must be reproduced verbatim in the report. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Read the `markdown_table` field from the parent node's JSON payload, verify that it contains a valid markdown table (e.g., starts with `|`), and assign it to a variable `comparative_table`. |

### 2. Load the filepaths (`accuracy_plot_filepath` and `forgetting_curve_filepath`) and captions (`accuracy_plot_caption`, `forgetting_curve_caption`) from the `produce_visualizations` node.

| Category | Details |
| --- | --- |
| **Reason** | Figures provide visual reinforcement of the numerical trends and are required for the Results section. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Extract the four string fields, check that the paths exist on the filesystem, and copy the images into a `figures/` sub‑directory of the report output folder. |

### 3. Compose the Abstract by summarizing (i) the problem of continual learning for 2‑D material classification, (ii) the CLIFF framework, (iii) key quantitative gains (e.g., +X% overall accuracy, -Y% forgetting), and (iv) the broader impact.

| Category | Details |
| --- | --- |
| **Reason** | The abstract must be self‑contained and give readers a rapid understanding of contributions. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Use template strings with placeholders filled from the metrics in `overall_accuracies` and `average_forgettings` (parent node outputs) and concise language. |

### 4. Write the Introduction by reviewing prior work on continual learning and prompt‑based adaptation, stating the research gap, and motivating CLIFF's design choices (frozen backbone + prompt pool + delta head).

| Category | Details |
| --- | --- |
| **Reason** | Sets the context and justifies why the proposed method matters. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Combine domain‑specific literature references (hard‑coded or configurable) with bullet‑point rationale; no external data needed. |

### 5. Generate the Method section using the design specifications from `design_backbone_and_base_head`, `implement_prompt_pool_structure`, `implement_cosine_similarity_gate`, `implement_delta_head`, and `configure_training_hyperparameters` nodes. Enumerate architecture, training schedule, replay buffer, and distillation loss.

| Category | Details |
| --- | --- |
| **Reason** | Readers need a reproducible description of the full CLIFF pipeline. |
| **Impact** | HIGH |
| **Complexity** | HIGH |
| **Method** | Iterate over each referenced node, extract key fields (e.g., `backbone_architecture`, `prompt_dimension`, `loss_expression`), and format them into subsections with code snippets where appropriate. |

### 6. Create the Experiments section describing dataset collection (`collect_reference_material_dataset`, `collect_new_material_datasets`), preprocessing (`preprocess_images`), splitting (`split_datasets`), and evaluation metrics (accuracy, forgetting). Include a concise table summarizing dataset sizes and split ratios.

| Category | Details |
| --- | --- |
| **Reason** | Provides transparency on experimental rigor and reproducibility. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Pull dataset statistics from `collect_*` nodes if available, otherwise synthesize a summary based on typical values; embed a markdown table manually. |

### 7. Populate the Results section with: (a) the `comparative_table` markdown, (b) the two figures inserted via standard Markdown image syntax (`![](figures/accuracy_plot.png)`), using the captions from the visualization node, and (c) a narrative interpretation of the numbers (e.g., percentage improvements, statistical significance if available).

| Category | Details |
| --- | --- |
| **Reason** | Directly presents the empirical evidence and ties it back to the research questions. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | String‑concatenate the table, then add newline, then embed images with captions; parse numeric values from `overall_accuracies` and `average_forgettings` arrays to compute delta values for the narrative. |

### 8. Draft the Discussion by analyzing why CLIFF outperforms baselines: effect of prompt pool gating, reduced forgetting via replay‑distillation, trade‑offs of frozen backbone, and potential failure modes. Cite specific rows of the comparative table to back claims.

| Category | Details |
| --- | --- |
| **Reason** | Critical reflection demonstrates deep understanding and guides future work. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Iterate over each model row, compare per‑material accuracies, and articulate observations; add bullet points for limitations and open questions. |

### 9. Write the Conclusion summarizing the main achievements (e.g., X% accuracy gain, Y% forgetting reduction), reiterating the significance for continual learning in materials science, and outlining concrete next steps (e.g., scaling to more materials, exploring alternative prompt encodings).

| Category | Details |
| --- | --- |
| **Reason** | Ends the report with a clear take‑away and roadmap. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Reuse key numbers already mentioned; keep the paragraph concise (3‑4 sentences). |

### 10. Assemble all section strings (`abstract`, `introduction`, `method`, `experiments`, `results`, `discussion`, `conclusion`) into a single JSON object matching the defined output structure and return it from the node.

| Category | Details |
| --- | --- |
| **Reason** | Conforms to the node's contract and makes downstream consumption trivial. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Create a Python dictionary with keys exactly as listed in `output_structure` and serialize it; ensure no stray newline characters break the JSON formatting. |
