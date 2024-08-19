from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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

    transactions = Transaction.query.join(User).join(Category).add_columns(
        Transaction.id,
        Transaction.date,
        Transaction.description,
        Transaction.amount,
        Transaction.payed,
        User.username.label('user_username'),
        Category.name.label('category_name')
    )

    if request.method == 'POST':
        selected_category = request.form.get('category')
        selected_user = request.form.get('user')
        selected_date = request.form.get('date')

        if selected_category:
            transactions = transactions.filter(Transaction.category_id == selected_category)
        if selected_user:
            transactions = transactions.filter(Transaction.created_by == selected_user)
        if selected_date:
            date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
            transactions = transactions.filter(Transaction.date == date_obj)

    transactions = transactions.all()

    transaction_list = []
    for transaction in transactions:
        transaction_list.append({
            'id': transaction.id,
            'date': transaction.date,
            'user': transaction.user_username,
            'category': transaction.category_name,
            'description': transaction.description,
            'amount': transaction.amount,
            'payed': transaction.payed
        })

    return render_template('index.html', transactions=transaction_list, categories=categories, users=users)


@app.route('/add', methods=['GET', 'POST'])
def add_transaction():
    categories = Category.query.all()
    users = User.query.all()

    if request.method == 'POST':
        category_id = request.form.get('category')
        user_id = request.form.get('user')
        description = request.form.get('description')
        amount = request.form.get('amount')
        date_value = request.form.get('date')
        payed = 'payed' in request.form

        date_obj = datetime.strptime(date_value, '%Y-%m-%d').date()
        transaction = Transaction(
            category_id=category_id, created_by=user_id, description=description,
            amount=amount, date=date_obj, payed=payed
        )
        db.session.add(transaction)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('add_transaction.html', categories=categories, users=users)


@app.route('/edit/<int:transaction_id>', methods=['GET', 'POST'])
def edit_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    categories = Category.query.all()
    users = User.query.all()

    if request.method == 'POST':
        transaction.category_id = request.form.get('category')
        transaction.created_by = request.form.get('user')
        transaction.description = request.form.get('description')
        transaction.amount = request.form.get('amount')
        date_value = request.form.get('date')
        transaction.date = datetime.strptime(date_value, '%Y-%m-%d').date()
        transaction.payed = 'payed' in request.form

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit_transaction.html', transaction=transaction, categories=categories, users=users)


@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form.get('username')
    user = User(username=username)
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('add_transaction'))


@app.route('/add_category', methods=['POST'])
def add_category():
    name = request.form.get('name')
    category = Category(name=name)
    db.session.add(category)
    db.session.commit()
    return redirect(url_for('add_transaction'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
