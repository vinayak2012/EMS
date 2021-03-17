# EMS
Employee Management System

Roles and permissions:-

1. User(Employee)

    a) Register on Employee management system
    
    b) Login into their account
    
    c) View their profile
    
    d) Update their profile
    
    e) Can change their existing password
    
    f) Can generate new password using forgot password facility
    

2.  Admin

    a) Login into their account
    
    b) Can view list of employees on master screen
    
    c) Can add an employee into the system
    
    d) Can update/delete details of an employee
    
    e) Can search an employee on basis of name(full name = first name + last name) or address.
     Also, both of these need to be exact same as that in database.
    
Deliverables:

1.	Web application developed using flask and Jinja

2.	Restful service developed using flask restful

3.	URL definitions of the scenarios (request/response JSONs)

4.	Docker images to be built using Dockerfile
 
5.	A docker-compose file for booting the applications from a single file


Tools/Technologies

1.	Python language with Flask

2.	Flask restful for microservices

3.	Docker as a deployment tool

4.	Username/password base authentication to secure API


Important Points: 

1. Employee and Admin both can login through same screen with different roles.

2. Forget password works with valid gmails. Ex- guptavinayak.2012@gmail.com for this project

3. Emails and phone no can't be changed during update(unique attributes).

4. Phone No's can be office landline no's also.

5. Date of birth is to be entered in YYYY-MM-DD format

6. Only admin can see master screen and can perform all opertions.

7. Only admin can search an employee in searchbar on master screen.

8. Any other user who want to search an employee will have to enter admin login credentials.

9. Password length min 8 characters.

10.	Restful microservice for searching an employee based on Name or address

11. Docker Commands:-

     Docker Image - docker build -t employee_management -f ./Dockerfile.dockerfile .
     
     Docker Container - docker run -d -p 5000:5000 employee_management
     
     Docker compose file - docker-compose up --build -d
     
     


