from odoo import models, fields, api, _
import subprocess
import ConfigParser
import os
import pysftp
import csv
import paramiko
# from odoo.osv import osv

import pyodbc
from odoo.exceptions import except_orm, Warning

''' Currently I am considering that biometric server is a windows server'''

class biometric_server(models.Model):

    _name = "biometric.server"

    #Biometric Server Details
    name = fields.Char('Server IP Address', required=True)
    port = fields.Char('Server Port', required=True)
    biometric_db_username = fields.Char('Biometric Database Username', required=True )
    biometric_db_password = fields.Char('Biometric Database Password' , required=True)
    biometric_db_name = fields.Char('Biometric Database Name' , required=True)
    #Fetch manual Attendance Database
    attendance_date_from = fields.Datetime(string="Attendance Date Form", default=False)

    @api.multi
    def fetch_attendance_data_manually(self):
        self.fetch_biometric_data()
        return True

    @api.model
    def fetch_biometric_data(self):
        attendace_rec_list = []
        config_details_rec = self.search([])
        conn_str = 'DRIVER=FreeTDS;SERVER=%s;PORT=%s;DATABASE=%s;UID=%s;PWD=%s;TDS_Version=8.0;' % (config_details_rec.name,config_details_rec.port,config_details_rec.biometric_db_name,config_details_rec.biometric_db_username, config_details_rec.biometric_db_password)
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        #below fetch_company is general for all companies except TIAD
        if self.env.user.company_id.bio_cmp_id :
            fetch_company = "SELECT CompanyName  FROM CompanyMaster where CompanyCode = %s " %(int(self.env.user.company_id.bio_cmp_id))
        else :
            raise except_orm(_('Warning!'), _("Configure Company Code!"))
       
        #fetch_company = "SELECT CompanyName  FROM CompanyMaster where CompanyCode in (1, 3) "
        cursor.execute(fetch_company)
        company_name = cursor.fetchone()[0]
        
        if config_details_rec.attendance_date_from : 
            attendance_query = "SELECT Emp_ID, Comp_Name, In_Punch, Out_Punch, Shift_In, Shift_Out, Status FROM MASTERPROCESSDAILYDATA where (Emp_ID IS NOT NULL) AND ((Out_Punch IS NOT NULL) OR (In_Punch IS NOT NULL)) AND (Comp_Name = '%s') AND ((Out_Punch >= '%s') OR  (In_Punch >= '%s')) " % (company_name, config_details_rec.attendance_date_from, config_details_rec.attendance_date_from)
        else :
            attendance_model = self.env['hr.attendance']
            attendance_ids = attendance_model.search([])
            last_attendance_id = attendance_ids and max(attendance_ids)
            
            if last_attendance_id :
                last_attendance_record = attendance_model.browse(last_attendance_id)
                last_attendance_record_time = datetime.strftime(last_attendance_record.name, "%Y-%m-%d")
                if last_attendance_record.action == 'sign_in' :
                    attendance_query = "SELECT Emp_ID, Comp_Name, In_Punch, Out_Punch, Shift_In, Shift_Out, Status FROM MASTERPROCESSDAILYDATA where (Emp_ID IS NOT NULL) AND (Comp_Name = '%s') AND (In_Punch > '%s') " % (company_name, last_attendance_record_time)
                else :
                    attendance_query = "SELECT Emp_ID, Comp_Name, In_Punch, Out_Punch, Shift_In, Shift_Out, Status FROM MASTERPROCESSDAILYDATA where (Emp_ID IS NOT NULL) AND (Comp_Name = '%s')  AND (Out_Punch > '%s') " % (company_name,last_attendance_record_time)
            else :
                attendance_query = "SELECT  Emp_ID, Comp_Name, In_Punch, Out_Punch, Shift_In, Shift_Out, Status FROM MASTERPROCESSDAILYDATA WHERE (Emp_ID IS NOT NULL) AND (Comp_Name = '%s')  AND ((In_Punch IS NOT NULL) OR (Out_Punch IS NOT NULL))"  %(company_name)

        for row in cursor.execute(attendance_query):
            Emp_ID = row[0]
            Comp_Name = row[1]
            In_Punch = row[2]
            Out_Punch = row[3]
            Shift_In = row[4]
            Shift_Out = row[5]
            Status = row[6]
            attendace_vals = {
                                'Emp_ID' : Emp_ID,
                                'In_Punch' : In_Punch,
                                'Out_Punch' : Out_Punch,
                                'Shift_In' : Shift_In,
                                'Shift_Out' : Shift_Out,
                                'Status' : Status
                            }
            attendace_rec_list.append(attendace_vals)
        if attendace_rec_list : 
            employee_model = self.env['hr.employee']
            employee_id = employee_model.process_attendance_details(attendace_rec_list)
