from setuptools import setup

setup(name='sgit',
      version='1.0',
      description='Simple git',
      author='Piotr Skoroszewski',
      packages=['simple_git'],
      entry_points={'console_scripts': ['sgit = simple_git.simple_git:main', ], },
      )
