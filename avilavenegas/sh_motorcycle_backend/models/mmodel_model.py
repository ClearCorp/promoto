# -*- coding: utf-8 -*-

from odoo import models, fields


class motorcycle_mmodel(models.Model):
    _name = "motorcycle.mmodel"
    _description = "mmodel."
    _order = "id desc"

    name = fields.Char(string="Name", required=True)
    displacement = fields.Char(string="Displacement")
    nicknames = fields.Char(string="Nicknames")
    standard_name = fields.Char(string="Standard Name")
    make_id = fields.Many2one(comodel_name="motorcycle.make",
                              string="Marca", required=True)
    type_id = fields.Many2one(comodel_name="motorcycle.type",
                              string="Tipo", required=True)
