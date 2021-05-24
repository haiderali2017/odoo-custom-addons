# -*- coding: utf-8 -*-
# from odoo import http


# class JobRecruitment(http.Controller):
#     @http.route('/job_recruitment/job_recruitment/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/job_recruitment/job_recruitment/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('job_recruitment.listing', {
#             'root': '/job_recruitment/job_recruitment',
#             'objects': http.request.env['job_recruitment.job_recruitment'].search([]),
#         })

#     @http.route('/job_recruitment/job_recruitment/objects/<model("job_recruitment.job_recruitment"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('job_recruitment.object', {
#             'object': obj
#         })
