from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class create_cliente(models.Model):
    _name = 'create.cliente'
    _description = 'Crear Cliente'

    name = fields.Char(string="Nombre De Usuario")
    email = fields.Char(string="Correo Electronico")
    is_proveedor = fields.Selection([("a","Proveedor"),("b","Cliente")], string='Tipo De Usuario', required=True)
    Type_proveedor = fields.Many2many('create.productos', string="Productos Que Provee")
    

class create_productos(models.Model):
    _name = 'create.productos'
    _description = 'Crear Productos'

    name = fields.Char(string="Nombre de Producto")
    image_1920 = fields.Image(string="image")
    price = fields.Integer(string="Precio de Producto")
    cost = fields.Integer(string="Costo de Producto")
    proveedores_id = fields.Many2many('create.cliente', string="Proveedor")
    
    
    @api.model
    def create(self, vals):
        record = super(create_productos, self).create(vals)
        crear = self.env['gestion.inventario'].create({'product_id': record.id})
        return record
    
    
class create_almacenes(models.Model):
    _name = 'create.almacenes'
    _description = 'Crear Almacenes'
    
    name = fields.Char(string="Nombre de Bodega")
    
    
class gestion_inventario(models.Model):
    _name = 'gestion.inventario'
    _description = 'Gestión de Inventario'
    
    product_id = fields.Many2one('create.productos', string="Producto")
    amount = fields.Integer(string="Cantidad", readonly=True)
    store_id = fields.Many2one('create.almacenes', string="Almacén de Producto")
        
        
class producto_ventas(models.Model):
    _name = 'producto.ventas' 
    _description = 'Ventas de Producto'
    
    stored_product = fields.Many2one('create.productos', string="Producto")
    product_id = fields.Many2one('pedidos.venta', string="Producto")      
    price = fields.Integer(related='stored_product.price',  required=True)
    sales_amount = fields.Integer(string="Cantidad de Producto", required=True)
    discount = fields.Float(string="Descuento aplicado")
    total = fields.Integer(string="Valor Total", compute="_compute_valor_linea", store="True")
    
    @api.depends('price', 'sales_amount', 'discount')
    def _compute_valor_linea(self):
        for record in self:
            valor_total = record.price * record.sales_amount
            descuento = record.discount / 100
            if record.discount > 0:
                precio_final = valor_total - (valor_total * descuento)
                record['total'] = precio_final
            else:
                record['total'] = valor_total
                    
           
                
  
    
