from odoo import models, fields, api, _
from datetime import date,datetime
from odoo.exceptions import except_orm, Warning, RedirectWarning

class acd_term(models.Model):
    _name = 'acd.term'
    
    name = fields.Char(string="Term Name",size=126)
    start_date = fields.Date(string ="Start Date")
    end_date = fields.Date(string ="End Date")
    batch_id = fields.Many2one('batch','Acadamic Year')
    seq = fields.Integer(string="Sequence")
   
    @api.model
    def create(self,vals):
        """
        ------------------
        :param vals:
        :return:
        """
        batch_brw=self.env['batch'].browse(vals['batch_id'])
        batch_start_date=batch_brw.start_date
        batch_stop_date=batch_brw.end_date
        
        start_date=vals['start_date']
        stop_date=vals['end_date']
        if start_date>=batch_start_date and start_date<=batch_stop_date and stop_date>=batch_start_date and stop_date <=batch_stop_date and start_date < stop_date:
            pass
        else:
            raise except_orm(_('Warning!'),
                        _("Start date and End date of Term should be inbetween Duration of Acadamic Year"))
               
        prev_terms=self.search([('batch_id','=',vals['batch_id'])])  
        if len(prev_terms)==0:
            vals['seq']=1
        else:
            len1=0
            len1=len(prev_terms)
            vals['seq']=prev_terms[len1-1].seq+1
            
        for each in prev_terms:
            if (start_date>=each.start_date and start_date<=each.end_date) or (stop_date >= each.start_date and stop_date <= each.end_date):
                  raise except_orm(_('Warning!'),
                        _("Your Dates already comes under %s term") % (each.name,))
      
        return super(acd_term, self).create(vals)

    @api.multi
    def write(self,vals):
        """
        -----------------
        :param vals:
        :return:
        """
        if ('start_date' in vals) or ('end_date' in vals):
           
            batch_id=self.batch_id.id
            batch_brw=self.env['batch'].browse(batch_id)
            
            batch_start_date=batch_brw.start_date
            batch_stop_date=batch_brw.end_date
            
            if 'start_date' in vals:
                start_date=vals['start_date']
            else:
                start_date=self.start_date
            if 'end_date' in vals:
                stop_date=vals['end_date']
            else:
                stop_date=self.end_date    
            if start_date>=batch_start_date and start_date<=batch_stop_date and stop_date>=batch_start_date and stop_date <=batch_stop_date and start_date < stop_date:
                pass
            else:
                raise except_orm(_('Warning!'),
                        _("Start date and End date of Term should be inbetween Duration of Acadamic Year"))    
            prev_terms=self.search([('batch_id','=',batch_id)])  
            for each in prev_terms:
                if each.id !=self.id:
                    if (start_date>=each.start_date and start_date<=each.end_date) or (stop_date >= each.start_date and stop_date <= each.end_date):
                        raise except_orm(_('Warning!'),
                            _("Your Dates already comes under %s term") % (each.name,))

        return super(acd_term, self).write(vals)

class Batch(models.Model):

    _name = 'batch'
    code= fields.Char(size=8, string='Code', required=True)
    name= fields.Char(size=32, string='Name', required=True)
