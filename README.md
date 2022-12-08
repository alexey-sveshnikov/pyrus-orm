pyrus-orm
=========

Radically simple, django/peewee-like, easy and **incomplete** ORM for [Pyrus](https://pyrus.com).

With pyrus-orm, you can read, create and modify [tasks](https://pyrus.com/en/help/api/models#form-registry-task).

Works with [pyrus-api](https://github.com/simplygoodsoftware/pyrusapi-python) under the hood.

This is an early development version
------------------------------------

Example
-------

```python

class Book(PyrusModel):
    title = TextField(1)  # 1 is a field ID in pyrus's form
    date = DateField(2)
    author = CatalogField(3, catalog=<catalog id>)

    class Meta:
        form_id = <form_id>

pyrus_api = PyrusAPI(...)
session = PyrusORMSession(pyrus_api)

set_session_global(session)

# create item

book = Book(
    title='Don Quixote',
    date='1605-01-01',
    author=Book.author.find({'Name': 'Alonso Fernández de Avellaneda'})
)

book.save()

book.id
>>> <task_id>

# read and modify item

book = Book.objects.get(id=...)

book.title
>>> 'Don Quixote'

book.author.values['Name']
>>> 'Alonso Fernández de Avellaneda'

book.author.find_and_set({'Name': 'Miguel de Cervantes'})  # may raise ValueError if no value found

book.save()


# explore things

book.author
# CatalogItem(item_id=..., values=<dict with your custom properties>)

book.author.catalog() 
>>> [CatalogItem(...), CatalogItem(...), ...]

book.author.catalog().find({'Name': 'William Shakespeare'})
>>> CatalogItem(...)

book.author.catalog().find({'Name': 'NonExistent'})
>>> ValueError raised
```
