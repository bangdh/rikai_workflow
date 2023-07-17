from odoo import api, fields, models
from datetime import datetime, time, date
from odoo.exceptions import ValidationError
import logging
from json import dumps
from odoo.http import request

logger = logging.getLogger(__name__)

class ProposeApprover(models.Model):
    _name = 'rikai.workflow.propose.approver'
    _description = 'Rikai Propose Approver'

    name = fields.Char(string="Approver", store=True, compute="_compute_result_tag")
    employee = fields.Many2one('employee')
    propose_step = fields.Many2one('rikai.workflow.propose.step')
    status = fields.Selection(
        [('waiting','Waiting'),('approved','Approved'),('confirming','Confirming'),('rejected','Rejected')],
        string='Status'
    )

    @api.depends("employee", "status")
    def _compute_result_tag(self):
        for record in self:
            record.name = "{}: {}".format(record.employee.name, dict(self._fields['status'].selection).get(record.status))
    
    # Do approve
    @api.one
    def do_approve(self):
        # Get email of login user
        email = request.env.user.email

        # Check if user have right to approve
        if email != self.employee.email:
            raise ValidationError("You don't have right to do this action")
            return False
        else:
            # change status to Approved
            self.status = 'approved'
            # Refresh approver status in step
            self.propose_step.change_status()
            return True

    # Do confirm
    @api.one
    def do_confirm(self):
        # Get email of login user
        email = request.env.user.email

        # Check if user have right to approve
        if email != self.employee.email:
            raise ValidationError("You don't have right to do this action")
            return False
        else:
            # change status to Approved
            self.status = 'confirming'
            # Refresh approver status in step
            self.propose_step.change_status()
            return True

    # Do reject
    @api.one
    def do_reject(self):
        # Get email of login user
        email = request.env.user.email

        # Check if user have right to approve
        if email != self.employee.email:
            raise ValidationError("You don't have right to do this action")
            return False
        else:
            # change status to Approved
            self.status = 'rejected'
            # Refresh approver status in step
            self.propose_step.change_status()
            return True