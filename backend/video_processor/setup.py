from setuptools import find_packages, setup

setup(
    name="video_processor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "google-cloud-storage==2.10.0",
        "google-cloud-aiplatform",
        "vertexai",
        "flask",
        "gunicorn",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-mock",
            "pytest-cov",
        ],
    },
)
