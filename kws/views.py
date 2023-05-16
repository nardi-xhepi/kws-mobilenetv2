import sys
sys.path.append('C:/Users/nardi/website/kws/ia/scripts/')

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import split_voice
import mix_noise_and_data
# Create your views here.

def home(request):
    return render(request, 'html/index.html')

@csrf_exempt
def send_audio(request):
    if request.method == 'POST' and request.FILES['audio']:
        audio_file = request.FILES['audio']

        # do something with the audio file here
        file_path = 'C:/Users/nardi/website/kws/ia/user_data/' + audio_file.name
        # Open a file with write binary mode
        with open(file_path, 'wb+') as destination:
            # Write the uploaded file data to the custom directory
            for chunk in audio_file.chunks():
                destination.write(chunk)

        print("ok")
        split_voice.split()
        mix_noise_and_data.mix()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request'})