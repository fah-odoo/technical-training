# -*- coding: utf-8 -*-

# exceptions is for constrains()
from odoo import api, exceptions, fields, models
from datetime import timedelta

class openacademy(models.Model):
    _name = 'openacademy.openacademy'
    _description = 'Open Academy'

    name = fields.Char()

class Course(models.Model):
    _name = 'openacademy.course'
    _description = 'Course'

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
    _description = 'Session'

    # OpenChatter
    _inherit = ['mail.thread']

    name = fields.Char(required=True)

    start_date = fields.Date(default=fields.Date.today)
    end_date = fields.Date(string="End Date", store=True,
                           compute='_get_end_date', inverse='_set_end_date')

    hours = fields.Float(string="Duration in hours",
                         compute='_get_hours', inverse='_set_hours')

    duration = fields.Float(digits=(6, 2), help="Duration in days")

    @api.depends('duration')
    def _get_hours(self):
        for r in self:
            r.hours = r.duration * 24

    def _set_hours(self):
        for r in self:
            r.duration = r.hours / 24


    @api.depends('start_date', 'duration')
    def _get_end_date(self):
        for r in self:
            if not (r.start_date and r.duration):
                r.end_date = r.start_date
                continue

            # Add duration to start_date, but: Monday + 5 days = Saturday, so
            # subtract one second to get on Friday instead
            start = fields.Datetime.from_string(r.start_date)
            duration = timedelta(days=r.duration, seconds=-1)
            r.end_date = start + duration

    def _set_end_date(self):
        for r in self:
            if not (r.start_date and r.end_date):
                continue

            # Compute the difference between dates, but: Friday - Monday = 4 days,
            # so add one day to get 5 days instead
            start_date = fields.Datetime.from_string(r.start_date)
            end_date = fields.Datetime.from_string(r.end_date)
            r.duration = (end_date - start_date).days + 1


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
    attendees_count = fields.Integer(
        string="Attendees count", compute='_get_attendees_count', store=True)

    taken_seats = fields.Float(string="Taken seats", compute='_taken_seats', store='True')
    
    # maximum seats using depends
    @api.depends('seats', 'attendee_ids')
    def _taken_seats(self):
        for r in self:
            if not r.seats:
                r.taken_seats = 0.0
            else:
                r.taken_seats = 100.0 * len(r.attendee_ids) / r.seats

    @api.depends('attendee_ids')
    def _get_attendees_count(self):
        for session in self:
            session.attendees_count = len(session.attendee_ids)

    @api.multi
    def action_draft(self):
        for rec in self:
            rec.state = 'draft'
            rec.message_post(body="Session %s of the course %s reset to draft" % (
                rec.name, rec.course_id.name))

    @api.multi
    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'
            rec.message_post(body="Session %s of the course %s confirmed" % (
                rec.name, rec.course_id.name))

    @api.multi
    def action_done(self):
        for rec in self:
            rec.state = 'done'
            rec.message_post(body="Session %s of the course %s done" %
                             (rec.name, rec.course_id.name))

    def _auto_transition(self):
        for rec in self:
            if rec.taken_seats >= 50.0 and rec.state == 'draft':
                rec.action_confirm()

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


