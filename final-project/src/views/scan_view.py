# views/scan_view.py
"""Modern view for QR code scanning and attendance recording."""

import flet as ft
from datetime import datetime
import time
import threading
from views.base_view import BaseView
from config.constants import CAMERA_WIDTH, CAMERA_HEIGHT, QR_SCAN_COOLDOWN, PRIMARY_COLOR
from utils.qr_scanner import QRCameraScanner


class ScanView(BaseView):
    """Modern QR scanning screen with OpenCV camera support."""
    
    def build(self, event_id: str):
        """Build and return the scan view."""
        event = self.db.get_event_by_id(event_id)
        if not event:
            self.page.go("/home")
            return ft.View("/", [ft.Container()])
        
        # Scan log list
        scan_log = ft.ListView(spacing=8, padding=12, expand=True)
        
        # Load recent scans
        attendance = self.db.get_attendance_by_event(event_id)
        for user_id, record in list(attendance.items())[:10]:
            scan_log.controls.append(
                self.create_list_tile_card(
                    leading_icon=ft.Icons.CHECK_CIRCLE,
                    leading_color=ft.Colors.GREEN_600,
                    title=record['name'],
                    subtitle=record['time'],
                )
            )
        
        # UI Components
        qr_input = self.create_modern_text_field(
            label="Enter ID manually",
            hint_text="e.g., E101 or scan QR code",
            prefix_icon=ft.Icons.QR_CODE_2,
        )
        
        camera_status = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.CIRCLE, size=10, color=ft.Colors.GREY_400),
                    ft.Text(
                        "Camera Ready",
                        size=13,
                        weight=ft.FontWeight.W_500,
                        color=ft.Colors.GREY_600,
                    ),
                ],
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=8,
            border_radius=20,
            bgcolor=ft.Colors.GREY_100,
        )
        
        camera_image = ft.Image(
            src_base64="",
            width=CAMERA_WIDTH,
            height=CAMERA_HEIGHT,
            fit=ft.ImageFit.CONTAIN,
            visible=False,
            border_radius=16,
        )
        
        camera_placeholder = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.QR_CODE_SCANNER_ROUNDED, size=80, color=PRIMARY_COLOR),
                    ft.Text(
                        "Tap to start camera",
                        size=16,
                        weight=ft.FontWeight.W_500,
                        color=ft.Colors.GREY_600,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=12,
            ),
            width=CAMERA_WIDTH,
            height=CAMERA_HEIGHT,
            bgcolor=ft.Colors.GREY_50,
            border_radius=16,
            border=ft.border.all(2, ft.Colors.GREY_200),
            alignment=ft.alignment.center,
        )
        
        camera_stack = ft.Stack([camera_placeholder, camera_image])
        
        camera_container = self.create_modern_card(
            content=camera_stack,
            padding=16,
        )
        
        camera_active = [False]
        
        def update_camera_frame(frame_base64: str):
            """Update the camera preview with new frame."""
            if not camera_active[0]:
                return
            
            try:
                if frame_base64 and len(frame_base64) > 0:
                    camera_image.src_base64 = frame_base64
                    camera_image.visible = True
                    camera_placeholder.visible = False
                    camera_image.update()
                    camera_placeholder.update()
            except Exception as e:
                print(f"Error updating frame: {e}")
        
        def process_scan(user_id: str):
            """Process a scanned or entered ID."""
            user_id = user_id.strip()
            
            if not user_id:
                return
            
            # Parse QR data
            if "|" in user_id:
                parts = user_id.split("|", 1)
                school_id = parts[0].strip()
                user_name = parts[1].strip()
            else:
                school_id = user_id
                user_name = user_id
            
            existing = self.db.is_user_checked_in(event_id, school_id)
            
            if existing:
                self.show_snackbar(f"⚠️ {user_name} already checked in at {existing}", ft.Colors.ORANGE)
                return
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.db.record_attendance(event_id, school_id, user_name, timestamp)
            
            # Update UI
            scan_log.controls.insert(0, 
                self.create_list_tile_card(
                    leading_icon=ft.Icons.CHECK_CIRCLE,
                    leading_color=ft.Colors.GREEN_600,
                    title=user_name,
                    subtitle=timestamp,
                )
            )
            
            try:
                scan_log.update()
            except:
                pass
            
            self.show_snackbar(f"✓ {user_name} checked in!", ft.Colors.GREEN)
        
        def on_qr_detected(qr_data: str):
            """Callback when QR code is detected."""
            process_scan(qr_data)
        
        def handle_manual_scan(e):
            """Handle manual ID entry."""
            user_id = qr_input.value
            qr_input.value = ""
            qr_input.update()
            process_scan(user_id)
        
        def toggle_camera(e):
            """Toggle camera on/off."""
            camera_active[0] = not camera_active[0]
            
            if camera_active[0]:
                # Start camera
                camera_btn.icon = ft.Icons.STOP_CIRCLE
                camera_btn.style.bgcolor = ft.Colors.RED_700
                camera_btn.tooltip = "Stop Camera"
                
                camera_status.content.controls[0].color = ft.Colors.ORANGE_600
                camera_status.content.controls[1].value = "Starting..."
                camera_status.content.controls[1].color = ft.Colors.ORANGE_700
                camera_status.bgcolor = ft.Colors.ORANGE_50
                
                camera_container.border = ft.border.all(2, ft.Colors.GREEN_400)
                
                camera_btn.update()
                camera_status.update()
                camera_container.update()
                
                # Initialize scanner
                self.app.qr_scanner = QRCameraScanner(
                    on_qr_detected, 
                    update_camera_frame,
                    CAMERA_WIDTH,
                    CAMERA_HEIGHT,
                    QR_SCAN_COOLDOWN
                )
                self.app.qr_scanner.start()
                
                # Update status after delay
                def update_status():
                    time.sleep(0.5)
                    if camera_active[0]:
                        try:
                            camera_status.content.controls[0].color = ft.Colors.GREEN_600
                            camera_status.content.controls[1].value = "Scanning..."
                            camera_status.content.controls[1].color = ft.Colors.GREEN_700
                            camera_status.bgcolor = ft.Colors.GREEN_50
                            camera_status.update()
                        except:
                            pass
                
                threading.Thread(target=update_status, daemon=True).start()
                
            else:
                # Stop camera
                camera_btn.icon = ft.Icons.VIDEOCAM
                camera_btn.style.bgcolor = PRIMARY_COLOR
                camera_btn.tooltip = "Start Camera"
                
                camera_status.content.controls[0].color = ft.Colors.GREY_400
                camera_status.content.controls[1].value = "Camera Stopped"
                camera_status.content.controls[1].color = ft.Colors.GREY_600
                camera_status.bgcolor = ft.Colors.GREY_100
                
                camera_container.border = ft.border.all(2, ft.Colors.GREY_200)
                
                camera_image.visible = False
                camera_placeholder.visible = True
                
                if self.app.qr_scanner:
                    self.app.qr_scanner.stop()
                
                camera_btn.update()
                camera_status.update()
                camera_container.update()
                camera_image.update()
                camera_placeholder.update()
        
        qr_input.on_submit = handle_manual_scan
        
        camera_btn = ft.IconButton(
            icon=ft.Icons.VIDEOCAM,
            icon_color=ft.Colors.WHITE,
            icon_size=28,
            style=ft.ButtonStyle(
                bgcolor=PRIMARY_COLOR,
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=12,
            ),
            tooltip="Start Camera",
            on_click=toggle_camera,
        )
        
        submit_btn = ft.IconButton(
            icon=ft.Icons.SEND,
            icon_color=ft.Colors.WHITE,
            icon_size=24,
            style=ft.ButtonStyle(
                bgcolor=PRIMARY_COLOR,
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=12,
            ),
            on_click=handle_manual_scan,
            tooltip="Submit ID",
        )
        
        # Build view
        content = ft.Column(
            [
                # Camera section
                camera_container,
                camera_status,
                
                ft.Container(height=8),
                
                # Input section
                ft.Row(
                    [qr_input, camera_btn, submit_btn],
                    spacing=12,
                    expand=True,
                ),
                
                ft.Container(height=16),
                ft.Divider(color=ft.Colors.GREY_200),
                ft.Container(height=8),
                
                # Recent activity
                self.create_section_title("Recent Activity", size=18, icon=ft.Icons.HISTORY),
                ft.Container(height=12),
                self.create_modern_card(
                    content=scan_log,
                    padding=0,
                    expand=True,
                ),
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        return ft.View(
            f"/scan/{event_id}",
            [
                self.create_app_bar(f"Scan: {event['name']}", show_back=True),
                ft.Container(
                    content=content,
                    padding=20,
                    expand=True,
                    bgcolor=ft.Colors.GREY_50,
                )
            ],
            bgcolor=ft.Colors.GREY_50,
        )