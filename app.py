import os
from flask import Flask
from flask_login import LoginManager
# from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from extensions import db

login_manager = LoginManager()

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "devsecret")  # fallback if not set
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate https


db_url = os.getenv("CLEARDB_DATABASE_URL")  # e.g. mysql://user:pass@host/db?reconnect=true
if db_url and db_url.startswith("mysql://"):
    db_url = db_url.replace("mysql://", "mysql+pymysql://", 1)

# Local dev fallback (encode special chars in password)
db_url = db_url or "mysql+pymysql://hardik:hardik%40005@localhost/prompt_gallery?charset=utf8mb4"

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


# initialize login manager
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

with app.app_context():
    import models  # import models so tables are registered
    db.create_all()
    models.init_sample_data()  # insert sample data
    import routes  # import routes last (after db + models setup)



# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)
