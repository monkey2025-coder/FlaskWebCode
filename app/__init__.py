from flask import Flask, render_template 
from flask_bootstrap import Bootstrap 
from flask_moment import Moment 
from flask_sqlalchemy import SQLAlchemy 
from config import config 
from flask_login import LoginManager 
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_pagedown import PageDown 

bootstrap = Bootstrap() 
moment = Moment() 
db = SQLAlchemy()
csrf = CSRFProtect()
migrate = Migrate()
pagedown = PageDown() 

login_manager = LoginManager() 
login_manager.session_protection = 'strong' 
login_manager.login_view = 'auth.login' 

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))

def create_app(config_name='default'): 
    app = Flask(__name__) 

    app.config.from_object(config[config_name])
    
    config[config_name].init_app(app) 
    bootstrap.init_app(app)  
    moment.init_app(app) 
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    pagedown.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint) 
    
    # 导入Permission并添加到模板上下文
    from .models import Permission
    @app.context_processor 
    def inject_permissions(): 
        return dict(Permission=Permission)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # 设置匿名用户类
    from .models import AnonymousUser
    login_manager.anonymous_user = AnonymousUser

    return app

# 创建默认应用实例，供Flask CLI使用
app = create_app()