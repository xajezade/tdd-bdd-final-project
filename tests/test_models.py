# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db
from service import app
from tests.factories import ProductFactory
from service.models import DataValidationError

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_read_a_product(self):
        """It should read a product"""
        product = ProductFactory()
        # Create a producte
        product.id = None
        product.create()        
        self.assertIsNotNone(product.id)
        # Test reading from fetching from the system 
        found_product = Product.find(product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(Decimal(found_product.price), product.price)
        self.assertEqual(found_product.id, product.id)
    def test_update_a_product(self):
        """It should Update a Product"""
        product = ProductFactory()
        # Create a product
        product.id = None
        product.create()
        # Log the product object after creation
        self.assertEqual(str(product), f"<Product {product.name} id=[{product.id}]>")
        # check if an id is assigned
        self.assertIsNotNone(product.id)
        # Update the product description
        product_id = product.id #storing the original id
        product_desc = "Updated Description for Test"
        product.description = product_desc 
        product.update()
        # Check if the product description is updated with the same id
        self.assertEqual(product.id, product_id)
        self.assertEqual(product.description, product_desc)
        # Check if the created product is the only created product
        products = Product.all()
        self.assertEqual(len(products), 1)
        found_product = products[0]
        self.assertEqual(product.id, found_product.id)   
        self.assertEqual(product.description, found_product.description)
    def test_update_a_product_with_empty_ID(self):
        """It should raise an error if ID is None"""
        product = ProductFactory()
        # Create a product
        product.id = None
        product.create()
        product.id = None
        self.assertRaises(DataValidationError,product.update)

    def test_delete_a_product(self):
        """It should Delete a Product"""
        product = ProductFactory()
        # Create a product
        # Create a product
        product.id = None
        product.create()
        # check if an id is assigned
        self.assertIsNotNone(product.id)
        # Check if it is the only product
        products = Product.all()
        self.assertEqual(len(products), 1)        
        # check if deleting make the length to zero
        product.delete()
        products = Product.all()
        self.assertEqual(len(products), 0)
    def test_list_all_products(self):
        """It should list all the products in the database"""
        products = Product.all()
        # check if it is empty
        self.assertEqual(len(products), 0)
        # create 5 products
        for _ in range(5):
            product = ProductFactory()
            product.id = None
            product.create()
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_by_name(self):
        """It should Find a Product by Name"""
        products = ProductFactory.create_batch(5)
        # create and save products in the database.
        for product in products:
            product.id = None
            product.create()
        first_product = products[0]
        name = first_product.name
        count = len([x for x in products if x.name == name])
        found_products = Product.find_by_name(name)
        # check if the count of the found products matches
        self.assertEqual(count, found_products.count())
        # check if the names matches
        for item in found_products:
            self.assertEqual(name, item.name)

    def test_find_by_availability(self):
        """It should Find a Product by Availability"""
        products = ProductFactory.create_batch(10)
        # create and save products in the database.
        for product in products:
            product.id = None
            product.create()
        first_product = products[0]
        avail = first_product.available
        count = len([x for x in products if x.available == avail])
        found_products = Product.find_by_availability(avail)
        # check if the count of the found products matches
        self.assertEqual(count, found_products.count())
        # check if the names matches
        for item in found_products:
            self.assertEqual(avail, item.available)

    def test_find_by_category(self):
        """It should Find a Product by category"""
        products = ProductFactory.create_batch(10)
        # create and save products in the database.
        for product in products:
            product.id = None
            product.create()
        first_product = products[0]
        cat = first_product.category
        count = len([x for x in products if x.category == cat])
        found_products = Product.find_by_category(cat)
        # check if the count of the found products matches
        self.assertEqual(count, found_products.count())
        # check if the names matches
        for item in found_products:
            self.assertEqual(cat, item.category)

    def test_serialize(self):
        """ Test if seriallization of database work"""
        product = ProductFactory()
        # Create a product
        # Create a product
        product.id = None
        product.create()
        # check if an id is assigned
        self.assertIsNotNone(product.id)
        data = product.serialize()
        self.assertEqual(data["id"], product.id)
        self.assertEqual(data["name"], product.name)
        self.assertEqual(data["description"], product.description)
        self.assertEqual(data["available"], product.available)
        self.assertEqual(data["category"], product.category.name)
                