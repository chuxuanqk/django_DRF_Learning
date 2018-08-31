from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'
    # app名字后台显示中文
    verbose_name = "用户管理"


def ready(self):
    """
    Override this method in subclasses to run code when Django starts.
    """
    import users.signals