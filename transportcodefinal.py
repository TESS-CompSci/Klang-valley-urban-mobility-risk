# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 04:14:50 2026

@author: Tess N
"""

import pandas as pd
import sqlite3
import os
from datetime import datetime

def run_production_pipeline():
    # 1. FILE VERIFICATION & INGESTION
    local_file = (r"C:\Users\Tess N\OneDrive\Desktop\TRANSPORT PROJECT\ridership_headline.parquet")
    
    if not os.path.exists(local_file):
        print(f"[ERROR] Could not find '{local_file}'")
        return

    print("Step 1: Ingesting production Parquet file...")
    df = pd.read_parquet(local_file)
    
    # 2. STANDARDIZATION & TIME-SERIES CLEANING
    print("Step 2: Cleaning and structuring time-series data...")
    df['date'] = pd.to_datetime(df['date'])
    
    # Filter for modern baseline data from 2024 up to current 2026 data
    df_modern = df[df['date'].dt.year >= 2024].copy()

    # The columns from the file
    target_lines = [
        'rail_lrt_ampang', 
        'rail_mrt_kajang', 
        'rail_lrt_kj', 
        'rail_monorail', 
        'rail_mrt_pjy',
        'rail_ets',
        'rail_intercity',
        'rail_komuter_utara',
        'rail_tebrau',
        'rail_komuter'
    ]
    
    # Melt directly using the correct schema keys
    melted_df = df_modern.melt(
        id_vars=['date'], 
        value_vars=target_lines,
        var_name='transit_line', # This column will now perfectly hold your 'rail_' strings!
        value_name='daily_passengers'
    )

    # Clean data gaps / telemetry errors
    melted_df['daily_passengers'] = melted_df['daily_passengers'].fillna(0).astype(int)
    
    # 3. CONSULTING CORE VALUE LAYER: RISK & DISRUPTION SIMULATION
    print("Step 3: Calculating operational risk coefficients & commuter impact scales...")
    
    # Extract month and day of week for macro filtering in dashboards
    melted_df['month_name'] = melted_df['date'].dt.strftime('%B')
    melted_df['day_of_week'] = melted_df['date'].dt.strftime('%A')
    
    # Injecting operational parameters
    melted_df['simulated_delay_minutes'] = 25 
    
    # Formula: Baseline volume * 10% affected capacity rate
    melted_df['passengers_affected'] = (melted_df['daily_passengers'] * 0.10).astype(int)

    # 4. DATABASE RELATIONAL LOADING
    print("Step 4: Establishing database handshake and writing to staging...")
    db_name = "malaysia_transit_real.db"
    conn = sqlite3.connect(db_name)
    
    # Stream the clean dataframe directly into a local SQL staging table
    melted_df.to_sql("stg_malaysia_ridership", conn, if_exists="replace", index=False)
    
    # Verify records written
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM stg_malaysia_ridership;")
    total_records = cursor.fetchone()[0]
    conn.close()

    print("\n" + "="*50)
    print(f"[SUCCESS] Pipeline complete. Generated: '{db_name}'")
    print(f"[METRIC] Total records successfully written to SQL: {total_records:,}")
    print("="*50)
    
    # Display snippet of the final corporate dataset output
    print("\n--- EXECUTIVE DATA EXTRACTION SAMPLE ---")
    print(melted_df.head(10).to_string(index=False))

if __name__ == "__main__":
    run_production_pipeline()