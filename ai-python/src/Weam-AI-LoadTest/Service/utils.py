from fpdf import FPDF
from datetime import datetime
import os

class PDFReport:
    def __init__(self, title="API Response Times Report"):
        self.title = title
        self.response_times = []
        self.pdf = FPDF()

    def add_response_time(self, method, url, time_taken, status_code):
        self.response_times.append({
            "method": method,
            "url": url,
            "time_taken": time_taken,
            "status_code": status_code
        })

    def calculate_statistics(self):
        times = [entry["time_taken"] for entry in self.response_times]
        success_count = sum(1 for entry in self.response_times if entry["status_code"] in (200, 207))
        failure_count = len(self.response_times) - success_count
        
        stats = {
            "average": sum(times) / len(times) if times else 0,
            "minimum": min(times) if times else 0,
            "maximum": max(times) if times else 0,
            "total": sum(times) if times else 0,
            "count": len(times),
            "success": success_count,
            "failure": failure_count
        }
        return stats

    def create_pdf(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs('Reports', exist_ok=True)
        file_name = os.path.join('Reports', f"api_response_times_{timestamp}.pdf")

        self.pdf.add_page()
        self.add_title_section()
        self.add_statistics_section()
        self.add_response_times_table()

        self.pdf.output(file_name)
        print(f"PDF report saved as {file_name}")

    def add_title_section(self):
        """Adds the title and subtitle sections to the PDF."""
        self.pdf.set_fill_color(70, 130, 180)  # Steel blue for title background
        self.pdf.set_text_color(255, 255, 255)
        self.pdf.set_font("Arial", "B", size=20)
        self.pdf.cell(0, 14, txt="API Response Times Report", ln=True, align='C', fill=True)
        
        self.pdf.set_text_color(50, 50, 50)  # Dark gray for subtitle
        self.pdf.set_font("Arial", "I", size=10)
        self.pdf.cell(0, 12, txt=f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
        self.pdf.ln(5)
        self.pdf.line(10, self.pdf.get_y(), 200, self.pdf.get_y())  # Line for a professional look
        self.pdf.ln(8)

    def add_statistics_section(self):
        """Adds the statistics summary section to the PDF."""
        stats = self.calculate_statistics()
        
        self.pdf.set_font("Arial", "B", size=14)
        self.pdf.cell(0, 12, txt="Statistics Summary", ln=True, align='L')
        self.pdf.set_fill_color(240, 248, 255)  # Alice blue background for stats
        self.pdf.set_font("Arial", size=12)
        self.pdf.ln(4)

        # Display statistics in a more refined table format
        self.add_statistic_row("Total Requests", str(stats['count']))
        self.add_statistic_row("Total Time (seconds)", f"{stats['total']:.2f}")
        self.add_statistic_row("Average Time (seconds)", f"{stats['average']:.2f}")
        self.add_statistic_row("Minimum Time (seconds)", f"{stats['minimum']:.2f}")
        self.add_statistic_row("Maximum Time (seconds)", f"{stats['maximum']:.2f}")
        self.add_statistic_row("Total Successes", str(stats['success']))
        self.add_statistic_row("Total Failures", str(stats['failure']))

        self.pdf.ln(8)

    def add_statistic_row(self, label, value):
        """Helper function to add a row in the statistics summary with improved style."""
        self.pdf.set_text_color(50, 50, 50)  # Consistent dark gray text color
        self.pdf.cell(90, 8, txt=label, border=0)
        self.pdf.cell(50, 8, txt=value, ln=True, align='L')

    def add_response_times_table(self):
        """Adds the detailed response times table to the PDF with professional styling."""
        self.pdf.set_font("Arial", "B", size=11)
        self.pdf.set_fill_color(220, 230, 255)  # Light blue for header background
        self.pdf.cell(10, 10, txt="#", border=1, fill=True, align='C')
        self.pdf.cell(20, 10, txt="Method", border=1, fill=True, align='C')
        self.pdf.cell(90, 10, txt="URL", border=1, fill=True, align='C')
        self.pdf.cell(30, 10, txt="Time Taken (s)", border=1, fill=True, align='C')
        self.pdf.cell(30, 10, txt="Status Code", border=1, fill=True, align='C')
        self.pdf.ln()

        for i, entry in enumerate(self.response_times, start=1):
            self.add_response_time_row(i, entry)

    def add_response_time_row(self, index, entry):
        """Helper function to add a row in the response times table with conditional styling."""
        status_code = entry["status_code"]
        if status_code == 200:
            self.pdf.set_fill_color(240, 255, 240)  # Light green for success
        elif 300 <= status_code < 500:
            self.pdf.set_fill_color(255, 239, 213)  # Light yellow for warnings
        elif status_code >= 500:
            self.pdf.set_fill_color(255, 228, 225)  # Light pink for errors

        # Populate each row with response data
        self.pdf.cell(10, 8, txt=str(index), border=1, fill=True, align='C')
        self.pdf.cell(20, 8, txt=entry["method"], border=1, fill=True, align='C')
        self.pdf.cell(90, 8, txt=entry["url"], border=1, fill=True, align='L')
        self.pdf.cell(30, 8, txt=f"{entry['time_taken']:.2f}", border=1, fill=True, align='C')
        self.pdf.cell(30, 8, txt=str(entry["status_code"]), border=1, fill=True, align='C')
        self.pdf.ln()
