def _customizable(name, bases, namespace):
    basecls = type(name, bases, dict(namespace))
    original_new = basecls.__new__
    def new(cls, name, **kwargs):
        try:
            new_attributes = {custom_attr: kwargs[custom_attr]
                              for custom_attr in cls.custom_attributes}
        except KeyError as e:
            raise TypeError("{} requires named argument {}".format(
                cls.__name__, e.args[0]))
        newtype = type(name, (cls,), new_attributes)
        newtype.__new__ = lambda cls, *args, **kwargs: original_new(newtype)
        return newtype
    basecls.__new__ = new
    return basecls

class CustomComponent(metaclass=_customizable):
    pass
