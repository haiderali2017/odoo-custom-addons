# -*- coding: utf-8 -*-
from datetime import datetime,date

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _

class Loans(models.Model):
    _name = 'manage.loans'
    _description = 'managing loans'
    # custom fields

    # name = fields.Char('Say')
    requester = fields.Many2one('res.users', string='Requester', default=lambda self: self.env.user, readonly=True)
    description = fields.Text('Description')
    date = fields.Date("Installment Date", required=True)
    date2 = fields.Date("Date")
    payment_type = fields.Selection(
        [('installment_no', 'Installment Number'),
         ('installment_amount', 'Installment Amount'),
         ],
        string="Payment Type",
        default="installment_no"
    )
    job_position = fields.Char("Job Position", related='employees.job_title')
    department = fields.Many2one("hr.department", "Department", related='employees.department_id')
    loan_amount = fields.Integer("Loan amount")
    employees = fields.Many2one('hr.employee', string="Employee", required=True)
    rel_loan_acc = fields.Many2one('account.payment', string="Memo", readonly=True, copy=False)
    installment_amt = fields.Float("Installment amount")
    installment_no = fields.Float("Installment number")
    rel_installment = fields.One2many('manage.installments', 'installments_id', string="Installments management")
    SELECTIONS = [('draft', 'Draft'),
                  ('to_submit', 'To Submit'),
                  ('in_process', 'In Process'),
                  ('approved', 'Approved'),
                  ('paid', 'Paid'),
                  ('posted', 'Posted'),
                  ('cancelled', 'Cancelled')
                  ]
    state = fields.Selection(SELECTIONS, default='draft')
    rel_loan_type = fields.Many2one('manage.loantypes', string='Loan Type')
    forward_next_month = fields.Integer('Forward months')

    # code chunk to prepare dictionary for create method - frequently used in installment number scenario
    def installment_number_chunk(self, category, record, amount, date_object):
        category['amount'] = amount
        category['installments_id'] = record.id
        category['loan_ref'] = "%s-%s" % (record.date, record.id)
        category['description'] = record.description
        category['payment_date'] = date_object
        category['status'] = "pending"
        category['emp_name'] = record.employees.name
        record1 = self.env['manage.installments'].create(category)

    # 9 buttons
    def to_submit(self):
        for change in self:
            change.state = 'to_submit'

        category = dict()
        for record in self:
            now = record.date   # collecting installment date
            year = now.strftime("%Y")   # collecting YEAR from installment date
            month = now.strftime("%m") # collecting MONTH from installment date
            date_part = now.strftime("%d") # collecting DATE from installment date
            month_change = int(month) # type casting
            if record.installment_amt: # if user enters installment amount
                loan_entries = record.loan_amount / record.installment_amt # calculate entries to be generated in tree
                remaining = loan_entries - int(loan_entries)
                for i in range(int(loan_entries)):
                    if month_change <= 12:
                        combine_date = date_part + "/" + str(month_change) + "/" + year
                        date_object = datetime.strptime(combine_date, "%d/%m/%Y")
                        month_change += 1
                    elif month_change > 12:
                        month_change = 1
                        yearchange = int(year) + 1
                        year = str(yearchange)
                        combine_date = date_part + "/" + str(month_change) + "/" + year
                        date_object = datetime.strptime(combine_date, "%d/%m/%Y")
                        month_change += 1
                    category['amount'] = record.installment_amt
                    category['installments_id'] = record.id
                    category['loan_ref'] = "%s-%s" % (record.date, record.id)
                    category['description'] = record.description
                    category['payment_date'] = date_object # using date from date_increment_chunk function
                    category['status'] = "pending"
                    category['emp_name'] = record.employees.name
                    record1 = self.env['manage.installments'].create(category)
                    # month_change += 1
                else:
                    if month_change <= 12:
                        combine_date = date_part + "/" + str(month_change) + "/" + year
                        date_object = datetime.strptime(combine_date, "%d/%m/%Y")
                        month_change += 1
                    elif month_change > 12:
                        month_change = 1
                        yearchange = int(year) + 1
                        year = str(yearchange)
                        combine_date = date_part + "/" + str(month_change) + "/" + year
                        date_object = datetime.strptime(combine_date, "%d/%m/%Y")
                        month_change += 1
                    category['amount'] = record.installment_amt*remaining
                    category['installments_id'] = record.id
                    category['loan_ref'] = "%s-%s" % (record.date, record.id)
                    category['description'] = record.description
                    category['payment_date'] = date_object  # using date from date_increment_chunk function
                    category['status'] = "pending"
                    category['emp_name'] = record.employees.name
                    record1 = self.env['manage.installments'].create(category)
            elif record.installment_no: # if user enters installment number
                installment_amount = record.loan_amount / record.installment_no # calculate installment amount
                for i in range(1,int(record.installment_no)+1):
                    if month_change <= 12:
                        combine_date = date_part + "/" + str(month_change) + "/" + year
                        date_object = datetime.strptime(combine_date, "%d/%m/%Y")
                        month_change += 1
                    elif month_change > 12:
                        month_change = 1
                        yearchange = int(year) + 1
                        year = str(yearchange)
                        combine_date = date_part + "/" + str(month_change) + "/" + year
                        date_object = datetime.strptime(combine_date, "%d/%m/%Y")
                        month_change += 1
                    self.installment_number_chunk(category, record, installment_amount, date_object) # using date from date_increment_chunk function
                    # month_change += 1

    def in_progress(self):
        for change in self:
            change.state = 'in_process'

    def reject(self):
        for change in self:
            change.state = 'to_submit'

    def approve(self):
        for change in self:
            change.state = 'approved'

    def register_payment(self):
        category=dict()
        for record in self:
            category['partner_name'] = record.employees.name
            category['payment_amount'] = record.loan_amount
            category['memo'] = "%s-%s" % (record.date, record.id)
            # category['rel_acc_loan'] = record.rel_loan_acc.id
            category['payment_date'] = record.date
            record2 = self.env['account.payment'].create(category)
            self.rel_loan_acc = record2
        for change in self:
            change.state = 'paid'

    def forward1(self):
        category=dict()
        if not self.forward_next_month < 1:
            largest_date = max([rec.payment_date for rec in self.rel_installment])
            if self.installment_no:  # if user enters installment amount
                now = self.date  # collecting installment date
                year = now.strftime("%Y")  # collecting YEAR from installment date
                month = now.strftime("%m")  # collecting MONTH from installment date
                date_part = now.strftime("%d")  # collecting DATE from installment date
                month_change = int(month)
                for i in range(self.forward_next_month): # Holding installments
                    if month_change > 12:
                        month_change = 1
                        yearchange=int(year) + 1
                        year = yearchange
                    date_object = date(int(year),month_change,int(date_part))
                    for rec in self.rel_installment:
                        if date_object == rec.payment_date:
                            rec.status = 'hold'
                    month_change += 1

                year = largest_date.strftime("%Y")  # collecting YEAR from installment date
                month = largest_date.strftime("%m")  # collecting MONTH from installment date
                date_part = largest_date.strftime("%d")  # collecting DATE from installment date
                month_change = int(month)
                month_change += 1
                for i in range(self.forward_next_month): # Creating more installments
                    if month_change <= 12:
                        combine_date = date_part + "/" + str(month_change) + "/" + year
                        date_object = datetime.strptime(combine_date, "%d/%m/%Y")
                        month_change += 1
                    elif month_change > 12:
                        month_change = 1
                        yearchange = int(year) + 1
                        year = str(yearchange)
                        combine_date = date_part + "/" + str(month_change) + "/" + year
                        date_object = datetime.strptime(combine_date, "%d/%m/%Y")
                        month_change += 1
                    installment_amount = self.loan_amount / self.installment_no  # calculate installment amount
                    category['amount'] = installment_amount
                    category['installments_id'] = self.id
                    category['loan_ref'] = "%s-%s" % (self.date, self.id)
                    category['description'] = self.description
                    category['payment_date'] = date_object
                    category['status'] = "pending"
                    category['emp_name'] = self.employees.name
                    record1 = self.env['manage.installments'].create(category)
                for change in self:
                    change.state = 'paid'
            elif self.installment_amt:
                now = self.date  # collecting installment date
                year = now.strftime("%Y")  # collecting YEAR from installment date
                month = now.strftime("%m")  # collecting MONTH from installment date
                date_part = now.strftime("%d")  # collecting DATE from installment date
                month_change = int(month)
                for i in range(self.forward_next_month):  # Holding installments
                    if month_change > 12:
                        month_change = 1
                        yearchange = int(year) + 1
                        year = yearchange
                    date_object = date(int(year), month_change, int(date_part))
                    for rec in self.rel_installment:
                        if date_object == rec.payment_date:
                            rec.status = 'hold'
                    month_change += 1

                year = largest_date.strftime("%Y")  # collecting YEAR from installment date
                month = largest_date.strftime("%m")  # collecting MONTH from installment date
                date_part = largest_date.strftime("%d")  # collecting DATE from installment date
                month_change = int(month)
                month_change += 1
                for i in range(self.forward_next_month):  # Creating more installments
                    if month_change <= 12:
                        combine_date = date_part + "/" + str(month_change) + "/" + year
                        date_object = datetime.strptime(combine_date, "%d/%m/%Y")
                        month_change += 1
                    elif month_change > 12:
                        month_change = 1
                        yearchange = int(year) + 1
                        year = str(yearchange)
                        combine_date = date_part + "/" + str(month_change) + "/" + year
                        date_object = datetime.strptime(combine_date, "%d/%m/%Y")
                        month_change += 1
                    category['amount'] = self.installment_amt
                    category['installments_id'] = self.id
                    category['loan_ref'] = "%s-%s" % (self.date, self.id)
                    category['description'] = self.description
                    category['payment_date'] = date_object
                    category['status'] = "pending"
                    category['emp_name'] = self.employees.name
                    record1 = self.env['manage.installments'].create(category)
        else:
            msg = _("Enter a positive integer")
            raise UserError(msg)

    def forward2(self):
        pass
        # for change in self:
        #     change.state = 'post'

    def post_journal(self):
        for change in self:
            change.state = 'posted'

    def paid(self):
        for change in self:
            change.state = 'to_approve'

    def cancelled(self):
        for change in self:
            change.state = 'cancelled'

    def name_get(self):
        result = []
        for rec in self:
            if rec.requester and rec.date:
                rec_name = "%s - %s" % (rec.employees.name, rec.date)
                result.append((rec.id, rec_name))
        return result

class Installments(models.Model):
    _name = 'manage.installments'
    _description = 'manage installments'
    _order = 'payment_date desc'
    installments_id = fields.Many2one('manage.loans', string="Installments")
    amount = fields.Float('Amount')
    status = fields.Selection(
        [('paid', 'Paid'),
        ('pending', 'Pending'),
        ('hold', 'Hold')
         ],
        string="Status",
        default="pending"
    )
    description = fields.Text('Description')
    loan_ref = fields.Char('Loan Ref.')
    emp_name = fields.Char('Employee')
    payment_date = fields.Date('Date')

class LoanType(models.Model):
    _name = 'manage.loantypes'
    _description = 'manage loan types'
    name = fields.Char("Loan Type")

class AccountPayment(models.Model):
    _name = 'account.payment'
    _description = 'manage acount payments'
    partner_name = fields.Char('Partner')
    payment_amount = fields.Float('Payment Amount')
    payment_date = fields.Date('Payment Amount')
    memo = fields.Char('Memo')
