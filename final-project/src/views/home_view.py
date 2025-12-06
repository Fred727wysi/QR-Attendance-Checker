# views/home_view.py
"""Modern home view displaying list of events."""

import flet as ft
from views.base_view import BaseView
from config.constants import PRIMARY_COLOR


class HomeView(BaseView):
    """Home screen with modern event list."""

    def build(self):
        """Build and return the home view with modern design."""
        try:
            events = self.db.get_all_events()

            def delete_event_handler(event_id: str, event_name: str):
                """Handle event deletion with modern confirmation dialog."""
                def confirm_delete(e):
                    self.db.delete_event(event_id)
                    self.show_snackbar(f"✓ Event '{event_name}' deleted", ft.Colors.GREEN)
                    self.page.close(dialog)
                    self.page.go("/home")

                def cancel_delete(e):
                    self.page.close(dialog)

                dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Row(
                        [
                            ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.RED_700, size=28),
                            ft.Text("Delete Event?", weight=ft.FontWeight.BOLD),
                        ],
                        spacing=8,
                    ),
                    content=ft.Text(
                        f"Are you sure you want to delete '{event_name}'?\n\n"
                        "This will permanently delete all attendance records for this event.",
                        size=14,
                    ),
                    actions=[
                        ft.TextButton(
                            "Cancel",
                            on_click=cancel_delete,
                        ),
                        ft.ElevatedButton(
                            "Delete",
                            on_click=confirm_delete,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.RED_700,
                                color=ft.Colors.WHITE,
                            ),
                        ),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                self.page.open(dialog)

            def create_event_card(event_id: str, event_data: dict):
                """Create a modern card for displaying an event."""
                return ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.ListTile(
                                    leading=ft.Container(
                                        content=ft.Icon(
                                            ft.Icons.EVENT,
                                            color=ft.Colors.WHITE,
                                            size=24,
                                        ),
                                        width=48,
                                        height=48,
                                        bgcolor=PRIMARY_COLOR,
                                        border_radius=12,
                                        alignment=ft.alignment.center,
                                    ),
                                    title=ft.Text(
                                        event_data['name'],
                                        weight=ft.FontWeight.W_600,
                                        size=16,
                                    ),
                                    subtitle=ft.Row(
                                        [
                                            ft.Icon(
                                                ft.Icons.CALENDAR_TODAY,
                                                size=14,
                                                color=ft.Colors.GREY_600,
                                            ),
                                            ft.Text(
                                                event_data['date'],
                                                size=13,
                                                color=ft.Colors.GREY_600,
                                            ),
                                        ],
                                        spacing=4,
                                    ),
                                    trailing=ft.PopupMenuButton(
                                        icon=ft.Icons.MORE_VERT,
                                        items=[
                                            ft.PopupMenuItem(
                                                text="View Attendance",
                                                icon=ft.Icons.PEOPLE_OUTLINE,
                                                on_click=lambda e, eid=event_id: self.page.go(f"/event/{eid}")
                                            ),
                                            ft.PopupMenuItem(
                                                text="Start Scanning",
                                                icon=ft.Icons.QR_CODE_SCANNER,
                                                on_click=lambda e, eid=event_id: self.page.go(f"/scan/{eid}")
                                            ),
                                            ft.PopupMenuItem(),  # Divider
                                            ft.PopupMenuItem(
                                                text="Delete Event",
                                                icon=ft.Icons.DELETE_OUTLINE,
                                                on_click=lambda e, eid=event_id, name=event_data['name']: 
                                                    delete_event_handler(eid, name)
                                            ),
                                        ]
                                    )
                                ),
                                # Event description
                                ft.Container(
                                    content=ft.Text(
                                        event_data['desc'],
                                        size=13,
                                        color=ft.Colors.GREY_700,
                                        max_lines=2,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                    padding=ft.padding.only(left=72, right=16, bottom=16),
                                ) if event_data.get('desc') and event_data['desc'] != "No description" else ft.Container(),
                            ],
                            spacing=0,
                        ),
                        padding=0,
                    ),
                    elevation=1,
                )

            # Create event list or empty state
            if events:
                event_list = ft.ListView(
                    controls=[create_event_card(eid, data) for eid, data in events.items()],
                    spacing=12,
                    padding=20,
                    expand=True,
                )
            else:
                event_list = self.create_empty_state(
                    icon=ft.Icons.EVENT_BUSY_OUTLINED,
                    title="No Events Yet",
                    subtitle="Create your first event to get started",
                )

            return ft.View(
                "/home",
                [
                    self.create_app_bar("MaScan"),
                    event_list,
                    ft.FloatingActionButton(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.ADD, size=24),
                                ft.Text("New Event", size=15, weight=ft.FontWeight.W_600),
                            ],
                            spacing=8,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        on_click=lambda e: self.page.go("/create_event"),
                        bgcolor=PRIMARY_COLOR,
                        width=140,
                        height=56,
                    )
                ],
                bgcolor=ft.Colors.GREY_50,
            )

        except Exception as ex:
            print(f"ERROR building HomeView: {ex}")
            import traceback
            traceback.print_exc()
            
            return ft.View(
                "/home",
                [
                    self.create_app_bar("Error", show_back=True),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.Icons.ERROR_OUTLINE, size=80, color=ft.Colors.RED_400),
                                ft.Text(
                                    "An error occurred",
                                    size=20,
                                    weight=ft.FontWeight.W_600,
                                    color=ft.Colors.RED_600,
                                ),
                                ft.Text(
                                    str(ex),
                                    size=13,
                                    color=ft.Colors.GREY_600,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=12,
                        ),
                        expand=True,
                        alignment=ft.alignment.center,
                    )
                ],
                bgcolor=ft.Colors.GREY_50,
            )