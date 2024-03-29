from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FloatField, RadioField, SelectField, DateTimeField, validators
from wtforms.validators import DataRequired, email, NumberRange, Length, ValidationError
import requests
import sqlite3
import os
import requests
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import update, and_
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
Bootstrap(app)



# Currency API _________________________________________________________________________________________________________
import requests
#def currency_api(from_to):
#    URL = 'https://free.currconv.com/api/v7/convert'
#    parameters = {
#       'apiKey': 'your api key',
#       'q': from_to,
#       'compact':'ultra'
#   }
#   response = requests.get(url=URL, params=parameters).json()
#   return response[from_to]

#EUR_MKD = currency_api('EUR_MKD')
EUR_MKD = 61.61
#MKD_EUR = currency_api('MKD_EUR')
MKD_EUR = 0.016

#USD_MKD = currency_api('USD_MKD')
USD_MKD = 56.09
#MKD_USD = currency_api('MKD_USD')
MKD_USD = 0.018

#EUR_USD = currency_api('EUR_USD')
EUR_USD = 1.10
#USD_EUR = currency_api('USD_EUR')
USD_EUR = 0.91


##CREATE DATABASE_______________________________________________________________________________________________________
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///e-commerce.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##CREATE TABLE__________________________________________________________________________________________________________
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(250), nullable=False, unique=False)
    last_name = db.Column(db.String(250), nullable=False, unique=False)
    email = db.Column(db.String(250), nullable=False, unique=False)
    credit_card = db.Column(db.Integer, nullable=True, unique=False)
    date = db.Column(db.String(250), nullable=False, unique=False)
    address = db.Column(db.String(250), nullable=False, unique=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(250), nullable=False, unique=False)
    category = db.Column(db.String(250), nullable=False, unique=False)
    quantity = db.Column(db.Integer, nullable=False, unique = False)
    size = db.Column(db.String, nullable=False, unique=False)
    price = db.Column(db.Float, nullable=False, unique=False)
    currency = db.Column(db.String(5), nullable=False, unique=False)

db.create_all()

#new_product = Product(title='Bluza',category='Pants',quantity=10,size='S',price=120,currency='MKD')
#db.session.add(new_product)
#db.session.commit()

#WTF_forms______________________________________________________________________________________________________________
class Add_Customer(FlaskForm):
    first_name = StringField('First name:',validators=[DataRequired()])
    last_name = StringField('Last name:',validators=[DataRequired()])
    email = StringField('Email:',validators=[DataRequired(), email()])
    credit_card = StringField('Credit_card:',validators=[Length(min=16,max=16), validators.Optional()])
    street_name = StringField('Street name and number:',validators=[DataRequired()])
    zip_code = StringField('Zip code:',validators=[DataRequired(), Length(min=4,max=4)])
    city = StringField('City:',validators=[DataRequired()])
    state = StringField('State',validators=[DataRequired()])
    submit = SubmitField('Submit',validators=[DataRequired()])

    def validate_credit_card(self, credit_card):
        if not credit_card.data.isnumeric():
            raise ValidationError("Field must not contain characters. Only numbers.")
        elif (int(credit_card.data[0]) != 5) and (int(credit_card.data[0]) != 4) and (int(credit_card.data[0]) != 6):
            print(type(int(credit_card.data[0])))
            raise ValidationError("Invalid credit card number.It must start with 4, 5 or 6")
    # 4 Consecutive digits
        n = credit_card.data
        size = len(n)
        for i in range(size-3):
            if n[i] == n[i + 1] and n[i + 1] == n[i + 2] and n[i + 2] == n[i + 3]:
                raise ValidationError("Invalid credit card number. It must not have more than 4 consecutive digits.")

    def validate_city(self,city):
        input_address = str(self.street_name.data) + ', ' + str(self.zip_code.data) + ', ' + str(
            self.city.data) + ', ' + str(self.state.data)
        exists = db.session.query(Customer).filter(
            Customer.first_name.like(self.first_name.data),
            Customer.last_name.like(self.last_name.data),
            Customer.address.like(input_address)
        ).first()
        if exists:
            raise ValidationError("This user can't have more than one address")

    def validate_zip_code(self, zip_code):
        input_address = str(self.street_name.data) + ', ' + str(zip_code.data) + ', ' + str(
            self.city.data) + ', ' + str(self.state.data)
        exists = db.session.query(Customer).filter(
            Customer.first_name.like(self.first_name.data),
            Customer.last_name.like(self.last_name.data),
            Customer.address.like(input_address)
        ).first()

        if exists:
            raise ValidationError("This user can't have more than one address")

    def validate_street_name(self, street_name   ):
        input_address = str(street_name.data) + ', ' + str(self.zip_code.data) + ', ' + str(
            self.city.data) + ', ' + str(self.state.data)
        exists = db.session.query(Customer).filter(
            Customer.first_name.like(self.first_name.data),
            Customer.last_name.like(self.last_name.data),
            Customer.address.like(input_address)
        ).first()

        if exists:
            raise ValidationError("This user can't have more than one address")

    def validate_state(self, state):
        input_address = str(self.street_name.data) + ', ' + str(self.zip_code.data) + ', ' + str(
            self.city.data) + ', ' + str(state.data)
        exists = db.session.query(Customer).filter(
            Customer.first_name.like(self.first_name.data),
            Customer.last_name.like(self.last_name.data),
            Customer.address.like(input_address)
        ).first()

        if exists:
            raise ValidationError("This user can't have more than one address")

