# -*- coding: utf-8 -*-
# from odoo import http


# class OdooPrueba(http.Controller):
#     @http.route('/odoo_prueba/odoo_prueba/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/odoo_prueba/odoo_prueba/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('odoo_prueba.listing', {
#             'root': '/odoo_prueba/odoo_prueba',
#             'objects': http.request.env['odoo_prueba.odoo_prueba'].search([]),
#         })

#     @http.route('/odoo_prueba/odoo_prueba/objects/<model("odoo_prueba.odoo_prueba"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('odoo_prueba.object', {
#             'object': obj
#         })
