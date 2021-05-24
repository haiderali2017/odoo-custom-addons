# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime,date
from odoo.exceptions import UserError


class MonthlyPlan(models.Model):
    _name = 'monthly.plan'
    _description = 'monthly plannings'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='draft')
    year = fields.Selection([(str(y), str(y)) for y in range(datetime.now().year, (datetime.now().year) + 11)], string='Year', required=True)
    month = fields.Selection([('1', 'Jan'), ('2', 'Feb'), ('3', 'Mar'),
                              ('4', 'Apr'), ('5', 'May'), ('6', 'Jun'),
                              ('7', 'Jul'), ('8', 'Aug'), ('9', 'Sep'),
                              ('10', 'Oct'), ('11', 'Nov'), ('12', 'Dec')], string='Month', required=True)
    sales_person = fields.Many2one("res.users", string="Sales Person", required=True)
    monthly_plan_id = fields.One2many('monthly.details', 'monthly_plan_details')

    def validate_name_date(self):
        record = self.env['daily.plan']
        domain = [('sales_person', '=', self.sales_person.name)]
        result = record.search(domain)
        for rec1 in result:
            for rec2 in self.monthly_plan_id:
                if (self.sales_person.name == rec1.sales_person) and (rec2.dated == rec1.dated):
                    raise models.ValidationError("%s already exists at %s" % (self.sales_person.name, rec2.dated))

    def check_illegal_branches(self):
        record = self.env['branch.data']
        domain = [('person.name', '=', self.sales_person.name)]
        rec = record.search(domain)
        list1 = [r.name for r in rec]
        list2=[]
        for rec2 in self.monthly_plan_id:
            for branch in rec2.collect_branch:
                list2.append(branch.name)

        if len(list1) < 1:
            raise models.ValidationError("That branch doesn't exist for %s" % (self.sales_person.name))
        else:
            for contents in list2:
                if contents not in list1:
                    raise models.ValidationError("%s doesn't exist for %s" % (contents,self.sales_person.name))

    def unlink(self):
        record = self.env['daily.plan']
        result = record.search([('sales_person', '=', self.sales_person.name)])
        for res in result:
            if res.dated in [check.dated for check in self.monthly_plan_id]:
                record.browse(res.id).unlink()
        return super(MonthlyPlan, self).unlink()

    def approve_button(self):
        self.check_illegal_branches()
        self.validate_name_date()

        unique_date = []
        categ1, categ2 = dict(), dict()
        record1 = self.env['daily.plan']
        record2 = self.env['daily.details']

        for rec in self.monthly_plan_id:
            if rec.dated not in unique_date:
                unique_date.append(rec.dated)

                for data in self: # collecting data from current model
                    categ1['sales_person'] = data.sales_person.name
                categ1['dated'] = rec.dated  # collecting date from tree view
                result = record1.create(categ1)

                for branch in rec.collect_branch: # collecting branches from tree view
                    categ2['branches'] = branch.name
                    categ2['daily_plan_details'] = result.id
                    record2.create(categ2)

                self.state = 'approved'
            else:
                raise models.ValidationError('Duplicate dates exist.')

    def reject_button(self):
        self.state = 'rejected'

    def name_get(self):
        result = []
        for rec in self:
            rec_name = "%s" % (rec.sales_person.name)
            result.append((rec.id, rec_name))
        return result

    @api.constrains('month')
    def month_validation(self):
        year = datetime.now().year
        currentMonth = datetime.now().month
        if int(self.year) == year:
            if int(self.month) < currentMonth:
                raise models.ValidationError('Past month can not selected')


class MonthlyPlanDetails(models.Model):
    _name = 'monthly.details'
    _description = 'monthly plan details'

    dated = fields.Date("Date", required=True)
    collect_branch = fields.Many2many('branch.data', string="Branches", required=True)
    monthly_plan_details = fields.Many2one('monthly.plan', string="Monthly Plan", required=True, ondelete='cascade')

    @api.constrains('dated')
    def _check_date(self):
        now = date.today()  # collecting current date
        for rec in self:
            if rec.dated < now:
                raise models.ValidationError('Enter current date or onwards.')

    @api.constrains('dated')
    def month_validation(self):
        for tree in self:
            final_date = tree.dated
            year = final_date.strftime("%Y")
            month = final_date.strftime("%m")
            for record in self.monthly_plan_details:
                if int(record.month) != int(month) or int(record.year) != int(year):
                    raise UserError("Selected the range according to the above month or year")

class DailyPlan(models.Model):
    _name = 'daily.plan'
    _description = 'daily plan details'

    sales_person = fields.Char("Sales Person", readonly=True, required=True)
    dated = fields.Date("Date", readonly=True, required=True)
    daily_plan_id = fields.One2many('daily.details', 'daily_plan_details')
    state = fields.Selection([('draft', 'Draft')], default='draft')

    def name_get(self):
        result = []
        for form_model in self:
            rec_name = "%s" % (form_model.sales_person)
            result.append((form_model.id, rec_name))
        return result

    def unlink(self):
        for rec in self.daily_plan_id:
            if rec.status == 'red':
                return super(DailyPlan, self).unlink()
            else:
                raise UserError("Cannot delete.")


class DailyPlanDetails(models.Model):
    _name = 'daily.details'
    _description = 'daily details'

    branches = fields.Char("Branches", readonly=True)
    status = fields.Selection([("green", "GREEN"),
                               ("yellow", "YELLOW"),
                               ("red", "RED")], default="green", compute="_compute_finalize", readonly=True)
    inventory = fields.Many2many('ir.attachment', relation="inventory_merchandiser", string="Inventory")
    images = fields.Many2many('ir.attachment', relation="images_merchandiser", string="Images")
    daily_plan_details = fields.Many2one('daily.plan', string="Daily Plan")

    @api.depends('inventory','images')
    def _compute_finalize(self):
        self.status = ""
        for rec in self:
            if (len(rec.inventory) and len(rec.images)) != 0:
                rec.status = 'green'
            elif len(rec.inventory) == 0:
                if len(rec.images) != 0:
                    rec.status = 'yellow'
                else:
                    rec.status = 'red'
            elif len(rec.images) == 0:
                if len(rec.inventory) != 0:
                    rec.status = 'yellow'
                else:
                    rec.status = 'red'
            else:
                rec.status = 'red'


class BranchData(models.Model):
    _name = 'branch.data'
    _description = 'branch assigning details'

    name = fields.Char("Branches", required=True)
    person = fields.Many2one("res.users", string="Sales Person")


    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Branch repetition is not allowed')
    ]

    def name_get(self):
        result = []
        for form_model in self:
            rec_name = "%s - %s" % (form_model.person.name, form_model.name)
            result.append((form_model.id, rec_name))
        return result

