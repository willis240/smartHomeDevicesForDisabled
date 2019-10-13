from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db = SQLAlchemy(app)

##Database Schema

# class User(db.Model):
# 	id = db.Column(db.Integer, primary_key=True)
# 	username = db.Column(db.String(80), unique=True, nullable=False)
# 	email = db.Column(db.String(120), unique=True, nullable=False)

# 	def __repr__(self):
# 		return '<User %r>' % self.username 

class disabilitycategory(db.Model):
	def __str__(self):
		return self.name 

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80), nullable=False)
	disabilities = db.relationship('Disability',
		backref='disabilitycategory', lazy=True)
	device = db.relationship('Device',
		backref='disabilitycategory', lazy=True)

class Disability(db.Model):
	def __str__(self):
		return self.name 

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80), nullable=False)
	category_id = db.Column(db.Integer, db.ForeignKey('disabilitycategory.id'),
		nullable=False)
	# ATR = db.relationship('assistivetechrating', 
	# 	backref='disability')

	community_rating = db.relationship('communityrating', 
		backref='disability')

class devicecategory(db.Model):
	def __str__(self):
		return self.name 
	name = db.Column(db.String(80), nullable=False)
	id = db.Column(db.Integer, primary_key=True)

	device = db.relationship('Device',
	 backref='devicecategory', lazy=True)

# class assistivetechrating(db.Model):
# 	def __str__(self):
# 		return "<ATR %r>" % self.name 

# 	id = db.Column(db.Integer, primary_key=True)
	

class communityrating(db.Model):
	def __str__(self):
		return  self.name 

	id = db.Column(db.Integer, primary_key=True)
	description = db.Column(db.String(500), nullable=False)
	title = db.Column(db.String(50), nullable=False)
	rating = db.Column(db.Integer, nullable=False)
	disability_id = db.Column(db.Integer, 
		db.ForeignKey('disability.id'), 
		nullable=False)
	device = db.relationship('Device',
		backref='communityrating', lazy=True)

class paymentoccurence(db.Model):
	def __str__(self):
		return  self.name 

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20), nullable=False)
	device = db.relationship('Device', 
		backref='paymentoccurence', lazy=True)

class Device(db.Model):
	def __str__(self):
		return self.name 

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80), nullable=False)
	description = db.Column(db.String(500), nullable=False)
	price = db.Column(db.Float)
	recurring_price = db.Column(db.Float)
	payment_occurence_id = db.Column(db.Integer, 
		db.ForeignKey('paymentoccurence.id'),
		nullable=False)
	link = db.Column(db.String(), nullable=False)

	category_id = db.Column(db.Integer, 
		db.ForeignKey('devicecategory.id'),
		nullable=False)
	# atp_rating_id = db.Column(db.Integer, 
	# 	db.ForeignKey('assistivetechrating.id'),
	# 	nullable=False)
	community_rating_id = db.Column(db.Integer, 
		db.ForeignKey('communityrating.id'))

	disability_category_id = db.Column(db.Integer, 
		db.ForeignKey('disabilitycategory.id'), 
		nullable=False)
	effectiveness_rating = db.Column(db.Integer, nullable=False)
	relevance_rating = db.Column(db.Integer, nullable=False)
	narrative = db.Column(db.String(500), nullable=False)
	# device = db.relationship('Device', 
	# 	backref='assistivetechrating', lazy=True)

##Routing 
@app.route('/')
def main(name=None):
	disCat = disabilitycategory.query.all()
	return render_template('form.html', disCat=disCat)

@app.route('/listDevices', methods=["GET", "POST"])
def list(name=None):
	devices = []
	if request.method == 'POST':
	#find all the compatible devices
		for dis in request.form.getlist('disability'):
			disability = disabilitycategory.query.filter_by(name=dis).first()
			ds = Device.query.with_parent(disability).filter_by(disability_category_id=disability.id).all()
			
			for d in ds:
				devices.append(d)
	if len(devices) == 0: 
		devices = Device.query.all()

	return render_template('list.html', devices=devices)

@app.route('/createDevice', methods=["GET", "POST"])
def createDevice(name=None):
	po = paymentoccurence.query.all()
	dc = devicecategory.query.all()
	disC = disabilitycategory.query.all()
	if request.method == 'POST':
		po = paymentoccurence.query.filter_by(name=request.form.get('payment_occurence')).first()
		dc = devicecategory.query.filter_by(name=request.form.get('device_category')).first()
		disC = disabilitycategory.query.filter_by(name=request.form.get('disability_category')).first()
		db.session.add(Device(name=request.form.get('name'), 
			description=request.form.get('desc'), 
			price=request.form.get('price'),
			recurring_price=request.form.get('recurring_price'),
			payment_occurence_id=po.id, 
			link=request.form.get('link'),
			category_id=dc.id, 
			disability_category_id=disC.id, 
			effectiveness_rating=request.form.get('effectiveness_rating'),
			relevance_rating=request.form.get('relevance_rating'),
			narrative=request.form.get('narrative')
			))
		db.session.commit()
		return redirect(url_for('list'))
	return render_template('create_device.html', po=po, deviceCat=dc, disabilityCat=disC)

if __name__ == '__main__':
	app.run()