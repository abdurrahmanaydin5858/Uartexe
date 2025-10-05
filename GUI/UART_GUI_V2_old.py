def _update_status_buttons(self):
        """Update status indicator buttons"""
        status_indices = [32, 39, 46, 25]  # SATA0, SATA1, GPU_12V, PMON
        
        for i, idx in enumerate(status_indices):
            if idx < len(self.received_data):
                status = self.received_data[idx]
                is_on = (status & 0x80) != 0
                
                btn = self.status_buttons[i]
                label = btn.text().split('\n')[0].replace("●  ", "")
                
                if is_on:
                    btn.setText(f"●  {label}\nENABLE")
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {AppStyle.STATUS_ENABLED};
                            color: white;
                            font-weight: bold;
                            font-size: 10px;
                            border-radius: 6px;
                            text-align: left;
                            padding-left: 15px;
                        }}
                    """)
                else:
                    btn.setText(f"●  {label}\nDISABLE")
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {AppStyle.STATUS_DISABLED};
                            color: white;
                            font-weight: bold;
                            font-size: 10px;
                            border-radius: 6px;
                            text-align: left;
                            padding-left: 15px;
                        }}
                    """)"""
UART Monitoring Interface
Professional GUI for monitoring UART communication with data validation and control
Author: [Your Name]
Version: 1.0
"""

import sys
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QLabel,
    QHeaderView, QGroupBox, QMessageBox
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor, QFont, QPalette

# Modern color scheme
class AppStyle:
    # Dark theme colors
    BACKGROUND = "#1e1e1e"
    SURFACE = "#252526"
    SURFACE_LIGHT = "#2d2d30"
    PRIMARY = "#0e639c"
    PRIMARY_DARK = "#094771"
    SUCCESS = "#4caf50"
    ERROR = "#f44336"
    WARNING = "#ff9800"
    TEXT = "#cccccc"
    TEXT_SECONDARY = "#969696"
    BORDER = "#3e3e42"
    
    # Status colors
    STATUS_ENABLED = "#2e7d32"
    STATUS_DISABLED = "#c62828"
    
    # Table colors
    TABLE_HEADER = "#2d2d30"
    TABLE_ROW_ALT = "#2a2a2d"
    TABLE_SUCCESS = "#1b5e20"
    TABLE_ERROR = "#b71c1c"
    
    @staticmethod
    def get_stylesheet():
        return """
            QMainWindow {
                background-color: #1e1e1e;
            }
            
            QWidget {
                color: #cccccc;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QGroupBox {
                background-color: #252526;
                border: 1px solid #3e3e42;
                border-radius: 6px;
                margin-top: 12px;
                padding: 15px;
                font-weight: bold;
                font-size: 11px;
            }
            
            QGroupBox::title {
                color: #cccccc;
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                left: 10px;
            }
            
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 10px;
            }
            
            QPushButton:hover {
                background-color: #094771;
            }
            
            QPushButton:pressed {
                background-color: #063456;
            }
            
            QPushButton:disabled {
                background-color: #2d2d30;
                color: #969696;
            }
            
            QComboBox {
                background-color: #2d2d30;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                padding: 6px;
                color: #cccccc;
                font-size: 10px;
            }
            
            QComboBox:hover {
                border: 1px solid #0e639c;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QLabel {
                color: #cccccc;
                font-size: 10px;
            }
            
            QTableWidget {
                background-color: #252526;
                alternate-background-color: #2a2a2d;
                border: 1px solid #3e3e42;
                gridline-color: #3e3e42;
                color: #cccccc;
                font-size: 9px;
            }
            
            QTableWidget::item {
                padding: 4px;
            }
            
            QHeaderView::section {
                background-color: #2d2d30;
                color: #cccccc;
                padding: 6px;
                border: none;
                border-right: 1px solid #3e3e42;
                border-bottom: 2px solid #0e639c;
                font-weight: bold;
                font-size: 9px;
            }
            
            QScrollBar:vertical {
                background-color: #252526;
                width: 12px;
                border: none;
            }
            
            QScrollBar::handle:vertical {
                background-color: #2d2d30;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #0e639c;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollBar:horizontal {
                background-color: #252526;
                height: 12px;
                border: none;
            }
            
            QScrollBar::handle:horizontal {
                background-color: #2d2d30;
                border-radius: 6px;
                min-width: 20px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background-color: #0e639c;
            }
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """


