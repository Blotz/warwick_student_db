from setuptools import setup

setup(
    name='warwick_student_db',
    version='0.1.0',    
    description='Python script to download student data from the Warwick Student Database',
    url='https://github.com/blotz/warwick_student_db',
    author='Ferdinand Theil',
    author_email='f.p.theil@gmail.com',
    license='MIT',
    packages=['warwick_student_db'],
    install_requires=['requests',
                        'bs4',
                        'xlsxwriter',
                        ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    zip_safe=False,
)
