#!/usr/bin/env python3
import requests, time, os, sys
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()
HUB = "https://us-central1-regenesis-art-hub.cloudfunctions.net/regenesis-hub-v1"

def get_data():
    """Get data from automation hub"""
    data = {}
    try:
        r = requests.get(HUB, timeout=3)
        data['hub'] = r.json()
    except:
        data['hub'] = {'status': 'offline'}
    try:
        r = requests.get(f"{HUB}/v1/financial", timeout=3)
        data['fin'] = r.json().get('financial', {})
    except:
        data['fin'] = {}
    try:
        r = requests.get(f"{HUB}/v1/artworks", timeout=3)
        data['arts'] = r.json().get('artworks', [])
    except:
        data['arts'] = []
    return data

def show_dash():
    """Display visual dashboard"""
    os.system('clear')
    data = get_data()
    
    # HEADER
    console.print("\n")
    console.print(Panel.fit(
        "[bold blue]🚀 DEEPSEEK BUSINESS AUTOMATION[/bold blue]",
        border_style="green"
    ))
    
    # STATUS TABLE
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("System", style="cyan", width=15)
    table.add_column("Status", style="green", width=15)
    table.add_column("Metrics", width=30)
    
    # Hub status
    hub_status = data['hub'].get('status', 'offline')
    table.add_row(
        "🤖 Hub",
        f"[green]{hub_status}[/green]" if hub_status == 'operational' else f"[red]{hub_status}[/red]",
        "v8.0"
    )
    
    # Financial status
    fin = data.get('fin', {})
    apv = fin.get('apv_total', 0)
    table.add_row(
        "💰 Financial",
        f"[yellow]${apv:.0f} APV[/yellow]",
        f"The Key: ${fin.get('the_key', {}).get('current', 0)}/{fin.get('the_key', {}).get('target', 6000)}"
    )
    
    # Artworks status
    arts = data.get('arts', [])
    count = len(arts)
    table.add_row(
        "🎨 Artworks",
        f"[cyan]{count}[/cyan]",
        f"Latest: {arts[-1].get('title', 'None') if arts else 'None'}"
    )
    
    console.print(table)
    console.print("\n")

    # PROGRESS BARS
    console.print("[bold]📊 Progress Gauges:[/bold]")
    
    # The Key progress
    key_current = fin.get('the_key', {}).get('current', 0)
    key_target = fin.get('the_key', {}).get('target', 6000)
    key_percent = (key_current / key_target * 100) if key_target > 0 else 0
    
    with Progress(
        TextColumn("[cyan]The Key[/cyan]"),
        BarColumn(bar_width=30),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        progress.add_task("", total=100, completed=key_percent)
    
    # APV progress for latest artwork
    if arts:
        latest = arts[-1]
        apv_current = latest.get('current_apv', 0)
        apv_target = latest.get('target_price', 100)
        apv_percent = (apv_current / apv_target * 100) if apv_target > 0 else 0
        
        console.print(f"\n[bold]🎯 {latest.get('title', 'Artwork')}:[/bold]")
        with Progress(
            TextColumn("[yellow]APV[/yellow]"),
            BarColumn(bar_width=30),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn(f"(${apv_current:.0f}/${apv_target})"),
        ) as progress:
            progress.add_task("", total=100, completed=apv_percent)
    
    console.print("\n")
    
    # COMMANDS PANEL
    commands = Panel(
        """[bold]⚡ Quick Commands:[/bold]
[yellow]1.[/yellow] Log hours: curl -X POST $HUB/v1/artworks/[ID]/log
[yellow]2.[/yellow] New artwork: curl -X POST $HUB/v1/artworks
[yellow]3.[/yellow] eBay listing: curl -X POST $HUB/v1/ebay/listing/[ID]
[yellow]4.[/yellow] View data: curl $HUB/v1/financial""",
        title="Automation Controls",
        border_style="blue"
    )
    
    console.print(commands)
    
    # FOOTER
    console.print("\n[dim]🔄 Auto-refresh: 10s | Press Ctrl+C to exit[/dim]")

def main():
    """Main loop"""
    try:
        while True:
            show_dash()
            time.sleep(10)
    except KeyboardInterrupt:
        console.print("\n[bold red]Dashboard stopped[/bold red]")
        sys.exit(0)

if __name__ == "__main__":
    main()