class UARTMonitor(QMainWindow):
    """Main application window for UART monitoring"""
    
    # Constants
    WINDOW_TITLE = "UART Monitoring Interface"
    WINDOW_WIDTH = 1800
    WINDOW_HEIGHT = 950
    TIMER_INTERVAL = 100  # milliseconds
    PACKET_SIZE = 133
    DATA_SIZE = 128
    
    # Protocol constants
    HEADER_1 = 0x41
    HEADER_2 = 0x56
    PACKET_LENGTH = 0x85
    PACKET_ID = 0x02
    
    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.is_connected = False
        self.received_data = [0] * self.DATA_SIZE
        
        self._init_data_limits()
        self._init_ui()
        self._init_timer()
        
    def _init_data_limits(self):
        """Initialize data validation limits"""
        self.data_limits = {
            'min': ['xx'] * self.DATA_SIZE,
            'max': ['xx'] * self.DATA_SIZE
        }
        
        # UART packet header and control bytes (fixed values)
        self._set_fixed_limits(0, self.HEADER_1)      # HEADER_1
        self._set_fixed_limits(1, self.HEADER_2)      # HEADER_2
        self._set_fixed_limits(2, self.PACKET_LENGTH) # LENGTH
        self._set_fixed_limits(3, self.PACKET_ID)     # PACKET_ID
        
        # Voltage, Current, Power limits (0-255 for all MSB/LSB pairs)
        voltage_current_power_indices = [
            (26, 31),   # LTC4281_PMON
            (33, 38),   # LTC4281_SATA0
            (40, 45),   # LTC4281_SATA1
            (47, 52),   # LTC4281_GPU_12V
            (54, 59),   # LTC4281_GPU_3V3
            (61, 66),   # LTC4281_GPU_5V
            (67, 72),   # INA260_PWR_BOARD
            (73, 78),   # INA260_PMON
        ]
        
        for start, end in voltage_current_power_indices:
            for i in range(start, end + 1):
                self.data_limits['min'][i] = 0
                self.data_limits['max'][i] = 255
        
        # Temperature sensor indices (always green)
        self.temp_indices = [79, 80, 81, 82, 83, 84, 85]
        
    def _set_fixed_limits(self, index, value):
        """Set min and max to the same value for fixed fields"""
        self.data_limits['min'][index] = value
        self.data_limits['max'][index] = value
        
    def _init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setGeometry(50, 50, self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        
        # Apply modern stylesheet
        self.setStyleSheet(AppStyle.get_stylesheet())
        
        # Disable maximize button
        self.setWindowFlags(
            Qt.Window | 
            Qt.WindowMinimizeButtonHint | 
            Qt.WindowCloseButtonHint
        )
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Connection panel
        main_layout.addWidget(self._create_connection_panel())
        
        # Content: Table and control panel
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)
        
        self.table_widget = self._create_data_table()
        content_layout.addWidget(self.table_widget, stretch=7)
        
        # Right side: Status indicators and controls
        right_side_layout = QVBoxLayout()
        right_side_layout.setSpacing(10)
        right_side_layout.addWidget(self._create_status_panel())
        right_side_layout.addWidget(self._create_control_panel())
        content_layout.addLayout(right_side_layout, stretch=3)
        
        main_layout.addLayout(content_layout)
        
    def _init_timer(self):
        """Initialize the data reading timer"""
        self.timer = QTimer()
        self.timer.timeout.connect(self._read_uart_data)
        
    def _create_connection_panel(self):
        """Create the connection configuration panel"""
        panel = QGroupBox("⚡ BAĞLANTI AYARLARI")
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # COM Port selection
        layout.addWidget(QLabel("Port:"))
        self.com_combo = QComboBox()
        self.com_combo.setMinimumWidth(200)
        self._refresh_com_ports()
        layout.addWidget(self.com_combo)
        
        # Baud rate selection
        layout.addWidget(QLabel("Baud Rate:"))
        self.baud_combo = QComboBox()
        self.baud_combo.setMinimumWidth(120)
        self.baud_combo.addItems(['9600', '19200', '38400', '57600', '115200'])
        self.baud_combo.setCurrentText('115200')
        layout.addWidget(self.baud_combo)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Yenile")
        refresh_btn.setMinimumWidth(100)
        refresh_btn.clicked.connect(self._refresh_com_ports)
        layout.addWidget(refresh_btn)
        
        # Connect button
        self.connect_btn = QPushButton("🔌 Bağlan")
        self.connect_btn.setMinimumWidth(120)
        self.connect_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppStyle.SUCCESS};
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
        """)
        self.connect_btn.clicked.connect(self._toggle_connection)
        layout.addWidget(self.connect_btn)
        
        # Status label
        self.status_label = QLabel("● Bağlantı Yok")
        self.status_label.setStyleSheet(f"color: {AppStyle.ERROR}; font-weight: bold; font-size: 11px;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        panel.setLayout(layout)
        return panel
    
    def _create_data_table(self):
        """Create the main data table"""
        table = QTableWidget()
        
        rows_per_column = 43
        table.setRowCount(rows_per_column)
        table.setColumnCount(18)
        
        headers = ['#', 'Sinyal', 'Min', 'Değer', 'Max', 'Meaning'] * 3
        table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().setVisible(False)
        
        # Set compact font
        font = QFont()
        font.setPointSize(8)
        table.setFont(font)
        table.verticalHeader().setDefaultSectionSize(20)
        
        # Column widths
        column_widths = {
            0: 30,   # Index
            1: 150,  # Signal name
            2: 40,   # Min
            3: 45,   # Value
            4: 40,   # Max
            5: 120   # Meaning
        }
        
        for i in range(18):
            col_type = i % 6
            table.setColumnWidth(i, column_widths[col_type])
        
        self._populate_table(table)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        return table
    
    def _populate_table(self, table):
        """Populate the table with initial data"""
        signal_names = self._get_signal_names()
        rows_per_column = 43
        
        for i in range(self.DATA_SIZE):
            col_group = i // rows_per_column
            row = i % rows_per_column
            
            if col_group < 3:
                base_col = col_group * 6
                
                # Index
                table.setItem(row, base_col, QTableWidgetItem(str(i)))
                
                # Signal name
                table.setItem(row, base_col + 1, 
                            QTableWidgetItem(signal_names.get(i, f"DATA_{i}")))
                
                # Min value
                min_val = self.data_limits['min'][i]
                min_item = QTableWidgetItem(
                    f"0x{min_val:02X}" if isinstance(min_val, int) else str(min_val)
                )
                table.setItem(row, base_col + 2, min_item)
                
                # Current value with color coding
                value_item = QTableWidgetItem("0")
                value_item.setBackground(self._get_value_color(i, 0))
                table.setItem(row, base_col + 3, value_item)
                
                # Max value
                max_val = self.data_limits['max'][i]
                max_item = QTableWidgetItem(
                    f"0x{max_val:02X}" if isinstance(max_val, int) else str(max_val)
                )
                table.setItem(row, base_col + 4, max_item)
                
                # Meaning
                table.setItem(row, base_col + 5, QTableWidgetItem("XX"))
    
    def _get_value_color(self, index, value):
        """Determine the appropriate color for a value"""
        if index in self.temp_indices:
            return QColor(27, 94, 32)  # Dark green for temperature
        
        min_val = self.data_limits['min'][index]
        max_val = self.data_limits['max'][index]
        
        if min_val == 'xx' or max_val == 'xx':
            return QColor(183, 28, 28)  # Dark red for undefined
        
        if min_val <= value <= max_val:
            return QColor(27, 94, 32)  # Dark green for valid
        
        return QColor(183, 28, 28)  # Dark red for out of range
    
    def _create_status_panel(self):
        """Create the status indicator panel"""
        panel = QGroupBox("📊 DURUM GÖSTERGELERİ")
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        self.status_buttons = []
        status_labels = ["SATA0", "SATA1", "GPU 12V", "PMON"]
        
        for label in status_labels:
            btn = QPushButton(f"●  {label}\nDISABLE")
            btn.setEnabled(False)
            btn.setMinimumHeight(55)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {AppStyle.STATUS_DISABLED};
                    color: white;
                    font-weight: bold;
                    font-size: 10px;
                    border-radius: 6px;
                    text-align: left;
                    padding-left: 15px;
                }}
            """)
            self.status_buttons.append(btn)
            layout.addWidget(btn)
        
        panel.setLayout(layout)
        return panel
    
    def _create_control_panel(self):
        """Create the control button panel"""
        panel = QGroupBox("Kontrol Paneli")
        main_layout = QVBoxLayout()
        
        # TX Controls
        main_layout.addWidget(self._create_tx_controls())
        
        # SATA Controls
        main_layout.addWidget(self._create_sata_controls())
        
        # LED Controls
        main_layout.addWidget(self._create_led_controls())
        
        main_layout.addStretch()
        panel.setLayout(main_layout)
        return panel
    
    def _create_tx_controls(self):
        """Create TX control buttons"""
        group = QGroupBox("📤 TX KONTROL")
        layout = QVBoxLayout()
        layout.setSpacing(6)
        
        self.tx_buttons = []
        for i in range(4):
            btn = QPushButton(f"TX{i+1} Enable")
            btn.setCheckable(True)
            btn.setMinimumHeight(42)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {AppStyle.SURFACE_LIGHT};
                    font-size: 10px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {AppStyle.PRIMARY};
                }}
                QPushButton:checked {{
                    background-color: {AppStyle.SUCCESS};
                }}
            """)
            btn.clicked.connect(lambda checked, b=btn: self._toggle_tx_button(b, checked))
            self.tx_buttons.append(btn)
            layout.addWidget(btn)
        
        group.setLayout(layout)
        return group
    
    def _create_sata_controls(self):
        """Create SATA control buttons"""
        group = QGroupBox("💾 SATA KONTROL")
        layout = QVBoxLayout()
        layout.setSpacing(6)
        
        self.sata1_btn = QPushButton("SATA1 Etkinleştir")
        self.sata1_btn.setMinimumHeight(42)
        self.sata1_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #1976d2;
                color: white;
                font-weight: 600;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background-color: #1565c0;
            }}
        """)
        self.sata1_btn.clicked.connect(self._activate_sata1)
        layout.addWidget(self.sata1_btn)
        
        self.satas_btn = QPushButton("SATAS Etkinleştir\n(SATA0 + SATA1)")
        self.satas_btn.setMinimumHeight(42)
        self.satas_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppStyle.WARNING};
                color: white;
                font-weight: 600;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background-color: #f57c00;
            }}
        """)
        self.satas_btn.clicked.connect(self._activate_satas)
        layout.addWidget(self.satas_btn)
        
        group.setLayout(layout)
        return group
    
    def _create_led_controls(self):
        """Create LED control buttons"""
        group = QGroupBox("💡 LED KONTROL")
        layout = QVBoxLayout()
        layout.setSpacing(6)
        
        self.led_buttons = []
        led_data = [("R", "#e53935"), ("G", "#43a047"), ("B", "#1e88e5")]
        
        for name, color in led_data:
            btn = QPushButton(f"●  LED {name}")
            btn.setCheckable(True)
            btn.setMinimumHeight(42)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {AppStyle.SURFACE_LIGHT};
                    color: {color};
                    font-weight: bold;
                    font-size: 10px;
                    text-align: left;
                    padding-left: 15px;
                }}
                QPushButton:hover {{
                    background-color: {AppStyle.PRIMARY};
                    color: white;
                }}
                QPushButton:checked {{
                    background-color: {color};
                    color: white;
                    border: 2px solid white;
                }}
            """)
            btn.clicked.connect(lambda checked, b=btn, c=color: self._toggle_led_button(b, checked, c))
            self.led_buttons.append(btn)
            layout.addWidget(btn)
        
        group.setLayout(layout)
        return group
    
    def _check_connection(self):
        """Check if serial connection is active"""
        if not self.is_connected:
            QMessageBox.warning(self, 'Uyarı', 'COM bağlı değil! Önce bağlantı yapın.')
            return False
        return True
    
    def _activate_sata1(self):
        """Activate SATA1 with confirmation"""
        if not self._check_connection():
            return
        
        reply = QMessageBox.question(
            self, 'SATA1 Etkinleştirme',
            'SATA1 etkinleştirilecek. Onaylıyor musunuz?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._send_sata_command(sata1=True, sata0=False)
            QMessageBox.information(self, 'Bilgi', 'SATA1 etkinleştirme komutu gönderildi.')
    
    def _activate_satas(self):
        """Activate both SATA0 and SATA1 with confirmation"""
        if not self._check_connection():
            return
        
        reply = QMessageBox.question(
            self, 'SATAS Etkinleştirme',
            'SATA1 ve SATA0 etkinleşecek. Emin misiniz?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._send_sata_command(sata1=True, sata0=True)
            QMessageBox.information(self, 'Bilgi', 'SATA0 ve SATA1 etkinleştirme komutu gönderildi.')
    
    def _send_sata_command(self, sata1=False, sata0=False):
        """Send SATA activation command"""
        if not self.serial_port or not self.serial_port.is_open:
            QMessageBox.warning(self, 'Uyarı', 'Seri port bağlı değil!')
            return
        
        command = bytearray([self.HEADER_1, self.HEADER_2, 0x05, 0x30])
        
        sata_mask = (0x01 if sata0 else 0x00) | (0x02 if sata1 else 0x00)
        command.append(sata_mask)
        
        checksum = (256 - (sum(command) % 256)) % 256
        command.append(checksum)
        
        try:
            self.serial_port.write(command)
            print(f"SATA command sent: {' '.join([f'0x{b:02X}' for b in command])}")
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'SATA komutu gönderilemedi: {str(e)}')
    
    def _refresh_com_ports(self):
        """Refresh the list of available COM ports"""
        self.com_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.com_combo.addItem(f"{port.device} - {port.description}")
    
    def _toggle_connection(self):
        """Toggle serial connection on/off"""
        if not self.is_connected:
            self._connect_serial()
        else:
            self._disconnect_serial()
    
    def _connect_serial(self):
        """Establish serial connection"""
        try:
            port_text = self.com_combo.currentText().split(' - ')[0]
            baud_rate = int(self.baud_combo.currentText())
            
            self.serial_port = serial.Serial(port_text, baud_rate, timeout=0.1)
            self.is_connected = True
            
            self.connect_btn.setText("⏸ Bağlantıyı Kes")
            self.connect_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {AppStyle.ERROR};
                    font-weight: bold;
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: #d32f2f;
                }}
            """)
            self.status_label.setText("● Bağlı")
            self.status_label.setStyleSheet(f"color: {AppStyle.SUCCESS}; font-weight: bold; font-size: 11px;")
            
            self.timer.start(self.TIMER_INTERVAL)
            
        except Exception as e:
            self.status_label.setText(f"● Hata: {str(e)}")
            self.status_label.setStyleSheet(f"color: {AppStyle.ERROR}; font-weight: bold; font-size: 11px;")
    
    def _disconnect_serial(self):
        """Close serial connection"""
        self.timer.stop()
        if self.serial_port:
            self.serial_port.close()
        
        self.is_connected = False
        self.connect_btn.setText("🔌 Bağlan")
        self.connect_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppStyle.SUCCESS};
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
        """)
        self.status_label.setText("● Bağlantı Yok")
        self.status_label.setStyleSheet(f"color: {AppStyle.ERROR}; font-weight: bold; font-size: 11px;")
    
    def _read_uart_data(self):
        """Read and process UART data"""
        if not self.serial_port or not self.serial_port.is_open:
            return
        
        try:
            if self.serial_port.in_waiting > 0:
                data = self.serial_port.read(self.serial_port.in_waiting)
                
                if len(data) >= self.PACKET_SIZE:
                    for i in range(len(data) - self.PACKET_SIZE + 1):
                        if data[i] == self.HEADER_1 and data[i+1] == self.HEADER_2:
                            packet = data[i:i+self.PACKET_SIZE]
                            if self._validate_packet(packet):
                                self._process_packet(packet)
                                break
        except Exception as e:
            print(f"Read error: {e}")
    
    def _validate_packet(self, packet):
        """Validate packet checksum"""
        if len(packet) != self.PACKET_SIZE:
            return False
        
        checksum = sum(packet[:self.PACKET_SIZE-1]) & 0xFF
        return checksum == 0x00
    
    def _process_packet(self, packet):
        """Process received packet data"""
        for i in range(self.DATA_SIZE):
            if i + 4 < len(packet):
                self.received_data[i] = packet[i + 4]
        
        self._update_table()
        self._update_status_buttons()
    
    def _update_table(self):
        """Update table with new data"""
        rows_per_column = 43
        
        for i in range(self.DATA_SIZE):
            col_group = i // rows_per_column
            row = i % rows_per_column
            
            if col_group < 3:
                base_col = col_group * 6
                value = self.received_data[i]
                
                # Update value
                item = self.table_widget.item(row, base_col + 3)
                if item:
                    item.setText(str(value))
                    item.setBackground(self._get_value_color(i, value))
                
                # Update meaning
                meaning_item = self.table_widget.item(row, base_col + 5)
                if meaning_item:
                    meaning_text = self._get_dynamic_meaning(i, value)
                    meaning_item.setText(meaning_text)
    
    def _update_status_buttons(self):
        """Update status indicator buttons"""
        status_indices = [32, 39, 46, 25]  # SATA0, SATA1, GPU_12V, PMON
        
        for i, idx in enumerate(status_indices):
            if idx < len(self.received_data):
                status = self.received_data[idx]
                is_on = (status & 0x80) != 0
                
                btn = self.status_buttons[i]
                label = btn.text().split('\n')[0]
                
                if is_on:
                    btn.setText(f"{label}\nENABLE")
                    btn.setStyleSheet("background-color: #00cc00; color: white; font-weight: bold;")
                else:
                    btn.setText(f"{label}\nDISABLE")
                    btn.setStyleSheet("background-color: #cc0000; color: white; font-weight: bold;")
    
    def _toggle_tx_button(self, button, checked):
        """Toggle TX button state"""
        if not self._check_connection():
            button.setChecked(False)
            return
        
        if checked:
            button.setText(button.text().replace("Enable", "Disable"))
            button.setStyleSheet("background-color: #00cc00; font-weight: bold;")
            self._send_tx_command(self.tx_buttons.index(button), True)
        else:
            button.setText(button.text().replace("Disable", "Enable"))
            button.setStyleSheet("background-color: #666666;")
            self._send_tx_command(self.tx_buttons.index(button), False)
    
    def _toggle_led_button(self, button, checked, color):
        """Toggle LED button state"""
        if not self._check_connection():
            button.setChecked(False)
            return
        
        if checked:
            button.setStyleSheet(f"background-color: {color}; color: white; font-weight: bold; border: 2px solid white;")
            self._send_led_command(self.led_buttons.index(button), True)
        else:
            button.setStyleSheet(f"background-color: #333333; color: {color}; font-weight: bold;")
            self._send_led_command(self.led_buttons.index(button), False)
    
    def _send_tx_command(self, index, enable):
        """Send TX control command"""
        if not self.serial_port or not self.serial_port.is_open:
            return
        
        command = bytearray([self.HEADER_1, self.HEADER_2, 0x05, 0x10 + index, int(enable)])
        checksum = (256 - (sum(command) % 256)) % 256
        command.append(checksum)
        
        try:
            self.serial_port.write(command)
        except Exception as e:
            print(f"TX send error: {e}")
    
    def _send_led_command(self, index, enable):
        """Send LED control command"""
        if not self.serial_port or not self.serial_port.is_open:
            return
        
        command = bytearray([self.HEADER_1, self.HEADER_2, 0x05, 0x20 + index, int(enable)])
        checksum = (256 - (sum(command) % 256)) % 256
        command.append(checksum)
        
        try:
            self.serial_port.write(command)
        except Exception as e:
            print(f"LED send error: {e}")
    
    def _get_signal_names(self):
        """Get signal name mappings"""
        names = {
            0: "HEADER_1", 1: "HEADER_2", 2: "LENGTH", 3: "PACKET_ID",
            4: "FPGA_VERSION", 5: "FPGA_REVISION",
            6: "I2C_ACK_STATUS_1", 7: "I2C_ACK_STATUS_2", 8: "I2C_ACK_STATUS_3",
            9: "I2C_ACK_STATUS_4", 10: "I2C_ACK_STATUS_5",
            11: "UART_STATUS", 12: "CPU_STATUS", 13: "HSN_STATUS",
            14: "SATA_STATUS", 15: "USB_STATUS", 16: "JTAG_STATUS",
            17: "GPU_STATUS_1", 18: "GPU_STATUS_2", 19: "HDMI_STATUS",
            20: "DISC_IN_VALUES", 21: "DISC_DISCREPANCY_CHECK",
            22: "DISC_OUT_BIT_STATUS", 23: "DISC_OUT_LB_FAIL_STATUS",
            24: "DISC_OUT_FAULT_STATUS", 25: "LTC4281_PMON_STATUS",
            26: "LTC4281_PMON_VOLTAGE_1", 27: "LTC4281_PMON_VOLTAGE_2",
            28: "LTC4281_PMON_CURRENT_1", 29: "LTC4281_PMON_CURRENT_2",
            30: "LTC4281_PMON_POWER_1", 31: "LTC4281_PMON_POWER_2",
            32: "LTC4281_SATA0_STATUS", 33: "LTC4281_SATA0_VOLTAGE_1",
            34: "LTC4281_SATA0_VOLTAGE_2", 35: "LTC4281_SATA0_CURRENT_1",
            36: "LTC4281_SATA0_CURRENT_2", 37: "LTC4281_SATA0_POWER_1",
            38: "LTC4281_SATA0_POWER_2", 39: "LTC4281_SATA1_STATUS",
            40: "LTC4281_SATA1_VOLTAGE_1", 41: "LTC4281_SATA1_VOLTAGE_2",
            42: "LTC4281_SATA1_CURRENT_1", 43: "LTC4281_SATA1_CURRENT_2",
            44: "LTC4281_SATA1_POWER_1", 45: "LTC4281_SATA1_POWER_2",
            46: "LTC4281_GPU_12V_STATUS", 47: "LTC4281_GPU_12V_VOLTAGE_1",
            48: "LTC4281_GPU_12V_VOLTAGE_2", 49: "LTC4281_GPU_12V_CURRENT_1",
            50: "LTC4281_GPU_12V_CURRENT_2", 51: "LTC4281_GPU_12V_POWER_1",
            52: "LTC4281_GPU_12V_POWER_2", 53: "LTC4281_GPU_3V3_STATUS",
            54: "LTC4281_GPU_3V3_VOLTAGE_1", 55: "LTC4281_GPU_3V3_VOLTAGE_2",
            56: "LTC4281_GPU_3V3_CURRENT_1", 57: "LTC4281_GPU_3V3_CURRENT_2",
            58: "LTC4281_GPU_3V3_POWER_1", 59: "LTC4281_GPU_3V3_POWER_2",
            60: "LTC4281_GPU_5V_STATUS", 61: "LTC4281_GPU_5V_VOLTAGE_1",
            62: "LTC4281_GPU_5V_VOLTAGE_2", 63: "LTC4281_GPU_5V_CURRENT_1",
            64: "LTC4281_GPU_5V_CURRENT_2", 65: "LTC4281_GPU_5V_POWER_1",
            66: "LTC4281_GPU_5V_POWER_2", 67: "INA260_PWR_BOARD_VOLTAGE_1",
            68: "INA260_PWR_BOARD_VOLTAGE_2", 69: "INA260_PWR_BOARD_CURRENT_1",
            70: "INA260_PWR_BOARD_CURRENT_2", 71: "INA260_PWR_BOARD_POWER_1",
            72: "INA260_PWR_BOARD_POWER_2", 73: "INA260_PMON_VOLTAGE_1",
            74: "INA260_PMON_VOLTAGE_2", 75: "INA260_PMON_CURRENT_1",
            76: "INA260_PMON_CURRENT_2", 77: "INA260_PMON_POWER_1",
            78: "INA260_PMON_POWER_2", 79: "TMP100_CPLD_TEMP",
            80: "TMP100_GPU_TEMP", 81: "TMP100_CARRIER_TEMP",
            82: "TMP100_PWR_REG_TEMP", 83: "TMP100_PWR_BOARD_TEMP",
            84: "TMP100_IGLOO2_TEMP", 85: "GPU_TEMP",
            86: "HSN_TRANS_DATA_1", 87: "HSN_TRANS_DATA_2",
            88: "HSN_TRANS_DATA_3", 89: "HSN_TRANS_DATA_4",
            90: "HSN_TRANS_DATA_5", 91: "HSN_TRANS_DATA_6",
            92: "HSN_TRANS_DATA_7", 93: "HSN_TRANS_DATA_8",
        }
        
        # Reserved and UART Loopback
        for i in range(94, 125):
            names[i] = "RESERVED"
        for i in range(125, 129):
            names[i] = "UART_LOOPBACK"
        
        return names
    
    def _get_dynamic_meaning(self, index, value):
        """
        Get dynamic meaning based on received value.
        Customize this function to decode status bits and provide meaningful descriptions.
        
        Args:
            index: Data byte index
            value: Received value
            
        Returns:
            String describing the meaning of the value
        """
        # Default: return XX for undefined meanings
        # Customize below for specific signals
        
        # Example implementations (uncomment and modify as needed):
        
        # if index == 11:  # UART_STATUS
        #     return "Timeout" if (value & 0x01) else "OK"
        
        # elif index in [25, 32, 39, 46, 53, 60]:  # LTC4281 STATUS registers
        #     status_bits = []
        #     if value & 0x80: status_bits.append("ON")
        #     if value & 0x40: status_bits.append("COOLDOWN")
        #     if value & 0x20: status_bits.append("SHORT")
        #     if value & 0x10: status_bits.append("ON_PIN")
        #     if value & 0x08: status_bits.append("PGOOD")
        #     if value & 0x04: status_bits.append("OC_COOL")
        #     if value & 0x02: status_bits.append("UV")
        #     if value & 0x01: status_bits.append("OV")
        #     return ", ".join(status_bits) if status_bits else "Normal"
        
        # elif index in self.temp_indices:  # Temperature sensors
        #     return f"{value}°C"
        
        return "XX"


def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern style
    
    window = UARTMonitor()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()