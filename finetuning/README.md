# Fine-tuning a Text2SQL Model with Distil CLI

Train a compact model that converts natural language questions into SQL queries using the Distil Labs platform.

## Prerequisites

Install the Distil CLI:

```bash
curl -fsSL https://cli-assets.distillabs.ai/install.sh | sh
```

Authenticate:

```bash
distil login
```

## Training Data

The `data/` folder contains everything needed to train the model:

| File | Description |
|------|-------------|
| `job_description.json` | Task definition for text-to-SQL generation |
| `train.jsonl` | Training examples (schema + question → SQL query) |
| `test.jsonl` | Evaluation examples |
| `config.yaml` | Training configuration (Qwen3-4B base model) |

### Example Training Sample

**Input:**
```
Schema:
CREATE TABLE employees (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  department TEXT,
  salary INTEGER
);

Question: How many employees are in the Sales department?
```

**Output:**
```sql
SELECT COUNT(*) FROM employees WHERE department = 'Sales';
```

## Training Steps

### 1. Create a Model

```bash
distil model create text2sql
```

Save the returned `<model-id>` for subsequent commands.

### 2. Upload Training Data

```bash
distil model upload-data <model-id> --data ./data
```

### 3. Run Teacher Evaluation

Validate that a large model can solve the task before training:

```bash
distil model run-teacher-evaluation <model-id>
```

Check status:

```bash
distil model teacher-evaluation <model-id>
```

### 4. Train the Model

Start distillation to create your compact text2sql model:

```bash
distil model run-training <model-id>
```

Monitor progress:

```bash
distil model training <model-id>
```

### 5. Download the Model

Once training completes, download the Ollama-ready package:

```bash
distil model download <model-id>
```

## Local Deployment

Run your trained model locally with [Ollama](https://ollama.com):

```bash
ollama create text2sql -f Modelfile
ollama run text2sql
```

## Model Configuration

The training uses:
- **Base model:** Qwen3-4B-Instruct-2507
- **Teacher model:** DeepSeek V3.1
- **Task type:** Question-answering

The model is trained across multiple domains: e-commerce, HR/business, education, healthcare, finance, and social/content.

## Learn More

- [Distil Documentation](https://docs.distillabs.ai)
- [Input Preparation Guide](https://docs.distillabs.ai/how-to/input-preparation)
