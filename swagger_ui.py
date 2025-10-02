#!/usr/bin/env python3
# coding: utf-8
"""
Swagger UI Integration
دمج واجهة Swagger UI للتوثيق التفاعلي للـ API

الاستخدام:
    from swagger_ui import register_swagger_ui
    register_swagger_ui(app)
"""

from flask import Blueprint, send_from_directory, render_template_string
import os

swagger_ui_bp = Blueprint('swagger_ui', __name__, url_prefix='/api/docs')

# HTML template for Swagger UI
SWAGGER_UI_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>aaPanel API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.10.0/swagger-ui.css">
    <style>
        body {
            margin: 0;
            padding: 0;
        }
        .topbar {
            display: none;
        }
        .swagger-ui .info {
            margin: 50px 0;
        }
        .swagger-ui .info .title {
            font-size: 36px;
            color: #3b4151;
        }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.10.0/swagger-ui-bundle.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.10.0/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {
            const ui = SwaggerUIBundle({
                url: '/api/docs/openapi.yaml',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                defaultModelsExpandDepth: 1,
                defaultModelExpandDepth: 1,
                docExpansion: 'list',
                filter: true,
                showRequestHeaders: true,
                tryItOutEnabled: true,
                persistAuthorization: true
            });
            window.ui = ui;
        };
    </script>
</body>
</html>
"""


@swagger_ui_bp.route('/')
def swagger_ui_index():
    """
    عرض واجهة Swagger UI
    """
    return render_template_string(SWAGGER_UI_HTML)


@swagger_ui_bp.route('/openapi.yaml')
def openapi_spec():
    """
    تقديم ملف OpenAPI YAML
    """
    # البحث عن ملف openapi.yaml في المجلد الجذري للمشروع
    # استخدام المسار الصحيح بدون dirname مزدوج
    project_root = os.path.dirname(os.path.abspath(__file__))
    openapi_path = os.path.join(project_root, 'openapi.yaml')
    
    if os.path.exists(openapi_path):
        return send_from_directory(project_root, 'openapi.yaml', mimetype='text/yaml')
    else:
        return {
            'error': 'OpenAPI specification not found',
            'message': 'Please ensure openapi.yaml exists in the project root'
        }, 404


@swagger_ui_bp.route('/openapi.json')
def openapi_spec_json():
    """
    تقديم ملف OpenAPI بصيغة JSON (اختياري)
    """
    import yaml
    import json
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    openapi_path = os.path.join(project_root, 'openapi.yaml')
    
    if not os.path.exists(openapi_path):
        return {
            'error': 'OpenAPI specification not found'
        }, 404
    
    try:
        with open(openapi_path, 'r', encoding='utf-8') as f:
            openapi_dict = yaml.safe_load(f)
        return json.dumps(openapi_dict, ensure_ascii=False, indent=2), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return {
            'error': 'Failed to parse OpenAPI specification',
            'message': str(e)
        }, 500


def register_swagger_ui(app):
    """
    تسجيل Swagger UI مع Flask app
    
    Args:
        app: Flask application instance
        
    Usage:
        from swagger_ui import register_swagger_ui
        register_swagger_ui(app)
        
        # ستكون الواجهة متاحة على:
        # http://localhost:5000/api/docs/
    """
    app.register_blueprint(swagger_ui_bp)
    
    # إضافة رسالة في السجل
    app.logger.info("Swagger UI registered at /api/docs/")


# دالة اختيارية لتفعيل CORS إذا لزم الأمر
def enable_cors_for_swagger(app):
    """
    تفعيل CORS للسماح بالوصول إلى Swagger UI من نطاقات مختلفة
    
    Args:
        app: Flask application instance
    """
    from flask import make_response
    
    @app.after_request
    def after_request(response):
        # السماح فقط لـ Swagger UI routes
        if '/api/docs' in str(response.headers.get('Location', '')):
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
