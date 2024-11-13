"""
    :file:     utils.py  
    :author:   Zhu Dengda (zhudengda@mail.iggcas.ac.cn)  
    :date:     2024-11

    辅助函数

"""

import os

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


# 读取版本号
def read_version():
    with open(os.path.join(os.path.dirname(__file__), "_version.py")) as f:
        exec(f.read())
    return locals()['__version__']