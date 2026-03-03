from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


def generate_student_report(data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph("<b>Student Report</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    # Student details
    student = data["student"]
    details = [
        ["Name", student["name"]],
        ["Student ID", student["student_id"]],
        ["Batch", student["batch"]],
        ["Email", student.get("email", "-")],
    ]
    table = Table(details, colWidths=[120, 350])
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,0), (0,-1), colors.lightgrey),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 16))

    # Generic section renderer
    def add_section(title, headers, rows):
        elements.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))
        elements.append(Spacer(1, 8))
        if rows:
            table = Table([headers] + rows)
            table.setStyle(TableStyle([
                ("GRID", (0,0), (-1,-1), 1, colors.black),
                ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("No records available.", styles["Normal"]))
        elements.append(Spacer(1, 16))

    # Attendance
    add_section(
        "Attendance",
        ["Session", "Status", "Duration (min)"],
        data["attendance"]
    )

    # Tasks
    add_section(
        "Tasks",
        ["Task", "Marks", "Status"],
        data["tasks"]
    )

    # Viva
    add_section(
        "Viva",
        ["Subject", "Marks", "Status"],
        data["viva"]
    )

    # Exams
    add_section(
        "Exams",
        ["Exam", "Marks", "Status"],
        data["exams"]
    )

    doc.build(elements)
    buffer.seek(0)
    return buffer