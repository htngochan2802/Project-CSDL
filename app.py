from flask import Flask, render_template, request, redirect, url_for, flash, send_file
return redirect(url_for('patients_add'))
return render_template('patients_form.html', action='add')


@app.route('/patients/edit/<int:pid>', methods=['GET','POST'])
def patients_edit(pid):
if request.method=='POST':
name = request.form.get('name','').strip()
birthdate = request.form.get('birthdate','')
if not name:
flash('Tên bệnh nhân không được để trống', 'danger')
return redirect(url_for('patients_edit', pid=pid))
tv2.update_patient(pid, {'name': name, 'birthdate': birthdate})
flash('Cập nhật thành công', 'success')
return redirect(url_for('patients_list'))
patient = tv2.get_patient(pid)
return render_template('patients_form.html', action='edit', patient=patient)


@app.route('/patients/delete/<int:pid>')
def patients_delete(pid):
ok = tv2.delete_patient(pid)
if ok:
flash('Đã xóa bệnh nhân', 'success')
else:
flash('Không thể xóa bệnh nhân (ràng buộc dữ liệu)', 'danger')
return redirect(url_for('patients_list'))


# Similar routes for doctors, treatments, sessions (follow same pattern)


# Reports
@app.route('/reports')
def reports_index():
return render_template('report.html')


@app.route('/reports/export/<report_id>')
def reports_export(report_id):
df = tv2.get_report_dataframe(report_id)
if df is None or df.empty:
flash('Không có dữ liệu để xuất', 'warning')
return redirect(url_for('reports_index'))
output = io.BytesIO()
df.to_csv(output, index=False, encoding='utf-8-sig')
output.seek(0)
return send_file(output, mimetype='text/csv', as_attachment=True,
download_name=f'report_{report_id}_{datetime.now().strftime("%Y%m%d")}.csv')


if __name__ == '__main__':
app.run(debug=True)
