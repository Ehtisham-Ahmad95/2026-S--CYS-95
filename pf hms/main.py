#!/usr/bin/env python3
"""
MEDICAL MANAGEMENT SYSTEM - Complete Application in ONE File
With Doctor Management and Disease Tracking
Run: python main.py
"""

import sys
import sqlite3
import hashlib
import shutil
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDialog, QMessageBox, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSpinBox,
    QComboBox, QDateTimeEdit, QDoubleSpinBox, QCheckBox, QTextEdit,
    QWidget, QStackedWidget, QTableWidget, QGroupBox, QGridLayout,
    QHeaderView, QTabWidget, QStatusBar
)
from PyQt5.QtCore import QDateTime, Qt

# DATABASE
DB_FILE = "medical_system.db"

class Database:
    def __init__(self):
        self.conn = None
        self.init_db()

    def init_db(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'staff',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            age INTEGER,
            gender TEXT,
            address TEXT,
            medical_history TEXT,
            disease TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Add disease column if it doesn't exist (for existing databases)
        try:
            cursor.execute('ALTER TABLE patients ADD COLUMN disease TEXT')
            self.conn.commit()
        except sqlite3.OperationalError:
            # Column already exists
            pass

        cursor.execute('''CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialty TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor TEXT,
            appointment_date DATETIME,
            status TEXT DEFAULT 'scheduled',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS billing (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            amount REAL,
            description TEXT,
            bill_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            paid BOOLEAN DEFAULT 0,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS symptoms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            symptoms TEXT,
            recommendation TEXT,
            analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )''')

        self.conn.commit()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def add_user(self, username, email, password, role='staff'):
        try:
            cursor = self.conn.cursor()
            cursor.execute('INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)',
                          (username, email, self.hash_password(password), role))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def authenticate_user(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                      (username, self.hash_password(password)))
        return cursor.fetchone()

    def get_all_users(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, username, email, role FROM users')
        return cursor.fetchall()

    def add_patient(self, name, email, phone, age, gender='', address='', medical_history='', disease=''):
        try:
            cursor = self.conn.cursor()
            cursor.execute('INSERT INTO patients (name, email, phone, age, gender, address, medical_history, disease) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                          (name, email, phone, age, gender, address, medical_history, disease))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def get_all_patients(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute('SELECT * FROM patients ORDER BY id DESC')
            return cursor.fetchall()
        except sqlite3.OperationalError:
            # Fallback if disease column doesn't exist
            cursor.execute('SELECT id, name, email, phone, age, gender, address, medical_history, created_at FROM patients ORDER BY id DESC')
            return cursor.fetchall()

    def search_patients(self, keyword):
        cursor = self.conn.cursor()
        try:
            cursor.execute('SELECT * FROM patients WHERE name LIKE ? OR email LIKE ? OR phone LIKE ?',
                          (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
        except sqlite3.OperationalError:
            # Fallback if disease column doesn't exist
            cursor.execute('SELECT id, name, email, phone, age, gender, address, medical_history, created_at FROM patients WHERE name LIKE ? OR email LIKE ? OR phone LIKE ?',
                          (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
        return cursor.fetchall()

    def delete_patient(self, patient_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM patients WHERE id = ?', (patient_id,))
        self.conn.commit()

    # Doctor Management Functions
    def add_doctor(self, name, specialty, phone='', email=''):
        try:
            cursor = self.conn.cursor()
            cursor.execute('INSERT INTO doctors (name, specialty, phone, email) VALUES (?, ?, ?, ?)',
                          (name, specialty, phone, email))
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error adding doctor: {e}")
            return None

    def get_all_doctors(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM doctors ORDER BY specialty, name')
        return cursor.fetchall()

    def get_doctors_by_specialty(self, specialty):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM doctors WHERE specialty LIKE ?', (f'%{specialty}%',))
        return cursor.fetchall()

    def delete_doctor(self, doctor_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM doctors WHERE id = ?', (doctor_id,))
        self.conn.commit()

    def add_appointment(self, patient_id, doctor, appointment_date, notes=''):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO appointments (patient_id, doctor, appointment_date, notes) VALUES (?, ?, ?, ?)',
                      (patient_id, doctor, appointment_date, notes))
        self.conn.commit()
        return cursor.lastrowid

    def get_all_appointments(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT a.*, p.name as patient_name FROM appointments a JOIN patients p ON a.patient_id = p.id ORDER BY a.appointment_date DESC')
        return cursor.fetchall()

    def get_today_appointments(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT a.*, p.name as patient_name FROM appointments a JOIN patients p ON a.patient_id = p.id WHERE DATE(a.appointment_date) = DATE("now") ORDER BY a.appointment_date')
        return cursor.fetchall()

    def update_appointment_status(self, appointment_id, status):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE appointments SET status = ? WHERE id = ?', (status, appointment_id))
        self.conn.commit()

    def add_bill(self, patient_id, amount, description):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO billing (patient_id, amount, description) VALUES (?, ?, ?)',
                      (patient_id, amount, description))
        self.conn.commit()
        return cursor.lastrowid

    def get_all_bills(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT b.*, p.name as patient_name FROM billing b JOIN patients p ON b.patient_id = p.id ORDER BY b.bill_date DESC')
        return cursor.fetchall()

    def mark_bill_paid(self, bill_id):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE billing SET paid = 1 WHERE id = ?', (bill_id,))
        self.conn.commit()

    def search_bills(self, keyword):
        cursor = self.conn.cursor()
        cursor.execute('SELECT b.*, p.name as patient_name FROM billing b JOIN patients p ON b.patient_id = p.id WHERE p.name LIKE ? OR p.email LIKE ? ORDER BY b.bill_date DESC',
                      (f'%{keyword}%', f'%{keyword}%'))
        return cursor.fetchall()

    def get_total_patients(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM patients')
        return cursor.fetchone()['count']

    def get_pending_bills_count(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM billing WHERE paid = 0')
        return cursor.fetchone()['count']

    def close(self):
        if self.conn:
            self.conn.close()


# LOGIN WINDOW
class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setup_ui()
        self.setWindowTitle("Medical Management System - Login")
        self.setGeometry(400, 200, 450, 350)

    def setup_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("MedCore System")
        layout.addWidget(title)
        
        subtitle = QLabel("Medical Management Platform")
        layout.addWidget(subtitle)
        
        layout.addSpacing(10)
        
        layout.addWidget(QLabel("Username:"))
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter username")
        layout.addWidget(self.username_edit)
        
        layout.addWidget(QLabel("Password:"))
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Enter password")
        self.password_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_edit)
        
        self.remember_check = QCheckBox("Remember me")
        layout.addWidget(self.remember_check)
        
        button_layout = QHBoxLayout()
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)
        button_layout.addWidget(login_btn)
        
        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.register)
        button_layout.addWidget(register_btn)
        
        layout.addLayout(button_layout)
        
        self.message_label = QLabel("")
        layout.addWidget(self.message_label)
        
        self.setLayout(layout)

    def login(self):
        username = self.username_edit.text()
        password = self.password_edit.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "❌ Please enter both username and password")
            return
        
        user = self.db.authenticate_user(username, password)
        if user:
            self.close()
            self.db.close()
            main_window = MainWindow(user)
            main_window.show()
        else:
            QMessageBox.warning(self, "Error", "❌ Invalid credentials")

    def register(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Register New User")
        dialog.setGeometry(450, 250, 400, 300)
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Username:"))
        username_edit = QLineEdit()
        layout.addWidget(username_edit)
        
        layout.addWidget(QLabel("Email:"))
        email_edit = QLineEdit()
        layout.addWidget(email_edit)
        
        layout.addWidget(QLabel("Password:"))
        password_edit = QLineEdit()
        password_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(password_edit)
        
        layout.addWidget(QLabel("Confirm Password:"))
        confirm_edit = QLineEdit()
        confirm_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(confirm_edit)
        
        def register_user():
            username = username_edit.text()
            email = email_edit.text()
            password = password_edit.text()
            confirm = confirm_edit.text()
            
            if not all([username, email, password, confirm]):
                QMessageBox.warning(dialog, "Error", "❌ All fields are required")
                return
            
            if password != confirm:
                QMessageBox.warning(dialog, "Error", "❌ Passwords do not match")
                return
            
            if self.db.add_user(username, email, password):
                dialog.close()
                QMessageBox.information(self, "Success", "✓ User registered successfully. Please login.")
            else:
                QMessageBox.warning(dialog, "Error", "❌ Username already exists")
        
        register_btn = QPushButton("Register")
        register_btn.clicked.connect(register_user)
        layout.addWidget(register_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()


# MAIN WINDOW
class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = Database()
        self.setWindowTitle("Medical Management System")
        self.setGeometry(0, 0, 1400, 900)
        
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # Sidebar
        sidebar = QWidget()
        sidebar.setMaximumWidth(250)
        sidebar_layout = QVBoxLayout()
        
        logo = QLabel("MedCore System")
        sidebar_layout.addWidget(logo)
        
        self.dashboard_btn = QPushButton("Dashboard")
        self.dashboard_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.dashboard_page))
        self.dashboard_btn.clicked.connect(self.load_dashboard) 
        sidebar_layout.addWidget(self.dashboard_btn)
        
        self.patient_btn = QPushButton("Patient Management")
        self.patient_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.patient_page))
        self.patient_btn.clicked.connect(self.load_patients)
        sidebar_layout.addWidget(self.patient_btn)
        
        self.appointment_btn = QPushButton("Appointments")
        self.appointment_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.appointment_page))
        self.appointment_btn.clicked.connect(self.load_appointments)
        sidebar_layout.addWidget(self.appointment_btn)
        
        self.billing_btn = QPushButton("Billing and Payments")
        self.billing_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.billing_page))
        self.billing_btn.clicked.connect(self.load_billing)
        sidebar_layout.addWidget(self.billing_btn)
        
        self.symptom_btn = QPushButton("Symptom Analyzer")
        self.symptom_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.symptom_page))
        sidebar_layout.addWidget(self.symptom_btn)
        
        self.admin_btn = QPushButton("Admin Settings")
        self.admin_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.admin_page))
        self.admin_btn.clicked.connect(self.load_admin)
        sidebar_layout.addWidget(self.admin_btn)
        
        sidebar_layout.addStretch()
        
        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.logout)
        sidebar_layout.addWidget(logout_btn)
        
        sidebar.setLayout(sidebar_layout)
        main_layout.addWidget(sidebar)
        
        # Stacked Widget for Pages
        self.stacked_widget = QStackedWidget()
        
        # Dashboard Page
        self.dashboard_page = QWidget()
        dashboard_layout = QVBoxLayout()
        
        title = QLabel("Dashboard")
        dashboard_layout.addWidget(title)
        
        stats_layout = QHBoxLayout()
        
        self.total_patients_box = QGroupBox("Total Patients")
        stats_layout.addWidget(self.total_patients_box)
        
        self.today_appt_box = QGroupBox("Today Appointments")
        stats_layout.addWidget(self.today_appt_box)
        
        self.pending_bills_box = QGroupBox("Pending Bills")
        stats_layout.addWidget(self.pending_bills_box)
        
        dashboard_layout.addLayout(stats_layout)
        
        self.dashboard_table = QTableWidget()
        self.dashboard_table.setColumnCount(4)
        self.dashboard_table.setHorizontalHeaderLabels(['Patient Name', 'Appointment Time', 'Doctor', 'Status'])
        dashboard_layout.addWidget(self.dashboard_table)
        
        self.dashboard_page.setLayout(dashboard_layout)
        self.stacked_widget.addWidget(self.dashboard_page)
        
        # Patient Page
        self.patient_page = QWidget()
        patient_layout = QVBoxLayout()
        
        patient_toolbar = QHBoxLayout()
        self.search_patient = QLineEdit()
        self.search_patient.setPlaceholderText("Search patient...")
        self.search_patient.textChanged.connect(self.search_patients)
        patient_toolbar.addWidget(self.search_patient)
        
        add_patient_btn = QPushButton("Add Patient")
        add_patient_btn.clicked.connect(self.add_patient_dialog)
        patient_toolbar.addWidget(add_patient_btn)
        
        patient_layout.addLayout(patient_toolbar)
        
        self.table_patients = QTableWidget()
        self.table_patients.setColumnCount(6)
        self.table_patients.setHorizontalHeaderLabels(['ID', 'Name', 'Email', 'Phone', 'Age', 'Disease'])
        patient_layout.addWidget(self.table_patients)
        
        self.patient_page.setLayout(patient_layout)
        self.stacked_widget.addWidget(self.patient_page)
        
        # Appointment Page
        self.appointment_page = QWidget()
        appointment_layout = QVBoxLayout()
        
        appt_toolbar = QHBoxLayout()
        add_appt_btn = QPushButton("Add Appointment")
        add_appt_btn.clicked.connect(self.add_appointment_dialog)
        appt_toolbar.addWidget(add_appt_btn)
        
        complete_appt_btn = QPushButton("Mark Complete")
        complete_appt_btn.clicked.connect(self.mark_appointment_complete)
        appt_toolbar.addWidget(complete_appt_btn)
        
        appointment_layout.addLayout(appt_toolbar)
        
        self.table_appointments = QTableWidget()
        self.table_appointments.setColumnCount(5)
        self.table_appointments.setHorizontalHeaderLabels(['ID', 'Patient', 'Doctor', 'Date and Time', 'Status'])
        appointment_layout.addWidget(self.table_appointments)
        
        self.appointment_page.setLayout(appointment_layout)
        self.stacked_widget.addWidget(self.appointment_page)
        
        # Billing Page
        self.billing_page = QWidget()
        billing_layout = QVBoxLayout()
        
        billing_toolbar = QHBoxLayout()
        self.search_billing = QLineEdit()
        self.search_billing.setPlaceholderText("Search billing...")
        self.search_billing.textChanged.connect(self.search_billing_func)
        billing_toolbar.addWidget(self.search_billing)
        
        create_bill_btn = QPushButton("Create Bill")
        create_bill_btn.clicked.connect(self.create_bill_dialog)
        billing_toolbar.addWidget(create_bill_btn)
        
        process_payment_btn = QPushButton("Process Payment")
        process_payment_btn.clicked.connect(self.process_payment)
        billing_toolbar.addWidget(process_payment_btn)
        
        billing_layout.addLayout(billing_toolbar)
        
        self.table_billing = QTableWidget()
        self.table_billing.setColumnCount(5)
        self.table_billing.setHorizontalHeaderLabels(['Bill ID', 'Patient', 'Amount', 'Date', 'Status'])
        billing_layout.addWidget(self.table_billing)
        
        self.billing_page.setLayout(billing_layout)
        self.stacked_widget.addWidget(self.billing_page)
        
        # Symptom Page
        self.symptom_page = QWidget()
        symptom_layout = QVBoxLayout()
        
        symptom_box = QGroupBox("Select Symptoms")
        symptom_grid = QGridLayout()
        
        self.chk_fever = QCheckBox("Fever")
        self.chk_cough = QCheckBox("Cough")
        self.chk_headache = QCheckBox("Headache")
        self.chk_nausea = QCheckBox("Nausea")
        self.chk_fatigue = QCheckBox("Fatigue")
        self.chk_breath = QCheckBox("Shortness of Breath")
        
        symptom_grid.addWidget(self.chk_fever, 0, 0)
        symptom_grid.addWidget(self.chk_cough, 0, 1)
        symptom_grid.addWidget(self.chk_headache, 0, 2)
        symptom_grid.addWidget(self.chk_nausea, 1, 0)
        symptom_grid.addWidget(self.chk_fatigue, 1, 1)
        symptom_grid.addWidget(self.chk_breath, 1, 2)
        
        symptom_box.setLayout(symptom_grid)
        symptom_layout.addWidget(symptom_box)
        
        symptom_btn_layout = QHBoxLayout()
        analyze_btn = QPushButton("Analyze")
        analyze_btn.clicked.connect(self.analyze_symptoms)
        symptom_btn_layout.addWidget(analyze_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_symptoms)
        symptom_btn_layout.addWidget(clear_btn)
        
        symptom_layout.addLayout(symptom_btn_layout)
        
        self.text_recommendation = QTextEdit()
        self.text_recommendation.setReadOnly(True)
        symptom_layout.addWidget(self.text_recommendation)
        
        self.symptom_page.setLayout(symptom_layout)
        self.stacked_widget.addWidget(self.symptom_page)
        
        # Admin Page
        self.admin_page = QWidget()
        admin_layout = QVBoxLayout()
        
        admin_title = QLabel("Administration Settings")
        admin_layout.addWidget(admin_title)
        
        admin_tabs = QTabWidget()
        
        # Users Tab
        users_tab = QWidget()
        users_layout = QVBoxLayout()
        
        users_toolbar = QHBoxLayout()
        add_user_btn = QPushButton("Add User")
        add_user_btn.clicked.connect(self.add_user_dialog)
        users_toolbar.addWidget(add_user_btn)
        
        users_layout.addLayout(users_toolbar)
        
        self.table_users = QTableWidget()
        self.table_users.setColumnCount(3)
        self.table_users.setHorizontalHeaderLabels(['Username', 'Email', 'Role'])
        users_layout.addWidget(self.table_users)
        
        users_tab.setLayout(users_layout)
        admin_tabs.addTab(users_tab, "User Management")
        
        # Doctors Tab
        doctors_tab = QWidget()
        doctors_layout = QVBoxLayout()
        
        doctors_toolbar = QHBoxLayout()
        add_doctor_btn = QPushButton("Add Doctor")
        add_doctor_btn.clicked.connect(self.add_doctor_dialog)
        doctors_toolbar.addWidget(add_doctor_btn)
        
        remove_doctor_btn = QPushButton("Remove Doctor")
        remove_doctor_btn.clicked.connect(self.remove_doctor)
        doctors_toolbar.addWidget(remove_doctor_btn)
        
        doctors_layout.addLayout(doctors_toolbar)
        
        self.table_doctors = QTableWidget()
        self.table_doctors.setColumnCount(4)
        self.table_doctors.setHorizontalHeaderLabels(['ID', 'Name', 'Specialty', 'Phone'])
        doctors_layout.addWidget(self.table_doctors)
        
        doctors_tab.setLayout(doctors_layout)
        admin_tabs.addTab(doctors_tab, "Doctor Management")
        
        # Settings Tab
        settings_tab = QWidget()
        settings_layout = QVBoxLayout()
        
        settings_label = QLabel("System configuration options")
        settings_layout.addWidget(settings_label)
        
        backup_btn = QPushButton("Backup Database")
        backup_btn.clicked.connect(self.backup_database)
        settings_layout.addWidget(backup_btn)
        
        settings_layout.addStretch()
        
        settings_tab.setLayout(settings_layout)
        admin_tabs.addTab(settings_tab, "System Settings")
        
        admin_layout.addWidget(admin_tabs)
        
        self.admin_page.setLayout(admin_layout)
        self.stacked_widget.addWidget(self.admin_page)
        
        main_layout.addWidget(self.stacked_widget)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        self.load_dashboard()

    def load_dashboard(self):
        total = self.db.get_total_patients()
        self.total_patients_box.setTitle(f"Total Patients: {total}")
        
        today_appts = self.db.get_today_appointments()
        self.today_appt_box.setTitle(f"Today Appointments: {len(today_appts)}")
        
        pending_bills = self.db.get_pending_bills_count()
        self.pending_bills_box.setTitle(f"Pending Bills: {pending_bills}")
        
        self.populate_table(self.dashboard_table, today_appts, ['patient_name', 'appointment_date', 'doctor', 'status'])

    def populate_table(self, table, data, columns):
        table.setRowCount(0)
        for row_idx, row_data in enumerate(data):
            table.insertRow(row_idx)
            for col_idx, col_name in enumerate(columns):
                try:
                    # Try to get the value, handle missing columns
                    if isinstance(row_data, dict) or hasattr(row_data, '__getitem__'):
                        try:
                            value = row_data[col_name]
                        except (KeyError, IndexError):
                            value = ""  # Default to empty string if column doesn't exist
                    else:
                        try:
                            value = getattr(row_data, col_name, "")
                        except AttributeError:
                            value = ""
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    table.setItem(row_idx, col_idx, item)
                except Exception as e:
                    # Fallback: set empty item
                    item = QTableWidgetItem("")
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    table.setItem(row_idx, col_idx, item)

    def add_patient_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Patient")
        dialog.setGeometry(450, 250, 500, 600)
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Name:"))
        name_edit = QLineEdit()
        layout.addWidget(name_edit)
        
        layout.addWidget(QLabel("Email:"))
        email_edit = QLineEdit()
        layout.addWidget(email_edit)
        
        layout.addWidget(QLabel("Phone:"))
        phone_edit = QLineEdit()
        layout.addWidget(phone_edit)
        
        layout.addWidget(QLabel("Age:"))
        age_spin = QSpinBox()
        age_spin.setRange(0, 150)
        layout.addWidget(age_spin)
        
        layout.addWidget(QLabel("Gender:"))
        gender_combo = QComboBox()
        gender_combo.addItems(['', 'Male', 'Female', 'Other'])
        layout.addWidget(gender_combo)
        
        layout.addWidget(QLabel("Address:"))
        address_edit = QLineEdit()
        layout.addWidget(address_edit)
        
        layout.addWidget(QLabel("Medical History:"))
        history_edit = QTextEdit()
        history_edit.setMaximumHeight(80)
        layout.addWidget(history_edit)
        
        layout.addWidget(QLabel("Disease:"))
        disease_edit = QLineEdit()
        disease_edit.setPlaceholderText("Enter disease/condition...")
        layout.addWidget(disease_edit)
        
        def save():
            name = name_edit.text()
            email = email_edit.text()
            phone = phone_edit.text()
            age = age_spin.value()
            gender = gender_combo.currentText()
            address = address_edit.text()
            history = history_edit.toPlainText()
            disease = disease_edit.text()
            
            if not name or not email:
                QMessageBox.warning(dialog, "Error", "❌ Name and Email are required")
                return
            
            patient_id = self.db.add_patient(name, email, phone, age, gender, address, history, disease)
            if patient_id:
                dialog.close()
                self.load_patients()
                QMessageBox.information(self, "Success", "✓ Patient added successfully")
            else:
                QMessageBox.warning(dialog, "Error", "❌ Email already exists")
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(save)
        layout.addWidget(save_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def load_patients(self):
        patients = self.db.get_all_patients()
        self.populate_table(self.table_patients, patients, ['id', 'name', 'email', 'phone', 'age', 'disease'])

    def search_patients(self):
        keyword = self.search_patient.text().strip()
        if keyword:
            patients = self.db.search_patients(keyword)
        else:
            patients = self.db.get_all_patients()
        self.populate_table(self.table_patients, patients, ['id', 'name', 'email', 'phone', 'age', 'disease'])

    def add_appointment_dialog(self):
        patients = self.db.get_all_patients()
        doctors = self.db.get_all_doctors()
        
        if not patients:
            QMessageBox.warning(self, "Error", "No patients found. Add a patient first.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Add Appointment")
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Patient:"))
        patient_combo = QComboBox()
        for p in patients:
            patient_combo.addItem(p['name'], p['id'])
        layout.addWidget(patient_combo)
        
        layout.addWidget(QLabel("Doctor:"))
        doctor_combo = QComboBox()
        if doctors:
            for d in doctors:
                doctor_combo.addItem(f"{d['name']} ({d['specialty']})", d['name'])
        else:
            doctor_combo.addItem("No doctors available")
        
        doctor_edit = QLineEdit()
        layout.addWidget(doctor_combo)
        
        layout.addWidget(QLabel("Or enter doctor name:"))
        layout.addWidget(doctor_edit)
        
        layout.addWidget(QLabel("Date and Time:"))
        datetime_edit = QDateTimeEdit()
        datetime_edit.setDateTime(QDateTime.currentDateTime())
        layout.addWidget(datetime_edit)

        # Yahan se dhyan dein: def save ab sahi spaces (8 spaces) par hai
        def save():
            patient_id = patient_combo.currentData()
            doctor = doctor_edit.text() if doctor_edit.text() else doctor_combo.currentData()
            dt = datetime_edit.dateTime().toPyDateTime()
            self.db.add_appointment(patient_id, doctor, dt)
            self.load_appointments()
            self.load_dashboard()  # Dashboard refresh call
            dialog.close()
            QMessageBox.information(self, "Success", "✓ Appointment added")
        
        # Yeh saari lines bhi save() se baahar aur main function ke andar hain
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(save)
        layout.addWidget(save_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()


    def load_appointments(self):
        appointments = self.db.get_all_appointments()
        self.populate_table(self.table_appointments, appointments, ['id', 'patient_name', 'doctor', 'appointment_date', 'status'])

    def mark_appointment_complete(self):
        row = self.table_appointments.currentRow()
        if row >= 0:
            appt_id = int(self.table_appointments.item(row, 0).text())
            self.db.update_appointment_status(appt_id, "completed")
            self.load_appointments()
            QMessageBox.information(self, "Success", "✓ Appointment marked complete")
        else:
            QMessageBox.warning(self, "Error", "Please select an appointment")

    def create_bill_dialog(self):
        patients = self.db.get_all_patients()
        if not patients:
            QMessageBox.warning(self, "Error", "No patients found")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Create Bill")
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Patient:"))
        patient_combo = QComboBox()
        for p in patients:
            patient_combo.addItem(p['name'], p['id'])
        layout.addWidget(patient_combo)
        
        layout.addWidget(QLabel("Amount:"))
        amount_spin = QDoubleSpinBox()
        amount_spin.setRange(0, 999999)
        layout.addWidget(amount_spin)
        
        layout.addWidget(QLabel("Description:"))
        desc_edit = QLineEdit()
        layout.addWidget(desc_edit)
        
        def save():
            patient_id = patient_combo.currentData()
            amount = amount_spin.value()
            desc = desc_edit.text()
            self.db.add_bill(patient_id, amount, desc)
            self.load_billing()
            dialog.close()
            QMessageBox.information(self, "Success", "✓ Bill created")
        
        save_btn = QPushButton("Create")
        save_btn.clicked.connect(save)
        layout.addWidget(save_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def load_billing(self):
        bills = self.db.get_all_bills()
        self.populate_table(self.table_billing, bills, ['id', 'patient_name', 'amount', 'bill_date', 'paid'])

    def process_payment(self):
        row = self.table_billing.currentRow()
        if row >= 0:
            bill_id = int(self.table_billing.item(row, 0).text())
            self.db.mark_bill_paid(bill_id)
            self.load_billing()
            QMessageBox.information(self, "Success", "✓ Payment processed")
        else:
            QMessageBox.warning(self, "Error", "Please select a bill")

    def search_billing_func(self):
        keyword = self.search_billing.text().strip()
        if keyword:
            bills = self.db.search_bills(keyword)
        else:
            bills = self.db.get_all_bills()
        self.populate_table(self.table_billing, bills, ['id', 'patient_name', 'amount', 'bill_date', 'paid'])

    def analyze_symptoms(self):
        symptoms = []
        if self.chk_fever.isChecked(): symptoms.append("Fever")
        if self.chk_cough.isChecked(): symptoms.append("Cough")
        if self.chk_headache.isChecked(): symptoms.append("Headache")
        if self.chk_nausea.isChecked(): symptoms.append("Nausea")
        if self.chk_fatigue.isChecked(): symptoms.append("Fatigue")
        if self.chk_breath.isChecked(): symptoms.append("Shortness of Breath")

        if not symptoms:
            self.text_recommendation.setText("Please select at least one symptom")
            return

        # Symptom to specialty mapping
        symptom_specialty_map = {
            "Fever": "General Practitioner",
            "Cough": "Pulmonologist",
            "Headache": "Neurologist",
            "Nausea": "Gastroenterologist",
            "Fatigue": "General Practitioner",
            "Shortness of Breath": "Cardiologist"
        }

        result = "Recommended Specialists:\n\n"
        specialists_map = {}
        
        for symptom in symptoms:
            if symptom in symptom_specialty_map:
                specialty = symptom_specialty_map[symptom]
                if specialty not in specialists_map:
                    specialists_map[specialty] = []
                specialists_map[specialty].append(symptom)
        
        # Get doctors from database
        doctors_db = self.db.get_all_doctors()
        doctor_map = {}
        for doc in doctors_db:
            specialty = doc['specialty']
            if specialty not in doctor_map:
                doctor_map[specialty] = []
            doctor_map[specialty].append(doc['name'])
        
        # Build recommendation with doctor names
        for specialty, symptom_list in sorted(specialists_map.items()):
            result += f"\n📋 For {', '.join(symptom_list)}:\n"
            
            # Find doctors for this specialty
            found_doctors = False
            for doc_specialty, doc_names in doctor_map.items():
                if specialty.lower() in doc_specialty.lower() or doc_specialty.lower() in specialty.lower():
                    for doc_name in doc_names:
                        result += f"   👨‍⚕️ Dr. {doc_name} ({specialty})\n"
                    found_doctors = True
            
            if not found_doctors:
                result += f"   🏥 Consult a {specialty}\n"

        self.text_recommendation.setText(result)

    def clear_symptoms(self):
        for chk in [self.chk_fever, self.chk_cough, self.chk_headache,
                   self.chk_nausea, self.chk_fatigue, self.chk_breath]:
            chk.setChecked(False)
        self.text_recommendation.clear()

    def add_doctor_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Doctor")
        dialog.setGeometry(450, 250, 400, 300)
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Doctor Name:"))
        name_edit = QLineEdit()
        layout.addWidget(name_edit)
        
        layout.addWidget(QLabel("Specialty:"))
        specialty_edit = QLineEdit()
        specialty_edit.setPlaceholderText("e.g., Cardiologist, Neurologist...")
        layout.addWidget(specialty_edit)
        
        layout.addWidget(QLabel("Phone:"))
        phone_edit = QLineEdit()
        layout.addWidget(phone_edit)
        
        layout.addWidget(QLabel("Email:"))
        email_edit = QLineEdit()
        layout.addWidget(email_edit)
        
        def save():
            name = name_edit.text()
            specialty = specialty_edit.text()
            phone = phone_edit.text()
            email = email_edit.text()
            
            if not name or not specialty:
                QMessageBox.warning(dialog, "Error", "❌ Name and Specialty are required")
                return
            
            if self.db.add_doctor(name, specialty, phone, email):
                dialog.close()
                self.load_doctors()
                QMessageBox.information(self, "Success", "✓ Doctor added successfully")
            else:
                QMessageBox.warning(dialog, "Error", "❌ Failed to add doctor")
        
        save_btn = QPushButton("Add")
        save_btn.clicked.connect(save)
        layout.addWidget(save_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def load_doctors(self):
        doctors = self.db.get_all_doctors()
        self.populate_table(self.table_doctors, doctors, ['id', 'name', 'specialty', 'phone'])

    def remove_doctor(self):
        row = self.table_doctors.currentRow()
        if row >= 0:
            doctor_id = int(self.table_doctors.item(row, 0).text())
            reply = QMessageBox.question(self, "Confirm", "Are you sure you want to remove this doctor?")
            if reply == QMessageBox.Yes:
                self.db.delete_doctor(doctor_id)
                self.load_doctors()
                QMessageBox.information(self, "Success", "✓ Doctor removed")
        else:
            QMessageBox.warning(self, "Error", "Please select a doctor")

    def add_user_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add User")
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Username:"))
        username_edit = QLineEdit()
        layout.addWidget(username_edit)
        
        layout.addWidget(QLabel("Email:"))
        email_edit = QLineEdit()
        layout.addWidget(email_edit)
        
        layout.addWidget(QLabel("Password:"))
        password_edit = QLineEdit()
        password_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(password_edit)
        
        layout.addWidget(QLabel("Role:"))
        role_combo = QComboBox()
        role_combo.addItems(["staff", "doctor", "admin"])
        layout.addWidget(role_combo)
        
        def save():
            username = username_edit.text()
            password = password_edit.text()
            email = email_edit.text()
            role = role_combo.currentText()
            
            if not username or not password or not email:
                QMessageBox.warning(dialog, "Error", "All fields are required")
                return
            
            if self.db.add_user(username, email, password, role):
                dialog.close()
                self.load_admin()
                QMessageBox.information(self, "Success", "✓ User created")
            else:
                QMessageBox.warning(self, "Error", "❌ Username already exists")
        
        save_btn = QPushButton("Create")
        save_btn.clicked.connect(save)
        layout.addWidget(save_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def load_admin(self):
        users = self.db.get_all_users()
        self.populate_table(self.table_users, users, ['username', 'email', 'role'])
        self.load_doctors()

    def backup_database(self):
        try:
            shutil.copy("medical_system.db", "medical_system_backup.db")
            QMessageBox.information(self, "Success", "✓ Database backed up successfully")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"❌ Backup failed: {str(e)}")

    def logout(self):
        self.close()
        self.db.close()
        login_window = LoginWindow()
        login_window.show()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
