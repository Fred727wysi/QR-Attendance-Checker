# views/create_event_view.py
"""Modern view for creating new events."""

import flet as ft
from views.base_view import BaseView
from config.constants import PRIMARY_COLOR
from datetime import datetime


class CreateEventView(BaseView):
    """Create new event screen with modern design."""
    
    def build(self):
        """Build and return the create event view."""
        # Store selected date
        selected_date = [None]
        
        # Form fields using modern styling
        name_field = self.create_modern_text_field(
            label="Event Name",
            hint_text="e.g., Annual Company Meeting",
            prefix_icon=ft.Icons.EVENT_NOTE,
            width=400,
        )
        
        # Date display field (read-only)
        date_display = ft.TextField(
            label="Event Date",
            hint_text="Click to select date",
            prefix_icon=ft.Icons.CALENDAR_TODAY,
            width=400,
            height=56,
            border_radius=12,
            filled=True,
            read_only=True,
            bgcolor=ft.Colors.GREY_50,
            border_color=ft.Colors.TRANSPARENT,
            focused_border_color=PRIMARY_COLOR,
            focused_bgcolor=ft.Colors.WHITE,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=16),
            text_size=15,
        )
        
        desc_field = self.create_modern_text_field(
            label="Description (Optional)",
            hint_text="Add event details or notes...",
            multiline=True,
            width=400,
        )
        
        # Status message
        status_text = ft.Text(
            "",
            size=13,
            text_align=ft.TextAlign.CENTER,
            visible=False,
        )
        
        def handle_date_change(e):
            """Handle date selection from date picker."""
            if e.control.value:
                selected_date[0] = e.control.value
                # Format date as "Month Day, Year" (e.g., "December 15, 2024")
                formatted_date = e.control.value.strftime("%B %d, %Y")
                date_display.value = formatted_date
                date_display.update()
        
        def handle_date_dismiss(e):
            """Handle date picker dismissal."""
            pass
        
        # Date picker
        date_picker = ft.DatePicker(
            on_change=handle_date_change,
            on_dismiss=handle_date_dismiss,
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31),
        )
        
        def open_date_picker(e):
            """Open the date picker dialog."""
            # Add date picker to page overlay if not already there
            if date_picker not in self.page.overlay:
                self.page.overlay.append(date_picker)
                self.page.update()
            date_picker.open = True
            self.page.update()
        
        # Container with date field and calendar button - properly centered
        date_container = ft.Row(
            [
                date_display,
                ft.IconButton(
                    icon=ft.Icons.CALENDAR_MONTH,
                    icon_color=PRIMARY_COLOR,
                    tooltip="Pick a date",
                    on_click=open_date_picker,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.with_opacity(0.1, PRIMARY_COLOR),
                        shape=ft.RoundedRectangleBorder(radius=12),
                    ),
                ),
            ],
            spacing=8,
        )
        
        # Make date field clickable
        date_display.on_click = open_date_picker
        
        def save_event(e):
            """Save the new event to database."""
            # Clear previous status
            status_text.visible = False
            status_text.update()
            
            if not name_field.value or not name_field.value.strip():
                status_text.value = "Event name is required"
                status_text.color = ft.Colors.RED_600
                status_text.visible = True
                status_text.update()
                return
            
            if not date_display.value or not date_display.value.strip():
                status_text.value = "Please select an event date"
                status_text.color = ft.Colors.RED_600
                status_text.visible = True
                status_text.update()
                return
            
            try:
                self.db.create_event(
                    name_field.value.strip(),
                    date_display.value.strip(),
                    desc_field.value.strip() if desc_field.value else "No description"
                )
                self.show_snackbar(
                    f"✓ Event '{name_field.value.strip()}' created successfully!",
                    ft.Colors.GREEN
                )
                self.page.go("/home")
            except Exception as ex:
                status_text.value = f"Error creating event: {str(ex)}"
                status_text.color = ft.Colors.RED_600
                status_text.visible = True
                status_text.update()
        
        # Modern form card
        form_card = self.create_modern_card(
            content=ft.Column(
                [
                    # Header with icon
                    ft.Column(
                        [
                            ft.Icon(
                                ft.Icons.ADD_CIRCLE_OUTLINE,
                                size=56,
                                color=PRIMARY_COLOR,
                            ),
                            self.create_section_title("Create New Event", size=24),
                            ft.Text(
                                "Set up a new event for attendance tracking",
                                size=14,
                                color=ft.Colors.GREY_600,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    
                    ft.Container(height=24),
                    
                    # Form fields - all centered
                    ft.Column(
                        [
                            ft.Container(
                                content=name_field,
                                alignment=ft.alignment.center,
                            ),
                            ft.Container(
                                content=date_container,
                                alignment=ft.alignment.center,
                            ),
                            ft.Container(
                                content=desc_field,
                                alignment=ft.alignment.center,
                            ),
                        ],
                        spacing=16,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    
                    ft.Container(height=8),
                    status_text,
                    ft.Container(height=16),
                    
                    # Action buttons
                    ft.Row(
                        [
                            ft.OutlinedButton(
                                "Cancel",
                                width=190,
                                height=50,
                                on_click=lambda e: self.page.go("/home"),
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=12),
                                    side=ft.BorderSide(1, ft.Colors.GREY_400),
                                ),
                            ),
                            self.create_modern_button(
                                text="Create Event",
                                icon=ft.Icons.CHECK_CIRCLE,
                                on_click=save_event,
                                width=190,
                            ),
                        ],
                        spacing=12,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            padding=40,
        )
        
        return ft.View(
            "/create_event",
            [
                self.create_app_bar("Create Event", show_back=True),
                self.create_gradient_container(
                    content=ft.Column(
                        [form_card],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ),
            ],
            bgcolor=ft.Colors.TRANSPARENT,
        )