import tempfile

def get_tmp_notebook(source):
    tf = tempfile.NamedTemporaryFile(suffix='.py')
    with open(tf.name, 'w') as f:
        f.write(source)
    return tf