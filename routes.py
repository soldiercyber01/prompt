
import os
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify,session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import app
import razorpay
from extensions import db
from models import User, Category, Prompt, SavedPrompt, Sponsorship
import uuid

razorpay_client = razorpay.Client(auth=("rzp_live_RMas2O1baWS96w", "pWyiHH9vjXOJmHN8EgPiwPAy"))
app.permanent_session_lifetime = timedelta(days=7) 

@app.before_request
def check_subscription():
    if current_user.is_authenticated:
        if current_user.is_subscribed and current_user.subscription_expiry:
            print(current_user.subscription_expiry,datetime.now())
            if current_user.subscription_expiry <= datetime.utcnow():
                print("Subscription expired for user:", current_user.username)
                # Subscription expired → reset
                current_user.is_subscribed = 0
                current_user.subscription_expiry = None
                db.session.commit()

@app.route('/')
def index():
    category_id = request.args.get('category', type=int)
    # Sponsorships
    sponsorships = Sponsorship.query.filter(
        Sponsorship.is_active == True,
        db.or_(Sponsorship.expires_at.is_(None), Sponsorship.expires_at > datetime.utcnow())
    ).all()
    page = request.args.get('page', 1, type=int)   # default = page 1                                  # show 9 prompts at once
    per_page =28-len(sponsorships)
    categories = Category.query.all()

    query = Prompt.query
    if category_id:
        query = query.filter_by(category_id=category_id)

    prompts = query.order_by(Prompt.id.desc()).paginate(page=page, per_page=per_page)

    return render_template(
        'index.html',
        prompts=prompts,
        categories=categories,
        selected_category=category_id,
        sponsorships=sponsorships
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
   
     
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            session.permanent = True
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        flash('Registration successful!', 'success')
        return redirect(url_for('index'))
    
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))


@app.route('/add_prompt', methods=['GET', 'POST'])
@login_required
def add_prompt():
    categories = Category.query.all()
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        prompt_text = request.form['prompt_text']
        category_id = request.form['category_id']
        
        # Handle image - either upload or URL
        image_url = ''
        image_source = request.form.get('image_source', 'url')
        
        if image_source == 'upload' and 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Create unique filename
                name, ext = os.path.splitext(filename)
                unique_filename = f"{uuid.uuid4()}{ext}"
                
                # Ensure uploads directory exists
                upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'prompts')
                os.makedirs(upload_dir, exist_ok=True)
                
                file_path = os.path.join(upload_dir, unique_filename)
                file.save(file_path)
                
                image_url = f'/static/uploads/prompts/{unique_filename}'
            else:
                flash('Please select a valid image file (PNG, JPG, JPEG, GIF, WebP)', 'error')
                return render_template('add_prompt.html', categories=categories)
        else:
            image_url = request.form.get('image_url', '')
        
        if not image_url:
            flash('Please provide an image URL or upload an image file', 'error')
            return render_template('add_prompt.html', categories=categories)
        
        prompt = Prompt(
            title=title,
            description=description,
            prompt_text=prompt_text,
            image_url=image_url,
            user_id=current_user.id,
            category_id=category_id
        )
        
        db.session.add(prompt)
        db.session.commit()
        
        flash('Prompt added successfully!', 'success')
        return redirect(url_for('my_prompts'))
    
    return render_template('add_prompt.html', categories=categories)


@app.route('/my_prompts')
@login_required
def my_prompts():
    category_id = request.args.get('category', type=int)
    categories = Category.query.all()
    
    query = Prompt.query.filter_by(user_id=current_user.id)
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    prompts = query.all()
    
    return render_template('my_prompts.html', prompts=prompts[::-1], categories=categories, selected_category=category_id)


@app.route('/edit_prompt/<int:prompt_id>', methods=['POST'])
@login_required
def edit_prompt(prompt_id):
    prompt = Prompt.query.get_or_404(prompt_id)
    
    # Check if user owns this prompt
    if prompt.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    file = request.files['image_file']
    if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Create unique filename
            name, ext = os.path.splitext(filename)
            unique_filename = f"{uuid.uuid4()}{ext}"
            # Ensure uploads directory exists
            upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'prompts')
            os.makedirs(upload_dir, exist_ok=True)
                
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
                
            image_url = f'/static/uploads/prompts/{unique_filename}'

    prompt.title = request.form['title']
    prompt.description = request.form['description']
    prompt.prompt_text = request.form['prompt_text']
    prompt.image_url = image_url if file and file.filename else request.form['image_url']
    prompt.category_id = request.form['category_id']
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Prompt updated successfully'})


