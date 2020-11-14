from DjHDGutils.dbutils import get_object_or_none



class RuntimeManager(object):

    def __getattr__(self,key):
        from models import RuntimeVariable
        rec = get_object_or_none(RuntimeVariable, key = key)
        if rec is None:
            raise AttributeError
        return rec.value

    def __setattr__(self,key,value):
        from models import RuntimeVariable

        rec = get_object_or_none(RuntimeVariable,key=key)
        if rec is None:
            raise AttributeError
        rec.value = value
        rec.save()


runtime_setting = RuntimeManager()


class SafeRuntimeManager(object):

    def __getattr__(self,key):
        from models import RuntimeVariable
        rec = get_object_or_none(RuntimeVariable, key = key)
        if rec is None:
            return 'undef: %s' % key

        return rec.value


get_variable = SafeRuntimeManager()


__all__ = [runtime_setting, get_variable]
