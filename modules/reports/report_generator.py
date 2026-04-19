import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

from database import get_connection
from ui.utils import to_urdu_numerals, format_date_urdu

class ReportGenerator:
    def __init__(self):
        self.output_dir = "D:/Madrassa Management System/reports/"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Font configuration
        self.font_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets", "fonts")
        self.font_path = os.path.join(self.font_dir, "Jameel Noori Nastaleeq Regular.ttf")
        self.font_name = "NotoNastaliq"
        self._register_fonts()
        
        self.madrassa_name = "مدارسہ مینجمنٹ سسٹم"
        
        self.months_urdu = {
            1: 'جنوری', 2: 'فروری', 3: 'مارچ', 4: 'اپریل',
            5: 'مئی', 6: 'جون', 7: 'جولائی', 8: 'اگست',
            9: 'ستمبر', 10: 'اکتوبر', 11: 'نومبر', 12: 'دسمبر'
        }

    def _register_fonts(self):
        """Register Urdu font for PDF generation."""
        try:
            if os.path.exists(self.font_path):
                pdfmetrics.registerFont(TTFont(self.font_name, self.font_path))
            else:
                print(f"Warning: Font file not found at {self.font_path}. Using default font.")
                self.font_name = "Helvetica"
        except Exception as e:
            print(f"Error registering font: {e}")
            self.font_name = "Helvetica"

    def _reverse_text(self, text):
        """Helper to reverse Urdu text for RTL display."""
        if not text:
            return ""
        return str(text)[::-1]

    def _draw_urdu_text(self, c, text, x, y, font_size=12, align='right'):
        """Draw Urdu text on canvas with RTL handling."""
        c.setFont(self.font_name, font_size)
        rev_text = self._reverse_text(text)
        
        if align == 'right':
            c.drawRightString(x, y, rev_text)
        elif align == 'center':
            c.drawCentredString(x, y, rev_text)
        else:
            c.drawString(x, y, rev_text)

    def generate_student_report(self, student_id, output_path=None):
        """Generate comprehensive student report."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Fetch student bio
            cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
            student = cursor.fetchone()
            if not student: return None
            
            cols = [c[0] for c in cursor.description]
            student_dict = dict(zip(cols, student))
            
            if not output_path:
                filename = f"student_report_{student_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
                output_path = os.path.join(self.output_dir, filename)
            
            c = canvas.Canvas(output_path, pagesize=A4)
            width, height = A4
            
            # Header
            self._draw_urdu_text(c, self.madrassa_name, width/2, height - 50, 18, 'center')
            self._draw_urdu_text(c, "طالب علم کی تفصیلی رپورٹ", width/2, height - 80, 16, 'center')
            c.line(50, height - 90, width - 50, height - 90)
            
            # Student Info
            y = height - 120
            info_labels = [
                f"نام: {student_dict['full_name']}",
                f"ولدیت: {student_dict['father_name']}",
                f"کلاس: {student_dict['class_name']}",
                f"رول نمبر: {to_urdu_numerals(student_dict['registration_number'])}",
                f"رابطہ: {to_urdu_numerals(student_dict['phone_number'])}"
            ]
            
            for label in info_labels:
                self._draw_urdu_text(c, label, width - 60, y, 12)
                y -= 25
            
            # Fee Summary Placeholder (Simplified for logic proof)
            y -= 20
            self._draw_urdu_text(c, "فیس کی تفصیلات", width - 60, y, 14)
            y -= 30
            # Fetch fee history
            cursor.execute("SELECT month, year, amount, status FROM fees WHERE student_id = ? ORDER BY year DESC, month DESC LIMIT 5", (student_id,))
            fees = cursor.fetchall()
            
            # Draw Table Header
            c.setFont(self.font_name, 10)
            headers = ["حیثیت", "رقم", "سال", "مہینہ"]
            x_positions = [100, 200, 300, 400]
            for i, h in enumerate(headers):
                self._draw_urdu_text(c, h, width - x_positions[i], y, 10)
            
            y -= 20
            for fee in fees:
                month_name = self.months_urdu.get(int(fee[0]), fee[0])
                data = [
                    "ادا شدہ" if fee[3] == 'paid' else "غیر ادا شدہ",
                    to_urdu_numerals(fee[2]),
                    to_urdu_numerals(fee[1]),
                    month_name
                ]
                for i, d in enumerate(data):
                    self._draw_urdu_text(c, d, width - x_positions[i], y, 10)
                y -= 20
            
            # Footer
            c.setFont(self.font_name, 8)
            footer_text = f"رپورٹ تیار کرنے کی تاریخ: {to_urdu_numerals(datetime.now().strftime('%d-%m-%Y'))}"
            self._draw_urdu_text(c, footer_text, width/2, 50, 8, 'center')
            
            c.save()
            return output_path
        except Exception as e:
            print(f"Error generating student report: {e}")
            return None
        finally:
            if 'conn' in locals(): conn.close()

    def generate_fee_summary_report(self, month, year, output_path=None):
        """Generate monthly fee collection report."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Fetch matching fees
            cursor.execute("""
                SELECT s.full_name, s.class_name, f.amount, f.paid_date, f.receipt_number 
                FROM fees f 
                JOIN students s ON f.student_id = s.id 
                WHERE f.month = ? AND f.year = ?
            """, (str(month).zfill(2), str(year)))
            fees = cursor.fetchall()
            
            total_collected = sum(f[2] for f in fees)
            
            if not output_path:
                filename = f"fee_report_{month}_{year}_{datetime.now().strftime('%Y%m%d')}.pdf"
                output_path = os.path.join(self.output_dir, filename)
            
            c = canvas.Canvas(output_path, pagesize=A4)
            width, height = A4
            
            self._draw_urdu_text(c, "ماہانہ فیس رپورٹ", width/2, height - 50, 18, 'center')
            month_name = self.months_urdu.get(int(month), month)
            self._draw_urdu_text(c, f"مہینہ: {month_name} {to_urdu_numerals(year)}", width/2, height - 80, 14, 'center')
            
            y = height - 120
            self._draw_urdu_text(c, f"کل وصولی: روپے {to_urdu_numerals(int(total_collected))}", width - 60, y, 14)
            
            # Simplified Table
            y -= 40
            headers = ["رسید نمبر", "تاریخ", "رقم", "کلاس", "طالب علم"]
            x_pos = [100, 200, 300, 400, 500]
            for i, h in enumerate(headers):
                self._draw_urdu_text(c, h, width - x_pos[i], y, 10)
            
            y -= 20
            for f in fees[:20]: # Limit for sample
                row = [f[4], to_urdu_numerals(f[3]), to_urdu_numerals(int(f[2])), f[1], f[0]]
                for i, d in enumerate(row):
                    self._draw_urdu_text(c, d, width - x_pos[i], y, 9)
                y -= 20
            
            c.save()
            return output_path
        except Exception as e:
            print(f"Error generating fee report: {e}")
            return None
        finally:
            if 'conn' in locals(): conn.close()

    def generate_donation_report(self, start_date, end_date, output_path=None):
        """Generate donation report."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT donor_name, amount, donation_type, donation_date, receipt_number 
                FROM donations 
                WHERE donation_date BETWEEN ? AND ?
            """, (start_date, end_date))
            donations = cursor.fetchall()
            
            total = sum(d[1] for d in donations)
            
            if not output_path:
                filename = f"donation_report_{datetime.now().strftime('%Y%m%d')}.pdf"
                output_path = os.path.join(self.output_dir, filename)
            
            c = canvas.Canvas(output_path, pagesize=A4)
            width, height = A4
            
            self._draw_urdu_text(c, "عطیات کی رپورٹ", width/2, height - 50, 18, 'center')
            date_range = f"{to_urdu_numerals(start_date)} سے {to_urdu_numerals(end_date)} تک"
            self._draw_urdu_text(c, date_range, width/2, height - 80, 12, 'center')
            
            y = height - 120
            self._draw_urdu_text(c, f"کل عطیات: روپے {to_urdu_numerals(int(total))}", width - 60, y, 14)
            
            y -= 40
            headers = ["رسید", "تاریخ", "قسم", "رقم", "نام"]
            x_pos = [80, 180, 280, 380, 500]
            for i, h in enumerate(headers):
                self._draw_urdu_text(c, h, width - x_pos[i], y, 10)
            
            y -= 20
            for d in donations[:25]:
                row = [d[4], to_urdu_numerals(d[3]), d[2], to_urdu_numerals(int(d[1])), d[0]]
                for i, row_data in enumerate(row):
                    self._draw_urdu_text(c, row_data, width - x_pos[i], y, 9)
                y -= 20
            
            c.save()
            return output_path
        except Exception as e:
            print(f"Error generating donation report: {e}")
            return None
        finally:
            if 'conn' in locals(): conn.close()

    def generate_attendance_report(self, class_id, month, year, output_path=None):
        """Generate class attendance report."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT class_name FROM classes WHERE id = ?", (class_id,))
            class_row = cursor.fetchone()
            class_name = class_row[0] if class_row else "نامعلوم"
            
            if not output_path:
                filename = f"attendance_report_{class_id}_{month}_{year}.pdf"
                output_path = os.path.join(self.output_dir, filename)
            
            c = canvas.Canvas(output_path, pagesize=A4)
            width, height = A4
            
            self._draw_urdu_text(c, "حاضری کی رپورٹ", width/2, height - 50, 18, 'center')
            month_name = self.months_urdu.get(int(month), month)
            self._draw_urdu_text(c, f"کلاس: {class_name} | مہینہ: {month_name} {to_urdu_numerals(year)}", width/2, height - 80, 14, 'center')
            
            # Fetch students and attendance summaries
            date_pattern = f"{year}-{str(month).zfill(2)}-%"
            cursor.execute("""
                SELECT s.full_name, 
                       SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END),
                       SUM(CASE WHEN a.status = 'absent' THEN 1 ELSE 0 END),
                       SUM(CASE WHEN a.status = 'leave' THEN 1 ELSE 0 END)
                FROM students s
                LEFT JOIN attendance a ON s.id = a.person_id AND a.person_type = 'student' AND a.date LIKE ?
                WHERE s.class_name = ?
                GROUP BY s.id
            """, (date_pattern, class_name))
            records = cursor.fetchall()
            
            y = height - 130
            headers = ["رخصت", "غیر حاضر", "حاضر", "طالب علم کا نام"]
            x_pos = [100, 200, 300, 500]
            for i, h in enumerate(headers):
                self._draw_urdu_text(c, h, width - x_pos[i], y, 10, 'right')
                
            y -= 25
            for r in records:
                row_data = [to_urdu_numerals(r[3] or 0), to_urdu_numerals(r[2] or 0), to_urdu_numerals(r[1] or 0), r[0]]
                for i, d in enumerate(row_data):
                    self._draw_urdu_text(c, d, width - x_pos[i], y, 10)
                y -= 20
                if y < 50:
                    c.showPage()
                    y = height - 50
            
            c.save()
            return output_path
        except Exception as e:
            print(f"Error generating attendance report: {e}")
            return None
        finally:
            if 'conn' in locals(): conn.close()

    def generate_exam_result_report(self, exam_id, output_path=None):
        """Generate exam results report."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT e.exam_name, c.class_name, s.subject_name, e.exam_date, e.total_marks, e.passing_marks
                FROM exams e
                JOIN classes c ON e.class_id = c.id
                JOIN subjects s ON e.subject_id = s.id
                WHERE e.id = ?
            """, (exam_id,))
            exam = cursor.fetchone()
            if not exam: return None
            
            if not output_path:
                filename = f"exam_results_{exam_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
                output_path = os.path.join(self.output_dir, filename)
            
            c = canvas.Canvas(output_path, pagesize=A4)
            width, height = A4
            
            self._draw_urdu_text(c, "امتحانی نتائج کی رپورٹ", width/2, height - 50, 18, 'center')
            sub_head = f"{exam[0]} - {exam[1]} ({exam[2]})"
            self._draw_urdu_text(c, sub_head, width/2, height - 80, 14, 'center')
            
            y = height - 120
            details = [
                f"تاریخ: {to_urdu_numerals(exam[3])}",
                f"کل نمبر: {to_urdu_numerals(exam[4])}",
                f"پاسنگ نمبر: {to_urdu_numerals(exam[5])}"
            ]
            for d in details:
                self._draw_urdu_text(c, d, width - 60, y, 11)
                y -= 20
            
            # Results table
            y -= 20
            cursor.execute("""
                SELECT s.full_name, s.registration_number, r.obtained_marks, r.grade, r.status
                FROM results r
                JOIN students s ON r.student_id = s.id
                WHERE r.exam_id = ?
                ORDER BY r.obtained_marks DESC
            """, (exam_id,))
            results = cursor.fetchall()
            
            headers = ["حیثیت", "گریڈ", "نمبر", "رول نمبر", "نام"]
            x_pos = [80, 150, 220, 320, 500]
            for i, h in enumerate(headers):
                self._draw_urdu_text(c, h, width - x_pos[i], y, 10)
            
            y -= 25
            for r in results:
                row = [r[4], r[3], to_urdu_numerals(r[2]), to_urdu_numerals(r[1]), r[0]]
                for i, d in enumerate(row):
                    self._draw_urdu_text(c, d, width - x_pos[i], y, 9)
                y -= 20
            
            c.save()
            return output_path
        except Exception as e:
            print(f"Error generating exam report: {e}")
            return None
        finally:
            if 'conn' in locals(): conn.close()

    def generate_employee_report(self, output_path=None):
        """Generate employee summary report."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT full_name, designation, salary, joining_date, phone_number FROM employees WHERE status = 'active'")
            employees = cursor.fetchall()
            
            total_salary = sum(e[2] for e in employees)
            
            if not output_path:
                filename = f"employees_report_{datetime.now().strftime('%Y%m%d')}.pdf"
                output_path = os.path.join(self.output_dir, filename)
            
            c = canvas.Canvas(output_path, pagesize=A4)
            width, height = A4
            
            self._draw_urdu_text(c, "ملازمین کی رپورٹ", width/2, height - 50, 18, 'center')
            y = height - 100
            self._draw_urdu_text(c, f"کل ملازمین: {to_urdu_numerals(len(employees))}", width - 60, y, 12)
            y -= 20
            self._draw_urdu_text(c, f"کل ماہانہ تنخواہ: روپے {to_urdu_numerals(int(total_salary))}", width - 60, y, 12)
            
            y -= 40
            headers = ["رابطہ", "تاریخ شمولیت", "تنخواہ", "عہدہ", "نام"]
            x_pos = [100, 200, 300, 400, 500]
            for i, h in enumerate(headers):
                self._draw_urdu_text(c, h, width - x_pos[i], y, 10)
            
            y -= 25
            for e in employees:
                row = [to_urdu_numerals(e[4]), to_urdu_numerals(e[3]), to_urdu_numerals(int(e[2])), e[1], e[0]]
                for i, d in enumerate(row):
                    self._draw_urdu_text(c, d, width - x_pos[i], y, 9)
                y -= 20
            
            c.save()
            return output_path
        except Exception as e:
            print(f"Error generating employee report: {e}")
            return None
        finally:
            if 'conn' in locals(): conn.close()

    def generate_general_receipt(self, receipt_type, receipt_id, output_path=None):
        """Generate generic receipt for fees or donations."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            width, height = A4
            if receipt_type == 'fee':
                cursor.execute("""
                    SELECT f.receipt_number, s.full_name, s.registration_number, s.class_name, 
                           f.amount, f.month, f.year, f.paid_date 
                    FROM fees f JOIN students s ON f.student_id = s.id WHERE f.id = ?
                """, (receipt_id,))
                data = cursor.fetchone()
                if not data: return None
                
                title = "فیس رسید"
                details = [
                    f"رسید نمبر: {to_urdu_numerals(data[0])}",
                    f"نام طالب علم: {data[1]}",
                    f"رول نمبر: {to_urdu_numerals(data[2])}",
                    f"کلاس: {data[3]}",
                    f"رقم: روپے {to_urdu_numerals(int(data[4]))}",
                    f"مہینہ: {self.months_urdu.get(int(data[5]), data[5])} {to_urdu_numerals(data[6])}",
                    f"تاریخ ادائیگی: {to_urdu_numerals(data[7])}"
                ]
            else:
                cursor.execute("SELECT receipt_number, donor_name, amount, donation_type, donation_date, donor_contact FROM donations WHERE id = ?", (receipt_id,))
                data = cursor.fetchone()
                if not data: return None
                
                title = "عطیہ رسید"
                details = [
                    f"رسید نمبر: {to_urdu_numerals(data[0])}",
                    f"عطیہ دہندہ: {data[1]}",
                    f"رقم: روپے {to_urdu_numerals(int(data[2]))}",
                    f"عطیے کی قسم: {data[3]}",
                    f"تاریخ: {to_urdu_numerals(data[4])}",
                    f"رابطہ: {to_urdu_numerals(data[5])}"
                ]
            
            if not output_path:
                output_path = os.path.join(self.output_dir, f"receipt_{receipt_id}.pdf")
            
            c = canvas.Canvas(output_path, pagesize=(width, height/2)) # Half A4 size
            h = height/2
            
            self._draw_urdu_text(c, self.madrassa_name, width/2, h - 50, 18, 'center')
            self._draw_urdu_text(c, title, width/2, h - 80, 16, 'center')
            c.line(50, h - 90, width - 50, h - 90)
            
            y = h - 120
            for d in details:
                self._draw_urdu_text(c, d, width - 60, y, 12)
                y -= 25
            
            c.line(50, 50, 200, 50)
            self._draw_urdu_text(c, "دستخط وصول کنندہ", 125, 40, 10, 'center')
            
            c.save()
            return output_path
        except Exception as e:
            print(f"Error generating receipt: {e}")
            return None
        finally:
            if 'conn' in locals(): conn.close()
