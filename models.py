from extensions import db
from flask_login import UserMixin
from datetime import datetime


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_subscribed = db.Column(db.Boolean, default=False, nullable=False)
    subscription_expiry = db.Column(db.DateTime, nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    profile_pic = db.Column(db.String(500), nullable=True)
    instagram_id = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    otp_code = db.Column(db.String(10), nullable=True)
    is_otp_verified = db.Column(db.Boolean, default=False, nullable=False)
    last_otp_sent = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    prompts = db.relationship('Prompt', backref='creator', lazy=True, cascade='all, delete-orphan')
    saved_prompts = db.relationship('SavedPrompt', backref='user', lazy=True, cascade='all, delete-orphan')


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Relationships
    prompts = db.relationship('Prompt', backref='category', lazy=True)


class Prompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    prompt_text = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    
    # Relationships
    saved_by = db.relationship('SavedPrompt', backref='prompt', lazy=True, cascade='all, delete-orphan')


class SavedPrompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    prompt_id = db.Column(db.Integer, db.ForeignKey('prompt.id'), nullable=False)


class Sponsorship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    redirect_url = db.Column(db.String(500), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    # Foreign Keys
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


def init_sample_data():
    """Initialize sample categories and prompts with stock photos"""
    
    # Check if data already exists
    if Category.query.first():
        return
    
    # Create categories
    categories = [
        {'name': 'Design & Art', 'description': 'Creative prompts for design and artistic projects'},
        {'name': 'Content Writing', 'description': 'Writing prompts for content creation'},
        {'name': 'Marketing', 'description': 'Marketing and advertising prompts'},
        {'name': 'Coding', 'description': 'Programming and development prompts'},
        {'name': 'Business', 'description': 'Business strategy and planning prompts'}
    ]
    
    for cat_data in categories:
        category = Category(**cat_data)
        db.session.add(category)
    
    db.session.commit()
    
    # Create a demo user
    from werkzeug.security import generate_password_hash
    demo_user = User(
        username='demo_user',
        email='demo@example.com',
        password_hash=generate_password_hash('demo123'),
        is_subscribed=False
    )
    db.session.add(demo_user)
    
    subscribed_user = User(
        username='premium_user',
        email='premium@example.com',
        password_hash=generate_password_hash('premium123'),
        is_subscribed=True
    )
    db.session.add(subscribed_user)
    
    admin_user = User(
        username='Admin Hardik',
        email='hardik@gmail.com',
        password_hash=generate_password_hash('Hardik@005'),
        is_subscribed=True,
        is_admin=True
    )
    db.session.add(admin_user)
    
    db.session.commit()
    db.session.refresh(demo_user)
    db.session.refresh(subscribed_user)
    
    # Stock photos data
    # stock_photos = {
    #     'ai generated artwork': [
    #         'https://pixabay.com/get/g431fa5955c1a886c1ed01b52aecde0dc1ab5b13b2b7dbf0adfe2b6bfbf5345fae76ef8e8b69d0909a8a4c309ec2e02332dc9156b9b002b3eb7e20792cefba944_1280.jpg',
    #         'https://pixabay.com/get/g10ee9e0ec9fc628d10369d7e40e71192fbefaab6f479dc9f3ff9c7e86dedbf091f7542e7bba1dabe49fef4ff1c6a0ae5055506ca2828119edaf2ab29b2c34d4d_1280.jpg',
    #         'https://pixabay.com/get/gcd5d03bd96c96e341b7c003cc64979aca3e214d1906eb6863b94c0c60c85b2dbf1d4c13e17518404e5e5349fe8d18c8d18dfc660db2f439018709aa22501798a_1280.jpg',
    #         'https://pixabay.com/get/gf78ae1fa697ac23cd0f6cd3dd8ee2fb618fffcb131bb8dad02c973592e152f7eead37781e13ce3daa55d7517a1d74aec2ae2c759ea2268e889bb379baa632f75_1280.jpg',
    #         'https://pixabay.com/get/g4670ac5dedcdd908197a633104e6a40929702ca54e24c5b041e596f0556c4cec4f183f3e02715feeb7e475f94e64cb24365fcc8c99019955197b97c37e9303eb_1280.jpg',
    #         'https://pixabay.com/get/g2a88b8d589956e0ec43aa2c1dbf2dee0e971e5bae09c8d1d9d44586b5712ca5483bccc09b6f42f783dbd4b7378cf3f8eaaca756cd6699f1193ad2837af6a5892_1280.jpg',
    #         'https://pixabay.com/get/g808d9279057e1714c903dcf9c05f1f2cb19e8cf26b8b62f0c665025a4c2f3366319bb14166cd68d39532e11b0e340676fcecc827521e97eebe6cfcfee48d4153_1280.jpg',
    #         'https://pixabay.com/get/g2e6b03619ca958d526c0888cdc7a9458b358a2b4452093046c0db3823b0f38008c023a0cb475e4cfb00ca124294750e46a5ce2c6db09a4be781aa6309199b7a8_1280.jpg'
    #     ],
    #     'digital art prompts': [
    #         'https://pixabay.com/get/gd7398612b0969e8d4696db7601a98167b35fab9a94d5296b7c8db2f3975483669d0c0b9b066a32a3266953e68c06f980faeed9216e958edbe735d77f02685fec_1280.jpg',
    #         'https://pixabay.com/get/ga28790244309245362a6bd809787dfe9ee5c3c08e41787fe59847dc4cba1d02e2f568671cf344973ff1f69edbf4d1429b614366449a5a7e3fc2dcd8ff0cfa9bc_1280.jpg',
    #         'https://pixabay.com/get/g1385c3ff9b10a8413e227b5138bd6278cbd89aeabe8284e1e72ab33bc68ca91100e3e2f7d4640e29898dd366462e0c86e2953aad6f18b4f7d4c257f43aad0b12_1280.jpg',
    #         'https://pixabay.com/get/g87833dacd05f7df295a190ec7d51eb015ffc13c4937f5d1871e960df7a1f1ccfeeee0ced1f9e3d8f080618df74f7f2b031c3e355cf381dd64f6e1707d4066060_1280.jpg',
    #         'https://pixabay.com/get/g211929e4a56ea4f6a827e9d82d607c786e81e96e16fdd358e2bd6a698a5900024972b9d25c1c2b9655ff250b2a9e96c891a11c244ef374edff60da41eeab81ed_1280.jpg',
    #         'https://pixabay.com/get/ge53eff530047faed0ba79881d7fc788850bc7add0d228196a7ca1ab66df7e43cf90ab0abe430e40ff7c509c41e4768a9e3bcb7cc802951b9f39c70963a3e7941_1280.jpg'
    #     ],
    #     'creative illustrations': [
    #         'https://pixabay.com/get/gc97b34ae5a2ddb017dad214def4b951cbdecd823375d43ba36151a9ac202d4ed7cdbc5fd0ea02c02e3dee07fae5e14544ce759b259f0bac160b9648242d6f126_1280.jpg',
    #         'https://pixabay.com/get/gbcc4f1b2311c39385acf8f638d8dce4a233880f8eb41469bb30329b35cf2398c584700c42b5e4a33c4f2112af59bc46b2dff77fae6886e2e432233dd94787940_1280.jpg',
    #         'https://pixabay.com/get/ga3e171bd779bcd892517612c10b701066ea82e237540fa35ba36815918216bbee6e958caabd412a00133ebacf55ff7c1d7dc7069fc52e4e3dbc84ef2edd9664d_1280.jpg',
    #         'https://pixabay.com/get/gdcd4583739fc7822a70db3a38ccaa4166374871f2e984b98686eae2a1052311e1a56557bde74e0a21f2cc1559a7fa91d95cc07d5acc87ce8f157cc95ea6bacaa_1280.jpg'
    #     ]
    # }
    
    # # Create sample prompts
    # design_category = Category.query.filter_by(name='Design & Art').first()
    
    # # AI Generated Artwork prompts
    # ai_prompts = [
    #     {'title': 'Futuristic Cityscape', 'description': 'Create a stunning futuristic cityscape with neon lights and flying vehicles', 'prompt': 'Generate a cyberpunk cityscape at night with neon lighting, flying cars, and towering skyscrapers'},
    #     {'title': 'Abstract Digital Art', 'description': 'Abstract digital composition with vibrant colors and geometric shapes', 'prompt': 'Create an abstract digital artwork using vibrant colors, geometric patterns, and fluid forms'},
    #     {'title': 'Fantasy Character Portrait', 'description': 'Detailed fantasy character with mystical elements', 'prompt': 'Generate a fantasy character portrait with magical elements, detailed armor, and mystical background'},
    #     {'title': 'Surreal Landscape', 'description': 'Dreamlike landscape with impossible architecture', 'prompt': 'Create a surreal landscape with floating islands, impossible architecture, and dreamlike atmosphere'},
    #     {'title': 'Digital Nature Scene', 'description': 'Nature scene enhanced with digital art techniques', 'prompt': 'Generate a nature scene using digital art techniques with enhanced colors and magical elements'},
    #     {'title': 'Retro Futurism Art', 'description': 'Retro-futuristic art style with vintage sci-fi elements', 'prompt': 'Create retro-futuristic artwork with vintage sci-fi elements and retro color palette'},
    #     {'title': 'Minimalist Digital Design', 'description': 'Clean minimalist design with modern aesthetics', 'prompt': 'Generate minimalist digital design with clean lines, modern aesthetics, and balanced composition'},
    #     {'title': 'Cosmic Digital Art', 'description': 'Space-themed artwork with cosmic elements', 'prompt': 'Create cosmic digital artwork with nebulas, stars, planets, and space phenomena'}
    # ]
    
    # digital_prompts = [
    #     {'title': 'Logo Design Concept', 'description': 'Modern logo design for tech startup', 'prompt': 'Design a modern logo for a technology startup with clean typography and innovative iconography'},
    #     {'title': 'UI Interface Design', 'description': 'User interface design for mobile app', 'prompt': 'Create a clean and intuitive user interface design for a mobile productivity app'},
    #     {'title': 'Brand Identity Package', 'description': 'Complete brand identity with colors and typography', 'prompt': 'Develop a comprehensive brand identity package including color palette, typography, and visual elements'},
    #     {'title': 'Infographic Layout', 'description': 'Data visualization infographic design', 'prompt': 'Design an engaging infographic layout for presenting complex data in an accessible format'},
    #     {'title': 'Website Landing Page', 'description': 'Modern landing page design concept', 'prompt': 'Create a modern landing page design with compelling visuals and clear call-to-action elements'},
    #     {'title': 'Social Media Graphics', 'description': 'Social media post templates and graphics', 'prompt': 'Design social media graphics templates with consistent branding and engaging visual elements'}
    # ]
    
    # illustration_prompts = [
    #     {'title': 'Character Illustration', 'description': 'Unique character design with personality', 'prompt': 'Illustrate a unique character with distinct personality traits, clothing, and expressive features'},
    #     {'title': 'Book Cover Design', 'description': 'Eye-catching book cover illustration', 'prompt': 'Create an eye-catching book cover illustration that captures the essence of the story'},
    #     {'title': 'Editorial Illustration', 'description': 'Illustration for magazine article', 'prompt': 'Design an editorial illustration that complements and enhances a magazine article'},
    #     {'title': 'Children\'s Book Art', 'description': 'Whimsical illustration for children\'s book', 'prompt': 'Create whimsical illustrations for a children\'s book with bright colors and engaging characters'}
    # ]
    
    # # Add AI artwork prompts
    # for i, prompt_data in enumerate(ai_prompts):
    #     prompt = Prompt(
    #         title=prompt_data['title'],
    #         description=prompt_data['description'],
    #         prompt_text=prompt_data['prompt'],
    #         image_url=stock_photos['ai generated artwork'][i],
    #         user_id=demo_user.id,
    #         category_id=design_category.id
    #     )
    #     db.session.add(prompt)
    
    # # Add digital art prompts
    # for i, prompt_data in enumerate(digital_prompts):
    #     prompt = Prompt(
    #         title=prompt_data['title'],
    #         description=prompt_data['description'],
    #         prompt_text=prompt_data['prompt'],
    #         image_url=stock_photos['digital art prompts'][i],
    #         user_id=subscribed_user.id,
    #         category_id=design_category.id
    #     )
    #     db.session.add(prompt)
    
    # # Add illustration prompts
    # for i, prompt_data in enumerate(illustration_prompts):
    #     prompt = Prompt(
    #         title=prompt_data['title'],
    #         description=prompt_data['description'],
    #         prompt_text=prompt_data['prompt'],
    #         image_url=stock_photos['creative illustrations'][i],
    #         user_id=demo_user.id,
    #         category_id=design_category.id
    #     )
    #     db.session.add(prompt)
    
    db.session.commit()