@app.route('/delete_prompt/<int:prompt_id>', methods=['POST'])
@login_required
def delete_prompt(prompt_id):
    prompt = Prompt.query.get_or_404(prompt_id)
    
    # Check if user owns this prompt
    if prompt.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    db.session.delete(prompt)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Prompt deleted successfully'})


@app.route('/saved_prompts')
@login_required
def saved_prompts():
    saved = db.session.query(Prompt).join(SavedPrompt).filter(SavedPrompt.user_id == current_user.id).all()
    return render_template('saved_prompts.html', prompts=saved[::-1])


@app.route('/save_prompt/<int:prompt_id>', methods=['POST'])
@login_required
def save_prompt(prompt_id):
    # Check if already saved
    existing = SavedPrompt.query.filter_by(user_id=current_user.id, prompt_id=prompt_id).first()
    
    if existing:
        return jsonify({'success': False, 'message': 'Prompt already saved'})
    
    saved_prompt = SavedPrompt(user_id=current_user.id, prompt_id=prompt_id)
    db.session.add(saved_prompt)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Prompt saved successfully'})


@app.route('/unsave_prompt/<int:prompt_id>', methods=['POST'])
@login_required
def unsave_prompt(prompt_id):
    saved_prompt = SavedPrompt.query.filter_by(user_id=current_user.id, prompt_id=prompt_id).first()
    
    if saved_prompt:
            db.session.delete(saved_prompt)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Prompt removed from saved'})
    
    return jsonify({'success': False, 'message': 'Prompt not found in saved'})


@app.route('/subscription',methods=['GET','POST'])
def subscription():
    if request.method=='POST':
        return render_template('subscription.html')
    return render_template('subscription.html')


@app.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    if request.method == 'POST':
        plan = request.form.get('plan')
        amount = int(request.form.get('amount'))
        duration = int(request.form.get('duration', '1'))
        
        plan_names = {'monthly': 'Monthly', 'quarterly': 'Quarterly'}
        plan_name = plan_names.get(plan) if plan else 'Unknown'
        
        order = razorpay_client.order.create(dict(
            amount=amount*100,
            currency="INR",
            payment_capture="1"
        ))

        return render_template('payment.html', 
                                plan=plan, 
                                plan_name=plan_name,
                                amount=amount, 
                                duration=duration,
                                order_id=order['id'],
                                razorpay_key="rzp_live_RMas2O1baWS96w")
    return redirect(url_for('subscription'))


