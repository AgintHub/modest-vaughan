# produce_visualizations PRD

## Description
Generate plots (e.g., accuracy vs. material order, forgetting curve) to visually illustrate CLIFF’s advantages.


## Implementation Plan

### 1. Load the JSON summary produced by `compute_accuracy_and_forgetting_metrics` and deserialize it into a Python dict.

| Category | Details |
| --- | --- |
| **Reason** | All required numeric data (per‑material accuracies and forgetting metrics for each model) are stored in this JSON; parsing it is the first step toward any visualisation. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use `json.load(open(summary_path))`; validate that keys `materials`, `cliff_per_material_accuracy`, `naive_fine_tuning_per_material_accuracy`, `prompt_baseline_per_material_accuracy`, `cliff_forgetting`, `naive_fine_tuning_forgetting`, `prompt_baseline_forgetting` exist; raise a descriptive error if any are missing. |

### 2. Prepare a unified pandas DataFrame where each row corresponds to a material and columns contain the three methods' accuracies and forgetting values.

| Category | Details |
| --- | --- |
| **Reason** | A DataFrame provides convenient indexing for matplotlib plotting and ensures the material order is consistent across both figures. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | ```python
import pandas as pd
materials = data['materials']
df = pd.DataFrame({
    'Material': materials,
    'CLIFF': data['cliff_per_material_accuracy'],
    'NaiveFineTuning': data['naive_fine_tuning_per_material_accuracy'],
    'PromptBaseline': data['prompt_baseline_per_material_accuracy'],
    'CLIFF_Forgetting': [data['cliff_forgetting']]*len(materials),
    'Naive_Forgetting': [data['naive_fine_tuning_forgetting']]*len(materials),
    'Prompt_Forgetting': [data['prompt_baseline_forgetting']]*len(materials),
})
``` |

### 3. Create the *accuracy‑over‑material‑order* line plot using Matplotlib: X‑axis = material index (preserve the order from `materials`), Y‑axis = top‑1 accuracy, one line per method, with markers and a legend.

| Category | Details |
| --- | --- |
| **Reason** | A line plot directly shows how each method’s performance evolves as new materials are added, highlighting CLIFF’s stability and improvement. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | ```python
import matplotlib.pyplot as plt
plt.figure(figsize=(8,5))
for method, color in zip(['CLIFF','NaiveFineTuning','PromptBaseline'], ['tab:blue','tab:orange','tab:green']):
    plt.plot(df['Material'], df[method], marker='o', color=color, label=method)
plt.xlabel('Material (learning order)')
plt.ylabel('Top‑1 Accuracy (%)')
plt.title('Accuracy vs. Material Order for CLIFF and Baselines')
plt.ylim(0,100)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend()
accuracy_plot_path = 'figures/accuracy_vs_material.png'
plt.tight_layout()
plt.savefig(accuracy_plot_path, dpi=300)
plt.close()
``` |

### 4. Create the *forgetting magnitude* bar plot: X‑axis = material name, Y‑axis = forgetting value, three grouped bars per material for the three methods.

| Category | Details |
| --- | --- |
| **Reason** | Bar charts make it easy to compare the amount of performance degradation (forgetting) each method suffers on previously learned materials. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | ```python
import numpy as np
x = np.arange(len(df['Material']))
width = 0.25
plt.figure(figsize=(9,5))
plt.bar(x - width, df['CLIFF_Forgetting'], width, label='CLIFF', color='tab:blue')
plt.bar(x, df['Naive_Forgetting'], width, label='Naive Fine‑Tuning', color='tab:orange')
plt.bar(x + width, df['Prompt_Forgetting'], width, label='Prompt‑Only', color='tab:green')
plt.xlabel('Material')
plt.ylabel('Forgetting (Δ Accuracy %)')
plt.title('Forgetting Magnitude per Material')
plt.xticks(x, df['Material'], rotation=45)
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.5)
forgetting_plot_path = 'figures/forgetting_per_material.png'
plt.tight_layout()
plt.savefig(forgetting_plot_path, dpi=300)
plt.close()
``` |

### 5. Return the four output fields as a JSON‑compatible dict, ensuring absolute or project‑relative file paths are used.

| Category | Details |
| --- | --- |
| **Reason** | Downstream nodes (e.g., `write_summary_report`) expect explicit file locations and human‑readable captions to embed the figures into the final manuscript. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | ```python
output = {
    'accuracy_plot_filepath': accuracy_plot_path,
    'forgetting_curve_filepath': forgetting_plot_path,
    'accuracy_plot_caption': 'Figure X: Accuracy progression as materials are introduced sequentially. CLIFF maintains higher and more stable accuracy compared to naive fine‑tuning and prompt‑only baselines.',
    'forgetting_curve_caption': 'Figure Y: Forgetting magnitude for each material. CLIFF exhibits substantially lower forgetting than the baselines, confirming its continual‑learning capability.'
}
print(json.dumps(output, indent=2))
``` |

### 6. Add robust error handling: if the metrics JSON is missing any required key, raise a `KeyError` with a clear message; if the `figures/` directory does not exist, create it before saving.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the node fails gracefully and produces reproducible artefacts even when upstream steps change. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Use `os.makedirs('figures', exist_ok=True)`; wrap the plotting code in a `try/except` block that logs the exception and re‑raises it. |
