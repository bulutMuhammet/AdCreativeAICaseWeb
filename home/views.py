from io import BytesIO

from PIL import Image
from django.core.files import File
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect
# Create your views here.
from home.ai_helpers import BgRemover
from home.models import ImageRequest


def index(request):
    if request.method == "POST":
        bg_rm = BgRemover(request.FILES["file"])
        img_rq = ImageRequest.objects.create(original_image=bg_rm.image)
        if bg_rm.is_transparent():
            img_rq.bg_removed_image = bg_rm.image
            img_rq.is_transparent = True
            img_rq.save()
            return redirect("add_bg", img_rq.id)
        else:
            return redirect("remove_bg",img_rq.id)
    return render(request, 'index.html')

def add_bg(request, id):
    img_rq = ImageRequest.objects.get(id=id)
    # if os.path.exists(image_path):
    #     os.remove(image_path)
    if request.method == "POST":
        bg_rm = BgRemover(img_rq.bg_removed_image.file)
        merged_img = bg_rm.add_background(request.FILES["file"])

        image_file = BytesIO()
        merged_img.save(image_file, format='png')
        img_rq.processed_image.save(f'pr{img_rq.id}.png',File(image_file))
        img_rq.save()
        return redirect("result", img_rq.id)

    return render(request, 'add_background.html', {"img_rq":img_rq})

def remove_bg(request,id):
    img_rq = ImageRequest.objects.get(id=id)
    if request.method == "POST":
        canny_low = request.POST["canny_low"]
        canny_high = request.POST["canny_high"]
        dilate_iter = request.POST["dilate_iter"]
        erode_iter = request.POST["erode_iter"]
        bg_rm = BgRemover(img_rq.original_image.file, canny_low, canny_high, dilate_iter, erode_iter)
        array = bg_rm.remove_background()
        image_pil = Image.fromarray(array)

        # PIL Image'ı bayt dizisine dönüştür
        image_bytes = BytesIO()
        image_pil.save(image_bytes, format='png')

        # Bayt dizisini Django FileField'a kaydet
        img_rq.bg_removed_image.save(f'pr{img_rq.id}.png', ContentFile(image_bytes.getvalue()), save=True)
        return redirect("add_bg", img_rq.id)
    return render(request, 'remove_bg.html', {"img_rq":img_rq})


def result(request, id):
    img_rq = ImageRequest.objects.get(id=id)
    return render(request, 'result.html', {"img_rq":img_rq})
