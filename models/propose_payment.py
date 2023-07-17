from odoo import api, fields, models, exceptions
from datetime import datetime, time, date
from odoo.exceptions import ValidationError
import logging
from json import dumps
from odoo.http import request
from odoo.exceptions import ValidationError
import math

logger = logging.getLogger(__name__)

class ProposePayment(models.Model):
    _name = 'rikai.workflow.propose.payment'
    _description = 'Rikai Payment'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']
    
    # Tên tờ trình
    name = fields.Char(
        string="Title",
        required=True,
        copy=False,
        track_visibility='onchange',
    )

    # Chu trình xét duyệt
    route = fields.Many2one(
        'rikai.workflow.config.route',
        required=True,
        copy=False,
        domain="[('apply_payment', '=', True)]",
        track_visibility='onchange',
    )

    # Các bước Approve theo chu chình duyệt đã chọn
    propose_steps = fields.One2many(
        'rikai.workflow.propose.step',
        'propose_payment',
        readonly=True, 
        compute="_compute_propose_steps",
        store=True,
        string="Propose Steps",
        copy=False,
        track_visibility='onchange',
    )

    # Đơn vị đứng ra thanh toán
    payment_company = fields.Char(
        string="Payment Comp.",
        store=True,
        compute="_compute_payment_company",
        track_visibility='onchange',
    )

    payment_department = fields.Many2one(
        'rikai.workflow.config.department',
        string="Payment Depart.",
        required =True,
        track_visibility='onchange',
    )

    # Đơn vị chủ sở hữu budget budget
    owner_company = fields.Char(
        string="Budget Comp.",
        store=True,
        compute="_compute_owner_company",
        track_visibility='onchange',
    )
    owner_department = fields.Char(
        string="Budget Depart.",
        store=True,
        compute="_compute_owner_company",
        track_visibility='onchange',
    )

    # Đơn vị tiền thanh toán
    currency = fields.Selection(
        [('VND','VND'),('JPY','JPY'),('USD','USD')],
        string="Currency",
        readonly=True,
        store=True,
        compute="_compute_owner_company",
        track_visibility='onchange',
    )

    # Số tiền budget sẽ xin
    budget_amount = fields.Float(
        string='Budget Use',
        required=True,
        track_visibility='onchange',
    )

    # Tổng số tiền thanh toán
    amount = fields.Float(
        string='Total Expense',
        copy=False,
        store=True,
        compute="_compute_amount",
        track_visibility='onchange',
    )

    # Hoá đơn thanh toán
    invoice = fields.Binary(
        string="Invoice",
        attachment=True,
        copy=False,
        track_visibility='onchange',
    )

    # Ngày thanh toán
    payment_date = fields.Date(
        string="Payment Date",
        required=True,
        copy=True,
        track_visibility='onchange',
    )

    # Trạng thái đề xuất
    state = fields.Selection(
        [
            ("creating","Creating"),
            ("submited","Submited"), 
            ("confirming","Confirming"), 
            ("approved","Approved"), 
            ("payment_request", "Payment Request"),
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

    # Kế toán theo dõi
    accountant = fields.Many2one(
        'employee', 
        string="Accountant",
        store=True,
        compute="_compute_payment_company",
        track_visibility='onchange',
    )

    # Chi tiết thanh toán
    payment_items = fields.One2many(
        'rikai.workflow.propose.payment.item',
        'payment',
        string="Payment Items",
        required=True,
        track_visibility='onchange',
    )

    # Tỷ lệ thuế GTGT
    tax_rate= fields.Float(
        string="Tax Rate(%)",
        required=True,
        track_visibility='onchange',
    )

    # Tổng thuế (làm tròn lên)
    tax_amount = fields.Float(
        string="Tax",
        store=True,
        readonly=True,
        compute="_compute_tax",
        track_visibility='onchange',
    )

    # Tổng số tiền phải thanh toán
    total_amount =fields.Float(
        string="Total Amount",
        store=True,
        readonly=True,
        compute="_compute_tax",
        track_visibility='onchange',
    )

    # Năm tài chính
    fiscal_year = fields.Selection(
        [('2022','2022'),('2023','2023'),('2024','2024')],
        string='Fiscal Year',
        required=True,
        track_visibility='onchange',
    )

    # Ngân sách của việc payment
    budget = fields.Many2one(
        'rikai.workflow.propose.budget',
        string='Budget',
        domain="[('id', 'in', budget_ids), ('state','=','approved')]",
        required=True,
        track_visibility='onchange',
    )

    # Domain for select Budget
    budget_ids = fields.Many2many(
        'rikai.workflow.propose.budget',
        compute='_compute_budget_ids',
        track_visibility='onchange',
    )
    
    # Hình thức thanh toán (Chuyển khoản, Tiền mặt, Thanh toán bằng Credit)
    transfer_type = fields.Selection(
        [('bank',"Bank Transfer"),('cash', 'Cash'), ('credit','Credit Card')],
        string="Transfer Type",
        track_visibility='onchange',
    )

    # Người thụ hưởng
    reciever = fields.Text(
        string="Reciever",
        track_visibility='onchange',
    )

    # Approver hiện tại
    approver = fields.Many2one(
        'rikai.workflow.propose.approver',
        readonly=True,
        track_visibility='onchange',
    )
    # Group Supper User của mục expense
    # Danh sách những người nằm trong danh sách approvers
    # Báo giá

    # prevent to edit submited record
    @api.one
    def write(self, vals):
        # For supper user
        # if self.env.user.email == "doanhaibang@rikai.technology":
        #     return super(ProposePayment, self).write(vals)

        # Only update when approver action
        if'approver' in vals and len(vals) == 1:
            return super(ProposePayment, self).write(vals)
        
        if'state' in vals and len(vals) == 1:
            return super(ProposePayment, self).write(vals)
        
        if 'message_main_attachment_id' in vals and len(vals) == 1:
            return super(ProposePayment, self).write(vals)
            
        # Prevent user to update when state is paid or jected
        if self.state == "paid" or self.state == "rejected":
            raise exceptions.UserError("Cannot update paid records.")
        
        # If creating then can update anything
        if self.state == "creating":
            return super(ProposePayment, self).write(vals)

        # Only allow update actual expenses
        if'payment_items' in vals and len(vals) == 1:
            return super(ProposePayment, self).write(vals)

        else:
            raise exceptions.UserError("Cannot update submited data.{}".format(vals))
        
    # prevent to delete submited record
    @api.multi
    def unlink(self):
        # For supper user
        # if self.env.user.email == "doanhaibang@rikai.technology":
        #     return super(ProposePayment, self).unlink()

        if self.state != "creating":
            raise exceptions.UserError("Cannot delete submited records.")
        else:
            return super(ProposePayment, self).unlink()

    @api.depends('name')
    def _compute_budget_ids(self):
        for record in self:
            email = self.env.user.email
            record.budget_ids = self.env['rikai.workflow.propose.budget'].search([('payees.email','=', email)])

    @api.depends('payment_department')
    def _compute_payment_company(self):
        for record in self:
            record.payment_company = record.payment_department.company
            record.accountant = record.payment_department.accountant

                
    
    @api.depends('budget')
    def _compute_owner_company(self):
        for record in self:
            record.owner_company = record.budget.company
            record.owner_department = record.budget.department.name
            record.currency = record.budget.currency
    
    @api.depends('payment_items.amount')
    def _compute_amount(self):
        for record in self:
            record.amount = sum(record.payment_items.mapped('amount'))

    @api.depends('amount', 'tax_rate')
    def _compute_tax(self):
        for record in self:
            record.tax_amount = math.ceil(record.amount * (record.tax_rate/100))
            record.total_amount = record.amount + record.tax_amount

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
    def action_payment_request(self):
        for record in self:
            email = record.create_uid.email
            if email != self.env.user.email:
                raise ValidationError("You don't have right to do this action")
                return
            else:
                if record.budget_amount >= record.amount:
                    record.state = "payment_request"
                else:
                    record.state = "creating"
                    record._reset_approver()
    
    @api.multi
    def action_paid(self):
        # Get login user email
        email = self.env.user.email
        for record in self:
            # If login user email is not accountant email then raise Error
            if email != record.accountant.email:
                raise ValidationError("You don't have right to do this action")
                return
            else:
                record.state = "paid"
    
    @api.multi
    def action_return(self):
        for record in self:
            record.state = "creating"
            record._reset_approver()

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

    
    # Reset status of approver
    @api.multi
    def _reset_approver(self):
        for record in self:
            for step in self.propose_steps:
                step.status = "waiting"
                for approver in step.approvers:
                    approver.status = "waiting"
    
    #######COMPUTE SECTION##########
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

class ProposePaymentItems(models.Model):
    _name = 'rikai.workflow.propose.payment.item'
    _description = 'Rikai Payment Items'
    
    # Tên sản phẩm order
    name = fields.Char(
        string="Item",
        required=True,
        copy=False
    )

    # Trong cho đợt thanh toán nào
    payment=fields.Many2one(
        'rikai.workflow.propose.payment', 
        string="Payment"
    )

    # Số lượng
    quantity = fields.Float(
        string="Quantity",
        required=True,
        copy=True
    )

    # Đơn giá
    price = fields.Float(
        string="Price",
        required=True,
        copy=True
    )

    #Tổng số tiền
    amount = fields.Float(
        string="Amount",
        store=True,
        compute="_compute_amount",
    )

    # Đơn vị tiền thanh toán
    currency = fields.Selection(
        [('VND','VND'),('JPY','JPY'),('USD','USD')],
        string="Currency",
        store=True,
        compute="_compute_currency",
    )

    @api.depends('quantity', 'price')
    def _compute_amount(self):
        for record in self:
            record.amount = record.quantity * record.price
    
    @api.depends('payment')
    def _compute_currency(self):
        for record in self:
            record.currency = record.payment.currency if record.payment.currency else None

