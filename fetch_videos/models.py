from django.db.models import Model, DateField, CharField, TextField, Index, URLField


class VideoModel(Model):
    date = DateField()
    title = CharField(max_length=70)
    description = TextField(max_length=5000)
    video_id = CharField(primary_key=True, max_length=50)
    thumbnail = URLField()

    class Meta:
        indexes = [
            Index(fields=["title", "description"]),
        ]
