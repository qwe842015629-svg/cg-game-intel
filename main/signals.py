from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
import os

from .media_library import upsert_media_asset

# Ignore these models to prevent recursion or duplicates
IGNORE_MODELS = ['MediaAsset', 'Session', 'LogEntry', 'ContentType', 'Permission', 'Group', 'User']

@receiver(post_save)
def sync_images_to_media_library(sender, instance, created, **kwargs):
    """
    Signal to automatically sync any ImageField upload to the MediaAsset library.
    """
    # 1. Check if model should be ignored
    model_name = sender.__name__
    if model_name in IGNORE_MODELS:
        return

    # 2. Iterate over all fields to find ImageFields
    for field in sender._meta.fields:
        if isinstance(field, models.ImageField):
            file_field = getattr(instance, field.name)
            
            # Check if file exists and has content
            if file_field and hasattr(file_field, 'name') and file_field.name:
                filename = os.path.basename(file_field.name) or f"{model_name.lower()}-{field.name}.jpg"

                try:
                    upsert_media_asset(
                        file_obj=file_field,
                        requested_name=filename,
                        category='other',
                        alt_text=f"Synced from {model_name}",
                        create_thumbnail=True,
                    )
                except Exception as e:
                    print(f"Failed to sync image from {model_name} to MediaLibrary: {e}")
