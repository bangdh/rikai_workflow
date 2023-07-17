from odoo import api, fields, models
from datetime import datetime, time, date
from odoo.exceptions import ValidationError
import logging
from json import dumps

logger = logging.getLogger(__name__)

class ProposeStep(models.Model):
    _name = 'rikai.workflow.propose.step'
    _description = 'Rikai Propose Step'

    name = fields.Char(
        string="Propose Step",
        readonly=True,
    )
    
    config_step = fields.Many2one('rikai.workflow.config.step', string="Config Step")

    step_type = fields.Selection(
        [
            ('payment_leader', 'Payment Leader'),
            ('owner_leader', 'Owner Leader'), 
            ('and_list', 'All listing approver (AND)'), 
            ('or_list', 'One of listing approver (OR)'),
            ('reo', 'Executive Officer')
        ],
        string="Type",
        readonly=True,
    )
    
    step_sequence = fields.Integer(
        string="Approve Sequence",
        readonly=True,
    )

    status = fields.Selection(
        [('waiting','Waiting'),('approved','Approved'),('confirming','Confirming'),('rejected','Rejected')],
        string='Status',
        readonly=True
    )

    approvers = fields.One2many(
        'rikai.workflow.propose.approver', 
        'propose_step', 
        string="Approvers",
        store=True,
        compute="_compute_approvers"
    )

    propose_payment = fields.Many2one(
        'rikai.workflow.propose.payment'
    )

    propose_budget = fields.Many2one(
        'rikai.workflow.propose.budget'
    )

    @api.depends('config_step', 'propose_payment', 'propose_budget')
    def _compute_approvers(self):
        for record in self:
            # If approvers is calculated then by pass
            if record.approvers:
                continue

            # If payment is not set then by pass
            if not record.propose_payment and not record.propose_budget:
                continue

            payment_department = ""
            owner_department = ""

            if record.propose_payment:
                # Get Payment Department
                payment_department = self.env["rikai.workflow.config.department"].search([("company","=", record.propose_payment.payment_company),("name","=", record.propose_payment.payment_department.name)])
                # Get Owner Department
                owner_department = self.env["rikai.workflow.config.department"].search([("company","=", record.propose_payment.owner_company),("name","=", record.propose_payment.owner_department)])

            # If step is propose_budget
            elif record.propose_budget:
                # Get Payment Department
                payment_department = self.env["rikai.workflow.config.department"].search([("company","=", record.propose_budget.company),("name","=", record.propose_budget.department.name)])
                # Get Owner Department
                owner_department = self.env["rikai.workflow.config.department"].search([("company","=", record.propose_budget.company),("name","=", record.propose_budget.department.name)])
    
            
            # Get payment leader
            payment_leader = payment_department.leader
            # Get owner leader
            owner_leader = owner_department.leader

            # Get REO of creator
            reo = payment_department.reo.leader

            # If type is AND or OR
            if record.config_step.step_type == 'and_list' or record.config_step.step_type == 'or_list':
                approver_list = []
                for config_approver in record.config_step.approvers:
                    approver_list.append([0,0, {'status':'waiting', 'employee': config_approver.name.id}])
                record.approvers = approver_list

            # Create approver for payment Leader
            elif record.config_step.step_type == 'payment_leader': # Payment leader
                approver_list = []
                approver_list.append([0,0, {'status':'waiting', 'employee': payment_leader.id}])
                record.approvers = approver_list

            # Create approver for owner Leader
            elif record.config_step.step_type == 'owner_leader': # Owner leader
                approver_list = []
                approver_list.append([0,0, {'status':'waiting', 'employee': owner_leader.id}])
                record.approvers = approver_list
            
            # Create approver for REO
            elif record.config_step.step_type == 'reo': # Executive
                approver_list = []
                approver_list.append([0,0, {'status':'waiting', 'employee': reo.id}])
                record.approvers = approver_list

            record.change_status()


    @api.depends('approvers')
    def change_status(self):
        # Change arrover_tags
        for record in self:
            record.status = 'waiting' #waiting
            # Check waiting or rejected
            for approver in record.approvers:
                if approver.status != 'waiting':
                    record.status = approver.status
                    break

            # Check confirming or approve
            if record.status != 'waiting' and record.status != 'rejected':
                record.status = 'approved'
                for approver in record.approvers:
                    if approver.status != 'approved':
                        record.status = 'confirming'
                        break
            
            # Checking OR condition Approve
            if record.step_type == 'or_list':
                for approver in record.approvers:
                    if approver.status == 'approved':
                        record.status = 'approved'
                        break

            # Checking OR Condition Reject
            if record.status == 'rejected':
                for approver in record.approvers:
                    if approver.status != 'rejected':
                        record.status = 'confirming'
                        break

        
                
   