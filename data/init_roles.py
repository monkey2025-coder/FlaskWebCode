#!/usr/bin/env python
import os
from app import create_app, db
from app.models import Role

# 创建应用实例
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# 在应用上下文中初始化权限表
with app.app_context():
    # 调用 insert_roles() 方法初始化权限表
    Role.insert_roles()
    print('权限表初始化成功！')
    print('已创建以下角色：')
    for role in Role.query.all():
        print(f'- {role.name} (权限: {role.permissions}, 默认: {role.default})')
