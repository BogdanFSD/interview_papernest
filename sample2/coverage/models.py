from django.db import models

class CoverageData(models.Model):
    operator = models.CharField(max_length=50)
    x = models.IntegerField()
    y = models.IntegerField()
    g2 = models.BooleanField()
    g3 = models.BooleanField()
    g4 = models.BooleanField()
