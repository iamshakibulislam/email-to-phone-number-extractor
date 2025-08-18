import csv
import os
import pandas as pd
from custom_functions import get_snippets, extract_phone_numbers, visit_and_extract_phone_info

def process_csv_for_phone_extraction():
    """
    Ultimate function to process CSV file:
    1. Read CSV with email and first_name columns
    2. Find phone numbers for each email
    3. Match found names with CSV first_name (case insensitive, partial match)
    4. Create result.csv with successful matches
    5. Remove processed rows from original CSV
    """
    
    # Get CSV file path from user
    csv_file_path = input("Enter the path to your CSV file: ").strip().strip('"')
    
    # Check if file exists
    if not os.path.exists(csv_file_path):
        print(f"Error: File '{csv_file_path}' not found.")
        return
    
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file_path)
        
        # Check if required columns exist
        if 'email' not in df.columns or 'first_name' not in df.columns:
            print("Error: CSV file must contain 'email' and 'first_name' columns.")
            return
        
        print(f"Processing {len(df)} records...")
        
        # Lists to store results and rows to remove
        successful_matches = []
        rows_to_remove = []
        
        # Process each row
        for index, row in df.iterrows():
            email = row['email']
            first_name = row['first_name']
            
            print(f"Processing: {first_name} - {email}")
            
            try:
                # Step 1: Get snippets for the email
                snippets = get_snippets(email)
                
                if not snippets:
                    print(f"  No snippets found for {email}")
                    rows_to_remove.append(index)
                    continue
                
                # Step 2: Extract phone numbers from snippets
                phone_numbers = extract_phone_numbers(snippets)
                
                if not phone_numbers:
                    print(f"  No phone numbers found for {email}")
                    rows_to_remove.append(index)
                    continue
                
                print(f"  Found {len(phone_numbers)} phone number(s): {phone_numbers}")
                
                # Step 3: Check each phone number for name match
                matched_phone = None
                matched_name = None
                
                for phone in phone_numbers:
                    try:
                        found_name = visit_and_extract_phone_info(phone)
                        
                        if found_name:
                            print(f"    Phone {phone} -> Name: {found_name}")
                            
                            # Case insensitive partial match check
                            if first_name.lower() in found_name.lower():
                                print(f"    ✓ Name match found! '{first_name}' is in '{found_name}'")
                                matched_phone = phone
                                matched_name = found_name
                                break
                            else:
                                print(f"    ✗ No match: '{first_name}' not in '{found_name}'")
                        else:
                            print(f"    Phone {phone} -> No name found")
                            
                    except Exception as e:
                        print(f"    Error checking phone {phone}: {str(e)}")
                        continue
                
                # Step 4: Handle the result
                if matched_phone:
                    # Add to successful matches
                    successful_matches.append({
                        'first_name': first_name,
                        'phone_number': matched_phone
                    })
                    print(f"  ✓ SUCCESS: {first_name} -> {matched_phone}")
                else:
                    print(f"  ✗ No matching names found for any phone numbers")
                
                # Always remove the row from original CSV (whether successful or not)
                rows_to_remove.append(index)
                
            except Exception as e:
                print(f"  Error processing {email}: {str(e)}")
                rows_to_remove.append(index)
                continue
        
        # Step 5: Save results and update original CSV
        if successful_matches:
            # Create or append to result.csv
            result_df = pd.DataFrame(successful_matches)
            result_file = 'result.csv'
            
            if os.path.exists(result_file):
                # Append to existing file
                existing_df = pd.read_csv(result_file)
                combined_df = pd.concat([existing_df, result_df], ignore_index=True)
                combined_df.to_csv(result_file, index=False)
                print(f"\nAppended {len(successful_matches)} successful matches to existing {result_file}")
            else:
                # Create new file
                result_df.to_csv(result_file, index=False)
                print(f"\nCreated {result_file} with {len(successful_matches)} successful matches")
        else:
            print("\nNo successful matches found.")
        
        # Step 6: Remove processed rows from original CSV
        if rows_to_remove:
            # Remove rows and save back to original file
            df_updated = df.drop(rows_to_remove)
            df_updated.to_csv(csv_file_path, index=False)
            print(f"Removed {len(rows_to_remove)} processed rows from original CSV")
            print(f"Original CSV now has {len(df_updated)} remaining rows")
        
        print("\nProcess completed!")
        
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        return

if __name__ == "__main__":
    process_csv_for_phone_extraction()
