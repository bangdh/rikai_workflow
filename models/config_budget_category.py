from odoo import api, fields, models
from datetime import datetime, time, date
import logging
from json import dumps
from odoo.http import request
from odoo.exceptions import ValidationError

logger = logging.getLogger(__name__)

class BudgetCategory(models.Model):
    _name = 'rikai.workflow.config.budget.category'
    _description = 'Rikai Budget Category'
    _sql_constraints = [
        ('name', 'unique (name)', "Category already exists!"),
    ]

    # Category Name
    name = fields.Char(string="Category Name", required=True)

    # Description
    description = fields.Text(string="Description")
    
    # Category Type
    type = fields.Selection([
        ('compute', 'Compute'),
        ('input', 'Input')
    ], string="Type", required=True)

    # Parameter for multiplier
    param = fields.Float(string="Parameter", copy=True)

    # Metric for multiplier
    multiplier = fields.Selection([
        ('capita', 'Capita'),
        ('billable', 'Billable'),
        ('allocation', 'Allocations'),
        ('progress_revenue', 'Progress Revenue'),
        #('contract_revenue', 'Contract Revenue'),
    ], string="Multiplier", copy=True)

    # Compute level at Department Level or Company Level
    compute_level = fields.Selection([
        ('department', 'Department'),
        ('company', 'Company')
    ], string="Compute Level", copy=True)

    # Validation constrains between fields
    @api.constrains('type', 'multiplier', 'param', 'compute_level')
    def _validate_compute(self):
        for record in self:
            if record.type == 'compute':
                if not record.multiplier:
                    raise ValidationError("Multiplier is mandatory when Type is Compute")
                
                if not record.param:
                    raise ValidationError("Parameter is mandatory when Type is Compute")
                
                if not record.compute_level:
                    raise ValidationError("Compute Level is mandatory when Type is Compute")
            
            