class pedidos_venta(models.Model):    
    _name = 'pedidos.venta' 
    _description = 'Pedidos de Venta'
    
    state = fields.Selection([("cancelled","Cancelado"), ("procces","En Proceso"), ("finalized", "Finalizado")], string="Estado",  default="procces", store=True)
    name = fields.Char(string="Código de Pedido", store="True")
    products_ids = fields.One2many('producto.ventas', 'product_id', store=True, string="Productos")
    store_id = fields.Many2one('create.almacenes', string="Almacén Asociado", required=True)
    cliente_id = fields.Many2one('create.cliente', string="Cliente", domain="[('is_proveedor', '=', 'b')]", required=True)
    date_pedido = fields.Date(string='fecha', default=datetime.today())
    discount_total = fields.Float(string="Descuento Aplicado")
    price_total = fields.Integer(string="Total", store=True, compute="valor_total")
    orders = fields.Many2one('envios.sales', string="envios asociados")
    iva = fields.Integer(string="19% Iva", compute="valor_iva", store=True)
    email_user = fields.Char(related='cliente_id.email', string="Correo Electonico")

    _sql_constraints = [
        ('cod_unique', 'UNIQUE(name)', 'Ya existe un pedido registrado con este numero'),
    ]
        
        
    @api.model
    def create(self, vals):
        record = super(pedidos_venta,self).create(vals) 
        record.name = 'T000' + str(record.id)  
        
        return record 
    
    @api.depends('products_ids', 'discount_total')
    def valor_total(self):
        for record in self:
            suma_total = 0
            lista = record.products_ids.mapped('total') 
            if lista:
                suma_total = sum(lista)
                descuento = record.discount_total / 100
                if record.discount_total > 0:
                    precio_final = suma_total - (suma_total * descuento)
                    record['price_total'] = precio_final
                    
                    
                else:    
                    record['price_total'] = suma_total
            # record.price_total = suma_total
            
    @api.depends('price_total')     
    def valor_iva(self): 
         for record in self:
            iva = 0.19
            resultado = record.price_total * 1
            final = (resultado * 19) / 100
            record.iva = final + record.price_total        


    def confirma_pago(self):
        for order in self:
            for line in order.products_ids:
                qty_sold = line.sales_amount
                if qty_sold > 0:
                    inventario = self.env['gestion.inventario'].search([
                        ('product_id', '=', line.stored_product.id),
                        ('store_id', '=', order.store_id.id)
                    ], limit=1)
                    if inventario.amount >= qty_sold:
                        inventario.amount -= qty_sold
                    else:
                        raise ValidationError(f'No hay Suficientes {inventario.product_id.name} cantidad existente {inventario.amount} Unidades')


                    order['state'] = 'finalized'
        
            money = self.env['balance.money'].search([('date', '=', order.date_pedido)])
            for retur in money:
                retur.stored += order.iva
            if not money:
                self.env['balance.money'].create({
                    'date': order.date_pedido,
                    'stored': order.iva,
                })
                    
                       
                
            
        
    

    
    def impri_factura(self):
        datas = {
            'id': self.id,
            'model': 'odoo_prueba.template_pedidos_ventas',
        }
        
        return {
            'type':'ir.actions.report',
            'report_name':'odoo_prueba.template_pedidos_ventas',
            'report_type':'qweb-pdf',
            'datas':datas,
            
        }
        
    def devolver_pediddo(self):
        for order in self:
            for line in order.products_ids:
                qty_sold = line.sales_amount
                if qty_sold > 0:
                    inventario = self.env['gestion.inventario'].search([
                        ('product_id', '=', line.stored_product.id),
                        ('store_id', '=', order.store_id.id)
                    ], limit=1)
                    if inventario:
                        inventario.amount += qty_sold
                        
                    order['state'] = 'cancelled'
                    for record in self:
                        cancell = self.env['envios.sales'].search([('cod_sales', '=', record.name)])
                        for lines in cancell:
                            lines['state'] = 'failed'

                                
                    

            money = self.env['balance.money'].search([])
            for retur in money:
                retur.stored -= order.iva
                
                
                        
  
    def env_email(self):
        raise ValidationError('mensaje')        
        
class compra_proveedores(models.Model):
    _name = 'compra.proveedores' 
    _description = 'compra proveedores'
    
    stored_product = fields.Many2one('create.productos', string="Producto")
    product_sales_id = fields.Many2one('provedores.store', string="Producto Vendido")      
    cost = fields.Integer(related='stored_product.cost',  required=True)
    sales_amount = fields.Integer(string="Cantidad de Producto", required=True)
    total = fields.Integer(string="Valor Total", compute="_compute_cost_linea", store="True")
    
    @api.depends('cost', 'sales_amount')
    def _compute_cost_linea(self):
        for record in self:
            record.total = record.cost * record.sales_amount 
      
      
            
        
