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
        
        # Create result.csv file immediately with headers
        result_file = 'result.csv'
        result_file_exists = os.path.exists(result_file)
        
        if not result_file_exists:
            # Create new result.csv with headers
            result_df = pd.DataFrame(columns=['first_name', 'phone_number'])
            result_df.to_csv(result_file, index=False)
            print(f"Created {result_file} file")
        else:
            print(f"Using existing {result_file} file")
        
        # Process each row one by one
        for index, row in df.iterrows():
            email = row['email']
            first_name = row['first_name']
            
            print(f"Processing: {first_name} - {email}")
            
            try:
                # Step 1: Get snippets for the email
                snippets = get_snippets(email)
                
                if not snippets:
                    print(f"  No snippets found for {email}")
                    # Delete this row from original CSV immediately
                    df = df.drop(index)
                    df.to_csv(csv_file_path, index=False)
                    print(f"  ✓ Deleted row from original CSV (no snippets)")
                    continue
                
                # Step 2: Extract phone numbers from snippets
                phone_numbers = extract_phone_numbers(snippets)
                
                if not phone_numbers:
                    print(f"  No phone numbers found for {email}")
                    # Delete this row from original CSV immediately
                    df = df.drop(index)
                    df.to_csv(csv_file_path, index=False)
                    print(f"  ✓ Deleted row from original CSV (no phone numbers)")
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
                    # Save immediately to result.csv
                    new_match = {
                        'first_name': first_name,
                        'phone_number': matched_phone
                    }
                    
                    # Simple append to result.csv
                    try:
                        # Read existing file or create new one
                        if os.path.exists(result_file):
                            existing_df = pd.read_csv(result_file)
                            new_row_df = pd.DataFrame([new_match])
                            updated_df = pd.concat([existing_df, new_row_df], ignore_index=True)
                        else:
                            updated_df = pd.DataFrame([new_match])
                        
                        # Save to file
                        updated_df.to_csv(result_file, index=False)
                        print(f"  ✓ SUCCESS: {first_name} -> {matched_phone} (saved to {result_file})")
                        
                    except Exception as e:
                        print(f"  ❌ ERROR saving to {result_file}: {str(e)}")
                        # Continue processing but don't delete the row
                        continue
                    
                    # Delete this row from original CSV immediately after successful save
                    df = df.drop(index)
                    df.to_csv(csv_file_path, index=False)
                    print(f"  ✓ Deleted row from original CSV (successful match)")
                    
                else:
                    print(f"  ✗ No matching names found for any phone numbers")
                    # Delete this row from original CSV immediately
                    df = df.drop(index)
                    df.to_csv(csv_file_path, index=False)
                    print(f"  ✓ Deleted row from original CSV (no match)")
                
            except Exception as e:
                print(f"  Error processing {email}: {str(e)}")
                print(f"  ⚠ KEEPING row in original CSV due to technical error")
                # Don't delete this row - keep it for retry
                continue
        
        # Step 5: Summary
        print(f"\nProcess completed!")
        print(f"Original CSV now has {len(df)} remaining rows")
        
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        return

if __name__ == "__main__":
    process_csv_for_phone_extraction()
