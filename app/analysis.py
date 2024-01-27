import asyncio
import subprocess
import os

myth = '/usr/local/bin/myth'
params = ['analyze', '--parallel-solving', '-o jsonv2']

async def run_myth(file, contract_name, args, session_dir):

    os.makedirs(session_dir, exist_ok=True)

    original_file_name = file.name

    result_file_path = os.path.join(session_dir, f"result.json")
    # 将上传的文件也保存在相同的目录下
    saved_file_path = os.path.join(session_dir, original_file_name)

    # 保存上传的文件
    with open(saved_file_path, 'wb') as saved_file:
        saved_file.write(file.body)
    
    args = params + [f"{saved_file_path}:{contract_name}"] + args

    # 异步运行myth程序
    process = await asyncio.create_subprocess_exec(
        myth, *args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    with open(result_file_path, 'w') as result_file:
        
        result_file.write(stdout)
        if process.returncode == 0:
            result_file.write(f"Error: {stderr.decode()}")
