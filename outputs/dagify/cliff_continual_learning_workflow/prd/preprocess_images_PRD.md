# preprocess_images PRD

## Description
Standardize all images (normalization, resizing, augmentation) and store them ready for training.


## Implementation Plan

### 1. Extract source image directories from the parent nodes: read `dataset_path` from `collect_reference_material_dataset` and each entry of `storage_paths` from `collect_new_material_datasets`.

| Category | Details |
| --- | --- |
| **Reason** | Ensures the preprocessing script knows exactly where the raw images reside for every material, avoiding hard‑coded paths. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Parse the JSON or Python objects returned by the parent nodes; store paths in a dict `material -> raw_dir`. |

### 2. Define preprocessing hyper‑parameters: set `image_width` and `image_height` (e.g., 224×224), `normalization_mean` = 0.5, `normalization_std` = 0.5, and a boolean `augmentation_enabled` (configurable via a command‑line flag or config file).

| Category | Details |
| --- | --- |
| **Reason** | These parameters are required by downstream training code and must be recorded for reproducibility. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Create a Python `argparse.Namespace` or a YAML config file; validate that values are positive integers/floats. |

### 3. Create the root output directory `processed_images_dir` (e.g., `data/processed/`) and, for each material, sub‑directories `{material}/train`, `{material}/val`, `{material}/test`.

| Category | Details |
| --- | --- |
| **Reason** | A deterministic folder hierarchy makes later splitting and data loading straightforward and matches the expectations of the `split_datasets` node. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | Use `os.makedirs(path, exist_ok=True)` in a loop over materials and splits. |

### 4. Initialize an empty list `processed_image_paths` and a counter `total_images_processed = 0`.

| Category | Details |
| --- | --- |
| **Reason** | Collecting these values during the loop allows immediate population of the required output fields without a second pass. |
| **Impact** | LOW |
| **Complexity** | LOW |
| **Method** | Python list and integer variables. |

### 5. Iterate over each material and over every image file (`.png`, `.jpg`, `.tif`) in its raw directory. For each image:

| Category | Details |
| --- | --- |
| **Reason** | Core processing loop – must handle all files robustly. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Use `glob.glob(os.path.join(raw_dir, "*.[pj][pn]g"))` and `tifffile.imread` for TIFFs. |

### 6. Load the image with Pillow (or OpenCV), convert to RGB, cast to `float32`, and scale pixel values to the range [0, 1].

| Category | Details |
| --- | --- |
| **Reason** | Standardizes input format for downstream deep‑learning frameworks that expect float tensors. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | `img = Image.open(path).convert('RGB'); img = np.asarray(img).astype(np.float32) / 255.0`. |

### 7. Apply normalization: `img = (img - normalization_mean) / normalization_std` element‑wise.

| Category | Details |
| --- | --- |
| **Reason** | Centers the data distribution, which improves training stability. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | NumPy broadcasting or torch transforms. |

### 8. Resize the normalized image to `(image_width, image_height)` using bilinear interpolation (`Image.BILINEAR`).

| Category | Details |
| --- | --- |
| **Reason** | All models expect a fixed input size; bilinear interpolation preserves visual quality. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | `img_resized = Image.fromarray((img*255).astype(np.uint8)).resize((image_width, image_height), Image.BILINEAR)`. |

### 9. If `augmentation_enabled` is True and the current split is `train`, generate augmented variants using a deterministic pipeline: random rotation (±15°), horizontal/vertical flip, and brightness jitter (±0.2). Append each augmented image to the same material `train` folder with suffixes `_rot`, `_flip`, `_bright`.

| Category | Details |
| --- | --- |
| **Reason** | Data augmentation increases robustness for the first training stage while keeping validation/test untouched. |
| **Impact** | HIGH |
| **Complexity** | MEDIUM |
| **Method** | Leverage `torchvision.transforms.Compose([RandomRotation(15), RandomHorizontalFlip(), ColorJitter(brightness=0.2)])`; apply to the PIL image before saving. |

### 10. Save the (possibly augmented) image as a lossless PNG (`cv2.imwrite` or `Image.save`) in the appropriate `{material}/{split}` folder. Record the absolute file path in `processed_image_paths` and increment `total_images_processed`.

| Category | Details |
| --- | --- |
| **Reason** | Persists the standardized data and builds the required output list for downstream nodes. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | `save_path = os.path.join(processed_images_dir, material, split, filename); Image.fromarray((img_resized*255).astype(np.uint8)).save(save_path)`. |

### 11. After processing all images, write a small `metadata.json` inside `processed_images_dir` containing the hyper‑parameters (`image_width`, `image_height`, `normalization_mean`, `normalization_std`, `augmentation_enabled`).

| Category | Details |
| --- | --- |
| **Reason** | Provides a self‑contained record for reproducibility and for any downstream audit. |
| **Impact** | MEDIUM |
| **Complexity** | LOW |
| **Method** | `json.dump({...}, open(os.path.join(processed_images_dir, 'metadata.json'), 'w'))`. |

### 12. Return the populated output fields: `processed_images_dir`, `processed_image_paths`, `total_images_processed`, `image_width`, `image_height`, `normalization_mean`, `normalization_std`, `augmentation_enabled`.

| Category | Details |
| --- | --- |
| **Reason** | Fulfills the node contract so that `split_datasets` can consume the standardized images. |
| **Impact** | HIGH |
| **Complexity** | LOW |
| **Method** | Construct a Python dict matching the output schema and output it via the workflow engine. |
