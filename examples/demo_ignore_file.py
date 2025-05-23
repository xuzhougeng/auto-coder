# -*- coding: utf-8 -*-
import os
import time
import shutil
import tempfile
from pathlib import Path
from autocoder.common.file_monitor.monitor import FileMonitor, Change


# --- 示例用法 ---
if __name__ == '__main__':
    # 创建临时目录作为测试根目录
    example_run_dir = os.path.join(os.path.dirname(__file__), "ignore_test_temp")
    if os.path.exists(example_run_dir):
        shutil.rmtree(example_run_dir)
    os.makedirs(example_run_dir)
    
    print(f"创建临时测试目录: {example_run_dir}")

    # 在根目录下创建测试文件和目录结构
    # 1. 创建一些普通文件
    normal_file = os.path.join(example_run_dir, "normal_file.txt")
    with open(normal_file, "w") as f:
        f.write("这是一个普通文件")
    
    # 2. 创建一些应该被忽略的目录和文件
    node_modules_dir = os.path.join(example_run_dir, "node_modules")
    os.makedirs(node_modules_dir)
    ignored_file = os.path.join(node_modules_dir, "package.json")
    with open(ignored_file, "w") as f:
        f.write('{"name": "test-package"}')
    
    # 3. 创建一个自定义忽略的目录和文件
    custom_ignored_dir = os.path.join(example_run_dir, "custom_ignored")
    os.makedirs(custom_ignored_dir)
    custom_ignored_file = os.path.join(custom_ignored_dir, "ignored.txt")
    with open(custom_ignored_file, "w") as f:
        f.write("这个文件应该被忽略")
    
    # 4. 创建一个不应该被忽略的文件，但在自定义忽略的目录中
    not_ignored_dir = os.path.join(example_run_dir, "not_ignored")
    os.makedirs(not_ignored_dir)
    not_ignored_file = os.path.join(not_ignored_dir, "not_ignored.txt")
    with open(not_ignored_file, "w") as f:
        f.write("这个文件不应该被忽略")
    
    # 创建 .autocoderignore 文件
    ignore_file_path = os.path.join(example_run_dir, ".autocoderignore")
    with open(ignore_file_path, "w") as f:
        f.write("# 这是一个示例 .autocoderignore 文件\n")
        f.write("# 忽略 custom_ignored 目录\n")
        f.write("custom_ignored/\n")
        f.write("# 忽略所有 .log 文件\n")
        f.write("*.log\n")
    
    print("创建了测试文件结构和 .autocoderignore 文件")
    
    # 进入新的工作目录
    os.chdir(example_run_dir)
    from autocoder.common.ignorefiles.ignore_file_utils import should_ignore, _ignore_manager    
    
    # 初始化 FileMonitor 以便 IgnoreFileManager 可以监控 .autocoderignore 文件
    monitor = FileMonitor(root_dir=example_run_dir)
    monitor.start()
    
    # 测试哪些文件应该被忽略
    print("\n--- 测试哪些文件应该被忽略 ---")
    test_paths = [
        normal_file,                # 普通文件，不应该被忽略
        ignored_file,               # 在 node_modules 中，应该被忽略（默认排除）
        custom_ignored_file,        # 在自定义忽略目录中，应该被忽略
        not_ignored_file,           # 不在任何忽略目录中，不应该被忽略
        os.path.join(example_run_dir, "test.log")  # .log 文件，应该被忽略
    ]
    
    for path in test_paths:
        # 如果文件不存在（如 test.log），则创建它
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write("测试文件")
        
        # 测试是否应该被忽略
        should_be_ignored = should_ignore(path)
        print(f"路径: {path}")
        print(f"  - 是否应该被忽略: {should_be_ignored}")
    
    # 演示修改 .autocoderignore 文件后的自动重新加载
    print("\n--- 修改 .autocoderignore 文件并观察重新加载 ---")
    print("修改 .autocoderignore 文件，添加 'not_ignored/' 目录到忽略列表")
    
    with open(ignore_file_path, "a") as f:
        f.write("# 添加 not_ignored 目录到忽略列表\n")
        f.write("not_ignored\n")
    
    # 等待文件监控检测到变化并重新加载
    print("等待文件监控检测到变化...")
    time.sleep(10)
    
    # 再次测试 not_ignored_file 是否现在被忽略
    should_be_ignored_now = should_ignore(not_ignored_file)
    print(f"路径: {not_ignored_file}")
    print(f"相对路径: {os.path.relpath(not_ignored_file, os.getcwd())}")
    print(f"当前工作目录: {os.getcwd()}")
    
    # 获取 IgnoreFileManager 实例并打印规则
    from autocoder.common.ignorefiles.ignore_file_utils import _ignore_manager
    print(f"忽略规则文件路径: {_ignore_manager._ignore_file_path}")        
    print(f"  - 修改后是否应该被忽略: {should_be_ignored_now}")

    print(should_ignore("not_ignored/not_ignored.txt"))
    
    # 打印忽略规则文件
    with open(_ignore_manager._ignore_file_path, 'r', encoding='utf-8') as f:
        print(f"\n--- 忽略规则文件内容 ---\n{f.read()}")
    
    # 停止文件监控
    print("\n--- 停止文件监控 ---")
    monitor.stop()
    
    # 清理临时文件和目录
    print("--- 清理临时目录 ---")
    attempts = 3
    while attempts > 0:
        try:
            shutil.rmtree(example_run_dir)
            print(f"成功删除临时目录: {example_run_dir}")
            break
        except OSError as e:
            attempts -= 1
            print(f"警告: 删除临时目录失败 (尝试 {3-attempts}): {e}. 1秒后重试...")
            if attempts == 0:
                print(f"错误: 多次尝试后无法删除临时目录 {example_run_dir}。")
            time.sleep(1)
    
    # 重置 FileMonitor 单例
    FileMonitor.reset_instance()
    print("示例运行完成。")
