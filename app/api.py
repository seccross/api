from sanic import Sanic, response
from sanic.request import File
import subprocess
import os
import json
import uuid
from .analysis import run_myth

def create_app(storage_dir):
    app = Sanic("MythAPI")

    def dir_path(request_id):
        return os.path.join(storage_dir, request_id[:2], request_id[2:4], request_id[4:])


    @app.post("/analyze")
    async def analyze_file(request):
        file_param = request.files.get('file')
        contract_name = request.form.get('contract_name')  # 假设参数以JSON格式传递
        args = request.form.get('args')  # 假设参数以JSON格式传递

        if not file_param:
            return response.json({"error": "No file provided"}, status=400)

        # 解析参数
        try:
            args = json.loads(args) if args else []
        except json.JSONDecodeError:
            return response.json({"error": "Invalid JSON format in args"}, status=400)
        
         # 确保存储目录存在
        os.makedirs(storage_dir, exist_ok=True)

        file: File = file_param[0]
        request_id = str(uuid.uuid4())
        session_dir = dir_path(request_id)

         # 异步执行myth分析
        request_id = await run_myth(file, contract_name, args, session_dir)
    
        # 返回request id
        return response.json({"request_id": request_id})
    
    @app.get("/result/<request_id>")
    async def get_result(request, request_id):
        # 构建结果文件的路径
        session_dir = dir_path(request_id)
        result_file_path = os.path.join(session_dir, f"result.json")

        if os.path.exists(result_file_path):
            with open(result_file_path, 'r') as file:
                result = file.read()
            return response.json({"result": result})
        if os.path.exists(session_dir):
            return response.json({"status": "Processing"}, status=202)
        return response.json({"error": "Result not found or still processing"}, status=202)

    return app