from distutils.core import setup

setup(
    name='Samflow',
    version='0.2',
    packages=['samflow', 'samflow.testsuite'],
    url='https://bitbucket.org/hanfeisun/pyflow',
    license='MIT',
    author='Hanfei Sun',
    author_email='hfsun.tju@gmail.com',
    description='A Python framework for writing flexible workflows',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Programming Language :: Python',
    ],
)
