from flask_sqlalchemy import SQLAlchemy
from ..models import Reviews, Paczkomats, User


class Repository:

    def __init__(self, user: User, db: SQLAlchemy):
        self.user = user
        self.db = db

    def add_review(self, review: Reviews):
        self.db.session.add(review)
        self.db.session.commit()


    def get_reviews_by_paczkomat_code_id(self, code_id: str) -> list[Reviews]:
        return Reviews.query.filter_by(code_id=code_id).all()

    def get_paczkomats_and_number_of_reviews(self) -> dict[str, int]:
        from ..models import Paczkomats
        results = self.db.session.query(
            Paczkomats,
            self.db.func.count(Reviews.id).label('review_count')
        ).outerjoin(Reviews, Paczkomats.code_id == Reviews.code_id
                    ).group_by(Paczkomats.code_id).all()
        return {paczkomat.code_id: review_count for paczkomat, review_count in results}


    def delete_review(self, review_id: str) -> None:
        Reviews.query.filter_by(id=review_id, user_id=self.user.id).delete()
        self.db.session.commit()
