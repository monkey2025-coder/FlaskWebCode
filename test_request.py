import sys
from app import app

with app.test_request_context('/'):
    try:
        # 导入必要的模块
        from app.models import User, Post, Permission
        from flask_login import current_user
        
        # 测试数据库连接
        from app import db
        print("Database connected successfully")
        
        # 测试查询
        posts = Post.query.all()
        print(f"Found {len(posts)} posts")
        
        # 测试模板渲染
        from flask import render_template
        template = render_template('index.html', form=None, posts=[], pagination=None, current_time=None)
        print("Template rendered successfully")
        
    except Exception as e:
        print(f"Error during request processing: {e}")
        import traceback
        traceback.print_exc()
