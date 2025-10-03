import sys
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QComboBox, QPushButton, QTableWidget, 
                             QTableWidgetItem, QLabel, QSpinBox, QHeaderView,
                             QGroupBox, QGridLayout, QMessageBox)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor, QFont

class UARTMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.is_connected = False
        
        # Veri limitleri - Sadece Voltage, Current, Power için aralıklar
        self.data_limits = {
            'min': ['xx'] * 128,  # Minimum değerler
            'max': ['xx'] * 128   # Maximum değerler
        }
        
        # UART Paket Header ve Kontrol Byte'ları (Sabit değerler)
        self.data_limits['min'][0] = 0x41   # HEADER_1
        self.data_limits['max'][0] = 0x41
        self.data_limits['min'][1] = 0x56   # HEADER_2
        self.data_limits['max'][1] = 0x56
        self.data_limits['min'][2] = 0x85   # LENGTH (133 decimal)
        self.data_limits['max'][2] = 0x85
        self.data_limits['min'][3] = 0x02   # PACKET_ID
        self.data_limits['max'][3] = 0x02
        
        # LTC4281_PMON - Voltage, Current, Power limitleri (Byte 26-31)
        # VOLTAGE (MSB+LSB olarak hesaplanacak, şimdilik byte bazında)
        self.data_limits['min'][26] = 0    # PMON_VOLTAGE_1 (MSB)
        self.data_limits['max'][26] = 255
        self.data_limits['min'][27] = 0    # PMON_VOLTAGE_2 (LSB)
        self.data_limits['max'][27] = 255
        self.data_limits['min'][28] = 0    # PMON_CURRENT_1 (MSB)
        self.data_limits['max'][28] = 255
        self.data_limits['min'][29] = 0    # PMON_CURRENT_2 (LSB)
        self.data_limits['max'][29] = 255
        self.data_limits['min'][30] = 0    # PMON_POWER_1 (MSB)
        self.data_limits['max'][30] = 255
        self.data_limits['min'][31] = 0    # PMON_POWER_2 (LSB)
        self.data_limits['max'][31] = 255
        
        # LTC4281_SATA0 - Voltage, Current, Power limitleri (Byte 33-38)
        self.data_limits['min'][33] = 0    # SATA0_VOLTAGE_1
        self.data_limits['max'][33] = 255
        self.data_limits['min'][34] = 0    # SATA0_VOLTAGE_2
        self.data_limits['max'][34] = 255
        self.data_limits['min'][35] = 0    # SATA0_CURRENT_1
        self.data_limits['max'][35] = 255
        self.data_limits['min'][36] = 0    # SATA0_CURRENT_2
        self.data_limits['max'][36] = 255
        self.data_limits['min'][37] = 0    # SATA0_POWER_1
        self.data_limits['max'][37] = 255
        self.data_limits['min'][38] = 0    # SATA0_POWER_2
        self.data_limits['max'][38] = 255
        
        # LTC4281_SATA1 - Voltage, Current, Power limitleri (Byte 40-45)
        self.data_limits['min'][40] = 0    # SATA1_VOLTAGE_1
        self.data_limits['max'][40] = 255
        self.data_limits['min'][41] = 0    # SATA1_VOLTAGE_2
        self.data_limits['max'][41] = 255
        self.data_limits['min'][42] = 0    # SATA1_CURRENT_1
        self.data_limits['max'][42] = 255
        self.data_limits['min'][43] = 0    # SATA1_CURRENT_2
        self.data_limits['max'][43] = 255
        self.data_limits['min'][44] = 0    # SATA1_POWER_1
        self.data_limits['max'][44] = 255
        self.data_limits['min'][45] = 0    # SATA1_POWER_2
        self.data_limits['max'][45] = 255
        
        # LTC4281_GPU_12V - Voltage, Current, Power limitleri (Byte 47-52)
        self.data_limits['min'][47] = 0    # GPU_12V_VOLTAGE_1
        self.data_limits['max'][47] = 255
        self.data_limits['min'][48] = 0    # GPU_12V_VOLTAGE_2
        self.data_limits['max'][48] = 255
        self.data_limits['min'][49] = 0    # GPU_12V_CURRENT_1
        self.data_limits['max'][49] = 255
        self.data_limits['min'][50] = 0    # GPU_12V_CURRENT_2
        self.data_limits['max'][50] = 255
        self.data_limits['min'][51] = 0    # GPU_12V_POWER_1
        self.data_limits['max'][51] = 255
        self.data_limits['min'][52] = 0    # GPU_12V_POWER_2
        self.data_limits['max'][52] = 255
        
        # LTC4281_GPU_3V3 - Voltage, Current, Power limitleri (Byte 54-59)
        self.data_limits['min'][54] = 0    # GPU_3V3_VOLTAGE_1
        self.data_limits['max'][54] = 255
        self.data_limits['min'][55] = 0    # GPU_3V3_VOLTAGE_2
        self.data_limits['max'][55] = 255
        self.data_limits['min'][56] = 0    # GPU_3V3_CURRENT_1
        self.data_limits['max'][56] = 255
        self.data_limits['min'][57] = 0    # GPU_3V3_CURRENT_2
        self.data_limits['max'][57] = 255
        self.data_limits['min'][58] = 0    # GPU_3V3_POWER_1
        self.data_limits['max'][58] = 255
        self.data_limits['min'][59] = 0    # GPU_3V3_POWER_2
        self.data_limits['max'][59] = 255
        
        # LTC4281_GPU_5V - Voltage, Current, Power limitleri (Byte 61-66)
        self.data_limits['min'][61] = 0    # GPU_5V_VOLTAGE_1
        self.data_limits['max'][61] = 255
        self.data_limits['min'][62] = 0    # GPU_5V_VOLTAGE_2
        self.data_limits['max'][62] = 255
        self.data_limits['min'][63] = 0    # GPU_5V_CURRENT_1
        self.data_limits['max'][63] = 255
        self.data_limits['min'][64] = 0    # GPU_5V_CURRENT_2
        self.data_limits['max'][64] = 255
        self.data_limits['min'][65] = 0    # GPU_5V_POWER_1
        self.data_limits['max'][65] = 255
        self.data_limits['min'][66] = 0    # GPU_5V_POWER_2
        self.data_limits['max'][66] = 255
        
        # INA260_PWR_BOARD - Voltage, Current, Power limitleri (Byte 67-72)
        self.data_limits['min'][67] = 0    # PWR_BOARD_VOLTAGE_1
        self.data_limits['max'][67] = 255
        self.data_limits['min'][68] = 0    # PWR_BOARD_VOLTAGE_2
        self.data_limits['max'][68] = 255
        self.data_limits['min'][69] = 0    # PWR_BOARD_CURRENT_1
        self.data_limits['max'][69] = 255
        self.data_limits['min'][70] = 0    # PWR_BOARD_CURRENT_2
        self.data_limits['max'][70] = 255
        self.data_limits['min'][71] = 0    # PWR_BOARD_POWER_1
        self.data_limits['max'][71] = 255
        self.data_limits['min'][72] = 0    # PWR_BOARD_POWER_2
        self.data_limits['max'][72] = 255
        
        # INA260_PMON - Voltage, Current, Power limitleri (Byte 73-78)
        self.data_limits['min'][73] = 0    # PMON_VOLTAGE_1
        self.data_limits['max'][73] = 255
        self.data_limits['min'][74] = 0    # PMON_VOLTAGE_2
        self.data_limits['max'][74] = 255
        self.data_limits['min'][75] = 0    # PMON_CURRENT_1
        self.data_limits['max'][75] = 255
        self.data_limits['min'][76] = 0    # PMON_CURRENT_2
        self.data_limits['max'][76] = 255
        self.data_limits['min'][77] = 0    # PMON_POWER_1
        self.data_limits['max'][77] = 255
        self.data_limits['min'][78] = 0    # PMON_POWER_2
        self.data_limits['max'][78] = 255
        
        # Temperature sensörleri (79-85) için limitler yok (her zaman yeşil, direkt değer gösterilir)
        self.temp_indices = [79, 80, 81, 82, 83, 84, 85]  # TMP100 ve GPU TEMP değerleri
        
        self.received_data = [0] * 128
        self.initUI()
        
        # Timer for periodic data reading
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_uart_data)
        
    def initUI(self):
        self.setWindowTitle('UART Monitoring Interface')
        self.setGeometry(100, 100, 1600, 900)
        
        # Ana widget ve layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Bağlantı paneli
        connection_panel = self.create_connection_panel()
        main_layout.addWidget(connection_panel)
        
        # Ana içerik: Tablo ve kontrol paneli
        content_layout = QHBoxLayout()
        
        # Tablo (3 sütunlu yapı)
        self.table_widget = self.create_data_table()
        content_layout.addWidget(self.table_widget, stretch=7)
        
        # Sağ taraf: Status göstergeleri ve kontrol paneli
        right_side_layout = QVBoxLayout()
        
        # Status göstergeleri (üst kısım)
        status_panel = self.create_status_panel()
        right_side_layout.addWidget(status_panel)
        
        # Kontrol paneli (alt kısım)
        control_panel = self.create_control_panel()
        right_side_layout.addWidget(control_panel)
        
        content_layout.addLayout(right_side_layout, stretch=3)
        
        main_layout.addLayout(content_layout)
        
    def create_connection_panel(self):
        panel = QGroupBox("Bağlantı Ayarları")
        layout = QHBoxLayout()
        
        # COM Port seçimi
        layout.addWidget(QLabel("COM Port:"))
        self.com_combo = QComboBox()
        self.refresh_com_ports()
        layout.addWidget(self.com_combo)
        
        # Baud rate seçimi
        layout.addWidget(QLabel("Baud Rate:"))
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(['9600', '19200', '38400', '57600', '115200'])
        self.baud_combo.setCurrentText('115200')
        layout.addWidget(self.baud_combo)
        
        # Yenile butonu
        refresh_btn = QPushButton("Yenile")
        refresh_btn.clicked.connect(self.refresh_com_ports)
        layout.addWidget(refresh_btn)
        
        # Bağlan butonu
        self.connect_btn = QPushButton("Bağlan")
        self.connect_btn.clicked.connect(self.toggle_connection)
        layout.addWidget(self.connect_btn)
        
        # Durum etiketi
        self.status_label = QLabel("Bağlantı Yok")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        panel.setLayout(layout)
        return panel
    
    def create_data_table(self):
        table = QTableWidget()
        
        # 128 satır, 3 ana grup için 18 sütun (3 grup x (İndeks + İsim + Min + Değer + Max + Meaning))
        rows_per_column = 43  # 128/3 ≈ 43
        table.setRowCount(rows_per_column)
        table.setColumnCount(18)
        
        headers = ['#', 'Sinyal', 'Min', 'Değer', 'Max', 'Meaning'] * 3
        table.setHorizontalHeaderLabels(headers)
        
        # Satır numaralarını gizle
        table.verticalHeader().setVisible(False)
        
        # Sütun genişlikleri
        header = table.horizontalHeader()
        for i in range(18):
            col_type = i % 6
            if col_type == 0:  # İndeks sütunu
                table.setColumnWidth(i, 40)
            elif col_type == 1:  # İsim sütunu
                table.setColumnWidth(i, 200)
            elif col_type == 2:  # Min sütunu
                table.setColumnWidth(i, 50)
            elif col_type == 3:  # Değer sütunu
                table.setColumnWidth(i, 60)
            elif col_type == 4:  # Max sütunu
                table.setColumnWidth(i, 50)
            else:  # Meaning sütunu
                table.setColumnWidth(i, 150)
        
        # Tabloyu doldur
        self.populate_table(table)
        
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        return table
    
    def populate_table(self, table):
        signal_names = self.get_signal_names()
        rows_per_column = 43
        
        for i in range(128):
            col_group = i // rows_per_column  # 0, 1, 2
            row = i % rows_per_column
            
            if col_group < 3:  # Sadece 3 sütun grubu var
                base_col = col_group * 6
                
                # İndeks
                table.setItem(row, base_col, QTableWidgetItem(str(i)))
                
                # Sinyal ismi
                table.setItem(row, base_col + 1, QTableWidgetItem(signal_names.get(i, f"DATA_{i}")))
                
                # Min değer
                min_val = self.data_limits['min'][i]
                min_item = QTableWidgetItem(str(min_val))
                if isinstance(min_val, int):
                    min_item.setText(f"0x{min_val:02X}")
                table.setItem(row, base_col + 2, min_item)
                
                # Değer - İlk renklendirmeyi yap
                value_item = QTableWidgetItem("0")
                # Temperature sensörleri yeşil
                if i in self.temp_indices:
                    value_item.setBackground(QColor(144, 238, 144))  # Açık yeşil
                # Limit belirlenmemişse kırmızı
                elif min_val == 'xx' or self.data_limits['max'][i] == 'xx':
                    value_item.setBackground(QColor(255, 182, 193))  # Açık kırmızı
                else:
                    # Başlangıç değeri 0, kontrol et
                    if min_val <= 0 <= self.data_limits['max'][i]:
                        value_item.setBackground(QColor(144, 238, 144))  # Açık yeşil
                    else:
                        value_item.setBackground(QColor(255, 182, 193))  # Açık kırmızı
                table.setItem(row, base_col + 3, value_item)
                
                # Max değer
                max_val = self.data_limits['max'][i]
                max_item = QTableWidgetItem(str(max_val))
                if isinstance(max_val, int):
                    max_item.setText(f"0x{max_val:02X}")
                table.setItem(row, base_col + 4, max_item)
                
                # Meaning - Başlangıçta XX olarak ayarla
                table.setItem(row, base_col + 5, QTableWidgetItem("XX"))
    
    def create_status_panel(self):
        panel = QGroupBox("Durum Göstergeleri")
        layout = QVBoxLayout()
        
        self.status_buttons = []
        status_labels = ["SATA0 Status", "SATA1 Status", "GPU Status"]
        
        for label in status_labels:
            btn = QPushButton(label + "\nDISABLE")
            btn.setEnabled(False)
            btn.setMinimumHeight(50)
            btn.setStyleSheet("background-color: #cc0000; color: white; font-weight: bold;")
            self.status_buttons.append(btn)
            layout.addWidget(btn)
        
        panel.setLayout(layout)
        return panel
    
    def create_control_panel(self):
        panel = QGroupBox("Kontrol Paneli")
        main_layout = QVBoxLayout()
        
        # TX Kontrol Butonları
        tx_group = QGroupBox("TX Kontrolleri")
        tx_layout = QVBoxLayout()
        
        self.tx_buttons = []
        tx_labels = ["TX1", "TX2", "TX3"]
        
        for label in tx_labels:
            btn = QPushButton(label + " Enable")
            btn.setCheckable(True)
            btn.setMinimumHeight(45)
            btn.clicked.connect(lambda checked, b=btn: self.toggle_tx_button(b, checked))
            btn.setStyleSheet("background-color: #666666;")
            self.tx_buttons.append(btn)
            tx_layout.addWidget(btn)
        
        tx_group.setLayout(tx_layout)
        main_layout.addWidget(tx_group)
        
        # SATA Kontrol Butonları
        sata_group = QGroupBox("SATA Kontrolleri")
        sata_layout = QVBoxLayout()
        
        # SATA1 butonu
        self.sata1_btn = QPushButton("SATA1 Etkinleştir")
        self.sata1_btn.setMinimumHeight(45)
        self.sata1_btn.setStyleSheet("background-color: #0066cc; color: white; font-weight: bold;")
        self.sata1_btn.clicked.connect(self.activate_sata1)
        sata_layout.addWidget(self.sata1_btn)
        
        # SATAS butonu (SATA0 + SATA1)
        self.satas_btn = QPushButton("SATAS Etkinleştir\n(SATA0 + SATA1)")
        self.satas_btn.setMinimumHeight(45)
        self.satas_btn.setStyleSheet("background-color: #cc6600; color: white; font-weight: bold;")
        self.satas_btn.clicked.connect(self.activate_satas)
        sata_layout.addWidget(self.satas_btn)
        
        sata_group.setLayout(sata_layout)
        main_layout.addWidget(sata_group)
        
        # LED Kontrol Butonları
        led_group = QGroupBox("LED Kontrolleri")
        led_layout = QVBoxLayout()
        
        self.led_buttons = []
        led_colors = [("R", "#ff0000"), ("G", "#00ff00"), ("B", "#0000ff")]
        
        for name, color in led_colors:
            btn = QPushButton(f"LED {name}")
            btn.setCheckable(True)
            btn.setMinimumHeight(45)
            btn.clicked.connect(lambda checked, b=btn, c=color: self.toggle_led_button(b, checked, c))
            btn.setStyleSheet(f"background-color: #333333; color: {color}; font-weight: bold;")
            self.led_buttons.append(btn)
            led_layout.addWidget(btn)
        
        led_group.setLayout(led_layout)
        main_layout.addWidget(led_group)
        
        main_layout.addStretch()
        panel.setLayout(main_layout)
        return panel
    
    def activate_sata1(self):
        """SATA1 aktivasyonu için onay dialogu"""
        reply = QMessageBox.question(
            self,
            'SATA1 Etkinleştirme',
            'SATA1 etkinleştirilecek. Onaylıyor musunuz?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # SATA1 etkinleştirme komutu gönder
            self.send_sata_command(sata1=True, sata0=False)
            QMessageBox.information(self, 'Bilgi', 'SATA1 etkinleştirme komutu gönderildi.')
    
    def activate_satas(self):
        """SATA0 ve SATA1 aktivasyonu için onay dialogu"""
        reply = QMessageBox.question(
            self,
            'SATAS Etkinleştirme',
            'SATA1 ve SATA0 etkinleşecek. Emin misiniz?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # SATA0 ve SATA1 etkinleştirme komutu gönder
            self.send_sata_command(sata1=True, sata0=True)
            QMessageBox.information(self, 'Bilgi', 'SATA0 ve SATA1 etkinleştirme komutu gönderildi.')
    
    def send_sata_command(self, sata1=False, sata0=False):
        """SATA etkinleştirme komutunu gönder"""
        if not self.serial_port or not self.serial_port.is_open:
            QMessageBox.warning(self, 'Uyarı', 'Seri port bağlı değil!')
            return
        
        # SATA komutu hazırla (formatınıza göre değiştirin)
        # Örnek: 0x41 0x56 [length] [command_id] [sata_mask]
        command = bytearray([0x41, 0x56, 0x05, 0x30])
        
        # SATA mask: Bit 0 = SATA0, Bit 1 = SATA1
        sata_mask = 0x00
        if sata0:
            sata_mask |= 0x01
        if sata1:
            sata_mask |= 0x02
        
        command.append(sata_mask)
        
        # Checksum hesapla
        checksum = (256 - (sum(command) % 256)) % 256
        command.append(checksum)
        
        try:
            self.serial_port.write(command)
            print(f"SATA komutu gönderildi: {' '.join([f'0x{b:02X}' for b in command])}")
        except Exception as e:
            QMessageBox.critical(self, 'Hata', f'SATA komutu gönderilemedi: {str(e)}')
    
    def refresh_com_ports(self):
        self.com_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.com_combo.addItem(f"{port.device} - {port.description}")
    
    def toggle_connection(self):
        if not self.is_connected:
            # Bağlan
            try:
                port_text = self.com_combo.currentText().split(' - ')[0]
                baud_rate = int(self.baud_combo.currentText())
                
                self.serial_port = serial.Serial(port_text, baud_rate, timeout=0.1)
                self.is_connected = True
                
                self.connect_btn.setText("Bağlantıyı Kes")
                self.status_label.setText("Bağlı")
                self.status_label.setStyleSheet("color: green; font-weight: bold;")
                
                self.timer.start(100)  # 100ms'de bir veri oku
                
            except Exception as e:
                self.status_label.setText(f"Hata: {str(e)}")
                self.status_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            # Bağlantıyı kes
            self.timer.stop()
            if self.serial_port:
                self.serial_port.close()
            
            self.is_connected = False
            self.connect_btn.setText("Bağlan")
            self.status_label.setText("Bağlantı Yok")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
    
    def read_uart_data(self):
        if not self.serial_port or not self.serial_port.is_open:
            return
        
        try:
            # UART'tan veri oku
            if self.serial_port.in_waiting > 0:
                data = self.serial_port.read(self.serial_port.in_waiting)
                
                # Paket başlangıcını ara (0x41, 0x56)
                if len(data) >= 133:  # Minimum paket boyutu
                    for i in range(len(data) - 132):
                        if data[i] == 0x41 and data[i+1] == 0x56:
                            packet = data[i:i+133]
                            if self.validate_packet(packet):
                                self.process_packet(packet)
                                break
        except Exception as e:
            print(f"Okuma hatası: {e}")
    
    def validate_packet(self, packet):
        if len(packet) != 133:
            return False
        
        # Checksum kontrolü
        checksum = sum(packet[:132]) & 0xFF
        return checksum == 0x00
    
    def process_packet(self, packet):
        # Paketten veriyi çıkar (byte 4'ten başlar)
        for i in range(128):
            if i + 4 < len(packet):
                self.received_data[i] = packet[i + 4]
        
        # Tabloyu güncelle
        self.update_table()
        
        # Status butonlarını güncelle
        self.update_status_buttons()
    
    def update_table(self):
        rows_per_column = 43
        
        for i in range(128):
            col_group = i // rows_per_column
            row = i % rows_per_column
            
            if col_group < 3:
                base_col = col_group * 6
                value = self.received_data[i]
                
                # Değeri güncelle
                item = self.table_widget.item(row, base_col + 3)
                if item:
                    item.setText(str(value))
                    
                    # Renk kontrolü
                    # Temperature sensörleri her zaman yeşil
                    if i in self.temp_indices:
                        item.setBackground(QColor(144, 238, 144))  # Açık yeşil
                    else:
                        # Min ve max değerleri kontrol et
                        min_val = self.data_limits['min'][i]
                        max_val = self.data_limits['max'][i]
                        
                        # Eğer min veya max 'xx' ise (belirlenmemişse) kırmızı yap
                        if min_val == 'xx' or max_val == 'xx':
                            item.setBackground(QColor(255, 182, 193))  # Açık kırmızı
                        # Aksi halde aralık kontrolü yap
                        elif min_val <= value <= max_val:
                            item.setBackground(QColor(144, 238, 144))  # Açık yeşil
                        else:
                            item.setBackground(QColor(255, 182, 193))  # Açık kırmızı
                
                # Meaning sütununu güncelle (gelen değere göre anlam)
                meaning_item = self.table_widget.item(row, base_col + 5)
                if meaning_item:
                    meaning_text = self.get_dynamic_meaning(i, value)
                    meaning_item.setText(meaning_text)
    
    def update_status_buttons(self):
        # Status byte'larını kontrol et (LTC4281 STATUS registerleri)
        # Byte 32: SATA0_STATUS, Byte 39: SATA1_STATUS, Byte 46: GPU_12V_STATUS
        status_indices = [32, 39, 46]  # LTC4281 status byte'ları
        
        for i, idx in enumerate(status_indices):
            if idx < len(self.received_data):
                status = self.received_data[idx]
                is_on = (status & 0x80) != 0  # Bit 7: ON_STATUS
                
                btn = self.status_buttons[i]
                if is_on:
                    btn.setText(btn.text().split('\n')[0] + "\nENABLE")
                    btn.setStyleSheet("background-color: #00cc00; color: white; font-weight: bold;")
                else:
                    btn.setText(btn.text().split('\n')[0] + "\nDISABLE")
                    btn.setStyleSheet("background-color: #cc0000; color: white; font-weight: bold;")
    
    def toggle_tx_button(self, button, checked):
        if checked:
            button.setText(button.text().replace("Enable", "Disable"))
            button.setStyleSheet("background-color: #00cc00; font-weight: bold;")
            # TX sinyali gönder
            self.send_tx_command(self.tx_buttons.index(button), True)
        else:
            button.setText(button.text().replace("Disable", "Enable"))
            button.setStyleSheet("background-color: #666666;")
            # TX sinyali gönder
            self.send_tx_command(self.tx_buttons.index(button), False)
    
    def toggle_led_button(self, button, checked, color):
        if checked:
            button.setStyleSheet(f"background-color: {color}; color: white; font-weight: bold; border: 2px solid white;")
            # LED komutunu gönder
            self.send_led_command(self.led_buttons.index(button), True)
        else:
            button.setStyleSheet(f"background-color: #333333; color: {color}; font-weight: bold;")
            # LED komutunu gönder
            self.send_led_command(self.led_buttons.index(button), False)
    
    def send_tx_command(self, index, enable):
        if not self.serial_port or not self.serial_port.is_open:
            return
        
        # TX komutu gönder (formatınıza göre değiştirin)
        command = bytearray([0x41, 0x56, 0x05, 0x10 + index, int(enable)])
        checksum = (256 - (sum(command) % 256)) % 256
        command.append(checksum)
        
        try:
            self.serial_port.write(command)
        except Exception as e:
            print(f"TX gönderme hatası: {e}")
    
    def send_led_command(self, index, enable):
        if not self.serial_port or not self.serial_port.is_open:
            return
        
        # LED komutu gönder (formatınıza göre değiştirin)
        command = bytearray([0x41, 0x56, 0x05, 0x20 + index, int(enable)])
        checksum = (256 - (sum(command) % 256)) % 256
        command.append(checksum)
        
        try:
            self.serial_port.write(command)
        except Exception as e:
            print(f"LED gönderme hatası: {e}")
    
    def get_signal_names(self):
        # Protokol dökümanından sinyal isimleri
        # Paket yapısı: HEADER_1(0x41) + HEADER_2(0x56) + LENGTH(0x85) + PACKET_ID(0x02) + DATA[128] + CHECKSUM
        # Bu fonksiyon DATA kısmındaki 128 byte'ın isimlerini içerir
        names = {
            0: "HEADER_1",
            1: "HEADER_2", 
            2: "LENGTH",
            3: "PACKET_ID",
            4: "FPGA_VERSION",           # Data byte 1
            5: "FPGA_REVISION",          # Data byte 2
            6: "I2C_ACK_STATUS_1",       # Data byte 3
            7: "I2C_ACK_STATUS_2",       # Data byte 4
            8: "I2C_ACK_STATUS_3",       # Data byte 5
            9: "I2C_ACK_STATUS_4",       # Data byte 6
            10: "I2C_ACK_STATUS_5",      # Data byte 7
            11: "UART_STATUS",           # Data byte 8
            12: "CPU_STATUS",            # Data byte 9
            13: "HSN_STATUS",            # Data byte 10
            14: "SATA_STATUS",           # Data byte 11
            15: "USB_STATUS",            # Data byte 12
            16: "JTAG_STATUS",           # Data byte 13
            17: "GPU_STATUS_1",          # Data byte 14
            18: "GPU_STATUS_2",          # Data byte 15
            19: "HDMI_STATUS",           # Data byte 16
            20: "DISC_IN_VALUES",        # Data byte 17
            21: "DISC_DISCREPANCY_CHECK", # Data byte 18
            22: "DISC_OUT_BIT_STATUS",   # Data byte 19
            23: "DISC_OUT_LB_FAIL_STATUS", # Data byte 20
            24: "DISC_OUT_FAULT_STATUS", # Data byte 21
            25: "LTC4281_PMON_STATUS",   # Data byte 22
            26: "LTC4281_PMON_VOLTAGE_1", # Data byte 23
            27: "LTC4281_PMON_VOLTAGE_2", # Data byte 24
            28: "LTC4281_PMON_CURRENT_1", # Data byte 25
            29: "LTC4281_PMON_CURRENT_2", # Data byte 26
            30: "LTC4281_PMON_POWER_1",  # Data byte 27
            31: "LTC4281_PMON_POWER_2",  # Data byte 28
            32: "LTC4281_SATA0_STATUS",  # Data byte 29
            33: "LTC4281_SATA0_VOLTAGE_1", # Data byte 30
            34: "LTC4281_SATA0_VOLTAGE_2", # Data byte 31
            35: "LTC4281_SATA0_CURRENT_1", # Data byte 32
            36: "LTC4281_SATA0_CURRENT_2", # Data byte 33
            37: "LTC4281_SATA0_POWER_1", # Data byte 34
            38: "LTC4281_SATA0_POWER_2", # Data byte 35
            39: "LTC4281_SATA1_STATUS",  # Data byte 36
            40: "LTC4281_SATA1_VOLTAGE_1", # Data byte 37
            41: "LTC4281_SATA1_VOLTAGE_2", # Data byte 38
            42: "LTC4281_SATA1_CURRENT_1", # Data byte 39
            43: "LTC4281_SATA1_CURRENT_2", # Data byte 40
            44: "LTC4281_SATA1_POWER_1", # Data byte 41
            45: "LTC4281_SATA1_POWER_2", # Data byte 42
            46: "LTC4281_GPU_12V_STATUS", # Data byte 43
            47: "LTC4281_GPU_12V_VOLTAGE_1", # Data byte 44
            48: "LTC4281_GPU_12V_VOLTAGE_2", # Data byte 45
            49: "LTC4281_GPU_12V_CURRENT_1", # Data byte 46
            50: "LTC4281_GPU_12V_CURRENT_2", # Data byte 47
            51: "LTC4281_GPU_12V_POWER_1", # Data byte 48
            52: "LTC4281_GPU_12V_POWER_2", # Data byte 49
            53: "LTC4281_GPU_3V3_STATUS", # Data byte 50
            54: "LTC4281_GPU_3V3_VOLTAGE_1", # Data byte 51
            55: "LTC4281_GPU_3V3_VOLTAGE_2", # Data byte 52
            56: "LTC4281_GPU_3V3_CURRENT_1", # Data byte 53
            57: "LTC4281_GPU_3V3_CURRENT_2", # Data byte 54
            58: "LTC4281_GPU_3V3_POWER_1", # Data byte 55
            59: "LTC4281_GPU_3V3_POWER_2", # Data byte 56
            60: "LTC4281_GPU_5V_STATUS",  # Data byte 57
            61: "LTC4281_GPU_5V_VOLTAGE_1", # Data byte 58
            62: "LTC4281_GPU_5V_VOLTAGE_2", # Data byte 59
            63: "LTC4281_GPU_5V_CURRENT_1", # Data byte 60
            64: "LTC4281_GPU_5V_CURRENT_2", # Data byte 61
            65: "LTC4281_GPU_5V_POWER_1", # Data byte 62
            66: "LTC4281_GPU_5V_POWER_2", # Data byte 63
            67: "INA260_PWR_BOARD_VOLTAGE_1", # Data byte 64
            68: "INA260_PWR_BOARD_VOLTAGE_2", # Data byte 65
            69: "INA260_PWR_BOARD_CURRENT_1", # Data byte 66
            70: "INA260_PWR_BOARD_CURRENT_2", # Data byte 67
            71: "INA260_PWR_BOARD_POWER_1", # Data byte 68
            72: "INA260_PWR_BOARD_POWER_2", # Data byte 69
            73: "INA260_PMON_VOLTAGE_1", # Data byte 70
            74: "INA260_PMON_VOLTAGE_2", # Data byte 71
            75: "INA260_PMON_CURRENT_1", # Data byte 72
            76: "INA260_PMON_CURRENT_2", # Data byte 73
            77: "INA260_PMON_POWER_1",   # Data byte 74
            78: "INA260_PMON_POWER_2",   # Data byte 75
            79: "TMP100_CPLD_TEMP",      # Data byte 76
            80: "TMP100_GPU_TEMP",       # Data byte 77
            81: "TMP100_CARRIER_TEMP",   # Data byte 78
            82: "TMP100_PWR_REG_TEMP",   # Data byte 79
            83: "TMP100_PWR_BOARD_TEMP", # Data byte 80
            84: "TMP100_IGLOO2_TEMP",    # Data byte 81
            85: "GPU_TEMP",              # Data byte 82
            86: "HSN_TRANS_DATA_1",      # Data byte 83
            87: "HSN_TRANS_DATA_2",      # Data byte 84
            88: "HSN_TRANS_DATA_3",      # Data byte 85
            89: "HSN_TRANS_DATA_4",      # Data byte 86
            90: "HSN_TRANS_DATA_5",      # Data byte 87
            91: "HSN_TRANS_DATA_6",      # Data byte 88
            92: "HSN_TRANS_DATA_7",      # Data byte 89
            93: "HSN_TRANS_DATA_8",      # Data byte 90
            94: "RESERVED",              # Data byte 91
            95: "RESERVED",              # Data byte 92
            96: "RESERVED",              # Data byte 93
            97: "RESERVED",              # Data byte 94
            98: "RESERVED",              # Data byte 95
            99: "RESERVED",              # Data byte 96
            100: "RESERVED",             # Data byte 97
            101: "RESERVED",             # Data byte 98
            102: "RESERVED",             # Data byte 99
            103: "RESERVED",             # Data byte 100
            104: "RESERVED",             # Data byte 101
            105: "RESERVED",             # Data byte 102
            106: "RESERVED",             # Data byte 103
            107: "RESERVED",             # Data byte 104
            108: "RESERVED",             # Data byte 105
            109: "RESERVED",             # Data byte 106
            110: "RESERVED",             # Data byte 107
            111: "RESERVED",             # Data byte 108
            112: "RESERVED",             # Data byte 109
            113: "RESERVED",             # Data byte 110
            114: "RESERVED",             # Data byte 111
            115: "RESERVED",             # Data byte 112
            116: "RESERVED",             # Data byte 113
            117: "RESERVED",             # Data byte 114
            118: "RESERVED",             # Data byte 115
            119: "RESERVED",             # Data byte 116
            120: "RESERVED",             # Data byte 117
            121: "RESERVED",             # Data byte 118
            122: "RESERVED",             # Data byte 119
            123: "RESERVED",             # Data byte 120
            124: "RESERVED",             # Data byte 121
            125: "UART_LOOPBACK",        # Data byte 122
            126: "UART_LOOPBACK",        # Data byte 123
            127: "UART_LOOPBACK",        # Data byte 124
            128: "UART_LOOPBACK",        # Data byte 125
            # Data byte 126, 127, 128 (index 129, 130, 131) = UART_LOOPBACK devam
            # CHECKSUM pakette var ama tabloda gösterilmez
        }
        return names
    
    def get_signal_meanings(self):
        # Her sinyalin anlamı/açıklaması
        meanings = {
            0: "Protocol Marker 1 (0x41)",
            1: "Protocol Marker 2 (0x56)",
            2: "Packet Length (133 bytes)",
            3: "Identifier Info",
            4: "FPGA Version Info",
            5: "FPGA Revision Info",
            6: "I2C ACK: SATA1 & SATA0 Sensors",
            7: "I2C ACK: GPU_12V & PMON Sensors",
            8: "I2C ACK: GPU_3V3 & GPU_5V Sensors",
            9: "I2C ACK: VID, HSN, INA260 Sensors",
            10: "I2C ACK: Temperature Sensors",
            11: "UART RX Timeout Status",
            12: "CPU 12V Switch Alert",
            13: "HSN Transceiver Interrupt",
            14: "SATA Card Status & Presence",
            15: "USB Switch Fault Status",
            16: "JTAG Power Good Status",
            17: "GPU Card Alerts & Presence",
            18: "GPU PCIe Clock Request",
            19: "HDMI Over Current Status",
            20: "Discrete Input Values",
            21: "Discrete Input Discrepancy",
            22: "Discrete Output Bit Status",
            23: "Discrete Loopback Fail Status",
            24: "Discrete Output Fault Status",
            25: "PMON Power Switch Status",
            26: "PMON Voltage MSB",
            27: "PMON Voltage LSB",
            28: "PMON Current MSB",
            29: "PMON Current LSB",
            30: "PMON Power MSB",
            31: "PMON Power LSB",
            32: "SATA0 Power Switch Status",
            33: "SATA0 Voltage MSB",
            34: "SATA0 Voltage LSB",
            35: "SATA0 Current MSB",
            36: "SATA0 Current LSB",
            37: "SATA0 Power MSB",
            38: "SATA0 Power LSB",
            39: "SATA1 Power Switch Status",
            40: "SATA1 Voltage MSB",
            41: "SATA1 Voltage LSB",
            42: "SATA1 Current MSB",
            43: "SATA1 Current LSB",
            44: "SATA1 Power MSB",
            45: "SATA1 Power LSB",
            46: "GPU 12V Power Switch Status",
            47: "GPU 12V Voltage MSB",
            48: "GPU 12V Voltage LSB",
            49: "GPU 12V Current MSB",
            50: "GPU 12V Current LSB",
            51: "GPU 12V Power MSB",
            52: "GPU 12V Power LSB",
            53: "GPU 3.3V Power Switch Status",
            54: "GPU 3.3V Voltage MSB",
            55: "GPU 3.3V Voltage LSB",
            56: "GPU 3.3V Current MSB",
            57: "GPU 3.3V Current LSB",
            58: "GPU 3.3V Power MSB",
            59: "GPU 3.3V Power LSB",
            60: "GPU 5V Power Switch Status",
            61: "GPU 5V Voltage MSB",
            62: "GPU 5V Voltage LSB",
            63: "GPU 5V Current MSB",
            64: "GPU 5V Current LSB",
            65: "GPU 5V Power MSB",
            66: "GPU 5V Power LSB",
            67: "Power Board Voltage MSB",
            68: "Power Board Voltage LSB",
            69: "Power Board Current MSB",
            70: "Power Board Current LSB",
            71: "Power Board Power MSB",
            72: "Power Board Power LSB",
            73: "PMON INA260 Voltage MSB",
            74: "PMON INA260 Voltage LSB",
            75: "PMON INA260 Current MSB",
            76: "PMON INA260 Current LSB",
            77: "PMON INA260 Power MSB",
            78: "PMON INA260 Power LSB",
            79: "CPLD Temperature (°C)",
            80: "GPU Temperature (°C)",
            81: "Carrier Board Temperature (°C)",
            82: "Power Regulator Temperature (°C)",
            83: "Power Board Temperature (°C)",
            84: "IGLOO2 FPGA Temperature (°C)",
            85: "GPU Sensor Temperature (°C)",
            86: "HSN Transceiver Data 1",
            87: "HSN Transceiver Data 2",
            88: "HSN Transceiver Data 3",
            89: "HSN Transceiver Data 4",
            90: "HSN Transceiver Data 5",
            91: "HSN Transceiver Data 6",
            92: "HSN Transceiver Data 7",
            93: "HSN Transceiver Data 8",
        }
        
        # Reserved ve UART Loopback için
        for i in range(94, 125):
            meanings[i] = "Reserved"
        
        for i in range(125, 129):
            meanings[i] = "UART Loopback Data"
        
        return meanings

def main():
    app = QApplication(sys.argv)
    window = UARTMonitor()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()