class Add_Product(FlaskForm):
    title = StringField('Title:', validators=[DataRequired()])
    category = SelectField('Category:', choices=['Pants', 'Pyjamas', 'Shirts'], validators=[DataRequired()])
    size = SelectField(label='Size', choices = ['S', 'M','L','XL'])
    price = StringField('Price:', validators=[DataRequired()])
    currency = SelectField('Currency:', choices = ['MKD', 'USD','EUR'])
    submit = SubmitField('Submit', validators=[DataRequired()])

class Currency_form(FlaskForm):
    currency = SelectField('Currency:', choices=['MKD', 'USD', 'EUR'])
    submit = SubmitField('Submit', validators=[DataRequired()])

#Endpoints______________________________________________________________________________________________________________
@app.route("/")
def home():
    all_customers = db.session.query(Customer).all()
    all_products = db.session.query(Product).order_by(Product.price).all()
    db.session.commit()
    return render_template('index.html', all_customers=all_customers, all_products=all_products)

@app.route("/customers")
def customers():
    all_customers = db.session.query(Customer).all()
    db.session.commit()
    return render_template('customers.html',all_customers=all_customers)

@app.route("/products", methods=["GET","POST"])
def products():
    form = Currency_form()
    all_products = db.session.query(Product).order_by(Product.price).all()
    print(all_products)
    if form.validate_on_submit():
        currency = form.currency.data
        if currency == 'MKD':
            # FROM EUR TO MKD
            product_to_update_EUR = Product.query.filter_by(currency='EUR')
            for product1 in product_to_update_EUR:
                product1.price = round(product1.price * EUR_MKD,2)
                product1.currency = 'MKD'
            # FROM USD TO MKD
            product_to_update_USD = Product.query.filter_by(currency='USD')
            for product1 in product_to_update_USD:
                product1.price = round(product1.price * USD_MKD,2)
                product1.currency = 'MKD'
            db.session.commit()
        elif currency == 'EUR':
            # FROM MKD TO EUR
            product_to_update_MKD = Product.query.filter_by(currency='MKD')
            for product1 in product_to_update_MKD:
                product1.price = round(product1.price * MKD_EUR,2)
                product1.currency = 'EUR'
            # FROM USD TO EUR
            product_to_update_USD = Product.query.filter_by(currency='USD')
            for product1 in product_to_update_USD:
                product1.price = round(product1.price * USD_EUR,2)
                product1.currency = 'EUR'
            db.session.commit()
        elif currency == 'USD':
            # FROM MKD TO USD
            product_to_update_MKD = Product.query.filter_by(currency='MKD')
            for product1 in product_to_update_MKD:
                product1.price = round(product1.price * MKD_USD,2)
                product1.currency = 'USD'
            # FROM EUR TO USD
            product_to_update_EUR = Product.query.filter_by(currency='EUR')
            for product1 in product_to_update_EUR:
                product1.price = round(product1.price * EUR_USD,2)
                product1.currency = 'USD'

            db.session.commit()
        return redirect(url_for('products'))

    db.session.commit()
    return render_template('products.html', all_products=all_products, form=form)

@app.route("/add_customer", methods=["GET","POST"])
def add_customer():
    form = Add_Customer()
    if form.validate_on_submit():
        today = datetime.now().strftime("%d/%m/%Y  %H:%M:%S")


        new_customer=Customer(first_name = form.first_name.data,
                              last_name= form.last_name.data,
                              email = form.email.data,
                              credit_card=form.credit_card.data,
                              date=today,
                              address=str(form.street_name.data) + ', ' + str(form.zip_code.data) + ', ' + str(form.city.data) + ', ' + str(form.state.data))
        db.session.add(new_customer)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add_customer.html',form=form)

@app.route("/add_product", methods=["GET","POST"])
def add_product():
    form = Add_Product()

    if form.validate_on_submit():
        exists = db.session.query(Product).filter(
                    Product.title.like(form.title.data),
                    Product.category.like(form.category.data),
                    Product.size.like(form.size.data)
        ).first()

        if not exists:
            new_product=Product(title = form.title.data,
                                  category= form.category.data,
                                  quantity = 1,
                                  size=form.size.data,
                                  price=form.price.data,
                                  currency=form.currency.data)
            db.session.add(new_product)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            exists.quantity = exists.quantity+1
            exists.price = form.price.data
            exists.currency = form.currency.data
            db.session.commit()
            #print(product_to_update)
            return redirect(url_for('home'))
    return render_template('add_product.html',form=form)

@app.route("/delete_customer")
def delete_customer():
    customer_id = request.args.get('id')
    customer_to_delete = Customer.query.get(customer_id)
    db.session.delete(customer_to_delete)
    db.session.commit()
    return redirect(url_for('customers'))

@app.route("/delete_product")
def delete_product():
    product_id = request.args.get('id')
    product_to_delete = Product.query.get(product_id)
    db.session.delete(product_to_delete)
    db.session.commit()
    return redirect(url_for('products'))




if __name__ == '__main__':
    app.run(debug=True)
