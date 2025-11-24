#!/usr/bin/env python3
"""
GroupDocs Landing Page Links Validator

This tool validates that the GroupDocs products landing page https://products.groupdocs.com/
contains all products from the product_versions.json file and that all
required links are present on the landing page and family pages.
"""

import json
import re
import sys
from typing import Dict, List, Tuple
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup


class ProductValidator:
    def __init__(self, json_url: str, landing_page_url: str):
        self.json_url = json_url
        self.landing_page_url = landing_page_url
        self.base_url = "https://products.groupdocs.com"
        self.products_data = {}
        self.errors = []
        self.warnings = []
        self.found_links = {
            "family_links": {},
            "product_links": {},
            "family_page_validations": {}
        }
        
    def fetch_json(self) -> Dict:
        """Fetch and parse the product versions JSON file."""
        try:
            print(f"Fetching product versions from {self.json_url}...")
            response = requests.get(self.json_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            all_products = data.get("versions", {})
            
            # Filter out CLI and UI products
            self.products_data = {
                name: platforms 
                for name, platforms in all_products.items() 
                if not self.should_ignore_product(name)
            }
            
            ignored_count = len(all_products) - len(self.products_data)
            print(f"Found {len(all_products)} total products in JSON")
            print(f"Ignoring {ignored_count} CLI/UI products")
            print(f"Validating {len(self.products_data)} products")
            return self.products_data
        except Exception as e:
            self.errors.append(f"Failed to fetch JSON: {e}")
            return {}
    
    def should_ignore_product(self, product_name: str) -> bool:
        """Check if product should be ignored (CLI or UI products)."""
        name_lower = product_name.lower()
        return name_lower.endswith("-cli") or name_lower.endswith(".ui") or name_lower.endswith("-ui")
    
    def normalize_product_name(self, product_name: str) -> str:
        """Normalize product name for comparison (e.g., 'Total' -> 'total')."""
        # Remove 'GroupDocs.' prefix if present
        name = product_name.replace("GroupDocs.", "").strip()
        # Convert to lowercase
        name = name.lower()
        # Handle special cases - convert dots to hyphens
        name = name.replace(".", "-")
        return name
    
    def get_product_name_variations(self, product_name: str) -> List[str]:
        """Get possible URL variations for a product name."""
        normalized = self.normalize_product_name(product_name)
        variations = [normalized]
        
        # Try without -ui suffix (e.g., editor-ui -> editor)
        if normalized.endswith("-ui"):
            variations.append(normalized[:-3])
        
        # Try without -cli suffix
        if normalized.endswith("-cli"):
            variations.append(normalized[:-4])
        
        return variations
    
    def get_platform_slug(self, platform: str) -> str:
        """Convert platform key to URL slug."""
        platform_map = {
            "net": "net",
            "java": "java",
            "nodejs-java": "nodejs",
            "python-net": "python"
        }
        return platform_map.get(platform, platform)
    
    def validate_link(self, url: str) -> Tuple[int, bool]:
        """Validate a link by checking HTTP status and content. Returns (status_code, is_valid)."""
        try:
            response = requests.get(url, timeout=30, allow_redirects=True)
            status_code = response.status_code
            content = response.text
            
            # Valid if status is 200 and content is not empty
            is_valid = status_code == 200 and content and len(content.strip()) >= 100
            return status_code, is_valid
        except Exception:
            return 0, False
    
    def parse_landing_page(self) -> BeautifulSoup:
        """Fetch and parse the landing page HTML."""
        print(f"\nFetching landing page from {self.landing_page_url}...")
        try:
            response = requests.get(self.landing_page_url, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            if response.status_code != 200:
                self.errors.append(f"Landing page returned status {response.status_code}")
                return None
            
            content = response.text
            if not content or len(content.strip()) < 100:
                self.errors.append("Landing page content is empty or too short")
                return None
            
            return BeautifulSoup(content, 'html.parser')
        except Exception as e:
            self.errors.append(f"Failed to fetch landing page: {e}")
            return None
    
    def find_product_family_links(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Find all product family links on the landing page."""
        family_links = {}
        
        # Find all product items
        product_items = soup.find_all('div', class_='product-item')
        print(f"\nFound {len(product_items)} product items on landing page")
        
        for item in product_items:
            # Find the family link - pattern: /product-name/
            all_links = item.find_all('a', href=True)
            for link in all_links:
                href = link.get('href', '')
                # Match pattern like /total/ or /conversion/
                if re.match(r'^/[^/]+/$', href):
                    product_match = re.search(r'/([^/]+)/$', href)
                    if product_match:
                        product_name = product_match.group(1).lower()
                        # Normalize product name variations
                        if product_name not in family_links:
                            family_links[product_name] = href
                            full_url = urljoin(self.base_url, href)
                            self.found_links["family_links"][product_name] = full_url
                            print(f"  Found family link: {product_name} -> {href}")
        
        return family_links
    
    def find_individual_product_links(self, soup: BeautifulSoup) -> Dict[str, Dict[str, str]]:
        """Find all individual product links on the landing page."""
        product_links = {}
        
        # Find all links that match pattern /product/platform/
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href', '')
            # Match pattern like /total/net/ or /conversion/java/ or /total/python-net/ or /product/nodejs-java/
            # Also handle absolute URLs
            if href.startswith('/'):
                # Match only the actual URL patterns used
                match = re.search(r'/([^/]+)/(net|java|nodejs-java|python-net)/$', href)
                if match:
                    product_name = match.group(1).lower()
                    platform_url = match.group(2)
                    
                    # Normalize platform URLs to standard platform names
                    if platform_url == 'python-net':
                        platform = 'python'
                    elif platform_url == 'nodejs-java':
                        platform = 'nodejs'
                    else:
                        platform = platform_url
                    
                    if product_name not in product_links:
                        product_links[product_name] = {}
                    if platform not in product_links[product_name]:
                        product_links[product_name][platform] = href
                        full_url = urljoin(self.base_url, href)
                        if product_name not in self.found_links["product_links"]:
                            self.found_links["product_links"][product_name] = {}
                        self.found_links["product_links"][product_name][platform] = full_url
        
        return product_links
    
    def validate_landing_page_products(self, soup: BeautifulSoup):
        """Validate that landing page contains all products from JSON."""
        print("\n=== Validating Landing Page Products ===")
        
        family_links = self.find_product_family_links(soup)
        individual_links = self.find_individual_product_links(soup)
        
        # Check each product in JSON
        for product_name, platforms in self.products_data.items():
            variations = self.get_product_name_variations(product_name)
            found_family = False
            
            # Check if family link exists (try all variations)
            for variation in variations:
                if variation in family_links:
                    found_family = True
                    print(f"✓ {product_name} has family link ({variation})")
                    break
            
            if not found_family:
                self.errors.append(
                    f"Product '{product_name}' missing family link on landing page (tried: {', '.join(variations)})"
                )
            
            # Check individual product links for each platform
            for platform, version in platforms.items():
                if version is None:  # Skip if platform not available
                    continue
                
                platform_slug = self.get_platform_slug(platform)
                found_link = False
                
                # Try all variations
                for variation in variations:
                    if variation in individual_links:
                        if platform_slug in individual_links[variation]:
                            found_link = True
                            print(f"  ✓ {product_name} {platform} link found")
                            break
                
                if not found_link:
                    self.errors.append(
                        f"Product '{product_name}' missing {platform} link on landing page"
                    )
    
    def validate_family_pages(self):
        """Validate that family pages contain links to their product pages."""
        print("\n=== Validating Family Pages ===")
        
        for product_name, platforms in self.products_data.items():
            variations = self.get_product_name_variations(product_name)
            
            # Find family page URL
            family_url = None
            for variation in variations:
                if variation in self.found_links["family_links"]:
                    family_url = self.found_links["family_links"][variation]
                    break
            
            if not family_url:
                # Family page link not found on landing page, skip validation
                continue
            
            print(f"\nValidating family page for '{product_name}': {family_url}")
            
            # Fetch and parse family page
            try:
                response = requests.get(family_url, timeout=30, allow_redirects=True)
                if response.status_code != 200:
                    self.errors.append(
                        f"Family page for '{product_name}' returned status {response.status_code}: {family_url}"
                    )
                    continue
                
                content = response.text
                if not content or len(content.strip()) < 100:
                    self.errors.append(
                        f"Family page for '{product_name}' is empty or too short: {family_url}"
                    )
                    continue
                
                soup = BeautifulSoup(content, 'html.parser')
                
                # Find all product page links on the family page
                found_platform_links = {}
                all_links = soup.find_all('a', href=True)
                
                for link in all_links:
                    href = link.get('href', '')
                    if href.startswith('/'):
                        # Match pattern like /product/platform/ or /product/python-net/ or /product/nodejs-java/
                        match = re.search(r'/([^/]+)/(net|java|nodejs-java|python-net)/$', href)
                        if match:
                            found_product = match.group(1).lower()
                            platform_url = match.group(2)
                            
                            # Check if this link matches any variation of our product
                            if found_product in variations:
                                # Normalize platform URL
                                if platform_url == 'python-net':
                                    platform = 'python'
                                elif platform_url == 'nodejs-java':
                                    platform = 'nodejs'
                                else:
                                    platform = platform_url
                                
                                full_url = urljoin(self.base_url, href)
                                found_platform_links[platform] = full_url
                
                # Store validation results
                self.found_links["family_page_validations"][product_name] = {
                    "url": family_url,
                    "found_platform_links": found_platform_links
                }
                
                # Check if all expected platforms have links
                for platform, version in platforms.items():
                    if version is None:
                        continue
                    
                    platform_slug = self.get_platform_slug(platform)
                    if platform_slug not in found_platform_links:
                        # Determine expected URL pattern
                        if platform == "python-net":
                            expected_url_slug = "python-net"
                        elif platform == "nodejs-java":
                            expected_url_slug = "nodejs-java"
                        else:
                            expected_url_slug = platform_slug
                        
                        self.errors.append(
                            f"Family page for '{product_name}' missing {platform} link (expected: /{variations[0]}/{expected_url_slug}/)"
                        )
                    else:
                        print(f"  ✓ Found {platform} link on family page")
            
            except Exception as e:
                self.errors.append(
                    f"Failed to validate family page for '{product_name}': {e}"
                )
    
    def run(self):
        """Run all validation checks."""
        print("=" * 60)
        print("GroupDocs Landing Page Links Validator")
        print("=" * 60)
        
        # Fetch JSON
        if not self.fetch_json():
            print("\n❌ Failed to fetch product data")
            return False
        
        # Parse landing page
        soup = self.parse_landing_page()
        if soup is None:
            print("\n❌ Failed to parse landing page")
            return False
        
        # Validate landing page products
        self.validate_landing_page_products(soup)
        
        # Validate family pages contain product page links
        self.validate_family_pages()
        
        # Print summary
        print("\n" + "=" * 60)
        print("Validation Summary")
        print("=" * 60)
        
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ All validations passed!")
        
        # Generate markdown report
        self.generate_markdown_report()
        
        # Generate JSON output
        self.generate_json_output()
        
        return len(self.errors) == 0
    
    def generate_markdown_report(self):
        """Generate a markdown report with all found links and validation results."""
        report_lines = [
            "# GroupDocs Landing Page Links Validation Report",
            "",
            f"**Generated:** {self._get_timestamp()}",
            f"**Landing Page:** {self.landing_page_url}",
            "",
            "## Summary",
            "",
            f"- **Total Products Validated:** {len(self.products_data)}",
            f"- **Product Family Links Found:** {len(self.found_links['family_links'])}",
            f"- **Product Links Found:** {sum(len(platforms) for platforms in self.found_links['product_links'].values())}",
            f"- **Errors:** {len(self.errors)}",
            f"- **Warnings:** {len(self.warnings)}",
            "",
            "---",
            "",
            "## Product Links",
            "",
        ]
        
        # Collect all unique platforms from found links
        all_platforms = set()
        if self.found_links["product_links"]:
            for product_platforms in self.found_links["product_links"].values():
                all_platforms.update(product_platforms.keys())
        
        # Also check products_data to include platforms that should exist
        for platforms in self.products_data.values():
            for platform, version in platforms.items():
                if version is not None:
                    platform_slug = self.get_platform_slug(platform)
                    all_platforms.add(platform_slug)
        
        # Sort platforms in a consistent order
        platform_order = ["net", "java", "nodejs", "python"]
        sorted_platforms = sorted(all_platforms, key=lambda x: (
            platform_order.index(x) if x in platform_order else 999, x
        ))
        
        # Platform header mapping
        platform_headers = {
            "net": ".NET",
            "java": "Java",
            "nodejs": "Node.js via Java",
            "python": "Python via .NET"
        }
        
        if sorted_platforms:
            # Create table header with Family Page column
            header = "| Product | Family Page |"
            separator = "|---------|-------------|"
            for platform in sorted_platforms:
                platform_header = platform_headers.get(platform, platform)
                header += f" {platform_header} |"
                separator += "----------------|"
            report_lines.append(header)
            report_lines.append(separator)
            
            # Add rows for each product
            # Use products_data as source of truth to avoid duplicates
            all_products = sorted(self.products_data.keys())
            
            if all_products:
                print("\nValidating links...")
                for product_name in all_products:
                    # Normalize product name for lookup
                    variations = self.get_product_name_variations(product_name)
                    row = f"| {product_name} |"
                    
                    # Add family page link
                    family_link_found = False
                    for variation in variations:
                        if variation in self.found_links["family_links"]:
                            url = self.found_links["family_links"][variation]
                            status_code, is_valid = self.validate_link(url)
                            if is_valid:
                                row += f" [✓]({url}) |"
                            else:
                                row += f" [{status_code}]({url}) |"
                            family_link_found = True
                            break
                    
                    if not family_link_found:
                        row += " |"
                    
                    # Add platform links
                    for platform in sorted_platforms:
                        # Try to find link in any variation
                        link_found = False
                        for variation in variations:
                            if variation in self.found_links["product_links"]:
                                if platform in self.found_links["product_links"][variation]:
                                    url = self.found_links["product_links"][variation][platform]
                                    status_code, is_valid = self.validate_link(url)
                                    if is_valid:
                                        row += f" [✓]({url}) |"
                                    else:
                                        row += f" [{status_code}]({url}) |"
                                    link_found = True
                                    break
                        
                        if not link_found:
                            row += " |"
                    
                    report_lines.append(row)
            else:
                report_lines.append("| *No products found* |" + " |" * (1 + len(sorted_platforms)))
        else:
            report_lines.append("| *No platforms found* |")
        
        # Add errors and warnings
        if self.errors:
            report_lines.extend([
                "",
                "## Errors",
                "",
            ])
            for error in self.errors:
                report_lines.append(f"- ❌ {error}")
        
        if self.warnings:
            report_lines.extend([
                "",
                "## Warnings",
                "",
            ])
            for warning in self.warnings:
                report_lines.append(f"- ⚠️ {warning}")
        
        # Write report to file
        report_content = "\n".join(report_lines)
        report_filename = "validation_report.md"
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\n📄 Markdown report generated: {report_filename}")
    
    def generate_json_output(self):
        """Generate JSON output with product links similar to input JSON structure."""
        from datetime import datetime
        
        output_data = {
            "generatedAt": datetime.now().isoformat() + "Z",
            "links": {}
        }
        
        # Build links structure similar to input JSON
        for product_name in sorted(self.products_data.keys()):
            variations = self.get_product_name_variations(product_name)
            
            # Find family page link
            family_url = None
            for variation in variations:
                if variation in self.found_links["family_links"]:
                    family_url = self.found_links["family_links"][variation]
                    break
            
            # Build product links structure
            product_links = {}
            
            # Add family page link
            if family_url:
                product_links["family"] = family_url
            
            # Add platform links
            platforms = self.products_data[product_name]
            for platform, version in platforms.items():
                if version is None:
                    continue
                
                platform_slug = self.get_platform_slug(platform)
                
                # Find platform link
                platform_url = None
                for variation in variations:
                    if variation in self.found_links["product_links"]:
                        if platform_slug in self.found_links["product_links"][variation]:
                            platform_url = self.found_links["product_links"][variation][platform_slug]
                            break
                
                # Map platform key to JSON key
                platform_key_map = {
                    "net": "net",
                    "java": "java",
                    "nodejs": "nodejs-java",
                    "python": "python-net"
                }
                json_platform_key = platform_key_map.get(platform_slug, platform)
                
                if platform_url:
                    product_links[json_platform_key] = platform_url
                else:
                    product_links[json_platform_key] = None
            
            output_data["links"][product_name] = product_links
        
        # Write JSON to file
        json_filename = "product_links.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"📄 JSON output generated: {json_filename}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp as string."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    json_url = "https://raw.githubusercontent.com/vladimir-litvinchik/groupdocs-product-grid/refs/heads/main/product_versions.json"
    landing_page_url = "https://products.groupdocs.com/"
    
    validator = ProductValidator(json_url, landing_page_url)
    success = validator.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

