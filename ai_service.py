import requests
import json
import re
from flask import current_app, stream_with_context, Response
from models import AIModelConfig, AIApiKey, db, AIMessage

class AIService:
    def __init__(self):
        self.timeout = 600  # 10分钟超时
    
    def get_api_key(self, provider='openai'):
        """获取API密钥"""
        api_key_obj = AIApiKey.query.filter_by(is_active=True).first()
        return api_key_obj.api_key if api_key_obj else None
    
    def render_prompt(self, template_content, variables):
        """渲染prompt模板，支持变量替换"""
        try:
            return template_content.format(**variables)
        except KeyError as e:
            raise ValueError(f"缺少必需的变量: {e}")
    
    def estimate_tokens(self, text):
        """简单估算token数量"""
        # 这是一个简单的估算，实际应该使用tiktoken库
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_words = len(re.findall(r'[a-zA-Z]+', text))
        return chinese_chars + english_words
    
    def stream_chat_completion(self, session, user_message, template=None, template_variables=None):
        """流式聊天完成"""
        model_config = AIModelConfig.query.filter_by(name=session.model_used, is_active=True).first()
        if not model_config:
            raise ValueError("模型配置不存在")
    
        api_key = self.get_api_key(provider='openai')
        if not api_key:
            raise ValueError("API密钥未配置")
    
        # 构建消息历史
        messages = self.build_message_history(session, user_message, template, template_variables or {})
    
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
        payload = {
            'model': model_config.model_name,
            'messages': messages,
            'stream': True,
            'max_tokens': model_config.max_tokens,
            'temperature': model_config.temperature
        }
    
        def generate():
            accumulated_content = ""
            # 立即发送一次心跳，确保客户端收到首字节，避免扩展/代理误判超时
            yield ":heartbeat\n\n"
            try:
                response = requests.post(
                    model_config.api_url,
                    headers=headers,
                    json=payload,
                    stream=True,
                    timeout=self.timeout
                )
                response.raise_for_status()
    
                for line in response.iter_lines():
                    if not line:
                        continue
                    line = line.decode('utf-8')
                    if line.startswith('data:'):
                        data = line[5:].strip()
                        if data == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data)
                            choices = chunk.get('choices', [{}])
                            if choices:
                                content = choices[0].get('delta', {}).get('content', '')
                                if content:
                                    accumulated_content += content
                                    yield f"data: {json.dumps({'content': content, 'done': False})}\n\n"
                        except json.JSONDecodeError:
                            continue
    
                # 保存完整的AI回复
                ai_message = AIMessage(
                    session_id=session.id,
                    role='assistant',
                    content=accumulated_content,
                    tokens=self.estimate_tokens(accumulated_content)
                )
                db.session.add(ai_message)
                db.session.commit()
    
                yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"
    
            except requests.exceptions.RequestException as e:
                error_msg = f"API请求错误: {str(e)}"
                yield f"data: {json.dumps({'error': error_msg, 'done': True})}\n\n"
            except Exception as e:
                error_msg = f"处理错误: {str(e)}"
                yield f"data: {json.dumps({'error': error_msg, 'done': True})}\n\n"
    
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )
    
    def build_message_history(self, session, user_message, template=None, template_variables=None):
        """构建消息历史"""
        messages = []
        
        # 添加系统消息（如果有模板）
        if template and template_variables:
            system_content = self.render_prompt(template.content, template_variables)
            messages.append({'role': 'system', 'content': system_content})
        
        # 添加历史消息（最近10条或基于token限制）
        history_messages = session.messages.order_by(AIMessage.created_at.asc()).all()
        
        # 简单的token限制管理（可优化）
        total_tokens = 0
        max_history_tokens = 2000
        
        for msg in reversed(history_messages[-20:]):  # 最多取最近20条
            msg_tokens = self.estimate_tokens(msg.content)
            if total_tokens + msg_tokens > max_history_tokens:
                break
            messages.insert(0, {'role': msg.role, 'content': msg.content})
            total_tokens += msg_tokens
        
        # 添加当前用户消息
        messages.append({'role': 'user', 'content': user_message})
        
        return messages
