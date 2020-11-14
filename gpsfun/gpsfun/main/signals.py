
def create_custom_user(sender, instance, signal, created, **kwargs):
    """When user is created also create a custom user."""
    from gpsfun.main.User.models import GPSFunUser
    if created:
        GPSFunUser.objects.create(user=instance)
    instance.gpsfunuser.save()
