import pandas as pd
import googlemaps
import sys

def process_material_excel(excel_file, api_key):
    # Load Google Maps client
    gmaps = googlemaps.Client(key=api_key)

    # Load Excel sheets
    warehouses_df = pd.read_excel(excel_file, sheet_name="warehouse", engine="openpyxl")
    region_map_df = pd.read_excel(excel_file, sheet_name="region", engine="openpyxl")

    # --- Process 'warehouse' and 'region' mapping for other uses (if needed) ---
    region_to_warehouse = dict(zip(region_map_df["region"], region_map_df["warehouse"]))
    warehouse_to_coords = dict(zip(
        warehouses_df["Warehouse"],
        zip(warehouses_df["latitude"], warehouses_df["longitude"])
    ))

    # --- Process 'transportation' sheet ---
    try:
        transportation_df = pd.read_excel(excel_file, sheet_name="transportation", engine="openpyxl")
        driving_times = []
        distance_texts = []
        for idx, row in transportation_df.iterrows():
            # Format as 'longitude,latitude' for both origin and destination
            site_coords = f"{row['longitude']},{row['latitude']}"
            warehouse_name = row["warehouse"]
            warehouse_coords = warehouse_to_coords.get(warehouse_name)
            if not warehouse_coords:
                print(f"Missing warehouse coordinates for '{warehouse_name}'")
                driving_times.append(None)
                distance_texts.append(None)
                continue
            warehouse_coords_str = f"{warehouse_coords[1]},{warehouse_coords[0]}"  # longitude,latitude
            # Print what will be sent to Google Maps
            print(f"Row {idx}: Sending to Google Maps - origin: {site_coords}, destination: {warehouse_coords_str}")
            try:
                result = gmaps.distance_matrix(
                    origins=[site_coords],
                    destinations=[warehouse_coords_str],
                    mode="driving",
                    units="metric"
                )
                # Print the full response from Google Maps
                print(f"Row {idx}: Google Maps response: {result}")
                element = result["rows"][0]["elements"][0]
                if element.get("status") == "OK" and "duration" in element and "distance" in element:
                    duration_sec = element["duration"]["value"]
                    duration_min = round(duration_sec / 60, 2)
                    driving_times.append(duration_min)
                    distance_texts.append(element["distance"]["text"])
                else:
                    print(f"API response for row {idx}: {element}")
                    driving_times.append(None)
                    distance_texts.append(None)
            except Exception as e:
                print(f"Error processing row {idx} in transportation: {e}")
                driving_times.append(None)
                distance_texts.append(None)
        transportation_df["Distance"] = driving_times
        transportation_df["distance"] = distance_texts
        # Save back to the same Excel file
        with pd.ExcelWriter(excel_file, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            transportation_df.to_excel(writer, sheet_name="transportation", index=False)
        print(f"Updated driving times and distances saved to {excel_file} (sheet: transportation)")
    except Exception as e:
        print(f"Error processing 'transportation' sheet: {e}")

# Example usage
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # --- USER: Set your Excel file name and Google Maps API key here ---
    excel_file = "material.xlsx"  # Make sure this matches your file name
    google_api_key = os.getenv('GOOGLE_MAPS_API_KEY')  # Get from environment variable
    
    if not google_api_key:
        print("Error: GOOGLE_MAPS_API_KEY environment variable not set")
        print("Please set your Google Maps API key in a .env file or environment variable")
        sys.exit(1)

    process_material_excel(excel_file, google_api_key)