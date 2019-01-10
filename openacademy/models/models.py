# -*- coding: utf-8 -*-

from odoo import models, fields, api

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


class Session(models.Model):
    _name = 'openacademy.session'

    name = fields.Char(required=True)
    start_date = fields.Date()
    duration = fields.Float(digits=(6, 2), help="Duration in days")
    seats = fields.Integer(string="Number of seats")

    # There can be several teachers for a course session
    instructor_id = fields.Many2one('res.partner', string="Instructor")

    # There can be several sessions of a course
    course_id = fields.Many2one('openacademy.course',
                                ondelete='cascade', string="Course", required=True)

    # There can be several attendees for a course session. There can be several course sessions for an attendee.                            
    attendee_ids = fields.Many2many('res.partner', string="Attendees")
