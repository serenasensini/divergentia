from setuptools import setup, find_packages

setup(
    name='divergentia-api',
    version='1.0.0',
    description='Flask API for document processing with AI-powered features',
    author='Your Name',
    packages=find_packages(),
    python_requires='>=3.9',
    install_requires=[
        'Flask>=3.0.2',
        'Flask-CORS>=4.0.0',
        'Flask-RESTful>=0.3.10',
        'python-dotenv>=1.0.1',
        'python-docx>=1.1.0',
        'PyPDF2>=3.0.1',
        'pdfplumber>=0.11.0',
        'PyMuPDF>=1.23.26',
        'reportlab>=4.1.0',
        'ollama>=0.1.6',
        'requests>=2.31.0',
        'pydantic>=2.6.1',
        'marshmallow>=3.20.2',
        'Flask-Limiter>=3.5.0',
        'Flask-Caching>=2.1.0',
        'gunicorn>=21.2.0',
        'python-magic-bin>=0.4.14',
    ],
    extras_require={
        'dev': [
            'pytest>=8.0.0',
            'pytest-cov>=4.1.0',
            'pytest-mock>=3.12.0',
            'pytest-flask>=1.3.0',
            'black>=24.2.0',
            'flake8>=7.0.0',
            'pylint>=3.0.3',
            'mypy>=1.8.0',
            'pre-commit>=3.6.0',
        ]
    },
)
