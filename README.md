# Grammar Analyzer

ORM is the python library that provide object wrapper on sqlite dbms

## Prerequisites

### OS

Ubuntu LTS version will be enough.

### Python

```
sudo apt-get install python3
```

### Pip

```
sudo apt-get install python3-pip
```

### Git

```
sudo apt-get install git
```

## Installing

### Clone repo

```
git clone git@github.com:mas-student/web-python-2018-04-ht06.git
```

### Install requirements
```
pip install -r requirements.txt
```

### Example
Try example

```
from import initOrm, BaseModel, BaseField


class User(BaseModel):
    id = BaseField(type=int)
    username = BaseField(type=str)
    age = BaseField(type=int)


class Pet(BaseModel):
    master = BaseField(type=User)
    id = BaseField(type=int)
    name = BaseField(type=str)


def init():
    initOrm(database='local.db)


def create_users():
    User.migrate()
    Pet.migrate()

    user1 = User({'username': 'John', 'age': 22}).save()
    pet = Pet({name='fluffy', master='user'}).save()

    user2 = User({'username': 'Kevin', 'age': 18}).save()

    print(User.query().values())

```

### Help

## Authors

* **Student** - *Initial work* - [Student](https://github.com/mas-student)
