# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _


class JobRecruitment(models.Model):
    _name = 'job.recruitment'
    _description = 'extension to recruitment module'

    # _rec_name = 'short_name'
    # short_name = fields.Char('Short title', required=True)
    requested_on = fields.Date('Requested On', required=True)
    users = fields.Many2one('res.users', string='Users', default=lambda self: self.env.user, readonly=True)
    SELECTIONS = [('new', 'New'),
                  ('to_approve', 'To Approve'),
                  ('approved', 'Approved'),
                  ('create_job_pos', 'Created Job Position'),
                  ('reject', 'Rejected')]
    state = fields.Selection(SELECTIONS, default='new')
    jobs = fields.One2many('recruitment.data', 'sub_jobs')

    def submit_new(self):
        for change in self:
            change.state = 'to_approve'

    def approve(self):
        for change in self:
            change.state = 'approved'

    def create_pos(self):
        for change in self:
            change.state = 'create_job_pos'

        category = dict()
        for line in self.jobs:
            category['name'] = line.name
            category['department_id'] = line.dept.id
            category['no_of_recruitment'] = line.new_employees
            category['description'] = line.description
            category['user_id'] = self.users.id
            record = self.env['hr.job'].create(category)


    def reject(self):
        for change in self:
            change.state = 'reject'

    def name_get(self):
        result = []
        for record in self:
            if record.users and record.requested_on:
                rec_name = "%s (%s)" % (record.users.name, record.requested_on)
                result.append((record.id, rec_name))
        return result

class RecruitmentData(models.Model):
    _name = 'recruitment.data'
    _description = 'job recruitment module data'

    name = fields.Char('Job Position', required=True)
    description = fields.Text('Description')
    dept = fields.Many2one('hr.department', string='Department', required=True, ondelete='restrict')
    new_employees = fields.Integer('New Employees', required=True)
    sub_jobs = fields.Many2one('job.recruitment')

    @api.constrains('new_employees')
    def _check_employee_count(self):
        for emp in self:
            if emp.new_employees < 1:
                raise models.ValidationError('Employees must be greater than 0')