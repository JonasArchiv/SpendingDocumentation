from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    payed = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


@app.route('/', methods=['GET', 'POST'])
def index():
    categories = Category.query.all()
    users = User.query.all()

    transactions = Transaction.query

    if request.method == 'POST':
        selected_category = request.form.get('category')
        selected_user = request.form.get('user')
        selected_date = request.form.get('date')

        if selected_category:
            transactions = transactions.filter_by(category_id=selected_category)
        if selected_user:
            transactions = transactions.filter_by(created_by=selected_user)
        if selected_date:
            date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
            transactions = transactions.filter_by(date=date_obj)

    transactions = transactions.all()

    return render_template('index.html', transactions=transactions, categories=categories, users=users)


@app.route('/add', methods=['GET', 'POST'])
def add_transaction():
    categories = Category.query.all()
    users = User.query.all()

    if request.method == 'POST':
        category_id = request.form['category']
        user_id = request.form['user']
        description = request.form['description']
        amount = request.form['amount']
        date_value = request.form['date']
        payed = 'payed' in request.form

        transaction = Transaction(category_id=category_id, created_by=user_id, description=description,
                                  amount=amount, date=date_value, payed=payed)
        db.session.add(transaction)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('add_transaction.html', categories=categories, users=users)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
