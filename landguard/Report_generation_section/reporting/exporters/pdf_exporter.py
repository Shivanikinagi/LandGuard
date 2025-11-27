"""
LandGuard Phase 4: PDF Exporter
Converts HTML reports to PDF format
"""

from typing import Optional
import logging


logger = logging.getLogger(__name__)


class PDFExporter:
    """
    Export reports to PDF format
    Uses HTML as intermediate format and converts to PDF
    """
    
    def __init__(self):
        self.has_weasyprint = self._check_weasyprint()
        self.has_pdfkit = self._check_pdfkit()
    
    def _check_weasyprint(self) -> bool:
        """Check if WeasyPrint is available"""
        try:
            import weasyprint
            return True
        except ImportError:
            logger.warning("WeasyPrint not installed. PDF generation will use alternative method.")
            return False
    
    def _check_pdfkit(self) -> bool:
        """Check if pdfkit is available"""
        try:
            import pdfkit
            return True
        except ImportError:
            logger.warning("pdfkit not installed.")
            return False
    
    def export(self, report) -> bytes:
        """
        Export report to PDF
        
        Args:
            report: Report object to export
        
        Returns:
            PDF as bytes
        """
        # First generate HTML
        from .html_exporter import HTMLExporter
        html_exporter = HTMLExporter()
        html_content = html_exporter.export(report)
        
        # Convert HTML to PDF
        if self.has_weasyprint:
            return self._convert_with_weasyprint(html_content)
        elif self.has_pdfkit:
            return self._convert_with_pdfkit(html_content)
        else:
            return self._convert_fallback(html_content, report)
    
    def _convert_with_weasyprint(self, html_content: str) -> bytes:
        """Convert HTML to PDF using WeasyPrint"""
        try:
            from weasyprint import HTML, CSS
            from io import BytesIO
            
            # Create PDF
            pdf_file = BytesIO()
            HTML(string=html_content).write_pdf(pdf_file)
            
            return pdf_file.getvalue()
            
        except Exception as e:
            logger.error(f"WeasyPrint conversion failed: {e}")
            return self._convert_fallback(html_content, None)
    
    def _convert_with_pdfkit(self, html_content: str) -> bytes:
        """Convert HTML to PDF using pdfkit"""
        try:
            import pdfkit
            
            options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'no-outline': None,
                'enable-local-file-access': None
            }
            
            pdf_bytes = pdfkit.from_string(html_content, False, options=options)
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"pdfkit conversion failed: {e}")
            return self._convert_fallback(html_content, None)
    
    def _convert_fallback(self, html_content: str, report=None) -> bytes:
        """
        Fallback: Return HTML as bytes with instructions
        This is used when no PDF library is available
        """
        logger.warning("No PDF library available. Returning HTML with PDF conversion instructions.")
        
        instructions = """
        <!--
        PDF CONVERSION INSTRUCTIONS:
        
        This HTML file can be converted to PDF using:
        1. Your web browser (Print -> Save as PDF)
        2. Install WeasyPrint: pip install weasyprint
        3. Install wkhtmltopdf and pdfkit: pip install pdfkit
        
        Or use online converters like:
        - https://www.html2pdf.com/
        - https://pdfcrowd.com/
        -->
        """
        
        html_with_instructions = instructions + html_content
        return html_with_instructions.encode('utf-8')


# Export
__all__ = ['PDFExporter']