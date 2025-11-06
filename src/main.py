import sys
import os
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QVBoxLayout, 
                             QHBoxLayout, QWidget, QPushButton, QComboBox, 
                             QLabel, QFileDialog, QTextEdit, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class DataVisualizationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.df = None
        self.db_connection = None
        self.current_table = None
        self.log_actions = []
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Анализ и визуализация данных')
        self.setGeometry(100, 100, 1200, 800)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QVBoxLayout(central_widget)
        
        # Заголовок
        title_label = QLabel('Система анализа и визуализации данных')
        title_label.setFont(QFont('Arial', 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Кнопка загрузки данных
        load_layout = QHBoxLayout()
        self.load_btn = QPushButton('Загрузить CSV файл')
        self.load_btn.clicked.connect(self.load_csv)
        self.load_db_btn = QPushButton('Подключиться к БД')
        self.load_db_btn.clicked.connect(self.connect_to_db)
        
        load_layout.addWidget(self.load_btn)
        load_layout.addWidget(self.load_db_btn)
        load_layout.addStretch()
        
        main_layout.addLayout(load_layout)
        
        # Вкладки
        self.tabs = QTabWidget()
        
        # Вкладка 1: Статистика
        self.tab1 = QWidget()
        self.setup_tab1()
        self.tabs.addTab(self.tab1, "Статистика")
        
        # Вкладка 2: Графики корреляции
        self.tab2 = QWidget()
        self.setup_tab2()
        self.tabs.addTab(self.tab2, "Корреляции")
        
        # Вкладка 3: Тепловая карта
        self.tab3 = QWidget()
        self.setup_tab3()
        self.tabs.addTab(self.tab3, "Тепловая карта")
        
        # Вкладка 4: Линейные графики
        self.tab4 = QWidget()
        self.setup_tab4()
        self.tabs.addTab(self.tab4, "Линейные графики")
        
        # Вкладка 5: Лог действий
        self.tab5 = QWidget()
        self.setup_tab5()
        self.tabs.addTab(self.tab5, "Лог действий")
        
        main_layout.addWidget(self.tabs)
        
        self.add_log("Приложение запущено")
        
    def setup_tab1(self):
        layout = QVBoxLayout()
        
        # Выбор таблицы
        table_layout = QHBoxLayout()
        table_layout.addWidget(QLabel("Выберите таблицу:"))
        self.table_combo = QComboBox()
        self.table_combo.currentTextChanged.connect(self.load_table_data)
        table_layout.addWidget(self.table_combo)
        table_layout.addStretch()
        
        layout.addLayout(table_layout)
        
        # Таблица для отображения данных
        self.data_table = QTableWidget()
        layout.addWidget(self.data_table)
        
        # Статистика
        stats_layout = QVBoxLayout()
        stats_layout.addWidget(QLabel("Статистика:"))
        self.stats_text = QTextEdit()
        self.stats_text.setMaximumHeight(200)
        stats_layout.addWidget(self.stats_text)
        
        layout.addLayout(stats_layout)
        self.tab1.setLayout(layout)
        
    def setup_tab2(self):
        layout = QVBoxLayout()
        
        # Кнопка построения корреляции
        self.corr_btn = QPushButton('Построить графики корреляции')
        self.corr_btn.clicked.connect(self.plot_correlation)
        layout.addWidget(self.corr_btn)
        
        # Область для графика
        self.corr_canvas = FigureCanvas(Figure(figsize=(10, 8)))
        layout.addWidget(self.corr_canvas)
        
        self.tab2.setLayout(layout)
        
    def setup_tab3(self):
        layout = QVBoxLayout()
        
        # Кнопка построения тепловой карты
        self.heatmap_btn = QPushButton('Построить тепловую карту корреляций')
        self.heatmap_btn.clicked.connect(self.plot_heatmap)
        layout.addWidget(self.heatmap_btn)
        
        # Область для тепловой карты
        self.heatmap_canvas = FigureCanvas(Figure(figsize=(10, 8)))
        layout.addWidget(self.heatmap_canvas)
        
        self.tab3.setLayout(layout)
        
    def setup_tab4(self):
        layout = QVBoxLayout()
        
        # Выбор столбца для графика
        column_layout = QHBoxLayout()
        column_layout.addWidget(QLabel("Выберите столбец:"))
        self.column_combo = QComboBox()
        column_layout.addWidget(self.column_combo)
        
        self.plot_btn = QPushButton('Построить линейный график')
        self.plot_btn.clicked.connect(self.plot_line_chart)
        column_layout.addWidget(self.plot_btn)
        column_layout.addStretch()
        
        layout.addLayout(column_layout)
        
        # Область для графика
        self.line_canvas = FigureCanvas(Figure(figsize=(10, 6)))
        layout.addWidget(self.line_canvas)
        
        self.tab4.setLayout(layout)
        
    def setup_tab5(self):
        layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        self.tab5.setLayout(layout)
        
    def add_log(self, action):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {action}"
        self.log_actions.append(log_entry)
        self.log_text.setText("\n".join(self.log_actions))
        
    def load_csv(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "Выберите CSV файл", "", "CSV Files (*.csv)")
            if file_path:
                self.df = pd.read_csv(file_path)
                self.current_table = "CSV Data"
                self.update_ui_after_data_load()
                self.add_log(f"Загружен CSV файл: {os.path.basename(file_path)}")
                QMessageBox.information(self, "Успех", f"Данные загружены успешно!\nРазмер: {self.df.shape}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки CSV: {str(e)}")
            
    def connect_to_db(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл БД", "", "SQLite Files (*.db *.sqlite)")
            if file_path:
                self.db_connection = sqlite3.connect(file_path)
                self.update_table_list()
                self.add_log(f"Подключено к БД: {os.path.basename(file_path)}")
                QMessageBox.information(self, "Успех", "Подключение к БД установлено!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка подключения к БД: {str(e)}")
            
    def update_table_list(self):
        if self.db_connection:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            self.table_combo.clear()
            for table in tables:
                self.table_combo.addItem(table[0])
                
    def load_table_data(self, table_name):
        if not table_name:
            return
            
        try:
            if self.db_connection:
                query = f"SELECT * FROM {table_name} LIMIT 1000"
                self.df = pd.read_sql_query(query, self.db_connection)
                self.current_table = table_name
                self.update_ui_after_data_load()
                self.add_log(f"Загружена таблица: {table_name}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки таблицы: {str(e)}")
            
    def update_ui_after_data_load(self):
        if self.df is not None:
            # Обновление таблицы
            self.update_data_table()
            
            # Обновление статистики
            self.update_statistics()
            
            # Обновление выпадающих списков
            self.update_column_combos()
            
    def update_data_table(self):
        self.data_table.setRowCount(min(100, len(self.df)))
        self.data_table.setColumnCount(len(self.df.columns))
        self.data_table.setHorizontalHeaderLabels(self.df.columns)
        
        for i in range(min(100, len(self.df))):
            for j in range(len(self.df.columns)):
                item = QTableWidgetItem(str(self.df.iloc[i, j]))
                self.data_table.setItem(i, j, item)
                
    def update_statistics(self):
        stats = []
        stats.append(f"Размер данных: {self.df.shape[0]} строк, {self.df.shape[1]} столбцов")
        stats.append("\nТипы данных:")
        stats.append(str(self.df.dtypes))
        stats.append("\nБазовая статистика:")
        stats.append(str(self.df.describe()))
        stats.append("\nПропущенные значения:")
        stats.append(str(self.df.isnull().sum()))
        
        self.stats_text.setText("\n".join(stats))
        
    def update_column_combos(self):
        numeric_columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
        self.column_combo.clear()
        for column in numeric_columns:
            self.column_combo.addItem(column)
            
    def plot_correlation(self):
        if self.df is None:
            QMessageBox.warning(self, "Предупреждение", "Сначала загрузите данные!")
            return
            
        numeric_df = self.df.select_dtypes(include=[np.number])
        if numeric_df.empty:
            QMessageBox.warning(self, "Предупреждение", "Нет числовых столбцов для анализа!")
            return
            
        try:
            # Очистка предыдущего графика
            self.corr_canvas.figure.clear()
            
            # Создание subplots для парных графиков
            g = sns.pairplot(numeric_df)
            g.fig.set_size_inches(12, 10)
            
            # Сохранение в canvas
            self.corr_canvas.figure = g.fig
            self.corr_canvas.draw()
            
            self.add_log("Построены графики корреляции")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка построения графиков: {str(e)}")
            
    def plot_heatmap(self):
        if self.df is None:
            QMessageBox.warning(self, "Предупреждение", "Сначала загрузите данные!")
            return
            
        numeric_df = self.df.select_dtypes(include=[np.number])
        if numeric_df.empty:
            QMessageBox.warning(self, "Предупреждение", "Нет числовых столбцов для анализа!")
            return
            
        try:
            # Очистка предыдущего графика
            self.heatmap_canvas.figure.clear()
            ax = self.heatmap_canvas.figure.add_subplot(111)
            
            # Расчет корреляционной матрицы
            corr_matrix = numeric_df.corr()
            
            # Построение тепловой карты
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, ax=ax)
            ax.set_title('Тепловая карта корреляций')
            
            self.heatmap_canvas.draw()
            self.add_log("Построена тепловая карта корреляций")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка построения тепловой карты: {str(e)}")
            
    def plot_line_chart(self):
        if self.df is None:
            QMessageBox.warning(self, "Предупреждение", "Сначала загрузите данные!")
            return
            
        selected_column = self.column_combo.currentText()
        if not selected_column:
            QMessageBox.warning(self, "Предупреждение", "Выберите столбец для построения графика!")
            return
            
        try:
            # Очистка предыдущего графика
            self.line_canvas.figure.clear()
            ax = self.line_canvas.figure.add_subplot(111)
            
            # Построение линейного графика
            data = self.df[selected_column].dropna()
            ax.plot(data.values, linewidth=1)
            ax.set_title(f'Линейный график: {selected_column}')
            ax.set_ylabel(selected_column)
            ax.set_xlabel('Индекс')
            ax.grid(True, alpha=0.3)
            
            self.line_canvas.draw()
            self.add_log(f"Построен линейный график для столбца: {selected_column}")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка построения графика: {str(e)}")

def main():
    app = QApplication(sys.argv)
    
    # Установка стиля
    app.setStyle('Fusion')
    
    window = DataVisualizationApp()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()