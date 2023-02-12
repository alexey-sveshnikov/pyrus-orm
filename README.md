pyrus-orm
=========

Radically simple, django/peewee-like, easy and incomplete ORM for [Pyrus](https://pyrus.com).

With pyrus-orm, you can read, create and modify [tasks](https://pyrus.com/en/help/api/models#form-registry-task).

Works with [pyrus-api](https://github.com/simplygoodsoftware/pyrusapi-python) under the hood.

### This is an early development version

### Features:

- Define models with:
    - [x] simple fields (text, number, dates, ...)
    - [x] catalog fields, single item
    - [ ] catalog fields, multiple items
    - [ ] "title" fields
    - [x] multiple choice fields (without nested fields at this moment)
- Operations with models:
    - [x] Create and save
    - [x] Read from registry by ID
    - [x] Modify and save changes
- Filtering:
    - [x] by include_archived and steps fields
    - [x] by value of simple or catalog fields
    - [ ] less than, greater than
    - [ ] value in a list
    - [ ] ranges

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
    time = TimeField(2)
    date = DateField(3)
    number = NumericField(4)
    round_number = IntegerField(5)
    author = CatalogField(6, catalog=<catalog id>)

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

# simple field
book.title
>>> 'Don Quixote'
book.title = 'Don Quixote, Part Two'
book.save('title changed')

# catalog field
book.author
>>> CatalogItem(item_id=..., values={'Name': 'Alonso Fernández de Avellaneda'})  # values comes from the catalog definition

book.author.find_and_set({'Name': 'Miguel de Cervantes'})  # may raise ValueError if no value found
book.save('changed an author to the real one')
```

### Catalog Enum fields

Enums can be mapped to catalog items by ID or by custom property name.

#### Enums mapped to specific catalog items ID

No catalog lookups are preformed on reading or writing of such fields.

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


#### Enums mapped to catalog item properties

(imagine book has a property 'media' with field 'Name')

```python
class Media(Enum):
    paper = 'paper'
    papirus = 'papirus'
    pdf = 'pdf'

class Book(PyrusModel):
    media = CatalogEnumField(<field_id>, catalog_id=<catalog_id>, enum=Genre, id_field='Name')
```

### Filtering

Only basic filtering is supported:

```python

Book.objects.get_filtered(
    title='Don Quixote',
)
>>> [Book(...), ...]


Book.objects.get_filtered(
    genre=Book.genre.find({'Name': 'Fiction'})
)
>>> [Book(...), ...]

Book.objects.get_filtered(
    ...
    include_archived=True,
    steps=[1, 2],
)
>>> [Book(...), ...]
```


### Catalog fields, all the API
```python
# Read values

# Non-empty value
book.author
>>> CatalogItem(item_id=..., values={<your custom values here>})

assert bool(book.author) == True

# Empty value
book.author
>>> CatalogEmptyValue()

assert bool(book.author) == False


# Get all possible values (works for empty fields as well)
book.author.catalog()
>>> [CatalogItem(...), CatalogItem(...), ...]


# Find a value in a catalog
new_author = book.author.catalog().find({'Name': 'Miguel de Cervantes'})
new_author
>>> CatalogItem(item_id=..., values={'Name': 'Miguel de Cervantes'})  # or None

book.author = new_author
book.save()


# Find and set shortcut
book.author.catalog().find_and_set({'Name': 'William Shakespeare'})

book.author.find_and_set({'Name': 'NonExistent'})
>>> ValueError raised


# Set value to a specific item_id
book.author = CatalogItem(item_id=123456)
```