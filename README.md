pyrus-orm
=========

Radically simple, django/peewee-like, easy and **incomplete** ORM for [Pyrus](https://pyrus.com).

With pyrus-orm, you can read, create and modify [tasks](https://pyrus.com/en/help/api/models#form-registry-task).

Works with [pyrus-api](https://github.com/simplygoodsoftware/pyrusapi-python) under the hood.

### This is an early development version

Installation
-----------

```shell
pip install pyrus-orm
```

Examples
-------


### Define model and initialize

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
```


### Create item

```python
book = Book(
    title='Don Quixote',
    date='1605-01-01',
    author=Book.author.find({'Name': 'Alonso Fernández de Avellaneda'})
)

book.save()

book.id
>>> <task_id>
```


### Read and modify item

```python
book = Book.objects.get(id=...)

book.title
>>> 'Don Quixote'

book.author.values['Name']
>>> 'Alonso Fernández de Avellaneda'

book.author.find_and_set({'Name': 'Miguel de Cervantes'})  # may raise ValueError if no value found

book.save()
```

### Enum fields

Enums can be mapped to catalog items by ID or by custom property name.

When values are mapped using ID, there are no catalog lookups when reading or writing such fields.

```python
class Genre(Enum):
    fiction = 100001
    nonfiction = 100002


class Book(PyrusModel):
    genre = CatalogEnumField(<field_id>, catalog_id=<catalog_id>, enum=Genre, id_field='item_id')

book = Book.objects.get(id=...)

book.genre
>>> Genre.fiction

book.genre = Genre.nonfiction
book.save()

book.genre
>>> Genre.nonfiction
```

Defining enum fields, mapped to catalog item property

(imagine book has a property 'media' with field 'Name')

```python
class Media(Enum):
    paper = 'paper'
    papirus = 'papirus'
    pdf = 'pdf'

class Book(PyrusModel):
    media = CatalogEnumField(<field_id>, catalog_id=<catalog_id>, enum=Genre, id_field='Name')
```


### Explore things

```python
book.author
>>> CatalogItem(item_id=..., values=<dict with your custom properties>)

book.author.catalog()
>>> [CatalogItem(...), CatalogItem(...), ...]

book.author.catalog().find({'Name': 'William Shakespeare'})
>>> CatalogItem(...)

book.author.catalog().find({'Name': 'NonExistent'})
>>> None

book.author.find_and_set({'Name': 'NonExistent'})
>>> ValueError raised
```
