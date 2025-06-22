"""
Main script for running Weather Shopper tests
"""
import subprocess
import sys

def run_tests():
    """Run the Weather Shopper tests with the specified browser"""
    
    # Default to chromium if no browser specified
    browser = "chromium"
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        browser = sys.argv[1].lower()
        
    # Validate browser option
    valid_browsers = ["chromium", "firefox", "webkit"]
    if browser not in valid_browsers:
        print(f"Invalid browser: {browser}")
        print(f"Valid options are: {', '.join(valid_browsers)}")
        return
    
    print(f"Running tests with {browser} browser...")
    
    # Build the pytest command
    cmd = [
        "pytest", 
        "tests/test_weather_shopper.py", 
        f"--browser-type={browser}",
        "-v"
    ]
    
    # Execute the command
    subprocess.run(cmd)

if __name__ == "__main__":
    run_tests()
 