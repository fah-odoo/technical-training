# -*- coding: utf-8 -*-

# exceptions is for constrains()
from odoo import api, exceptions, fields, models


class openacademy(models.Model):
    _name = 'openacademy.openacademy'

    name = fields.Char()

class Course(models.Model):
    _name = 'openacademy.course'

    name = fields.Char(string="Title", required=True)
    description = fields.Text()

    # One person can be responsible for several courses
    responsible_id = fields.Many2one('res.users',
                                     ondelete='set null', string="Responsible", index=True)

    # course_id corresponds to session_ids                                 
    session_ids=fields.One2many('openacademy.session', 'course_id', string="Sessions")

    # Number of sessions for a course
    session_count = fields.Integer(compute="_compute_session_count")

    @api.depends('session_ids')
    def _compute_session_count(self):
        for course in self:
            course.session_count = len(course.session_ids)


    level = fields.Selection(
        [(1, 'Easy'), (2, 'Medium'), (3, 'Hard')], string="Difficulty Level")

    # To create a "copy" of a course
    @api.multi
    def copy(self, default=None):
        default = dict(default or {})

        copied_count = self.search_count(
            [('name', '=like', u"Copy of {}%".format(self.name))])
        if not copied_count:
            new_name = u"Copy of {}".format(self.name)
        else:
            new_name = u"Copy of {} ({})".format(self.name, copied_count)

        default['name'] = new_name
        return super(Course, self).copy(default)

    # Forbidding course duplicates
    _sql_constraints = [
        ('name_description_check',
         'CHECK(name != description)',
         "The title of the course should not be the description"),

        ('name_unique',
         'UNIQUE(name)',
         "The course title must be unique"),
    ]

class Session(models.Model):
    _name = 'openacademy.session'

    name = fields.Char(required=True)

    # The start date is today if not specified
    start_date = fields.Date(default=fields.Date.today)
    duration = fields.Float(digits=(6, 2), help="Duration in days")
    end_date = fields.Date(default=fields.Date.today)

    seats = fields.Integer(string="Number of seats")

    level = fields.Selection(related='course_id.level', readonly=True)


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

    taken_seats = fields.Float(string="Taken seats", compute='_taken_seats', store='True')

    # maximum seats using depends
    @api.depends('seats', 'attendee_ids')
    def _taken_seats(self):
        for r in self:
            if not r.seats:
                r.taken_seats = 0.0
            else:
                r.taken_seats = 100.0 * len(r.attendee_ids) / r.seats

    # maximum seats using onchange
    @api.onchange('seats', 'attendee_ids')
    def _change_taken_seats(self):
        if self.taken_seats > 100:
            return {'warning': {
                'title':   'Too many attendees',
                'message': 'The room has %s available seats and there is %s attendees registered' % (self.seats, len(self.attendee_ids))
            }}

    # maximum seats using constrains
    @api.constrains('seats', 'attendee_ids')
    def _check_taken_seats(self):
        for session in self:
            if session.taken_seats > 100:
                raise exceptions.ValidationError('The room has %s available seats and there is %s attendees registered' % (
                    session.seats, len(session.attendee_ids)))

    # maximum seats using sql constraints
    _sql_constraints = [
        # possible only if taken_seats is stored
        ('session_full', 'CHECK(taken_seats <= 100)', 'The room is full'),
    ]


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

    @api.constrains('instructor_id', 'attendee_ids')
    def _check_instructor_not_in_attendees(self):
        for r in self:
            if r.instructor_id and r.instructor_id in r.attendee_ids:
                raise exceptions.ValidationError("A session's instructor can't be an attendee")


