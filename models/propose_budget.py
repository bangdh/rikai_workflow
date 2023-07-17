from odoo import api, fields, models, exceptions
from datetime import datetime, time, date
from odoo.exceptions import ValidationError
import logging
from json import dumps
from odoo.http import request
from odoo.exceptions import ValidationError

logger = logging.getLogger(__name__)

months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

class ProposeBudget(models.Model):
    _name = 'rikai.workflow.propose.budget'
    _description = 'Rikai Budget'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']

    # Tên của Budget
    name=fields.Char(
        string="Budget Name",
        required=True,
        track_visibility='onchange',
    )

    # Phân loại Budget nội bộ
    category = fields.Many2one(
        'rikai.workflow.config.budget.category',
        string="Category",
        required=True,
        track_visibility='onchange',
    )

    # Category Type là Tự tính hay tính tự động
    category_type = fields.Selection(
        [
            ('compute', 'Compute'),
            ('input', 'Input')
        ], 
        string="Category Type",
        store=True,
        compute="_compute_category_type",
        track_visibility='onchange',
    )

    # Thực tế chi phí
    payments = fields.One2many(
        'rikai.workflow.propose.payment',
        'budget',
        string='Payments',
        copy=False,
        track_visibility='onchange',
    )

    # Năm tài chính của Budget
    fiscal_year = fields.Selection(
        [('2022','2022'),('2023','2023'),('2024','2024')],
        string='Fiscal Year',
        required=True,
        track_visibility='onchange',
    )

    # Năm cần phải thanh toán
    payment_year = fields.Selection(
        [('2022','2022'),('2023','2023'),('2024','2024')],
        string='Payment Year',
        required=True,
        track_visibility='onchange',
    )

    # Đơn vị lập budget
    company = fields.Char(
        string="Company",
        readonly=True,
        store=True,
        compute="_compute_company",
        track_visibility='onchange',
    )

    # Đơn vị lập budget
    department = fields.Many2one(
        'rikai.workflow.config.department',
        string="Department",
        required=True,
        track_visibility='onchange',
    )

    # Leader của đơn vị lập budget
    owner = fields.Many2one(
        'employee',
        string="Budget Owner",
        store=True,
        compute="_compute_company",
        track_visibility='onchange',
    )

    # Những người có thể request dùng budget
    payees = fields.Many2many(
        'employee',
        string="Payees",
        track_visibility='onchange',
        domain="[('email', 'ilike', '%@rikai.technology')]",
    )

    # Đơn vị tiền thanh toán
    currency = fields.Selection(
        [('VND','VND'),('JPY','JPY'),('USD','USD')],
        string="Currency",
        required=True,
        track_visibility='onchange',
    )
    
    # Tổng budget cả năm
    total_amount =fields.Float(
        string="Total Amount",
        readonly=True,
        store=True,
        compute="_compute_total",
        track_visibility='onchange',
    )

    # Tổng budget tới tháng hiện tại
    mte_amount = fields.Float(
        string="Remain(MTE)",
        readonly=True,
        track_visibility='onchange',
        store=True,
        compute="_compute_total",   
    )

    # Chu trình xét duyệt
    route = fields.Many2one(
        'rikai.workflow.config.route',
        required=True,
        copy=False,
        domain="[('apply_budget', '=', True)]",
        track_visibility='onchange',
    )

    # Các bước Approve theo chu chình duyệt đã chọn
    propose_steps = fields.One2many(
        'rikai.workflow.propose.step',
        'propose_budget',
        readonly=True, 
        compute="_compute_propose_steps",
        store=True,
        string="Propose Steps",
        copy=False,
        track_visibility='onchange',
    )

    # Trạng thái đề xuất
    state = fields.Selection(
        [
            ("creating","Creating"),
            ("submited","Submited"), 
            ("confirming","Confirming"), 
            ("approved","Approved"), 
            ("paid","Paid"),
            ("rejected","Rejected"), 
        ],
        string="State",
        copy=False,
        index=True,
        default="creating",
        readonly=True,
        track_visibility='onchange',
    )

    # Approver hiện tại
    approver = fields.Many2one(
        'rikai.workflow.propose.approver',
        readonly=True,
        track_visibility='onchange',
    )

    # Ghi chú thêm
    note = fields.Text(
        string="Notes",
        copy=True,
        #track_visibility='onchange',
        
    )

    jan = fields.Float(
        string="Jan",
        readonly=False,
        track_visibility='onchange',
        
    )

    feb = fields.Float(
        string="Feb",
        readonly=False,
        track_visibility='onchange',
        
    )

    mar = fields.Float(
        string="Mar",
        readonly=False,
        track_visibility='onchange',
        
    )

    apr = fields.Float(
        string="Apr",
        readonly=False,
        track_visibility='onchange',
        
    )

    may = fields.Float(
        string="May",
        readonly=False,
        track_visibility='onchange',
        
    )

    jun = fields.Float(
        string="Jun",
        readonly=False,
        track_visibility='onchange',
        
    )

    jul = fields.Float(
        string="Jul",
        readonly=False,
        track_visibility='onchange',
        
    )

    aug = fields.Float(
        string="Aug",
        readonly=False,
        track_visibility='onchange',
        
    )

    sep = fields.Float(
        string="Sep",
        readonly=False,
        track_visibility='onchange',
        
    )

    oct = fields.Float(
        string="Oct",
        readonly=False,
        track_visibility='onchange',
        
    )

    nov = fields.Float(
        string="Nov",
        readonly=False,
        track_visibility='onchange',
        
    )

    dec = fields.Float(
        string="Dec",
        readonly=False,
        track_visibility='onchange',
        
    )

    @api.one
    def write(self, vals):
        # Only update when approver action
        if'approver' in vals and len(vals) == 1:
            return super(ProposeBudget, self).write(vals)

        # Only update when approver action
        if'mte_amount' in vals and len(vals) == 1:
            return super(ProposeBudget, self).write(vals)
        
        # Only update when approver action
        if'total_amount' in vals and len(vals) == 1:
            return super(ProposeBudget, self).write(vals)

        # only change state is permited
        if'state' in vals and len(vals) == 1:
            return super(ProposeBudget, self).write(vals)

        # only change payees is permited
        if 'payees' in vals and len(vals) == 1:
            return super(ProposeBudget, self).write(vals)
            
        # If state is not creating, user can not update
        elif self.state != "creating":
            raise exceptions.UserError("Cannot update submited records.{}".format(vals))
        
        # If state is creating then user can update
        else:
            return super(ProposeBudget, self).write(vals)
        
    
    @api.multi
    def unlink(self):
        if self.state != "creating":
            raise exceptions.UserError("Cannot delete submited records.")
        else:
            return super(ProposeBudget, self).unlink()

    #######COMPUTE SECTION##########
    # Compute company
    @api.depends('department')
    def _compute_company(self):
        for record in self:
            record.company = record.department.company
            record.owner = record.department.leader

    # Compute total value
    @api.depends('jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec')
    def _compute_total(self):
        current_month = datetime.now().month
        for record in self:
            # Reset sum to zero for each record
            record.mte_amount = 0  
            record.total_amount = 0
            for index, month in enumerate(months):
                # Calculate Month To End
                record.mte_amount += getattr(record, month) if index + 1 >= current_month else 0
                # Calculate full year
                record.total_amount += getattr(record, month)

    # Compute category Type
    @api.depends('category')
    def _compute_category_type(self):
        for record in self:
            record.category_type = record.category.type

    # Tính các bước Approve theo chu trình đã chọn
    @api.depends('route')
    def _compute_propose_steps(self):
        for record in self:
            # reset steps
            propose_steps = [] 
            # Sort the step list based on the step_sequence
            sorted_steps = sorted(record.route.step_list, key=lambda step: step.step_sequence)

            for config_step in sorted_steps:
                # Create approve step
                propose_step = {
                    "name": config_step.name,
                    "step_type": config_step.step_type,
                    "approve_status": "Waiting",
                    "step_sequence": config_step.step_sequence,
                    "config_step":config_step.id
                }

                # Add step
                propose_steps += [(0, 0, propose_step)]
            
            # Add steps to record
            record.propose_steps = propose_steps

    @api.multi
    def action_approve(self):
        for record in self:
            if record.approver:
                record.approver.do_approve()
                record.approver = self._get_next_approver()
                record._compute_state()
        
    
    @api.multi
    def action_confirm(self):
        for record in self:
            if record.approver:
                record.approver.do_confirm()
                record.approver = self._get_next_approver()
                record._compute_state()
       
    
    @api.multi
    def action_reject(self):
        for record in self:
            if record.approver:
                record.approver.do_reject()
                record.approver = self._get_next_approver()
                record._compute_state()
        
    
    @api.multi
    def action_submit(self):
        for record in self:
            record.state = "submited"
            record.approver = self._get_next_approver()

    @api.multi
    def action_return(self):
        for record in self:
            if record.state == "submited" or record.state == "confirming":
                record.state = "creating"
                record.approver = self._get_next_approver()
    
    @api.multi
    def action_paid(self):
        for record in self:
            record.state = "paid"

    @api.multi
    def action_fix(self):
        for record in self:
            record._compute_total()    

    # compute state
    @api.multi
    def _compute_state(self):
        # Rejected Status
        for record in self:
            # Record is creating
            if record.state == "creating":
                continue
            
            # Record is rejected
            is_break = False
            for step in self.propose_steps:
                if step.status == 'rejected':
                    record.state = 'rejected'
                    is_break = True
                    break
            if is_break:
                continue

            # Record is approved or confirming
            is_break = False
            for step in self.propose_steps:
                if step.status != "approved":
                    is_break = True
                    break
            
            record.state = "confirming" if is_break else "approved"


    # Get next Approver
    @api.multi
    def _get_next_approver(self):
        for record in self:
            if record.state != "creating":
                for step in self.propose_steps:
                    if step.status == 'rejected':
                        return None
                    if step.status == "approved":
                        continue
                    for approver in step.approvers:
                        if approver.status != 'approved' and approver.status != 'rejected':
                            return approver
        return None