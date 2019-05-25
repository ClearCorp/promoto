# -*- coding: utf-8 -*-


from odoo import models, fields


class motorcycle_year(models.Model):
    _name = "motorcycle.year"
    _description = "year."
    _order = "id desc"

    name = fields.Char(string="Name", required=True)
