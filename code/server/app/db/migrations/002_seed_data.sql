-- ============================================================
-- 预设数据: 5 组风格标签 + 3 个模型配置
-- ============================================================

-- ============================================================
-- 预设风格标签
-- ============================================================
INSERT INTO style_tags (name, color, icon, description, applicable_types, positive_prompt, negative_prompt, variables, default_params, is_preset)
VALUES
(
    '水墨风格',
    '#2D2D2D',
    '🎨',
    '黑白灰调、墨色浓淡、写意笔触',
    ARRAY['水墨山水', '文人画'],
    '中国传统水墨画风格。{主体}，墨色浓淡相宜，留白构图，宣纸质感。云雾在山间缓慢流动，水面有细微涟漪，远处有飞鸟掠过天际。镜头缓慢横移(camera panning)，如展开手卷般徐徐呈现。保持水墨笔触和墨韵，气韵生动，写意精神。',
    '色彩鲜艳，油画质感，3D渲染，过度锐化，画面闪烁，突变跳帧，现代建筑，西方透视，照片级写实，卡通风格，饱和度失真',
    ARRAY['{主体}', '{朝代}', '{作者}', '{材质}', '{尺寸}'],
    '{"duration": 10, "resolution": "1080p", "motionStrength": "gentle", "cfgScale": 6.0, "inferenceSteps": 50}',
    TRUE
),
(
    '青绿山水',
    '#166534',
    '🏔️',
    '青绿设色、工笔细描、金碧辉煌',
    ARRAY['青绿设色山水', '金碧山水'],
    '中国青绿山水画风格，石青石绿设色，金碧辉煌，工笔细描。{主体}，山峦层叠，水波缓缓流动，阳光在峰顶流转。树梢轻微摇曳，云雾在山腰缭绕，江面有细微波光。镜头缓慢推进(slow zoom in)，保持矿物颜料质感。',
    '黑白灰调，水墨渲染，抽象表现，现代摄影，画面抖动，色彩失真',
    ARRAY['{主体}', '{朝代}', '{作者}', '{材质}', '{尺寸}'],
    '{"duration": 10, "resolution": "1080p", "motionStrength": "gentle", "cfgScale": 6.0, "inferenceSteps": 50}',
    TRUE
),
(
    '工笔重彩',
    '#991B1B',
    '🖌️',
    '精细线条、浓重色彩、装饰性强',
    ARRAY['工笔人物', '花鸟画'],
    '中国工笔重彩画风格，精细线条勾勒，浓重设色，装饰性构图。{主体}，人物衣袂轻轻飘动，花卉叶片微颤，发丝随风轻拂。烛光摇曳，珠帘微动，画面有呼吸感。镜头固定微动(gentle handheld)，光线柔和变化。',
    '粗犷笔触，写意风格，模糊晕染，现代服饰，面部扭曲，肢体变形',
    ARRAY['{主体}', '{朝代}', '{作者}', '{材质}', '{尺寸}'],
    '{"duration": 10, "resolution": "1080p", "motionStrength": "medium", "cfgScale": 7.0, "inferenceSteps": 50}',
    TRUE
),
(
    '浅绛淡彩',
    '#92400E',
    '🌫️',
    '淡雅色调、赭石为主、文人气息',
    ARRAY['浅绛山水', '文人小品'],
    '中国浅绛山水画风格，赭石淡彩，水墨为骨，文人雅致气息。{主体}，远山在薄雾中若隐若现，溪水潺潺流动。烟雨朦胧氛围，画面有湿润感和空间深度。镜头极缓慢推移(slow dolly)，如同漫步画中。',
    '色彩浓烈，对比强烈，装饰性过强，卡通渲染，画面跳变',
    ARRAY['{主体}', '{朝代}', '{作者}', '{材质}', '{尺寸}'],
    '{"duration": 8, "resolution": "1080p", "motionStrength": "gentle", "cfgScale": 5.5, "inferenceSteps": 45}',
    TRUE
),
(
    '白描线稿',
    '#4F46E5',
    '✏️',
    '纯线条勾勒、无设色、书法用笔',
    ARRAY['白描人物', '纯线描'],
    '中国传统白描画风格，纯墨线勾勒，书法用笔，线条富有韵律。{主体}，线条如行云流水般自然流动，人物姿态有微妙变化。如手卷徐徐展开，画面连贯流动。保持线的独立性和书法美感，十八描技法气韵。',
    '明暗渲染，体积感，透视阴影，色彩填充，素描风格，3D模型',
    ARRAY['{主体}', '{朝代}', '{作者}', '{材质}', '{尺寸}'],
    '{"duration": 8, "resolution": "1080p", "motionStrength": "gentle", "cfgScale": 6.0, "inferenceSteps": 40}',
    TRUE
);

