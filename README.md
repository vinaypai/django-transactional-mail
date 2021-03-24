## Requirements
* `django` >= 2.2

## Quick Start
Install `django-transactional-mail`
```
pip install django-transactional-mail
```
Add `transactional_mail` to `INSTALLED_APPS` in your project's `settings.py`.

```python
INSTALLED_APPS = (
    ...
     'transactional_mail',
    ...
)
```

Run migrations in your project to create the models for the CMS app.

```
./manage.py migrate transactional_mail
```


## Distributing and update

Build an sdist to ensure that the templates are included:

```
python -m build --sdist
```

Publish to pypi

```
python3 -m twine upload dist/*
```
