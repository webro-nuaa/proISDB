-- MySQL dump 10.13  Distrib 8.4.7, for Linux (x86_64)
--
-- Host: localhost    Database: proisdb_db
-- ------------------------------------------------------
-- Server version	8.4.7-0ubuntu0.25.10.3

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- Table structure for table `admin_logs`
--


-- Ensure target database exists and switch to it
-- Target database for destructive replace per user request
CREATE DATABASE IF NOT EXISTS `proisdb_db` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `proisdb_db`;

--
-- Table structure for table `admin_logs`
--
DROP TABLE IF EXISTS `admin_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `action` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `resource_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `resource_id` int DEFAULT NULL,
  `details` json DEFAULT NULL COMMENT '操作详情',
  `ip_address` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_agent` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user` (`user_id`),
  KEY `idx_action` (`action`),
  KEY `idx_resource` (`resource_type`,`resource_id`),
  KEY `idx_created` (`created_at`),
  CONSTRAINT `admin_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=96 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `article_tags`
--

DROP TABLE IF EXISTS `article_tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `article_tags` (
  `article_id` int NOT NULL,
  `tag_id` int NOT NULL,
  PRIMARY KEY (`article_id`,`tag_id`),
  KEY `tag_id` (`tag_id`),
  CONSTRAINT `article_tags_ibfk_1` FOREIGN KEY (`article_id`) REFERENCES `knowledge_articles` (`id`) ON DELETE CASCADE,
  CONSTRAINT `article_tags_ibfk_2` FOREIGN KEY (`tag_id`) REFERENCES `knowledge_tags` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `batch_imports`
--

DROP TABLE IF EXISTS `batch_imports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `batch_imports` (
  `id` int NOT NULL AUTO_INCREMENT,
  `filename` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `original_filename` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `total_records` int NOT NULL,
  `successful_records` int DEFAULT '0',
  `failed_records` int DEFAULT '0',
  `status` enum('processing','completed','failed') COLLATE utf8mb4_unicode_ci DEFAULT 'processing',
  `error_log` text COLLATE utf8mb4_unicode_ci COMMENT '错误日志',
  `imported_by` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `completed_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_status` (`status`),
  KEY `idx_imported_by` (`imported_by`),
  CONSTRAINT `batch_imports_ibfk_1` FOREIGN KEY (`imported_by`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `is_elements`
--

DROP TABLE IF EXISTS `is_elements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `is_elements` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `family` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `group` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `synomyns` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `iso` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `origin` varchar(80) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `length` int DEFAULT NULL,
  `tam` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `le_cleavage_site` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `re_cleavage_site` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `orf1` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `orf2` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `accession_number` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `mge_type` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `related_element_s` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `isoform` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `host` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `transposition` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_sequence` text COLLATE utf8mb4_unicode_ci,
  `is_length` int DEFAULT NULL,
  `orf_number` int DEFAULT NULL,
  `orf_1` int DEFAULT NULL,
  `orf_1_length` int DEFAULT NULL,
  `orf_1_begin` int DEFAULT NULL,
  `orf_1_end` int DEFAULT NULL,
  `orf_1_strand` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fusion_orf_1` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `orf_1_function` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `orf_1_chemistry` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `orf_1_sequence` varchar(254) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `orf_2` int DEFAULT NULL,
  `orf_2_length` int DEFAULT NULL,
  `orf_2_begin` int DEFAULT NULL,
  `orf_2_end` int DEFAULT NULL,
  `orf_2_strand` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fusion_orf_2` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `orf_2_function` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `orf_2_chemistry` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `orf_2_sequence` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `comment` longtext COLLATE utf8mb4_unicode_ci,
  `references` longtext COLLATE utf8mb4_unicode_ci,
  `submitter_first_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `submitter_last_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `submitter_institution` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `submitter_department` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `submitter_postal_address` varchar(300) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `submitter_postal_code` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `submitter_country` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `submitter_email` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `submitter_telephone` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `submitter_id` int DEFAULT NULL,
  `reviewer_id` int DEFAULT NULL,
  `submission_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `review_date` datetime DEFAULT NULL,
  `review_comment` longtext COLLATE utf8mb4_unicode_ci,
  `status` enum('pending','approved','rejected') COLLATE utf8mb4_unicode_ci DEFAULT 'pending',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_name` (`name`),
  KEY `idx_family` (`family`),
  KEY `idx_group` (`group`),
  KEY `idx_host` (`host`),
  KEY `idx_status` (`status`),
  KEY `idx_submitter` (`submitter_id`),
  KEY `idx_accession` (`accession_number`),
  KEY `reviewer_id` (`reviewer_id`),
  KEY `idx_is_status_family` (`status`,`family`),
  KEY `idx_is_status_host` (`status`,`host`),
  FULLTEXT KEY `idx_search` (`name`,`family`,`group`,`host`,`comment`),
  CONSTRAINT `is_elements_ibfk_1` FOREIGN KEY (`submitter_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `is_elements_ibfk_2` FOREIGN KEY (`reviewer_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=20026 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `knowledge_articles`
--

DROP TABLE IF EXISTS `knowledge_articles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `knowledge_articles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'URL友好标识',
  `content` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `summary` text COLLATE utf8mb4_unicode_ci COMMENT '摘要',
  `featured_image` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '特色图片',
  `category_id` int DEFAULT NULL,
  `author_id` int NOT NULL,
  `status` enum('draft','published','archived') COLLATE utf8mb4_unicode_ci DEFAULT 'draft',
  `view_count` int DEFAULT '0',
  `like_count` int DEFAULT '0',
  `is_featured` tinyint(1) DEFAULT '0' COMMENT '是否推荐',
  `meta_keywords` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'SEO关键词',
  `meta_description` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'SEO描述',
  `published_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `idx_category` (`category_id`),
  KEY `idx_author` (`author_id`),
  KEY `idx_status` (`status`),
  KEY `idx_published` (`published_at`),
  KEY `idx_featured` (`is_featured`),
  KEY `idx_articles_status_category` (`status`,`category_id`,`published_at`),
  FULLTEXT KEY `idx_content_search` (`title`,`content`,`summary`),
  CONSTRAINT `knowledge_articles_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `knowledge_categories` (`id`) ON DELETE SET NULL,
  CONSTRAINT `knowledge_articles_ibfk_2` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `knowledge_categories`
--

DROP TABLE IF EXISTS `knowledge_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `knowledge_categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `parent_id` int DEFAULT NULL COMMENT '父分类ID',
  `sort_order` int DEFAULT '0',
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_parent` (`parent_id`),
  KEY `idx_active` (`is_active`),
  CONSTRAINT `knowledge_categories_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `knowledge_categories` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `knowledge_tags`
--

DROP TABLE IF EXISTS `knowledge_tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `knowledge_tags` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `color` varchar(7) COLLATE utf8mb4_unicode_ci DEFAULT '#007bff' COMMENT '标签颜色',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `article_images`
--

DROP TABLE IF EXISTS `article_images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `article_images` (
  `id` int NOT NULL AUTO_INCREMENT,
  `article_id` int NOT NULL COMMENT '文章ID',
  `image_path` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '图片相对路径（相对于static/）',
  `filename` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '原始文件名',
  `uploaded_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
  PRIMARY KEY (`id`),
  KEY `idx_article` (`article_id`),
  KEY `idx_uploaded` (`uploaded_at`),
  CONSTRAINT `article_images_ibfk_1` FOREIGN KEY (`article_id`) REFERENCES `knowledge_articles` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文章图片关联表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `page_views`
--

DROP TABLE IF EXISTS `page_views`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `page_views` (
  `id` int NOT NULL AUTO_INCREMENT,
  `page_type` enum('is_element','knowledge_article','home','search','auth','other') COLLATE utf8mb4_unicode_ci NOT NULL,
  `page_id` int DEFAULT NULL COMMENT '页面对应的记录ID',
  `user_id` int DEFAULT NULL,
  `ip_address` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_agent` text COLLATE utf8mb4_unicode_ci,
  `referer` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_page_type` (`page_type`),
  KEY `idx_page_id` (`page_id`),
  KEY `idx_user` (`user_id`),
  KEY `idx_created` (`created_at`),
  CONSTRAINT `page_views_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=1268 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `pending_submissions`
--

DROP TABLE IF EXISTS `pending_submissions`;
/*!50001 DROP VIEW IF EXISTS `pending_submissions`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `pending_submissions` AS SELECT 
 1 AS `id`,
 1 AS `name`,
 1 AS `family`,
 1 AS `host`,
 1 AS `submitter_name`,
 1 AS `submission_date`,
 1 AS `comment`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `popular_searches`
--

DROP TABLE IF EXISTS `popular_searches`;
/*!50001 DROP VIEW IF EXISTS `popular_searches`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `popular_searches` AS SELECT 
 1 AS `search_term`,
 1 AS `search_count`,
 1 AS `last_searched`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `search_logs`
--

DROP TABLE IF EXISTS `search_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `search_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `search_term` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `search_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `results_count` int DEFAULT '0',
  `user_id` int DEFAULT NULL,
  `ip_address` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_agent` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_search_term` (`search_term`),
  KEY `idx_search_type` (`search_type`),
  KEY `idx_user` (`user_id`),
  KEY `idx_created` (`created_at`),
  KEY `idx_search_logs_term_type` (`search_term`,`search_type`,`created_at`),
  CONSTRAINT `search_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=67 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `site_statistics`
--

DROP TABLE IF EXISTS `site_statistics`;
/*!50001 DROP VIEW IF EXISTS `site_statistics`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `site_statistics` AS SELECT 
 1 AS `total_is_elements`,
 1 AS `pending_submissions`,
 1 AS `published_articles`,
 1 AS `total_users`,
 1 AS `searches_this_week`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `submission_history`
--

DROP TABLE IF EXISTS `submission_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `submission_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `is_element_id` int NOT NULL,
  `submitter_id` int DEFAULT NULL,
  `action` enum('create','update','delete') COLLATE utf8mb4_unicode_ci NOT NULL,
  `old_data` json DEFAULT NULL COMMENT '修改前数据',
  `new_data` json DEFAULT NULL COMMENT '修改后数据',
  `status` enum('pending','approved','rejected') COLLATE utf8mb4_unicode_ci DEFAULT 'pending',
  `submission_reason` text COLLATE utf8mb4_unicode_ci COMMENT '提交原因',
  `review_comment` text COLLATE utf8mb4_unicode_ci COMMENT '审核意见',
  `reviewer_id` int DEFAULT NULL COMMENT '审核者ID',
  `submitted_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `reviewed_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_element` (`is_element_id`),
  KEY `idx_submitter` (`submitter_id`),
  KEY `idx_status` (`status`),
  KEY `reviewer_id` (`reviewer_id`),
  CONSTRAINT `submission_history_ibfk_1` FOREIGN KEY (`is_element_id`) REFERENCES `is_elements` (`id`) ON DELETE CASCADE,
  CONSTRAINT `submission_history_ibfk_2` FOREIGN KEY (`submitter_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `submission_history_ibfk_3` FOREIGN KEY (`reviewer_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `system_configs`
--

DROP TABLE IF EXISTS `system_configs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_configs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `config_key` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `config_value` text COLLATE utf8mb4_unicode_ci,
  `description` text COLLATE utf8mb4_unicode_ci,
  `config_type` enum('string','number','boolean','json') COLLATE utf8mb4_unicode_ci DEFAULT 'string',
  `is_editable` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `config_key` (`config_key`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` enum('root','admin','visitor') COLLATE utf8mb4_unicode_ci DEFAULT 'visitor',
  `full_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `institution` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `last_login` timestamp NULL DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_username` (`username`),
  KEY `idx_email` (`email`),
  KEY `idx_role` (`role`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping events for database 'proisdb_db'
--

--
-- Dumping routines for database 'proisdb_db'
--

--
-- Final view structure for view `pending_submissions`
--

/*!50001 DROP VIEW IF EXISTS `pending_submissions`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `pending_submissions` AS select `ie`.`id` AS `id`,`ie`.`name` AS `name`,`ie`.`family` AS `family`,`ie`.`host` AS `host`,`u`.`username` AS `submitter_name`,`ie`.`submission_date` AS `submission_date`,`ie`.`comment` AS `comment` from (`is_elements` `ie` left join `users` `u` on((`ie`.`submitter_id` = `u`.`id`))) where (`ie`.`status` = 'pending') order by `ie`.`submission_date` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `popular_searches`
--

/*!50001 DROP VIEW IF EXISTS `popular_searches`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `popular_searches` AS select `search_logs`.`search_term` AS `search_term`,count(0) AS `search_count`,max(`search_logs`.`created_at`) AS `last_searched` from `search_logs` where (`search_logs`.`created_at` >= (now() - interval 30 day)) group by `search_logs`.`search_term` order by `search_count` desc limit 20 */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `site_statistics`
--

/*!50001 DROP VIEW IF EXISTS `site_statistics`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `site_statistics` AS select (select count(0) from `is_elements` where (`is_elements`.`status` = 'approved')) AS `total_is_elements`,(select count(0) from `is_elements` where (`is_elements`.`status` = 'pending')) AS `pending_submissions`,(select count(0) from `knowledge_articles` where (`knowledge_articles`.`status` = 'published')) AS `published_articles`,(select count(0) from `users` where (`users`.`role` = 'visitor')) AS `total_users`,(select count(0) from `search_logs` where (`search_logs`.`created_at` >= (now() - interval 7 day))) AS `searches_this_week` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-16  0:21:17
