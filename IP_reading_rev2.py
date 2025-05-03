import sys
import os
import pandas as pd
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar, QTabWidget
from ftplib import FTP


class SimpleVisualizationTool(QWidget):
    def __init__(self):
        super().__init__()
        self.xml_file_path = "config.xml"  # XML 파일 이름
        self.initUI()
        self.load_and_visualize_data()

    def initUI(self):
        self.layout = QVBoxLayout()

        # 탭 위젯 추가
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # 첫 번째 탭 (기존 데이터)
        self.tab1 = QWidget()
        self.tab1_layout = QVBoxLayout(self.tab1)
        self.table1 = QTableWidget(self.tab1)
        self.tab1_layout.addWidget(self.table1)
        self.tabs.addTab(self.tab1, "용량 데이터 시각화")
        self.table1.horizontalHeader().sectionClicked.connect(lambda index: self.handle_header_click(self.table1, index))


        # 두 번째 탭 (IP 주소 및 컴퓨터명 데이터)
        self.tab2 = QWidget()
        self.tab2_layout = QVBoxLayout(self.tab2)
        self.table2 = QTableWidget(self.tab2)
        self.tab2_layout.addWidget(self.table2)
        self.tabs.addTab(self.tab2, "IP 주소 데이터 시각화")
        self.table2.horizontalHeader().sectionClicked.connect(lambda index: self.handle_header_click(self.table2, index))

        # Tab3 (SMB Drive 정보 탭)
        self.tab3 = QWidget()
        self.tab3_layout = QVBoxLayout(self.tab3)
        self.table3 = QTableWidget(self.tab3)
        self.tab3_layout.addWidget(self.table3)
        self.tabs.addTab(self.tab3, "MAC Drive 용량 시각화")
        self.table3.horizontalHeader().sectionClicked.connect(lambda index: self.handle_header_click(self.table3, index))


        self.setLayout(self.layout)

        # 창 크기 조정
        self.resize(1200, 600)
        self.setWindowTitle('Simple Data Visualization Tool')
        self.show()

    def read_config_from_xml(self):
        try:
            base_path = os.path.dirname(os.path.abspath(sys.executable))
            xml_file_path = os.path.join(base_path, self.xml_file_path)

            tree = ET.parse(xml_file_path)
            root = tree.getroot()

            ftp_server = root.find('FTPServer').text
            username = root.find('Username').text
            password = root.find('Password').text
            remote_file1 = root.find('RemoteFilePath1').text  # 첫 번째 경로
            local_file1 = root.find('LocalFilePath1').text
            remote_file2 = root.find('RemoteFilePath2').text  # 두 번째 경로
            local_file2 = root.find('LocalFilePath2').text
            remote_file3 = root.find('RemoteFilePath3').text  # 두 번째 경로
            local_file3 = root.find('LocalFilePath3').text

            return ftp_server, username, password, remote_file1, local_file1, remote_file2, local_file2, remote_file3, local_file3
        except Exception as e:
            print(f"Error reading XML file: {e}")
            return None, None, None, None, None, None, None, None, None

    def download_file_from_ftp(self, server, username, password, remote_path, local_path):
        try:
            ftp = FTP(server)
            ftp.login(user=username, passwd=password)

            with open(local_path, 'wb') as file:
                ftp.retrbinary(f'RETR {remote_path}', file.write)

            ftp.quit()
        except Exception as e:
            print(f"Error downloading file from FTP: {e}")

    def load_and_visualize_data(self):
        ftp_server, username, password, remote_file1, local_file1, remote_file2, local_file2, remote_file3, local_file3 = self.read_config_from_xml()

        if ftp_server is None:
            return

        # 첫 번째 파일 다운로드 및 시각화
        self.download_file_from_ftp(ftp_server, username, password, remote_file1, local_file1)
        if os.path.isfile(local_file1):
            self.visualize_data1(local_file1)

        # 두 번째 파일 다운로드 및 시각화
        self.download_file_from_ftp(ftp_server, username, password, remote_file2, local_file2)
        if os.path.isfile(local_file2):
            self.visualize_data2(local_file2)

        # 세 번째 파일 다운로드 및 시각화
        self.download_file_from_ftp(ftp_server, username, password, remote_file3, local_file3)
        if os.path.isfile(local_file3):
            self.visualize_data1(local_file3)

    def visualize_data1(self, file_path):
        df = pd.read_csv(file_path)

        df['드라이브 용량 (GB)'] = df['드라이브 용량 (GB)'].apply(lambda x: f"{x:.2f}")
        df['사용한 용량 (GB)'] = df['사용한 용량 (GB)'].apply(lambda x: f"{x:.2f}")
        df['남은 용량 (GB)'] = df['남은 용량 (GB)'].apply(lambda x: f"{x:.2f}")
        df['수집 시간'] = pd.to_datetime(df['수집 시간']).apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))

        self.table1.setRowCount(len(df))
        self.table1.setColumnCount(len(df.columns) + 1)  # 추가 열 (비율) 포함

        headers = list(df.columns) + ['비율']
        self.table1.setHorizontalHeaderLabels(headers)

        for row in range(len(df)):
            for col in range(len(df.columns)):
                self.table1.setItem(row, col, QTableWidgetItem(str(df.iat[row, col])))

            usage_ratio = int(df['사용 비율 (%)'][row])
            progress_bar = QProgressBar(self)
            progress_bar.setValue(usage_ratio)
            self.table1.setCellWidget(row, len(df.columns), progress_bar)

        self.table1.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def visualize_data2(self, file_path):
        df = pd.read_csv(file_path)

        self.table2.setRowCount(len(df))
        self.table2.setColumnCount(3)  # 컴퓨터 명, IP 주소, 수집 시간

        headers = ['컴퓨터 명', 'IP 주소', '수집 시간']
        self.table2.setHorizontalHeaderLabels(headers)

        for row in range(len(df)):
            self.table2.setItem(row, 0, QTableWidgetItem(df.iat[row, 0]))  # 컴퓨터 명
            self.table2.setItem(row, 1, QTableWidgetItem(df.iat[row, 1]))  # IP 주소
            self.table2.setItem(row, 2, QTableWidgetItem(df.iat[row, 2]))  # 수집 시간

        self.table2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def visualize_data3(self, file_path):
        df = pd.read_csv(file_path)

        df['드라이브 용량 (GB)'] = df['드라이브 용량 (GB)'].apply(lambda x: f"{x:.2f}")
        df['사용한 용량 (GB)'] = df['사용한 용량 (GB)'].apply(lambda x: f"{x:.2f}")
        df['남은 용량 (GB)'] = df['남은 용량 (GB)'].apply(lambda x: f"{x:.2f}")
        df['수집 시간'] = pd.to_datetime(df['수집 시간']).apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))

        self.table3.setRowCount(len(df))
        self.table3.setColumnCount(len(df.columns) + 1)  # 추가 열 (비율) 포함

        headers = list(df.columns) + ['비율']
        self.table3.setHorizontalHeaderLabels(headers)

        for row in range(len(df)):
            for col in range(len(df.columns)):
                self.table3.setItem(row, col, QTableWidgetItem(str(df.iat[row, col])))

            usage_ratio = int(df['사용 비율 (%)'][row])
            progress_bar = QProgressBar(self)
            progress_bar.setValue(usage_ratio)
            self.table3.setCellWidget(row, len(df.columns), progress_bar)

        self.table3.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


    def handle_header_click(self, table, index):
        # 오름차순/내림차순 정렬
        order = table.horizontalHeader().sortIndicatorOrder()
        table.sortItems(index, order)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SimpleVisualizationTool()
    sys.exit(app.exec_())