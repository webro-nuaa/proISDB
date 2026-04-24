# 邮箱验证功能配置指南

## 概述

InsertQ现在支持邮箱验证功能。用户可以添加和验证他们的邮箱地址，系统会发送验证码到用户邮箱进行验证。

## 功能特点

- ✉️ 验证码通过邮件发送
- ⏱️ 验证码15分钟有效期
- 🔒 最多5次验证尝试
- 🎯 Root用户邮箱作为官方发件地址
- 📝 完整的验证日志记录
- 🛡️ 防止重复邮箱注册

## 配置步骤

### 1. 配置环境变量

在 `.env` 文件中添加以下配置：

```bash
# 邮件服务器配置
MAIL_SERVER=smtp.gmail.com           # SMTP服务器地址
MAIL_PORT=587                        # SMTP端口（TLS通常用587，SSL用465）
MAIL_USE_TLS=true                    # 是否使用TLS
MAIL_USERNAME=your.email@gmail.com   # 发件邮箱
MAIL_PASSWORD=your_app_password      # 邮箱应用密码
```

### 2. 常用邮件服务商配置

#### Gmail
```bash
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your.email@gmail.com
MAIL_PASSWORD=your_app_password  # 需要生成应用专用密码
```

**注意**：Gmail需要启用"两步验证"并生成"应用专用密码"
1. 访问 https://myaccount.google.com/security
2. 启用两步验证
3. 生成应用专用密码

#### QQ邮箱
```bash
MAIL_SERVER=smtp.qq.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your_qq@qq.com
MAIL_PASSWORD=your_authorization_code  # 需要开启SMTP并获取授权码
```

#### 163邮箱
```bash
MAIL_SERVER=smtp.163.com
MAIL_PORT=465
MAIL_USE_TLS=false  # 163使用SSL
MAIL_USERNAME=your_email@163.com
MAIL_PASSWORD=your_authorization_code
```

#### Outlook/Hotmail
```bash
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your_email@outlook.com
MAIL_PASSWORD=your_password
```

### 3. 运行数据库迁移

```bash
python migrate_add_email_verification.py
```

这将创建 `email_verifications` 表来存储验证码记录。

### 4. 重启应用

```bash
flask run
# 或
python run.py
```

## 使用流程

### 用户端使用

1. 登录系统
2. 访问个人资料页面
3. 点击"Verify Email"或直接访问 `/auth/verify-email`
4. 输入邮箱地址，点击"Send Verification Code"
5. 检查邮箱收件箱（和垃圾邮件箱）
6. 输入收到的6位验证码
7. 点击"Verify and Save Email"

### Admin创建时的邮箱验证

Root用户在创建Admin账号时：
1. 可以选择是否填写邮箱（邮箱可选）
2. 如果不填邮箱，Admin用户需要后续自行验证
3. Admin用户登录后可以添加和验证自己的邮箱

## 数据库表结构

```sql
CREATE TABLE `email_verifications` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `email` varchar(200) NOT NULL,
  `verification_code` varchar(6) NOT NULL,
  `purpose` enum('registration','email_change','password_reset'),
  `is_verified` tinyint(1) DEFAULT '0',
  `attempts` int DEFAULT '0',
  `max_attempts` int DEFAULT '5',
  `expires_at` datetime NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `verified_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_user` (`user_id`),
  KEY `idx_email` (`email`),
  CONSTRAINT FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## API路由

### 发送验证码
- **路由**: `POST /auth/verify-email`
- **参数**: `action=send`, `email=xxx@example.com`
- **返回**: 成功消息或错误信息

### 验证验证码
- **路由**: `POST /auth/verify-email`
- **参数**: `action=verify`, `email=xxx@example.com`, `verification_code=123456`
- **返回**: 验证结果

## 安全措施

1. **验证码有效期**: 15分钟自动过期
2. **尝试限制**: 最多5次尝试，超过后验证码失效
3. **邮箱唯一性**: 防止多个账号使用同一邮箱
4. **验证码随机**: 6位数字随机生成
5. **已验证标记**: 防止重复使用验证码
6. **审计日志**: 记录所有验证操作

## 故障排除

### 1. 邮件发送失败

**检查项**:
- 环境变量是否正确配置
- SMTP服务器地址和端口是否正确
- 邮箱密码是否为应用专用密码（不是登录密码）
- 防火墙是否阻止SMTP端口

**测试连接**:
```python
from app import create_app
from app.utils.email_service import EmailService

app = create_app()
with app.app_context():
    success, message = EmailService.test_connection()
    print(f"连接测试: {message}")
```

### 2. 验证码未收到

- 检查垃圾邮件箱
- 等待几分钟（有时会延迟）
- 确认邮箱地址输入正确
- 重新发送验证码

### 3. 验证码过期

- 验证码有效期15分钟
- 可以重新请求新的验证码
- 旧验证码会自动失效

### 4. 尝试次数用尽

- 每个验证码最多尝试5次
- 需要重新发送新的验证码
- 旧验证码会被锁定

## 邮件模板

系统使用HTML邮件模板，包含：
- InsertQ品牌标识
- 清晰的验证码显示
- 使用说明
- 有效期提醒
- 安全提示

模板位置：`app/utils/email_service.py` 中的 `_get_verification_email_template()` 方法

## 扩展功能

未来可以扩展的功能：
- 密码重置功能
- 新用户注册验证
- 登录异常通知
- 账号变更通知
- 批量邮件通知

## 相关文件

- **模型**: `app/models/email_verification.py`
- **服务**: `app/utils/email_service.py`
- **表单**: `app/forms/email_verification.py`
- **视图**: `app/views/auth.py` (verify_email路由)
- **模板**: `app/templates/auth/verify_email.html`
- **迁移**: `migrate_add_email_verification.py`

## 更新日期

2026-01-24
