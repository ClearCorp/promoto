# -*- coding: utf-8 -*-


from odoo import fields, models


class product_product(models.Model):
    _inherit = "product.product"

    motorcycle_ids = fields.Many2many('motorcycle.motorcycle',
                                      'product_product_motorcycle_motorcycle_rel',
                                      'product_id', 'motorcycle_id',
                                      string='Motorcyle', copy=True)
