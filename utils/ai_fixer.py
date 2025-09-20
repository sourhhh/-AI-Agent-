import requests
import json
import time
import os
import re
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class AIFixerEngine:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.api_url = "https://api.deepseek.com/chat/completions"
        self.max_retries = 3
        self.timeout = 30

    def is_available(self) -> bool:
        """检查AI修复引擎是否可用"""
        return bool(self.api_key)

    def extract_pure_code(self, ai_response: str) -> str:
        """从AI回复中提取纯净的代码"""
        if not ai_response:
            return ""

        text = ai_response.strip()

        # 处理代码块格式
        if '```' in text:
            code_blocks = re.findall(r'```(?:\w+)?\s*(.*?)```', text, re.DOTALL)
            if code_blocks:
                code = code_blocks[-1].strip()
                lines = code.split('\n')
                # 移除可能的语言标识行
                if len(lines) > 1 and lines[0].strip() in ['python', 'javascript', 'java', 'cpp', 'c++']:
                    return '\n'.join(lines[1:]).strip()
                return code

        return text

    def _build_detailed_prompt(self, problem_code: str, error_info: str, context_code: str, language: str) -> str:
        """构建详细的修复提示词"""

        # 根据错误类型提供具体指令
        specific_instructions = ""

        if "syntax" in error_info.lower() and "=" in error_info and ("if" in problem_code or "while" in problem_code):
            specific_instructions = "请检查条件语句中的赋值操作符(=)，在条件判断中应该使用比较操作符(==)或者使用'is None'。"

        elif "eval" in error_info.lower():
            specific_instructions = "请将eval替换为ast.literal_eval，并确保导入了ast模块。eval是不安全的，ast.literal_eval只能计算字面量表达式。"

        # 更具体的提示
        prompt = f"""你是一个专业的{language}代码修复专家。请修复以下代码中的错误。

    错误信息：{error_info}

    {specific_instructions}

    请特别注意：{error_info}

    需要修复的代码：
    ```{language}
    {problem_code}
    ```"""

        if context_code and context_code.strip():
            prompt += f"""

    相关上下文代码（供参考）：
    ```{language}
    {context_code}
    ```"""

        prompt += f"""

    修复要求：
    1. 只返回修复后的完整代码，不要任何解释
    2. 使用Markdown代码块包裹代码
    3. 确保修复指定的错误：{error_info}
    4. 保持代码格式和缩进正确
    5. 不要修改其他无关的代码

    修复后的代码："""

        return prompt

    def fix_with_ai(self, problem_code: str, error_info: str, context_code: str = "",
                    language: str = "python") -> Dict:
        """
        AI代码修复引擎
        """
        if not self.is_available():
            logger.warning("AI修复引擎不可用")
            return {
                "success": False,
                "fixed_code": problem_code,
                "error_message": "未设置DEEPSEEK_API_KEY环境变量",
                "original_code": problem_code
            }

        # 添加调试信息
        print(f"🔍 AI修复调试信息:")
        print(f"错误信息: {error_info}")
        print(f"原始代码前50字符: {problem_code[:50]}...")

        # 构建提示词
        prompt = self._build_detailed_prompt(problem_code, error_info, context_code, language)

        print(f"提示词前100字符: {prompt[:100]}...")

        # 准备API请求数据
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 2000
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # 重试机制
        for attempt in range(self.max_retries):
            try:
                logger.info(f"AI正在分析代码问题... (尝试 {attempt + 1}/{self.max_retries})")
                response = requests.post(self.api_url, headers=headers, json=data, timeout=self.timeout)

                if response.status_code == 200:
                    response_data = response.json()
                    ai_response = response_data['choices'][0]['message']['content']

                    print(f"AI原始响应: {ai_response[:200]}...")

                    fixed_code = self.extract_pure_code(ai_response)

                    print(f"提取的代码: {fixed_code[:100]}...")

                    if not fixed_code or fixed_code == problem_code:
                        return {
                            "success": False,
                            "fixed_code": problem_code,
                            "error_message": "AI未能提供有效的修复代码",
                            "original_code": problem_code
                        }

                    logger.info("AI修复完成！")
                    return {
                        "success": True,
                        "fixed_code": fixed_code,
                        "error_message": None,
                        "original_code": problem_code
                    }

                elif response.status_code == 429:
                    logger.warning("请求过于频繁，等待重试...")
                    time.sleep(2)
                    continue
                else:
                    error_msg = f"API错误: {response.status_code} - {response.text}"
                    print(f"API错误: {error_msg}")
                    return {
                        "success": False,
                        "fixed_code": None,
                        "error_message": error_msg,
                        "original_code": problem_code
                    }

            except requests.exceptions.Timeout:
                if attempt == self.max_retries - 1:
                    return {
                        "success": False,
                        "fixed_code": None,
                        "error_message": "请求超时",
                        "original_code": problem_code
                    }
                logger.warning("请求超时，重试中...")
                time.sleep(1)

            except Exception as e:
                if attempt == self.max_retries - 1:
                    return {
                        "success": False,
                        "fixed_code": None,
                        "error_message": f"发生错误: {str(e)}",
                        "original_code": problem_code
                    }
                logger.warning(f"发生错误，重试中: {str(e)}")
                time.sleep(1)

        return {
            "success": False,
            "fixed_code": None,
            "error_message": "所有重试尝试均失败",
            "original_code": problem_code
        }


# 全局实例
ai_fixer = AIFixerEngine()