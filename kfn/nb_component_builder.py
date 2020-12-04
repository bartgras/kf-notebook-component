import re
import pkgutil
import kfp.components as comp
from kfn.lib import ExtraCodeBuilder, convert_source_to_func
from kfn.kf_notebook_runner import KFNotebookRunner
from kfn.injected_code import notebook_injected_artifacts, notebook_injected_code, exec_nb

class NbComponentBuilder:
    def __init__(self, op_name, inject_notebook_path=None, remote_notebook_path=None, 
                 remove_nb_inputs=False):
        '''
        Builds Kubeflow component that executes code inside Jupyter Notebook

        Parameters:
        -----------
        - op_name - Component name
        - inject_notebook_path - path to notebook .py file (jupytext format of "Notebook 
          paired with percent script")
        - remote_notebook_path - path to Google/AWS storage from which notebook will be fetched
        - remove_nb_inputs - if True, generated notebook HTML output won't have notebook input cells
        '''
        assert inject_notebook_path or remote_notebook_path, \
            'You need to provide either path to google storage or local filename path ' + \
            'of the notebook that will be injected into component'
        assert not (inject_notebook_path and remote_notebook_path), \
            'Choose either notebook source or path, can\'t do both.'     
            
        self.op_name = re.sub(r'[^a-zA-Z0-9_]+', '', op_name.replace(' ','-').lower())    
        self.input_params = []
        self.output_params = []
        self.input_artifacts = []
        self.output_artifacts = []
        self.inject_notebook_path = inject_notebook_path
        self.remote_notebook_path = remote_notebook_path
        self.remove_nb_inputs = remove_nb_inputs

        self.extra_code_builder = ExtraCodeBuilder()
        imports_source = pkgutil.get_data(__name__, "imports.py")
        injected_code_source = pkgutil.get_data(__name__, "injected_code.py")

        for code in [imports_source.decode(), injected_code_source.decode(), KFNotebookRunner]:
            self.extra_code_builder.add_code(code)

        if self.inject_notebook_path:
            if not self.extra_code_builder:
                self.extra_code_builder = ExtraCodeBuilder()
            self.extra_code_builder.inject_notebook(self.inject_notebook_path)
    
    def add_input_param(self, param_name, param_type, default_value=None): 
        self.input_params.append({
            'param_name': param_name,
            'param_type': param_type,
            'default_value': default_value
        })
        
    def add_output_param(self, param_name, param_type): 
        self.output_params.append({
            'param_name': param_name,
            'param_type': param_type
        })
        
    def add_input_artifact(self, name): 
        self.input_artifacts.append(name)
        
    def add_output_artifact(self, name):
        self.output_artifacts.append(name)        
    
    def build_component_function_source(self):
        def input_param_to_str(p):
            s = '%s: %s' % (p['param_name'], p['param_type'].__name__)
            if p.get('default_value'):
                s += ' = %s' % p['default_value']
            return s        
                    
        func_body = '''
    
    input_params = {input_params}
    output_params = {output_params}
    use_injected_nb_source_code = {inject_code}
    remote_notebook_path = '{remote_notebook_path}'
    ouput_artifacts = [{out_artif}]
    input_artifacts = [{in_artif}]
    remove_nb_inputs = {remove_nb_inputs}
    
    return exec_nb(locals(), input_params, output_params, use_injected_nb_source_code, 
                   remote_notebook_path, ouput_artifacts, input_artifacts, remove_nb_inputs)

'''

        func_body = func_body.format(
            input_params=self._notebook_inputs_params(), 
            output_params=[p['param_name'] for p in self.output_params],
            inject_code=True if self.inject_notebook_path else False, 
            remote_notebook_path=self.remote_notebook_path if self.remote_notebook_path else '',
            out_artif=', '.join(["('{a}', {a})".format(a=a) for a in self.output_artifacts]) 
                      if self.output_artifacts else '',
            in_artif=', '.join(["('{a}', {a})".format(a=a) for a in self.input_artifacts]) 
                      if self.input_artifacts else '',
            remove_nb_inputs='True' if self.remove_nb_inputs else 'False'
        )

        args_str = []
        args_str = ['%s: OutputPath(str)' % p for p in self.output_artifacts]
        args_str += ['%s: InputPath()' % p for p in self.input_artifacts]
        default_sorted_input_params = [i for i in self.input_params if not i.get('default_value')] + \
                                      [i for i in self.input_params if i.get('default_value')]
        args_str += [input_param_to_str(p) for p in default_sorted_input_params]
        args_str = ', '.join(args_str)
        
        # ouput_artifacts don't have to be put here, they are being 
        # outputed by adding OutputPath param on function's input
        tuple_params = ["('%s', %s)" % (p['param_name'], p['param_type'].__name__) for p in self.output_params]
        
        return_str = "NamedTuple('TaskOutput', [('mlpipeline_ui_metadata', 'UI_metadata'), " + \
                     "('mlpipeline_metrics', 'Metrics'), %s])"
        return_str = return_str % ', '.join(tuple_params)
        
        func_source = 'from kfp.components import InputPath, OutputPath\n' 
        func_source += 'from typing import NamedTuple\n\n'
        func_source += f'def {self.op_name}({args_str}) -> {return_str}:\n{func_body}'
        return func_source

    def build_component_function(self):
        '''`kfp` module uses `inspect.getsource()` method which won't work unless 
        function's source code is loaded from a file'''
        function_source = self.build_component_function_source()
        return convert_source_to_func(function_source, self.op_name)
    
    def build_op(self, base_image, packages_to_install=[], *args, **kwargs):
        task_op = comp.func_to_container_op(
            self.build_component_function(), 
            base_image=base_image,
            packages_to_install=packages_to_install,
            extra_code=self.extra_code_builder.get_code,
            *args, **kwargs
        )
        return task_op                     
                     
    def _notebook_inputs_params(self): 
        'Returns inputs list formatted as a string'
        input_names = [i['param_name'] for i in self.input_params] + self.input_artifacts 
        return '[' + ', '.join(["\'%s\'" % n for n in input_names]) + ']'
