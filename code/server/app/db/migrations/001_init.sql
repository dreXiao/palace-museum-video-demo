-- ============================================================
-- 故宫日历·图生视频管理平台 — 数据库初始化脚本
-- PostgreSQL 16+  required
-- ============================================================

-- 启用 UUID 扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- 用户表
-- ============================================================
CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username      VARCHAR(50)  NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role          VARCHAR(20)  NOT NULL DEFAULT 'developer',  -- admin / developer / viewer
    is_active     BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 模型配置表
-- ============================================================
CREATE TABLE model_configs (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name              VARCHAR(100) NOT NULL,
    provider          VARCHAR(50)  NOT NULL,
    description       TEXT,
    api_type          VARCHAR(30)  NOT NULL,       -- dashscope / volcengine-ark / kling / custom
    endpoint          VARCHAR(255) NOT NULL,
    api_key_env       VARCHAR(100) NOT NULL,       -- 环境变量名，如 DASHSCOPE_API_KEY
    model_ids         JSONB        NOT NULL DEFAULT '{}',
    parameters        JSONB        NOT NULL DEFAULT '{}',
    pricing           JSONB        NOT NULL DEFAULT '{}',
    generation_config JSONB        DEFAULT '{}',
    is_default        BOOLEAN      DEFAULT FALSE,
    is_preset         BOOLEAN      DEFAULT FALSE,
    connection_status VARCHAR(20)  DEFAULT 'untested',
    last_tested_at    TIMESTAMPTZ,
    created_by        UUID         REFERENCES users(id) ON DELETE SET NULL,
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- 确保只有一个默认模型
CREATE UNIQUE INDEX idx_model_default_single ON model_configs (is_default) WHERE is_default = TRUE;

-- ============================================================
-- 风格标签表
-- ============================================================
CREATE TABLE style_tags (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name             VARCHAR(100) NOT NULL,
    color            VARCHAR(7)   NOT NULL DEFAULT '#6366F1',
    icon             VARCHAR(10)  NOT NULL DEFAULT '🎨',
    description      TEXT,
    applicable_types TEXT[],
    positive_prompt  TEXT         NOT NULL,
    negative_prompt  TEXT         DEFAULT '',
    variables        TEXT[]       DEFAULT '{}',
    default_params   JSONB        DEFAULT '{}',
    is_preset        BOOLEAN      DEFAULT FALSE,
    usage_count      INTEGER      DEFAULT 0,
    created_by       UUID         REFERENCES users(id) ON DELETE SET NULL,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 标签版本历史
-- ============================================================
CREATE TABLE style_tag_versions (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tag_id         UUID         NOT NULL REFERENCES style_tags(id) ON DELETE CASCADE,
    version_number INTEGER      NOT NULL,
    snapshot       JSONB        NOT NULL,
    change_note    TEXT,
    created_by     UUID         REFERENCES users(id) ON DELETE SET NULL,
    created_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (tag_id, version_number)
);

-- ============================================================
-- 图片资产表
-- ============================================================
CREATE TABLE image_assets (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_name  VARCHAR(255)  NOT NULL,
    storage_key    VARCHAR(500)  NOT NULL,
    storage_url    VARCHAR(1000) NOT NULL,
    thumbnail_key  VARCHAR(500),
    width          INTEGER,
    height         INTEGER,
    size_bytes     BIGINT,
    mime_type      VARCHAR(50),
    metadata       JSONB         DEFAULT '{}',
    created_by     UUID          REFERENCES users(id) ON DELETE SET NULL,
    created_at     TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 生成分组表
-- ============================================================
CREATE TABLE generation_groups (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    image_asset_id  UUID        NOT NULL REFERENCES image_assets(id) ON DELETE RESTRICT,
    tag_id          UUID        NOT NULL REFERENCES style_tags(id) ON DELETE RESTRICT,
    model_id        UUID        NOT NULL REFERENCES model_configs(id) ON DELETE RESTRICT,
    user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    best_attempt_id UUID,
    total_attempts  SMALLINT    DEFAULT 0,
    total_cost_yuan DECIMAL(10, 4) DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 生成任务表
-- ============================================================
CREATE TABLE generation_tasks (
    id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id               UUID         NOT NULL REFERENCES generation_groups(id) ON DELETE CASCADE,
    user_id                UUID         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    image_asset_id         UUID         NOT NULL REFERENCES image_assets(id) ON DELETE RESTRICT,

    -- 输入快照
    tag_snapshot           JSONB        NOT NULL,
    model_snapshot         JSONB        NOT NULL,
    prompt                 TEXT         NOT NULL,
    negative_prompt        TEXT         DEFAULT '',

    -- 参数
    duration               INTEGER      NOT NULL,
    resolution             VARCHAR(10)  NOT NULL,
    extended_params        JSONB        DEFAULT '{}',

    -- 外部 API 信息
    api_task_id            VARCHAR(255),
    api_provider           VARCHAR(50),

    -- 输出
    status                 VARCHAR(20)  NOT NULL DEFAULT 'queued',
    result_video_key       VARCHAR(500),
    result_thumbnail_key   VARCHAR(500),
    error_message          TEXT,

    -- 评估
    quality_score          SMALLINT     CHECK (quality_score >= 1 AND quality_score <= 5),
    quality_notes          TEXT,
    is_best_attempt        BOOLEAN      DEFAULT FALSE,

    -- 元数据
    attempt_number         SMALLINT     NOT NULL DEFAULT 1,
    generation_time_seconds INTEGER,
    cost_yuan              DECIMAL(10, 4),

    created_at             TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    completed_at           TIMESTAMPTZ
);

-- 添加分组最佳尝试外键 (延迟添加避免循环引用)
ALTER TABLE generation_groups
    ADD CONSTRAINT fk_group_best_attempt
    FOREIGN KEY (best_attempt_id) REFERENCES generation_tasks(id) ON DELETE SET NULL;

-- ============================================================
-- 用户偏好表
-- ============================================================
CREATE TABLE user_preferences (
    user_id          UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    default_model_id UUID,
    default_resolution VARCHAR(10) DEFAULT '1080p',
    default_duration   INTEGER    DEFAULT 10,
    history_view       VARCHAR(10) DEFAULT 'grid',
    page_size          INTEGER    DEFAULT 20,
    language           VARCHAR(10) DEFAULT 'zh-CN',
    theme              VARCHAR(10) DEFAULT 'system',
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 索引
-- ============================================================
-- 生成任务查询索引
CREATE INDEX idx_tasks_status ON generation_tasks (status);
CREATE INDEX idx_tasks_created ON generation_tasks (created_at DESC);
CREATE INDEX idx_tasks_group ON generation_tasks (group_id);
CREATE INDEX idx_tasks_user ON generation_tasks (user_id, created_at DESC);
CREATE INDEX idx_tasks_api ON generation_tasks (api_task_id) WHERE api_task_id IS NOT NULL;

-- 生成分组查询索引
CREATE INDEX idx_groups_user ON generation_groups (user_id, created_at DESC);
CREATE INDEX idx_groups_tag ON generation_groups (tag_id);
CREATE INDEX idx_groups_model ON generation_groups (model_id);
CREATE INDEX idx_groups_image ON generation_groups (image_asset_id);

-- 标签索引
CREATE INDEX idx_tags_preset ON style_tags (is_preset);
CREATE INDEX idx_tags_usage ON style_tags (usage_count DESC);

-- 模型索引
CREATE INDEX idx_models_status ON model_configs (connection_status);
CREATE INDEX idx_models_type ON model_configs (api_type);

-- 图片索引
CREATE INDEX idx_images_user ON image_assets (created_by, created_at DESC);

-- ============================================================
-- 触发器: 自动更新 updated_at
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_model_configs_updated_at
    BEFORE UPDATE ON model_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_style_tags_updated_at
    BEFORE UPDATE ON style_tags
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_generation_groups_updated_at
    BEFORE UPDATE ON generation_groups
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_user_preferences_updated_at
    BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- 触发器: 生成任务完成后更新分组
-- ============================================================
CREATE OR REPLACE FUNCTION update_group_on_task_complete()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status IN ('completed', 'failed') AND (OLD.status IS NULL OR OLD.status NOT IN ('completed', 'failed')) THEN
        UPDATE generation_groups
        SET total_attempts = total_attempts + 1,
            total_cost_yuan = total_cost_yuan + COALESCE(NEW.cost_yuan, 0)
        WHERE id = NEW.group_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_task_complete_update_group
    AFTER UPDATE OF status ON generation_tasks
    FOR EACH ROW EXECUTE FUNCTION update_group_on_task_complete();

-- ============================================================
-- 触发器: 标签使用计数自动更新
-- ============================================================
CREATE OR REPLACE FUNCTION increment_tag_usage()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE style_tags
    SET usage_count = usage_count + 1
    WHERE id = (NEW.tag_snapshot->>'id')::UUID;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_task_increment_tag_usage
    AFTER INSERT ON generation_tasks
    FOR EACH ROW EXECUTE FUNCTION increment_tag_usage();
