#from kfn.kf_notebook_runner import KFNotebookRunner

notebook_injected_artifacts = '''

import pickle

if '_input_artifacts' in locals():
    exec('_in_artifacts = %s' % _input_artifacts)
    for artif in _in_artifacts:
        with open(artif[1], 'rb') as f:
            try:
                exec('%s = pickle.loads(f.read())' % artif[0] )
            except pickle.UnpicklingError:
                with open(artif[1], 'r') as f:
                    exec('%s = f.read()' % artif[0] )

'''

notebook_injected_code = '''

# %%
import pickle

if 'outputs' in locals() and type(outputs) == dict:
    with open('/tmp/outputs.pickle', 'wb') as f:
        f.write(pickle.dumps(outputs))

if '_output_artifacts' in locals():
    exec('_artifacts = %s' % _output_artifacts)
    for artif in _artifacts:
        with open(artif[1], 'wb') as f:
            f.write(pickle.dumps(artifacts[artif[0]]))

if 'metrics' in locals() and type(metrics) == dict:
    with open('/tmp/metrics.pickle', 'wb') as f:
        f.write(pickle.dumps(metrics))    

'''

def exec_nb(_locals, input_params, output_params, use_injected_nb_source_code=False, remote_notebook_path=None, 
            output_artifacts=None, input_artifacts=None, remove_nb_inputs=False):
    import json
    import pickle
    import random
    import string
    from collections import namedtuple

    random_filename = ''.join(random.choice(string.ascii_lowercase) 
                              for i in range(8))
    tmp_notebook = '/tmp/%s.py' % random_filename
    
    params_dict = {}
    for param_name in input_params:
        params_dict[param_name] = _locals[param_name]
    
    if output_artifacts:
        params_dict.update({'_output_artifacts': str(output_artifacts)})
    
    if input_artifacts:
        params_dict.update({'_input_artifacts': str(input_artifacts)})
    
    if use_injected_nb_source_code:        
        with open(tmp_notebook, 'w') as f:
            # Note: Variable `notebook_source` is being injected earlier
            f.write(notebook_source)
    
    if remote_notebook_path:
        # TODO: Download from GS and save to /tmp/notebook.py
        raise('Not implemented')
        
    nr = KFNotebookRunner(
        local_py_name=tmp_notebook, 
        inject_params=params_dict,
        remove_nb_inputs=remove_nb_inputs) 
    nr.run()
    
    metadata = {
        'outputs' : [{
          'type': 'web-app',
          'storage': 'inline',
          'source': nr.notebook_html_output
        }]
    }
    
    metrics_list = []
    
    if nr.metrics:
        if type(nr.metrics) != dict:
            raise(TypeError('Invalid metrics format. Passed values are: %s' % nr.metrics))

        for mk, mv in nr.metrics.items():
            try:
                float(mv)
            except:
                TypeError('Invalid metric: {%s:%s}' % (mk,mv))

            metrics_list.append({
                'name': mk, 
                'numberValue':  mv, 
                'format': "RAW",   
            })
    metrics = {'metrics': metrics_list}
    
    tuple_outputs = [json.dumps(metadata), json.dumps(metrics)] + [nr.outputs[p] for p in output_params]
    
    tuple_inputs = ['mlpipeline_ui_metadata', 'mlpipeline_metrics']
    if output_params:
        tuple_inputs += output_params
    
    task_out = namedtuple('TaskOutput', tuple_inputs)
    return task_out(*tuple_outputs)