import unittest
import tempfile

from kfn.nb_component_builder import NbComponentBuilder
from kfn.test.notebooks_source import notebook_source, invalid_notebook_source
from kfn.test.lib import get_tmp_notebook
from kfp.components import InputPath, OutputPath

class NbComponentBuilderTestCase(unittest.TestCase):
    def test_injecting_notebook_code(self):
        nb_file = get_tmp_notebook('NOTEBOOK SOURCE CODE')
        builder = NbComponentBuilder('op1', inject_notebook_path=nb_file.name)
        self.assertTrue('NOTEBOOK SOURCE CODE' in builder.extra_code_builder.get_code)
        
    def test_build_plain_function(self):
        nb_file = get_tmp_notebook(notebook_source)

        builder = NbComponentBuilder('op1', inject_notebook_path=nb_file.name)
        func_source = builder.build_component_function_source()
        annotation = "def op1() -> NamedTuple('TaskOutput', [('mlpipeline_ui_metadata', 'UI_metadata'), ('mlpipeline_metrics', 'Metrics'), ]):"
        self.assertTrue(annotation in func_source)

    def test_raise_notebook_not_found(self):
        with self.assertRaises(FileNotFoundError):
            NbComponentBuilder('op1', inject_notebook_path='/wrong/filename/path.py')

    def test_build_function(self):
        nb_file = get_tmp_notebook(notebook_source)
        builder = NbComponentBuilder('op1', inject_notebook_path=nb_file.name)
        x = builder.build_component_function()
        self.assertEquals(x.__name__, 'op1')

    def test_build_function_with_input_output_params(self):
        nb_file = get_tmp_notebook(notebook_source)
        builder = NbComponentBuilder('op1', inject_notebook_path=nb_file.name)
        builder.add_input_param('a', int, default_value=1)
        builder.add_output_param('x', float)
        func = builder.build_component_function()
        self.assertEqual(func.__annotations__['a'], int)
        self.assertEqual(list(func.__annotations__['return'].__annotations__.keys()),
                         ['mlpipeline_ui_metadata', 'mlpipeline_metrics', 'x'])
        self.assertEqual(func.__annotations__['return'].__annotations__['x'], float)             

    def test_build_function_with_input_output_artifacts(self):
        nb_file = get_tmp_notebook(notebook_source)
        builder = NbComponentBuilder('op1', inject_notebook_path=nb_file.name)
        builder.add_input_artifact('a_in')
        builder.add_output_artifact('a_out')
        func = builder.build_component_function()
        self.assertEqual(type(func.__annotations__['a_in']), type(InputPath()))
        self.assertEqual(type(func.__annotations__['a_out']), type(OutputPath()))
