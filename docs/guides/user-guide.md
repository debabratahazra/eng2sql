# Eng2SQL — User Guide

> **Last Updated**: 2026-05-28
> **Version**: v1.2.0 (Sprint 7)

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Selecting a Database Type](#selecting-a-database-type)
3. [Connecting to MySQL — Two-Step Flow](#connecting-to-mysql--two-step-flow)
4. [Connecting to MongoDB — Two-Step Flow](#connecting-to-mongodb--two-step-flow)
5. [Generating SQL / MQL](#generating-sql--mql)
6. [Step-by-Step Progress Indicator](#step-by-step-progress-indicator)
7. [Reading Your SQL Results](#reading-your-sql-results)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

---

## Getting Started

### Prerequisites

- A web browser (Chrome, Firefox, Edge, Safari)
- An OpenAI API key — [get one here](https://platform.openai.com/api-keys)
- *(Optional for Live mode)* Access to a MySQL 8.0 database

### Launch the App

**Docker (quickest)**
```bash
cp .env.example .env          # fill in OPENAI_API_KEY
docker compose up
```
Open **http://localhost:8501** in your browser.

> **Docker image**: `ghcr.io/your-org/eng2sql:1.0.0` (or `latest` for the most recent build)
> The cert bundle at `cert/ca-bundle.crt` is mounted automatically by `docker-compose.yml`.

**Local Python — Windows (PowerShell)**
```powershell
pip install -r requirements.txt
Copy-Item .env.example .env   # fill in OPENAI_API_KEY
.\scripts\run_app.ps1         # default port 8501
.\scripts\run_app.ps1 -Port 8502  # custom port
```

**Local Python — WSL2 / Linux / macOS**
```bash
pip install -r requirements.txt
cp .env.example .env          # fill in OPENAI_API_KEY
bash scripts/run_app.sh       # default port 8501
bash scripts/run_app.sh 8502  # custom port
```

Both scripts activate `.venv` automatically (if present), verify Python and Streamlit are on the PATH, and open the browser for you after a 3-second delay. They also print clear warnings if `.env` or `.venv` are missing.

**Manual launch (any platform)**
```bash
streamlit run src/app.py
```

---

## Static Schema Mode

Static Schema mode lets you generate SQL without connecting to a real database. The app
uses the bundled e-commerce schema (`config/database_config.yaml`).

### Available Tables

| Table         | Key Columns                                       |
| ------------- | ------------------------------------------------- |
| `customers`   | id, first_name, last_name, email, country         |
| `products`    | id, name, price, stock_qty, category_id           |
| `categories`  | id, name, parent_id                               |
| `orders`      | id, customer_id, status, total_amount, created_at |
| `order_items` | id, order_id, product_id, quantity, unit_price    |
| `reviews`     | id, product_id, customer_id, rating, comment      |

### How to Use

1. Open the app — **Static Schema** is selected by default in the sidebar.
2. Type your question in the **"Ask in English"** text area.
3. Click **⚡ Generate SQL**.
4. Watch the step-by-step progress update.
5. Copy the generated SQL from the output panel.

### Example Questions

```
Show me the top 10 customers by total order value.
List all products with less than 5 items in stock.
How many orders were placed in January 2026?
Find all customers who have never placed an order.
What is the average rating per product category?
```

---

## Live Database Mode

---

## Selecting a Database Type

The sidebar shows a **Database type** radio button at the top. Choose:
- **MySQL** — connect to a MySQL 8.0 server (default)
- **PostgreSQL** — connect to a PostgreSQL 12+ server (EPIC-009)
- **MongoDB** — connect to a MongoDB server

Switching the radio clears any existing connection state, so you always start fresh with
the chosen database engine.

---

## Connecting to PostgreSQL — Two-Step Flow

### Step 1 — Select PostgreSQL

In the **Database type** radio at the top of the sidebar, select **PostgreSQL**.

### Step 2 — Enter Connection Details

| Field    | Example         | Notes                                                                                                                              |
| -------- | --------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Host     | `localhost`     | IP or hostname                                                                                                                     |
| Port     | `5432`          | Default PostgreSQL port                                                                                                            |
| User     | `readonly_user` | Use a read-only role with `CONNECT` + `USAGE` + `SELECT` grants only                                                               |
| Password | `••••••••`      | Stored only in session memory; cleared after Step 2                                                                                |
| SSL mode | `prefer`        | `disable` / `allow` / `prefer` / `require` / `verify-ca` / `verify-full`                                                           |
| Admin DB | `postgres`      | Database used to enumerate other databases (US-052). Override if your provider has disabled `postgres` (e.g. Azure Single Server). |

The first connection attaches to the **Admin DB** (default `postgres`) so we can
enumerate all user-accessible databases. Once Step 2 selects the target database, a new
engine is built against it.

> **sslmode tip**: For local development use `disable` or `prefer`. For managed cloud
> instances (RDS, Azure, etc.) use `require` or `verify-full` and supply CA certs via
> the `PGSSLROOTCERT` environment variable. When `verify-ca` or `verify-full` is
> selected and no CA bundle is reachable, the sidebar shows a yellow warning
> reminding you to set `PGSSLROOTCERT` or place a bundle at `~/.postgresql/root.crt`
> (US-056).

### Step 3 — Connect & Select

1. Click **🔗 Connect** — the dropdown populates with non-template, non-system
   databases (`postgres`, `template0`, `template1` are filtered out).
2. Pick your database and click **Select Database** — the live schema is auto-detected.

### Step 4 — Generate & Execute

Identical to MySQL: type the question, click **⚡ Generate SQL**, then **▶ Execute SQL**.
The LLM is told the dialect is PostgreSQL and uses `ILIKE`, `::` casts, and `LIMIT N
OFFSET M` accordingly.

---

## Live Database Mode

Live Database mode connects to your MySQL database, auto-detects its schema, and uses the
real table structure when generating and executing SQL.

### Step 1 — Select Live Database Mode

Click **"Live Database"** in the sidebar radio buttons.### Step 2 — Enter Connection Details

| Field    | Example         | Notes                         |
| -------- | --------------- | ----------------------------- |
| Host     | `localhost`     | IP or hostname                |
| Port     | `3306`          | Default MySQL port            |
| User     | `readonly_user` | Use a read-only DB user       |
| Password | `••••••••`      | Stored only in session memory |
| Database | `my_database`   | Target database name          |

> **Security tip**: Create a dedicated MySQL user with `SELECT`-only privileges for this
> tool. Never use your root or admin account.

### Step 3 — Connect

Click **🔗 Connect**. The status indicator will show:
- ✅ **Connected to `<database>`** — schema detected successfully
- ❌ **Connection failed** — check your credentials or network access

### Step 4 — Browse the Schema

Expand the **🗄️ Detected Schema** panel to see all tables and columns that were found.
Click **🔄 Refresh Schema** after making DDL changes to your database.

### Step 5 — Generate & Execute

1. Type your question and click **⚡ Generate SQL**.
2. Review the generated SQL in the output panel.
3. In MySQL Live mode, click **▶ Execute SQL** to run it against your database.
4. Results appear in the **📊 Query Results** table below.

---

## Connecting to MongoDB — Two-Step Flow

### Step 1 — Select MongoDB

In the **Database type** radio at the top of the sidebar, select **MongoDB**.

### Step 2 — Enter Connection Details

MongoDB Step 1 shows a **Connection input mode** toggle with two options:

#### Fields mode (default)

| Field          | Example         | Notes                                                        |
| -------------- | --------------- | ------------------------------------------------------------ |
| Host           | `localhost`     | IP address or hostname of the MongoDB server                 |
| Port           | `27017`         | Default MongoDB port                                         |
| Username       | `readonly_user` | Leave blank for unauthenticated connections                  |
| Password       | `••••••••`      | Stored only in session memory — never written to disk        |
| Auth Source    | `admin`         | Database that holds the user credentials (typically `admin`) |
| Auth Mechanism | `SCRAM-SHA-256` | Choose `None / No Auth` for unauthenticated servers          |

#### URI + credentials mode

Use this mode when you have a full MongoDB connection URI (e.g. from a cloud provider
dashboard) and want to supply credentials separately.

| Field       | Example                      | Notes                                                          |
| ----------- | ---------------------------- | -------------------------------------------------------------- |
| MongoDB URI | `mongodb://localhost:27017/` | Bare URI — **do not include credentials in the URI itself**    |
| Username    | `readonly_user`              | Leave blank for unauthenticated connections                    |
| Password    | `••••••••`                   | Injected into the URI before connecting; never written to disk |

**Supported URI formats:**
```
mongodb://localhost:27017/
mongodb://localhost:27017/?authSource=admin
mongodb+srv://cluster0.mongodb.net/?authSource=admin&retryWrites=true
```

> **Important**: Do **not** embed credentials directly in the URI
> (e.g. `mongodb://user:pass@host/`). The app will show a warning and block the
> connection. Enter credentials in the Username and Password fields instead.

> **SRV URIs** (`mongodb+srv://`): The app automatically omits `directConnection`
> for SRV URIs, which is required for Atlas and replica-set connections that use
> the SRV discovery scheme.

### Step 3 — Connect

Click **🔗 Connect**. The status indicator shows:
- ✅ **Connected — N databases found** — server reachable
- ❌ **Connection failed** — check credentials, host, and port

### Step 4 — Select Database

A dropdown appears with all non-system databases on the server (`admin`, `local`, and
`config` are filtered out automatically). Choose a database and click **Select Database**.

The schema viewer immediately shows all discovered collections and their sampled fields.

### Step 5 — Generate MQL

Type your question in plain English and click **⚡ Generate SQL**.

The output panel will display a MongoDB-flavoured query (e.g., `db.collection.find(...)`
or an aggregation pipeline). Because MongoDB uses MQL rather than SQL, the **Execute**
button is hidden in MongoDB mode — copy the generated query and run it in your MongoDB
client or shell.

---

## Generating SQL / MQL

While SQL is being generated, you will see four steps:

| Step                                   | What’s Happening                                     |
| -------------------------------------- | ---------------------------------------------------- |
| Step 1/4 — Reading schema…             | Reading pre-detected schema from session state       |
| Step 2/4 — Building prompt…            | Assembling the LLM system prompt with schema context |
| Step 3/4 — Generating SQL with OpenAI… | GPT-5.2 is writing your query                        |
| Step 4/4 — Done ✅                      | SQL is ready                                         |

---

## Reading Your SQL Results

- The generated SQL is displayed in a **syntax-highlighted code block**.
- Click anywhere in the code block and use `Ctrl+A` / `Cmd+A` to select all, then copy.
- Use the **🗑️ Clear** button to reset the output and start a new question.
- In Live mode, the **📊 Query Results** dataframe supports sorting by clicking column headers.
- After results appear, click **⬇ Download CSV** to save the result set as a UTF-8 CSV
  file named `eng2sql_results_<YYYYMMDD>.csv` (US-086). If the result set is empty, the
  button is shown as disabled with a "No results to export" label.

---

## Query History (Sprint 20)

Every successful query is added to the **🕒 Query History** panel that appears below the
input/output columns. The panel shows the last 10 queries (most-recent first).

- Each entry shows the plain-English question and the generated SQL/MQL (truncated to 80
  characters if longer).
- Click **↩ Re-use** next to any entry to pre-populate the input box with that question.
- History is **session-scoped** — it is cleared when you reload the page.


---

## Troubleshooting

### "❌ SQL generation failed — OpenAI API error"

- Check that `OPENAI_API_KEY` is set correctly in your `.env` file.
- Verify your API key has sufficient credits at [platform.openai.com](https://platform.openai.com).
- Check your network can reach `api.openai.com`.

### "❌ Connection failed: Access denied"

- Verify the username and password.
- Ensure the MySQL user has `SELECT` privilege on the target database.
- Check that the host allows connections from your IP (firewall / `GRANT` statement).

### "⚠️ Remove credentials from the URI"

This warning appears when you paste a URI that already contains `username:password@` in
URI + credentials mode. Remove the credentials from the URI field and enter them in the
separate Username and Password fields instead.

### "❌ Connection failed: Could not connect to server"

- Confirm the host and port are correct.
- If using Docker, make sure the DB container is running (`docker ps`).
- Check for firewall rules blocking port 3306.

### Generated SQL References Wrong Tables

- In Static mode, edit `config/database_config.yaml` to match your schema.
- In Live mode, click **🔄 Refresh Schema** to re-detect the latest tables.

---

## FAQ

**Q: Can the tool modify data (INSERT/UPDATE/DELETE)?**
No. The app only generates and executes `SELECT` statements. Write operations are blocked by design.

**Q: Is my database password stored anywhere?**
No. Passwords are held only in Streamlit's in-memory session state and cleared when the browser tab closes. They are never written to disk or logs.

**Q: Which SQL dialects are supported?**
MySQL 8.0 is the primary SQL target. MongoDB MQL (aggregation pipeline / `find()`) is supported via the MongoDB mode. SQLite is used for testing. PostgreSQL support is on the roadmap.

**Q: Can the tool execute MongoDB queries?**
Not yet. The generated MongoDB MQL is displayed in the output panel for you to copy and run in your MongoDB client or shell. In-app MongoDB query execution is planned for a future sprint.

**Q: Can I use my own schema YAML file?**
Yes. Set the `STATIC_SCHEMA_PATH` environment variable to point to your custom YAML file.
See [config/database_config.yaml](../../config/database_config.yaml) for the required format.

**Q: How do I report a bug?**
Open a GitHub issue or create a bug report in `docs/bug-reports/` following the template.
