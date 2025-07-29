# 🛡️ Input & Output Guardrail System using OpenAI-Compatible Gemini API

This project demonstrates how to use **input** and **output guardrails** with a multi-agent system using the **OpenAI-compatible Gemini 2.0 Flash model**.

## 📁 Files

### 1. `input_guardrail.py`
Implements an **input guardrail** to detect if the user is asking about the **Prime Minister**. If detected, the request is passed (handed off) to a `second_agent` that provides extra information.

- ✅ Uses `@input_guardrail` decorator
- 🔍 Detects "prime minister" queries
- 🤖 Uses `AsyncOpenAI` Gemini-compatible client
- 🔄 Hands off to `second_agent` if tripwire is triggered

### 2. `output_guardrail.py`
Implements an **output guardrail** to detect if the user query result mentions the **President**. If yes, it triggers a secondary response using a second agent that provides extra context.

- ✅ Uses `@output_guardrail` decorator
- 🔍 Detects "president" responses
- 🤖 Uses `Runner.run_sync()` for synchronous execution
- 🧠 Demonstrates how to use `GuardrailFunctionOutput`

---

## 🧪 Example Use Case

> "Who is the President of Pakistan in 2023?"

- If the input or output contains references to the **President or Prime Minister**, a **tripwire is triggered**, and a second agent provides **additional information** automatically.

---

## ⚙️ Requirements

- Python 3.10+
- `pydantic`
- `python-dotenv`
- `rich`
- `openai`-compatible SDK with Gemini support

Install dependencies:

```bash
pip install -r requirements.txt


🔑 Environment Setup
GEMINI_API_KEY=your_api_key_here

🚀 Running the Scripts
For Input Guardrail:

python input_guardrail.py
For Output Guardrail:

python output_guardrail.py
🧠 Concepts Used
Agents with guardrails (input & output)

Tripwire logic using GuardrailFunctionOutput

Multi-agent handoff architecture

OpenAI-compatible Gemini model integration

📬 Contact
Created by Sohail Nawaz
🔗 GitHub | 🌐 LinkedIn

📄 License
This project is licensed under the MIT License.
