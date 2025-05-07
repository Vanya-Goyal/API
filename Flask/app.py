from flask import Flask, render_template, request, redirect, url_for, flash,session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,login_user,login_required,logout_user,current_user,LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from functools import wraps
import os
from datetime import datetime
from flask_marshmallow import Marshmallow
from flask_cors import CORS


app = Flask(__name__)
app.secret_key="ShillUp"
basedir=os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db=SQLAlchemy(app)
migrate = Migrate(app, db)  

ma = Marshmallow(app)
CORS(app)

bcrypt=Bcrypt(app) # to connect bcrypt with orm
login_manager=LoginManager() # to initialise login manager , flask_login module to authenticate user, session data,(e.g decorators = user mixing, login_required, these are if else conditions nothing else inbuilt functions)
login_manager.init_app(app) # 
login_manager.login_view="login" # if not authorised will redirect to login page

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, nullable=False)
    student_id = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin,db.Model): # for objects in tables usermixing = user authenticate, activate, anonymous(not logged in), get_id(returns unique id)
    tablename="user"  # Mapping to a Table: It helps SQLAlchemy map the model class to a specific table in the database.
    id=db.Column(db.Integer,primary_key=True) # id is primary key
    name=db.Column(db.String(150),nullable=False)
    email=db.Column(db.String(150),nullable=False,unique=True)
    password_hash=db.Column(db.String(256),nullable=False)
    mobile=db.Column(db.String(15),nullable=True)
    role=db.Column(db.String(50),nullable=False,default='user') # default user = user registered as default role when login
    occupation = db.Column(db.String(100))   
    interests = db.Column(db.PickleType, default=[])  # Stores a list of interests
    enrolled_courses = db.relationship('EnrolledCourse', backref='user', lazy=True)
    wishlist = db.Column(db.PickleType, default=[])
    purchase_history = db.relationship('Purchase', backref='user', lazy=True)
    enrolled_courses = db.relationship('EnrolledCourse', backref='user', lazy=True)
    purchase_history = db.relationship('Purchase', backref='user', lazy=True)
    

    def set_password(self,password):  # set password 
        self.password_hash=bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self,password): # to match credential input with password  in data base for that we need to hash password for we use check_password ,is handled by bcrypt
        return bcrypt.check_password_hash(self.password_hash,password) #check password checks stored hashed password with entered password
    
    def get_id(self):
        return str(self.id)
    
class CustomUser(UserMixin, db.Model):
    _tablename_ = 'custom_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)

    # This is the relationship from instructor to their DSA assignments
    dsa_assignments = db.relationship('DSAAssignment', backref='instructor', lazy=True)


class Course(db.Model):
    _tablename_ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    instructor = db.Column(db.Integer, nullable=True)  # Will store instructor_id as an integer only
    price = db.Column(db.Numeric(6, 2), default=0.00)
    category = db.Column(db.String(100), nullable=True)
    image = db.Column(db.String(255), nullable=True)  # Stores the image path or filename
    assignments = db.relationship('DSAAssignment', back_populates='course', cascade='all, delete-orphan')


    def _repr_(self):
        return f"<Course {self.title}>"
    
class EnrolledCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    progress = db.Column(db.Integer, default=0)  # Progress in percentage (0-100)

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
  
class DSAAssignment(db.Model):
    _tablename_ = 'dsa_assignment'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(10), nullable=False, default='Easy')
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    course = db.relationship('Course', back_populates='assignments')
    instructor_id = db.Column(db.Integer, db.ForeignKey('custom_user.id'), nullable=False)
    
    # course relationship (this one is OK)
    course = db.relationship('Course', backref='dsa_assignments')

with app.app_context(): 
    db.create_all()

@login_manager.user_loader


def load_user(user_id):
    return User.query.get(int(user_id)) # when we  use current user data we use current user module
login_manager.login_view = 'login'  # Redirects users to /login if not authenticated

