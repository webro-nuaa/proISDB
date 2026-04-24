# Email字段变更说明

## 修改内容

将用户表的email字段从必填改为可选（除Root用户外）。

## 修改的文件

### 1. 数据库层
- **insertq_db.sql** - email字段改为 `DEFAULT NULL`
- **app/models/user.py** - email列改为 `nullable=True`

### 2. 表单验证层
- **app/forms/admin_management.py**
  - 移除email的`DataRequired`验证
  - 修改验证逻辑，只在有值时检查唯一性

### 3. 视图层
- **app/views/admin.py**
  - 创建admin时，email使用 `form.email.data or None`
  - 日志记录时标记email状态

### 4. 模板层
- **app/templates/admin/create_admin.html**
  - 移除必填标记`*`
  - 添加`(Optional)`提示
- **app/templates/admin/admins.html**
  - 显示"Not set"当email为空时

### 5. CLI命令
- **run.py**
  - `create-admin`命令：email参数改为optional
  - 添加无邮箱提示信息
  - `create-root`命令：保持email必填

### 6. 迁移脚本
- **migrate_email_optional.py** - 数据库迁移脚本

### 7. 文档
- **docs/ROLE_SYSTEM.md** - 更新邮箱策略说明

## 使用方式

### 创建Root用户（邮箱必填）
```bash
flask create-root
# 会提示输入username, email, password
```

### 创建Admin用户（邮箱可选）

**只能通过Web界面创建：**
1. Root用户登录系统
2. 访问 Admin Panel → Admin Management
3. 点击 "Create New Admin"
4. 填写用户名和密码（邮箱为可选字段）

**注意**：为了安全性，系统已移除命令行创建admin的功能。所有admin账号必须由root用户通过Web界面创建和管理。

## 数据库迁移

```bash
# 执行迁移
python migrate_email_optional.py
```

迁移脚本会：
1. 检查当前email字段状态
2. 询问确认
3. 将email字段改为NULL
4. 显示修改后的状态和用户统计

## 验证

迁移后验证：
```sql
-- 检查字段定义
DESCRIBE users;

-- 查看email分布
SELECT 
    role,
    COUNT(*) as total,
    SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END) as without_email,
    SUM(CASE WHEN email IS NOT NULL THEN 1 ELSE 0 END) as with_email
FROM users
GROUP BY role;
```

## 设计理念

1. **Root用户必须有邮箱** - 确保系统管理员可联系
2. **Admin用户邮箱可选** - 允许快速创建测试账号
3. **后续邮箱验证** - 可以后续补充邮箱并进行验证
4. **降低使用门槛** - 简化初始账号创建流程

## 注意事项

- 现有用户数据不受影响
- email的unique约束保持不变（有email时必须唯一）
- 后续可以添加邮箱验证功能
- 建议为重要账号补充邮箱用于密码找回

## 更新日期

2026-01-24
