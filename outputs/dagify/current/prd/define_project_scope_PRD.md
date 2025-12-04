# define_project_scope PRD

## Description
State the precise research goals, performance metrics, and constraints for the CLIFF framework.


## Implementation Plan

### 1. Gather domain‑specific requirements by reviewing recent literature on optical‑microscopy flake‑layer classification and consulting project stakeholders to capture the overarching research intent.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the scope reflects both state‑of‑the‑art capabilities and the actual needs of the research team. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Conduct a brief literature survey (e.g., 5‑7 recent papers), hold a 30‑minute stakeholder interview, and summarize key goals in a bullet list. |

### 2. Formulate a single‑sentence primary objective that explicitly mentions (a) continual learning, (b) classification of flake layers, and (c) the use of optical microscopy images.

| Category | Details |
| --- | --- |
| **Reason** | A concise, well‑crafted objective provides a clear north‑star for all downstream development. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Combine the three required elements using the template: "Develop a continual‑learning framework that accurately classifies the number of layers in 2D material flakes from optical‑microscopy images while preserving knowledge of previously learned materials." |

### 3. Enumerate evaluation metrics that will quantitatively measure both instantaneous performance and knowledge retention, such as top‑1 accuracy per material, mean accuracy across all materials, forgetting (accuracy drop on earlier materials), and optional secondary metrics like macro‑F1 or inference latency.

| Category | Details |
| --- | --- |
| **Reason** | A comprehensive metric set enables rigorous assessment of the continual‑learning trade‑off between plasticity and stability. |
| **Impact** | MEDIUM |
| **Complexity** | MEDIUM |
| **Method** | Create a list of strings: ["top‑1 accuracy", "mean accuracy", "forgetting", "macro‑F1 (optional)", "inference latency (optional)"] and justify each choice in a comment. |

### 4. Identify high‑level system constraints that must be respected throughout the project, including: (1) backbone network weights are frozen after pre‑training, (2) prompt vectors and delta head are the only trainable components during incremental phases, (3) memory replay buffer size ≤ 5 % of total training samples, (4) maximum GPU memory footprint ≤ 12 GB, and (5) data privacy compliance (no external data sharing).

| Category | Details |
| --- | --- |
| **Reason** | Explicit constraints prevent scope creep and guide architectural decisions such as model size and replay strategy. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Write each constraint as a concise string and optionally prefix with a category tag (e.g., "[Model] frozen backbone"). |

### 5. Populate the three output fields (primary_objective, evaluation_metrics, high_level_constraints) using the strings and lists created in the previous steps, ensuring they conform to the declared PrimitiveTypes.

| Category | Details |
| --- | --- |
| **Reason** | Transforms the narrative scope into the machine‑readable JSON structure required by downstream nodes. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Assign: primary_objective = <sentence from bullet 2>; evaluation_metrics = <list from bullet 3>; high_level_constraints = <list from bullet 4>. |

### 6. Validate the constructed output against the schema: check that primary_objective is a non‑empty string, evaluation_metrics is a non‑empty list of strings, and high_level_constraints is a non‑empty list of strings; raise a clear error if any check fails.

| Category | Details |
| --- | --- |
| **Reason** | Automatic validation catches formatting bugs early, avoiding downstream failures. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Implement a simple assert‑style function or use a JSON schema validator (e.g., jsonschema.validate) with the defined output_structure. |

### 7. Return the final JSON object containing the three fields, ready to be consumed by the downstream node `design_backbone_and_base_head`.

| Category | Details |
| --- | --- |
| **Reason** | Completes the node’s responsibility and provides a clean hand‑off to the next stage of the workflow. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Serialize the Python dict to JSON (or directly output the dict in the system) and ensure no extra fields are present. |
