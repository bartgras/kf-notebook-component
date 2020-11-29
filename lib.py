import sys
import os
import tempfile
import importlib
import inspect

def convert_source_to_func(function_source, component_name):
    '''
    Converts source string into function.

    Parameters:
    -----------
    - function_source - function source string
    - component_name - component name that should match function
      name in source code    
    '''
    tmp_dir = tempfile.gettempdir()
    comp_tmp_dir= os.path.join(tmp_dir, 'component_functions')
    
    if not os.path.exists(comp_tmp_dir):
        os.mkdir(comp_tmp_dir)
        open(os.path.join(comp_tmp_dir, '__init__.py'), 'a').close()
    func_filepath = os.path.join(comp_tmp_dir, '%s.py' % component_name)
    with open(func_filepath, 'w') as f:
        f.write(function_source)

    sys.path.append(comp_tmp_dir)
    task_module = importlib.import_module(component_name)
    importlib.reload(task_module)
    return getattr(task_module, component_name)


class ExtraCodeBuilder:
    def __init__(self):
        self._extra_code = ''
        
    def inject_notebook(self, notebook_path):
        with open(notebook_path, 'r') as f:
            self._extra_code += '\nnotebook_source = \'\'\'' + f.read() + '\'\'\'\n\n'
    
    def add_code(self, code):
        '`code` can be `Class` of `function`'
        self._extra_code += '\n' + inspect.getsource(code) + '\n'
        # with open(extra_code, 'r') as f:
        #     self._extra_code += '\n' + f.read() + '\n'
            
    @property
    def get_code(self):
        return self._extra_code
