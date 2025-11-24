# GroupDocs Landing Page Link Validator

A validation tool that checks the GroupDocs products landing page (index page at https://products.groupdocs.com/) to ensure it contains all products from the product versions JSON file and that all required links are present.

## Features

- Fetches product data from the product_versions.json file
- **Ignores CLI and UI products** (e.g., Conversion-CLI, Editor.UI, Viewer.UI)
- Validates that the landing page contains links to all product families
- Validates that the landing page contains links to all individual product pages (by platform)
- **Generates a comprehensive markdown report** (`validation_report.md`) with all found links and validation results

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python validate_landing_page_links.py
```

## Output

The tool will:
1. Fetch the product versions JSON file
2. Parse the landing page HTML (https://products.groupdocs.com/)
3. Validate that all products (excluding CLI/UI products) have family links on the landing page
4. Validate that all products have individual product links (by platform) on the landing page
5. Print a summary of errors and warnings
6. Generate a markdown report (`validation_report.md`) containing:
   - Summary statistics
   - All found family page links
   - All found individual product links from the landing page
   - Any errors or warnings encountered
7. Generate a JSON output (`product_links.json`) containing:
   - Generated timestamp
   - Links structure with family and platform links for each product

## Report Format

The generated `validation_report.md` includes:
- **Summary**: Total products validated, links found, error/warning counts
- **Found Links on Landing Page**: 
  - Family page links discovered on the landing page
  - Individual product links discovered on the landing page
- **Errors & Warnings**: Detailed list of any issues found (missing links, etc.)

The generated `product_links.json` includes:
- **generatedAt**: ISO timestamp when the report was generated
- **links**: Object with product names as keys, each containing:
  - **family**: URL to the product family page
  - **net**, **java**, **nodejs-java**, **python-net**: URLs to platform-specific product pages (or `null` if not found)

## GitHub Actions Workflow

The repository includes a GitHub Actions workflow (`.github/workflows/landing-page-validation.yml`) that:
- Runs daily at 08:00 UTC
- Validates the landing page
- Creates or updates a GitHub issue if validation errors are found
- Uploads validation reports as artifacts

## Requirements

- Python 3.7+
- requests
- beautifulsoup4
- lxml

