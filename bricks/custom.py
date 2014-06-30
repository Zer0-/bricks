def customizable(name, bases, namespace):
    if 'custom_attributes' in namespace:
        custom_attributes = namespace['custom_attributes']
        del namespace['custom_attributes']
    else:
        custom_attributes = ()
    new_namespace = namespace.copy()
    def customnew(cls, name, **kwargs):
        try:
            new_attributes = {custom_attr: kwargs[custom_attr]
                              for custom_attr in custom_attributes}
        except KeyError as e:
            raise TypeError("{} requires named argument {}".format(
                cls.__name__, e.args[0]))
        clsnamespace = cls.__dict__.copy()
        if "__new__" in clsnamespace:
            del clsnamespace['__new__']
        namespace.update(clsnamespace)
        namespace.update(new_attributes)
        return type(name, bases, namespace)
    new_namespace['__new__'] = customnew
    return type(name, bases, new_namespace)
