import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db
    from app.models import AIPromptTemplate, AIModelConfig, AIApiKey
    
    def init_ai_data():
        """初始化AI聊天所需的默认数据"""
        
        with app.app_context():
            # 添加默认模型配置
            default_models = [
                {
                    'name': 'GPT-5',
                    'api_url': 'https://api.chatanywhere.tech/v1/chat/completions',
                    'model_name': 'gpt-5',
                    'max_tokens': 4000,
                    'temperature': 0.7
                },
                {
                    'name': 'GPT-3.5-Turbo', 
                    'api_url': 'https://api.chatanywhere.tech/v1/chat/completions',
                    'model_name': 'gpt-3.5-turbo',
                    'max_tokens': 4000,
                    'temperature': 0.7
                }
            ]
            
            for model_data in default_models:
                if not AIModelConfig.query.filter_by(name=model_data['name']).first():
                    model = AIModelConfig(**model_data)
                    db.session.add(model)
                    print(f"添加模型: {model_data['name']}")
            
            # 添加默认prompt模板
            default_templates = [
                {
                    'name': '代码审查',
                    'content': '请审查以下代码：\n\n{code}\n\n请提供：\n1. 代码问题分析\n2. 改进建议\n3. 优化后的代码',
                    'description': '用于代码审查的模板',
                    'variables': ['code']
                },
                {
                    'name': '快速帮助',
                    'content': '请帮我解决以下问题：{user_input}',
                    'description': '快速问题帮助模板',
                    'variables': ['user_input']
                },
                {
                    'name': '技术咨询', 
                    'content': '作为技术专家，请回答以下问题：\n\n问题：{question}\n\n上下文：{context}',
                    'description': '技术问题咨询模板',
                    'variables': ['question', 'context']
                }
            ]
            
            for template_data in default_templates:
                if not AIPromptTemplate.query.filter_by(name=template_data['name']).first():
                    template = AIPromptTemplate(**template_data)
                    db.session.add(template)
                    print(f"添加模板: {template_data['name']}")
            
            db.session.commit()
            print("AI数据初始化完成！")
            
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保：")
    print("1. 在Flask应用根目录运行此脚本")
    print("2. 检查app/__init__.py文件是否存在")
    print("3. 或者使用独立版本脚本")

if __name__ == '__main__':
    init_ai_data()