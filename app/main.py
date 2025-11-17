from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import pandas as pd
import io
from datetime import datetime

# Import kết nối và các modules logic
from app.db.connection import get_db_connection
from app.models import patient_model, doctor_model, treatment_model, session_model
from app.services import dashboard_service

# Khởi tạo Flask app
# template_folder: nơi chứa file HTML (của TV3)
# static_folder: nơi chứa CSS/JS/Ảnh (của TV3)
app = Flask(__name__, template_folder='ui/templates', static_folder='ui/static')
app.secret_key = 'your_secret_key_here'  # Cần thiết để dùng flash message

# ==========================================
# 1. DASHBOARD (TRANG CHỦ)
# ==========================================
@app.route('/')
def dashboard():
    # Lấy số liệu KPI từ service
    kpis = dashboard_service.get_kpis()
    
    # Lấy dữ liệu cho biểu đồ (Ví dụ: Top 5 điều trị phổ biến nhất)
    # (Logic này có thể tách ra service nếu muốn gọn hơn)
    conn = get_db_connection()
    chart_data = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT t.TreatmentName, COUNT(*) as count
            FROM TreatmentSessions s
            JOIN Treatments t ON s.TreatmentID = t.TreatmentID
            GROUP BY t.TreatmentName
            ORDER BY count DESC
            LIMIT 5
        """
        cursor.execute(sql)
        chart_data = cursor.fetchall()
        conn.close()
        
    # Chuyển dữ liệu biểu đồ thành list để dễ dùng trong JS
    labels = [item['TreatmentName'] for item in chart_data]
    data = [item['count'] for item in chart_data]
    
    return render_template('dashboard.html', kpis=kpis, chart_labels=labels, chart_data=data)

# ==========================================
# 2. QUẢN LÝ BỆNH NHÂN (PATIENTS)
# ==========================================
@app.route('/patients')
def patients_list():
    keyword = request.args.get('search', '')
    if keyword:
        patients = patient_model.search_patients(keyword)
    else:
        patients = patient_model.get_all_patients()
    return render_template('patients.html', patients=patients, search_keyword=keyword)

@app.route('/patients/add', methods=['POST'])
def patients_add():
    name = request.form['name']
    birthdate = request.form['birthdate']
    if patient_model.create_patient(name, birthdate):
        flash('Thêm bệnh nhân thành công!', 'success')
    else:
        flash('Lỗi khi thêm bệnh nhân.', 'danger')
    return redirect(url_for('patients_list'))

@app.route('/patients/edit/<int:id>', methods=['GET', 'POST'])
def patients_edit(id):
    if request.method == 'POST':
        name = request.form['name']
        birthdate = request.form['birthdate']
        if patient_model.update_patient(id, name, birthdate):
            flash('Cập nhật thành công!', 'success')
            return redirect(url_for('patients_list'))
        else:
            flash('Lỗi cập nhật.', 'danger')
    
    # GET: Hiển thị form với dữ liệu cũ
    patient = patient_model.get_patient_by_id(id)
    return render_template('patients_edit.html', patient=patient)

@app.route('/patients/delete/<int:id>')
def patients_delete(id):
    if patient_model.delete_patient(id):
        flash('Đã xóa bệnh nhân.', 'success')
    else:
        flash('Không thể xóa (do ràng buộc dữ liệu).', 'danger')
    return redirect(url_for('patients_list'))

# ==========================================
# 3. QUẢN LÝ BÁC SĨ (DOCTORS)
# ==========================================
@app.route('/doctors')
def doctors_list():
    keyword = request.args.get('search', '')
    if keyword:
        doctors = doctor_model.search_doctors(keyword)
    else:
        doctors = doctor_model.get_all_doctors()
    return render_template('doctors.html', doctors=doctors, search_keyword=keyword)

@app.route('/doctors/add', methods=['POST'])
def doctors_add():
    name = request.form['name']
    specialty = request.form['specialty']
    doctor_model.create_doctor(name, specialty)
    flash('Thêm bác sĩ thành công!', 'success')
    return redirect(url_for('doctors_list'))

@app.route('/doctors/edit/<int:id>', methods=['GET', 'POST'])
def doctors_edit(id):
    if request.method == 'POST':
        name = request.form['name']
        specialty = request.form['specialty']
        doctor_model.update_doctor(id, name, specialty)
        flash('Cập nhật thành công!', 'success')
        return redirect(url_for('doctors_list'))
    
    doctor = doctor_model.get_doctor_by_id(id)
    return render_template('doctors_edit.html', doctor=doctor)

@app.route('/doctors/delete/<int:id>')
def doctors_delete(id):
    if doctor_model.delete_doctor(id):
        flash('Đã xóa bác sĩ.', 'success')
    else:
        flash('Không thể xóa (Bác sĩ đã có lịch khám).', 'danger')
    return redirect(url_for('doctors_list'))

# ==========================================
# 4. QUẢN LÝ ĐIỀU TRỊ (TREATMENTS)
# ==========================================
@app.route('/treatments')
def treatments_list():
    keyword = request.args.get('search', '')
    if keyword:
        treatments = treatment_model.search_treatments(keyword)
    else:
        treatments = treatment_model.get_all_treatments()
    return render_template('treatments.html', treatments=treatments, search_keyword=keyword)

@app.route('/treatments/add', methods=['POST'])
def treatments_add():
    name = request.form['name']
    cost = request.form['cost']
    treatment_model.create_treatment(name, cost)
    flash('Thêm liệu trình thành công!', 'success')
    return redirect(url_for('treatments_list'))

@app.route('/treatments/edit/<int:id>', methods=['GET', 'POST'])
def treatments_edit(id):
    if request.method == 'POST':
        name = request.form['name']
        cost = request.form['cost']
        treatment_model.update_treatment(id, name, cost)
        flash('Cập nhật thành công!', 'success')
        return redirect(url_for('treatments_list'))
        
    treatment = treatment_model.get_treatment_by_id(id)
    return render_template('treatments_edit.html', treatment=treatment)

@app.route('/treatments/delete/<int:id>')
def treatments_delete(id):
    if treatment_model.delete_treatment(id):
        flash('Đã xóa liệu trình.', 'success')
    else:
        flash('Không thể xóa (Liệu trình đã được sử dụng).', 'danger')
    return redirect(url_for('treatments_list'))

# ==========================================
# 5. QUẢN LÝ PHIÊN ĐIỀU TRỊ (SESSIONS) - PHỨC TẠP NHẤT
# ==========================================
@app.route('/sessions')
def sessions_list():
    keyword = request.args.get('search', '')
    if keyword:
        sessions = session_model.search_sessions(keyword)
    else:
        sessions = session_model.get_all_sessions()
    
    # Cần lấy danh sách để đổ vào Dropdown form Thêm mới (Modal)
    patients = patient_model.get_all_patients()
    doctors = doctor_model.get_all_doctors()
    treatments = treatment_model.get_all_treatments()
    
    return render_template('sessions.html', sessions=sessions, 
                           patients=patients, doctors=doctors, treatments=treatments,
                           search_keyword=keyword)

@app.route('/sessions/add', methods=['POST'])
def sessions_add():
    patient_id = request.form['patient_id']
    doctor_id = request.form['doctor_id']
    treatment_id = request.form['treatment_id']
    
    # Xử lý ngày giờ hiện tại nếu người dùng không chọn
    date_str = request.form.get('date')
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    session_model.create_session(patient_id, doctor_id, treatment_id, date_str)
    flash('Tạo phiên điều trị thành công!', 'success')
    return redirect(url_for('sessions_list'))

@app.route('/sessions/delete/<int:id>')
def sessions_delete(id):
    session_model.delete_session(id)
    flash('Đã xóa phiên điều trị.', 'success')
    return redirect(url_for('sessions_list'))

# ==========================================
# 6. BÁO CÁO & XUẤT FILE (REPORTS)
# ==========================================
def get_report_data_internal(report_type):
    """Hàm nội bộ để chạy SQL cho báo cáo"""
    conn = get_db_connection()
    data = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        sql = ""
        
        if report_type == 'inner_join':
            sql = """
                SELECT p.PatientName, t.TreatmentName, s.TreatmentDate, t.StandardCost 
                FROM TreatmentSessions s 
                JOIN Patients p ON s.PatientID = p.PatientID 
                JOIN Treatments t ON s.TreatmentID = t.TreatmentID
                ORDER BY s.TreatmentDate DESC
            """
        elif report_type == 'left_join':
            sql = """
                SELECT p.PatientName, t.TreatmentName, t.StandardCost, s.TreatmentDate 
                FROM Patients p 
                LEFT JOIN TreatmentSessions s ON p.PatientID = s.PatientID 
                LEFT JOIN Treatments t ON s.TreatmentID = t.TreatmentID
                ORDER BY p.PatientName
            """
        elif report_type == 'multi_table_join':
            sql = """
                SELECT p.PatientName, d.DoctorName, t.TreatmentName, s.TreatmentDate, t.StandardCost 
                FROM TreatmentSessions s 
                JOIN Patients p ON s.PatientID = p.PatientID 
                JOIN Doctors d ON s.DoctorID = d.DoctorID 
                JOIN Treatments t ON s.TreatmentID = t.TreatmentID
                ORDER BY s.TreatmentDate DESC
            """
        elif report_type == 'high_cost':
            sql = """
                SELECT t.TreatmentName, t.StandardCost, p.PatientName, s.TreatmentDate
                FROM TreatmentSessions s 
                JOIN Treatments t ON s.TreatmentID = t.TreatmentID 
                JOIN Patients p ON s.PatientID = p.PatientID 
                WHERE t.StandardCost > (SELECT AVG(StandardCost) FROM Treatments)
                ORDER BY t.StandardCost DESC
            """
            
        if sql:
            cursor.execute(sql)
            data = cursor.fetchall()
        conn.close()
    return data

@app.route('/reports/<report_type>')
def reports_view(report_type):
    data = get_report_data_internal(report_type)
    
    titles = {
        'inner_join': 'Báo cáo Hoạt động (Inner Join)',
        'left_join': 'Danh sách Tổng hợp Bệnh nhân (Left Join)',
        'multi_table_join': 'Báo cáo Chi tiết Toàn diện (Multi-Join)',
        'high_cost': 'Báo cáo Các ca Chi phí cao'
    }
    
    page_title = titles.get(report_type, 'Báo cáo')
    return render_template('report.html', results=data, title=page_title, report_id=report_type)

@app.route('/reports/export/<report_type>')
def reports_export(report_type):
    data = get_report_data_internal(report_type)
    
    if not data:
        flash('Không có dữ liệu để xuất.', 'warning')
        return redirect(url_for('dashboard'))
        
    # Chuyển list of dicts thành DataFrame
    df = pd.DataFrame(data)
    
    # Tạo buffer trong bộ nhớ để lưu file CSV
    output = io.BytesIO()
    # encoding='utf-8-sig' để Excel mở tiếng Việt không bị lỗi font
    df.to_csv(output, index=False, encoding='utf-8-sig')
    output.seek(0)
    
    return send_file(
        output, 
        mimetype='text/csv', 
        as_attachment=True, 
        download_name=f'report_{report_type}_{datetime.now().strftime("%Y%m%d")}.csv'
    )

# ==========================================
# KHỞI CHẠY ỨNG DỤNG
# ==========================================
if __name__ == '__main__':
    # debug=True giúp tự động reload khi sửa code (chỉ dùng khi dev)
    app.run(debug=True, port=5000)
