from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import datetime

class Movimiento(models.Model):
	_name = "sa.movimiento" # nombre tecnico de la tabla sa_movimiento
	_description = "Movimiento"
	_inherit = "mail.thread"

	name = fields.Char(string="Nombre",required=True)
	type_move = fields.Selection(selection=[("ingreso","Ingreso"),("gasto","Gasto")],string ="Tipo",default="ingreso",required=True)
	date = fields.Datetime("Fecha")
	amount = fields.Float("Monto",track_visibility="onchange")
	receipt_image = fields.Binary("Foto del recibo")
	notas = fields.Html(string="Notas")

	currency_id = fields.Many2one("res.currency",default=33)

	user_id = fields.Many2one("res.users",string="Usuario",default=lambda self:self.env.user.id)
	category_id = fields.Many2one("sa.category",string="Categoria")
	#tag_ids = fields.Many2many("sa.tag",string="Tag")
	tag_ids = fields.Many2many("sa.tag","sa_mov_sa_tag_rel","move_id","tag_id")

	email = fields.Char(related="user_id.email",string="Correo electronico")

	@api.constrains("amount")
	def _check_amount(self):
		if not(self.amount >= 0 and self.amount<=100000):
			raise ValidationError("El monto debe encontrarse entre 0 y 100,000")

	@api.onchange("type_move")
	def onchange_type_move(self):
		if self.type_move == "ingreso":
			self.name = "Ingreso: "
			self.amount = 50
		elif self.type_move == "gasto":
			self.name = "Gasto: "
			self.amount = 100

	@api.model
	def create(self,vals):
		name = vals.get("name","-")
		amount = vals.get("amount",0)
		type_move = vals.get("type_move","")
		date = vals.get("date","")

		notas = """<p>Tipo de Movimiento: {}</p><p>Nombre: {}</p><p>Monto: {}</p><p>Fecha: {}</p>"""
		vals["notas"] = notas.format(type_move,name,amount,date)

		res = super(Movimiento,self).create(vals)
		return res

	def unlink(self):
		for record in self:
			if record.amount >=50:
				raise ValidationError("Movimientos con montos mayores a 50 no pueden ser eliminados")
		return super(Movimiento.self).unlink()

class Category(models.Model):
	_name ="sa.category"
	_description = "Categoria"

	name = fields.Char("Nombre")

	type_move = fields.Selection(selection=[("ingreso","Ingreso"),("gasto","Gasto")],string ="Tipo",default="ingreso",required=True)

	def ver_movimientos(self):
		return {
			"type": "ir.actions.act_window",
			"name":"Movimientos de categoria "+self.name,
			"res_model":"sa.movimiento",
			"views":[[False,"tree"]],
			"target":"new",
			"domain":[["category_id","=",self.id]]
		}

class Tag(models.Model):
	_name = "sa.tag"
	_description = "Tag"

	name = fields.Char("Nombre")
	type_move = fields.Selection(selection=[("ingreso","Ingreso"),("gasto","Gasto")],string ="Tipo",default="ingreso",required=True)
	#move_id = fields.Many2one("sa.movimiento",string="move_id")
	#move_id = fields.Many2many("sa.movimiento","sa_mov_sa_tag_rel","move_id","tag_ids",string="move_id")


#Modificando un modelo ya existente Usuarios
class ResUsers(models.Model):
	_inherit ="res.users"

	movimiento_ids = fields.One2many("sa.movimiento","user_id")
	total_ingresos = fields.Float("Total de Ingresos",compute="_compute_movimientos")
	total_egresos = fields.Float("Total de gastos",compute="_compute_movimientos")
	count_movimientos = fields.Integer("Cantidad de movimientos por mes",compute="_compute_movimientos")

	@api.depends("movimiento_ids")
	def _compute_movimientos(self):
		for record in self:
			record.total_ingresos = sum(record.movimiento_ids.filtered(lambda r:r.type_move == 'ingreso').mapped("amount"))
			record.total_egresos = sum(record.movimiento_ids.filtered(lambda r:r.type_move == 'gasto').mapped("amount"))
			mes = datetime.now().month
			movs = record.movimiento_ids.filtered(lambda r: r.create_date.month == mes)
			record.count_movimientos = len(movs)

	def mi_cuenta(self):
		return{
			"type":"ir.actions.act_window",
			"name":"Mi cuenta",
			"res_model":"res.users",
			"res_id":self.env.user.id,
			"target":"self",
			"views":[(False,"form")]
		}
	