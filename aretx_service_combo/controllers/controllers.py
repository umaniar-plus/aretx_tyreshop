# -*- coding: utf-8 -*-
# from odoo import http


# class ServiceCombo(http.Controller):
#     @http.route('/service_combo/service_combo', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/service_combo/service_combo/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('service_combo.listing', {
#             'root': '/service_combo/service_combo',
#             'objects': http.request.env['service_combo.service_combo'].search([]),
#         })

#     @http.route('/service_combo/service_combo/objects/<model("service_combo.service_combo"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('service_combo.object', {
#             'object': obj
#         })
