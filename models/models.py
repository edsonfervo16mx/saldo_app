from odoo import fields, models

class Movimiento(models.Model):
	_name = "sa.movimiento" # nombre tecnico de la tabla sa_movimiento
	_description = "Movimiento"

	name = fields.Char(string="Nombre",required=True)
	type_move = fields.Selection(selection=[("ingreso","Ingreso"),("gasto","Gasto")],string ="Tipo",default="ingreso",required=True)
	date = fields.Datetime("Fecha")
	amount = fields.Float("Monto")
	receipt_image = fields.Binary("Foto del recibo")
	notas = fields.Html(string="Notas")

	currency_id = fields.Many2one("res.currency")

	user_id = fields.Many2one("res.users",string="Usuario")
	category_id = fields.Many2one("sa.category","Categoria")
	tag_ids = fields.Many2one("sa.tag","Tag")

class Category(models.Model):
	_name ="sa.category"
	_description = "Categoria"

	name = fields.Char("Nombre")

class Tag(models.Model):
	_name = "sa.tag"
	_description = "Tag"

	name = fields.Char("Nombre")
	move_id = fields.One2many("sa.movimiento","tag_ids")


#Modificando un modelo ya existente Usuarios
class ResUsers(models.Model):
	_inherit ="res.users"

	movimiento_ids = fields.One2many("sa.movimiento","user_id")
