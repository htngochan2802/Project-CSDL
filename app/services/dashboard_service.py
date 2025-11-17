from app.db.connection import get_db_connection

def get_kpis():
    conn = get_db_connection()
    kpis = {
        'total_patients': 0,
        'total_doctors': 0,
        'total_sessions': 0,
        'avg_cost': 0,
        'high_cost_count': 0
    }
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # 1. Đếm tổng số lượng
        cursor.execute("SELECT COUNT(*) as cnt FROM Patients")
        kpis['total_patients'] = cursor.fetchone()['cnt']
        
        cursor.execute("SELECT COUNT(*) as cnt FROM Doctors")
        kpis['total_doctors'] = cursor.fetchone()['cnt']
        
        cursor.execute("SELECT COUNT(*) as cnt FROM TreatmentSessions")
        kpis['total_sessions'] = cursor.fetchone()['cnt']
        
        # 2. Tính chi phí trung bình
        cursor.execute("SELECT AVG(StandardCost) as avg FROM Treatments")
        res_avg = cursor.fetchone()['avg']
        kpis['avg_cost'] = round(res_avg, 2) if res_avg else 0
        
        # 3. Đếm số ca điều trị chi phí cao (> trung bình)
        sql_high_cost = """
            SELECT COUNT(*) as cnt FROM Treatments 
            WHERE StandardCost > (SELECT AVG(StandardCost) FROM Treatments)
        """
        cursor.execute(sql_high_cost)
        kpis['high_cost_count'] = cursor.fetchone()['cnt']
        
        conn.close()
    
    return kpis
