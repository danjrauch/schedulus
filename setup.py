import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="schedulus",
    version="0.0.1",
    author="Dan Rauch & Nicholas Velcich",
    author_email="drauch@hawk.iit.edu & nvelcich@hawk.iit.edu",
    description="HPC Scheduling Simulator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject", # Change
    packages=setuptools.find_packages(),
    install_requires=[
        'Click',
        'numpy',
        'ttictoc',
        'simulus'
    ],
    entry_points='''
        [console_scripts]
        schedulus=src.main:cli
    ''',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)