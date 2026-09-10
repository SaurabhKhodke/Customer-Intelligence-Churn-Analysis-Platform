# Customer Intelligence — AI-Powered Churn Prediction

## Overview

This system is an end-to-end AI-powered customer intelligence and churn prediction platform. It allows users to ask natural-language questions about customer data, retention, and model explanations.

The end-to-end flow is:
User question → intent detection → RAG / SQL / SHAP as appropriate → grounded LLM response → FastAPI → React frontend.

The system combines:
* Customer churn prediction
* SQL-based customer analytics
* RAG for domain/model knowledge
* SHAP-based model explainability
* LLM-powered natural-language answers
* FastAPI backend
* React frontend

## Key Features

* Customer churn prediction
* Risk categorization (HIGH, MEDIUM, LOW)
* Customer-level predictions
* SQL analytics (for factual database queries)
* RAG retrieval (for domain and model knowledge)
* SHAP explanations (to interpret individual customer predictions)
* Natural-language customer intelligence queries
* Dashboard / frontend insights
* API layer exposing intelligence and predictions

## Architecture

User
↓
React Frontend
↓
FastAPI
↓
Customer Intelligence Pipeline
├── Intent Router
├── SQL Analytics
├── RAG Retrieval
├── Churn Prediction
└── SHAP Explainability
↓
Grounded LLM Response
↓
Frontend

## Project Structure

```text
customer-intelligence/
├── api/                  # FastAPI backend entry point
│   └── main.py           # Backend endpoints
├── data/                 # Raw/processed datasets and SQLite database
│   ├── customer_churn.db
│   ├── processed/
│   └── raw/
├── frontend/             # React/Vite frontend source code
├── models/               # Trained models
│   └── final_churn_model.pkl
├── notebooks/            # Jupyter notebooks for data analysis and ML experimentation
├── rag/                  # RAG, LLM, SHAP, and SQL logic
├── scripts/              # Helper scripts
├── sql/                  # SQL tools or definitions
├── src/                  # Core logic, predictions, preprocessing
├── Dockerfile            # Backend Docker setup
├── .env.example          # Example environment variables
├── .gitignore            # Git exclusion rules
└── README.md             # This file
```

## ML Pipeline

The ML workflow used to build the final model involved:
1. Raw dataset
2. Data cleaning
3. Feature engineering
4. Preprocessing
5. Train/test split
6. Model comparison
7. Hyperparameter tuning
8. Final model selection (Logistic Regression)
9. Model persistence (`final_churn_model.pkl`)
10. Prediction (Stored in SQLite database)
11. SHAP explainability

The actual final model used by the project is a Logistic Regression model.

## Features Used

**Numerical Features:**
* age
* tenure_months
* orders_count
* monthly_spend
* discount_usage_rate
* support_tickets
* satisfaction_score
* recency_days
* orders_per_month
* support_tickets_per_month

**Categorical Features:**
* gender
* city
* acquisition_channel
* subscription_plan
* payment_method

**Target:**
* churn (binary: 1 or 0)

*Note: `recency_days`, `orders_per_month`, and `support_tickets_per_month` are engineered features derived from the raw data.*

## RAG + SQL + SHAP

* **RAG:** Used for domain/model knowledge and retention guidance.
* **SQL:** Used for factual customer/database queries and aggregations from the `customer_churn.db`.
* **SHAP:** Used to explain which model features contributed to an individual prediction.

*Note: SHAP explanations represent model behavior and feature contribution to the prediction. They should NOT be interpreted as causal explanations for actual real-world churn.*

## Intent Routing

The intelligence pipeline routes questions into one of four intent categories:
* **OUT_OF_SCOPE**: Used to politely reject questions unrelated to customer intelligence or churn prediction.
* **RAG**: Used when the question requires domain knowledge or concepts from retrieved documents.
* **SQL**: Used when the question requires querying the database for factual data.
* **BOTH**: Used when the question requires combining database facts with domain knowledge.

## API

The backend uses FastAPI and exposes the following important endpoints:

