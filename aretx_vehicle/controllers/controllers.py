# -*- coding: utf-8 -*-
# from odoo import http


# class Vehicle(http.Controller):
#     @http.route('/vehicle/vehicle', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vehicle/vehicle/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('vehicle.listing', {
#             'root': '/vehicle/vehicle',
#             'objects': http.request.env['vehicle.vehicle'].search([]),
#         })

#     @http.route('/vehicle/vehicle/objects/<model("vehicle.vehicle"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vehicle.object', {
#             'object': obj
#         })
