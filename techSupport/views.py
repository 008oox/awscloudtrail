import os, locale, glob, re
from django.shortcuts import render, redirect, Http404
from django.http import JsonResponse, FileResponse, HttpResponseRedirect
import subprocess
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

BASE_DIR = os.path.join(settings.BASE_DIR, 'techtools')

def get_directory_structure(rootdir, relative_path=""):
    tree = []
    try:
        items = os.listdir(rootdir)
    except Exception as e:
        items = []
    pattern = re.compile(r'^[a-zA-Z0-9]')

    for item in items:
        if not pattern.match(item):
            continue
        item_full_path = os.path.join(rootdir, item)
        item_rel_path = os.path.join(relative_path, item)

        if os.path.isdir(item_full_path):
            tree.append({
                'name': item,
                'type': 'dir',
                'path': item_rel_path,
                'children': get_directory_structure(item_full_path, item_rel_path)
            })
        else:
            tree.append({
                'name': item,
                'type': 'file',
                'path': item_rel_path
            })
    return tree

def list_files(request):
    if request.user.is_authenticated:
        file_tree = get_directory_structure(BASE_DIR, "")
        return render(request, 'list_files.html', {'file_tree': file_tree})
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/techSupport/list_files/')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})

    return render(request, 'login.html')

def view_file(request):
    rel_path = request.GET.get('path')
    if not rel_path:
        raise Http404("未指定文件路径")
    
    full_path = os.path.join(BASE_DIR, rel_path)
    full_path = os.path.abspath(full_path)
    if not full_path.startswith(os.path.abspath(BASE_DIR)):
        raise Http404("无效的文件路径")
    
    if not os.path.isfile(full_path):
        raise Http404("文件不存在")
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        content = f"读取文件出错: {e}"
    
    return render(request, 'view_file.html', {
        'file_name': os.path.basename(full_path),
        'content': content,
    })


def run_task(request):
    if request.method == "POST":
        file_path = request.POST.get('file_path')
        parameter = request.POST.get('parameter', '').strip()
        parameter = parameter.replace(" ", "")

        if not file_path or not parameter:
            raise Http404("缺少参数")
        if not re.fullmatch(r'^(csv|HFS[\w-]+)$', parameter, re.IGNORECASE):
            raise Http404("非法参数")

        full_path = os.path.join(BASE_DIR, file_path)
        full_path = os.path.abspath(full_path)

        if not full_path.startswith(os.path.abspath(BASE_DIR)) or not os.path.isfile(full_path):
            raise Http404("无效的文件路径或文件不存在")

        command = ["python3", full_path, parameter]
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            output = result.stdout
            error = result.stderr
            exit_code = result.returncode
        except Exception as e:
            output = ""
            error = str(e)
            exit_code = -1

        csv_files = sorted(glob.glob(os.path.join(settings.BASE_DIR, "*.csv")), key=os.path.getmtime, reverse=True)
        latest_csv = csv_files[0] if csv_files else None

        return render(request, 'run_task_result.html', {
            'file_name': os.path.basename(full_path),
            'command': " ".join(command),
            'output': output,
            'error': error,
            'exit_code': exit_code,
            'csv_file_path': latest_csv,
            'csv_filename': os.path.basename(latest_csv) if latest_csv else None  
        })
    else:
        return redirect('list_files')


@csrf_exempt
def download_file(request):
    if request.method == 'POST':
        csv_filename = request.POST.get('csv_filename')
        if not csv_filename:
            raise Http404("未指定文件名")

        full_path = csv_filename

        if not full_path.startswith(os.path.abspath(settings.BASE_DIR)) or not os.path.isfile(full_path):
            raise Http404("无效的文件路径或文件不存在")

        try:
            file_stream = open(full_path, 'rb')
            response = FileResponse(file_stream, as_attachment=True, filename=os.path.basename(full_path))

            def delete_file():
                try:
                    os.remove(full_path)
                    print(f"文件已删除: {full_path}")
                except Exception as e:
                    print(f"删除文件失败: {e}")

            response.close = delete_file
            return response
        except Exception as e:
            raise Http404("文件无法打开")
    else:
        return Http404("无效的请求方法")
