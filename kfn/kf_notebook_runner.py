# TODO: FIX @@@@@@@@@@@@@@
# Note: Imports moved inside class to make it easier to inject 
# source code into Kubeflow component
# import os
# import re
# import pickle
# from jupytext.cli import jupytext
# import papermill
# from nbconvert import HTMLExporter
# from traitlets.config import Config
# from collections import namedtuple
# import json

from kfn.imports import os, re, pickle, jupytext, papermill, HTMLExporter, Config, namedtuple, json
from kfn.injected_code import notebook_injected_artifacts, notebook_injected_code

class KFNotebookRunner:
    def __init__(self, local_py_name, inject_params={}, remove_nb_inputs=False, kernel_name='python3'):
        """
        Converts (jupytext format of "Notebook paired with percent script")).py file to .ipynb, executes 
        it and generates separate output in HTML format. All converted/generated files will be written to 
        the same directory as input py file.

        Parameters:
        -----------
        - local_py_name: Path to py file that will be used for run.

        - inject_params: Parameters that will be injected to notebook. Follow papermill
          (https://papermill.readthedocs.io/en/latest/usage-parameterize.html) 
          documentation how to do that.

        - remove_nb_inputs: By default HTML output will contain both code and 
          output cells. Setting `remote_nb_inputs` to True will remove code cells.
        """

        py_filename = os.path.split(local_py_name)[-1]
        path = os.path.split(local_py_name)[0]
        self.path_prefix = path + '/' + py_filename.split('.py')[0]
        self.inject_params = inject_params
        self.remove_nb_inputs = remove_nb_inputs
        self.kernel_name = kernel_name

        self._notebook_html_output = ''
        self._outputs = {}
        self._metrics = {}
        self._component_return_stuct = None

    def run(self):
        self.inject_saving_outputs()
        self.convert_and_run_in_notebook()
        self.nb_html_convert()            
        self.build_component_output()
        self.build_component_metrics()

    def inject_saving_outputs(self):
        with open(self.path_prefix + '.py', 'r') as f_in:
            with open(self.path_prefix + '_inject_output.py', 'w') as f_out:
                file_content = f_in.read()
                if len(re.findall('tags=\["parameters"', file_content)) == 0:
                    raise(Exception('Notebook is missing "parameters" tag set on one of it\'s cells'))
                file_content = re.sub(r'# %% tags=\["parameters"(.*)\](.+?)# %%', 
                                      r'# %% tags=["parameters"\1]\2\n# %%\n{code}\n\n# %%'.format(
                                          code=notebook_injected_artifacts), 
                                      file_content, 
                                      flags=re.S)
                f_out.write(file_content)
                f_out.write(notebook_injected_code)

    def convert_and_run_in_notebook(self):
        jupytext([self.path_prefix + '_inject_output.py', '--to', 'ipynb'])
        
        papermill.execute_notebook(
            '%s_inject_output.ipynb' % self.path_prefix, 
            '%s_inject_output_out.ipynb' % self.path_prefix, 
            parameters=self.inject_params,
            kernel_name=self.kernel_name
        )
        
    def nb_html_convert(self):
        c = Config()
        if self.remove_nb_inputs:
            c.HTMLExporter.exclude_input_prompt = True
            c.HTMLExporter.exclude_input = True
            c.HTMLExporter.exclude_output_prompt = True

        htmlExporter = HTMLExporter(config=c)
        htmlExporter.template_name = 'classic'
        body, _ = htmlExporter.from_filename("%s_inject_output_out.ipynb" % self.path_prefix)

        self._notebook_html_output = body

    def build_component_output(self):
        fname = '/tmp/outputs.pickle'
        if os.path.exists(fname):
            with open(fname, 'rb') as f:
                self._outputs = pickle.loads(f.read())      
    
    def build_component_metrics(self):
        fname = '/tmp/metrics.pickle'
        if os.path.exists(fname):
            with open(fname, 'rb') as f:
                self._metrics = pickle.loads(f.read())    

    @property
    def outputs(self):
        return self._outputs
    
    @property
    def metrics(self):
        return self._metrics

    @property
    def notebook_html_output(self):
        return self._notebook_html_output