-- ============================================================
-- 预设模型配置
-- ============================================================
INSERT INTO model_configs (name, provider, description, api_type, endpoint, api_key_env, model_ids, parameters, pricing, generation_config, is_preset, is_default)
VALUES
(
    '通义万相 Wan 2.7',
    '阿里云',
    '阿里云通义万相图生视频模型，古画风格保持最佳，光影渲染出色',
    'dashscope',
    'https://dashscope.aliyuncs.com',
    'DASHSCOPE_API_KEY',
    '{"720p": "wan2.7-i2v-2026-04-25", "1080p": "wan2.7-i2v-2026-04-25"}',
    '{
        "duration": {"min": 2, "max": 15, "default": 10},
        "resolutions": {"options": ["720p", "1080p"], "default": "1080p"},
        "audio": {"supported": true, "default": false},
        "frameControl": {"supported": true},
        "extended": {
            "prompt_extend": {"type": "boolean", "label": "提示词扩展", "description": "使用LLM自动扩展和优化提示词", "default": true, "expose": true},
            "seed": {"type": "number", "label": "随机种子", "description": "-1为随机", "default": -1, "expose": true},
            "guidance_scale": {"type": "slider", "label": "提示词引导强度", "description": "控制生成结果对提示词的遵循程度", "min": 1.0, "max": 20.0, "step": 0.5, "default": 6.0, "expose": true},
            "num_inference_steps": {"type": "slider", "label": "推理步数", "description": "更多步数=更高质量但更慢", "min": 20, "max": 100, "step": 1, "default": 50, "expose": true},
            "watermark": {"type": "boolean", "label": "水印", "default": false, "expose": false},
            "negative_prompt": {"type": "textarea", "label": "覆盖负向提示词", "description": "留空则使用标签默认值", "default": "", "expose": false}
        }
    }',
    '{"mode": "per_second", "currency": "CNY", "rates": {"720p": 0.60, "1080p": 1.00}, "freeQuota": {"totalSeconds": 50, "validDays": 90}}',
    '{"maxConcurrent": 2, "pollIntervalMs": 3000, "timeoutMs": 300000, "retryCount": 2}',
    TRUE,
    TRUE
),
(
    '豆包 Seedance 2.0',
    '字节跳动',
    '火山引擎豆包Seedance图生视频模型，综合性价比高',
    'volcengine-ark',
    'https://ark.cn-beijing.volces.com',
    'SEEDANCE_API_KEY',
    '{"480p": "doubao-seedance-2-0-260128", "720p": "doubao-seedance-2-0-260128", "1080p": "doubao-seedance-2-0-260128"}',
    '{
        "duration": {"min": 4, "max": 15, "default": 10},
        "resolutions": {"options": ["480p", "720p", "1080p"], "default": "1080p"},
        "audio": {"supported": true, "default": false},
        "frameControl": {"supported": true},
        "extended": {
            "seed": {"type": "number", "label": "随机种子", "description": "-1为随机", "default": -1, "expose": true},
            "cfg_scale": {"type": "slider", "label": "CFG引导强度", "min": 1.0, "max": 20.0, "step": 0.5, "default": 7.0, "expose": true},
            "watermark": {"type": "boolean", "label": "水印", "default": false, "expose": true},
            "negative_prompt": {"type": "textarea", "label": "覆盖负向提示词", "default": "", "expose": false}
        }
    }',
    '{"mode": "per_second", "currency": "CNY", "rates": {"480p": 0.40, "720p": 0.40, "1080p": 0.95}}',
    '{"maxConcurrent": 2, "pollIntervalMs": 5000, "timeoutMs": 600000, "retryCount": 2}',
    TRUE,
    FALSE
),
(
    '可灵 Kling 3.0',
    '快手',
    '可灵开放平台图生视频模型，画质天花板，支持4K',
    'kling',
    'https://api.klingai.com',
    'KLING_API_KEY',
    '{"720p": "kling-v3-std-image-to-video", "1080p": "kling-v3-pro-image-to-video", "4k": "kling-v3-pro-image-to-video"}',
    '{
        "duration": {"min": 4, "max": 15, "default": 10},
        "resolutions": {"options": ["720p", "1080p", "4k"], "default": "1080p"},
        "audio": {"supported": false, "default": false},
        "frameControl": {"supported": true},
        "extended": {
            "mode": {"type": "select", "label": "生成模式", "options": [{"label": "标准", "value": "std"}, {"label": "专业", "value": "pro"}], "default": "std", "expose": true},
            "seed": {"type": "number", "label": "随机种子", "default": -1, "expose": true},
            "cfg_scale": {"type": "slider", "label": "CFG引导强度", "min": 1.0, "max": 10.0, "step": 0.5, "default": 5.0, "expose": true},
            "negative_prompt": {"type": "textarea", "label": "覆盖负向提示词", "default": "", "expose": false}
        }
    }',
    '{"mode": "per_second", "currency": "CNY", "rates": {"720p": 0.50, "1080p": 0.67, "4k": 0.84}}',
    '{"maxConcurrent": 1, "pollIntervalMs": 5000, "timeoutMs": 600000, "retryCount": 3}',
    TRUE,
    FALSE
);