def admin_required(func): 
    @wraps(func) 
    def wrapper(*args, **kwargs): 
        if current_user.role != 'admin': 
            flash("Access denied!", "danger") 
            return redirect(url_for('admindashboard')) 
        return func(*args, **kwargs) 
    return wrapper

# Route for Home Page
@app.route('/')
def home():
    return render_template('index.html', courses=courses)

@app.route("/signup",methods=["GET","POST"])
def signup():
    if request.method=="POST":
        fullname=request.form.get("fullname")
        email=request.form.get("email")
        password=request.form.get("password").strip()
        confirm_password=request.form.get("confirm_password").strip()
        mobile = request.form.get("mobile")   
        if password!=confirm_password:
            flash("Passwords do not match","danger")
            return redirect(url_for("signup"))

        if User.query.filter_by(email=email).first():
            flash("Email already exists","danger")
            return redirect(url_for("signup"))
        
        try:
            new_user = User(
                name=fullname,
                email=email,                
                mobile=mobile,
                role="user"  
            )
            
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            flash("Registered successfully","success")
            return redirect(url_for('login'))
    
        except Exception as e:
            db.session.rollback()
            flash("Registration failed. Please check all fields", "danger")
            return redirect(url_for("signup"))
    
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password").strip()
        
        
        # Define admin credentials
        ADMIN_EMAIL = "admin@example.com"  
        ADMIN_PASSWORD = "admin123"  
            
        
        # Check for admin login
        if email == ADMIN_EMAIL :
            if password == ADMIN_PASSWORD:
                # Get or create admin user
                admin_user = User.query.filter_by(email=ADMIN_EMAIL).first()
                if not admin_user:
                    admin_user = User(
                        name="Admin",
                        email=ADMIN_EMAIL,
                        role="admin"
                    )
                    admin_user.set_password(ADMIN_PASSWORD)
                    db.session.add(admin_user)
                    db.session.commit()
                
                login_user(admin_user)
                flash("Admin login successful!", "success")
                return redirect(url_for("instructor_dashboard"))
            else:
                flash("Invalid admin credentials!", "danger")
                return redirect(url_for('login'))
        
        # Regular user login
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Invalid credentials!", "danger")
            return redirect(url_for('login'))
         
        if user.check_password(password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials!", "danger")
        
    return render_template('login.html')


# routes.py (or your main Flask file)
@app.route('/forgetPassword', methods=['GET', 'POST'])
def forgetPassword():
    if request.method == 'POST':
        email = request.form.get('email')
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')

        # Basic validation
        if not email or not new_password or not confirm_password:
            flash("All fields are required!", "danger")
            return redirect(url_for('forgetPassword'))

        if new_password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('forgetPassword'))

        # Find user by email
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("No account found with that email!", "danger")
            return redirect(url_for('forgetPassword'))


        # Update password
        user.set_password(new_password)
        db.session.commit()

        flash("Password updated successfully!", "success")
        return redirect(url_for('login'))

    return render_template('forgetPassword.html')


@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role=='admin':  
        return redirect(url_for('admindashboard'))
    return render_template('dashboard.html', user=current_user)


@app.route('/admin') 
@login_required 
@admin_required 
def admin(): 
    if current_user.role != "admin":  
        flash("Access Denied! Admins only.", "danger")
        return redirect(url_for('admindashboard', user=current_user))  
    return render_template("index.html")


