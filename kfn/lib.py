import sys
import os
import tempfile
import importlib
import inspect
from jupytext.cli import jupytext
from jupytext.paired_paths import InconsistentPath

def convert_source_to_func(function_source, component_name):
    '''
    Converts source string into function by writing it to 
    disk, loading as module and getting funciton from that module.

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
        if not os.path.exists(notebook_path):
            raise FileNotFoundError('Incorrect notebook path: %s' % notebook_path)

        with open(notebook_path, 'r') as f:
            self._extra_code += '\nnotebook_source = \'\'\'' + f.read() + '\'\'\'\n\n'
    
    def add_code(self, code):
        '`code` can be `str`, `Class` or `function`'
        if type(code) == str:
            self._extra_code += '\n' + code + '\n'
        else:
            self._extra_code += '\n' + inspect.getsource(code) + '\n'     
            
    @property
    def get_code(self):
        return self._extra_code
