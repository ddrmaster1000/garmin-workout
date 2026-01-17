"""Example usage of WahooToGarminConverter with evaluation, retry, and upload."""

import json
import os
import sys
from getpass import getpass

from garth.exc import GarthException, GarthHTTPError
from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
)
from wahoo_to_garmin_converter import WahooToGarminConverter

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
TOKENSTORE = os.getenv("GARMINTOKENS") or "~/.garminconnect"

def get_mfa() -> str:
    """Get MFA code from user input."""
    return input("Enter MFA code: ").strip()


def init_api(email: str | None = None, password: str | None = None) -> Garmin | None:
    """Initialize Garmin API with smart error handling and recovery."""
    # First try to login with stored tokens
    try:
        print(f"Attempting to login using stored tokens from: {TOKENSTORE}")

        garmin = Garmin()
        garmin.login(TOKENSTORE)
        print("Successfully logged in using stored tokens!")
        return garmin

    except (
        FileNotFoundError,
        GarthHTTPError,
        GarminConnectAuthenticationError,
        GarminConnectConnectionError,
    ):
        print("No valid tokens found. Requesting fresh login credentials.")

    # Loop for credential entry with retry on auth failure
    while True:
        try:
            # Get credentials if not provided
            if not email or not password:
                email = input("Email address: ").strip()
                password = getpass("Password: ")

            print("Logging in with credentials...")
            garmin = Garmin(
                email=email, password=password, is_cn=False, return_on_mfa=True
            )
            result1, result2 = garmin.login()

            if result1 == "needs_mfa":
                print("Multi-factor authentication required")

                mfa_code = get_mfa()
                print("🔄 Submitting MFA code...")

                try:
                    garmin.resume_login(result2, mfa_code)
                    print("✅ MFA authentication successful!")

                except GarthHTTPError as garth_error:
                    # Handle specific HTTP errors from MFA
                    error_str = str(garth_error)
                    print(f"🔍 Debug: MFA error details: {error_str}")

                    if "429" in error_str and "Too Many Requests" in error_str:
                        print("❌ Too many MFA attempts")
                        print("💡 Please wait 30 minutes before trying again")
                        sys.exit(1)
                    elif "401" in error_str or "403" in error_str:
                        print("❌ Invalid MFA code")
                        print("💡 Please verify your MFA code and try again")
                        continue
                    else:
                        # Other HTTP errors - don't retry
                        print(f"❌ MFA authentication failed: {garth_error}")
                        sys.exit(1)

                except GarthException as garth_error:
                    print(f"❌ MFA authentication failed: {garth_error}")
                    print("💡 Please verify your MFA code and try again")
                    continue

            # Save tokens for future use
            garmin.garth.dump(TOKENSTORE)
            print(f"Login successful! Tokens saved to: {TOKENSTORE}")

            return garmin

        except GarminConnectAuthenticationError:
            print("❌ Authentication failed:")
            print("💡 Please check your username and password and try again")
            # Clear the provided credentials to force re-entry
            email = None
            password = None
            continue

        except (
            FileNotFoundError,
            GarthHTTPError,
            GarthException,
            GarminConnectConnectionError,
        ) as err:
            print(f"❌ Connection error: {err}")
            print("💡 Please check your internet connection and try again")
            return None

        except KeyboardInterrupt:
            print("\nLogin cancelled by user")
            return None


def main():
    """Convert example Wahoo workout with evaluation, retry, and upload."""
    print("Wahoo to Garmin Converter with Evaluation, Retry & Upload")
    print("=" * 60)
    
    # Initialize converter
    converter = WahooToGarminConverter(region_name="us-east-1")
    
    # Load the Wahoo workout text
    with open("example_wahoo_workout.txt", encoding="utf-8") as f:
        wahoo_text = f.read()
    
    print("\nConverting workout (auto-detecting type)...")
    print("-" * 60)
    
    # Convert with retry (auto-detect workout type)
    output_file = "generated_swimming_workout.py"
    success, message, workout = converter.convert_with_retry(
        wahoo_text,
        workout_type=None,  # Auto-detect from workout text
        output_file=output_file,
        max_retries=3
    )
    
    print("\n" + "=" * 60)
    print("CONVERSION RESULT")
    print("=" * 60)
    
    if success:
        print(f"✓ {message}")
        print(f"✓ Workout saved to: {output_file}")
        
        # Save JSON representation
        json_file = output_file.replace(".py", ".json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(workout.to_dict(), f, indent=2)
        print(f"✓ JSON saved to: {json_file}")
        
        # Ask if user wants to upload
        print("\n" + "=" * 60)
        print("UPLOAD TO GARMIN CONNECT")
        print("=" * 60)
        
        upload_choice = input("\nUpload workout to Garmin Connect? (y/n): ").strip().lower()
        
        if upload_choice == 'y':
            # Initialize Garmin API
            garmin_api = init_api()
            
            if garmin_api:
                try:
                    print(f"\n📤 Uploading workout to Garmin Connect...")
                    result = converter.upload_workout(workout, garmin_api)
                    
                    print("\n✓ Workout uploaded successfully!")
                    # print(f"Response: {json.dumps(result, indent=2)}")
                    
                except Exception as e:
                    print(f"\n✗ Upload failed: {e}")
                    sys.exit(1)
            else:
                print("\n✗ Could not login to Garmin Connect")
                sys.exit(1)
        else:
            print("\nSkipping upload.")
    else:
        print(f"✗ {message}")
        sys.exit(1)


if __name__ == "__main__":
    main()
