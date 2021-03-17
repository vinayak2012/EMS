
from assignment.models import Employees
from flask import jsonify
from flask_restful import Resource
from assignment import api, db
from flask_httpauth import HTTPBasicAuth


auth = HTTPBasicAuth()
admin = db.session.query(Employees).filter_by(email='admin@gmail.com').one()
print(admin.password)
USER_DATA = {
    "admin@gmail.com": admin.password
}


@auth.verify_password
def verify(username, password):
    if not (username and password):
        return False
    return USER_DATA.get(username) == password


class Hello(Resource):
    decorators = [auth.login_required]

    def get(self, name):
        users = Employees.query.all()
        count = 1
        employee_dict = {}
        print(name)
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