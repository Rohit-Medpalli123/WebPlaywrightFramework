"""Run Weather Shopper tests with specified browser.

Simple command-line script to run tests with different browsers.
"""

import argparse
import multiprocessing
import subprocess
import sys
from typing import Dict, List, Any

# Available browsers
BROWSERS = ['chromium', 'firefox', 'webkit']


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.
    
    Returns:
        argparse.Namespace: Command line arguments.
    """
    parser = argparse.ArgumentParser(description='Run Weather Shopper tests')
    
    parser.add_argument('--browser', default='chromium',
                      choices=BROWSERS + ['all'],
                      help='Browser to use (default: chromium)')
                      
    parser.add_argument('--headless', action='store_true',
                      help='Run in headless mode')
                      
    parser.add_argument('--parallel', action='store_true',
                      help='Run tests in parallel')
                      
    parser.add_argument('--test', default='tests/test_weather_shopper.py',
                      help='Test file or test to run')
                      
    return parser.parse_args()


def create_commands(args: argparse.Namespace) -> tuple[List[str], List[List[str]]]:
    """Create pytest commands based on arguments.
    
    Args:
        args: Command line arguments.
        
    Returns:
        tuple: List of browsers and list of commands to run.
    """
    # Determine which browsers to run
    browsers = BROWSERS if args.browser == 'all' else [args.browser]
    
    # Create commands for each browser
    commands = []
    for browser in browsers:
        cmd = ['pytest', args.test, '-v', f'--browser-type={browser}']
        
        # Add headless mode if specified
        if args.headless:
            cmd.append('--headless')
            
        # When running in parallel, ensure each browser gets its own log file
        # by setting a unique log file name via environment variable
        if args.parallel and args.browser == 'all':
            # Use environment variable prefixing to ensure each browser gets a unique log file
            cmd = ["env", f"PYTEST_LOG_BROWSER={browser}"] + cmd
            
        commands.append(cmd)
        
    # Print run information
    mode = 'parallel' if args.parallel and len(browsers) > 1 else 'sequential'
    headless = 'in headless mode' if args.headless else ''
    print(f"Running tests {mode} on {', '.join(browsers)} {headless}")
    
    return browsers, commands


def run_commands(browsers: List[str], commands: List[List[str]], 
                parallel: bool = False) -> int:
    """Run commands in parallel or sequentially.
    
    Args:
        browsers: List of browsers being tested.
        commands: List of commands to run.
        parallel: Whether to run in parallel mode.
        
    Returns:
        int: Return code (0 for success, non-zero for failure).
    """
    if parallel and len(browsers) > 1:
        # Parallel execution using multiprocessing
        with multiprocessing.Pool(len(browsers)) as pool:
            results = pool.map(_run_command, commands)
    else:
        # Sequential execution
        results = []
        for i, cmd in enumerate(commands):
            if len(browsers) > 1:
                print(f"\nStarting tests with {browsers[i]} browser...")
            results.append(_run_command(cmd))
    
    # Return worst result (0 is success, highest number is worst failure)
    return max(results) if results else 1


def _run_command(cmd: List[str]) -> int:
    """Run a command and return its exit code.
    
    Args:
        cmd: Command to execute.
        
    Returns:
        int: Command exit code.
    """
    try:
        return subprocess.run(cmd, check=False).returncode
    except Exception as e:
        print(f"Error: {e}")
        return 1


def main() -> int:
    """Main entry point for the script.
    
    Returns:
        int: Exit code indicating success (0) or failure (non-zero).
    """
    args = parse_args()
    browsers, commands = create_commands(args)
    return run_commands(browsers, commands, args.parallel)


if __name__ == "__main__":
    sys.exit(main())