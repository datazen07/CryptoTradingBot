from django.db import models


class Chart(models.Model):
    image = models.ImageField(upload_to='media/')
    objects = models.Manager()

    def get_image(self):
        return self.image

    def __str__(self):
        return self.image

    # Metadata
    class Meta:
        ordering = ['image']
