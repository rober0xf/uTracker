import pytest

from app.services.fighters import delete_fighter_service

from .conftest import MockFighterRepo


class TestDeleteFighterService:
    def test_returns_none_success(self, mock_repo: MockFighterRepo):
        mock_repo.delete.return_value = True
        result = delete_fighter_service(1, mock_repo)
        assert result is None

    def test_calls_repo_with_id(self, mock_repo: MockFighterRepo):
        mock_repo.delete.return_value = True
        delete_fighter_service(1, mock_repo)
        mock_repo.delete.assert_called_once_with(1, mock_repo)

    def test_fails_if_not_found(self, mock_repo: MockFighterRepo):
        mock_repo.delete.return_value = None
        with pytest.raises(ValueError, match="fighter not found"):
            delete_fighter_service(1, mock_repo)
