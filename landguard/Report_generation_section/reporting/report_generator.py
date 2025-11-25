import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

try:
    from weasyprint import HTML  # for PDF
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False


# ---------- Data Contract ----------

@dataclass
class ReportConfig:
    project_name: str = "LandGuard"
    organization: str = "Pied Piper Labs"
    include_pdf: bool = True
    include_csv: bool = True
    include_json: bool = True
    # add more flags later if needed


class ReportGenerator:
    """
    Takes analyzer output and generates:
    - HTML report (with charts)
    - Optional PDF (via WeasyPrint)
    - CSV summary
    - Dashboard JSON
    """

    def __init__(self, templates_dir: Optional[str] = None, config: Optional[ReportConfig] = None):
        base_dir = Path(__file__).resolve().parent
        self.templates_dir = Path(templates_dir) if templates_dir else base_dir / "templates"
        self.config = config or ReportConfig()

        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(["html", "xml"])
        )

    # ---------- PUBLIC API ----------

    def generate_all(
        self,
        analyzer_result: Dict[str, Any],
        output_dir: str,
        base_name: str,
    ) -> Dict[str, str]:
        """
        Generate HTML, PDF, CSV, JSON in one go.

        Returns a dict with paths to generated files.
        """
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)

        normalized = self._normalize_analyzer_result(analyzer_result)

        # HTML
        html_output_path = output_dir_path / f"{base_name}.html"
        html = self.render_html(normalized)
        html_output_path.write_text(html, encoding="utf-8")

        results = {"html": str(html_output_path)}

        # PDF
        if self.config.include_pdf and WEASYPRINT_AVAILABLE:
            pdf_output_path = output_dir_path / f"{base_name}.pdf"
            self.export_pdf(html, pdf_output_path)
            results["pdf"] = str(pdf_output_path)

        # CSV
        if self.config.include_csv:
            csv_output_path = output_dir_path / f"{base_name}.csv"
            self.export_csv(normalized, csv_output_path)
            results["csv"] = str(csv_output_path)

        # JSON
        if self.config.include_json:
            json_output_path = output_dir_path / f"{base_name}.json"
            self.export_json(normalized, json_output_path)
            results["json"] = str(json_output_path)

        return results

    def render_html(self, normalized: Dict[str, Any]) -> str:
        template = self.env.get_template("report.html")
        return template.render(
            report=normalized,
            generated_at=datetime.utcnow().isoformat() + "Z",
            project_name=self.config.project_name,
            organization=self.config.organization,
        )

    def export_pdf(self, html_str: str, output_path: Path) -> None:
        if not WEASYPRINT_AVAILABLE:
            raise RuntimeError("WeasyPrint is not installed. Run `pip install weasyprint`.")
        HTML(string=html_str).write_pdf(str(output_path))

    def export_csv(self, normalized: Dict[str, Any], output_path: Path) -> None:
        """
        Writes a flat CSV: one row per anomaly / issue.
        """
        rows = []

        for anomaly in normalized["anomalies"]:
            rows.append(
                {
                    "land_id": normalized["summary"]["land_id"],
                    "risk_score": normalized["summary"]["risk_score"],
                    "rule_id": anomaly.get("rule_id"),
                    "rule_name": anomaly.get("rule_name"),
                    "severity": anomaly.get("severity"),
                    "description": anomaly.get("description"),
                    "timestamp": anomaly.get("timestamp", ""),
                }
            )

        # Fallback: if no anomalies, add a summary row
        if not rows:
            rows.append(
                {
                    "land_id": normalized["summary"]["land_id"],
                    "risk_score": normalized["summary"]["risk_score"],
                    "rule_id": "",
                    "rule_name": "",
                    "severity": "NONE",
                    "description": "No anomalies detected",
                    "timestamp": "",
                }
            )

        with output_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "land_id",
                    "risk_score",
                    "rule_id",
                    "rule_name",
                    "severity",
                    "description",
                    "timestamp",
                ],
            )
            writer.writeheader()
            writer.writerows(rows)

    def export_json(self, normalized: Dict[str, Any], output_path: Path) -> None:
        """
        Dashboard-ready JSON. You can directly feed this to a React / Plotly frontend.
        """
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(normalized, f, indent=2, default=str)

    # ---------- INTERNAL: Normalization Layer ----------

    def _normalize_analyzer_result(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Shape whatever your analyzer returns into a stable schema for reporting.
        Adjust this to match your actual engine output.
        """

        # Example assumptions about `raw` keys (adapt to your real structure):
        # raw = {
        #   "land_id": "...",
        #   "owner": {...},
        #   "transactions": [...],
        #   "rules": [...],
        #   "anomalies": [...],
        #   "geo": {"lat": ..., "lon": ...},
        #   "stats": {...},
        # }

        land_id = raw.get("land_id", "UNKNOWN")
        owner = raw.get("owner", {})
        stats = raw.get("stats", {})
        rules = raw.get("rules", [])
        anomalies = raw.get("anomalies", [])
        transactions = raw.get("transactions", [])
        geo = raw.get("geo", {})

        # Compute summary numbers
        total_rules = len(rules)
        triggered_rules = [r for r in rules if r.get("triggered")]
        anomaly_count = len(anomalies)
        risk_score = stats.get("risk_score", self._compute_risk_score(triggered_rules, anomalies))

        # Prepare chart data
        rule_hit_counts = self._build_rule_hit_counts(rules)
        severity_distribution = self._build_severity_distribution(anomalies)
        timeline = self._build_timeline(transactions)

        normalized = {
            "summary": {
                "land_id": land_id,
                "owner_name": owner.get("name", "Unknown"),
                "location": owner.get("address", "Unknown"),
                "risk_score": risk_score,
                "total_rules": total_rules,
                "triggered_rule_count": len(triggered_rules),
                "anomaly_count": anomaly_count,
            },
            "rules": rules,
            "anomalies": anomalies,
            "transactions": transactions,
            "geo": geo,
            "charts": {
                "rule_hit_counts": rule_hit_counts,
                "severity_distribution": severity_distribution,
                "timeline": timeline,
            },
        }

        return normalized

    def _compute_risk_score(self, triggered_rules: List[Dict[str, Any]], anomalies: List[Dict[str, Any]]) -> float:
        """
        Simple fallback risk scoring. You can replace this with your ML score later.
        """
        base = 0.0
        for r in triggered_rules:
            severity = r.get("severity", "medium").lower()
            if severity == "low":
                base += 5
            elif severity == "medium":
                base += 10
            elif severity == "high":
                base += 20

        # anomalies bonus
        base += len(anomalies) * 2.5

        # cap at 100
        return min(base, 100.0)

    def _build_rule_hit_counts(self, rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        labels = []
        values = []
        for r in rules:
            labels.append(r.get("id", r.get("name", "rule")))
            values.append(int(r.get("hit_count", 1 if r.get("triggered") else 0)))
        return {"labels": labels, "values": values}

    def _build_severity_distribution(self, anomalies: List[Dict[str, Any]]) -> Dict[str, Any]:
        buckets = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for a in anomalies:
            sev = str(a.get("severity", "medium")).lower()
            if sev not in buckets:
                buckets[sev] = 0
            buckets[sev] += 1

        labels = list(buckets.keys())
        values = [buckets[k] for k in labels]
        return {"labels": labels, "values": values}

    def _build_timeline(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Expecting each transaction like:
        { "date": "2024-01-01", "amount": 1000000, "type": "sale" }
        """
        dates = []
        values = []
        for t in sorted(transactions, key=lambda x: x.get("date", "")):
            dates.append(t.get("date", ""))
            values.append(t.get("amount", 0))
        return {"dates": dates, "values": values}