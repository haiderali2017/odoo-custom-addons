# -*- coding: utf-8 -*-
# from odoo import http


# class Merchandizer(http.Controller):
#     @http.route('/merchandizer/merchandizer/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/merchandizer/merchandizer/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('merchandizer.listing', {
#             'root': '/merchandizer/merchandizer',
#             'objects': http.request.env['merchandizer.merchandizer'].search([]),
#         })

#     @http.route('/merchandizer/merchandizer/objects/<model("merchandizer.merchandizer"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('merchandizer.object', {
#             'object': obj
#         })
