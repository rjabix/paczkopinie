from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus
from ..models import Reviews, Paczkomats, User, City
from ..utils.PaczkomatCount import PaczkomatCount


class Repository:

    def __init__(self, user: User, db: SQLAlchemy):
        self.user = user
        self.db = db

    # City management
    def add_city(self, name: str) -> City:
        slug = quote_plus(name.lower())
        city = City(name=name, slug=slug)
        self.db.session.add(city)
        self.db.session.commit()
        return city

    def get_city_by_slug(self, slug: str) -> City:
        return City.query.filter_by(slug=slug).first()

    def get_all_cities_with_counts(self) -> list[tuple[City, int]]:
        results = self.db.session.query(
            City,
            self.db.func.count(Paczkomats.code_id).label('paczkomat_count')
        ).outerjoin(Paczkomats).group_by(City.id).all()
        return [(city, count) for city, count in results]

    # Paczkomat management
    def add_paczkomat(self, code_id: str, address: str, city_id: int, additional_info: str = None) -> Paczkomats:
        paczkomat = Paczkomats(
            code_id=code_id,
            address=address,
            city_id=city_id,
            additional_info=additional_info
        )
        self.db.session.add(paczkomat)
        self.db.session.commit()
        return paczkomat

    def get_paczkomats_by_city(self, city_id: int) -> list[tuple[Paczkomats, int]]:
        results = self.db.session.query(
            Paczkomats,
            self.db.func.count(Reviews.id).label('review_count')
        ).outerjoin(
            Reviews, Paczkomats.code_id == Reviews.code_id
        ).filter(
            Paczkomats.city_id == city_id
        ).group_by(
            Paczkomats.code_id
        ).all()

        returnList = []
        for paczkomat, review_count in results:
            returnList.append(PaczkomatCount((paczkomat, review_count)))
        return returnList
        return [(paczkomat, review_count) for paczkomat, review_count in results]

    def get_paczkomat_by_code_id(self, code_id: str) -> Paczkomats | None:
        return Paczkomats.query.filter_by(code_id=code_id).first()

    def get_paczkomats_and_number_of_reviews(self) -> dict[Paczkomats, int]:
        from ..models import Paczkomats
        results = self.db.session.query(
            Paczkomats,
            self.db.func.count(Reviews.id).label('review_count')
        ).outerjoin(Reviews, Paczkomats.code_id == Reviews.code_id
                    ).group_by(Paczkomats.code_id).all()
        return {paczkomat: review_count for paczkomat, review_count in results}

    # Review management
    def add_review(self, review: Reviews):
        self.db.session.add(review)
        self.db.session.commit()

    def get_reviews_by_paczkomat_code_id(self, code_id: str) -> list[Reviews]:
        return Reviews.query.filter_by(code_id=code_id).all()

    def delete_review(self, review_id: str) -> None:
        Reviews.query.filter_by(id=review_id, user_id=self.user.id).delete()
        self.db.session.commit()
