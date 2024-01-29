import asyncio
import subprocess
import os

TS_MYTH = '/usr/local/bin/myth'
TS_PARAMS = ['analyze', '--parallel-solving', '-o', 'jsonv2']

XG_SLITHER = '/usr/local/xguard/bin/slither'
XG_PARAMS = ['--checklist', '--show-ignored-findings']

XG_T1 = 'incomplete-event,incorrect-event'
XG_T2 = 'miss-crosschain-data-check'
XG_T3 = 'crosschain-message-injection'
XG_DETECT = '--detect'

async def run_myth(file, contract_name, args, session_dir):

    os.makedirs(session_dir, exist_ok=True)

    original_file_name = file.name

    result_file_path = os.path.join(session_dir, f"result.json")
    err_file_path = os.path.join(session_dir, f"error.json")
    # 将上传的文件也保存在相同的目录下
    saved_file_path = os.path.join(session_dir, original_file_name)

    # 保存上传的文件
    with open(saved_file_path, 'wb') as saved_file:
        saved_file.write(file.body)
    
    args = TS_PARAMS + [f"{saved_file_path}:{contract_name}"] + args

    # 异步运行myth程序
    process = await asyncio.create_subprocess_exec(
        TS_MYTH, *args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    with open(result_file_path, 'wb') as result_file:  
        result_file.write(stdout)
    if process.returncode == 0:
        with open(err_file_path, 'wb') as err_file:
            err_file.write(stderr)

# 1: 异常退出；2：发现bug；0：未发现bug
async def run_slither(file, solc_version, env, checks, args, session_dir):

    os.makedirs(session_dir, exist_ok=True)

    original_file_name = file.name

    result_file_path = os.path.join(session_dir, f"result.json")
    report_file_path = os.path.join(session_dir, f"report.md")
    err_file_path = os.path.join(session_dir, f"error.json")
    ok_file_path = os.path.join(session_dir, f"OK")
    # 将上传的文件也保存在相同的目录下
    saved_file_path = os.path.join(session_dir, original_file_name)

    # 保存上传的文件
    with open(saved_file_path, 'wb') as saved_file:
        saved_file.write(file.body)
    
    check_list = checks.split(",")

    detects = ''

    if 'T1' in check_list:
        detects += XG_T1
    if 'T2' in check_list:
        detects += ',' + XG_T2
    if 'T3' in check_list:
        detects += ',' + XG_T3
    
    args =  [f"{saved_file_path}", ] + [XG_DETECT, detects] + XG_PARAMS + ["--solc-solcs-select", f"{solc_version}", "--json", f"{result_file_path}"] + args

    # 异步运行myth程序
    process = await asyncio.create_subprocess_exec(
        XG_SLITHER, *args,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    with open(report_file_path, 'wb') as report_file:  
        report_file.write(stdout)
    if process.returncode == 1:
        with open(err_file_path, 'wb') as err_file:
            err_file.write(stderr)
    if process.returncode == 0:
        with open(ok_file_path, 'w') as ok_file:
            ok_file.write('OK')
