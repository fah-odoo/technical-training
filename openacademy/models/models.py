# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models


class openacademy(models.Model):
    _name = 'openacademy.openacademy'

    name = fields.Char()

class Course(models.Model):
    _name = 'openacademy.course'

    name = fields.Char(string="Title", required=True)
    description = fields.Text()

    # There can be several people responsible for a course
    responsible_id = fields.Many2one('res.users',
                                     ondelete='set null', string="Responsible", index=True)

    # course_id corresponds to session_ids                                 
    session_ids=fields.One2many('openacademy.session', 'course_id', string="Sessions")

    level = fields.Selection(
        [(1, 'Easy'), (2, 'Medium'), (3, 'Hard')], string="Difficulty Level")

class Session(models.Model):
    _name = 'openacademy.session'

    name = fields.Char(required=True)
    start_date = fields.Date()
    duration = fields.Float(digits=(6, 2), help="Duration in days")
    seats = fields.Integer(string="Number of seats")

    archive = fields.Boolean(default=False)
    # One instructor can teach several course sessions
    
    # instructor is set to True OR the name contains (case insensitive) "teacher"
    instructor_id = fields.Many2one('res.partner', string="Instructor",
                                    domain=['|', ('instructor', '=', True),
                                            ('category_id.name', 'ilike', "Teacher")])


    state = fields.Selection([('draft', "Draft"), ('confirmed', "Confirmed"), ('done', "Done")], default='draft')
    
    # There can be several sessions of a course
    course_id = fields.Many2one('openacademy.course',
                                ondelete='cascade', string="Course", required=True)

    # There can be several attendees for a course session. There can be several course sessions for an attendee.                            
    attendee_ids = fields.Many2many('res.partner', string="Attendees")
