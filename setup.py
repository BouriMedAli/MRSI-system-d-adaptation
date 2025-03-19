from setuptools import setup, find_packages

setup(
    name='recommandation_system',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'uvicorn',
        'pandas',
        'numpy',
        'scikit-learn',
        'pydantic',
        # Ajoute d'autres dépendances si nécessaire
    ],
)
