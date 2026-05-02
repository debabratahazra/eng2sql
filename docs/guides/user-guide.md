# Eng2SQL — User Guide

> **Last Updated**: 2026-05-02
> **Version**: [v1.0.0](../deployment/RELEASE-1.0.0.md)

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Connecting to MySQL — Two-Step Flow](#connecting-to-mysql--two-step-flow)
3. [Generating SQL](#generating-sql)
4. [Step-by-Step Progress Indicator](#step-by-step-progress-indicator)
5. [Reading Your SQL Results](#reading-your-sql-results)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)

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

**Local Python**
```bash
pip install -r requirements.txt
cp .env.example .env          # fill in OPENAI_API_KEY
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

Live Database mode connects to your MySQL database, auto-detects its schema, and uses the
real table structure when generating and executing SQL.

### Step 1 — Select Live Database Mode

Click **"Live Database"** in the sidebar radio buttons.

### Step 2 — Enter Connection Details

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
3. Click **▶ Execute SQL** to run it against your database.
4. Results appear in the **📊 Query Results** table below.

---

## Step-by-Step Progress Indicator

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
MySQL 8.0 is the primary target. SQLite is supported for testing. PostgreSQL support is on the roadmap.

**Q: Can I use my own schema YAML file?**
Yes. Set the `STATIC_SCHEMA_PATH` environment variable to point to your custom YAML file.
See [config/database_config.yaml](../../config/database_config.yaml) for the required format.

**Q: How do I report a bug?**
Open a GitHub issue or create a bug report in `docs/bug-reports/` following the template.
