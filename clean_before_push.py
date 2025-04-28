#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
清理脚本，用于在推送代码到仓库前清理不需要的文件
"""

import os
import shutil

def clean_pycache():
    """清理所有的__pycache__目录和.pyc文件"""
    # 清理根目录下的__pycache__
    if os.path.exists('__pycache__'):
        print("删除 __pycache__ 目录")
        shutil.rmtree('__pycache__')

    # 清理子目录下的__pycache__
    for root, dirs, files in os.walk('.'):
        for dir in dirs:
            if dir == '__pycache__':
                pycache_path = os.path.join(root, dir)
                print(f"删除 {pycache_path}")
                shutil.rmtree(pycache_path)

        # 清理.pyc, .pyo, .pyd文件
        for file in files:
            if file.endswith(('.pyc', '.pyo', '.pyd')):
                file_path = os.path.join(root, file)
                print(f"删除 {file_path}")
                os.remove(file_path)

def clean_migration_scripts():
    """保留迁移脚本，但提示用户检查"""
    migration_scripts = ['migrate_db.py', 'migrate_weight.py', 'init_db.py']
    print("\n数据库迁移和初始化脚本:")
    for script in migration_scripts:
        if os.path.exists(script):
            print(f"  - {script} (已保留)")
    print("注意: 这些脚本已保留在代码仓库中，用于在新环境中初始化数据库。")

def clean_sensitive_info():
    """提示用户检查敏感信息"""
    print("\n警告: config.py 包含数据库连接信息，请确保这些信息适合推送到代码仓库。")
    print("如果需要，请将敏感信息替换为环境变量或占位符。")

def main():
    print("开始清理不需要的文件...")

    # 清理Python缓存文件
    clean_pycache()

    # 清理临时迁移脚本
    clean_migration_scripts()

    # 提示检查敏感信息
    clean_sensitive_info()

    print("\n清理完成！现在可以安全地推送代码到仓库了。")

if __name__ == "__main__":
    main()
