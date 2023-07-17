from odoo import api, fields, models, _
from datetime import datetime, time, date
from odoo.exceptions import ValidationError
import logging
from json import dumps

logger = logging.getLogger(__name__)

class ExecutiveOfficer(models.Model):
    _name = 'rikai.workflow.config.reo'
    _description = 'Rikai Executive Officer'

    name = fields.Char(string="Title")
    description = fields.Char(string="Description")
    leader = fields.Many2one('employee', string="Leader")
    departments = fields.One2many('rikai.workflow.config.department', 'reo', string="Departments")
    deleted = fields.Boolean(string="Deleted")

class Department(models.Model):
    _name = 'rikai.workflow.config.department'
    _description = 'Rikai Virtual Department'

    name = fields.Char(string="Department", readonly=False)
    company = fields.Char(string="Company", readonly=False)

    leader = fields.Many2one('employee', string="Leader")
    accountant = fields.Many2one('employee', string="Accountant")
    reo = fields.Many2one('rikai.workflow.config.reo')

    deleted = fields.Boolean(string="Deleted")

    @api.multi
    def _get_department_by_employee(self, employee):
        return self.search([('company','=',employee.company), ('name','=',employee.department)])

    @api.multi
    def reload_department(self):
        # Delete logically all record
        self.search([('name','!=','TECH'),('name','!=','MIND'),('name','!=','RIKAI')]).write({'deleted':True})
        
        # Search employees base on employee_type=INTERNAL, retire_date is not set OR > Today
        grouped_employees = self.env['employee'].read_group(
            [('employee_type', '=', '01'),'|', ('retire_date','=', False), ('retire_date','>', date.today())],
            ['company','department'],
            ['company','department'],
            lazy=False
        )
        
        # create department base on employee department
        for group in grouped_employees:
            company = group['company']
            department = group['department']
            if not department:
                continue
            
            # search current deparment
            record = self.search([("company","=", company),("name","=", department)])
            if record:
                record.deleted = False
            else:
                self.create({"company":company, "name":department, "deleted":False})

        
        view_id_tree = self.env.ref('rikai_workflow.rikai_workflow_config_department_tree')
        return {
            'name': _('/'),
            'res_model': 'rikai.workflow.config.department',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'views': [(view_id_tree[0].id, 'list')],
            'target': 'current',
            'domain': [],
        }  
