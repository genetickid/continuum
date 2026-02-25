from django.conf import settings
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BackgroundTask(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SUCCESS = 'SUCCESS', 'Success'
        FAILED = 'FAILED', 'Failed'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='background_tasks'
    )
    task_id = models.CharField(max_length=255, unique=True)
    task_name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return (
            f'User: {self.user.username}; '
            f'Task: {self.task_name}; '
            f'Status: {self.status}'
        )

    @classmethod
    def change_status(cls, db_task_id: int, new_status: str):
        cls.objects.filter(id=db_task_id).update(status=new_status)
