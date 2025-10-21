# uTracker

Web application that predicts MMA fight based on basic fighter statistics, and external API information.  
It combines **FastAPI**, **PyTorch**, and **htmx** to serve real-time predictions directly in the browser.

---
### Folder Structure
```
uTracker/
├── app/
│   ├── main.py                # FastAPI app setup and model loading
│   ├── routes/                # API and HTML endpoints
│   ├── schemas/               # Pydantic models
│   ├── services/              # Business logic and model definition 
│   └── db/                    # SQLAlchemy models
│
├── templates/                 # Jinja2 + htmx templates
│
├── pytorch/
│   ├── predictor.pt
│   ├── predictor_meta.json
│   └── utracker.ipynb
├── requirements.txt
└── README.md
```
---
### Features

- **Fight Prediction** — Uses a tiny PyTorch neural network to predict the probability of each fighter winning.  
- **Automatic Data Fetching** — Retrieves missing fighter stats from an external API (RapidAPI).  
- **Database Caching** — Stores fetched features locally to avoid redundant API calls.  
- **Live Web Interface** — Simple frontend using htmx for dynamic updates without full-page reloads.  

---
### Setup

#### 1- Clone and install
```bash
git clone https://github.com/rober0xf/uTracker.git
cd uTracker
uv venv
source .venv/bin/activate
uv pip install -e .
```
#### 2- Set the env variables
```
DATABASE_URL=sqlite:///utracker.db
RAPIDAPI_API_KEY=<your-rapidapi-key>
```
#### 3- Model Setup
```
pytorch/predictor.pt
pytorch/predictor_meta.json
```
---
### Contributions
All contributions are welcome. Keep changes simple, clear, and consistent with the existing code. Use type hints and short, meaningful commit messages.
