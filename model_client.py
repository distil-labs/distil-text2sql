import argparse

from openai import OpenAI

DEFAULT_QUESTION = """Schema:
CREATE TABLE clinics (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  address TEXT,
  phone TEXT
);

CREATE TABLE visits (
  id INTEGER PRIMARY KEY,
  clinic_id INTEGER REFERENCES clinics(id),
  patient_name TEXT,
  visit_date DATE,
  diagnosis TEXT
);

Question: How many patient visits per clinic this year?"""


class DistilLabsLLM(object):
    def __init__(self, model_name: str, api_key: str = "EMPTY", port: int = 11434):
        self.model_name = model_name
        self.client = OpenAI(base_url=f"http://127.0.0.1:{port}/v1", api_key=api_key)

    def get_prompt(
        self,
        question: str,
    ) -> list[dict[str, str]]:
        return [
            {
                "role": "system",
                "content": """
You are a problem solving model working on task_description XML block:
<task_description>You are given a database schema and a natural language question. Generate the SQL query that answers the question.

Input:
- Schema: One or two table definitions in SQL DDL format
- Question: Natural language question about the data

Output:
- A single SQL query that answers the question
- No explanations, comments, or additional text

Rules:
- Use only tables and columns from the provided schema
- Use uppercase SQL keywords (SELECT, FROM, WHERE, etc.)
- Use SQLite-compatible syntax</task_description>
You will be given a single task in the question XML block
Solve only the task in question block.
Generate only the answer, do not generate anything else
""",
            },
            {
                "role": "user",
                "content": f"""

Now for the real task, solve the task in question block.
Generate only the solution, do not generate anything else
<question>{question}</question>
""",
            },
        ]

    def invoke(self, question: str) -> str:
        chat_response = self.client.chat.completions.create(
            model=self.model_name,
            messages=self.get_prompt(question),
            temperature=0,
            reasoning_effort="none",
        )
        return chat_response.choices[0].message.content


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", type=str, default=DEFAULT_QUESTION, required=False)
    parser.add_argument("--api-key", type=str, default="EMPTY", required=False)
    parser.add_argument("--model", type=str, default="distil-qwen3-4b-text2sql-gguf-4bit", required=False)
    parser.add_argument("--port", type=int, default=11434, required=False)
    args = parser.parse_args()

    client = DistilLabsLLM(model_name=args.model, api_key=args.api_key, port=args.port)

    print(client.invoke(args.question))