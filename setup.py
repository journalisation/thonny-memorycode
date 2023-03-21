from setuptools import find_packages, setup

#with open("doc/help.md", "r") as f:
#    long_description = f.read()

setup(
    name="memorycode",
    version="0.0.1",
    author="Jerome Amiguet",
    packages=["thonnycontrib.thonny-memorycode"],
    description="Autosaving",
    long_description="Autosaving",
    long_description_content_type="text/markdown",
    url="https://github.com/epfl-mobots/thonny-memorycode",
    install_requires=[
        "GitPython",
    ],
    package_data={
        "thonnycontrib.thonny-memorycode": [
            "res/*",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Intended Audience :: Education",
    ],
    python_requires=">=3.6",
)