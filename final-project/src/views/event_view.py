# views/event_view.py
"""Modern view for displaying event details and attendance records."""

import flet as ft
from views.base_view import BaseView
from config.constants import PRIMARY_COLOR
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
import os


class EventView(BaseView):
    """Modern event detail with attendance log."""
    
    def build(self, event_id: str):
        """Build and return the event detail view."""
        event = self.db.get_event_by_id(event_id)
        if not event:
            self.page.go("/home")
            return ft.View("/", [ft.Container()])
        
        attendance = self.db.get_attendance_by_event(event_id)
        
        # Modern data table
        attendance_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Name", weight=ft.FontWeight.W_600, size=13)),
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.W_600, size=13)),
                ft.DataColumn(ft.Text("Time", weight=ft.FontWeight.W_600, size=13)),
                ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.W_600, size=13)),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(record['name'], size=13)),
                        ft.DataCell(ft.Text(user_id, size=13)),
                        ft.DataCell(ft.Text(record['time'], size=13)),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(
                                    record['status'],
                                    color=ft.Colors.WHITE,
                                    size=11,
                                    weight=ft.FontWeight.W_600,
                                ),
                                bgcolor=ft.Colors.GREEN_600,
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=8,
                            )
                        ),
                    ]
                ) for user_id, record in attendance.items()
            ] if attendance else [
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("No attendance records yet", italic=True, color=ft.Colors.GREY_500)),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                ])
            ],
            border=ft.border.all(1, ft.Colors.GREY_200),
            border_radius=12,
            heading_row_color=ft.Colors.GREY_50,
        )
        
        # Folder picker for PDF export
        folder_picker = ft.FilePicker()
        
        def generate_pdf_at_location(folder_path: str):
            """Generate PDF at the selected location."""
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_event_name = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' 
                                         for c in event['name'])
                filename = f"Attendance_{safe_event_name}_{timestamp}.pdf"
                pdf_path = os.path.join(folder_path, filename)
                
                doc = SimpleDocTemplate(pdf_path, pagesize=letter)
                story = []
                styles = getSampleStyleSheet()
                
                # Add title
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=18,
                    textColor=colors.HexColor('#1976D2'),
                    spaceAfter=12,
                    alignment=1
                )
                story.append(Paragraph("MaScan Attendance Report", title_style))
                story.append(Spacer(1, 0.2*inch))
                
                # Add event details
                details_style = ParagraphStyle('Details', parent=styles['Normal'], fontSize=11, spaceAfter=6)
                story.append(Paragraph(f"<b>Event:</b> {event['name']}", details_style))
                story.append(Paragraph(f"<b>Date:</b> {event['date']}", details_style))
                story.append(Paragraph(f"<b>Description:</b> {event.get('desc', 'N/A')}", details_style))
                story.append(Paragraph(f"<b>Total Attendees:</b> {len(attendance)}", details_style))
                story.append(Paragraph(f"<b>Export Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", details_style))
                story.append(Spacer(1, 0.3*inch))
                
                # Add table
                table_title_style = ParagraphStyle('TableTitle', parent=styles['Heading2'], 
                                                  fontSize=14, textColor=colors.HexColor('#1976D2'), spaceAfter=10)
                story.append(Paragraph("Attendance Records", table_title_style))
                
                if attendance:
                    table_data = [["#", "Name", "ID", "Time", "Status"]]
                    for idx, (user_id, record) in enumerate(attendance.items(), 1):
                        table_data.append([str(idx), record['name'], user_id, record['time'], record['status']])
                    
                    table = Table(table_data, colWidths=[0.4*inch, 2*inch, 1.2*inch, 1*inch, 1*inch])
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 11),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('TOPPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 9),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
                    story.append(table)
                else:
                    story.append(Paragraph("No attendance records found.", styles['Normal']))
                
                # Footer
                story.append(Spacer(1, 0.5*inch))
                footer_style = ParagraphStyle('Footer', parent=styles['Normal'], 
                                             fontSize=8, textColor=colors.grey, alignment=1)
                story.append(Paragraph(
                    f"Generated by MaScan Attendance System | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                    footer_style
                ))
                
                doc.build(story)
                self.show_snackbar(f"✅ PDF saved: {filename}", ft.Colors.GREEN)
                
            except Exception as ex:
                print(f"ERROR generating PDF: {ex}")
                import traceback
                traceback.print_exc()
                self.show_snackbar(f"❌ Export error: {str(ex)}", ft.Colors.RED)
        
        def on_folder_selected(e: ft.FilePickerResultEvent):
            if e.path:
                self.show_snackbar("Generating PDF...", ft.Colors.BLUE)
                generate_pdf_at_location(e.path)
            else:
                self.show_snackbar("Export cancelled", ft.Colors.ORANGE)
        
        def export_data(e):
            if not attendance:
                self.show_snackbar("⚠️ No attendance records to export", ft.Colors.ORANGE)
                return
            
            folder_picker.on_result = on_folder_selected
            folder_picker.get_directory_path("Select folder to save attendance report")
        
        if folder_picker not in self.page.overlay:
            self.page.overlay.append(folder_picker)
        
        # Build content
        content_card = self.create_modern_card(
            content=ft.Column(
                [
                    # Header section
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.EVENT, color=ft.Colors.WHITE, size=32),
                                width=64,
                                height=64,
                                bgcolor=PRIMARY_COLOR,
                                border_radius=16,
                                alignment=ft.alignment.center,
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        event['name'],
                                        size=24,
                                        weight=ft.FontWeight.BOLD,
                                        color=PRIMARY_COLOR,
                                    ),
                                    ft.Row(
                                        [
                                            ft.Icon(ft.Icons.CALENDAR_TODAY, size=16, color=ft.Colors.GREY_600),
                                            ft.Text(event['date'], size=15, color=ft.Colors.GREY_700),
                                        ],
                                        spacing=6,
                                    ),
                                ],
                                spacing=4,
                                expand=True,
                            ),
                        ],
                        spacing=16,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                    
                    ft.Divider(height=32, color=ft.Colors.GREY_200),
                    
                    # Stats section
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Icon(ft.Icons.PEOPLE, color=PRIMARY_COLOR, size=32),
                                        ft.Text(
                                            str(len(attendance)),
                                            size=28,
                                            weight=ft.FontWeight.BOLD,
                                            color=PRIMARY_COLOR,
                                        ),
                                        ft.Text("Attendees", size=13, color=ft.Colors.GREY_600),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=4,
                                ),
                                padding=20,
                                bgcolor=ft.Colors.BLUE_50,
                                border_radius=12,
                                expand=True,
                            ),
                        ],
                    ),
                    
                    ft.Container(height=16),
                    
                    # Attendance table
                    self.create_section_title("Attendance Records", icon=ft.Icons.LIST_ALT),
                    ft.Container(height=12),
                    ft.Container(
                        content=ft.Column(
                            [attendance_table],
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        border=ft.border.all(1, ft.Colors.GREY_200),
                        border_radius=12,
                        padding=12,
                        expand=True,
                        bgcolor=ft.Colors.WHITE,
                    ),
                    
                    ft.Container(height=16),
                    
                    # Export button
                    ft.Row(
                        [
                            self.create_modern_button(
                                text="Export to PDF",
                                icon=ft.Icons.PICTURE_AS_PDF,
                                on_click=export_data,
                                width=200,
                            ),
                            ft.Text(
                                f"📄 {len(attendance)} records ready" if attendance else "No records to export",
                                size=13,
                                color=ft.Colors.GREY_600,
                                italic=True,
                            ),
                        ],
                        spacing=16,
                        alignment=ft.MainAxisAlignment.START,
                    ),
                ],
                spacing=0,
            ),
            padding=24,
            expand=True,
        )
        
        return ft.View(
            f"/event/{event_id}",
            [
                self.create_app_bar(event['name'], show_back=True),
                ft.Container(
                    content=content_card,
                    padding=20,
                    expand=True,
                    bgcolor=ft.Colors.GREY_50,
                )
            ],
            bgcolor=ft.Colors.GREY_50,
        )