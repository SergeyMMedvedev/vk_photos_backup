from progress.bar import Bar


def progress(bar_name, operation, attr=None):
    bar = Bar(bar_name, max=1)
    def custom_decorator(f):
        def wrapper(self, *args, **kwargs):
            bar.suffix  = f'{operation} - %(percent)d%%'.ljust(60, ' ')
            value = ''
            if attr:
                value = self.__dict__[attr]
            if value:
                bar.suffix  = f'{operation} "{value}" - %(percent)d%%'.ljust(60, ' ')
            bar.update()
            result = f(self, *args,**kwargs)
            bar.update()
            bar.next()
            if bar.index >= bar.max:
                bar.finish()
            return result
        return wrapper
    return custom_decorator
