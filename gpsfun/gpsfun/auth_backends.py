from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
#from django.db.models.loading import get_model

class CustomUserModelBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        print('auth', username, password)
        try:
            user = self.user_class.objects.get(username=username)
            if user.check_password(password):
                return user
        except self.user_class.DoesNotExist:
            print('==================')
            return None

    def get_user(self, user_id):
        print('get user', user_id)
        try:
            return self.user_class.objects.get(pk=user_id)
        except self.user_class.DoesNotExist:
            print('*****************')
            return None

    @property
    def user_class(self):
        print('user class. get model', get_user_model())
        return get_user_model()
        #if not hasattr(self, '_user_class'):
            #self._user_class = get_model(*settings.CUSTOM_USER_MODEL.split('.', 2))
            #if not self._user_class:
                #raise ImproperlyConfigured('Could not get custom user model')
        #return self._user_class
