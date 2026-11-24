import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "source_companies", ROOT / "scripts" / "source_companies.py")
SOURCE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SOURCE)


class SourceCompaniesTests(unittest.TestCase):
    def test_parse_exa_results(self):
        output = """Title: Acme | Product
URL: https://www.acme.com/product
Published: N/A
Author: N/A
Highlights:
Acme provides automated incident response.

---

Title: Example
URL: https://example.org/
Highlights:
Example text.
"""
        rows = SOURCE.parse_exa(output)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["url"], "https://www.acme.com/product")
        self.assertIn("incident response", rows[0]["summary"])

    def test_page_parser_reads_metadata_and_visible_text(self):
        parser = SOURCE.PageParser()
        parser.feed("""<html><head><title>Acme</title>
            <meta name="description" content="Acme protects cloud systems.">
            <script>hidden()</script></head><body>Managed response</body></html>""")
        self.assertEqual(parser.title, "Acme")
        self.assertEqual(parser.description, "Acme protects cloud systems.")
        self.assertIn("Managed response", parser.text)
        self.assertNotIn("hidden", parser.text)

    def test_merge_keeps_manual_rows_and_replaces_generated_rows(self):
        cols = SOURCE.DEFAULT_COLUMNS
        existing = [
            {"company": "Manual", "url": "https://manual.test", "evidence_type": "manual"},
            {"company": "Old", "url": "https://old.test", "evidence_type": "exa_web_search"},
        ]
        generated = [
            {"company": "New", "url": "https://new.test", "evidence_type": "company_website"},
        ]
        rows, manual_count = SOURCE.merge_rows(existing, generated, cols, 30)
        self.assertEqual(manual_count, 1)
        self.assertEqual([row["company"] for row in rows], ["Manual", "New"])

    def test_root_domain_normalizes_documentation_hosts(self):
        self.assertEqual(SOURCE.root_domain("https://docs.faro.io/start"), "faro.io")
        self.assertEqual(SOURCE.root_domain("https://acme.co.uk/about"), "acme.co.uk")

    def test_company_name_uses_domain_for_marketing_titles(self):
        name = SOURCE.company_name("Automated crypto perpetual futures trading", "tradefloor.co")
        self.assertEqual(name, "Tradefloor")


if __name__ == "__main__":
    unittest.main()
