# implement_cosine_similarity_gate PRD

## Description
Build a gate that selects and weights prompts based on cosine similarity between input features and prompt embeddings.


## Implementation Plan

### 1. Load the prompt pool metadata produced by `implement_prompt_pool_structure` (variable name, dimensionality D, list of material IDs, and the learnable tensor containing all prompt embeddings).

| Category | Details |
| --- | --- |
| **Reason** | The gate must have direct access to the raw prompt embeddings to compute similarity with the backbone output. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Import the prompt pool variable (e.g., `material_prompts`) from the model's state dictionary; ensure it is a tensor of shape (num_materials, D). |

### 2. During the forward pass, retrieve the backbone feature vector `f` for the current input image (shape: [D]), ensuring it is L2‑normalized before similarity computation.

| Category | Details |
| --- | --- |
| **Reason** | Cosine similarity requires both vectors to be unit‑norm; normalizing the backbone output eliminates scale bias. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Apply `f_norm = f / (torch.norm(f, p=2) + 1e-8)` using the same precision as the prompt embeddings. |

### 3. L2‑normalize each prompt embedding in the pool to obtain `P_norm` (shape: [num_materials, D]).

| Category | Details |
| --- | --- |
| **Reason** | Consistent normalization across prompts guarantees that the dot product equals cosine similarity. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Compute `P_norm = material_prompts / (torch.norm(material_prompts, dim=1, keepdim=True) + 1e-8)` once per training step or cache if static. |

### 4. Compute cosine similarity scores by taking the matrix‑vector product between `P_norm` and the normalized backbone vector `f_norm`: `scores = torch.matmul(P_norm, f_norm)` resulting in a 1‑D tensor of length `num_materials`.

| Category | Details |
| --- | --- |
| **Reason** | Matrix‑vector multiplication is highly efficient on GPUs and yields the exact cosine similarity for each prompt. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Use PyTorch/TF tensor ops; ensure dtype consistency (float32). Store the result as `similarity_scores`. |

### 5. Apply a temperature‑scaled softmax to the similarity scores to obtain attention weights: `weights = torch.softmax(scores / temperature, dim=0)`. Choose a default temperature of 0.1 to sharpen the distribution.

| Category | Details |
| --- | --- |
| **Reason** | Softmax converts raw similarities into a probability distribution that can be used for weighted aggregation; temperature controls sharpness. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Implement as a separate function `softmax_weights(scores, temperature=0.1)`. Store the output as `softmax_weights`. |

### 6. Compute the weighted prompt aggregation by performing a weighted sum of the original (non‑normalized) prompt embeddings: `weighted_prompt = torch.sum(weights.unsqueeze(1) * material_prompts, dim=0)`.

| Category | Details |
| --- | --- |
| **Reason** | Using the original embeddings preserves their learned magnitude while still being guided by similarity‑based attention. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Broadcast `weights` to shape `[num_materials, 1]`, multiply with `material_prompts`, then sum over the material dimension. Store as `weighted_prompt_vector`. |

### 7. Package the four outputs (`pseudo_code`, `similarity_scores`, `softmax_weights`, `weighted_prompt_vector`) into the node's result structure. The `pseudo_code` field should contain a language‑agnostic, step‑by‑step script reflecting the operations above.

| Category | Details |
| --- | --- |
| **Reason** | The node contract requires both concrete numeric outputs for downstream computation and a human‑readable pseudo‑code description for documentation. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Construct a multi‑line string with clear comments, variable names matching the steps, and include optional type hints. Example provided in the pseudo‑code field. |

### 8. Add sanity‑check assertions: verify that `similarity_scores` length equals `number_of_materials`, that `softmax_weights` sum to 1 (within tolerance), and that `weighted_prompt_vector` shape matches `prompt_dimension` D.

| Category | Details |
| --- | --- |
| **Reason** | Early detection of shape or numerical errors prevents downstream crashes in incremental training loops. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `assert torch.allclose(weights.sum(), torch.tensor(1.0), atol=1e-5)` and shape checks; raise informative errors if violated. |
