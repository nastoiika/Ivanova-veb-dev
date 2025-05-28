# import time
# import pytest
# from app.repositories.visit_log_repository import VisitLogRepository

# def test_add_and_get_all(visit_log_repository, existing_user):
#     visit_log_repository.add('/test/page', user_id=existing_user['id'])
#     visits = visit_log_repository.all()
#     assert any(v['path'] == '/test/page' and v['user_id'] == existing_user['id'] for v in visits)


# def test_all_returns_desc_order(visit_log_repository):
#     visit_log_repository.add('/page/1')
#     time.sleep(1)
#     visit_log_repository.add('/page/2')

#     visits = visit_log_repository.all()
#     assert visits[0]['created_at'] >= visits[1]['created_at']

# def test_get_by_user_id_returns_only_user_logs(visit_log_repository, existing_user):
#     visit_log_repository.add('/user/page', user_id=existing_user['id'])
#     visit_log_repository.add('/anonymous/page')

#     user_visits = visit_log_repository.get_by_user_id(existing_user['id'])
#     assert all(v['user_id'] == existing_user['id'] for v in user_visits)

# def test_get_by_user_id_returns_empty_for_nonexisting_user(visit_log_repository):
#     visits = visit_log_repository.get_by_user_id(99999)
#     assert visits == []