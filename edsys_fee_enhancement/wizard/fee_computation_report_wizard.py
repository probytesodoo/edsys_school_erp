from odoo import models, fields, api 
import time
# from datetime import date

class fee_computation_report(models.Model):
   
    _name = 'fee.compt.report'
     
    class_id = fields.Many2one('course','Class')
    student_section_id = fields.Many2one('section', 'Section')
    batch_id = fields.Many2one('batch', 'Academic Year')
    parent_ids = fields.Many2many('res.partner','parent_fee_report','parent_fee_id', 'fee_report_parent_id','Parent')
    
    
    @api.onchange('class_id', 'student_section_id', 'batch_id')
    def onchange_class_ids(self):
        res = {}
        class_id_list = []
        section_id_list = []
        if self.class_id or self.student_section_id or self.batch_id: 
            if self.class_id :
                for class_id in self.class_id :
                    class_id_list.append(class_id.id)
            if self.student_section_id :
                for section_id in self.student_section_id :
                    section_id_list.append(section_id.id)
            
                
            
            if class_id_list and section_id_list and self.batch_id:
                res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True ),('chield1_ids.batch_id', '=', self.batch_id.id), ('chield1_ids.class_id', 'in', class_id_list), ('chield1_ids.student_section_id', 'in', section_id_list)]}
                
            elif class_id_list and section_id_list and not self.batch_id :
                res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True ),('chield1_ids.student_section_id', 'in', section_id_list),('chield1_ids.class_id', 'in', class_id_list)]}
            elif class_id_list and not section_id_list and self.batch_id :
                res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True ),('chield1_ids.batch_id', '=', self.batch_id.id),('chield1_ids.class_id', 'in', class_id_list)]}
            elif not class_id_list and section_id_list and self.batch_id :
                res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True ), ('chield1_ids.batch_id', '=', self.batch_id.id),('chield1_ids.student_section_id', 'in', section_id_list)]}
            
            elif not class_id_list and not section_id_list and self.batch_id :
                res['domain'] = {'parent_ids': [ ('is_student','=',False),('is_parent','=', True ),('active','=', True ),('chield1_ids.batch_id', '=', self.batch_id.id)]}
            elif class_id_list and not section_id_list and not self.batch_id :
                res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True ), ('chield1_ids.class_id', 'in', class_id_list)]}
            elif not class_id_list and section_id_list and not self.batch_id :
                res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True ),('chield1_ids.student_section_id', 'in', section_id_list)]}
            else :
                res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True )]}
        else :
            res['domain'] = {'parent_ids': [('is_student','=',False),('is_parent','=', True ),('active','=', True )]}
            
        return res
    
       
    @api.multi
    def fee_compute_report(self):
        '''
        This function prints the sales order and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        return self.env['report'].get_action(self,'edsys_fee_enhancement.report_fee_computation_wizard_report')

       


    
  