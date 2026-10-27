# NKU Sports Dashboard

## Run the dashboard

From the repository root, start the Django API:

```bash
.venv/bin/python manage.py runserver 8001
```

In a second terminal, start the React frontend:

```bash
cd frontend
npm run dev
```

Open the URL printed by Vite, usually `http://localhost:5173`.

## Refresh Detroit Mercy statistics

From the repository root, run:

```bash
.venv/bin/python -m Scraping.scrape_pages detroit
```

The scraper writes `detroit_stats.xlsx` to the repository root. The dashboard
loads it when Detroit Mercy is selected. Northern Kentucky data is read from
`norse_stats.xlsx`. Other schools appear in the selector but do not have
workbooks connected to the API yet.
