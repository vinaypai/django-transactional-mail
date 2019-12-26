import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='django-transactional-mail',
    version='0.1.3',
    author='Vinay Pai',
    author_email='vinay@vinaypai.com',
    description='Transactional emails in Django projects made easy',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/vinaypai/django-transactional-mail/',
    packages=['cms'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Content Management System',
    ],
    install_requires=[
        'django >= 1.11',
    ]
)
