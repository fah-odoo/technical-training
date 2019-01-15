from odoo import models, fields, api


class library(models.Model):
    _name = 'library.library'
    
    name = fields.Char()

class Book(models.Model):
    _name = 'library.book'
    _description = 'Book'

    name = fields.Char(string='Title')

    author_ids = fields.Many2many("library.author", string="Authors")
    edition_date = fields.Date()
    isbn = fields.Char(string='ISBN')
    publisher_id = fields.Many2one('library.publisher', string='Publisher')

    rental_ids = fields.One2many('library.rental', 'book_id', string='Rentals')

class BookInstance(models.Model):    
     _name = 'library.bookinstance'
     
#     _description = 'Book instance'

#     customer_id = fields.Many2one('library.customer', string='Customer')
#     book_id = fields.Many2one('library.book', string='Book')

#     rental_date = fields.Date()
#     return_date = fields.Date()


class Customer(models.Model):
    _name = 'library.customer'
    _description = 'Customer'

    name = fields.Char()
    email = fields.Char()
    address = fields.Text()
    rental_ids = fields.One2many(
        'library.rental', 'customer_id', string='Rentals')

class Author(models.Model):
    _name = 'library.author'
    _description = 'Author'
    name = fields.Char()

class Publisher(models.Model):
    _name = 'library.publisher'
    _description = 'Publisher'
    name = fields.Char()


class Rentals(models.Model):
    _name = 'library.rental'
    _description = 'Book rental'

    customer_id = fields.Many2one('library.customer', string='Customer')
    book_id = fields.Many2one('library.book', string='Book')

    rental_date = fields.Date()
    return_date = fields.Date()

    customer_address = fields.Text(related='customer_id.address')
    customer_email = fields.Char(related='customer_id.email')

    book_authors = fields.Many2many(related='book_id.author_ids')
    book_edition_date = fields.Date(related='book_id.edition_date')
    book_publisher = fields.Many2one(related='book_id.publisher_id')
