from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.timezone import now

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Table,
    TableStyle,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm

# =========================
# MODEL IMPORTS (CORRECT)
# =========================
from apps.students.models import Student, Attendance
from apps.evaluation.models import (
    VivaRecord,
    TaskSubmission,
    StudentExam,
)

# =====================================================
# Helper styles
# =====================================================
def section_title(text):
    return Paragraph(
        f"<b>{text.upper()}</b>",
        ParagraphStyle(
            name="SectionTitle",
            fontSize=12,
            spaceBefore=14,
            spaceAfter=8
        )
    )


def styled_table(data, col_widths=None):
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


# =====================================================
# MAIN PDF VIEW
# =====================================================
def student_report_pdf(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'inline; filename="student_{student.student_id}_report.pdf"'
    )

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    styles = getSampleStyleSheet()
    story = []

    # =========================
    # TITLE
    # =========================
    story.append(Paragraph("<b>STUDENT REPORT</b>", styles["Title"]))
    story.append(Spacer(1, 12))

    # =========================
    # STUDENT DETAILS
    # =========================
    story.append(section_title("Student Details"))

    story.append(styled_table(
        [
            ["Student Name", student.name],
            ["Student ID", student.student_id],
            ["Batch", str(student.batch)],
        ],
        col_widths=[6 * cm, 8 * cm]
    ))

    # =========================
    # ATTENDANCE SUMMARY
    # =========================
    story.append(section_title("Attendance Summary"))

    total = Attendance.objects.filter(student=student).count()
    present = Attendance.objects.filter(student=student, status="PRESENT").count()
    absent = Attendance.objects.filter(student=student, status="ABSENT").count()
    late = Attendance.objects.filter(student=student, status="LATE").count()

    story.append(styled_table(
        [
            ["Total Sessions", "Present", "Absent", "Late"],
            [total, present, absent, late],
        ]
    ))

    # =========================
    # VIVA DETAILS
    # =========================
    story.append(section_title("Viva Details"))

    viva_qs = VivaRecord.objects.filter(student=student)

    if viva_qs.exists():
        data = [["Date", "Subject / Session", "Marks", "Status"]]

        for v in viva_qs:
            # Determine date safely
            viva_date = "-"
            if v.conducted_at:
                viva_date = v.conducted_at.strftime("%d-%m-%Y")
            elif v.viva_session:
                viva_date = v.viva_session.date.strftime("%d-%m-%Y")

            subject = (
                v.viva_session.subject
                if v.viva_session else "Lab Viva"
            )

            data.append([
                viva_date,
                subject,
                v.marks if v.marks is not None else "-",
                v.status.title(),
            ])

        story.append(styled_table(data))
    else:
        story.append(Paragraph("No viva records found.", styles["Normal"]))

    # =========================
    # TASK EVALUATION
    # =========================
    story.append(section_title("Task Evaluation"))

    task_qs = TaskSubmission.objects.filter(student=student)

    if task_qs.exists():
        data = [["Task", "Marks", "Status", "Submitted On"]]

        for t in task_qs:
            data.append([
                t.task.title,
                t.marks if t.marks is not None else "-",
                t.status.title(),
                t.submitted_at.strftime("%d-%m-%Y"),
            ])

        story.append(styled_table(data))
    else:
        story.append(Paragraph("No task submissions found.", styles["Normal"]))

    # =========================
    # EXAM PERFORMANCE
    # =========================
    story.append(section_title("Exam Performance"))

    exam_qs = StudentExam.objects.filter(student=student)

    if exam_qs.exists():
        data = [["Exam", "Marks", "Status"]]

        for e in exam_qs:
            data.append([
                e.session.title,
                e.marks if e.marks is not None else "-",
                e.status.title(),
            ])

        story.append(styled_table(data))
    else:
        story.append(Paragraph("No exam records found.", styles["Normal"]))

    # =========================
    # FOOTER
    # =========================
    story.append(Spacer(1, 20))
    story.append(Paragraph(
        f"<font size='9'>Generated on: {now().strftime('%d %b %Y, %I:%M %p')}</font>",
        styles["Normal"]
    ))

    doc.build(story)
    return response