* `GET /health`
  * Purpose: Check API health and status.
  * Response fields: `status`, `model`, `stored_predictions`.

* `POST /predict`
  * Purpose: Generate a churn prediction for a new customer payload.
  * Request fields: Customer features (age, tenure_months, gender, etc.).
  * Response fields: `churn_probability`, `risk`, `top_factors`.

* `GET /customer/{customer_id}`
  * Purpose: Retrieve details and stored predictions for a specific customer.
  * Response fields: Customer details, `churn_probability`, `predicted_churn`, `risk`.

* `GET /customers/high-risk`
  * Purpose: Retrieve high-risk customers ordered by churn probability.
  * Request fields (query): `limit`, `offset`.
  * Response fields: `total_high_risk_customers`, `limit`, `offset`, `returned`, `customers`.

* `GET /customers/risk-summary`
  * Purpose: Return the count of customers in each risk category.
  * Response fields: `total_customers`, `risk_distribution`.

* `GET /dashboard/summary`
  * Purpose: Return the prediction metrics used by the dashboard.
  * Response fields: `total_customers`, `predicted_churn_customers`, `average_churn_probability`, `high_risk_customers`, `medium_risk_customers`, `low_risk_customers`.

* `GET /customers/{customer_id}/explanation`
  * Purpose: Return SHAP-based explanation for a stored customer prediction.
  * Response fields: `customer_id`, `churn_probability`, `risk`, `top_factors`, `explanation_method`.

* `POST /ai/query`
  * Purpose: Process a natural-language customer intelligence query.
  * Request fields: `question`.
  * Response fields: `question`, `intent`, `answer`, `sql`, `sql_result`, `shap_explanations`, and more.

## Frontend

The frontend is built using **React** and **Vite**.
It communicates with the FastAPI backend to display major screens/components, including a dashboard with prediction insights, risk summaries, and individual customer SHAP explanations. Natural language queries can be run to interact with the AI-powered intelligence pipeline.

## Setup

The project uses:
* Python 3.10
* a project-local `.venv`
* Jupyter kernel named `Python (customer-intelligence)`

### 1. Clone repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Create virtual environment

```bash
py -3.10 -m venv .venv
```

### 3. Activate `.venv`

**Windows PowerShell:**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Environment variables

Copy the example environment file and update it:
```bash
cp .env.example .env
```
Ensure your `.env` contains valid credentials like your `GROQ_API_KEY`.

### 6. Jupyter kernel

To register and use the kernel with the `.venv`:
```bash
python -m ipykernel install --user --name=customer-intelligence --display-name="Python (customer-intelligence)"
```
*Make sure the kernel points to the same project `.venv`.*

### 7. Run backend

From the project root:
```bash
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

### 8. Run frontend

Open a new terminal, navigate to the `frontend` folder, install packages (if required), and run:
```bash
cd frontend
npm run dev
```

### 9. Open application

* Frontend: Typically available at `http://localhost:5173`
* Backend API / Docs: `http://127.0.0.1:8000/docs`

## Data and Model Files

This repository contains several important pre-built artifacts to ensure the demo works out of the box without needing retraining:
* **SQLite Database** (`data/customer_churn.db`): Contains sample customers and pre-computed predictions required by the API. This file is intentionally committed.
* **Trained Model** (`models/final_churn_model.pkl`): The persisted Logistic Regression pipeline used for new predictions and SHAP explanations. It is intentionally committed.
* **Raw/Processed Data** (`data/raw/`, `data/processed/`): Used during data ingestion and global SHAP exploration. 

*If any data or model files are missing or you wish to retrain, follow the provided Jupyter notebooks.*

## Docker

This repository includes a `Dockerfile` designed to containerize the **backend API** only (the frontend can be hosted separately or via its own container/service).

* **What it containerizes:** The FastAPI backend, data files, and ML model.
* **Status:** Ready for production/demo use. Requirements are installed automatically during build.
* **Build:**
  ```bash
  docker build -t customer-intelligence-api .
  ```
* **Run:**
  ```bash
  docker run -p 8000:8000 customer-intelligence-api
  ```
* **Exposed Port:** 8000
