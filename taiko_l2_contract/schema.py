from peewee import MySQLDatabase
from peewee import Model, BigIntegerField, CharField, SmallIntegerField, BlobField, DecimalField

class MediumBlogField(BlobField):
    field_type = 'MEDIUMBLOB'

# Connect to a MySQL database on network.
mysql_db = MySQLDatabase(
    database = 'taiko_data',
    user='aaaaaaa',
    password='bbbbbb',
    host='127.0.0.1', port=3306
)

class BaseModel(Model):
    class Meta:
        database = mysql_db
        legacy_table_names = False


class L2ContractInfo(BaseModel):
    address                 = CharField(index=True)
    name                    = CharField(index=True)
    is_proxy                = CharField(index=True)
    implementation_name     = CharField(index=True)
    implementation_address  = CharField(index=True)


# Connect to our database.
mysql_db.connect()

# Create the tables if not exist.
mysql_db.create_tables([
    L2ContractInfo
])