import csv
import unittest
from decimal import Decimal, ROUND_HALF_UP
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def percentage(numerator, denominator):
    if numerator is None or denominator is None or denominator == 0:
        return None
    return Decimal(str(numerator)) / Decimal(str(denominator)) * 100


def formatted(value, places=2):
    if value is None:
        return "—"
    precision = Decimal(1).scaleb(-places)
    return str(value.quantize(precision, rounding=ROUND_HALF_UP)).replace(".", ",")


class DashboardParser(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.tags = []
        self.ids = set()
        self.links = []
        self.rows = []
        self.row = None
        self.cell = None
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        self.tags.append((tag, attributes))
        if "id" in attributes:
            self.ids.add(attributes["id"])
        if tag == "a":
            self.links.append(attributes.get("href", ""))
        if tag == "tr" and any(key.startswith("data-") for key in attributes):
            self.row = {"attrs": attributes, "cells": []}
        if tag in ("td", "th") and self.row is not None:
            self.cell = []

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.row is not None and self.cell is not None:
            self.row["cells"].append("".join(self.cell).strip())
            self.cell = None
        if tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None


class DashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / "index.html").read_text()
        cls.html = DashboardParser(cls.source)

    def rows(self, dimension):
        return [row for row in self.html.rows if f"data-{dimension}" in row["attrs"]]

    def test_product_commissions_and_roi(self):
        self.assertEqual(len(self.rows("product")), 3)
        for row in self.rows("product"):
            data = row["attrs"]
            price = Decimal(data["data-price"])
            sales = int(data["data-sales"])
            commission = Decimal(data["data-commission"])
            cost = Decimal(data["data-cost"])
            self.assertEqual(price * Decimal("0.15") * sales, commission)
            self.assertEqual(row["cells"][2], formatted(price * Decimal("0.15")) + " €")
            self.assertEqual(row["cells"][-1], formatted(percentage(commission - cost, cost), 1) + " %")

    def test_totals_reconcile_across_all_three_dimensions(self):
        for dimension in ("product", "platform", "campaign"):
            for field, expected in (("sales", 842), ("commission", 9666), ("cost", 2800)):
                self.assertEqual(sum(int(row["attrs"][f"data-{field}"]) for row in self.rows(dimension)), expected)
        self.assertEqual(formatted(percentage(9666 - 2800, 2800), 1), "245,2")

    def test_platform_rates_match_display(self):
        for row in self.rows("platform"):
            data = row["attrs"]
            reach = int(data["data-reach"])
            self.assertEqual(row["cells"][2], formatted(percentage(int(data["data-interactions"]), reach)) + " %")
            self.assertEqual(row["cells"][4], formatted(percentage(int(data["data-sales"]), reach), 3) + " %")
            self.assertEqual(row["cells"][-1], formatted(percentage(int(data["data-commission"]) - int(data["data-cost"]), int(data["data-cost"])), 1) + " %")
        for field, expected in (("reach", 1240000), ("interactions", 84560), ("impressions", 2480000)):
            self.assertEqual(sum(int(row["attrs"][f"data-{field}"]) for row in self.rows("platform")), expected)

    def test_global_kpi_rates(self):
        self.assertIn(formatted(percentage(842, 1240000), 3) + " %", self.source)
        self.assertIn(formatted(percentage(84560, 1240000)) + " %", self.source)
        self.assertIn(formatted(percentage(9666 - 8150, 8150), 1) + " %", self.source)
        self.assertIn(formatted(percentage(842 - 748, 748), 1) + " %", self.source)

    def test_zero_and_missing_data_never_divide(self):
        for numerator, denominator in ((10, 0), (None, 5), (5, None), (0, 0)):
            self.assertEqual(formatted(percentage(numerator, denominator)), "—")
        self.assertEqual(formatted(percentage(0, 100)), "0,00")
        self.assertIn("Otras plataformas", self.source)

    def test_daily_chart_reconciles(self):
        daily = [int(attrs["title"].split(": ")[1].split(" ")[0]) for tag, attrs in self.html.tags if "title" in attrs and "oct:" in attrs["title"] and "€" in attrs["title"]]
        self.assertEqual(len(daily), 15)
        self.assertEqual(sum(daily), 9666)
        activity = [int(attrs["title"].split(": ")[1].split(" ")[0]) for tag, attrs in self.html.tags if "publicaci" in attrs.get("title", "")]
        self.assertEqual(sum(activity), 32)

    def test_semantics_responsive_and_no_prohibited_technology(self):
        tags = [tag for tag, attrs in self.html.tags]
        for tag in ("header", "nav", "main", "section", "article", "table", "caption", "thead", "tbody", "th"):
            self.assertIn(tag, tags)
        self.assertEqual(tags.count("h1"), 1)
        self.assertEqual(tags.count("table"), 3)
        self.assertNotIn("script", tags)
        self.assertNotIn("style", tags)
        self.assertNotIn("cdn.tailwindcss.com", self.source)
        self.assertNotIn("@tailwindcss/browser", self.source)
        for prefix in ("sm:", "md:", "lg:"):
            self.assertIn(prefix, self.source)
        for section in ("resumen", "rendimiento", "operaciones", "alertas"):
            self.assertIn(section, self.html.ids)
        for tag, attrs in self.html.tags:
            self.assertNotIn("style", attrs)
            if tag == "th":
                self.assertIn(attrs.get("scope"), ("row", "col"))
            if tag == "img":
                self.assertIn("alt", attrs)

    def test_navigation_and_local_assets_exist(self):
        for href in self.html.links:
            if href.startswith("#"):
                self.assertIn(href[1:], self.html.ids)
            elif href.startswith("./"):
                self.assertTrue((ROOT / href).exists())
        self.assertTrue((ROOT / "dist/styles.css").is_file())

    def test_csv_matches_html(self):
        with (ROOT / "data/informe-octubre.csv").open(newline="") as source:
            records = list(csv.DictReader(source, delimiter=";"))
        total = next(row for row in records if row["tipo"] == "total")
        self.assertEqual(int(total["ventas"]), 842)
        self.assertEqual(int(total["comisiones_eur"]), 9666)
        self.assertEqual(int(total["costes_eur"]), 2800)
        for kind in ("producto", "plataforma", "campana"):
            rows = [row for row in records if row["tipo"] == kind and row["datos"] == "DEMOSTRACION"]
            self.assertEqual(sum(int(row["ventas"]) for row in rows), 842)
            self.assertEqual(sum(int(row["comisiones_eur"]) for row in rows), 9666)


if __name__ == "__main__":
    unittest.main()