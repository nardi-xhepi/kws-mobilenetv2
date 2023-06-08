import sys
sys.path.append('C:/Users/nardi/website/kws/ia/scripts/')

from django.shortcuts import render
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt

import split_voice
from trainer import *

keyword_dir = "C:\\Users\\nardi\\Desktop\\TSP\\Developpement informatique\\data\\axel"
noise_dir = "C:\\Users\\nardi\\Desktop\\TSP\\Developpement informatique\\data\\noise_chunk"
unknown_dir = "C:\\Users\\nardi\\Desktop\\TSP\\Developpement informatique\\data\\unknown"

def home(request):
    return render(request, 'html/index.html')

import threading
import uuid

tasks = {}

def long_running_task(audio_file, task_id):


    split_voice.split()

    #C:\\Users\\nardi\\
    dataloader = DataLoader(axel_dir = "C:\\Users\\nardi\\Desktop\\TSP\\Developpement informatique\\data\\axel",
    noise_dir = "C:\\Users\\nardi\\Desktop\\TSP\\Developpement informatique\\data\\noise_chunk",
    unknown_dir = "C:\\Users\\nardi\\Desktop\\TSP\\Developpement informatique\\data\\unknown")
    """
    dataloader = DataLoader(axel_dir = "C:\\Users\\nardi\\website\\kws\\ia\\data\\keyword",
                            noise_dir = "C:\\Users\\nardi\\website\\kws\\ia\\data\\noise",
                            unknown_dir = "C:\\Users\\nardi\\website\\kws\\ia\\data\\unknown")
    
    """
    import warnings
    warnings.filterwarnings("ignore")
    dataloader.load_data()
    trainer = Trainer(dataloader.all_data)
    trainer.train()

    tasks[task_id] = 'complete'

@csrf_exempt
def check_task_status(request):
    task_id = request.GET.get('task_id')
    if task_id in tasks:
        return JsonResponse({'status': tasks[task_id]})
    else:
        return JsonResponse({'status': 'not found'})

#
@csrf_exempt
def send_audio(request):
    if request.method == 'POST' and request.FILES['audio']:
        audio_file = request.FILES['audio']

        file_path = 'C:/Users/nardi/website/kws/ia/user_data/' + audio_file.name
    
        with open(file_path, 'wb+') as destination:
            for chunk in audio_file.chunks():
                destination.write(chunk)

        # create a unique task id
        task_id = str(uuid.uuid4())
        tasks[task_id] = 'in progress'

        # start the long running task in a separate thread
        threading.Thread(target=long_running_task, args=(audio_file, task_id)).start()

        # immediately respond with the task id
        return JsonResponse({'task_id': task_id})

    else:
        return JsonResponse({'success': False, 'error': 'Invalid request'})


@csrf_exempt
def send_file(request):
    # get the file of the trained neural network
    file_path = 'C:/Users/nardi/website/kws/ia/user_data/model.h5'  # use your file path
    response = FileResponse(open(file_path, 'rb'), content_type='application/x-hdf')
    response['Content-Disposition'] = 'attachment; filename=model.h5'
    return response
