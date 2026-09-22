NSW Live Fuel Price Pipeline
A production-grade, end-to-end data engineering pipeline that automates the ingestion, cloud storage, transformation, and analytical modeling of live fuel price data across New South Wales (NSW).

🏗️ Architecture & Tech Stack
Orchestration: Apache Airflow (automated daily scheduling at 23:58 to prep morning reports)

Storage & Cloud: AWS S3 (Data Lake architecture)

Transformation: dbt (data build tool) implementing a rigorous Medallion Architecture (Bronze, Silver, and Gold layers)

Query & Analytics: Amazon Athena

Environment & Package Management: uv for fast dependency resolution and clean environment control

Version Control: Git & GitHub

📂 Project Structure
Plaintext
├── dags/                     # Airflow DAG scripts for daily orchestration and API retrieval
│   ├── fuel_pipeline_dag.py
│   ├── incremental_dag.py
│   └── scripts/              # Python helper scripts for API calls and S3 uploads
├── dbt_transforms/           # dbt project directory (Medallion Architecture)
│   └── fuel_pipeline_dbt/
│       ├── models/
│       │   ├── bronze/       # Raw data ingestion layers
│       │   ├── silver/       # Cleaned, standardized data models
│       │   └── gold/         # Aggregated business-level summary models
│       ├── dbt_project.yml
│       └── profiles.yaml
├── uv.lock                   # Dependency lock file managed by uv
├── .gitignore                # Excludes sensitive data, virtual environments, and temp files
└── README.md
🔄 Pipeline Workflow
Ingestion: Airflow triggers daily Python scripts to fetch live fuel price feeds via API.

Storage: Raw data files are pushed securely to AWS S3.

Transformation (Medallion Architecture):

Bronze Layer: Raw transactional and station reference data ingested directly from the source.

Silver Layer: Data cleaned, type-casted, and structured for reliability.

Gold Layer: Fully aggregated analytical tables (gold_station_summary, gold_stations_per_area, gold_weekwise_status) optimized for querying and reporting.

🚀 Getting Started & Setup
Clone the Repository:

Bash
git clone https://github.com/your-username/nsw-fuel-price-pipeline.git
cd nsw-fuel-price-pipeline
Configure Environment:
Set up your environment variables (.env) for AWS credentials and Airflow configurations (ensure .env is kept out of version control).

Install Dependencies:
Use uv for fast local dependency installation:

Bash
uv sync
Run dbt Models:
Navigate into the dbt project folder and execute transformations:

Bash
cd dbt_transforms/fuel_pipeline_dbt
dbt run