@app.route('/createcourse', methods=['GET', 'POST'])
@login_required
def createcourse():
    if current_user.role != 'admin':
        flash("Access denied!", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form.get('price', 0.0)
        category = request.form.get('category')
        image = request.form.get('image')

        course = Course(
            title=title,
            description=description,
            price=price,
            category=category,
            image=image,
            
        )

        db.session.add(course)
        db.session.commit()
        flash("Course created successfully!", "success")
        return redirect(url_for('courses'))

    return render_template('createcourse.html')



@app.route("/courses")
def courses():
    query = request.args.get("q", "")
    sort = request.args.get("sort", "")
    page = request.args.get("page", 1, type=int)

    # Basic query logic (adjust with your models)
    courses_query = Course.query
    if query:
        courses_query = courses_query.filter(Course.title.ilike(f"%{query}%"))

    if sort == "price_asc":
        courses_query = courses_query.order_by(Course.price.asc())
    elif sort == "price_desc":
        courses_query = courses_query.order_by(Course.price.desc())

    courses = courses_query.paginate(page=page, per_page=6)

    return render_template("courses.html", courses=courses, user=current_user)


@app.route('/course/<int:course_id>/assignments', endpoint='assignment_list')
def show_assignments(course_id):  # function name can be anything now
    course = Course.query.get_or_404(course_id)
    assignments = DSAAssignment.query.filter_by(course_id=course_id).all()
    return render_template('assignment_list.html', course=course, assignments=assignments)




@app.route('/termscondition')
def termscondition():
    return render_template('termscondition.html')

@app.route('/student-dashboard')
@login_required
def student_dashboard():
    # Get enrolled courses for the current user
    # Replace this with your actual query to get enrolled courses
    enrolled_courses = Course.query.filter_by(student_id=current_user.id).all()
    
    return render_template('student_dashboard.html', enrolled_courses=enrolled_courses)


# Instructor dashboard
@app.route('/instructor/dashboard')
def instructor_dashboard():
    courses = Course.query.all()
    return render_template('instructor-dashboard.html', courses=courses)

# Edit course route
@app.route('/edit-course/<int:course_id>', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('login'))

    course = Course.query.get_or_404(course_id)

    if request.method == 'POST':
        course.title = request.form['title']
        course.description = request.form['description']
        course.price = request.form['price']
        course.category = request.form['category']
        course.image = request.form['image']

        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('instructor_dashboard'))

    return render_template('editcourse.html', course=course)


# Delete course route
@app.route('/courses/<int:course_id>/delete')
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted successfully!')
    return redirect(url_for('instructor_dashboard'))



@app.route('/add-assignment/<int:course_id>', methods=['GET', 'POST'])
@login_required
def add_assignment(course_id):
    if current_user.role != 'admin':
        flash("Only instructors can add assignments!", "danger")
        return redirect(url_for('home'))

    course = Course.query.get_or_404(course_id)

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        difficulty = request.form.get('difficulty')
        due_date_str = request.form.get('due_date')

        # Convert string to datetime
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d %H:%M:%S') if due_date_str else None

        assignment = DSAAssignment(
        title=title,
        description=description,
        difficulty=difficulty,
        due_date=due_date,
        instructor_id=current_user.id,
        course=course
                     )


        db.session.add(assignment)
        db.session.commit()
        flash("Assignment added successfully!", "success")
        return redirect(url_for('instructor_dashboard'))  # Change to your dashboard route

    return render_template('add_assignment.html', course=course)


