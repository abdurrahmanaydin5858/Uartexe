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
        
        # Veri limitleri - Burada her sinyal için min/max değerleri belirleyin
        self.data_limits = {
            'min': ['xx'] * 128,  # Minimum değerler
            'max': ['xx'] * 128   # Maximum değerler
        }
        
        # Örnek: Bazı sinyaller için limit değerleri
        # self.data_limits['min'][22] = 10
        # self.data_limits['max'][22] = 250
        # self.data_limits['min'][23] = 0
        # self.data_limits['max'][23] = 255
        
        # Temperature sensörleri (76-81) için limitler belirlenmeyecek (her zaman yeşil)
        self.temp_indices = [76, 77, 78, 79, 80, 81, 82]  # TEMP değerleri
        
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
        
        # 128 satır, 3 ana grup için 15 sütun (3 grup x (İndeks + İsim + Min + Değer + Max))
        rows_per_column = 43  # 128/3 ≈ 43
        table.setRowCount(rows_per_column)
        table.setColumnCount(15)
        
        headers = ['#', 'Sinyal', 'Min', 'Değer', 'Max'] * 3
        table.setHorizontalHeaderLabels(headers)
        
        # Sütun genişlikleri
        header = table.horizontalHeader()
        for i in range(15):
            col_type = i % 5
            if col_type == 0:  # İndeks sütunu
                table.setColumnWidth(i, 40)
            elif col_type == 1:  # İsim sütunu
                header.setSectionResizeMode(i, QHeaderView.Stretch)
            elif col_type == 2:  # Min sütunu
                table.setColumnWidth(i, 50)
            elif col_type == 3:  # Değer sütunu
                table.setColumnWidth(i, 60)
            else:  # Max sütunu
                table.setColumnWidth(i, 50)
        
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
                base_col = col_group * 5
                
                # İndeks
                table.setItem(row, base_col, QTableWidgetItem(str(i)))
                
                # Sinyal ismi
                table.setItem(row, base_col + 1, QTableWidgetItem(signal_names.get(i, f"DATA_{i}")))
                
                # Min değer
                min_val = self.data_limits['min'][i]
                table.setItem(row, base_col + 2, QTableWidgetItem(str(min_val)))
                
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
                table.setItem(row, base_col + 4, QTableWidgetItem(str(max_val)))
    
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
                base_col = col_group * 5
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
    
    def update_status_buttons(self):
        # Örnek: byte 22, 29, 43'teki ON_STATUS bitini kontrol et
        status_indices = [29, 36, 43]  # SATA0, SATA1, GPU_12V status byte'ları
        
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
        names = {
            0: "HEADER_1",
            1: "HEADER_2",
            2: "LENGTH",
            3: "PACKET_ID",
            4: "FPGA_VERSION",
            5: "FPGA_REVISION",
            6: "I2C_ACK_1",
            7: "I2C_ACK_2",
            8: "I2C_ACK_3",
            9: "I2C_ACK_4",
            10: "I2C_ACK_5",
            11: "UART_STATUS",
            12: "CPU_STATUS",
            13: "HSN_STATUS",
            14: "SATA_STATUS",
            15: "USB_STATUS",
            16: "JTAG_STATUS",
            17: "GPU_STATUS_1",
            18: "GPU_STATUS_2",
            19: "HDMI_STATUS",
            20: "DISC_IN_VAL",
            21: "DISC_DISC_CHK",
            22: "PMON_STATUS",
            23: "PMON_VOLT_H",
            24: "PMON_VOLT_L",
            25: "PMON_CUR_H",
            26: "PMON_CUR_L",
            27: "PMON_POW_H",
            28: "PMON_POW_L",
            29: "SATA0_STATUS",
            30: "SATA0_VOLT_H",
            76: "CPLD_TEMP",
            77: "GPU_TEMP",
            78: "CARRIER_TEMP",
            79: "PWR_REG_TEMP",
            80: "PWR_BRD_TEMP",
            81: "IGLOO2_TEMP",
            82: "GPU_TEMP_2",
        }
        return names

def main():
    app = QApplication(sys.argv)
    window = UARTMonitor()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()