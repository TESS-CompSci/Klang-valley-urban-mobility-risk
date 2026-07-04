# Klang-valley-urban-mobility-risk

![Data Pipeline Dashboard](dashboard.png)

An end-to-end ETL pipeline translating raw Malaysian public transit data into executive economic loss intelligence using Python, SQLite, and Power BI. 

# Klang Valley Urban Mobility Risk Index

An end-to-end data engineering pipeline translating raw Malaysian public transit ridership data (2024–2026) into executive-ready economic loss intelligence.

## Business Problem & Impact
* **The Bottleneck:** Government transit data from data.gov.my arrives raw and un-contextualized, requiring consulting teams to spend 10+ hours weekly manually cleaning spreadsheets.
* **The Solution:** Automated the entire ingestion and modeling framework, saving ~10 hours of manual labor per week and providing immediate ministerial-ready insight.
* **The Metric:** Translated raw passenger delays into a **Simulated Economic Loss Index (MYR)**, revealing a macroeconomic risk concentration on the MRT Kajang and LRT Kelana Jaya lines.

## System Architecture
1. **Ingest & Clean (Python/Pandas):** Automated schema mapping, data melting, and typecasting on 8,820 records from the Prasarana ridership API.
2. **Analytics Warehouse (SQLite):** Developed a decoupled database schema separating operational records from an adjustable parameters table (`cfg_transit_parameters`) to prevent hardcoded variables.
3. **Executive Visualization (Power BI):** Built a high-level operational risk cockpit mapping out financial implications across 10 major rail lines.

##  Technical Stack
* **Language/Libraries:** Python 3.x, Pandas, SQLite3
* **Database Engine:** SQLite (Relational Views, Config tables, Inner Joins)
* **BI Tooling:** Power BI Desktop (DAX Measures, Data Modeling)

## Repository Structure
* `/scripts`: Core Python processing scripts.
* `/sql`: Database build queries and operational summary views.
* `/dashboard`: Production `.pbix` template.
* `/documentation`: Executive portfolio presentation deck.

## Key SQL Insights & Relational Modeling

To calculate the financial impact of transit delays dynamically without hardcoding assumptions, a relational database view was constructed in SQLite. This view joins daily ridership facts with economic parameter configurations to output an executive-level risk summary:
-- 1. DROP THE OLD HARDCODED VIEW
DROP VIEW IF EXISTS v_malaysia_executive_summary;

-- 2. BUILD THE DYNAMIC RELATIONAL VIEW
CREATE VIEW v_malaysia_executive_summary AS
SELECT 
    f.transit_line,
    COUNT(f.date) AS monitored_operating_days,
    SUM(f.daily_passengers) AS total_recorded_volume,
    SUM(f.passengers_affected) AS total_delayed_citizens,
    
    -- Dynamic Math pulling directly from your config table variables
    ROUND(SUM(
        (p.assumed_delay_minutes / 60.0) * (f.daily_passengers * p.capacity_affected_rate) * p.hourly_wage_myr
    ), 2) AS simulated_economic_loss_myr

FROM stg_malaysia_ridership f
INNER JOIN cfg_transit_parameters p 
    ON f.transit_line = p.transit_line
GROUP BY f.transit_line;

-- 3. FETCH THE RESULTS
SELECT * FROM v_malaysia_executive_summary ORDER BY simulated_economic_loss_myr DESC;
