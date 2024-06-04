# -*- coding: utf-8 -*-
{
    'name': "Store Odoo",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "7777",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'application': True,

    # any module necessary for this one to work correctly
    'depends': ['base','mail','calendar', 'contacts'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/almacen.xml',
        'views/cliente.xml',
        'views/inventario.xml',
        'views/pedidos.xml',
        'views/productos.xml',
        'views/ventas.xml',
        'report/bill_report.xml',
        'views/report_template.xml',
        'views/compra_proveedores.xml',
        'views/proveedores.xml',
        'views/balance.xml',
        'views/envios.xml',
        'views/email.xml',
        'views/res_city.xml',
        'views/menus.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