@app.route('/edit-assignment/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
def edit_assignment(assignment_id):
    assignment = DSAAssignment.query.get_or_404(assignment_id)

    # Only the instructor who created the assignment can edit it
    if current_user.role != 'admin' or assignment.instructor_id != current_user.id:
        flash("You are not authorized to edit this assignment!", "danger")
        return redirect(url_for('home'))

    course = assignment.course  # Get course object

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        difficulty = request.form.get('difficulty')
        due_date_str = request.form.get('due_date')

        # Convert string to date if provided
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d') if due_date_str else None
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
            return redirect(request.url)

        # Update assignment fields
        assignment.title = title
        assignment.description = description
        assignment.difficulty = difficulty
        assignment.due_date = due_date

        db.session.commit()
        flash("Assignment updated successfully!", "success")
        return redirect(url_for('assignment_list', course_id=assignment.course_id))

    return render_template('edit_assignment.html', assignment=assignment, course_title=course.title)


@app.route('/delete-assignment/<int:assignment_id>', methods=['GET','POST'])
@login_required
def delete_assignment(assignment_id):
    assignment = DSAAssignment.query.get_or_404(assignment_id)

    if current_user.id != assignment.instructor_id and current_user.role != 'admin':
        flash("You don't have permission to delete this assignment.", "danger")
        return redirect(url_for('home'))

    db.session.delete(assignment)
    db.session.commit()
    flash("Assignment deleted successfully.", "success")
    return redirect(url_for('instructor_dashboard'))



@app.route("/fullstack-web-development")
def fullstack_webdev():
    return render_template("webdev.html")

@app.route('/data-science')
def data_science():
    return render_template('datascience.html')

@app.route('/AIML')
def AIML():
    return render_template('AIML.html')

@app.route('/checkout')
def checkout():
    
        # Here, you would handle the payment processing
        # For demonstration, we'll just flash a success message
        
        return render_template('checkout.html')


# Route for Cart Page
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    course_id = request.form.get('course_id')
    course_name = request.form.get('course_name')
    price = float(request.form.get('price'))  # Convert price to float

    if 'cart' not in session:
        session['cart'] = []

    

    # Prevent duplicate courses in cart
    existing_item = next((item for item in session['cart'] if item['id'] == course_id), None)
    if existing_item:
        flash("Course is already in the cart!", "info")
    else:
        session['cart'].append({'id': course_id, 'name': course_name, 'price': price})
        session.modified = True
        flash("Course added to cart!", "success")

    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    total_price = sum(item['price'] for item in cart_items)  # Calculate total price
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@app.route('/remove_from_cart/<course_id>')
def remove_from_cart(course_id):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['id'] != course_id]
        session.modified = True
        flash("Course removed from cart!", "warning")

    return redirect(url_for('cart'))

@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)  # Remove cart from session
    flash("Cart cleared!", "danger")
    return redirect(url_for('cart'))


# Route for Language Selection (Placeholder)
@app.route('/language/<lang>')
def set_language(lang):
    return f"Language changed to {lang}"  # Placeholder, actual implementation needed

@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    flash("Logged out successfully", "success")
    # Add cache-control headers to prevent back button access
    response = redirect(url_for('login'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


#                                *********************************************************************
# API Routes
@app.route('/api/users', methods=['GET'])
# @login_required
# @admin_required
def api_get_users():
    users = User.query.all()
    users_list = [{
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.role,
        'mobile': user.mobile
    } for user in users]
    return jsonify(users_list)

@app.route('/api/user/<int:user_id>', methods=['GET'])
@login_required
def api_get_user(user_id):
    if current_user.id != user_id and current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.role,
        'mobile': user.mobile,
        'occupation': user.occupation,
        'interests': user.interests
    })

@app.route('/api/courses', methods=['GET'])
def api_get_courses():
    courses = Course.query.all()
    courses_list = [{
        'id': course.id,
        'title': course.title,
        'description': course.description,
        'price': course.price,
        'category': course.category,
        'image_url': course.image  # Use 'image' field from model
    } for course in courses]
    return jsonify(courses_list)

@app.route('/api/course/<int:course_id>', methods=['GET'])
def api_get_course(course_id):
    course = Course.query.get_or_404(course_id)
    return jsonify({
        'id': course.id,
        'title': course.title,
        'description': course.description,
        'price': course.price,
        'category': course.category,
        'instructor': course.instructor,  # Fixed field name
        'image_url': getattr(course, 'image_url', None)  # Safe access
    })
  
@app.route('/api/courses', methods=['POST'])

