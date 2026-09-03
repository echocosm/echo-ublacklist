import requests

INPUT = "rules-list.txt"
OUTPUT = "stitcher-output.txt"

with open(INPUT, encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip()]

# Remove duplicate URLs while preserving order
urls = list(dict.fromkeys(urls))

print(f"Found {len(urls)} unique URLs")

with open(OUTPUT, "w", encoding="utf-8") as out:
    # Start marker
    out.write("# echo -------------------------------------- START OF AGGREGATION\n\n")

    for url in urls:
        print(f"Downloading: {url}")

        response = requests.get(url)
        response.raise_for_status()

        lines = response.text.splitlines()

        # Comment out everything between the --- markers
        inside_header = False

        for i, line in enumerate(lines):
            if line.strip() == "---":
                lines[i] = "#" + line
                inside_header = not inside_header
            elif inside_header:
                lines[i] = "#" + line

        out.write("\n".join(lines))
        out.write("\n\n")

    # End marker
    out.write("# echo -------------------------------------- END OF AGGREGATION\n")

print(f"\nDone! Created {OUTPUT}")