
def try_except_decorator(status_bar_str):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                status_bar = getattr(self, status_bar_str)()
                status_bar.showMessage(f"Error! {str(e)}", 3000)
                
        return wrapper
    return decorator