class provedores_store(models.Model):
    _name = 'provedores.store' 
    _description = 'Proveedores'
    
    state = fields.Selection([("cancelled","Cancelado"), ("procces","En Proceso"), ("finalized", "Finalizado")], string="Estado",  default="procces")
    num_order = fields.Char(string="Código de Pedido", store="True")
    date_pedido = fields.Date(string='fecha', default=datetime.today())
    products_ids = fields.One2many('compra.proveedores', 'product_sales_id', store=True, string="Productos Vendidos")
    store_id = fields.Many2one('create.almacenes', string="Almacén Asociado", required=True)
    proveedor_id = fields.Many2one('create.cliente', string="Proveedor", domain="[('is_proveedor', '=', 'a')]", required=True)
    cost_total = fields.Integer(string="Total", store="True", compute="compute_cost_total")
    iva = fields.Integer(string="+ 19% Iva", compute="cost_iva")
    
    
    @api.model
    def create(self, vals):
        record = super(provedores_store,self).create(vals) 
        record.num_order = 'C000' + str(record.id)  
        
        return record
    
    @api.depends('products_ids')
    def compute_cost_total(self):
        for record in self:
            suma_total = 0
            lista = record.products_ids.mapped('total') 
            if lista:
                suma_total = sum(lista)
            record.cost_total = suma_total
    
    
    @api.depends('cost_total')     
    def cost_iva(self): 
         for record in self:
            iva = 0.19
            resultado = record.cost_total * 1
            final = (resultado * 19) / 100
            record.iva = final + record.cost_total   
            
            
    def proveedores_pago(self):
        for order in self:
            sold_qty_dict = {}
            for line in order.products_ids:
                qty_sold = line.sales_amount
                if qty_sold > 0:
                    if line.stored_product.id in sold_qty_dict:
                        sold_qty_dict[line.stored_product.id] += qty_sold
                    else:
                        sold_qty_dict[line.stored_product.id] = qty_sold
            for product_id, qty_sold in sold_qty_dict.items():
                inventario = self.env['gestion.inventario'].search([
                    ('product_id', '=', product_id),
                    ('store_id', '=', order.store_id.id)
                ], limit=1)
                if inventario:
                    inventario.amount += qty_sold
                
          
            money = self.env['balance.money'].search([('date', '=', order.date_pedido)])
            for retur in money:
                retur.invested += order.iva
            if not money:
                self.env['balance.money'].create({
                    'date': order.date_pedido,
                    'invested': order.iva,
                })    
                
                
            order['state'] = 'finalized'   
                    
                            
    def cancela_compra(self):
        for order in self:
            for line in order.products_ids:
                qty_sold = line.sales_amount
                if qty_sold > 0:
                    inventario = self.env['gestion.inventario'].search([
                        ('product_id', '=', line.stored_product.id),
                        ('store_id', '=', order.store_id.id)
                    ], limit=1)
                    if inventario:
                        inventario.amount -= qty_sold
                        
            money = self.env['balance.money'].search([])
            for retur in money:
                retur.invested -= order.iva            
                        
            order['state'] = "cancelled"
            
            
                         
            
class balance_money(models.Model):
    _name = 'balance.money'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'balance money'
    
    
    date = fields.Date(string="Fecha", readonly=True)
    stored = fields.Integer(string="Dinero De venta", readonly=True, tracking=True)
    invested = fields.Integer(string="Dinero De Inversion", readonly=True, tracking=True)
    revenue = fields.Integer(string="Ganancias", compute="ganancias_renue", tracking=True)
    
    
    
    
    
                
    @api.depends('stored', 'invested')
    def ganancias_renue(self):
        for record in self:
            ganancias = record.stored - record.invested
            iva = ganancias * 0.19
            if ganancias > 0:
                sin_impuestos = ganancias - iva
                record['revenue'] = sin_impuestos
            else:
                sin_impuestos = record.stored - record.invested
                record['revenue'] = sin_impuestos
                    
            
            
            
class envios_sales(models.Model):
    _name = 'envios.sales'
    __description = 'enios sales'
    
    state = fields.Selection([("delivered","Entregado"), ("procces","En Proceso"), ("failed", "Cancelado")], string="Estado de Envio",  default="procces")
    date_start = fields.Date(string="Fecha De Entrega")
    cod_sales = fields.Many2one('pedidos.venta', string="Numero de venta Asociado", required=True, domain="[('state', '=', 'finalized')]")
    bill_associated = fields.Many2many('pedidos.venta', string="Pedido", compute="factured")
    address = fields.Many2one('res.country', string="Direccion")
    value = fields.Integer(string="Valor de envio")
    driver = fields.Many2one('hr.employee.public', string="Conductor Asociado")
     
    @api.onchange('cod_sales') 
    def factured(self):
        for record in self:
            if record.cod_sales:
                record.bill_associated = [(4,record.cod_sales.id)]
                
                
    def delivered(self):
        for record in self:
            record['state'] = 'delivered'
              
                            
                            
                            
