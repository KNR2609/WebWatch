import json
from monitor import check_website
from rich.table import Table
from rich.console import Console
from rich import box

console = Console()

def get_row_color(status):
    if status == "Very Slow":
        return "yellow"
    elif status == "Server Down":
        return "red"
    elif status in ["Forbidden", "Not Found"]:
        return "magenta"
    else:
        return None

def build_table(results):
    table = Table(title="WebWatch Monitoring", box=box.SIMPLE_HEAVY)

    table.add_column("Website Name", style="bold")
    table.add_column("URL")
    table.add_column("Status")
    table.add_column("Response Time (ms)")
    table.add_column("HTTP Code")
    table.add_column("HTTP Message")

    for result in results:
        row_color = get_row_color(result.status)

        table.add_row(
            result.name,
            result.url,
            result.status,
            f"{round(result.response_time, 2)}" if result.response_time else "N/A",
            str(result.status_code) if result.status_code else "N/A",
            result.http_message if result.http_message else "N/A",
            style=row_color
        )

    return table

def build_single_row(result):
    table = Table(title="Website View", box=box.SIMPLE_HEAVY)

    table.add_column("Website Name", style="bold")
    table.add_column("URL")
    table.add_column("Status")
    table.add_column("Response Time (ms)")
    table.add_column("HTTP Code")
    table.add_column("HTTP Message")

    row_color = get_row_color(result.status)

    table.add_row(
        result.name,
        result.url,
        result.status,
        f"{round(result.response_time, 2)}" if result.response_time else "N/A",
        str(result.status_code) if result.status_code else "N/A",
        result.http_message if result.http_message else "N/A",
        style=row_color
    )

    return table

def main():
    try:
        with open("sites.json") as f:
            sites = json.load(f)
    except FileNotFoundError:
        print("sites.json not found!")
        return

    # Run monitoring once
    results = []
    for site in sites:
        results.append(check_website(site["name"], site["url"]))

    # Print full table first
    console.print(build_table(results))

    # Search mode
    while True:
        search_name = console.input(
            "\nEnter website name to view (or type 'exit' to quit): "
        ).strip()

        if search_name.lower() == "exit":
            break

        matched = next(
            (r for r in results if r.name.lower() == search_name.lower()),
            None
        )

        if matched:
            console.print(build_single_row(matched))
        else:
            console.print("[red]Website not found.[/red]")

if __name__ == "__main__":
    main()
