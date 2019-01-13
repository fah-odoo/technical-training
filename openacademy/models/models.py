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

    # The start date is today if not specified
    start_date = fields.Date(default=fields.Date.today)
    duration = fields.Float(digits=(6, 2), help="Duration in days")
    seats = fields.Integer(string="Number of seats")

    # Sessions are active (not archived) by default
    active = fields.Boolean(default=True)
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

    taken_seats = fields.Float(string="Taken seats", compute='_taken_seats')

    @api.depends('seats', 'attendee_ids')
    def _taken_seats(self):
        for r in self:
            if not r.seats:
                r.taken_seats = 0.0
            else:
                r.taken_seats = 100.0 * len(r.attendee_ids) / r.seats

    @api.onchange('seats', 'attendee_ids')
    def _verify_valid_seats(self):
        if self.seats < 0:
            return {
                'warning': {
                    'title': "Incorrect 'seats' value",
                    'message': "The number of available seats may not be negative",
                },
            }
        if self.seats < len(self.attendee_ids):
            return {
                'warning': {
                    'title': "Too many attendees",
                    'message': "Increase seats or remove excess attendees",
                },
            }

    @api.onchange('seats', 'attendee_ids')
    def _change_taken_seats(self):
        if self.taken_seats > 100:
            return {'warning': {
                'title':   'Too many attendees',
                'message': 'The room has %s available seats and there is %s attendees registered' % (self.seats, len(self.attendee_ids))
            }}
