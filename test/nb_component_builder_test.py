import unittest
import inspect
import tempfile

from nb_component_builder import NbComponentBuilder
from notebooks_source import notebook_source, invalid_notebook_source

def get_tmp_notebook(source):
    tf = tempfile.NamedTemporaryFile(suffix='.py')
    with open(tf.name, 'w') as f:
        f.write(source)
    return tf


class NbComponentBuilderTestCase(unittest.TestCase):
    def test_build_plain_function(self):
        nb_file = get_tmp_notebook(notebook_source)

        builder = NbComponentBuilder('op1', inject_notebook_path=nb_file.name)
        func = builder.build_component_function()
        
