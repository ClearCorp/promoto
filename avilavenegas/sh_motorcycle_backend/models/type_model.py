# -*- coding: utf-8 -*-

from odoo import models, fields


class motorcycle_type(models.Model):
    _name = "motorcycle.type"
    _description = "type model."
    _order = "id desc"

    name = fields.Char(string="Name", required=True)
