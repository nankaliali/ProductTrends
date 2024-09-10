from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    Float,
    ForeignKey,
    VARBINARY,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.exc import IntegrityError

Base = declarative_base()


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)

    products = relationship("Product", back_populates="organization")

    def __repr__(self):
        return f"Organization(id={self.id}, name={self.name})"


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    parent = relationship("Category", remote_side=[id], backref="children")
    products = relationship("Product", back_populates="category")

    def __repr__(self):
        return f"Category(id={self.id}, name={self.name}, parent_id={self.parent_id})"


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(Text, nullable=False)
    path = Column(String(255), nullable=False)

    products = relationship("Product", back_populates="image")

    def __repr__(self):
        return f"Image(id={self.id}, url={self.url}, path={self.path})"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    url = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text)
    image_id = Column(Integer, ForeignKey("images.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))

    category = relationship("Category", back_populates="products")
    image = relationship("Image", back_populates="products")
    organization = relationship("Organization", back_populates="products")

    def __repr__(self):
        return f"Product(id={self.id}, title={self.title}, url={self.url}, category_id={self.category_id}, price={self.price}, description={self.description}, image_id={self.image_id}, organization_id={self.organization_id})"


class SQLServerManager:
    def __init__(self, server, database, username, password):
        connection_string = (
            f"mssql+pyodbc://{username}:{password}@{server}/{database}?"
            "driver=ODBC+Driver+17+for+SQL+Server"
        )
        # delete all tables
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)
        # Base.metadata.drop_all(self.engine)

        Base.metadata.create_all(self.engine)
        print("All tables created successfully.")

    def get_session(self):
        return self.Session()

    def add_organization(self, name, session=None):
        if session is None:
            session = self.get_session()

        existing_organization = session.query(Organization).filter_by(name=name).first()
        if existing_organization:
            print(f"Organization '{name}' already exists.")
            return existing_organization.id

        organization = Organization(name=name)
        session.add(organization)
        try:
            session.commit()
            print(f"Organization '{name}' added successfully.")
            return organization.id
        except IntegrityError as e:
            session.rollback()
            print(f"Error: Could not add organization '{name}'. Details: {e}")
            return None

    def add_category(self, name, parent_id=None, session=None):
        if session is None:
            session = self.get_session()
        category = Category(name=name, parent_id=parent_id)
        session.add(category)
        try:
            session.commit()
            print(f"Category '{name}' added successfully.")
        except IntegrityError as e:
            session.rollback()
            print(f"Error: Category '{name}' already exists or invalid parent ID.")

    def get_category_by_name(self, name, session):
        return session.query(Category).filter_by(name=name).first()

    def get_or_create_category(self, name, parent_id=None, session=None):
        if session is None:
            session = self.get_session()
        category = self.get_category_by_name(name, session)
        if category is None:
            category = Category(name=name, parent_id=parent_id)
            session.add(category)
            try:
                session.commit()
                print(f"Category '{name}' added successfully.")
            except IntegrityError as e:
                session.rollback()
                print(f"Error: Could not add category '{name}'. Details: {e}")
                category = self.get_category_by_name(name, session)
        return category

    def add_hierarchical_category(self, category_path, session):
        parent_id = None
        for category_name in category_path:
            category = self.get_or_create_category(category_name, parent_id, session)
            parent_id = category.id

    def add_image(self, url, path, session=None):
        if session is None:
            session = self.get_session()
        image = Image(url=url, path=path)
        session.add(image)
        try:
            session.commit()
            print(f"Image added successfully.")
            return image.id
        except IntegrityError as e:
            session.rollback()
            print(f"Error: Could not add image. Details: {e}")
            return None

    def add_product(
        self,
        title,
        url,
        category_id,
        price,
        description,
        image_id,
        organization_id,
        session=None,
    ):
        if session is None:
            session = self.get_session()
        product = Product(
            title=title,
            url=url,
            category_id=category_id,
            price=price,
            description=description,
            image_id=image_id,
            organization_id=organization_id,
        )
        session.add(product)
        try:
            session.commit()
            print(f"Product '{title}' added successfully.")
        except IntegrityError as e:
            session.rollback()
            print(f"Error: Could not add product '{title}'. Details: {e}")

    def get_images(self, session=None):
        if session is None:
            session = self.get_session()
        images = session.query(Image).all()
        session.close()
        return images

    def delete_all_tables(self):
        Base.metadata.drop_all(self.engine)
        print("All tables deleted successfully.")
