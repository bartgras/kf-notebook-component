from setuptools import setup

setup(name='kfn',
      version='0.1',
      description='Kubeflow notebook component builder',
      url='https://github.com/bartgras/kf-notebook-component',
      author='Bart Grasza',
      author_email='bartgras@protonmail.com',
      license='MIT',
      packages=['kfn', 'kfn.test'],
      install_requires=[
          'kfp',
          'papermill',
          'jupytext',
          'nbconvert'
      ],
      zip_safe=False)