@app.route('/process_payment')
@login_required
def process_payment():
    success = request.args.get('success') == 'true'
    plan = request.args.get('plan')
    duration = int(request.args.get('duration', 1))
    
    if success:
        # Update user subscription
        current_user.is_subscribed = True
        current_user.subscription_expiry = datetime.utcnow() + timedelta(days=30 * duration)
        db.session.commit()
        
        flash(f'Payment successful! Your subscription is now active. for {plan.capitalize()} plan', 'success')
    else:
        flash('Payment failed. Please try again.', 'error')
    
    return redirect(url_for('index'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Handle profile picture upload
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and file.filename:
                filename = secure_filename(file.filename)
                # Create unique filename
                name, ext = os.path.splitext(filename)
                unique_filename = f"{uuid.uuid4()}{ext}"
                
                # Ensure uploads directory exists
                upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'profiles')
                os.makedirs(upload_dir, exist_ok=True)
                
                file_path = os.path.join(upload_dir, unique_filename)
                file.save(file_path)
                
                # Store relative path in database
                current_user.profile_pic = f'/static/uploads/profiles/{unique_filename}'
        
        # Update Instagram ID
        instagram_id = request.form.get('instagram_id', '').strip()
        current_user.instagram_id = instagram_id if instagram_id else None
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html')


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/get_prompt/<int:prompt_id>')
def get_prompt(prompt_id):
    prompt = Prompt.query.get_or_404(prompt_id)
    is_saved = False
    
    if current_user.is_authenticated:
        is_saved = SavedPrompt.query.filter_by(user_id=current_user.id, prompt_id=prompt_id).first() is not None
    
    return jsonify({
        'id': prompt.id,
        'title': prompt.title,
        'description': prompt.description,
        'prompt_text': prompt.prompt_text,
        'image_url': prompt.image_url,
        'category': prompt.category.name,
        'creator': prompt.creator.username,
        'created_at': prompt.created_at.strftime('%B %d, %Y'),
        'creator_profile_pic': prompt.creator.profile_pic,
        'creator_instagram': prompt.creator.instagram_id,
        'is_saved': is_saved,
        'can_edit': current_user.is_authenticated and prompt.user_id == current_user.id,
        'can_view_details': current_user.is_authenticated and (current_user.is_subscribed or (current_user.subscription_expiry and current_user.subscription_expiry > datetime.utcnow()))
    })


@app.route('/upgrade_subscription', methods=['POST'])
@login_required
def upgrade_subscription():
    # In a real app, this would integrate with a payment processor
    current_user.is_subscribed = True
    db.session.commit()
    
    flash('Subscription upgraded successfully!', 'success')
    return redirect(url_for('index'))


# Admin routes for sponsorship management
@app.route('/admin/sponsorships')
@login_required
def admin_sponsorships():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    sponsorships = Sponsorship.query.order_by(Sponsorship.created_at.desc()).all()
    return render_template('admin_sponsorships.html', sponsorships=sponsorships)


@app.route('/admin/add_sponsorship', methods=['GET', 'POST'])
@login_required
def add_sponsorship():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        client_name = request.form['client_name']
        redirect_url = request.form['redirect_url']
        expires_at = request.form.get('expires_at')
        
        # Handle image - either upload or URL
        image_url = ''
        image_source = request.form.get('image_source', 'url')
        
        if image_source == 'upload' and 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Create unique filename
                name, ext = os.path.splitext(filename)
                unique_filename = f"{uuid.uuid4()}{ext}"
                
                # Ensure uploads directory exists
                upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'sponsorships')
                os.makedirs(upload_dir, exist_ok=True)
                
                file_path = os.path.join(upload_dir, unique_filename)
                file.save(file_path)
                
                image_url = f'/static/uploads/sponsorships/{unique_filename}'
            else:
                flash('Please select a valid image file (PNG, JPG, JPEG, GIF, WebP)', 'error')
                return render_template('add_sponsorship.html')
        else:
            image_url = request.form.get('image_url', '')
        
        if not image_url:
            flash('Please provide an image URL or upload an image file', 'error')
            return render_template('add_sponsorship.html')
        
        # Parse expiry date if provided
        expires_at_date = None
        if expires_at:
            try:
                expires_at_date = datetime.strptime(expires_at, '%Y-%m-%d')
            except ValueError:
                flash('Invalid expiry date format', 'error')
                return render_template('add_sponsorship.html')
        
        sponsorship = Sponsorship(
            title=title,
            description=description,
            image_url=image_url,
            client_name=client_name,
            redirect_url=redirect_url,
            expires_at=expires_at_date,
            admin_id=current_user.id
        )
        
        db.session.add(sponsorship)
        db.session.commit()
        
        flash('Sponsorship added successfully!', 'success')
        return redirect(url_for('admin_sponsorships'))
    
    return render_template('add_sponsorship.html')


@app.route('/admin/toggle_sponsorship/<int:sponsorship_id>', methods=['POST'])
@login_required
def toggle_sponsorship(sponsorship_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    sponsorship = Sponsorship.query.get_or_404(sponsorship_id)
    sponsorship.is_active = not sponsorship.is_active
    db.session.commit()
    
    status = 'activated' if sponsorship.is_active else 'deactivated'
    return jsonify({'success': True, 'message': f'Sponsorship {status} successfully'})


@app.route('/admin/delete_sponsorship/<int:sponsorship_id>', methods=['POST'])
@login_required
def delete_sponsorship(sponsorship_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    sponsorship = Sponsorship.query.get_or_404(sponsorship_id)
    db.session.delete(sponsorship)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Sponsorship deleted successfully'})


@app.route('/sponsorship/<int:sponsorship_id>')
def view_sponsorship(sponsorship_id):
    sponsorship = Sponsorship.query.get_or_404(sponsorship_id)
    
    if not sponsorship.is_active:
        flash('This sponsorship is no longer available.', 'error')
        return redirect(url_for('index'))
    
    # Check if expired
    if sponsorship.expires_at and sponsorship.expires_at < datetime.utcnow():
        flash('This sponsorship has expired.', 'error')
        return redirect(url_for('index'))
    
    return render_template('sponsorship_detail.html', sponsorship=sponsorship)

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy-policy.html')

@app.route('/terms-conditions')
def terms_conditions():
    return render_template('terms-conditions.html')

@app.route('/shipping-delivery')
def shipping_delivery():
    return render_template('shipping-delivery.html')

@app.route('/contact-us')
def contact_us():
    return render_template('contact-us.html')

@app.route('/cancellation-refund')
def cancellation_refund():
    return render_template('cancellation-refund.html')
