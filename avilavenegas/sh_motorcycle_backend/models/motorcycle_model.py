# -*- coding: utf-8 -*-

from odoo import fields, models, api


class motorcycle_motorcycle(models.Model):
    _name = "motorcycle.motorcycle"
    _description = "Motorcycle"
    _order = "id desc"

    name = fields.Char(string="Name", compute="_get_complete_name")
    year_id = fields.Many2one(comodel_name="motorcycle.year",
                              string="Año", required=True)
    mmodel_id = fields.Many2one(comodel_name="motorcycle.mmodel",
                                string="Modelo", required=True)
    type_id = fields.Many2one(comodel_name="motorcycle.type",
                              string="Tipo",
                              related="mmodel_id.type_id",
                              store=True
                              )
    make_id = fields.Many2one(comodel_name="motorcycle.make",
                              string="Marca",
                              related="mmodel_id.make_id",
                              store=True
                              )
    product_ids = fields.Many2many('product.product',
                                   'product_product_motorcycle_motorcycle_rel',
                                   'motorcycle_id', 'product_id',
                                   string='Products', copy=True)

    @api.multi
    def _get_complete_name(self):
        if self:
            for rec in self:
                name = ''
                if rec.make_id:
                    name += rec.make_id.name + ' '
                if rec.mmodel_id:
                    name += rec.mmodel_id.name + ' '
                if rec.year_id:
                    name += rec.year_id.name
                if name == '':
                    name = False
                rec.name = name
