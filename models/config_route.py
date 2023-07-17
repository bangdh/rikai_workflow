from odoo import api, fields, models
from datetime import datetime, time, date
from odoo.exceptions import ValidationError
import logging
from json import dumps

logger = logging.getLogger(__name__)

# Route model
class Route(models.Model):
    _name = 'rikai.workflow.config.route'
    _description = 'Rikai Route'

    # Route Name
    name = fields.Char(string="Route Name")
    # Descriptions
    description = fields.Char(string="Descriptions")
    # List of step to approve
    step_list = fields.One2many('rikai.workflow.config.step', 'route', string="Propose Steps")
    
    # Apply for Budget or not
    apply_budget = fields.Boolean(
        string="Budgets",
    )
    # Apply for Payment or Not
    apply_payment = fields.Boolean(
        string="Payments",
    )


# Step Model
class Step(models.Model):
    _name = 'rikai.workflow.config.step'
    _description = 'Rikai Step'
    name = fields.Char(string="Approve Step")  
    step_type = fields.Selection(
        [
            ('payment_leader', 'Payment Leader'),
            ('owner_leader', 'Budget Owner Leader'), 
            ('and_list', 'All listing approver (AND)'), 
            ('or_list', 'One of listing approver (OR)'),
            ('reo', 'Executive Officer')
        ],
        string="Type"
    )
    
    step_sequence = fields.Integer(string="Approve Sequence")  
    route = fields.Many2one('rikai.workflow.config.route')
    approvers = fields.One2many('rikai.workflow.config.approver', 'step', string="Approvers")
    approver_tags = fields.Char(compute='_compute_approver_tags', store=True, readonly=True)

    @api.depends('approvers')
    def _compute_approver_tags(self):
        for record in self:
            if record.approvers:
                record.approver_tags = ', '.join(record.approvers.mapped('name.name'))

# Approver Model
class Approver(models.Model):
    _name = 'rikai.workflow.config.approver'
    _description = 'Rikai Approver'

    name = fields.Many2one('employee')
    step = fields.Many2one('rikai.workflow.config.step')