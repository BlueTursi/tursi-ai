from setuptools import setup, find_packages

setup(
    name="tursi",
    version="0.2.2",
    description="A simple framework to deploy AI models locally with one command, no containers needed",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Kresna Sucandra",
    author_email="kresnasucandra@gmail.com",
    url="https://github.com/BlueTursi/tursi-ai",
    packages=find_packages(),
    install_requires=[
        "transformers",
        "flask",
        "torch>=2.3.2",
        "requests",
        "numpy<2",
        "python-dotenv",
        "cryptography",
        "Flask-Limiter>=3.5.0",
    ],
    entry_points={
        "console_scripts": [
            "tursi-engine = tursi.engine:main",
            "tursi-test = tursi.test:main",
        ],
    },
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)