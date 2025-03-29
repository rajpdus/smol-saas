from setuptools import setup, find_packages
import os

# Read requirements
with open('requirements.txt') as f:
    requirements = f.read().splitlines()
    # Filter out comments
    requirements = [req for req in requirements if not req.startswith('#')]

# Read long description from README if it exists
long_description = ''
if os.path.exists('README.md'):
    with open('README.md', 'r') as f:
        long_description = f.read()

setup(
    name="smol-saas",
    version="0.1.0",
    description="A CLI tool for generating AWS serverless SaaS applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Smol AI",
    author_email="info@smol.ai",
    url="https://github.com/YOUR_USERNAME/smol-saas",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    extras_require={
        "auto": ["smol-dev>=0.0.4"],
    },
    entry_points={
        'console_scripts': [
            'smol-saas=smol_saas.main:cli',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
) 