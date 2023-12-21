from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from .inference import CarLicensePlateDetector
import cv2
import os

# 初始化 CarLicensePlateDetector，假設模型文件在 'models/best.pt'
detector = CarLicensePlateDetector('models/best.pt')

@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({"error": "沒有提供文件或文件名為空"}, status=400)

        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        file_path = fs.path(filename)

        try:
            return process_file(filename, file_path)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

def process_file(filename, file_path):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        return process_image(file_path, filename)
    elif filename.lower().endswith(('.mp4', '.mov', '.avi')):
        return process_video(file_path, filename)
    else:
        return JsonResponse({"error": "不支持的文件格式"}, status=400)

def process_image(file_path, filename):
    info, processed_image = detector.recognize_license_plate(file_path)
    output_path = os.path.join('media', 'processed_' + filename)
    cv2.imwrite(output_path, cv2.cvtColor(processed_image, cv2.COLOR_RGB2BGR))
    response = HttpResponse(open(output_path, 'rb').read(), content_type="image/jpeg")
    response['Content-Disposition'] = 'attachment; filename=' + 'processed_' + filename
    return response

def process_video(file_path, filename):
    video_output_path = os.path.join('media', 'processed_' + filename)
    detector.process_video(file_path, video_output_path)
    response = HttpResponse(open(video_output_path, 'rb').read(), content_type="video/mp4")
    response['Content-Disposition'] = 'attachment; filename=' + 'processed_' + filename
    return response
