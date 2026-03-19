#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Role

# 创建应用实例
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# 在应用上下文中创建数据库表
with app.app_context():
    db.create_all()
    print('Database tables created successfully!')
