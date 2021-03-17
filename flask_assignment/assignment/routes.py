import requests
from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from assignment import app, db, bcrypt, api, mail
from assignment.forms import RegistrationForm, LoginForm, UpdateAccountForm, AddForm, ChangePasswordForm, \
    RequestResetForm, ResetPasswordForm
from assignment.models import Employees
from flask_login import login_user, current_user, logout_user, login_required
from flask_restful import Resource
from flask_mail import Message
import logging
from flask_httpauth import HTTPBasicAuth

logging.basicConfig(filename='record.log', level=logging.DEBUG,
                    format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
auth = HTTPBasicAuth()
admin = db.session.query(Employees).filter_by(email='admin@gmail.com').one()
USER_DATA = {
    admin.email: admin.password
}


@auth.verify_password
def verify(username, password):
    if not (username and password):
        return False
    return USER_DATA.get(username) == password


@app.route("/")
@app.route("/home")
def home():
    db.create_all()
    if current_user.is_authenticated:
        logout_user()
        flash('You were Logged out successfully', 'info')
    return render_template('home.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        employee = Employees(first_name=form.first_name.data,
                             last_name=form.last_name.data,
                             email=form.email.data,
                             phone_no=form.phone_no.data,
                             date_of_birth=form.date_of_birth.data,
                             address=form.address.data,
                             password=hashed_password)
        try:
            db.session.add(employee)
            db.session.commit()
            app.logger.info(f"New employee registered with name {employee.first_name} {employee.last_name}")
            flash('Your account has been created! You are now able to log in', 'success')
        except:
            flash('This Phone no is already registered! .Please enter a new Phone no', 'info')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Employees.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            if user.is_admin:
                app.logger.info(f"{user.first_name} login into the software ")
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))

        elif user is None:
            flash('Please register first to use EMS', 'info')
        else:
            flash('Wrong credentials. Please check email or password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    app.logger.info(f"Current User was logged out ")
    logout_user()
    flash('Successfully Logged Out', 'info')
    return redirect(url_for('home'))


@app.route("/change_password", methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        old_pwd = form.old_password.data
        new_pwd = form.new_password.data
        new_confirm_pwd = form.new_confirm_password.data
        if bcrypt.check_password_hash(current_user.password, old_pwd):
            hashed_password = bcrypt.generate_password_hash(new_pwd).decode('utf-8')
            current_user.password = hashed_password
            db.session.commit()
            app.logger.info(f"{current_user.first_name} changed password")
            flash('Password has been updated successfully!', 'success')
            return redirect(url_for('account'))
        else:
            flash('Wrong Old Password Entered!', 'danger')
            return redirect(url_for('forgot_password'))
    return render_template('change_password.html', form=form, title="Change Password")


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        if current_user.email != form.email.data:
            flash("Email can't be changed", 'info')
            return redirect(url_for('account'))
        if current_user.phone_no != form.phone_no.data:
            flash("Phone No can't be changed", 'info')
            return redirect(url_for('account'))
        current_user.date_of_birth = form.date_of_birth.data
        current_user.address = form.address.data
        db.session.commit()
        app.logger.info(f"{current_user.first_name} updated profile")
        flash('Account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
        form.phone_no.data = current_user.phone_no
        form.date_of_birth.data = current_user.date_of_birth
        form.address.data = current_user.address
    return render_template('account.html', form=form, title="Update Account")


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template('dashboard.html', title='Dashboard')


@app.route("/admin_dashboard")
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)
    return render_template('admin_dashboard.html', title='Admin Dashboard')


def check_admin():
    if not current_user.is_admin:
        abort(403)


@app.route('/employees', methods=['GET', 'POST'])
@login_required
def list_employees():
    """
    List all employees
    """
    check_admin()
    try:
        if request.method == "POST":
            name = request.form['name']
            # if name is None:
            #     flash('No input entered, Try again!!!', 'info')
            r = requests.get(url=f"http://127.0.0.1:5000/search/{name}",
                                 auth=(current_user.email, current_user.password))
            app.logger.info(f"Admin searched an Employee")
            if len(r.json()):
                return render_template("employee_search.html", employee=r.json())

        employees = Employees.query.all()
        return render_template('employee_details.html',
                               employees=employees, title='Employees')
    except:
        flash('No user found with this details', 'info')
        return redirect(url_for('list_employees'))


@app.route('/employees/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_employee(id):
    """
    Assign a department and a role to an employee
    """
    check_admin()

    employee = Employees.query.get_or_404(id)

    db.session.delete(employee)
    db.session.commit()
    app.logger.info(f"Admin deleted an employee with id = {id}")
    flash('You have successfully deleted the account.', 'danger')

    # redirect to the roles page
    return redirect(url_for('list_employees'))


@app.route("/add_employee", methods=['GET', 'POST'])
@login_required
def add_employee():
    check_admin()
    form = AddForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        employee = Employees(first_name=form.first_name.data,
                             last_name=form.last_name.data,
                             email=form.email.data,
                             phone_no=form.phone_no.data,
                             date_of_birth=form.date_of_birth.data,
                             address=form.address.data,
                             password=hashed_password)
        try:
            db.session.add(employee)
            db.session.commit()
            app.logger.info(f"Admin added an employee")
            flash('Account has been created!', 'success')
            return redirect(url_for('list_employees'))
        except:
            flash('Please enter a new Phone no', 'info')
            return redirect(url_for('add_employee'))
    return render_template('admin_add.html', title='Add Employee', form=form)


@app.route('/employees/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_employee(id):
    """
    Edit a department
    """
    check_admin()
    if not current_user.is_admin:
        login_user()
    add_employee = False
    user = Employees.query.get_or_404(id)
    form = UpdateAccountForm()
    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        if user.email != form.email.data:
            flash("Email can't be changed", 'info')
            return redirect(url_for('list_employees'))
        if user.phone_no != form.phone_no.data:
            flash("Phone No can't be changed", 'info')
            return redirect(url_for('list_employees'))
        user.date_of_birth = form.date_of_birth.data
        user.address = form.address.data
        db.session.commit()
        app.logger.info(f"Admin edited an employee with id = {id}")
        flash('Account has been updated!', 'success')
        return redirect(url_for('list_employees'))
    elif request.method == 'GET':
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.email.data = user.email
        form.phone_no.data = user.phone_no
        form.date_of_birth.data = user.date_of_birth
        form.address.data = user.address
    return render_template('update_employee.html', action="Edit", add_employee=add_employee, title='Update Account',
                           user=user, form=form)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = Employees.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        app.logger.info(f"Password reset link has been sent to employee over email with id = {user.id}")
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = Employees.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        app.logger.info("New password made by the current user")
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


class Hello(Resource):
    decorators = [auth.login_required]

    def get(self, name):
        users = Employees.query.all()
        if users is None:
            return jsonify({"message": "Empty Database"})
        count = 1
        employee_dict = {}
        for user in users:
            full_name = user.first_name + " " + user.last_name
            if (full_name == name) or (user.address == name):
                temp = "Employee " + str(count)
                dict = {}
                dict['Id'] = user.id
                dict['First Name'] = user.first_name
                dict['Last Name'] = user.last_name
                dict['Email'] = user.email
                dict['Phone No'] = user.phone_no
                dict['Date of Birth'] = user.date_of_birth
                dict['Address'] = user.address
                employee_dict[temp] = dict
                count += 1
        if count == 1:
            return jsonify({"message": "User Not Found"})
        else:
            return jsonify(employee_dict)


api.add_resource(Hello, '/search/<string:name>')
