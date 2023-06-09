# Imports for compressing images
import uuid
from io import BytesIO
import sys
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile

from datetime import datetime


class CompressImageBeforeSaveMixin:
    def save(self, *args, **kwargs):
        try:
            # Opening the uploaded image
            image = Image.open(self.image)

            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")

            # Correct image orientation if necessary
            if hasattr(image, '_getexif') and image._getexif() is not None:
                exif = dict(image._getexif().items())
                orientation = exif.get(0x0112)
                if orientation is not None:
                    if orientation == 3:
                        image = image.rotate(180, expand=True)
                    elif orientation == 6:
                        image = image.rotate(270, expand=True)
                    elif orientation == 8:
                        image = image.rotate(90, expand=True)

            output = BytesIO()

            # Resize/modify the image
            original_width, original_height = image.size
            aspect_ratio = original_height / original_width
            desired_width = self.image_width
            desired_height = round(desired_width * aspect_ratio)

            image = image.resize((desired_width, desired_height))

            # after modifications, save it to the output
            image.save(output, format='JPEG', quality=90)
            output.seek(0)

            # change the imagefield value to be the newley modifed image value
            date_string = datetime.now().strftime('%Y_%m_%d')
            random_uuid = str(uuid.uuid4())[:8]
            self.image = InMemoryUploadedFile(output, 'ImageField', f"{date_string}_{self.image_name_suffix}_{random_uuid}.jpg",
                                              'image/jpeg', sys.getsizeof(output), None)

        except ValueError:
            pass

        super().save(*args, **kwargs)