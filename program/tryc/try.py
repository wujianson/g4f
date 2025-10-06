import os
import sys
import shlex

def run_ls(args):
    """
    列出目录内容
    """
    path = args[1] if len(args) > 1 else "."
    try:
        entries = os.listdir(path)
        for e in entries:
            print(e)
    except OSError as e:
        print(f"ls: {e}", file=sys.stderr)

def run_cd(args):
    """
    改变工作目录
    """
    path = args[1] if len(args) > 1 else os.path.expanduser("~")
    try:
        os.chdir(path)
    except OSError as e:
        print(f"cd: {e}", file=sys.stderr)

def run_pwd(args):
    """
    输出当前工作目录
    """
    print(os.getcwd())

def main_loop():
    """
    主循环，读取用户输入并执行
    """
    while True:
        try:
            # 显示当前目录作为提示符
            prompt = f"{os.getcwd()}$ "
            line = input(prompt)
        except EOFError:
            # Ctrl-D 退出
            print()
            break
        except KeyboardInterrupt:
            # Ctrl-C 取消当前输入，继续循环
            print()
            continue

        if not line.strip():
            continue  # 空行不做任何事

        # 解析命令行（支持空格、引号等）
        try:
            args = shlex.split(line)
        except ValueError as e:
            print(f"解析错误: {e}", file=sys.stderr)
            continue

        cmd = args[0].lower()

        if cmd == "exit":
            break
        elif cmd == "pwd":
            run_pwd(args)
        elif cmd == "cd":
            run_cd(args)
        elif cmd == "ls":
            run_ls(args)
        else:
            print(f"{cmd}: command not found", file=sys.stderr)

if __name__ == "__main__":
    main_loop()
