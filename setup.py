from setuptools import setup, find_packages

setup(
    name="infoflow",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "mesa>=3.0.0",
        "matplotlib>=3.7.0",
        "numpy>=1.24.0",
        "networkx>=3.1",
        "scipy>=1.10.0",
        "seaborn>=0.12.0",
        "flask>=2.3.0",
        "pandas>=2.0.0",
        "solara>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    author="Shingai Thornton",
    author_email="rthornton@binghamton.edu",
    description="Agent-based model of information flow and truth assessment in social networks",
    keywords="agent-based, truth assessment, networks, social influence, information diffusion",
    python_requires=">=3.11",
)