import unittest
import os
import re

from kfn.kf_notebook_runner import KFNotebookRunner
from kfn.test.notebooks_source import notebook_source, invalid_notebook_source
from kfn.test.lib import get_tmp_notebook

try:
    kernel = os.environ['NOTEBOOK_KERNEL_NAME']
except:
    raise Exception('Set environment variable that points to your ' + \
                    'Jupyter kernel that will execute the notebook. ' + \
                    'Example: NOTEBOOK_KERNEL_NAME=<kernel_name>')

class KFNotebookRunnerTestCase(unittest.TestCase):
    def test_executes_without_params(self):
        nb_file = get_tmp_notebook(notebook_source)
        runner = KFNotebookRunner(nb_file.name, kernel_name=kernel)
        runner.run()
        
        self.assertTrue(runner.notebook_html_output)
        self.assertEqual(runner.outputs, {'a': 11})
        self.assertEqual(runner.metrics, {'accuracy': 1})

        nb_pref = re.sub('.py$', '', nb_file.name)
        self.assertTrue(os.path.exists(nb_pref + '_inject_output.ipynb'))
        self.assertTrue(os.path.exists(nb_pref + '_inject_output_out.ipynb'))
        nb_file.close()

    def test_injectind_and_overwriting_inputs(self):
        nb_file = get_tmp_notebook(notebook_source)
        runner = KFNotebookRunner(nb_file.name, inject_params={'a': 1}, kernel_name=kernel)
        runner.run()

        self.assertEqual(runner.outputs['a'], 1)
        nb_file.close()

    def test_enabled_notebook_inputs(self):
        nb_file = get_tmp_notebook(notebook_source)
        runner = KFNotebookRunner(nb_file.name, kernel_name=kernel)
        runner.run()

        self.assertRegex(runner.notebook_html_output, r'.*TEST-COMMENT.*')  
        nb_file.close()      

    def test_disabled_notebook_inputs(self):
        nb_file = get_tmp_notebook(notebook_source)
        runner = KFNotebookRunner(nb_file.name, kernel_name=kernel, remove_nb_inputs=True)
        runner.run()

        self.assertNotRegex(runner.notebook_html_output, r'.*TEST-COMMENT.*')    
        nb_file.close()            

    def test_failing_without_parameters_tag(self):
        nb_file = get_tmp_notebook(invalid_notebook_source)
        runner = KFNotebookRunner(nb_file.name, kernel_name=kernel)

        with self.assertRaises(Exception):
            runner.run()
        nb_file.close()
        