# AdCreativeAICaseWeb
Background Remover with OpenCV Python - WEB LIVE

See live demo at https://mbulut.pythonanywhere.com/

A background can also be generated directly from text using libraries such as DALL·E. I was going to try that too but I didn't have the API key :)

# How does the system work?</h5>
The system works in two ways. First, we check whether the background is transparent by looking at the alpha values of the photo you uploaded.
If there is a transparent background, we don't do anything about artificial intelligence. We simply combine the image with the background of your choice.

 However, if the picture is not transparent, we try to erase the background of the picture with <b>Canny edge detection</b> algorithm with <b>Opencv</b>.
This algorithm is not a deep learning algorithm, so it may be necessary to change the parameters to get the correct result.
When the background is deleted, we do the first thing we mentioned and add the newly selected background to the transparent picture.

_**Open source deep learning libraries such as https://github.com/danielgatis/rembg can also be used. However, I made it with opencv so that no 3rd source application is used. But with deep learning, much clearer results can be obtained.**_
## I created an example that the functions I wrote in this project will be made into a class and used in a real application.
``` python
from io import BytesIO
import cv2
import numpy as np
from PIL import Image


class BgRemover:

    def __init__(self, image, canny_low=20, canny_high=0.9, dilate_iter=10,
                 erode_iter=11):
        self.image = image
        self.canny_low = float(canny_low)
        self.canny_high = float(canny_high)
        self.dilate_iter = int(dilate_iter)
        self.erode_iter = int(erode_iter)

    def add_background(self, background_image_path):
        foreground_image = Image.open(self.image).convert("RGBA")
        background_image = Image.open(background_image_path).convert("RGBA")

        resized_background = background_image.resize(foreground_image.size,
                                                     Image.ANTIALIAS)

        merged_image = Image.new("RGBA", foreground_image.size)
        merged_image.paste(resized_background, (0, 0))
        merged_image.paste(foreground_image, (0, 0), mask=foreground_image)

        return merged_image

    def is_transparent(self):
        image = Image.open(self.image).convert("RGBA")
        alpha_range = image.getextrema()[-1]
        if alpha_range == (255, 255):
            return False
        else:
            return True

    def remove_background(self):
        image_file = self.image.read()
        # BytesIO kullanarak görüntüyü PIL Image nesnesine dönüştür
        image = Image.open(BytesIO(image_file))
        # Resmi oku
        image = np.array(image)
        # Resmi GRAYSCALE'e dönüştür
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Kenar tespiti için Canny uygula
        canny = cv2.Canny(gray, self.canny_low, self.canny_high)

        # Kenarları genişletmek için bir çekirdek tanımla
        kernel = np.ones((3, 3), np.uint8)

        # Genişletme ve erozyon işlemlerini uygula
        dilated = cv2.dilate(canny, kernel, iterations=self.dilate_iter)
        eroded = cv2.erode(dilated, kernel, iterations=self.erode_iter)

        # Konturları bul
        contours, _ = cv2.findContours(eroded, cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)

        # Konturların alanını hesapla ve en büyük olanı seç
        max_area = 0
        max_contour = None
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > max_area:
                max_area = area
                max_contour = contour

        # Maske oluştur
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        cv2.drawContours(mask, [max_contour], -1, (255), thickness=cv2.FILLED)

        # Alfa kanalı oluştur
        alpha = np.ones(image.shape[:2], dtype=np.uint8) * 255
        alpha = cv2.bitwise_and(alpha, alpha, mask=mask)

        # RGB renk uzayında transparan kanalı eklemek için resmi dönüştür
        image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

        # Alfa kanalını ekle
        image[:, :, 3] = alpha

        return image
 ```
