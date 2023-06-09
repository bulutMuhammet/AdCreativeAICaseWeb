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
