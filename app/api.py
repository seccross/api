from sanic import Sanic, response
from sanic.request import File
from sanic_cors import CORS
import os
import json
import uuid
import asyncio
from .analysis import run_myth, run_slither

def create_app(storage_dir):
    app = Sanic("MythAPI")
    CORS(app)

    def dir_path(job_name, request_id):
        return os.path.join(storage_dir, job_name, request_id[:2], request_id[2:4], request_id[4:])


    @app.post("/analyze")
    async def analyze_file(request):
        file = request.files.get('file')
        contract_name = request.form.get('contract_name')  # 假设参数以JSON格式传递
        args = request.form.get('args')  # 假设参数以JSON格式传递

        if not file:
            return response.json({"error": "No file provided"}, status=400)

        # 解析参数
        try:
            args = json.loads(args) if args else []
        except json.JSONDecodeError:
            return response.json({"error": "Invalid JSON format in args"}, status=400)
        
         # 确保存储目录存在
        os.makedirs(storage_dir, exist_ok=True)

        request_id = str(uuid.uuid4())
        session_dir = dir_path("tsniffer", request_id)

         # 异步执行myth分析
        asyncio.create_task(run_myth(file, contract_name, args, session_dir))
    
        # 返回request id
        return response.json({"request_id": request_id})
    
    @app.get("/result/<request_id>")
    async def get_result(request, request_id):
        # 构建结果文件的路径
        session_dir = dir_path("tsniffer", request_id)
        result_file_path = os.path.join(session_dir, f"result.json")
        error_file_path = os.path.join(session_dir, f"error.json")

        if os.path.exists(error_file_path):
            with open(result_file_path, 'r') as file:
                error = json.load(file)
            return response.json({"error": error}, status=422)

        if os.path.exists(result_file_path):
            with open(result_file_path, 'r') as file:
                result = json.load(file)
            return response.json({"result": result})
        if os.path.exists(session_dir):
            return response.json({"status": "Processing"}, status=202)
        return response.json({"error": "Request not found"}, status=404)
    
    # @app.route('/favicon.ico')
    # async def favicon(request):
    #     return await response.file('/var/mythapi/favicon.ico')
    
    @app.post("/xg/analyze")
    async def xg_analyze_file(request):
        file = request.files.get('file')
        solc_version = request.form.get('solc_version')  # 假设参数以JSON格式传递
        
        send_funcs = request.form.get('send_funcs')
        receive_funcs = request.form.get('receive_funcs')
        events = request.form.get('events')
        send_stores = request.form.get('send_stores')

        env_vars = {'SEND_FUNCS': send_funcs, 'RECEIVE_FUNCS': receive_funcs, 'EVENTS': events, 'SEND_STORES': send_stores}
        env = {k: v for k, v in env_vars.items() if v is not None}
        
        checks = request.form.get('check')
        args = request.form.get('args')  # 假设参数以JSON格式传递

        if not file:
            return response.json({"error": "No file provided"}, status=400)

        # 解析参数
        try:
            args = json.loads(args) if args else []
        except json.JSONDecodeError:
            return response.json({"error": "Invalid JSON format in args"}, status=400)
        
         # 确保存储目录存在
        os.makedirs(storage_dir, exist_ok=True)

        request_id = str(uuid.uuid4())
        session_dir = dir_path("xguard", request_id)

         # 异步执行myth分析
        asyncio.create_task(run_slither(file, solc_version, env, checks, args, session_dir))
    
        # 返回request id
        return response.json({"request_id": request_id})
    
    @app.get("/xg/result/<request_id>")
    async def xg_get_result(request, request_id):
        # 构建结果文件的路径
        session_dir = dir_path("xguard", request_id)
        result_file_path = os.path.join(session_dir, f"result.json")
        report_file_path = os.path.join(session_dir, f"report.md")
        error_file_path = os.path.join(session_dir, f"error.json")
        ok_file_path = os.path.join(session_dir, f"OK")

        if os.path.exists(error_file_path):
            with open(error_file_path, 'r') as file:
                error = file.read()
            return response.json({"error": error}, status=201)
        
        pass_check = True if os.path.exists(ok_file_path) else False
        
        if os.path.exists(result_file_path):
            with open(result_file_path, 'r') as file:
                result = json.load(file)
                with open(report_file_path, 'r') as file:
                    report = file.read()
                return response.json({"passed": pass_check, "result": result, "report": report})
        
        if os.path.exists(session_dir):
            return response.json({"status": "Processing"}, status=202)
        
        return response.json({"error": "Request not found"}, status=404)
    
    @app.route('/xg/favicon.ico')
    async def favicon(request):
        return await response.file('/var/mythapi/favicon.ico')

    return app