# -*- coding: utf-8 -*-
from odoo import fields, models, api
class Partner(models.Model):
    _inherit = 'res.partner'
    _description = 'Partner'
    
    # Add a new column to the res.partner model, by default partners are not instructors
    instructor = fields.Boolean("Instructor", default=False)

    session_ids = fields.Many2many('openacademy.session',
                                   string="Attended Sessions", readonly=True)

    session_count = fields.Integer(compute="_compute_session_count")

    @api.depends('session_ids')
    def _compute_session_count(self):
        for partner in self:
            partner.session_count = len(partner.session_ids)

    @api.depends('category_id', 'category_id.name')
    def _get_level(self):
        for partner in self:
            level = []
            for categ in partner.category_id:
                if "Chain Level" in categ.name:
                    level.append(int(categ.name.split(' ')[-1]))
            partner.level = max(level) if level else 0
