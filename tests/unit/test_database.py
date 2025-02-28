from unittest import TestCase

from flask_alchemydumps.database import AlchemyDumpsDatabase

from ..integration.app import Post, SomeControl, User, app, db


class TestSQLAlchemyHelper(TestCase):
    def setUp(self):
        self.db = db
        self.db.create_all()

    def tearDown(self):
        self.db.drop_all()
        db_file = app.extensions["alchemydumps"].basedir / "test.db"
        if db_file.exists():
            db_file.unlink()

    def test_mapped_classes(self):
        with app.app_context():
            alchemy = AlchemyDumpsDatabase()
            classes = alchemy.get_mapped_classes()
            self.assertIn(User, classes)
            self.assertIn(Post, classes)
            self.assertIn(SomeControl, classes)
            self.assertEqual(len(classes), 4)

    def test_get_and_parse_data(self):
        with app.app_context():
            # control data
            user = User(email="me@example.etc")
            post1 = Post(title="Post 1", content="Lorem...", author_id=1)
            post2 = Post(title="Post 2", content="Ipsum...", author_id=1)
            control = SomeControl(uuid="1")

            # feed user table
            self.db.session.add(user)
            self.db.session.commit()

            # feed post table
            self.db.session.add(post1)
            self.db.session.add(post2)
            self.db.session.commit()

            # feed some control table
            self.db.session.add(control)
            self.db.session.commit()

            # get data
            alchemy = AlchemyDumpsDatabase()
            data = alchemy.get_data()

            # parse data
            parsed_user = alchemy.parse_data(data["User"])
            parsed_posts = alchemy.parse_data(data["Post"])
            parsed_control = alchemy.parse_data(data["SomeControl"])

            # assert length
            self.assertEqual(len(parsed_user), 1)
            self.assertEqual(len(parsed_posts), 2)
            self.assertEqual(len(parsed_control), 1)

            # assert values
            self.assertEqual(user.email, parsed_user[0].email)
            self.assertEqual(post1.title, parsed_posts[0].title)
            self.assertEqual(post2.content, parsed_posts[1].content)
            self.assertTrue(parsed_posts[0].created_on)
            self.assertTrue(parsed_posts[0].updated_on)
            self.assertTrue(parsed_posts[1].created_on)
            self.assertTrue(parsed_posts[1].updated_on)
            self.assertEqual(control.uuid, parsed_control[0].uuid)
