# GroupDocs Landing Page Link Validator

A validation tool that checks the GroupDocs products landing page to ensure it contains all products from the product versions JSON file and that all required links are present.

## Validation Report

**Generated:** 2025-12-09 06:29:39

**Landing Page:** https://products.groupdocs.com/

**Summary**

- **Total Products Validated:** 16
- **Product Family Links Found:** 16
- **Product Links Found:** 49
- **Errors:** 2
- **Warnings:** 0

| Product | Family Page | .NET | Java | Node.js via Java | Python via .NET |
|---------|:------------:|:----------------:|:----------------:|:----------------:|:----------------:|
| Annotation | [✓](https://products.groupdocs.com/annotation/) | [✓](https://products.groupdocs.com/annotation/net/) | [✓](https://products.groupdocs.com/annotation/java/) | | |
| Assembly | [✓](https://products.groupdocs.com/assembly/) | [✓](https://products.groupdocs.com/assembly/net/) | [✓](https://products.groupdocs.com/assembly/java/) | | [✓](https://products.groupdocs.com/assembly/python-net/) |
| Classification | [✓](https://products.groupdocs.com/classification/) | [✓](https://products.groupdocs.com/classification/net/) | | | |
| Comparison | [✓](https://products.groupdocs.com/comparison/) | [✓](https://products.groupdocs.com/comparison/net/) | [✓](https://products.groupdocs.com/comparison/java/) | [✓](https://products.groupdocs.com/comparison/nodejs-java/) | [✓](https://products.groupdocs.com/comparison/python-net/) |
| Conversion | [✓](https://products.groupdocs.com/conversion/) | [✓](https://products.groupdocs.com/conversion/net/) | [✓](https://products.groupdocs.com/conversion/java/) | [✓](https://products.groupdocs.com/conversion/nodejs-java/) | [✓](https://products.groupdocs.com/conversion/python-net/) |
| Editor | [✓](https://products.groupdocs.com/editor/) | [✓](https://products.groupdocs.com/editor/net/) | [✓](https://products.groupdocs.com/editor/java/) | [✓](https://products.groupdocs.com/editor/nodejs-java/) | |
| Markdown | [✓](https://products.groupdocs.com/markdown/) | [✓](https://products.groupdocs.com/markdown/net/) | | | |
| Merger | [✓](https://products.groupdocs.com/merger/) | [✓](https://products.groupdocs.com/merger/net/) | [✓](https://products.groupdocs.com/merger/java/) | [✓](https://products.groupdocs.com/merger/nodejs-java/) | [✓](https://products.groupdocs.com/merger/python-net/) |
| Metadata | [✓](https://products.groupdocs.com/metadata/) | [✓](https://products.groupdocs.com/metadata/net/) | [✓](https://products.groupdocs.com/metadata/java/) | [✓](https://products.groupdocs.com/metadata/nodejs-java/) | [✓](https://products.groupdocs.com/metadata/python-net/) |
| Parser | [✓](https://products.groupdocs.com/parser/) | [✓](https://products.groupdocs.com/parser/net/) | [✓](https://products.groupdocs.com/parser/java/) | | |
| Redaction | [✓](https://products.groupdocs.com/redaction/) | [✓](https://products.groupdocs.com/redaction/net/) | [✓](https://products.groupdocs.com/redaction/java/) | | [✓](https://products.groupdocs.com/redaction/python-net/) |
| Search | [✓](https://products.groupdocs.com/search/) | [✓](https://products.groupdocs.com/search/net/) | [✓](https://products.groupdocs.com/search/java/) | [✓](https://products.groupdocs.com/search/nodejs-java/) | |
| Signature | [✓](https://products.groupdocs.com/signature/) | [✓](https://products.groupdocs.com/signature/net/) | [✓](https://products.groupdocs.com/signature/java/) | [✓](https://products.groupdocs.com/signature/nodejs-java/) | [✓](https://products.groupdocs.com/signature/python-net/) |
| Total | [✓](https://products.groupdocs.com/total/) | [✓](https://products.groupdocs.com/total/net/) | [✓](https://products.groupdocs.com/total/java/) | | [✓](https://products.groupdocs.com/total/python-net/) |
| Viewer | [✓](https://products.groupdocs.com/viewer/) | [✓](https://products.groupdocs.com/viewer/net/) | [✓](https://products.groupdocs.com/viewer/java/) | [✓](https://products.groupdocs.com/viewer/nodejs-java/) | [✓](https://products.groupdocs.com/viewer/python-net/) |
| Watermark | [✓](https://products.groupdocs.com/watermark/) | [✓](https://products.groupdocs.com/watermark/net/) | [✓](https://products.groupdocs.com/watermark/java/) | [✓](https://products.groupdocs.com/watermark/nodejs-java/) | [✓](https://products.groupdocs.com/watermark/python-net/) |

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python validate_landing_page_links.py
```

## Output

The tool generates:
- `validation_report.md` - Markdown report with validation results and found links
- `product_links.json` - JSON file with all product links

## GitHub Actions

The workflow runs daily at 06:00 UTC and automatically creates GitHub issues if validation errors are found.

