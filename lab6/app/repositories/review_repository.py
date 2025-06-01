from app.models import Review
from app.models import Course

class ReviewRepository:
    def __init__(self, db):
        self.db = db

    def get_latest_reviews_by_course(self, course_id, limit=5):
        query = (self.db.session.query(Review)
                 .filter(Review.course_id == course_id)
                 .order_by(Review.created_at.desc())
                 .limit(limit))
        return query.all()
    
    def get_reviews_by_course(self, course_id, sort='newest', page=1, per_page=10):
        query = self.db.session.query(Review).filter(Review.course_id == course_id)

        if sort == 'positive':
            query = query.order_by(Review.rating.desc(), Review.created_at.desc())
        elif sort == 'negative':
            query = query.order_by(Review.rating.asc(), Review.created_at.desc())
        else:
            query = query.order_by(Review.created_at.desc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return pagination
    
    def get_review_by_user_and_course(self, user_id, course_id):
        return self.db.session.query(Review).filter_by(user_id=user_id, course_id=course_id).first()
    
    def add_or_update_review(self, user_id, course_id, rating, text):
        review = self.get_review_by_user_and_course(user_id, course_id)
        if review:
            review.rating = rating
            review.text = text
        else:
            review = Review(user_id=user_id, course_id=course_id, rating=rating, text=text)
            self.db.session.add(review)
        self.db.session.commit()
        return review

    def recalc_course_rating(self, course_id):
        course = self.db.session.get(Course, course_id)
        reviews = self.db.session.query(Review).filter_by(course_id=course_id).all()
        course.rating_num = len(reviews)
        course.rating_sum = sum(r.rating for r in reviews)
        self.db.session.commit()