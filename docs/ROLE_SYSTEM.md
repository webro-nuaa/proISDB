# InsertQ 角色系统说明

## 角色层级

InsertQ系统现在支持三种用户角色：

### 1. Root（超级管理员）
- **权限**：拥有系统最高权限
  - 所有admin权限
  - 创建admin账号
  - 禁用/启用admin账号
  - 删除admin账号
  - 管理员账号管理
- **数量**：建议只有1-2个root账号
- **邮箱**：创建时必须提供邮箱
- **创建方式**：`flask create-root`

### 2. Admin（管理员）
- **权限**：
  - 管理IS元素数据
  - 审核用户提交
  - 管理知识库文章
  - 查看系统统计
  - 批量导入数据
- **限制**：不能管理其他admin账号
- **邮箱**：创建时可选，后续可补充和验证
- **创建方式**：只能由root用户通过Web界面的Admin Management创建

### 3. Visitor（访客）
- **权限**：
  - 浏览公开内容
  - 提交IS元素数据
  - 浏览知识库
  - 搜索数据
- **邮箱**：注册时可选
- **创建方式**：用户自主注册

## 邮箱策略

### 设计理念

- **Root用户**：必须提供邮箱，确保系统管理员可联系
- **Admin用户**：邮箱可选，允许快速创建账号
  - 初始创建时可以不填邮箱
  - 后续通过邮箱验证功能补充
  - 便于测试和临时账号管理
- **Visitor用户**：邮箱可选，降低注册门槛

### 邮箱验证（待实现）

未来可以添加邮箱验证功能：
1. 用户补充邮箱地址
2. 发送验证链接
3. 确认邮箱有效性
4. 用于密码找回等功能

## 数据库迁移

### 从旧版本升级

如果你的数据库是旧版本，需要执行以下迁移：

#### 1. 添加root角色
```bash
# 运行迁移脚本
python migrate_add_root_role.py

# 创建第一个root用户
flask create-root

# 或者将现有admin提升为root
mysql -u root -p insertq_db -e "UPDATE users SET role='root' WHERE username='your_admin_username';"
```

#### 2. 将email字段改为可选
```bash
# 运行迁移脚本
python migrate_email_optional.py
```

迁移说明：
- email字段从NOT NULL改为NULL
- 保持unique索引不变（有email时仍需唯一）
- 现有用户数据不受影响

## 管理员管理功能

### Root用户专属功能

访问路径：Admin Panel → Admin Management

功能包括：
1. **查看所有管理员** - 列出所有root和admin账号
2. **创建Admin账号** - 创建新的admin用户
3. **禁用Admin** - 暂时禁用admin账号（不删除数据）
4. **启用Admin** - 重新启用被禁用的admin账号
5. **删除Admin** - 永久删除admin账号（需要先清理关联数据）

### 保护机制

- Root账号不能被禁用或删除
- 删除admin前会检查是否有关联数据：
  - 提交的IS元素
  - 审核的IS元素
  - 创建的文章
- 有关联数据的admin不能直接删除，需要先转移或删除数据

## 代码中的权限检查

### 使用方法

```python
# 检查是否为root
if current_user.is_root():
    # 只有root可以执行的操作
    pass

# 检查是否为admin（不包括root）
if current_user.is_admin():
    # 只有admin可以执行的操作
    pass

# 检查是否具有管理员权限（包括root和admin）
if current_user.has_admin_permission():
    # root和admin都可以执行的操作
    pass
```

### 路由保护示例

```python
@admin.route('/admins')
@login_required
def manage_admins():
    """管理员账号管理（仅root可访问）"""
    if not current_user.is_root():
        flash('只有ROOT用户可以访问此页面。', 'error')
        return redirect(url_for('admin.index'))
    # ...

@admin.route('/is-elements')
@login_required
def is_elements():
    """IS元素管理（root和admin都可访问）"""
    if not current_user.has_admin_permission():
        flash('您没有权限访问此页面。', 'error')
        return redirect(url_for('admin.login'))
    # ...
```

## 命令行工具

### 创建Root用户

```bash
# 创建root用户（超级管理员）- 仅在初始化系统时使用
flask create-root

# 注意：Admin用户只能通过Web界面由root创建
```

### 数据库操作

```bash
# 创建数据库
flask init-db

# 重置数据库
flask reset-db --drop
```

### 查看用户

```bash
# 查看所有用户
mysql -u root -p insertq_db -e "SELECT id, username, email, role, is_active FROM users;"

# 查看管理员用户
mysql -u root -p insertq_db -e "SELECT id, username, email, role, is_active FROM users WHERE role IN ('root', 'admin');"
```

## 安全建议

1. **Root账号管理**
   - 只创建必要数量的root账号（建议1-2个）
   - 使用强密码
   - 定期更换密码
   - 记录root账号的操作日志

2. **Admin账号管理**
   - 根据实际需要创建admin账号
   - 离职人员及时禁用账号
   - 定期审查admin账号列表
   - 不再使用的账号及时删除

3. **操作日志**
   - 所有admin管理操作都会记录在`admin_logs`表中
   - 可以追踪谁创建、禁用或删除了哪个账号
   - 建议定期审查操作日志

## 常见问题

### Q1: 如何将现有admin提升为root？

```bash
mysql -u root -p insertq_db
```

```sql
UPDATE users SET role='root' WHERE username='your_admin_username';
```

### Q2: 忘记root密码怎么办？

通过数据库直接重置：

```sql
-- 首先生成新密码的哈希值（使用bcrypt）
-- 然后更新数据库
UPDATE users 
SET password_hash='$2b$12$...' 
WHERE username='root_username';
```

或者创建新的root账号。

### Q3: 可以有多个root账号吗？

可以，但建议只保留1-2个root账号，以便于管理和安全控制。

### Q4: admin可以看到Admin Management页面吗？

不可以，只有root用户可以访问Admin Management功能。

### Q5: 删除admin会影响他创建的数据吗？

- IS元素：设置了外键`ON DELETE SET NULL`，删除admin后submitter_id会变为NULL
- 文章：设置了`ON DELETE CASCADE`，删除admin会同时删除其创建的文章
- 因此在删除admin前，系统会检查并提示有关联数据

## 更新日志

- **2026-01-23**：添加root角色和admin管理功能
  - 新增root角色
  - 新增admin管理界面
  - 新增create-root命令
  - 更新权限检查逻辑
  - 添加数据库迁移脚本
