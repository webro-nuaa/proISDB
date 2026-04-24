-- 更新用户表结构，添加详细的个人信息字段
-- 执行前请备份数据库！

-- 1. 添加新字段
ALTER TABLE users 
ADD COLUMN first_name VARCHAR(50) AFTER role,
ADD COLUMN last_name VARCHAR(50) AFTER first_name,
ADD COLUMN department VARCHAR(200) AFTER institution,
ADD COLUMN postal_address VARCHAR(300) AFTER department,
ADD COLUMN postal_code VARCHAR(20) AFTER postal_address,
ADD COLUMN country VARCHAR(100) AFTER postal_code,
ADD COLUMN telephone VARCHAR(50) AFTER country;

-- 2. 修改email字段长度以匹配ISElement
ALTER TABLE users MODIFY COLUMN email VARCHAR(200);

-- 3. 尝试从full_name分割数据到first_name和last_name（如果有数据的话）
UPDATE users 
SET first_name = SUBSTRING_INDEX(full_name, ' ', 1),
    last_name = SUBSTRING(full_name, LENGTH(SUBSTRING_INDEX(full_name, ' ', 1)) + 2)
WHERE full_name IS NOT NULL AND full_name != '';

-- 4. 如果last_name为空，将first_name复制到last_name
UPDATE users 
SET last_name = first_name
WHERE (last_name IS NULL OR last_name = '') AND first_name IS NOT NULL;

-- 5. 删除旧的full_name字段（可选，如果确认数据已迁移）
-- ALTER TABLE users DROP COLUMN full_name;

-- 6. 验证数据
SELECT id, username, first_name, last_name, email, institution, country FROM users;
