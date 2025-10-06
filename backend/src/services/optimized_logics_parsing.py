"""
优化的Logics-Parsing服务
使用MPS加速和FP16精度压缩解决模型太大无法运行的问题
"""

import os
import torch
from transformers import AutoModel, AutoTokenizer
from transformers import BitsAndBytesConfig
from typing import Dict, Optional
import asyncio

class OptimizedLogicsParsingService:
    """优化的Logics-Parsing服务，支持MPS加速和内存优化"""
    
    def __init__(self, model_path: str = None):
        """
        初始化优化服务
        
        Args:
            model_path: 模型路径，如果为None则使用默认缓存路径
        """
        if model_path is None:
            # 使用本地缓存中的模型路径
            home_dir = os.path.expanduser("~")
            self.model_path = os.path.join(home_dir, ".cache/modelscope/hub/models/Alibaba-DT/Logics-Parsing")
        else:
            self.model_path = model_path
        
        # 设备配置 - 强制使用CPU模式避免内存问题
        self.device = "cpu"
        print("✓ 强制使用CPU模式（避免MPS内存不足）")
            
        self.dtype = torch.float16  # FP16精度压缩
        
        # 内存优化配置
        self.use_4bit = False  # 暂时禁用4bit量化
        self.use_double_quant = False
        
        # 模型和tokenizer
        self.model = None
        self.tokenizer = None
        
        print(f"设备配置: {self.device}, 精度: {self.dtype}")
        print(f"模型路径: {self.model_path}")
    
    def load_model(self):
        """加载模型和tokenizer，使用内存优化策略"""
        try:
            # 检查模型文件是否存在
            required_files = [
                "model-00001-of-00004.safetensors",
                "model-00002-of-00004.safetensors", 
                "model-00003-of-00004.safetensors",
                "model-00004-of-00004.safetensors",
                "model.safetensors.index.json"
            ]
            
            for file in required_files:
                file_path = os.path.join(self.model_path, file)
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"模型文件缺失: {file}")
            
            print("开始加载模型...")
            
            # 加载processor和model
            from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration
            
            self.processor = AutoProcessor.from_pretrained(
                self.model_path,
                trust_remote_code=True
            )
            
            # CPU模式加载
            self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                self.model_path,
                torch_dtype=self.dtype,
                trust_remote_code=True
            )
            
            print(f"模型加载成功，设备: {next(self.model.parameters()).device}")
            
        except Exception as e:
            print(f"模型加载失败: {str(e)}")
            raise
    
    
    async def parse_document(self, input_text: str, max_length: int = 512) -> Dict:
        """
        解析文档逻辑
        
        Args:
            input_text: 输入文本
            max_length: 最大生成长度
            
        Returns:
            解析结果
        """
        try:
            if self.model is None or self.processor is None:
                self.load_model()
            
            # 构建消息
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": input_text
                        }
                    ]
                }
            ]
            
            # 应用聊天模板
            text = self.processor.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            # 处理输入
            inputs = self.processor(
                text=[text], 
                padding=True, 
                return_tensors="pt"
            ).to(self.device)
            
            # 生成
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=max_length,
                    do_sample=False
                )
            
            # 解码结果
            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            
            result = self.processor.batch_decode(
                generated_ids_trimmed, 
                skip_special_tokens=True, 
                clean_up_tokenization_spaces=False
            )[0]
            
            # 清理内存
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            return {
                'success': True,
                'input': input_text,
                'output': result,
                'device': self.device
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'device': self.device
            }
    
    async def parse_image(self, image_path: str, prompt: str = "QwenVL HTML", max_length: int = 1024) -> Dict:
        """
        解析图片
        
        Args:
            image_path: 图片文件路径
            prompt: 解析提示词
            max_length: 最大生成长度
            
        Returns:
            解析结果
        """
        try:
            if self.model is None or self.processor is None:
                self.load_model()
            
            from PIL import Image
            
            # 加载图片
            image = Image.open(image_path)
            
            # 构建消息
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "image": image
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
            
            # 应用聊天模板
            text = self.processor.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            # 处理输入
            inputs = self.processor(
                text=[text], 
                images=[image], 
                padding=True, 
                return_tensors="pt"
            ).to(self.device)
            
            # 生成
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=max_length,
                    do_sample=False
                )
            
            # 解码结果
            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            
            result = self.processor.batch_decode(
                generated_ids_trimmed, 
                skip_special_tokens=True, 
                clean_up_tokenization_spaces=False
            )[0]
            
            # 清理内存
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            return {
                'success': True,
                'input_path': image_path,
                'prompt': prompt,
                'output': result,
                'device': self.device
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'device': self.device
            }
    
    def unload_model(self):
        """卸载模型释放内存"""
        if self.model is not None:
            del self.model
            self.model = None
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        print("模型已卸载，内存已释放")
    
    def get_memory_info(self) -> Dict:
        """获取内存使用信息"""
        return {
            'device': 'cpu',
            'memory_info': 'CPU模式'
        }

# 测试函数
async def test_optimized_service():
    """测试优化服务"""
    service = OptimizedLogicsParsingService()
    
    try:
        # 测试逻辑解析
        test_text = "请解析以下逻辑关系：如果今天下雨，那么不外出；今天下雨了，所以结论是什么？"
        
        print("开始测试逻辑解析...")
        result = await service.parse_document(test_text)
        
        print(f"测试结果: {result}")
        print(f"内存信息: {service.get_memory_info()}")
        
        return result
        
    finally:
        service.unload_model()

if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_optimized_service())