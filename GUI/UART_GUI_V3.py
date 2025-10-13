"""
UART Monitoring Interface
Professional GUI for monitoring UART communication with data validation and control
Version: 3.0 - Updated per feedback
"""

import sys
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QLabel,
    QHeaderView, QGroupBox, QMessageBox, QRadioButton, QButtonGroup,
    QScrollArea,QGridLayout 
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor, QFont, QPalette

class AppStyle:
    # Dark theme colors
    BACKGROUND = "#1e1e1e"
    SURFACE = "#252526"
    SURFACE_LIGHT = "#2d2d30"
    PRIMARY = "#0e639c"
    PRIMARY_DARK = "#094771"
    SUCCESS = "#39ae3d"
    ERROR = "#f44336"
    WARNING = "#ff9800"
    TEXT = "#cccccc"
    TEXT_SECONDARY = "#969696"
    BORDER = "#3e3e42"
    
    # Status colors - Updated per feedback
    STATUS_ENABLED = "#39ae3d"     # Green for enabled/OK
    STATUS_DISABLED = "#c62828"     # Red for disabled/error
    STATUS_NEUTRAL = "#ffffff"      # White for neutral disabled
    STATUS_NA = "#666666"           # Gray for N/A
    
    # Table colors
    TABLE_HEADER = "#2d2d30"
    TABLE_ROW_ALT = "#2a2a2d"
    TABLE_SUCCESS = "#1b5e20"
    TABLE_ERROR = "#b71c1c"
    TABLE_NA = "#424242"            # Gray for N/A cells
    
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
                border: 2px solid #0e639c;
                border-radius: 6px;
                margin-top: 16px;
                padding: 15px;
                padding-top: 20px;
                font-weight: bold;
                font-size: 12px;
            }
            
            QGroupBox::title {
                background-color: #0e639c;
                color: #ffffff;
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 10px;
                left: 10px;
                top: -2px;
                font-size: 11px;
                font-weight: bold;
                border-radius: 3px;
            }
            
            QMessageBox {
                background-color: #2d2d30;
            }
            
            QMessageBox QLabel {
                color: #ffffff;
                font-size: 11px;
                min-width: 300px;
            }
            
            QMessageBox QPushButton {
                min-width: 80px;
                min-height: 28px;
                font-size: 10px;
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
            
            QRadioButton {
                color: #cccccc;
                font-size: 10px;
            }
            
            QTableWidget {
                background-color: #252526;
                alternate-background-color: #252526;;
                border: 1px solid #3e3e42;
                gridline-color: #3e3e42;
                color: #cccccc;
                font-size: 9px;
            }
            
            QTableWidget::item {
                padding: 4px;
            }

            /* YENİ EKLENEN BLOK */
            QHeaderView {
                background-color: #2d2d30;
            }
            
            QHeaderView::section {
                background-color: #2d2d30;
                color: #cccccc;
                padding: 6px;
                border: none;
                border-right: 1px solid #3e3e42;
                border-bottom: 2px solid #0e3d5c;
                font-weight: bold;
                font-size: 9px;
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
    WINDOW_TITLE = "KAANGES ETC TEST SW"
    WINDOW_WIDTH = 1800
    WINDOW_HEIGHT = 950
    TIMER_INTERVAL = 100  # milliseconds (gelen verileri 100ms'de bir okur ve tabloyu günceller)
    PACKET_SIZE = 133
    DATA_SIZE = 132
    
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
        self.disc_type = "OPEN/GND"  # Default disc type
        self.sata_command_to_send = (0, 0)
        self._init_data_limits()
        self._init_ui()
        self._init_timer()
        
    def _init_data_limits(self):
        """Initialize data validation limits"""
        self.data_limits = {
            'min': ['N/A'] * self.DATA_SIZE,
            'max': ['N/A'] * self.DATA_SIZE
        }
        
        # UART packet header and control bytes (fixed values)
        self._set_fixed_limits(0, self.HEADER_1)      # HEADER_1
        self._set_fixed_limits(1, self.HEADER_2)      # HEADER_2
        self._set_fixed_limits(2, self.PACKET_LENGTH) # LENGTH
        self._set_fixed_limits(3, self.PACKET_ID)     # PACKET_ID
        
        # 2-byte measurement pairs - only first byte has limits
        # Second byte is marked as N/A (will be grayed out)
        voltage_current_power_pairs = [
            (26, 27),   # LTC4281_PMON_VOLTAGE
            (28, 29),   # LTC4281_PMON_CURRENT
            (30, 31),   # LTC4281_PMON_POWER
            (33, 34),   # LTC4281_SATA0_VOLTAGE
            (35, 36),   # LTC4281_SATA0_CURRENT
            (37, 38),   # LTC4281_SATA0_POWER
            (40, 41),   # LTC4281_SATA1_VOLTAGE
            (42, 43),   # LTC4281_SATA1_CURRENT
            (44, 45),   # LTC4281_SATA1_POWER
            (47, 48),   # LTC4281_GPU_12V_VOLTAGE
            (49, 50),   # LTC4281_GPU_12V_CURRENT
            (51, 52),   # LTC4281_GPU_12V_POWER
            (54, 55),   # LTC4281_GPU_3V3_VOLTAGE
            (56, 57),   # LTC4281_GPU_3V3_CURRENT
            (58, 59),   # LTC4281_GPU_3V3_POWER
            (61, 62),   # LTC4281_GPU_5V_VOLTAGE
            (63, 64),   # LTC4281_GPU_5V_CURRENT
            (65, 66),   # LTC4281_GPU_5V_POWER
            (67, 68),   # INA260_PWR_BOARD_VOLTAGE
            (69, 70),   # INA260_PWR_BOARD_CURRENT
            (71, 72),   # INA260_PWR_BOARD_POWER
            (73, 74),   # INA260_PMON_VOLTAGE
            (75, 76),   # INA260_PMON_CURRENT
            (77, 78),   # INA260_PMON_POWER
        ]
        
        # Set limits for first byte of each pair
        for first_byte, second_byte in voltage_current_power_pairs:
            self.data_limits['min'][first_byte] = 0
            self.data_limits['max'][first_byte] = 255

        
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
        self.setMinimumSize(1200, 700)
        self.setStyleSheet(AppStyle.get_stylesheet())
        
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
        
        # Right side: Status indicators and controls with scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setMinimumWidth(300)
        scroll_area.setMaximumWidth(350)
        
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #1e1e1e;
                border: none;
            }
        """)

        scroll_widget = QWidget()
        # Scroll widget arka plan rengini ayarla
        scroll_widget.setAutoFillBackground(True)
        palette = scroll_widget.palette()
        palette.setColor(QPalette.Window, QColor("#1e1e1e"))
        scroll_widget.setPalette(palette)
        
        right_side_layout = QVBoxLayout(scroll_widget)
        right_side_layout.setSpacing(8)
        right_side_layout.setContentsMargins(5, 5, 5, 5)
        right_side_layout.addWidget(self._create_status_panel())
        right_side_layout.addWidget(self._create_disc_in_status())
        right_side_layout.addWidget(self._create_control_panel())
        right_side_layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        content_layout.addWidget(scroll_area, stretch=3)
        
        main_layout.addLayout(content_layout)
        
    def _init_timer(self):
        """Initialize the data reading timer"""
        self.timer = QTimer()
        self.timer.timeout.connect(self._read_uart_data)
        
    def _create_connection_panel(self):
        """Create the connection configuration panel"""
        panel = QGroupBox("⚡ CONNECTION SETTINGS")
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        
        # COM Port selection
        layout.addWidget(QLabel("PORT:"))
        self.com_combo = QComboBox()
        self.com_combo.setMinimumWidth(200)
        self._refresh_com_ports()
        layout.addWidget(self.com_combo)
        
        # Baud rate selection
        layout.addWidget(QLabel("BAUD RATE:"))
        self.baud_combo = QComboBox()
        self.baud_combo.setMinimumWidth(120)
        self.baud_combo.addItems(['9600', '19200', '38400', '57600', '115200'])
        self.baud_combo.setCurrentText('115200')
        layout.addWidget(self.baud_combo)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 REFRESH")
        refresh_btn.setMinimumWidth(100)
        refresh_btn.clicked.connect(self._refresh_com_ports)
        layout.addWidget(refresh_btn)
        
        # Connect button
        self.connect_btn = QPushButton("🔌 CONNECT")
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
        self.status_label = QLabel("● DISCONNECTED")
        self.status_label.setStyleSheet(f"color: {AppStyle.ERROR}; font-weight: bold; font-size: 11px;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        panel.setLayout(layout)
        return panel
    
    def _create_data_table(self):
        """Create the main data table"""
        table = QTableWidget()
        
        rows_per_column = 44
        table.setRowCount(rows_per_column)
        table.setColumnCount(18)
        
        # Updated headers - all in English
        headers = ['#', 'SIGNAL', 'MIN', 'VALUE', 'MAX', 'MEANING'] * 3
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
            1: 165,  # Signal name
            2: 40,   # Min
            3: 40,   # Value
            4: 40,   # Max
            5: 120  # Meaning
        }
        
        for i in range(18):
            col_type = i % 6
            table.setColumnWidth(i, column_widths[col_type])

        header = table.horizontalHeader()
        for i in range(18):
                header.setSectionResizeMode(i, QHeaderView.Stretch)

        # fixed columns
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        header.setSectionResizeMode(8, QHeaderView.Fixed)
        header.setSectionResizeMode(9, QHeaderView.Fixed)
        header.setSectionResizeMode(10, QHeaderView.Fixed)
        header.setSectionResizeMode(12, QHeaderView.Fixed)
        header.setSectionResizeMode(14, QHeaderView.Fixed)
        header.setSectionResizeMode(15, QHeaderView.Fixed)
        header.setSectionResizeMode(16, QHeaderView.Fixed)
         
        # changing columns
        header.setSectionResizeMode(1, QHeaderView.Stretch)   # SIGNAL
        header.setSectionResizeMode(5, QHeaderView.Stretch)   # MEANING
        header.setSectionResizeMode(7, QHeaderView.Stretch)   # SIGNAL
        header.setSectionResizeMode(11, QHeaderView.Stretch)  # MEANING
        header.setSectionResizeMode(13, QHeaderView.Stretch)  # SIGNAL
        header.setSectionResizeMode(17, QHeaderView.Stretch)  # MEANING
            
        self._populate_table(table)
        
        # '#' sütunlarını ortalama ve arka plan rengi ayarlama
        for row in range(rows_per_column):
            for col in [0, 6, 12]:  # '#' sütunları (0, 6, 12)
                item = table.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setBackground(QColor("#224055"))  
        
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        return table
    
    def _populate_table(self, table):
        """Populate the table with initial data"""
        signal_names = self._get_signal_names()
        rows_per_column = 44
        
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
                
                # Check if this is a second byte of a 2-byte pair (should be grayed out)
                is_second_byte = self._is_second_byte_of_pair(i)
                
                # Min value
                min_val = self.data_limits['min'][i]
                if min_val == 'N/A':
                    min_item = QTableWidgetItem("N/A")
                    min_item.setBackground(QColor(AppStyle.TABLE_NA))
                else:
                    min_item = QTableWidgetItem(f"0x{min_val:02X}")
                table.setItem(row, base_col + 2, min_item)
                
                # Current value with color coding
                
                value_item = QTableWidgetItem("0")
            
                value_item.setBackground(self._get_value_color(i, 0))
                table.setItem(row, base_col + 3, value_item)
                
                # Max value
                max_val = self.data_limits['max'][i]
                if max_val == 'N/A':
                    max_item = QTableWidgetItem("N/A")
                    max_item.setBackground(QColor(AppStyle.TABLE_NA))
                else:
                    max_item = QTableWidgetItem(f"0x{max_val:02X}")
                table.setItem(row, base_col + 4, max_item)
                
                # Meaning
                meaning_item = QTableWidgetItem("N/A")
                table.setItem(row, base_col + 5, meaning_item)
    
    def _is_second_byte_of_pair(self, index):
        """Check if this index is the second byte of a 2-byte measurement pair"""
        second_bytes = [27, 29, 31, 34, 36, 38, 41, 43, 45, 48, 50, 52, 
                       55, 57, 59, 62, 64, 66, 68, 70, 72, 74, 76, 78]
        return index in second_bytes
    
    def _get_value_color(self, index, value):
        """Determine the appropriate color for a value"""
        # Temperature sensors - always green
        if index in self.temp_indices:
            return QColor(27, 94, 32)
        
        min_val = self.data_limits['min'][index]
        max_val = self.data_limits['max'][index]
        
        # N/A values
        if min_val == 'N/A' or max_val == 'N/A':
            return QColor(66, 66, 66)  # Gray for N/A
        
        # Valid range - green
        if min_val <= value <= max_val:
            return QColor(27, 94, 32)
        
        # Out of range - red (error)
        return QColor(183, 28, 28)
    
    def _create_status_panel(self):
        """Create the status indicator panel - Updated per feedback"""
        panel = QGroupBox("📊 STATUS INDICATORS")
        panel.setMaximumWidth(350)

        layout = QGridLayout()
        layout.setSpacing(6)
        
        self.status_buttons = []
        # Updated labels: SATA0, SATA1, GPU, PMON
        status_labels = ["SATA0", "SATA1", "GPU STATUS", "PMON STATUS"]
        
        for idx, label in enumerate(status_labels):
            # Set initial text based on button type
            if "PMON" in label:
                initial_text = f"● {label}\nPOWER FAIL"
            else:
                initial_text = f"● {label}\nDISABLED"
            
            btn = QPushButton(initial_text)
            btn.setEnabled(False)
            btn.setMinimumHeight(45)
            btn.setMaximumHeight(50)
            # Initial state depends on the type
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {AppStyle.STATUS_DISABLED};
                    color: white;
                    font-weight: bold;
                    font-size: 11px;
                    border-radius: 4px;
                    text-align: left;
                    padding-left: 10px;
                }}
            """)

            self.status_buttons.append(btn)

            row = idx // 2  # Satır: 0, 0, 1, 1
            col = idx % 2   # Sütun: 0, 1, 0, 1
            layout.addWidget(btn, row, col)

        panel.setLayout(layout)
        return panel
    
    def _create_disc_in_status(self):
        """Create DISC_IN_STATUS indicator - New feature"""
        panel = QGroupBox("📌 DISC_IN_STATUS")
        panel.setMaximumWidth(350)
        layout = QGridLayout()
        layout.setSpacing(5)
        
        self.disc_in_labels = []
        for i in range(4):
            label = QLabel(f"DISC_IN_{i}: OPEN")
            label.setStyleSheet("""
                QLabel {
                    background-color: #2d2d30;
                    color: #cccccc;
                    font-weight: bold;
                    font-size: 11px;
                    padding: 8px;
                    border-radius: 3px;
                }
            """)
            label.setMinimumHeight(28)
            label.setMaximumHeight(32)
            self.disc_in_labels.append(label)
            
            row = i // 2
            col = i % 2
            layout.addWidget(label, row, col)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        panel.setLayout(layout)
        return panel
    
    def _create_control_panel(self):
        """Create the control button panel"""
        panel = QGroupBox("CONTROL PANEL")
        panel.setMaximumWidth(350)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(6)
        panel.setAutoFillBackground(True)
        
        # DISC Type Selection
        main_layout.addWidget(self._create_disc_type_selector())
        
        # DISC OUT Controls
        main_layout.addWidget(self._create_disc_out_controls())
        
        # SATA Zeroize Controls
        main_layout.addWidget(self._create_sata_controls())
        
        # LED2 Controls
        main_layout.addWidget(self._create_led_controls())
        
        main_layout.addStretch()
        panel.setLayout(main_layout)
        return panel
    
    def _create_disc_type_selector(self):
        """Create DISC type selector - New feature"""
        group = QGroupBox("🔧 DISC TYPE")
        layout = QHBoxLayout()
        layout.setSpacing(4)
        
        self.disc_type_group = QButtonGroup()
        
        # OPEN/GND (default)
        self.disc_gnd_radio = QRadioButton("OPEN/GND")
        self.disc_gnd_radio.setChecked(True)
        self.disc_gnd_radio.setStyleSheet("font-size: 11px;")
        self.disc_gnd_radio.toggled.connect(lambda: self._set_disc_type("OPEN/GND"))
        
        # OPEN/28V
        self.disc_28v_radio = QRadioButton("OPEN/28V")
        self.disc_28v_radio.setStyleSheet("font-size: 11px;")
        self.disc_28v_radio.toggled.connect(lambda: self._set_disc_type("OPEN/28V"))
        
        self.disc_type_group.addButton(self.disc_gnd_radio)
        self.disc_type_group.addButton(self.disc_28v_radio)
        
        layout.addWidget(self.disc_gnd_radio)
        layout.addWidget(self.disc_28v_radio)
        
        group.setLayout(layout)
        return group
    
    def _set_disc_type(self, disc_type):
        """Set the DISC type and send an updated command packet."""
        self.disc_type = disc_type
        print(f"DISC type set to: {disc_type}")
        self._build_and_send_command_packet() # Send updated state

    
    def _create_disc_out_controls(self):
        """Create DISC OUT control buttons - Updated from TX"""
        group = QGroupBox("📤 DISC OUT CONTROL")
        layout = QGridLayout()
        layout.setSpacing(4)
        
        self.disc_out_buttons = []
        for i in range(4):
            btn = QPushButton(f"DISC OUT {i+1}\nDISABLED")
            btn.setCheckable(True)
            btn.setMinimumHeight(40)
            btn.setMaximumHeight(45)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {AppStyle.STATUS_NA};
                    color: white;
                    font-size: 11px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {AppStyle.PRIMARY};
                }}
                QPushButton:checked {{
                    background-color: {AppStyle.SUCCESS};
                }}
            """)
            btn.clicked.connect(lambda checked, b=btn, idx=i: self._toggle_disc_out_button(b, checked, idx))
            self.disc_out_buttons.append(btn)
            

            row = i // 2
            col = i % 2
            layout.addWidget(btn, row, col)
        
        group.setLayout(layout)
        return group
    
    def _create_sata_controls(self):
        """Create SATA ZEROIZE control buttons - Updated"""
        group = QGroupBox("💾 SATA ZEROIZE CONTROL")
        layout = QVBoxLayout()
        layout.setSpacing(4)
        
        self.sata1_btn = QPushButton("ONLY SATA1\nZEROIZE ACTIVATE")
        self.sata1_btn.setMinimumHeight(36)
        self.sata1_btn.setMaximumHeight(50)
        self.sata1_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppStyle.STATUS_NEUTRAL};
                color: black;
                font-weight: 600;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: #e0e0e0;
            }}
            QPushButton:pressed {{
                background-color: {AppStyle.STATUS_DISABLED};
                color: white;
            }}
        """)
        self.sata1_btn.clicked.connect(self._activate_sata1)
        layout.addWidget(self.sata1_btn)
        
        self.satas_btn = QPushButton("SATA0 && SATA1\nZEROIZE ACTIVATE")
        self.satas_btn.setMinimumHeight(36)
        self.satas_btn.setMaximumHeight(50)
        self.satas_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppStyle.STATUS_NEUTRAL};
                color: black;
                font-weight: 600;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: #e0e0e0;
            }}
            QPushButton:pressed {{
                background-color: {AppStyle.STATUS_DISABLED};
                color: white;
            }}
        """)
        self.satas_btn.clicked.connect(self._activate_satas)
        layout.addWidget(self.satas_btn)
        
        group.setLayout(layout)
        return group
    
    def _create_led_controls(self):
        """Create LED2 control buttons - Updated"""
        group = QGroupBox("💡 LED2 CONTROL")
        layout = QHBoxLayout()
        layout.setSpacing(4)
        
        self.led_buttons = []
        led_data = [("R", "#e53935"), ("G", "#43a047"), ("B", "#1e88e5")]
        
        for name, color in led_data:
            btn = QPushButton(f"● LED {name}\nDISABLED")
            btn.setCheckable(True)
            btn.setMinimumHeight(36)
            btn.setMaximumHeight(40)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {AppStyle.STATUS_NA};
                    color: {color};
                    font-weight: bold;
                    font-size: 10px;
                    text-align: left;
                    padding-left: 10px;
                }}
                QPushButton:hover {{
                    background-color: {AppStyle.PRIMARY};
                    color: white;
                }}
                QPushButton:checked {{
                    background-color: {AppStyle.SUCCESS};
                    color: white;
                }}
            """)
            btn.clicked.connect(lambda checked, b=btn, c=color, n=name: self._toggle_led_button(b, checked, c, n))
            self.led_buttons.append(btn)
            layout.addWidget(btn)
        
        group.setLayout(layout)
        return group
    
    def _check_connection(self):
        """Check if serial connection is active"""
        if not self.is_connected:
            QMessageBox.warning(self, 'WARNING', 'NOT CONNECTED! PLEASE CONNECT FIRST.')
            return False
        return True
    
    def _activate_sata1(self):
        """Activate SATA1 with confirmation"""
        if not self._check_connection():
            return
        
        reply = QMessageBox.question(
            self, 'SATA1 ZEROIZE ACTIVATION',
            'SATA1 WILL BE ZEROIZED. DO YOU CONFIRM?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Set the one-shot command and send the packet
            self.sata_command_to_send = (0xAA, 0x55)
            self._build_and_send_command_packet()
            QMessageBox.information(self, 'INFO', 'SATA1 Zeroize command sent.')
    
    def _activate_satas(self):
        """Activate both SATA0 and SATA1 with confirmation"""
        if not self._check_connection():
            return
        
        reply = QMessageBox.question(
            self, 'SATA ZEROIZE ACTIVATION',
            'SATA1 AND SATA0 WILL BE ZEROIZED. ARE YOU SURE?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Set the one-shot command and send the packet
            self.sata_command_to_send = (0xBB, 0x44)
            self._build_and_send_command_packet()
            QMessageBox.information(self, 'INFO', 'SATA0 & SATA1 Zeroize command sent.')
            
    def _build_and_send_command_packet(self):
        """
        Gathers the current state of all UI controls, builds the 37-byte command packet,
        calculates the checksum, and sends it via UART.
        """
        if not self.is_connected:
            QMessageBox.warning(self, 'WARNING', 'NOT CONNECTED! PLEASE CONNECT FIRST.')
            return

        # Initialize a 37-byte packet with all zeros.
        command_packet = bytearray(37)

        # Bytes 0-4: Headers, Packet length, ID
        command_packet[0] = self.HEADER_1
        command_packet[1] = self.HEADER_2
        command_packet[2] = 37  # Packet length
        command_packet[3] = 0x01 # ID

        # Byte 4: Sense Select
        if self.disc_type == "OPEN/28V":
            command_packet[4] = 0x01
        else: # OPEN/GND
            command_packet[4] = 0x00

        # Byte 5: Disc Out Drives
        disc_out_byte = 0
        for i, button in enumerate(self.disc_out_buttons):
            if button.isChecked():
                disc_out_byte |= (1 << i)  # Set bit 'i' to 1
        command_packet[5] = disc_out_byte

        # Bytes 6 & 7: SATA Zeroize Command
        # This is set by _activate_sata... functions right before sending.
        command_packet[6] = self.sata_command_to_send[0]
        command_packet[7] = self.sata_command_to_send[1]

        # Byte 8: Zeroize SATA LSB (Assuming this is a separate flag, not used by buttons)
        # Kept as 0 for now as per your description.
        command_packet[8] = 0 

        # Byte 9: LED Control
        led_byte = 0
        if self.led_buttons[0].isChecked(): led_byte |= 0b001  # Red LED
        if self.led_buttons[1].isChecked(): led_byte |= 0b010  # Green LED
        if self.led_buttons[2].isChecked(): led_byte |= 0b100  # Blue LED
        command_packet[9] = led_byte

        # Bytes 10-35 are already 0 (Reserved)

        # Byte 36: Checksum
        # Calculate checksum over the first 36 data bytes.
        checksum = (256 - (sum(command_packet[0:36]) % 256)) % 256
        command_packet[36] = checksum

        # --- Send the final packet ---
        try:
            self.serial_port.write(command_packet)
            print(f"Sent Packet: {' '.join(f'{b:02X}' for b in command_packet)}")
        except Exception as e:
            QMessageBox.critical(self, 'Send Error', f'Failed to send command: {str(e)}')
        
        # Reset one-shot commands after sending
        self.sata_command_to_send = (0, 0)

    
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
            
            self.connect_btn.setText("⏸ DISCONNECT")
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
            self.status_label.setText("● CONNECTED")
            self.status_label.setStyleSheet(f"color: {AppStyle.SUCCESS}; font-weight: bold; font-size: 11px;")
            
            self.timer.start(self.TIMER_INTERVAL)
            
        except Exception as e:
            self.status_label.setText(f"● ERROR: {str(e)}")
            self.status_label.setStyleSheet(f"color: {AppStyle.ERROR}; font-weight: bold; font-size: 11px;")
    
    def _disconnect_serial(self):
        """Close serial connection"""
        self.timer.stop()
        if self.serial_port:
            self.serial_port.close()
        
        self.is_connected = False
        self.connect_btn.setText("🔌 CONNECT")
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
        self.status_label.setText("● DISCONNECTED")
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
        """
        Validates the packet using the Two's Complement checksum method.
        Checks if the sum of ALL 133 bytes is zero (in 8-bit).
        """
        if len(packet) != self.PACKET_SIZE:
            return False

        # Paketin tamamını (133 byte) topla ve sonucun 8-bitlik değerinin
        # sıfır olup olmadığını kontrol et.
        if sum(packet) & 0xFF == 0:
            return True
        else:
            return False
    
    def _process_packet(self, packet):
        """Process received packet data"""
        # Transfer the incoming packet data to the received_data list.
        for i in range(self.DATA_SIZE):
            if i < len(packet):
                self.received_data[i] = packet[i]
        
        # These functions will now be called with the correct data.
        self._update_table()
        self._update_status_buttons()
        self._update_disc_in_status()
        
    def _update_table(self):
        """Update table with new data"""
        rows_per_column = 44
        
        for i in range(self.DATA_SIZE):
            col_group = i // rows_per_column
            row = i % rows_per_column
            second_voltage_bytes = [26,33,40,47,54,61,67,73]
            second_current_bytes = [28,35,42,49,56,63,69,75]
            second_power_bytes   = [30,37,44,51,58,65,71,77]

            if col_group < 3:
                base_col = col_group * 6
                value = self.received_data[i]
                next_value = self.received_data[i+1]

                # Update value
                item = self.table_widget.item(row, base_col + 3)
                # Update meaning
                meaning_item = self.table_widget.item(row, base_col + 5)
                if item:
                    item.setText(f"0x{value:02X}")
                    item.setBackground(self._get_value_color(i, value))
                    meaning_item.setBackground(self._get_value_color(i, value))
                
                
                if meaning_item:
                    if i in second_voltage_bytes:
                        meaning_text = self._get_voltage_meaning((i), value, next_value)
                    elif i in second_current_bytes:
                        meaning_text = self._get_current_meaning((i), value, next_value)
                    elif i in  second_power_bytes:
                        meaning_text = self._get_power_meaning((i), value, next_value)
                    else:
                        meaning_text, is_error = self._get_dynamic_meaning(i, value)
                        # Set background color based on the error status
                        if is_error:
                            meaning_item.setBackground(QColor(183, 28, 28))
                        else:
                            meaning_item.setBackground(QColor(66, 66, 66))
                    meaning_item.setText(meaning_text)
                        
                    
        
    def _update_status_buttons(self):
        """Update status indicator buttons - Updated per feedback"""
        status_indices = [32, 39, 46, 25]  # SATA0, SATA1, GPU_12V, PMON
        
        for i, idx in enumerate(status_indices):
            if idx < len(self.received_data):
                status = self.received_data[idx]
                is_on = (status & 0x80) != 0
                
                btn = self.status_buttons[i]
                label = btn.text().split('\n')[0].replace("● ", "")
                
                # SATA0 and SATA1 (indices 0, 1)
                if i in [0, 1]:
                    if is_on:
                        btn.setText(f"● {label}\nENABLED")
                        btn.setStyleSheet(f"""
                            QPushButton {{
                                background-color: {AppStyle.STATUS_ENABLED};
                                color: white;
                                font-weight: bold;
                                font-size: 9px;
                                border-radius: 4px;
                                text-align: left;
                                padding-left: 10px;
                            }}
                        """)
                    else:
                        btn.setText(f"● {label}\nDISABLED")
                        btn.setStyleSheet(f"""
                            QPushButton {{
                                background-color: {AppStyle.STATUS_DISABLED};
                                color: white;
                                font-weight: bold;
                                font-size: 9px;
                                border-radius: 4px;
                                text-align: left;
                                padding-left: 10px;
                            }}
                        """)
                
                # GPU STATUS (index 2)
                elif i == 2:
                    if is_on:
                        btn.setText(f"● {label}\nENABLED")
                        btn.setStyleSheet(f"""
                            QPushButton {{
                                background-color: {AppStyle.STATUS_ENABLED};
                                color: white;
                                font-weight: bold;
                                font-size: 9px;
                                border-radius: 4px;
                                text-align: left;
                                padding-left: 10px;
                            }}
                        """)
                    else:
                        btn.setText(f"● {label}\nDISABLED")
                        btn.setStyleSheet(f"""
                            QPushButton {{
                                background-color: {AppStyle.STATUS_DISABLED};
                                color: black;
                                font-weight: bold;
                                font-size: 9px;
                                border-radius: 4px;
                                text-align: left;
                                padding-left: 10px;
                            }}
                        """)
                
                # PMON STATUS (index 3)
                elif i == 3:
                    if is_on:
                        btn.setText(f"● {label}\nPOWER OK")
                        btn.setStyleSheet(f"""
                            QPushButton {{
                                background-color: {AppStyle.STATUS_ENABLED};
                                color: white;
                                font-weight: bold;
                                font-size: 9px;
                                border-radius: 4px;
                                text-align: left;
                                padding-left: 10px;
                            }}
                        """)
                    else:
                        btn.setText(f"● {label}\nPOWER FAIL")
                        btn.setStyleSheet(f"""
                            QPushButton {{
                                background-color: {AppStyle.STATUS_DISABLED};
                                color: white;
                                font-weight: bold;
                                font-size: 9px;
                                border-radius: 4px;
                                text-align: left;
                                padding-left: 10px;
                            }}
                        """)
    
    def _update_disc_in_status(self):
        """Update DISC_IN_STATUS indicators"""
        # Assuming DISC_IN_VALUES is at index 20
        disc_in_value = self.received_data[20]
        
        for i in range(4):
            bit_value = (disc_in_value >> i) & 0x01
            if self.disc_type == "OPEN/GND":
                status_text = "GND" if bit_value else "OPEN"
            else:  # OPEN/28V
                status_text = "28V" if bit_value else "OPEN"
            
            self.disc_in_labels[i].setText(f"DISC_IN_{i}: {status_text}")
    
    def _toggle_disc_out_button(self, button, checked, index):
        """Toggle DISC OUT button state"""
        if not self._check_connection():
            button.setChecked(False)
            return
        
        if checked:
            button.setText(button.text().split('\n')[0] + "\nENABLED")
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {AppStyle.SUCCESS};
                    color: white;
                    font-weight: bold;
                    font-size: 8px;
                }}
            """)
        else:
            button.setText(button.text().split('\n')[0] + "\nDISABLED")
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {AppStyle.STATUS_NA};
                    color: white;
                    font-weight: bold;
                    font-size: 8px;
                }}
            """)
        self._build_and_send_command_packet()
    
    def _toggle_led_button(self, button, checked, color, name):
        """Toggle LED button state"""
        if not self._check_connection():
            button.setChecked(False)
            return
        
        if checked:
            button.setText(f"● LED {name}\nENABLED")
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {AppStyle.SUCCESS};
                    color: white;
                    font-weight: bold;
                    font-size: 8px;
                    text-align: left;
                    padding-left: 10px;
                }}
            """)
        else:
            button.setText(f"● LED {name}\nDISABLED")
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {AppStyle.STATUS_NA};
                    color: {color};
                    font-weight: bold;
                    font-size: 8px;
                    text-align: left;
                    padding-left: 10px;
                }}
            """)
        self._build_and_send_command_packet() # Send updated state
    
    
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
            20: "DISC_IN_STATUS", 21: "DISC_DISCREPANCY_CHECK",
            22: "DISC_OUT_BIT_STATUS", 23: "DISC_OUT_LB_FAIL_STATUS",
            24: "DISC_OUT_FAULT_STATUS", 25: "LTC4281_CPU_12V_STATUS",
            26: "LTC4281_CPU_VOLTAGE_1", 27: "LTC4281_CPU_VOLTAGE_2",
            28: "LTC4281_CPU_CURRENT_1", 29: "LTC4281_CPU_CURRENT_2",
            30: "LTC4281_CPU_POWER_1", 31: "LTC4281_CPU_POWER_2",
            32: "LTC4281_SATA0_3V3_STATUS", 33: "LTC4281_SATA0_3V3_VOLTAGE_1",
            34: "LTC4281_SATA0_3V3_VOLTAGE_2", 35: "LTC4281_SATA0_3V3_CURRENT_1",
            36: "LTC4281_SATA0_3V3_CURRENT_2", 37: "LTC4281_SATA0_3V3_POWER_1",
            38: "LTC4281_SATA0_3V3_POWER_2", 39: "LTC4281_SATA1_3V3_STATUS",
            40: "LTC4281_SATA1_3V3_VOLTAGE_1", 41: "LTC4281_SATA1_3V3_VOLTAGE_2",
            42: "LTC4281_SATA1_3V3_CURRENT_1", 43: "LTC4281_SATA1_3V3_CURRENT_2",
            44: "LTC4281_SATA1_3V3_POWER_1", 45: "LTC4281_SATA1_3V3_POWER_2",
            46: "LTC4281_GPU_12V_STATUS", 47: "LTC4281_GPU_12V_VOLTAGE_1",
            48: "LTC4281_GPU_12V_VOLTAGE_2", 49: "LTC4281_GPU_12V_CURRENT_1",
            50: "LTC4281_GPU_12V_CURRENT_2", 51: "LTC4281_GPU_12V_POWER_1",
            52: "LTC4281_GPU_12V_POWER_2", 53: "LTC4281_GPU_5V_STATUS",
            54: "LTC4281_GPU_5V_VOLTAGE_1", 55: "LTC4281_GPU_5V_VOLTAGE_2",
            56: "LTC4281_GPU_5V_CURRENT_1", 57: "LTC4281_GPU_5V_CURRENT_2",
            58: "LTC4281_GPU_5V_POWER_1", 59: "LTC4281_GPU_5V_POWER_2",
            60: "LTC4281_GPU_3V3_STATUS", 61: "LTC4281_GPU_3V3_VOLTAGE_1",
            62: "LTC4281_GPU_3V3_VOLTAGE_2", 63: "LTC4281_GPU_3V3_CURRENT_1",
            64: "LTC4281_GPU_3V3_CURRENT_2", 65: "LTC4281_GPU_3V3_POWER_1",
            66: "LTC4281_GPU_3V3_POWER_2", 67: "INA260_PWR_BOARD_27V_VOLTAGE_1",
            68: "INA260_PWR_BOARD_27V_VOLTAGE_2", 69: "INA260_PWR_BOARD_27V_CURRENT_1",
            70: "INA260_PWR_BOARD_27V_CURRENT_2", 71: "INA260_PWR_BOARD_27V_POWER_1",
            72: "INA260_PWR_BOARD_27V_POWER_2", 73: "INA260_CPLD_3V3_VOLTAGE_1",
            74: "INA260_CPLD_3V3_VOLTAGE_2", 75: "INA260_CPLD_3V3_CURRENT_1",
            76: "INA260_CPLD_3V3_CURRENT_2", 77: "INA260_CPLD_3V3_POWER_1",
            78: "INA260_CPLD_3V3_POWER_2", 79: "TMP100_CPLD_TEMP",
            80: "TMP100_GPU_TEMP", 81: "TMP100_CARRIER_TEMP",
            82: "TMP100_PWR_REG_TEMP", 83: "TMP100_PWR_BOARD_TEMP",
            84: "TMP100_IGLOO2_TEMP", 85: "GPU_TEMP",
            86: "HSN_TRANS_DATA_1", 87: "HSN_TRANS_DATA_2",
            88: "HSN_TRANS_DATA_3", 89: "HSN_TRANS_DATA_4",
            90: "HSN_TRANS_DATA_5", 91: "HSN_TRANS_DATA_6",
            92: "HSN_TRANS_DATA_7", 93: "HSN_TRANS_DATA_8",
        }
        
        # Reserved and UART Loopback
        for i in range(94, 127):
            names[i] = "RESERVED"
        for i in range(128, 132):
            names[i] = "UART_LOOPBACK"
        
        return names
    
    def _get_dynamic_meaning(self, index, value):
        """
        Get dynamic meaning based on the received value.
        This function is customized to show different interpretations based on the data index.
        """
        # Show data for specified indices in 8-bit binary format.
        binary_indices = list(range(6, 26)) + [32, 39, 46, 53, 60]
        if index in binary_indices:
            is_error = False  
            
            # Check if only a single bit is set to 1 (indicates an error/status).
            if index == 10:
                if (value & 0x3F) != 0:
                    is_error = True
            elif index == 21:
                if (value & 0x1F) != 0:
                    is_error = True
            elif index in [14, 23]:
                if (value & 0x0F) != 0:
                    is_error = True
            elif index == 15:
                if (value & 0x07) != 0:
                    is_error = True
            elif index in [11, 12, 13, 16, 18, 19]:
                if (value & 0x01) != 0:
                    is_error = True
            else:
                is_error = (value != 0)        
            
            # Format the binary string with spaces between bits for readability.
            binary_string = f"{value:08b}"
            spaced_binary_string = ' '.join(binary_string)
            
            # Return the formatted text and the error status as a tuple.
            return (f"0b {spaced_binary_string}", is_error)
        
        return ("N/A", False)


    def _get_voltage_meaning(self, index, msb_value, lsb_value):
        """
        Calculates the voltage from MSB and LSB values and updates the table item.
        """
        # 1. Combine MSB and LSB to get a 16-bit value
        combined_value = (msb_value << 8) | lsb_value

        # 2. Apply the specific voltage scaling factor
        if index in [26, 47]:  # LTC4281 12V mode 
            voltage_value = combined_value * (0.254e-3)
            return f"{voltage_value:.3f} V"
        elif index in [33, 40, 61]:  # LTC4281 3v3 mode 
            voltage_value = combined_value * (0.0847e-3)
            return f"{voltage_value:.3f} V"
        elif index in [54]:  # LTC4281 5v mode 
            voltage_value = combined_value * (0.127e-3)
            return f"{voltage_value:.3f} V"
        elif index in [67, 73]:  # INA260 mode
            voltage_value = combined_value * (1.25e-3)
            return f"{voltage_value:.3f} V"
        else:
            return "N/A"


    def _get_current_meaning(self, index, msb_value, lsb_value):
        """
        Calculates the current from MSB and LSB values and updates the table item.
        """
        # 1. Combine MSB and LSB to get a 16-bit value
        combined_value = (msb_value << 8) | lsb_value

        # 2. Apply the specific current scaling factor
        if index in [28, 35, 42, 49, 56, 63]:  # LTC4281 mode 
            current_value = combined_value * (0.305e-3)
            return f"{current_value:.3f} A"
        elif index in [69, 75]:  # INA260 mode
            current_value = combined_value * (1.25e-3)
            return f"{current_value:.3f} A"  
        else:
            return "N/A"


    def _get_power_meaning(self, index, msb_value, lsb_value):
        """
        Calculates the power from MSB and LSB values and updates the table item.
        """
        # 1. Combine MSB and LSB to get a 16-bit value
        combined_value = (msb_value << 8) | lsb_value

        # 2. Apply the specific power scaling factor
        if index in [30, 51]:  # LTC4281 12V mode 
            power_value = combined_value * (5.08e-3)
            return f"{power_value:.3f} W"
        elif index in [37, 44, 65]:  # LTC4281 3V3 V mode 
            power_value = combined_value * (1.69e-3)
            return f"{power_value:.3f} W"
        elif index in [58]:  # LTC4281 5V mode 
            power_value = combined_value * (2.54e-3)
            return f"{power_value:.3f} W"
        elif index in [71, 77]:  # INA260 mode
            power_value = combined_value * (10e-3)
            return f"{power_value:.3f} W"
        else:
            return "N/A"

def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = UARTMonitor()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()