def api_create_course():
    
    # Get JSON data from request
    data = request.json
    
    # Validate required fields
    required_fields = ['title', 'description']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Get values from request data
    title = data.get('title')
    description = data.get('description')
    price = data.get('price', 0.0)
    category = data.get('category')
    image = data.get('image')
    
    # Create new course
    course = Course(
        title=title,
        description=description,
        price=price,
        category=category,
        image=image,
    )
    
    # Save to database
    db.session.add(course)
    db.session.commit()
    
    # Return success response with created course data
    return jsonify({
        "message": "Course created successfully",
        "course": {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "price": course.price,
            "category": course.category,
            "image": course.image
        }
    }), 201


@app.route('/api/course/<int:course_id>', methods=['PUT'])
def api_update_course(course_id):
    course = Course.query.get_or_404(course_id)
    data = request.get_json()

    if 'title' in data:
        course.title = data['title']
    if 'description' in data:
        course.description = data['description']
    if 'price' in data:
        course.price = data['price']
    if 'category' in data:
        course.category = data['category']
    if 'image' in data:
        course.image = data['image']

    db.session.commit()
    return jsonify({
        'id': course.id,
        'title': course.title,
        'description': course.description,
        'price': str(course.price),
        'category': course.category,
        'image': course.image
    })


@app.route('/api/course/<int:course_id>', methods=['DELETE'])
def api_delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    return jsonify({'message': 'Course deleted successfully'})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing email or password'}), 400
    
    # Admin login check
    ADMIN_EMAIL = "admin@example.com"
    ADMIN_PASSWORD = "admin123"
    
    if data['email'] == ADMIN_EMAIL:
        if data['password'] == ADMIN_PASSWORD:
            admin_user = User.query.filter_by(email=ADMIN_EMAIL).first()
            if not admin_user:
                admin_user = User(
                    name="Admin",
                    email=ADMIN_EMAIL,
                    role="admin"
                )
                admin_user.set_password(ADMIN_PASSWORD)
                db.session.add(admin_user)
                db.session.commit()
            
            login_user(admin_user)
            return jsonify({
                'message': 'Admin login successful',
                'user': {
                    'id': admin_user.id,
                    'name': admin_user.name,
                    'email': admin_user.email,
                    'role': admin_user.role
                }
            })
        else:
            return jsonify({'error': 'Invalid admin credentials'}), 401
    
    # Regular user login
    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    login_user(user)
    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role
        }
    })


@app.route('/api/logout', methods=['POST'])
# @login_required
def api_logout():
    logout_user()
    session.clear()
    response = jsonify({'message': 'Logged out successfully'})
    # Clear session cookies for API too if they exist
    response.set_cookie('session', '', expires=0)
    response.set_cookie('remember_token', '', expires=0)
    return response

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    try:
        new_user = User(
            name=data['name'],
            email=data['email'],
            mobile=data.get('mobile', ''),
            role="user"
        )
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': new_user.id,
                'name': new_user.name,
                'email': new_user.email,
                'role': new_user.role
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500
    
@app.route('/feedback', methods=['POST'])
def add_feedback():
    try:
        data = request.get_json()
        
        # Validate all required fields exist
        required_fields = ['course_id', 'student_id', 'rating']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate data types
        try:
            new_feedback = Feedback(
                course_id=int(data['course_id']),
                student_id=int(data['student_id']),
                rating=int(data['rating']),
                comment=str(data.get('comment', ''))
            )
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid data types'}), 400
        
        # Add to database
        db.session.add(new_feedback)
        db.session.commit()
        
        return jsonify({
            'message': 'Feedback added successfully',
            'feedback': {
                'id': new_feedback.id,
                'course_id': new_feedback.course_id,
                'student_id': new_feedback.student_id,
                'rating': new_feedback.rating,
                'comment': new_feedback.comment,
                'timestamp': new_feedback.timestamp.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error adding feedback: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.context_processor
def inject_user():
    return dict(session=session)


if __name__ == "__main__":
    with app.app_context():
        
        db.create_all()
    app.run(debug=True,port=5001)
