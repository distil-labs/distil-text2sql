# Distil CLI

The Distil CLI is a command-line tool for fine-tuning compact language models using the Distil Labs platform. It enables you to train specialized models up to 70x smaller than teacher models while maintaining comparable accuracy—without requiring ML expertise.

## Installation

```bash
curl -fsSL https://cli-assets.distillabs.ai/install.sh | sh
```

## Authentication

```bash
distil login      # Login to Distil Labs platform
distil whoami     # Display current user
distil logout     # Logout from platform
```

## Workflow

The Distil workflow consists of four main steps:

### 1. Create a Model

```bash
distil model create my-model-name
```

### 2. Upload Data

Prepare your data files and upload them to the platform.

**Option A: Upload from a directory**

Point to a directory containing all required files with standard names:

```bash
distil model upload-data <model-id> --data ./my-data-folder
```

**Option B: Upload individual files**

Specify each file path explicitly:

```bash
distil model upload-data <model-id> \
  --job-description job_description.json \
  --train train.csv \
  --test test.csv \
  --config config.yaml \
  [--unstructured unstructured.csv]
```

**Data files:**
| File | Format | Required | Description |
|------|--------|----------|-------------|
| `job_description` | `.json` | Yes | Task objectives and configuration |
| `train` | `.csv` or `.jsonl` | Yes | 20–100 labeled (question, answer) pairs |
| `test` | `.csv` or `.jsonl` | Yes | Held-out evaluation set |
| `unstructured` | `.csv` or `.jsonl` | No | Domain documents for synthetic data generation |
| `config` | `.yaml` | No | Training hyperparameters |

For detailed file format specifications, see: https://docs.distillabs.ai/how-to/input-preparation

### 3. Run Teacher Evaluation

Validate that a large language model can solve your task before training:

```bash
distil model run-teacher-evaluation <model-id>
distil model teacher-evaluation <model-id>  # Check status
```

This evaluates using Exact-Match, LLM-as-a-Judge, ROUGE-L, and METEOR metrics.

### 4. Train Your Model

Start the training process to distill knowledge into a compact model:

```bash
distil model run-training <model-id>
distil model training <model-id>  # Check status
```

### 5. Download Your Model

Once training completes, download the model as an Ollama-ready package:

```bash
distil model download <model-id>
```

## Additional Commands

```bash
distil model show                    # List all models
distil model show <model-id>         # Show model details
distil model download-data <model-id>  # Download uploaded data files
```

Use `--output json` flag for JSON-formatted output.

## Local Deployment

Deploy your trained model locally with [Ollama](https://ollama.com):

```bash
ollama create my-model -f Modelfile
ollama run my-model
```

## Learn More

For a complete tutorial, visit: https://docs.distillabs.ai/tutorials/question-answering