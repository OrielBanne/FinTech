import pandas as pd
import json
import os

data_dir = '/home/ubuntu/rl_trading_system/data'
processed_data_dir = '/home/ubuntu/rl_trading_system/data/processed'
os.makedirs(processed_data_dir, exist_ok=True)

symbols = ["AAPL", "GOOG", "NVDA"]

def process_insights_data(symbol):
    file_path = os.path.join(data_dir, f"{symbol}_insights.json")
    print(f"Processing insights data for {symbol} from {file_path}...")
    try:
        with open(file_path, "r") as f:
            raw_data = json.load(f)

        if not raw_data or "finance" not in raw_data or "result" not in raw_data["finance"] or not raw_data["finance"]["result"]:
            print(f"Warning: No valid finance insights data found for {symbol} in {file_path}")
            return None

        result = raw_data["finance"]["result"]
        insights = {}

        # Extract basic info
        insights["symbol"] = result.get("symbol")

        # Extract Technical Events Outlooks (if available)
        tech_events = result.get("instrumentInfo", {}).get("technicalEvents", {})
        for term in ["shortTerm", "intermediateTerm", "longTerm"]:
            outlook = tech_events.get(f"{term}Outlook", {})
            insights[f"{term}_direction"] = outlook.get("direction")
            insights[f"{term}_score"] = outlook.get("score")
            insights[f"{term}_stateDescription"] = outlook.get("stateDescription")

        # Extract Company Snapshot (if available)
        snapshot = result.get("companySnapshot", {})
        company_metrics = snapshot.get("company", {})
        sector_metrics = snapshot.get("sector", {})
        insights["company_innovativeness"] = company_metrics.get("innovativeness")
        insights["company_hiring"] = company_metrics.get("hiring")
        insights["company_sustainability"] = company_metrics.get("sustainability")
        insights["company_insiderSentiments"] = company_metrics.get("insiderSentiments")
        insights["sector_hiring"] = sector_metrics.get("hiring") # Example sector metric

        # Extract Valuation (if available)
        valuation = result.get("instrumentInfo", {}).get("valuation", {})
        insights["valuation_description"] = valuation.get("description")
        insights["valuation_discount"] = valuation.get("discount")
        insights["valuation_relativeValue"] = valuation.get("relativeValue")

        # Extract Recommendation (if available)
        recommendation = result.get("recommendation", {})
        insights["recommendation_targetPrice"] = recommendation.get("targetPrice")
        insights["recommendation_rating"] = recommendation.get("rating")

        # Convert insights dict to DataFrame
        # Note: This creates a single row DataFrame as insights are typically point-in-time snapshots from the API call
        df_insights = pd.DataFrame([insights])

        # Save processed insights data
        output_path = os.path.join(processed_data_dir, f"{symbol}_processed_insights.csv")
        df_insights.to_csv(output_path, index=False)
        print(f"Successfully processed and saved insights data for {symbol} to {output_path}")
        return df_insights

    except Exception as e:
        print(f"Error processing insights data for {symbol}: {e}")
        return None

# Process insights data for all relevant symbols
processed_insights_dfs = {}
for symbol in symbols:
    processed_df = process_insights_data(symbol)
    if processed_df is not None:
        processed_insights_dfs[symbol] = processed_df

print("\nFinished processing all insights data.")

# Example: Display processed AAPL insights data
if "AAPL" in processed_insights_dfs:
    print("\nSample processed insights data for AAPL:")
    print(processed_insights_dfs["AAPL"].to_string())

