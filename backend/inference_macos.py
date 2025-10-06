#!/usr/bin/env python3
"""
修改版的Logics-Parsing推理脚本，支持macOS
"""
import torch
import os 
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from PIL import Image,ImageFont,ImageDraw
import json 
import re
import math 
import cv2 
import argparse


def inference(img_url, prompt, system_prompt="You are a helpful assistant"):
    # 确保使用绝对路径
    if not os.path.isabs(img_url):
        img_url = os.path.abspath(img_url)
    image = Image.open(img_url)
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
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
    
    # 强制使用CPU模式避免内存问题
    device = "cpu"
    print("使用CPU设备（避免MPS内存不足）")
    
    # 模型路径
    model_path = os.path.expanduser("~/.cache/modelscope/hub/models/Alibaba-DT/Logics-Parsing")
    
    # 加载模型到CPU，不使用device_map
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        model_path, 
        torch_dtype=torch.float16,  # 使用FP16
        device_map=None,  # 不使用device_map
        trust_remote_code=True
    )
    model = model.to(device)
    
    processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)
    
    text = processor.apply_chat_template(
        messages, 
        tokenize=False, 
        add_generation_prompt=True
    )
    
    inputs = processor(
        text=[text], 
        images=[image], 
        padding=True, 
        return_tensors="pt"
    )
    
    inputs = inputs.to(device)
    
    # 生成
    generated_ids = model.generate(
        **inputs,
        max_new_tokens=1024,
        do_sample=False
    )
    
    generated_ids_trimmed = [
        out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    
    response = processor.batch_decode(
        generated_ids_trimmed, 
        skip_special_tokens=True, 
        clean_up_tokenization_spaces=False
    )
    
    return response[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, required=True)
    parser.add_argument("--image_path", type=str, required=True)
    parser.add_argument("--output_path", type=str, required=True)
    parser.add_argument("--prompt", type=str, default="QwenVL HTML")
    
    args = parser.parse_args()
    
    try:
        # 执行推理
        result = inference(args.image_path, args.prompt)
        
        # 保存结果
        with open(args.output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        
        print(f"推理完成，结果保存到: {args.output_path}")
        
    except Exception as e:
        print(f"推理失败: {str(e)}")
        raise


if __name__ == "__main__":
    main()