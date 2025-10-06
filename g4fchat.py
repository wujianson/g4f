#!/usr/bin/env python3
import os
import json
import readline
import signal
import threading
from datetime import datetime
from g4f.client import Client
import time

class GF4Chat:
    def __init__(self):
        self.client = Client()
        self.history_dir = os.path.expanduser("~/gf4chat")
        self.session_file = None
        self.conversation_history = []
        self.timeout_seconds = 30  # 30秒超时
        
        # 创建历史记录目录
        os.makedirs(self.history_dir, exist_ok=True)
        self._create_new_session()
        
    def _create_new_session(self):
        """创建新的会话文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_file = os.path.join(self.history_dir, f"session_{timestamp}.json")
        
        session_data = {
            "created_at": datetime.now().isoformat(),
            "model": "gpt-4o-mini",
            "messages": []
        }
        self._save_session(session_data)
    
    def _save_session(self, data=None):
        """保存会话数据"""
        try:
            if data is None:
                data = {
                    "created_at": datetime.now().isoformat(),
                    "model": "gpt-4o-mini",
                    "messages": self.conversation_history
                }
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  保存会话失败: {e}")
    
    def _chat_with_timeout(self, messages, web_search=False):
        """带超时的聊天请求"""
        result = [None]  # 用于存储结果
        exception = [None]  # 用于存储异常
        
        def worker():
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    web_search=web_search
                )
                result[0] = response.choices[0].message.content
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()
        thread.join(self.timeout_seconds)
        
        if thread.is_alive():
            return None, "请求超时，请检查网络连接或稍后重试"
        elif exception[0] is not None:
            return None, f"API错误: {str(exception[0])}"
        else:
            return result[0], None
    
    def chat(self, message, web_search=False):
        """发送消息到 GPT-4（优化版）"""
        try:
            # 添加用户消息到历史
            user_msg = {
                "role": "user", 
                "content": message,
                "timestamp": datetime.now().isoformat()
            }
            self.conversation_history.append(user_msg)
            
            print("⏳ 思考中...", end='', flush=True)
            
            # 使用带超时的请求
            reply, error = self._chat_with_timeout(self.conversation_history, web_search)
            
            if error:
                print(f"\r❌ {error}")
                reply = f"抱歉，处理您的请求时出现问题：{error}"
            else:
                print(f"\r✅ 完成!")  # 清空"思考中"提示
            
            # 添加助手回复到历史
            assistant_msg = {
                "role": "assistant",
                "content": reply,
                "timestamp": datetime.now().isoformat()
            }
            self.conversation_history.append(assistant_msg)
            
            # 异步保存会话，不阻塞主线程
            save_thread = threading.Thread(target=self._save_session)
            save_thread.daemon = True
            save_thread.start()
            
            return reply
            
        except Exception as e:
            error_msg = f"系统错误: {str(e)}"
            print(f"\r❌ {error_msg}")
            return error_msg
    
    def quick_chat(self, message):
        """快速聊天，不保存历史（用于简单问答）"""
        try:
            print("⏳ 思考中...", end='', flush=True)
            messages = [{"role": "user", "content": message}]
            
            reply, error = self._chat_with_timeout(messages, False)
            
            if error:
                print(f"\r❌ {error}")
                return None
            else:
                print(f"\r✅ 完成!")
                return reply
                
        except Exception as e:
            print(f"\r❌ 错误: {str(e)}")
            return None
    
    def interactive_chat(self):
        """启动交互式对话（优化版）"""
        print("🤖 GF4Chat 终端对话程序 (优化版)")
        print(f"📁 会话文件: {os.path.basename(self.session_file)}")
        print("💡 提示: 输入 /quick 进行快速对话（不保存历史）")
        print("输入 '/help' 查看可用命令")
        print("输入 '/exit' 退出")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\n🧑 You: ").strip()
                
                if not user_input:
                    continue
                    
                # 处理命令
                if user_input.startswith('/'):
                    if user_input == '/exit' or user_input == '/quit':
                        print("再见！👋")
                        break
                    elif user_input == '/help':
                        self._show_help()
                    elif user_input == '/clear':
                        self.conversation_history = []
                        print("🗑️  对话历史已清空")
                    elif user_input == '/quick':
                        self._quick_chat_mode()
                    elif user_input == '/status':
                        print(f"📊 当前对话数: {len(self.conversation_history)}")
                        print(f"⏱️  超时设置: {self.timeout_seconds}秒")
                    elif user_input.startswith('/timeout '):
                        self._set_timeout(user_input[9:])
                    else:
                        print("❌ 未知命令，输入 /help 查看帮助")
                    continue
                
                # 处理普通对话
                start_time = time.time()
                response = self.chat(user_input)
                end_time = time.time()
                
                print(f"🤖 AI ({end_time - start_time:.1f}s): {response}")
                
            except KeyboardInterrupt:
                print("\n\n输入 /exit 退出程序")
            except Exception as e:
                print(f"\n❌ 错误: {e}")
    
    def _quick_chat_mode(self):
        """快速聊天模式"""
        print("\n🚀 进入快速聊天模式（不保存历史）")
        print("输入 /back 返回正常模式")
        
        while True:
            try:
                user_input = input("\n🧑 Quick: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input == '/back':
                    print("返回正常模式")
                    break
                
                response = self.quick_chat(user_input)
                if response:
                    print(f"🤖 AI: {response}")
                    
            except KeyboardInterrupt:
                print("\n返回正常模式")
                break
    
    def _set_timeout(self, timeout_str):
        """设置超时时间"""
        try:
            timeout = int(timeout_str)
            if 10 <= timeout <= 120:
                self.timeout_seconds = timeout
                print(f"✅ 超时时间设置为 {timeout} 秒")
            else:
                print("❌ 超时时间应在10-120秒之间")
        except ValueError:
            print("❌ 请输入有效的数字")
    
    def _show_help(self):
        """显示帮助信息"""
        help_text = """
可用命令:
  /help     - 显示此帮助信息
  /exit     - 退出程序
  /clear    - 清空当前对话历史
  /quick    - 快速聊天模式（不保存历史）
  /status   - 显示当前状态
  /timeout <秒> - 设置请求超时时间(10-120秒)
        """
        print(help_text)

def main():
    # 设置信号处理，避免卡死时无法退出
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    chat = GF4Chat()
    chat.interactive_chat()

if __name__ == "__main__":
    main()
