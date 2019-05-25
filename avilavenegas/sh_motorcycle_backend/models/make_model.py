# -*- coding: utf-8 -*-

from odoo import models, fields


class motorcycle_make(models.Model):
    _name = "motorcycle.make"
    _description = 'make model.'
    _order = 'id desc'

    name = fields.Char(string="Name", required=True)
