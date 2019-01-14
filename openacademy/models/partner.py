# -*- coding: utf-8 -*-
from odoo import fields, models, api


class Partner(models.Model):
    _inherit = 'res.partner'

    #no _name!
    # Add a new column to the res.partner model, by default partners are not instructors
    instructor = fields.Boolean("Instructor", default=False)

    session_ids = fields.Many2many('openacademy.session',
                                   string="Attended Sessions", readonly=True)

    session_count = fields.Integer(compute="_compute_session_count")

    @api.depends('session_ids')
    def _compute_session_count(self):
        for partner in self:
            partner.session_count = len(partner.session_ids)
