from flask import Flask, render_template, request, redirect, url_for, send_file
import pandas as pd
import io

# Import các models và services
from app.db.connection import get_db_connection
from app.models import patient_model, doctor_model, treatment_model, session_model
from app.services import dashboard_service

# Cấu hình Flask để tìm templates và static đúng chỗ
app = Flask(__name__, template_folder='ui/templates', static_folder='ui/static')

# --- 1. DASHBOARD ROUTE ---
@app.route('/')
def index():
    kpis = dashboard_service.get_kpis()
    return render_template('dashboard.html', kpis=kpis)

# --- 2. CRUD ROUTES (VÍ DỤ CHO PATIENTS) ---
@app.route('/patients')
def list_patients():
    patients = patient_model.get_all_patients()
    return render_template('patients.html', patients=patients)

@app.route('/patients/add', methods=['POST'])
def add_patient():
    name = request.form.get('name')
    birthdate = request.form.get('birthdate')
    if name and birthdate:
        patient_model.create_patient(name, birthdate)
    return redirect(url_for('list_patients'))

# (Tương tự, bạn cần thêm các route cho Doctors, Treatments, Sessions tại đây...)

# --- 3. REPORT ROUTES (4 BÁO CÁO BẮT BUỘC) --- [cite: 74-79]
def get_report_data(query_type):
    """Hàm hỗ trợ chạy SQL query báo cáo"""
    conn = get_db_connection()
    data = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        if query_type == 'inner': # Query 1
            sql = """SELECT p.PatientName, t.TreatmentName, s.TreatmentDate, t.StandardCost 
                     FROM TreatmentSessions s 
                     JOIN Patients p ON s.PatientID = p.PatientID 
                     JOIN Treatments t ON s.TreatmentID = t.TreatmentID"""
        elif query_type == 'left': # Query 2
            sql = """SELECT p.PatientName, t.TreatmentName, t.StandardCost 
                     FROM Patients p 
                     LEFT JOIN TreatmentSessions s ON p.PatientID = s.PatientID 
                     LEFT JOIN Treatments t ON s.TreatmentID = t.TreatmentID"""
        elif query_type == 'multi': # Query 3
            sql = """SELECT p.PatientName, d.DoctorName, t.TreatmentName, s.TreatmentDate, t.StandardCost 
                     FROM TreatmentSessions s 
                     JOIN Patients p ON s.PatientID = p.PatientID 
                     JOIN Doctors d ON s.DoctorID = d.DoctorID 
                     JOIN Treatments t ON s.TreatmentID = t.TreatmentID"""
        elif query_type == 'high_cost': # Query 4
            sql = """SELECT t.TreatmentName, t.StandardCost, p.PatientName 
                     FROM TreatmentSessions s 
                     JOIN Treatments t ON s.TreatmentID = t.TreatmentID 
                     JOIN Patients p ON s.PatientID = p.PatientID 
                     WHERE t.StandardCost > (SELECT AVG(StandardCost) FROM Treatments)"""
        
        cursor.execute(sql)
        data = cursor.fetchall()
        conn.close()
    return data

@app.route('/reports/<report_type>')
def show_report(report_type):
    # report_type có thể là: inner, left, multi, high_cost
    data = get_report_data(report_type)
    titles = {
        'inner': 'Báo cáo Phiên điều trị (Inner Join)',
        'left': 'Báo cáo Tất cả Bệnh nhân (Left Join)',
        'multi': 'Báo cáo Chi tiết Tổng hợp (Multi-Join)',
        'high_cost': 'Báo cáo Điều trị Chi phí cao'
    }
    return render_template('report.html', results=data, title=titles.get(report_type, 'Báo cáo'), report_type=report_type)

# --- 4. EXPORT CSV ROUTE --- [cite: 75]
@app.route('/export/<report_type>')
def export_csv(report_type):
    data = get_report_data(report_type)
    if not data:
        return "Không có dữ liệu để xuất", 404
        
    # Dùng pandas tạo CSV
    df = pd.DataFrame(data)
    output = io.BytesIO()
    df.to_csv(output, index=False, encoding='utf-8-sig')
    output.seek(0)
    
    return send_file(output, mimetype='text/csv', as_attachment=True, download_name=f'{report_type}_report.csv')

if __name__ == '__main__':
    app.run(debug=True)
